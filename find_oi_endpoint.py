import requests
import json
import time

session = requests.Session()
session.get('https://www.nseindia.com', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
time.sleep(1.5)

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': '*/*',
    'Accept-Encoding': 'identity',
    'Referer': 'https://www.nseindia.com/market-data/oi-spurts',
    'X-Requested-With': 'XMLHttpRequest',
}

# Test with stock_opt parameter
print("Testing liveEquity-derivatives with stock_opt parameter...")
resp = session.get('https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt', 
                   headers=headers, timeout=15)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(f"Keys: {list(data.keys())}")
    if 'data' in data:
        print(f"Number of records: {len(data['data'])}")
        if data['data']:
            print("\nFirst record sample:")
            print(json.dumps(data['data'][0], indent=2)[:800])
