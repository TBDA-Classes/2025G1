import argparse
import json
import pandas as pd
from data_service import get_state_times, get_energy_consumption, get_machine_alarms

def main():
    parser = argparse.ArgumentParser(description="Query PostgreSQL for water treatment data.")
    
    parser.add_argument("datatype", choices=["wh", "ec", "alarms"], 
                        help="Type of data: 'wh' (work hours), 'ec' (energy), 'alarms' (warnings).")
    
    parser.add_argument("-f", "--from-date", required=True, help="Start date (YYYY-MM-DD HH:MI:SS).")
    parser.add_argument("-u", "--until-date", required=True, help="End date (YYYY-MM-DD HH:MI:SS).")
    args = parser.parse_args()

    print("\n--- Interface / Terminal Request ---")
    print(f"REQUEST: Data type '{args.datatype}' from {args.from_date} to {args.until_date}")

    # 1. Fetching DataFrame
    try:
        status = "success"
        
        if args.datatype == "wh":
            df = get_state_times(args.from_date, args.until_date)
        elif args.datatype == "ec":
            df = get_energy_consumption(args.from_date, args.until_date)
        elif args.datatype == "alarms":
            df = get_machine_alarms(args.from_date, args.until_date)
            
    except Exception as e:
        print(f"Error executing query: {e}")
        df = pd.DataFrame()
        status = "error"

    # 2. Data Preparation for JSON
    data_list = []
    
    if not df.empty:
        # Cleanup specific to single machine context
        cols_to_drop = ['machine_id', 'machine_name', 'device_id', 'equipment_id']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # Formatting numbers
        if 'total_hours' in df.columns:
            df['total_hours'] = df['total_hours'].round(4)
        if 'duration_sec' in df.columns:
            df['duration_sec'] = df['duration_sec'].round(2)
        if 'total_duration_sec' in df.columns:
            df['total_duration_sec'] = df['total_duration_sec'].round(2)

        # Convert date/timestamp objects to string
        for col in df.select_dtypes(include=['datetime', 'datetimetz']).columns:
            df[col] = df[col].astype(str)
            
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
        if 'ts' in df.columns:
            df['ts'] = df['ts'].astype(str)
        if 'last_seen' in df.columns:
            df['last_seen'] = df['last_seen'].astype(str)

        data_list = df.to_dict(orient='records')
    else:
        if status == "success":
            status = "no_data"

    # 3. JSON Response Construction
    response = {
        "status": status,
        "machine_context": "single_machine",
        "period": {
            "from": args.from_date, 
            "until": args.until_date
        },
        "count": len(data_list),
        "data": data_list 
    }

    print("\n--- JSON Response for Interface ---\n")
    # CORRECTION ICI : ensure_ascii=False permet d'afficher les accents dans le terminal
    print(json.dumps(response, indent=4, ensure_ascii=False))
    print("\n----------------------------------------")
    print("The JSON response file is available here: api_response.json")

    with open("api_response.json", "w", encoding="utf-8") as f:
        # CORRECTION ICI AUSSI : ensure_ascii=False permet d'écrire les accents dans le fichier
        json.dump(response, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()