import argparse
import json
import pandas as pd
from data_service import get_state_times, get_energy_consumption

def main():
    parser = argparse.ArgumentParser(description="Query PostgreSQL for water treatment data.")
    parser.add_argument("datatype", choices=["wh", "ec"], help="Type of data to retrieve ('wh' for work hours, 'ec' for energy consumption).")
    parser.add_argument("-f", "--from-date", required=True, help="Start date (YYYY-MM-DD HH:MI:SS).")
    parser.add_argument("-u", "--until-date", required=True, help="End date (YYYY-MM-DD HH:MI:SS).")
    args = parser.parse_args()

    print("\n--- Interface / Terminal Request ---")
    print(f"REQUEST: Data type '{args.datatype}' from {args.from_date} to {args.until_date}")

    # 1. Récupération du DataFrame (Pandas)
    try:
        if args.datatype == "wh":
            df = get_state_times(args.from_date, args.until_date)
        else:
            df = get_energy_consumption(args.from_date, args.until_date)
            
        # Statut de base
        status = "success"
        
    except Exception as e:
        # En cas d'erreur SQL ou code, on crée un DF vide et on log l'erreur
        print(f"Error executing query: {e}")
        df = pd.DataFrame()
        status = "error"

    # 2. Préparation des données pour JSON (Correction de l'erreur de sérialisation)
    data_list = []
    
    if not df.empty:
        # IMPORTANT: Convertir les objets Date/Timestamp en string pour éviter l'erreur JSON
        # On cherche les colonnes de type datetime et on les convertit
        for col in df.select_dtypes(include=['datetime', 'datetimetz']).columns:
            df[col] = df[col].astype(str)
            
        # Si vous avez une colonne nommée 'date' qui n'est pas détectée, forcez-la :
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)

        # Conversion du DataFrame en liste de dictionnaires
        # Exemple : [{"date": "2022...", "val": 10}, {"date": "2022...", "val": 12}]
        data_list = df.to_dict(orient='records')
    else:
        if status == "success":
            status = "no_data"

    # 3. Construction de la réponse
    response = {
        "status": status,
        "period": {
            "from": args.from_date, 
            "until": args.until_date
        },
        "count": len(data_list),
        "data": data_list  # On passe la liste convertie, pas le DataFrame brut
    }

    print("\n--- JSON Response for Interface ---\n")
    print(json.dumps(response, indent=4))
    print("\n----------------------------------------")
    print("The JSON response file is available here: api_response.json")

    with open("api_response.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4)

if __name__ == "__main__":
    main()