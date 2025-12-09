import pandas as pd
import pytz # <-- NÉCESSAIRE POUR LA GESTION DU FUSEAU HORAIRE

from datetime import datetime
from database_dao import run_query_data

# --- CONSTANTS ---
# Standard time format for parsing date inputs
DEFAULT_FMT = "%Y-%m-%d %H:%M:%S"
FALLBACK_FMT = "%Y-%m-%d"

# --- HELPER FUNCTION ---

def _prepare_date_timestamps(from_date: str, until_date: str) -> tuple[int, int]:
    """
    Converts input date strings into UTC-based start/end milliseconds.
    """
    fmt = "%Y-%m-%d %H:%M:%S"
    
    try:
        dt_start = datetime.strptime(from_date, fmt)
        dt_end = datetime.strptime(until_date, fmt)
    except ValueError:
        # Fallback pour date-only input, en forçant les bornes complètes
        dt_start = datetime.strptime(from_date + " 00:00:00", fmt)
        dt_end = datetime.strptime(until_date + " 23:59:59", fmt)

    # 🚨 FIX CRITIQUE : Forcer la date à être interprétée comme UTC
    utc_tz = pytz.utc
    dt_start_utc = utc_tz.localize(dt_start)
    dt_end_utc = utc_tz.localize(dt_end)

    # Le timestamp calculé sera désormais universel
    ms_start = int(dt_start_utc.timestamp()) * 1000
    ms_end = int(dt_end_utc.timestamp()) * 1000
    
    return ms_start, ms_end
    return ms_start, ms_end

# ----------------------------------------------------------------------
# 📈 CORE DATA SERVICE FUNCTIONS
# ----------------------------------------------------------------------

def get_state_times(from_date: str, until_date: str) -> pd.DataFrame:
    """
    Calculates the total time (in Hours) spent in each state based on 
    distinct variable count and signal gaps.
    Version: FAST & HONEST (No fake data filling).
    """
    
    ms_start, ms_end = _prepare_date_timestamps(from_date, until_date)

    sql_query = """
    WITH RawSignal AS (
        -- 1. Aggregate: Count distinct variables per second-timestamp
        SELECT
            to_timestamp(floor(CAST(date AS BIGINT) / 1000)) AS timestamp,
            COUNT(DISTINCT id_var) AS distinct_vars_count
        FROM
            public.variable_log_float
        WHERE
            CAST(date AS BIGINT) >= :ms_start 
            AND CAST(date AS BIGINT) <= :ms_end
        GROUP BY
            timestamp
    ),
    IdleGaps AS (
        -- 2. Calculate True Idle (Off) time via Gaps in the signal
        SELECT
            'True Idle (Off)' AS state,
            SUM(EXTRACT(EPOCH FROM gap_duration)) / 3600.0 as total_hours
        FROM (
            SELECT
                -- Calculate duration between the current timestamp and (previous timestamp + 1s)
                timestamp - (LAG(timestamp) OVER (ORDER BY timestamp) + interval '1 second') AS gap_duration
            FROM
                RawSignal
        ) AS Gaps
        WHERE
            gap_duration > interval '0 seconds'
    ),
    SmoothedSignal AS (
        -- 3. Calculate Smoothed Signal for Activity Classification
        SELECT
            timestamp,
            AVG(distinct_vars_count) OVER (
                PARTITION BY date(timestamp) 
                ORDER BY timestamp
                ROWS BETWEEN 14 PRECEDING AND CURRENT ROW -- Moving Average over 15 points
            ) AS smoothed_count,
            ROW_NUMBER() OVER (PARTITION BY date(timestamp) ORDER BY timestamp) as row_num_per_day
        FROM
            RawSignal
    ),
    ActiveStateTotals AS (
        -- 4. Classify Active States based on the smoothed count
        SELECT
            CASE
                WHEN smoothed_count <= 14 THEN 'Low Activity'
                WHEN smoothed_count <= 20 THEN 'Intermediate Activity'
                ELSE 'High Activity'
            END AS state,
            (COUNT(*) * 1.0) / 3600.0 as total_hours 
        FROM
            SmoothedSignal
        WHERE
            row_num_per_day > 14 -- Ignore initial 14 points (warm-up period for moving average)
        GROUP BY
            state
    )
    -- Final Output: Combine Idle time and Active times
    SELECT * FROM IdleGaps
    UNION ALL
    SELECT * FROM ActiveStateTotals;
    """
    
    params = {"ms_start": ms_start, "ms_end": ms_end}
    df = run_query_data(sql_query, params)
    
    if df.empty:
        return pd.DataFrame(columns=['state', 'total_hours'])
        
    return df

