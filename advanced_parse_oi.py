"""
More advanced parsing to find where OI Spurts table data is loaded from
Look for JavaScript fetch/axios calls and data structures
"""
import requests
import re
import time
import json as jsonlib

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
}

session = requests.Session()

# Initialize
print("Initializing session...")
session.get("https://www.nseindia.com", headers=headers, timeout=10)
time.sleep(2)

# Fetch the OI Spurts page
url = "https://www.nseindia.com/market-data/oi-spurts"
print(f"Fetching {url}...")

response = session.get(url, headers=headers, timeout=15)
content = response.text

print(f"Status: {response.status_code}, Size: {len(content)}")

# Strategy 1: Look for fetch/axios URLs
print("\n" + "="*80)
print("STRATEGY 1: Finding API calls in JavaScript")
print("="*80)

# Patterns for API calls
patterns = [
    r'fetch\s*\(\s*[\'"]([^\'"]+[\w/]+)[\'"]',
    r'axios\.get\s*\(\s*[\'"]([^\'"]+)[\'"]',
    r'url:\s*[\'"]([^\'"]+)[\'"]',
    r'"/api/[^"]*"',
    r"'/api/[^']*'",
]

found_urls = set()
for pattern in patterns:
    matches = re.findall(pattern, content)
    found_urls.update(matches)

print(f"Found {len(found_urls)} potential API URLs:")
for url in sorted(found_urls):
    if 'nseindia' in url or url.startswith('/api') or url.startswith('/market'):
        print(f"  • {url[:80]}")

# Strategy 2: Look for component/framework data
print("\n" + "="*80)
print("STRATEGY 2: Finding ReactJS/Angular data in window")
print("="*80)

# Look for React-like data structures
if 'window.__INITIAL_STATE__' in content:
    print("Found window.__INITIAL_STATE__")
    pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        print("Sample:", matches[0][:300])

if '__init' in content and 'state' in content:
    print("Found potential state initialization")

# Strategy 3: Look for table data
print("\n" + "="*80)
print("STRATEGY 3: Extracting table content")
print("="*80)

# Get the HTML around "Open Interest"
oi_index = content.find('Open Interest')
if oi_index > 0:
    print(f"Found 'Open Interest' at position {oi_index}")
    # Look at surrounding context
    start = max(0, oi_index - 500)
    end = min(len(content), oi_index + 1500)
    context = content[start:end]
    
    # Look for table rows nearby
    rows_nearby = re.findall(r'<tr[^>]*>.*?</tr>', context, re.DOTALL)
    if rows_nearby:
        print(f"Found {len(rows_nearby)} table rows near 'Open Interest'")
        for i, row in enumerate(rows_nearby[:2]):
            cells = re.findall(r'<td[^>]*>([^<]*)</td>', row)
            if cells:
                print(f"  Row {i+1}: {cells[:5]}")

# Strategy 4: Look for hidden data DIVs or script data variables
print("\n" + "="*80)
print("STRATEGY 4: Finding embedded data in DIVs or scripts")
print("="*80)

# Look for data attributes
data_attrs = re.findall(r'data-[\w-]+="([^"]*(?:oi|spurts|interest)[^"]*)"', content, re.IGNORECASE)
if data_attrs:
    print(f"Found {len(data_attrs)} data attributes mentioning OI:")
    for attr in data_attrs[:5]:
        print(f"  • {attr[:80]}")

# Look for specific table IDs or classes related to OI
table_patterns = [
    r'<table[^>]*id="[^"]*oi[^"]*"[^>]*>',
    r'<table[^>]*class="[^"]*oi[^"]*"[^>]*>',
    r'<table[^>]*id=".*?spurts.*?"[^>]*>',
]

for pattern in table_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        print(f"Found matching tables: {matches}")

# Strategy 5: Look specifically for the "Stock" names and OI numbers
print("\n" + "="*80)
print("STRATEGY 5: Finding stock symbols and OI values")
print("="*80)

# Common stock names might appear
stock_pattern = r'(?:RELIANCE|INFY|TCS|ITC|LT|HDFC|AXIS|ICICI|JBJART|WIPRO|M&M).*?(\d+)'
matches = re.findall(stock_pattern, content)
if matches:
    print(f"Found {len(matches)} potential stock references")

# Look for large numbers that could be OI
large_numbers = re.findall(r'>\s*(\d{7,})\s*<', content)
if large_numbers:
    print(f"Found {len(large_numbers)} potential OI values (7+ digits):")
    for num in large_numbers[:10]:
        print(f"  • {num}")

print("\n" + "="*80)
print("HTML excerpt around 'Open Interest':")
print("="*80)
if oi_index > 0:
    snippet = content[max(0, oi_index-200):min(len(content), oi_index+500)]
    print(snippet[:300])
