"""
Simple check of stock_opt data to see all fields
"""
import requests
import json
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Encoding": "identity",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)
time.sleep(2)

url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt"

try:
    response = session.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'data' in data and data['data']:
            print("First record from stock_opt:")
            print(json.dumps(data['data'][0], indent=2))
            
            print("\n\nAll field names in first record:")
            for key in data['data'][0].keys():
                print(f"  - {key}")
            
            print(f"\n\nTotal records: {len(data['data'])}")
            print(f"Data keys: {data.keys()}")
    else:
        print(f"Status: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