# ----------------------------------------------------------------------

def get_machine_alarms(from_date: str, until_date: str) -> pd.DataFrame:
    """
    Returns AGGREGATED statistics for alarms (occurrence_count, last_seen).
    Uses Islands and Gaps logic to count distinct incidents.
    """
    
    ms_start, ms_end = _prepare_date_timestamps(from_date, until_date)

    sql_query = r"""
    WITH raw AS (
        -- 1. Filter Raw String Log (Variable 447)
        SELECT
            to_timestamp(floor(CAST(date AS BIGINT) / 1000)) AS ts,
            value,
            LEAD(to_timestamp(floor(CAST(date AS BIGINT) / 1000))) OVER (ORDER BY date) AS next_ts
        FROM variable_log_string
        WHERE id_var = 447
          AND CAST(date AS BIGINT) >= :ms_start 
          AND CAST(date AS BIGINT) <= :ms_end
          
          -- ⚡ EARLY FILTER (Noise Suppression) ⚡
          AND value !~ '(PLC00054|PLC00010|PLC01005|PLC00499|PLC00051|PLC00050|PLC00474|PLC00475|2a8-0003|130-019c|PLC00052|PLC00761)'
    ),
    flat AS (
        -- 2. Extract Alarm Code and Text using Regex
        SELECT
            r.ts,
            r.next_ts,
            (m)[1] AS alarm_code,
            (m)[2] AS alarm_text
        FROM raw r
        CROSS JOIN LATERAL regexp_matches(
            r.value,
            '\["([^"]+)","([^"]+)",([0-9]+),([0-9]+),([0-9]+)\]',
            'g'
        ) AS m
        WHERE r.next_ts IS NOT NULL
    ),
    segments AS (
        -- 3. Define Segments and Identify Previous End Time
        SELECT
            alarm_code, alarm_text, ts, next_ts,
            LAG(next_ts) OVER (PARTITION BY alarm_code, alarm_text ORDER BY ts) AS prev_end
        FROM flat
    ),
    marked AS (
        -- 4. Mark the Start of a New Incident (Gap in Signal)
        SELECT *, 
               CASE 
                   WHEN prev_end IS NULL OR prev_end < ts THEN 1 
                   ELSE 0 
               END AS new_group
        FROM segments
    ),
    islands AS (
        -- 5. Group Consecutive Records into the Same Incident (Island)
        SELECT *, 
               SUM(new_group) OVER (PARTITION BY alarm_code, alarm_text ORDER BY ts) AS grp
        FROM marked
    ),
    periods AS (
        -- 6. Define the Start Time for each unique Incident (Group)
        SELECT
            alarm_code,
            alarm_text,
            MIN(ts) AS start_time
        FROM islands
        GROUP BY alarm_code, alarm_text, grp
    )

    -- FINAL OUTPUT: Aggregate incidents by code/text
    SELECT
        alarm_code,
        alarm_text,
        COUNT(*) AS occurrence_count,
        MAX(start_time) AS last_seen
    FROM periods
    GROUP BY alarm_code, alarm_text
    ORDER BY occurrence_count DESC;
    """

    params = {"ms_start": ms_start, "ms_end": ms_end}
    return run_query_data(sql_query, params)

