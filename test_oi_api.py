"""
Diagnostic script to check NSE OI Spurts data structure
"""
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
    'Referer': 'https://www.nseindia.com/market-data/oi-spurts',
    'X-Requested-With': 'XMLHttpRequest',
}

print("Initializing session...")
session.get('https://www.nseindia.com', headers=base_headers, timeout=10)
time.sleep(1.5)

# Test different OI-related endpoints
endpoints = [
    ("OI Spurts API", "https://www.nseindia.com/api/oi-spurts"),
    ("Top Gainers", "https://www.nseindia.com/api/live-equity-market"),
    ("Market Data", "https://www.nseindia.com/api/equity-stockIndices"),
    ("Stock Movers", "https://www.nseindia.com/api/topGainers"),
]

for name, url in endpoints:
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    try:
        time.sleep(1)
        resp = session.get(url, headers=api_headers, timeout=15)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
                print(f"\nSample Data (first 800 chars):")
                print(json.dumps(data, indent=2)[:800])
            except:
                print("Could not parse JSON")
        else:
            print(f"Error: {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")
