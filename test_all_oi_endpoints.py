"""
Try option-chain-indices with proper symbol parameter
Also look for any OI-specific endpoints
"""
import requests
import json
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
    "Referer": "https://www.nseindia.com/market-data/oi-spurts",
}

session = requests.Session()

# Initialize session
print("Initializing session...")
session.get("https://www.nseindia.com", headers=headers, timeout=10)
time.sleep(2)

# Try with NIFTY symbol
print("\n" + "="*80)
print("Testing /api/option-chain-indices with NIFTY symbol")
print("="*80)

url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
print(f"\nURL: {url}")

try:
    response = session.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response size: {len(response.text)} chars")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✓ Valid JSON")
            print(f"Root keys: {list(data.keys())}")
            
            # Check for records
            if 'records' in data:
                records = data['records']
                if isinstance(records, dict):
                    print(f"Records is dict with keys: {list(records.keys())}")
                    if 'data' in records:
                        print(f"  'data' contains {len(records['data'])} items")
                        if records['data']:
                            print(f"  First item keys: {list(records['data'][0].keys())}")
                            first_item = records['data'][0]
                            # Print OI-related fields
                            for k, v in first_item.items():
                                if 'oi' in k.lower() or 'change' in k.lower() or 'chng' in k.lower():
                                    print(f"    {k}: {v}")
                elif isinstance(records, list):
                    print(f"Records has {len(records)} items")
                    if records:
                        print(f"First record keys: {list(records[0].keys())}")
            
            # Full JSON structure for reference
            print(f"\nFull response (first 2000 chars):")
            print(json.dumps(data, indent=2)[:2000])
                    
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error: {e}")
            print(f"Response text (first 500 chars): {response.text[:500]}")
    else:
        print(f"Non-200 response: {response.text[:300]}")
        
except Exception as e:
    print(f"Error: {e}")

# Try common OI-related endpoints
print("\n" + "="*80)
print("Trying other potential OI endpoints")
print("="*80)

endpoints = [
    "/api/oistats",
    "/api/oi-stats",
    "/api/oiSpur",
    "/api/oistats?index=oi_spurts",
    "/market-data/oi-spurts",  # The HTML page - maybe we can parse it differently?
]

for endpoint in endpoints:
    if endpoint.startswith("http"):
        url = endpoint
    else:
        url = f"https://www.nseindia.com{endpoint}"
    
    print(f"\n✓ Testing: {url}")
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}, Size: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  ✓ JSON response, keys: {list(data.keys())[:3]}")
            except:
                # Check if it's HTML table data
                if '<table' in response.text.lower():
                    print(f"  Content: HTML with table")
                elif '{' in response.text:
                    print(f"  Content: Possibly JSON malformed")
                else:
                    print(f"  Content: {response.text[:100]}")
        
        time.sleep(1)
    except Exception as e:
        print(f"  Error: {str(e)[:60]}")
