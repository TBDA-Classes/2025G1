import yaml
import pandas as pd
from sqlalchemy import create_engine, text

# Reading the config.yaml file (Make sure it contains your credentials)
with open("config.yaml", "r") as file:
    DB_CONFIG = yaml.safe_load(file)

def get_engine():
    """Creates a SQLAlchemy connection to the PostgreSQL database."""
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@"
            f"{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
        )
        # Do not print successful connection in a production/Streamlit environment
        # print(f"✅ SUCCESS: Connected to {DB_CONFIG['DB_HOST']}...") 
        return engine
    except Exception as e:
        print(f"❌ ERROR: Database connection failed - {e}")
        # Optional: Make the error visible in Streamlit for debugging
        raise

def run_query_data(sql_query: str, params: dict) -> pd.DataFrame:
    """
    Executes a SELECT query with parameters and returns a DataFrame.
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection, params=params)
        return df

    except Exception as e:
        print(f"SQLAlchemy Error (SELECT): {e}")
        return pd.DataFrame()

# NEW FUNCTION: Executes a command without result
def execute_sql_command(sql_command: str):
    """
    Executes an SQL command (CREATE, REFRESH, INSERT, etc.) that does not return a DataFrame.
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text(sql_command))
            connection.commit() # Important for DDL/DML commands
            # print(f"✅ SUCCESS: Command executed: {sql_command.splitlines()[0].strip()}...")
        return True
    except Exception as e:
        # print(f"❌ ERROR: SQL command failed - {e}")
        return False