import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG

def get_engine():
    """Crée une connexion SQLAlchemy à la base PostgreSQL."""
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@"
            f"{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
        )
        print(f"✅ SUCCESS: Connected to {DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']} ({DB_CONFIG['DB_NAME']}) as {DB_CONFIG['DB_USER']}")
        return engine
    except Exception as e:
        print(f"❌ ERROR: Database connection failed - {e}")
        raise

def run_query_data(sql_query: str, params: dict) -> pd.DataFrame:
    """
    Exécute une requête SQL avec paramètres et renvoie un DataFrame.
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection, params=params)
        return df

    except Exception as e:
        print(f"SQLAlchemy Error: {e}")
        return pd.DataFrame()
