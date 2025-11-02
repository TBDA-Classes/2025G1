# app.py
import argparse
import json
from data_service import get_state_times, get_energy_consumption 

def main():
    parser = argparse.ArgumentParser(description="API backend for CNC machine monitoring data.")
    
    # Mandatory argument to choose the data type to request (ec, wh, or it)
    parser.add_argument('data', choices= ["ec", "wh", "it"], help='specify the data - ex ec/wh/it')
    
    # Mandatory arguments for the time period
    parser.add_argument('-f', '--from-date', help='Start date YYYY-MM-DD', required=True)
    parser.add_argument('-u', '--until-date', help='End date YYYY-MM-DD', required=True)

    args = parser.parse_args()
    
    print(f"\n--- Interface / Terminal Request ---")
    print(f"REQUEST: Data type '{args.data}' from {args.from_date} to {args.until_date}")

    response_data = {}
    
    # Logic to route requests to the appropriate service
    if args.data == "ec":
        response_data = get_energy_consumption(args.from_date, args.until_date)
    elif args.data == "wh" or args.data == "it":
        # The request for wh/it is the same as both are based on machine state times
        response_data = get_state_times(args.from_date, args.until_date)
    else:
        response_data = {"status": "error", "message": "Unknown data type."}


    # Displaying the JSON result
    print("\n--- JSON Response for Interface ---\n")
    json_output = json.dumps(response_data, indent=4)
    print(json_output)
    print("\n----------------------------------------")
    
    # Writing the JSON response to a file for review
    with open('api_response.json', 'w') as f:
        f.write(json_output)
        
    print("The JSON response file is available here: api_response.json")

if __name__ == "__main__":
    main()
