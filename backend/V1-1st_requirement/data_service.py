import pandas as pd
from database_dao import run_query_data

# IMPORTANT NOTE: 
# The SQL queries below are just examples based on aggregated totals. 
# You will need to adjust them if your actual backend data is more 
# granular (per day/machine).

def get_state_times(from_date: str, until_date: str) -> pd.DataFrame:
    """
    Retrieves the total time spent in each activity state
    from the Materialized View (or raw table) between two dates.
    """
    # 🛑 QUERY USING THE MATERIALIZED VIEW
    # We use the MV if it exists, otherwise we can revert to the raw table.
    # Note that the MV does not have machine detail, it just gives a global COUNT DISTINCT.
    sql_query = """
    SELECT
        t1.timestamp::date AS date,
        SUM(t1.distinct_vars_count) AS operating_count
    FROM
        variable_counts_per_second t1
    WHERE
        t1.timestamp >= :start_date AND t1.timestamp <= :end_date
    GROUP BY
        1
    ORDER BY
        1;
    """
    
    # To simulate the Operating and Standby columns for the frontend, we will generate dummy data
    # based on the result to maintain interface compatibility.
    params = {"start_date": from_date, "end_date": until_date}
    df = run_query_data(sql_query, params)
    
    # If the MV is empty or not yet ready, return an empty DataFrame or use the simulation
    if df.empty:
        # Return to a structure compatible with the simulation if real data is missing
        return pd.DataFrame(columns=['date', 'machine', 'Operating', 'Standby'])


    # --- SIMULATION FOR STREAMLIT INTERFACE COMPATIBILITY ---
    # The Streamlit interface expects 'machine', 'Operating', 'Standby' per day.
    # We simulate this granularity from the global count.
    
    # Machine definition (must match app.py)
    MACHINES = ["Machine A", "Machine B", "Machine C"]
    
    rows = []
    for index, row in df.iterrows():
        # Total available hours per day (ex: 24h)
        total_seconds_in_day = 8 * 3600 # 8 working hours for the demo
        total_count = row['operating_count']
        
        # Arbitrary distribution of activity across machines
        for machine in MACHINES:
            # Simulate machine activity proportional to the count
            operating_hours = (total_count / 1000) / len(MACHINES) # Fake normalization
            operating_hours = max(1, min(7.5, operating_hours)) # Reasonable range 1h to 7.5h
            standby_hours = max(0, 8 - operating_hours - 0.5) # Inactivity time
            
            rows.append({
                "date": row['date'],
                "machine": machine,
                "Operating": operating_hours,
                "Standby": standby_hours,
            })
            
    return pd.DataFrame(rows)
    # -----------------------------------------------------------------


def get_energy_consumption(from_date: str, until_date: str) -> pd.DataFrame:
    """
    Retrieves energy consumption between two dates.
    (The SQL query needs to be adjusted based on your energy table structure).
    """
    # Example query (assuming an 'energy_log' table and hourly aggregation)
    sql_query = """
    SELECT
        date_trunc('day', energy_timestamp) AS date,
        machine_id,
        SUM(kwh_value) AS total_energy_kwh
    FROM
        public.energy_log
    WHERE
        energy_timestamp >= :start_date AND energy_timestamp <= :end_date
    GROUP BY
        1, 2
    ORDER BY
        1;
    """
    # Here, we return dummy data for energy because the real table doesn't exist in our context
    # YOU MUST REPLACE THE FOLLOWING WITH THE REAL CALL TO YOUR DATABASE:
    # params = {"start_date": from_date, "end_date": until_date}
    # return run_query_data(sql_query, params)
    
    # --- SIMULATION (Based on the old generate_energy_data function for compatibility) ---
    from app import generate_energy_data, datetime
    
    df_energy_full = generate_energy_data()
    
    start_dt = datetime.strptime(from_date.split(" ")[0], "%Y-%m-%d").date()
    end_dt = datetime.strptime(until_date.split(" ")[0], "%Y-%m-%d").date()
    
    df_filtered = df_energy_full[
        (df_energy_full["date"] >= start_dt) &
        (df_energy_full["date"] <= end_dt)
    ]
    return df_filtered
    # ----------------------------------------------------------------------------------------