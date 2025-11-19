import pandas as pd
from database_dao import run_query_data

# NOTE IMPORTANTE : 
# Les requêtes SQL ci-dessous ne sont que des exemples basés sur
# les totaux agrégés. Vous devrez les ajuster si vos données
# réelles du backend sont plus granulaires (par jour/machine).

def get_state_times(from_date: str, until_date: str) -> pd.DataFrame:
    """
    Récupère le temps total passé dans chaque état d'activité
    à partir de la Vue Matérialisée (ou de la table brute) entre deux dates.
    """
    # 🛑 REQUÊTE UTILISANT LA VUE MATÉRIALISÉE
    # Nous utilisons la MV si elle existe, sinon nous pouvons revenir à la table brute
    # Notez que la MV n'a pas de machine, elle donne juste un COUNT DISTINCT global.
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
    
    # Pour simuler les colonnes Operating et Standby du front-end, nous allons générer des données factices
    # basées sur le résultat pour maintenir la compatibilité de l'interface.
    params = {"start_date": from_date, "end_date": until_date}
    df = run_query_data(sql_query, params)
    
    # Si la MV est vide ou n'est pas encore prête, retournez un DataFrame vide ou utilisez la simulation
    if df.empty:
        # Retour à une structure compatible avec la simulation si les données réelles sont absentes
        return pd.DataFrame(columns=['date', 'machine', 'Operating', 'Standby'])


    # --- SIMULATION POUR COMPATIBILITÉ AVEC L'INTERFACE STREAMLIT ---
    # L'interface Streamlit s'attend à 'machine', 'Operating', 'Standby' par jour.
    # Nous simulons cette granularité à partir du count global.
    
    # Définition des machines (doit correspondre à app.py)
    MACHINES = ["Machine A", "Machine B", "Machine C"]
    
    rows = []
    for index, row in df.iterrows():
        # Heures totales disponibles par jour (ex: 24h)
        total_seconds_in_day = 8 * 3600 # 8 heures de travail pour la démo
        total_count = row['operating_count']
        
        # Répartition arbitraire de l'activité sur les machines
        for machine in MACHINES:
            # Simuler l'activité de la machine proportionnelle au count
            operating_hours = (total_count / 1000) / len(MACHINES) # Normalisation factice
            operating_hours = max(1, min(7.5, operating_hours)) # Plage raisonnable 1h à 7.5h
            standby_hours = max(0, 8 - operating_hours - 0.5) # Temps d'inactivité
            
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
    Récupère la consommation d'énergie entre deux dates.
    (La requête SQL doit être ajustée en fonction de la structure de votre table d'énergie).
    """
    # Exemple de requête (assumant une table 'energy_log' et une agrégation horaire)
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
    # Ici, nous retournons des données factices pour l'énergie car la table réelle n'existe pas dans notre contexte
    # VOUS DEVEZ REMPLACER CE QUI SUIT PAR L'APPEL RÉEL À VOTRE BASE :
    # params = {"start_date": from_date, "end_date": until_date}
    # return run_query_data(sql_query, params)
    
    # --- SIMULATION (Basée sur l'ancienne fonction generate_energy_data pour compatibilité) ---
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