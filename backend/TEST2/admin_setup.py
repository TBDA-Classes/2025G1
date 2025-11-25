# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 16:23:21 2025

@author: gabri
"""

# admin_setup.py
import sys
from database_dao import execute_sql_command

def setup_materialized_view():
    """
    Crée la Vue Matérialisée et son index.
    Utilise 'IF NOT EXISTS' pour ne pas échouer si la vue existe déjà.
    """
    print("--- 🛠️ Initialisation de la Base de Données pour l'Optimisation ---")

    # Commande 1 : Création de la Vue Matérialisée
    create_mv_sql = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS variable_counts_per_second AS
    SELECT
        date_trunc('second', to_timestamp(CAST(date AS BIGINT)/1000)) AS timestamp,
        COUNT(DISTINCT id_var) AS distinct_vars_count
    FROM
        public.variable_log_float
    GROUP BY
        1;
    """
    print("Tentative de création de la Vue Matérialisée...")
    execute_sql_command(create_mv_sql)
    
    # Commande 2 : Création de l'Index Unique
    create_index_sql = "CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_timestamp ON variable_counts_per_second (timestamp);"
    print("Tentative de création de l'Index...")
    execute_sql_command(create_index_sql)
    
    print("Setup terminé. Veuillez rafraîchir la vue maintenant.")

def refresh_materialized_view():
    """
    Rafraîchit les données de la Vue Matérialisée.
    Ceci doit être exécuté après chaque nouvelle insertion de données brutes.
    """
    print("--- 🔄 Rafraîchissement de la Vue Matérialisée ---")
    
    refresh_sql = "REFRESH MATERIALIZED VIEW variable_counts_per_second;"
    print("Démarrage du rafraîchissement. Ceci peut prendre du temps...")
    execute_sql_command(refresh_sql)
    
    print("Rafraîchissement terminé. La fonction 'get_state_times' est maintenant à jour.")

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("\nUsage:")
        print("  Pour l'initialisation : python admin_setup.py setup")
        print("  Pour le rafraîchissement : python admin_setup.py refresh")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    
    if action == "setup":
        setup_materialized_view()
    elif action == "refresh":
        refresh_materialized_view()
    else:
        print(f"Action non reconnue : {action}. Utilisez 'setup' ou 'refresh'.")