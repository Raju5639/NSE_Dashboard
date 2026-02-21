"""
Debug script to check actual OI API response structure
"""
import requests
import json
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
}

session = requests.Session()

# Initialize session
print("Initializing session...")
try:
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    time.sleep(2)
    print("✓ Session initialized\n")
except Exception as e:
    print(f"✗ Session init failed: {e}\n")

# Fetch OI data
print("Fetching OI data from stock_opt endpoint...")
url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt"

try:
    response = session.get(url, headers=headers, timeout=15)
    print(f"✓ Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            print(f"✓ Found {len(data['data'])} records\n")
            
            # Show first few items with all fields
            print("=" * 80)
            print("FIRST 3 ITEMS (All Fields):")
            print("=" * 80)
            for idx, item in enumerate(data['data'][:3]):
                print(f"\nRecord {idx + 1}:")
                print(json.dumps(item, indent=2))
            
            # Group by underlying and show aggregated data
            print("\n" + "=" * 80)
            print("UNIQUE SYMBOLS (Aggregated by underlying):")
            print("=" * 80)
            underlying_oi = {}
            for item in data['data']:
                underlying = item.get('underlying', '')
                if underlying:
                    if underlying not in underlying_oi:
                        underlying_oi[underlying] = {
                            "underlying": underlying,
                            "count": 1,
                            "first_item": item
                        }
                    else:
                        underlying_oi[underlying]["count"] += 1
            
            print(f"\nFound {len(underlying_oi)} unique symbols:\n")
            for symbol, data_dict in list(underlying_oi.items())[:5]:
                print(f"\n{symbol} (count: {data_dict['count']})")
                print(f"  Fields: {list(data_dict['first_item'].keys())}")
                print(f"  Sample data: {json.dumps(data_dict['first_item'], indent=4)}")
        else:
            print("✗ No data found in response")
    else:
        print(f"✗ HTTP {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
