"""
Fetch the OI Spurts webpage and extract the actual API endpoint from JavaScript
"""
import requests
import re
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
}

session = requests.Session()

# Initialize session
print("Initializing session...")
session.get("https://www.nseindia.com", headers=headers, timeout=10)
time.sleep(1)

# Fetch the OI Spurts page
url = "https://www.nseindia.com/market-data/oi-spurts"
print(f"Fetching {url}...")

try:
    response = session.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Search for API endpoints in the response
        print("\n" + "="*80)
        print("Searching for API calls in page content...")
        print("="*80)
        
        # Look for common API patterns
        api_patterns = [
            r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',  # fetch() calls
            r'\.get\s*\(\s*[\'"]([^\'"]+)[\'"]',   # axios.get() calls
            r'url:\s*[\'"]([^\'"]+)[\'"]',         # url properties
            r'api/[a-zA-Z0-9\-_/]+',               # /api/* patterns
            r'nseindia\.com/api/[a-zA-Z0-9\-_/]+', # full nseindia API URLs
        ]
        
        found_apis = set()
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'nseindia' in match.lower() or match.startswith('/api'):
                    if 'javascript' not in match.lower() and 'css' not in match.lower():
                        found_apis.add(match)
        
        if found_apis:
            print(f"\nFound {len(found_apis)} API references:\n")
            for api in sorted(found_apis):
                print(f"  • {api}")
        else:
            print("\nNo obvious API endpoints found in page source")
        
        # Look for script tags that might contain API data
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"\n" + "="*80)
        print(f"Found {len(scripts)} script blocks")
        print("="*80)
        
        # Search for data endpoints in scripts
        print("\nSearching for API/data patterns in scripts:")
        
        for i, script in enumerate(scripts):
            # Skip if too large (likely external script)
            if len(script) > 5000:
                continue
            
            if 'oi' in script.lower() or 'api' in script.lower() or 'fetch' in script.lower():
                # Extract relevant lines
                lines = script.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['api', 'oi', 'fetch', '/data', 'endpoint']):
                        line = line.strip()
                        if line and not line.startswith('//'):
                            print(f"  {line[:120]}")
        
        # Try to find data URLs in specific patterns
        print(f"\n" + "="*80)
        print("Checking for common NSE API endpoints related to options/OI:")
        print("="*80)
        
        endpoints_to_try = [
            "/api/option-chain-indices",
            "/api/option-chain",
            "/api/derivatives-statistics",
            "/api/oi-statistics",
            "/api/derivatives-data",
            "/api/getOptionData",
            "/api/equity-derivatives",
        ]
        
        print("\nTrying alternative endpoints...")
        for endpoint in endpoints_to_try:
            test_url = f"https://www.nseindia.com{endpoint}"
            try:
                resp = session.get(test_url + "?index=oi_spurts", headers=headers, timeout=10)
                if resp.status_code == 200:
                    print(f"  ✓ {endpoint} (200 OK)")
                    # Try to parse
                    try:
                        data = resp.json()
                        print(f"    Returns JSON with keys: {list(data.keys())[:5]}")
                    except:
                        print(f"    Returns non-JSON data")
                elif resp.status_code != 500:
                    print(f"  ! {endpoint} ({resp.status_code})")
            except:
                pass
            time.sleep(0.5)
        
except Exception as e:
    print(f"Error: {e}")
