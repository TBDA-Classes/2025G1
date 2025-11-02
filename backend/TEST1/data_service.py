# data_service.py
import json
import pandas as pd
from database_dao import run_query_data

def get_state_times(from_date: str, until_date: str) -> dict:
    """
    Constructs the SQL query and calls the DAO to retrieve the total state times 
    (Active, Intermediate, Idle) for the period requested by the user.
    """
    
    # --- FINAL SQL QUERY (Aggregation Logic) ---
    # This query uses the K-Means thresholds (17 and 24) and dynamically filters by date (%s).
    sql_query = """
    WITH VariablesPerSecond AS (
        -- 1. Get the distinct variables per second within the date range defined by the user.
        SELECT
            to_timestamp(floor(CAST(date AS BIGINT) / 1000)) AS timestamp,
            id_var
        FROM
            public.variable_log_float
        WHERE
            -- DYNAMIC DATE FILTER: Uses the two Python parameters
            to_timestamp(CAST(date AS BIGINT) / 1000) BETWEEN %s AND %s 
        GROUP BY
            timestamp, id_var
    ),
    DistinctCountPerSecond AS (
        -- 2. Calculate the count of distinct active variables per second.
        SELECT
            timestamp,
            COUNT(id_var) AS distinct_vars_count
        FROM
            VariablesPerSecond
        GROUP BY
            timestamp
    ),
    InstantaneousStates AS (
        -- 3. Assign the state label based on K-Means thresholds.
        SELECT
            timestamp,
            CASE
                WHEN distinct_vars_count <= 17 THEN 'Idle'           -- K-Means Threshold 1
                WHEN distinct_vars_count <= 24 THEN 'Intermediate'    -- K-Means Threshold 2
                ELSE 'Active'
            END AS state_label,
            CASE
                WHEN distinct_vars_count <= 17 THEN 0 
                WHEN distinct_vars_count <= 24 THEN 1 
                ELSE 2 
            END AS state_num
        FROM
            DistinctCountPerSecond
    ),
    StateChanges AS (
        -- 4. Identify the moments when the state changes
        SELECT timestamp, state_num, state_label
        FROM (
            SELECT 
                timestamp, state_num, state_label, 
                LAG(state_num, 1, -1) OVER (ORDER BY timestamp) AS previous_state_num
            FROM InstantaneousStates
        ) AS Subquery
        WHERE state_num <> previous_state_num
    ),
    RelevantDataTimeRange AS (
        -- CTE to get the min/max timestamps in the filtered set
        SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts FROM InstantaneousStates
    ),
    PeriodStarts AS (
        -- 5. Construct all starting points for the periods
        SELECT timestamp, state_num, state_label FROM StateChanges
        UNION ALL
        -- Ensure the first timestamp is included if it's not a change point
        SELECT
            min_ts,
            (SELECT state_num FROM InstantaneousStates WHERE timestamp = min_ts),
            (SELECT state_label FROM InstantaneousStates WHERE timestamp = min_ts)
        FROM RelevantDataTimeRange
        WHERE NOT EXISTS (SELECT 1 FROM StateChanges sc WHERE sc.timestamp = min_ts)
        
    ),
    DetailedPeriods AS (
        -- 6. Calculate the duration for each period
         SELECT
            state_label AS state,
            LEAD(timestamp, 1, (SELECT max_ts + interval '1 second' FROM RelevantDataTimeRange)) OVER (ORDER BY timestamp) - timestamp AS duration
         FROM
            PeriodStarts
         ORDER BY timestamp
    )
    -- FINAL STEP: Aggregate the detailed periods to get the total time for each state (in hours)
    SELECT
        state,
        EXTRACT(EPOCH FROM SUM(duration)) / 3600.0 AS "Duration(Hours)" 
    FROM
        DetailedPeriods
    GROUP BY
        state;
    """
    
    # The parameters are passed to the DAO: (from_date, until_date)
    params = (from_date, until_date)

    # Call the DAO to execute the DB query
    result_df = run_query_data(sql_query, params)
    
    if result_df.empty:
        return {
            "status": "error",
            "message": "No data retrieved. Check dates, DB connection, or SQL execution.",
            "data": None
        }
        
    try:
        # Transform the Pandas DataFrame into a dictionary for the JSON response
        pivot_data = result_df.set_index('state')['Duration(Hours)'].to_dict()
        
        active_time = pivot_data.get('Active', 0)
        intermediate_time = pivot_data.get('Intermediate', 0)
        idle_time = pivot_data.get('Idle', 0)
        
    except KeyError as e:
        return {
            "status": "error",
            "message": f"Data processing error: Missing column {e} in SQL result.",
            "data": None
        }

    # Format the final JSON result
    return {
        "status": "success",
        "period": {"from": from_date, "until": until_date},
        "totals_in_hours": {
            "active": round(active_time, 2),
            "intermediate": round(intermediate_time, 2),
            "idle": round(idle_time, 2)
        }
    }

def get_energy_consumption(from_date: str, until_date: str) -> dict:
    """
    PLACEHOLDER: Future function for energy consumption (ec).
    """
    return {
        "status": "success",
        "period": {"from": from_date, "until": until_date},
        "message": "Energy Consumption (ec) function not yet implemented.",
        "data": {"energy_kwh": 0, "co2_eq": 0}
    }
