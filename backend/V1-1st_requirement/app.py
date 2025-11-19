# app.py
import argparse
import json
from data_service import get_state_times, get_energy_consumption

def main():
    parser = argparse.ArgumentParser(description="Query PostgreSQL for water treatment data.")
    parser.add_argument("datatype", choices=["wh", "ec"], help="Type of data to retrieve ('wh' for work hours, 'ec' for energy consumption).")
    parser.add_argument("-f", "--from-date", required=True, help="Start date (YYYY-MM-DD HH:MI:SS).")
    parser.add_argument("-u", "--until-date", required=True, help="End date (YYYY-MM-DD HH:MI:SS).")
    args = parser.parse_args()

    print("\n--- Interface / Terminal Request ---")
    print(f"REQUEST: Data type '{args.datatype}' from {args.from_date} to {args.until_date}")

    if args.datatype == "wh":
        data_result = get_state_times(args.from_date, args.until_date)
    else:
        data_result = get_energy_consumption(args.from_date, args.until_date)

    response = {
        "status": data_result.get("status", "error"),
        "period": data_result.get("period", {"from": args.from_date, "until": args.until_date}),
        "data": data_result
    }

    print("\n--- JSON Response for Interface ---\n")
    print(json.dumps(response, indent=4))
    print("\n----------------------------------------")
    print("The JSON response file is available here: api_response.json")

    with open("api_response.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4)

if __name__ == "__main__":
    main()