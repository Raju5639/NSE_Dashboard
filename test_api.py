"""
Diagnostic script to test NSE API endpoints and inspect actual responses
"""
import requests
import json
import time
import gzip

# Set up session exactly like data_engine.py
session = requests.Session()

base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

api_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

# Also try without compression
api_headers_no_compress = api_headers.copy()
api_headers_no_compress["Accept-Encoding"] = "identity"

print("=" * 80)
print("NSE API DIAGNOSTIC TEST")
print("=" * 80)

# Step 1: Initialize session
print("\n[Step 1] Initializing session with NSE homepage...")
try:
    homepage = session.get("https://www.nseindia.com", headers=base_headers, timeout=10)
    print(f"✅ Homepage loaded: {homepage.status_code}")
    print(f"   Cookies set: {len(session.cookies)} cookies")
    time.sleep(1.5)
except Exception as e:
    print(f"❌ Failed to load homepage: {e}")

# Step 2: Test different API endpoints
test_endpoints = [
    ("Indices API (with compression)", "https://www.nseindia.com/api/allIndices", api_headers),
    ("Indices API (no compression)", "https://www.nseindia.com/api/allIndices", api_headers_no_compress),
    ("Market Open API", "https://www.nseindia.com/api/getMarketStatus", api_headers_no_compress),
    ("Equity Market Data", "https://www.nseindia.com/api/equity-markets", api_headers_no_compress),
]

for endpoint_name, endpoint_url, headers in test_endpoints:
    print(f"\n{'=' * 80}")
    print(f"[Testing] {endpoint_name}")
    print(f"URL: {endpoint_url}")
    print("-" * 80)
    
    try:
        time.sleep(1)  # Human-like delay
        response = session.get(endpoint_url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
        
        if response.status_code == 200:
            try:
                # Try to get text directly (requests should auto-decompress)
                text_content = response.text
                
                # If it looks like gzip, try manual decompression
                if text_content.startswith('\x1f\x8b'):
                    print("Detected GZIP, decompressing...")
                    text_content = gzip.decompress(response.content).decode('utf-8')
                
                data = json.loads(text_content)
                print(f"✅ Response Type: JSON")
                print(f"Response Size: {len(str(data))} bytes")
                print(f"\nTop-level keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                
                # Print response for inspection
                print(f"\nFull Response:")
                print(json.dumps(data, indent=2)[:2000])
                if len(json.dumps(data, indent=2)) > 2000:
                    print("...[truncated]")
                
            except Exception as e:
                print(f"❌ Error parsing response: {e}")
                print(f"Raw response (first 500 chars): {response.text[:500]}")
        
        elif response.status_code in [401, 403]:
            print(f"⚠️  Access Denied (Status {response.status_code}) - WAF/Firewall Issue")
        
        elif response.status_code == 404:
            print(f"❌ Endpoint not found (404)")
        
        elif response.status_code == 429:
            print(f"⚠️  Rate Limited (429) - Try again later")
        
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    
    except requests.exceptions.Timeout:
        print(f"❌ Timeout - API took too long to respond")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Check internet connection")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
