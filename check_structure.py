import requests
import json
import time

session = requests.Session()
session.get('https://www.nseindia.com', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
time.sleep(1.5)

headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*', 'Accept-Encoding': 'identity', 
           'Referer': 'https://www.nseindia.com/market-data/oi-spurts', 'X-Requested-With': 'XMLHttpRequest'}

# Get one sector's stocks with details
print("Checking stock data structure...")
resp = session.get('https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20AUTO', 
                   headers=headers, timeout=15)

if resp.status_code == 200:
    sector_data = resp.json()
    print(f"Total items in response: {len(sector_data.get('data', []))}")
    print("\nAll items:")
    for i, item in enumerate(sector_data.get('data', [])):
        print(f"{i+1}. Symbol: {item.get('symbol'):20} Priority: {item.get('priority')} Open: {item.get('open')}")