# ----------------------------------------------------------------------

def get_energy_consumption(from_date: str, until_date: str) -> pd.DataFrame:
    """
    Calculates Energy (kWh) from Load Percentage (Variable 630) using the
    Islands & Gaps method (to identify distinct runs).
    Data Team Formula: (Value% / 100) * 15kW * Hours.
    """
    ms_start, ms_end = _prepare_date_timestamps(from_date, until_date)

    sql_query = """
    WITH params AS (
        SELECT 15.0::float AS power_kw, 0.0::float AS on_threshold
    ),
    s AS (
        -- 1. Filter raw data, clamp percentage, and convert date to timestamp
        SELECT
            to_timestamp(l.date/1000.0) AS ts,
            GREATEST(LEAST(l.value::float, 100), 0) AS pct
        FROM variable_log_float l
        
        -- Utilizing JOIN on variable name for safety, but parameter must match Python logic
        JOIN variable v ON v.id = l.id_var 
        WHERE v.name = 'MANDRINO_CONSUMO_VISUALIZADO'
          AND CAST(l.date AS BIGINT) >= :ms_start 
          AND CAST(l.date AS BIGINT) <= :ms_end
          AND l.value = l.value -- Filter out NaN
    ),
    o AS (
        -- 2. Identify the next timestamp and if the machine is 'on'
        SELECT
            ts,
            LEAD(ts) OVER (ORDER BY ts) AS ts_next,
            pct,
            (pct > (SELECT on_threshold FROM params)) AS is_on
        FROM s
    ),
    iv AS (
        -- 3. Filter for valid intervals (no NULL next timestamp)
        SELECT *
        FROM o
        WHERE ts_next IS NOT NULL AND ts_next > ts
    ),
    mark AS (
        -- 4. Mark the start of a new 'run' (transition from off -> on)
        SELECT
            *,
            CASE
              WHEN is_on AND (LAG(is_on) OVER (ORDER BY ts) IS DISTINCT FROM TRUE) THEN 1
              ELSE 0
            END AS start_flag
        FROM iv
    ),
    runs AS (
        -- 5. Group consecutive 'on' segments into a unique run_id
        SELECT
            *,
            SUM(start_flag) OVER (ORDER BY ts
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS run_id
        FROM mark
        WHERE is_on 
    ),
    split AS (
        -- 6. Split intervals crossing midnight for accurate daily attribution
        SELECT
            (gs)::timestamp AS day_start,
            GREATEST(ts, gs) AS seg_start,
            LEAST(ts_next, gs + interval '1 day') AS seg_end,
            run_id,
            pct
        FROM runs
        JOIN LATERAL generate_series(
              date_trunc('day', ts),
              date_trunc('day', ts_next),
              interval '1 day'
            ) AS gs ON TRUE
        WHERE ts_next > ts
    ),
    seg AS (
        -- 7. Calculate total hours and energy (kWh) per segment
        SELECT
            day_start::date AS day,
            run_id,
            EXTRACT(EPOCH FROM (seg_end - seg_start))/3600.0 AS hours,
            (pct/100.0) * (SELECT power_kw FROM params)
              * EXTRACT(EPOCH FROM (seg_end - seg_start))/3600.0 AS energy_kwh
        FROM split
    )
    -- FINAL OUTPUT: Total Energy per day
    SELECT
        day,
        SUM(energy_kwh) AS total_energy_kwh
        -- total_duration_h and run_count columns are available but excluded 
        -- to match Streamlit application's needs (only total_energy_kwh is used).
    FROM seg
    GROUP BY day
    ORDER BY day;
    """
    
    params = {"ms_start": ms_start, "ms_end": ms_end}
    df = run_query_data(sql_query, params)
    
    if df.empty:
        return pd.DataFrame(columns=['date', 'total_energy_kwh'])
        
    return df