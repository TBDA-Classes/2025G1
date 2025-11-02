import argparse

def get_energy_consumption(from_date, until_date):
    query = " "
    
    return run_query(query, (from_date, until_date))

def get_working_hours(from_date, until_date):
    query = " "
    
    return run_query(query, (from_date, until_date))

def get_idle_time(from_date, until_date):
    query = " "
    
    return run_query(query, (from_date, until_date))

def run_query(query, params): 
    #TODO big times... 
    return []

def send_to_frontend(argsdata, data):  
    return

def main():
    parser = argparse.ArgumentParser(description="send data from backend to frontend")
    
    parser.add_argument('data', choices= ["ec", "wh", "it"], help='specify the data - ex ec/wh/it')
    
    parser.add_argument('-f', '--from-date', help='Start date YYYY-MM-DD', required=True)
    parser.add_argument('-u', '--until-date', help='End date YYYY-MM-DD', required=True)

    args = parser.parse_args()
    if args.data == "ec":
        print(f" Fetching energy consumption data from {args.from_date} to {args.until_date}...")
        data = get_energy_consumption(args.from_date, args.until_date)
    elif args.data == "wh":
        print(f"Fetching working hours data from {args.from_date} to {args.until_date}...")
        data = get_working_hours(args.from_date, args.until_date)
    elif args.data == "it":
        print(f"Fetching idle time data from {args.from_date} to {args.until_date}...")
        data = get_idle_time(args.from_date, args.until_date)


    print(f"Found {len(data)} rows. Sending to frontend...")
    send_to_frontend(args.data, data)

if __name__ == "__main__":
    main()