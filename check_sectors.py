import requests
import json
import time

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

print("Fetching indices...")
resp = session.get('https://www.nseindia.com/api/allIndices', headers=api_headers, timeout=15)
data = resp.json()

print("\n" + "=" * 150)
print("ALL AVAILABLE INDICES:")
print("=" * 150)

for i, item in enumerate(data['data']):
    index = item.get('index', '')
    key = item.get('key', '')
    last = item.get('last', '')
    print(f"{i+1:3}. {index:45} | Key: {key:50} | LTP: {last}")

print("\n" + "=" * 150)
print("SECTOR INDICES (filtered):")
print("=" * 150)

sector_count = 0
for i, item in enumerate(data['data']):
    index = item.get('index', '')
    key = item.get('key', '')
    
    # Look for sector-related indices
    if 'SECTORAL' in key.upper() or ('NIFTY' in index.upper() and any(x in index.upper() for x in ['PHARMA', 'BANK', 'AUTO', 'IT', 'PSU', 'ENERGY', 'MEDIA', 'METAL', 'UTILITY', 'REALTY', 'FMCG', 'F&O'])):
        sector_count += 1
        last = item.get('last', '')
        change = item.get('percentChange', '')
        print(f"{sector_count:3}. {index:45} | LTP: {last} | % Change: {change}%")

if sector_count == 0:
    print("No sector indices found in 'SECTORAL' filter. Showing all non-main indices:")
    sector_count = 0
    for item in data['data']:
        index = item.get('index', '')
        key = item.get('key', '')
        
        # Exclude main broad indices
        exclude = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY100', 'SENSEX', 'VIX', 'DERIVATIVE', 'FINANCIAL', 'BROAD', 'INDIA VIX']
        if not any(x in index.upper() for x in exclude) and 'NIFTY' in index.upper():
            sector_count += 1
            last = item.get('last', '')
            change = item.get('percentChange', '')
            print(f"{sector_count:3}. {index:45} | LTP: {last} | % Change: {change}%")
