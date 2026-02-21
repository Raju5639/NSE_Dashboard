"""
Test to check what stock data is available from NSE API
"""
import requests
import json
import time
import urllib.parse

session = requests.Session()
base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive',
}

api_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/market-data/live-equity-market',
    'X-Requested-With': 'XMLHttpRequest',
}

print("Initializing session...")
session.get('https://www.nseindia.com', headers=base_headers, timeout=10)
time.sleep(1.5)

# Test accessing a sector's stocks
sector_name = "NIFTY AUTO"
encoded_sector = urllib.parse.quote(sector_name)
url = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded_sector}"

print(f"\nFetching stocks for {sector_name}...")
print(f"URL: {url}")
print('='*100)

try:
    time.sleep(1)
    resp = session.get(url, headers=api_headers, timeout=15)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        try:
            data = resp.json()
            print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
            
            if isinstance(data, dict) and 'data' in data:
                print(f"\nNumber of stocks: {len(data['data'])}")
                print("\nFirst stock sample:")
                print(json.dumps(data['data'][0], indent=2))
                
                print("\n\nAll available fields in stock data:")
                if data['data']:
                    print(list(data['data'][0].keys()))
            
        except Exception as e:
            print(f"Error parsing: {e}")
            print(f"Raw response (first 500 chars): {resp.text[:500]}")
    else:
        print(f"Error: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*100)
print("Testing allIndices endpoint for stock info...")
time.sleep(1)
resp2 = session.get("https://www.nseindia.com/api/allIndices", headers=api_headers, timeout=15)
if resp2.status_code == 200:
    data2 = resp2.json()
    # Find a sector index
    sector = None
    for item in data2['data']:
        if item.get('key') == 'SECTORAL INDICES':
            sector = item
            break
    
    if sector:
        print("\nSector index sample:")
        print(json.dumps(sector, indent=2))
