"""
Parse the OI Spurts HTML page to extract the table data
Since the website shows the data, we can parse it directly
"""
import requests
import re
import time
from html.parser import HTMLParser

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
time.sleep(2)

# Fetch the OI Spurts page
url = "https://www.nseindia.com/market-data/oi-spurts"
print(f"Fetching {url}...")

try:
    response = session.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Length: {len(response.text)} chars")
    
    if response.status_code == 200:
        content = response.text
        
        # Look for table data
        print("\n" + "="*80)
        print("Looking for table headers")
        print("="*80)
        
        # Find <th> tags for headers
        th_pattern = r'<th[^>]*>([^<]+)</th>'
        headers_found = re.findall(th_pattern, content, re.IGNORECASE)
        
        if headers_found:
            print(f"\nFound {len(headers_found)} table headers:")
            for i, header in enumerate(headers_found[:20]):  # Show first 20
                print(f"  {i+1}. {header.strip()}")
        
        # Look for table rows with data
        print("\n" + "="*80)
        print("Looking for table data rows")
        print("="*80)
        
        # Try to find <tr> tags with data
        tr_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(tr_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"Found {len(rows)} table rows")
        
        if rows:
            # Extract cells from first few rows
            for row_idx in range(min(3, len(rows))):
                row = rows[row_idx]
                td_pattern = r'<td[^>]*>([^<]*)</td>'
                cells = re.findall(td_pattern, row, re.IGNORECASE)
                
                if cells:
                    print(f"\nRow {row_idx + 1} ({len(cells)} cells):")
                    for cell_idx, cell in enumerate(cells[:10]):  # First 10 cells
                        print(f"  Cell {cell_idx + 1}: {cell.strip()[:50]}")
        
        # Look for JavaScript data objects
        print("\n" + "="*80)
        print("Looking for JavaScript data")
        print("="*80)
        
        # Look for common JS data patterns
        json_patterns = [
            r'var\s+data\s*=\s*(\[{[^;]+\]);',
            r'tableData\s*=\s*(\[{[^;]+\]);',
            r'"records":\s*(\[[^\]]+\])',
            r'(\[{.*?"openInterest".*?}\])',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"Found pattern match:")
                print(matches[0][:300])
                break
        
        # Look for any numeric OI data
        print("\n" + "="*80)
        print("Searching for OI-related JavaScript data")
        print("="*80)
        
        # Extract script tags
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"Found {len(scripts)} script blocks")
        
        # Check if data is embedded in scripts
        for i, script in enumerate(scripts):
            if len(script) > 1000 and len(script) < 100000:  # Reasonable size for data
                if any(keyword in script.lower() for keyword in ['oi', 'spurts', 'underlying', 'data']):
                    # Check for JSON-like structure
                    if '[{' in script or '{"' in script:
                        print(f"\nScript {i} contains data-like structure:")
                        # Try to extract JSON
                        json_match = re.search(r'(\[{.*?}\])', script, re.DOTALL)
                        if json_match:
                            print("Found potential JSON array:")
                            print(json_match.group(1)[:500])
                            break
        
        # Show relevant content snippets
        print("\n" + "="*80)
        print("Page structure summary")
        print("="*80)
        print(f"Total size: {len(content)} bytes")
        print(f"Contains <table>: {'<table' in content.lower()}")
        print(f"Contains <tbody>: {'<tbody' in content.lower()}")
        print(f"Contains 'openInterest': {'openInterest' in content}")
        print(f"Contains 'oi-spurts': {'oi-spurts' in content.lower()}")
        
except Exception as e:
    print(f"Error: {e}")
