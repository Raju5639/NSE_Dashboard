"""
Test /api/option-chain-indices endpoint
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

# Test option-chain-indices endpoint
url = "https://www.nseindia.com/api/option-chain-indices"
print(f"\nFetching {url}...")

try:
    response = session.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"Content Length: {len(response.text)}")
    
    if response.status_code == 200:
        # Try to parse as JSON
        try:
            data = response.json()
            print(f"\n✓ Valid JSON response")
            print(f"Root keys: {list(data.keys())}")
            
            if 'records' in data:
                print(f"Records count: {len(data.get('records', []))}")
                if data['records']:
                    print(f"First record keys: {list(data['records'][0].keys())}")
                    print(f"First record:\n{json.dumps(data['records'][0], indent=2)}")
            
            elif 'data' in data:
                print(f"Data structure: {type(data['data'])}")
                if isinstance(data['data'], list):
                    print(f"Data count: {len(data['data'])}")
                    if data['data']:
                        print(f"First item keys: {list(data['data'][0].keys())}")
                        print(f"First item:\n{json.dumps(data['data'][0], indent=2)}")
            
            # Show sample data
            print(f"\nSample of first 3 top-level keys/values:")
            for key, value in list(data.items())[:3]:
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} (size: {len(value)})")
                else:
                    print(f"  {key}: {value}")
                    
        except json.JSONDecodeError:
            print(f"✗ Not JSON, first 500 chars:\n{response.text[:500]}")
    else:
        print(f"Response text (first 500 chars):\n{response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

# Also try with index parameter
print("\n" + "="*80)
print("Trying with index parameter...")
print("="*80)

for idx_param in ["oi_spurts", "NIFTY", "FINNIFTY"]:
    url_with_param = f"https://www.nseindia.com/api/option-chain-indices?index={idx_param}"
    print(f"\n✓ Testing with index={idx_param}")
    
    try:
        response = session.get(url_with_param, headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'records' in data:
                    print(f"  Records: {len(data['records'])} items")
                    if data['records']:
                        first = data['records'][0]
                        print(f"  Sample record keys: {list(first.keys())[:8]}")
                elif 'data' in data:
                    print(f"  Data type: {type(data['data'])}")
            except:
                print(f"  Non-JSON response")
        
        time.sleep(1)
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")
