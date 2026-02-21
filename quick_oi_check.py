import requests
import json
import time

session = requests.Session()
session.get('https://www.nseindia.com', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
time.sleep(1.5)

headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*', 'Accept-Encoding': 'identity', 
           'Referer': 'https://www.nseindia.com/market-data/oi-spurts', 'X-Requested-With': 'XMLHttpRequest'}

# Get one sector's stocks
print("Fetching NIFTY AUTO stocks...")
resp = session.get('https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20AUTO', 
                   headers=headers, timeout=15)

if resp.status_code == 200:
    sector_data = resp.json()
    stocks_list = [item.get('symbol') for item in sector_data.get('data', [])]
    print(f"Found {len(stocks_list)} stocks in NIFTY AUTO")
    print(f"First 5 stocks: {stocks_list[:5]}")
else:
    print(f"Failed to get stocks: {resp.status_code}")

# Get OI data
print("\nFetching options OI data...")
resp_oi = session.get('https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt', 
                      headers=headers, timeout=15)

if resp_oi.status_code == 200:
    oi_data = resp_oi.json()
    underlyings = set([item.get('underlying') for item in oi_data.get('data', [])])
    print(f"Found {len(underlyings)} unique stocks with options OI")
    print(f"First 5: {sorted(list(underlyings))[:5]}")
    
    # Check match
    match_count = len(set(stocks_list) & underlyings)
    print(f"\nMatching stocks (OI available): {match_count} out of {len(stocks_list)}")
    print(f"Matching: {sorted(list(set(stocks_list) & underlyings))}")
else:
    print(f"Failed to get OI: {resp_oi.status_code}")
