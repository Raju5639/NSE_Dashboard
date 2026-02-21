"""
Debug script to find OI Spurts API endpoint and structure
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
print("Initializing session with NSE website...")
try:
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    time.sleep(2)
    print("✓ Session initialized\n")
except Exception as e:
    print(f"✗ Session init failed: {e}\n")

# Try different OI Spurts endpoints
endpoints = [
    "https://www.nseindia.com/api/oi-spurts",
    "https://www.nseindia.com/api/liveEquity-derivatives?index=oi_spurts",
    "https://www.nseindia.com/market-data/oi-spurts",
]

print("Trying different OI Spurts endpoints...\n")
print("=" * 80)

for endpoint in endpoints:
    print(f"\nTesting: {endpoint}")
    try:
        response = session.get(endpoint, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Valid JSON Response!")
                
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")
                    
                    # Try to find data array
                    if 'data' in data:
                        print(f"Data length: {len(data.get('data', []))}")
                        if data['data']:
                            print(f"\nFirst item:")
                            print(json.dumps(data['data'][0], indent=2))
                            break
                    else:
                        print(f"First 500 chars: {json.dumps(data)[:500]}")
                        
            except json.JSONDecodeError:
                print("Response is not JSON")
                print(f"First 200 chars: {response.text[:200]}")
        else:
            print(f"HTTP {response.status_code}")
            print(f"First 200 chars: {response.text[:200]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    time.sleep(1)

print("\n" + "=" * 80)
print("\nDone!")
