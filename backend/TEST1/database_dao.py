# database_dao.py
import pandas as pd
import psycopg2
# Import configuration variables from the config.py file
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

def run_query_data(sql_query: str, params: tuple) -> pd.DataFrame:
    """
    Establishes the connection to the DB, executes the parameterized SQL query, 
    and returns a result as a Pandas DataFrame.

    Args:
        sql_query: The SQL query string containing placeholders (%s).
        params: A tuple of parameters (e.g., dates) to safely substitute into the query.

    Returns:
        A Pandas DataFrame with the query results, or an empty DataFrame on error.
    """
    conn = None
    try:
        # Attempt to establish the connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        
        # Execute the SQL query and load the results directly into a Pandas DataFrame.
        # pandas.read_sql_query securely handles the parameter substitution for psycopg2.
        df = pd.read_sql_query(sql_query, conn, params=params)
        
        return df

    except psycopg2.Error as e:
        # Handles errors specific to database connection or SQL execution
        print(f"SQL Connection or Execution Error: {e}")
        return pd.DataFrame()
        
    finally:
        # Ensures the connection is closed even if an error occurred
        if conn is not None:
            conn.close()
