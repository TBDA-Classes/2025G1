# data_service.py
import pandas as pd
from database_dao import run_query_data

def get_state_times(from_date: str, until_date: str) -> dict:
    """
    Optimized version that avoids schema changes.
    Keeps CAST(to_timestamp(...)) but simplifies and optimizes SQL logic.
    """

    sql_query = """
    WITH filtered AS (
        SELECT
            to_timestamp(CAST(date AS BIGINT)/1000) AS ts,
            id_var
        FROM public.variable_log_float
        WHERE to_timestamp(CAST(date AS BIGINT)/1000)
              BETWEEN :from_date AND :until_date
    ),
    counts AS (
        SELECT
            date_trunc('second', ts) AS ts_sec,
            COUNT(DISTINCT id_var) AS distinct_vars
        FROM filtered
        GROUP BY 1
    ),
    states AS (
        SELECT
            ts_sec,
            CASE
                WHEN distinct_vars <= 17 THEN 'Idle'
                WHEN distinct_vars <= 24 THEN 'Intermediate'
                ELSE 'Active'
            END AS state,
            CASE
                WHEN distinct_vars <= 17 THEN 0
                WHEN distinct_vars <= 24 THEN 1
                ELSE 2
            END AS state_num
        FROM counts
    ),
    transitions AS (
        SELECT
            ts_sec AS timestamp,
            state,
            state_num,
            LAG(state_num) OVER (ORDER BY ts_sec) AS prev_state
        FROM states
    ),
    state_periods AS (
        SELECT
            timestamp,
            state,
            state_num
        FROM transitions
        WHERE prev_state IS DISTINCT FROM state_num
    ),
    durations AS (
        SELECT
            state,
            LEAD(timestamp, 1, (SELECT MAX(ts_sec) FROM states)) 
                OVER (ORDER BY timestamp) - timestamp AS duration
        FROM state_periods
    )
    SELECT
        state,
        ROUND(EXTRACT(EPOCH FROM SUM(duration)) / 3600.0, 2) AS "Duration(Hours)"
    FROM durations
    GROUP BY state
    ORDER BY state;
    """

    params = {"from_date": from_date, "until_date": until_date}
    result_df = run_query_data(sql_query, params)

    if result_df.empty:
        return {
            "status": "error",
            "message": "No data retrieved. Check dates, DB connection, or SQL execution.",
            "data": None
        }

    pivot_data = result_df.set_index('state')['Duration(Hours)'].to_dict()

    return {
        "status": "success",
        "period": {"from": from_date, "until": until_date},
        "totals_in_hours": {
            "active": round(pivot_data.get('Active', 0), 2),
            "intermediate": round(pivot_data.get('Intermediate', 0), 2),
            "idle": round(pivot_data.get('Idle', 0), 2)
        }
    }


def get_energy_consumption(from_date: str, until_date: str) -> dict:
    """Placeholder for energy consumption."""
    return {
        "status": "success",
        "period": {"from": from_date, "until": until_date},
        "message": "Energy Consumption (ec) function not yet implemented.",
        "data": {"energy_kwh": 0, "co2_eq": 0}
    }
