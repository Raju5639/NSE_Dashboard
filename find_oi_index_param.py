"""
Debug script to find the right liveEquity-derivatives parameters for OI
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

# Try different index parameters for liveEquity-derivatives
indices = [
    "stock_opt",
    "oi_spurts",
    "oi-spurts",
    "all",
    "NIFTY%2050",
    "NIFTY",
]

print("Trying different index parameters for liveEquity-derivatives endpoint:\n")
print("=" * 80)

for idx in indices:
    url = f"https://www.nseindia.com/api/liveEquity-derivatives?index={idx}"
    print(f"\n✓ Testing index='{idx}'")
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if isinstance(data, dict) and 'data' in data:
                    records = data.get('data', [])
                    print(f"  ✓ Status 200, Found {len(records)} records")
                    
                    if records:
                        # Show first record's fields
                        first_record = records[0]
                        fields = list(first_record.keys())
                        print(f"  Fields: {fields}")
                        
                        # Check for date-related fields
                        for field in fields:
                            if 'date' in field.lower() or 'oi' in field.lower() or 'chng' in field.lower():
                                print(f"    - {field}: {first_record.get(field)}")
                else:
                    print(f"  ✗ Response structure unexpected: {type(data)}")
            except json.JSONDecodeError:
                print(f"  ✗ Invalid JSON response")
        else:
            print(f"  ✗ HTTP {response.status_code}")
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
    
    time.sleep(1)

print("\n" + "=" * 80)
