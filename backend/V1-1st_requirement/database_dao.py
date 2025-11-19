import yaml
import pandas as pd
from sqlalchemy import create_engine, text

# Lecture du fichier config.yaml (Assurez-vous qu'il contient vos identifiants)
with open("config.yaml", "r") as file:
    DB_CONFIG = yaml.safe_load(file)

def get_engine():
    """Crée une connexion SQLAlchemy à la base PostgreSQL."""
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@"
            f"{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
        )
        # Ne pas imprimer la connexion réussie dans un environnement de production/Streamlit
        # print(f"✅ SUCCESS: Connected to {DB_CONFIG['DB_HOST']}...") 
        return engine
    except Exception as e:
        print(f"❌ ERROR: Database connection failed - {e}")
        # Optionnel : Rendre l'erreur visible dans Streamlit pour débogage
        raise

def run_query_data(sql_query: str, params: dict) -> pd.DataFrame:
    """
    Exécute une requête SELECT avec paramètres et renvoie un DataFrame.
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection, params=params)
        return df

    except Exception as e:
        print(f"SQLAlchemy Error (SELECT): {e}")
        return pd.DataFrame()

# NOUVELLE FONCTION : Exécute une commande sans résultat
def execute_sql_command(sql_command: str):
    """
    Exécute une commande SQL (CREATE, REFRESH, INSERT, etc.) qui ne retourne pas de DataFrame.
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text(sql_command))
            connection.commit() # Important pour les commandes DDL/DML
            # print(f"✅ SUCCESS: Command executed: {sql_command.splitlines()[0].strip()}...")
        return True
    except Exception as e:
        # print(f"❌ ERROR: SQL command failed - {e}")
        return False