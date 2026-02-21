"""
Try to fetch the OI table using BeautifulSoup
Since we can't find an API, let's parse the HTML table directly
"""
import requests
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)
time.sleep(2)

url = "https://www.nseindia.com/market-data/oi-spurts"
print(f"Fetching {url}...")
response = session.get(url, headers=headers, timeout=15)

if response.status_code == 200:
    # Try BeautifulSoup parsing
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Find the main content table
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            if rows:
                print(f"\nTable {table_idx} has {len(rows)} rows")
                
                # Get headers
                headers_row = rows[0]
                headers_cells = headers_row.find_all(['th', 'td'])
                headers_text = [th.get_text(strip=True) for th in headers_cells]
                print(f"Headers: {headers_text[:8]}")
                
                # Get first few data rows
                if len(rows) > 1:
                    for row_idx in range(1, min(4, len(rows))):
                        cells = rows[row_idx].find_all('td')
                        if cells:
                            cells_text = [td.get_text(strip=True) for td in cells]
                            print(f"Row {row_idx}: {cells_text[:8]}")
    
    except ImportError:
        print("BeautifulSoup not installed, trying regex")
        import re
        
        # Extract table with all content
        table_match = re.search(r'<table[^>]*>(.*?)</table>', response.text, re.DOTALL)
        if table_match:
            table_html = table_match.group(1)
            
            # Find headers
            headers_pattern = r'<th[^>]*>([^<]+)</th>'
            headers_list = re.findall(headers_pattern, table_html, re.IGNORECASE)
            print(f"Table headers found: {headers_list[:10]}")
            
            # Find rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table_html, re.DOTALL | re.IGNORECASE)
            
            print(f"Table rows found: {len(rows)}")
            
            # Extract first few rows
            for row_idx in range(min(3, len(rows))):
                cell_pattern = r'<td[^>]*>([^<]*)</td>'
                cells = re.findall(cell_pattern, rows[row_idx], re.IGNORECASE)
                if cells:
                    print(f"Row {row_idx + 1}: {cells[:6]}")

else:
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
