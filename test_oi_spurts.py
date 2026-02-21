"""
Test to find the correct OI Spurts API endpoint
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
    ("OI Spurts", "https://www.nseindia.com/api/oi-spurts"),
    ("Option Chain", "https://www.nseindia.com/api/option-chain-data"),
    ("Live Derivatives", "https://www.nseindia.com/api/liveEquity-derivatives"),
    ("Derivatives Data", "https://www.nseindia.com/api/derivatives"),
    ("OI Data", "https://www.nseindia.com/api/oi-data"),
    ("Top OI Gainers", "https://www.nseindia.com/api/top-oi-gainers"),
    ("Market Activity", "https://www.nseindia.com/api/market-activity"),
]

for name, url in endpoints:
    print(f"\n{'='*100}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*100)
    
    try:
        time.sleep(1)
        resp = session.get(url, headers=api_headers, timeout=15)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict):
                    print(f"Response Keys: {list(data.keys())[:20]}")
                    print(f"\nSample Data (first 1000 chars):")
                    print(json.dumps(data, indent=2)[:1000])
                else:
                    print(f"Response is list with {len(data)} items")
                    print(f"First item: {json.dumps(data[0], indent=2)[:500]}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Response size: {len(resp.text)} chars")
        else:
            print(f"Status {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "="*100)
print("Trying derivative data with specific stock...")
time.sleep(1)

# Try with a specific stock
resp = session.get('https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt', 
                   headers=api_headers, timeout=15)
print(f"\nDerivatives (options) status: {resp.status_code}")
if resp.status_code == 200:
    try:
        data = resp.json()
        if 'data' in data:
            print(f"Found {len(data['data'])} options records")
            if data['data']:
                print("\nFirst option record:")
                print(json.dumps(data['data'][0], indent=2))
    except:
        print("Could not parse response")
