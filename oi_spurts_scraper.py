"""
Web scraping solution for OI Spurts data using Selenium
Since NSE loads the table dynamically, we need browser automation
Supports both Chrome and Brave browsers
"""

import pandas as pd
import time
import os
import re

# Module-level debug log for last fetch
oi_spurts_last_debug = []

def find_brave_browser():
    """Find Brave browser executable path"""
    possible_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Users\{}\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe".format(os.getenv("USERNAME")),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found Brave at: {path}")
            return path
    
    return None

def find_chrome_browser():
    """Find Chrome browser executable path"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv("USERNAME")),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found Chrome at: {path}")
            return path
    
    return None

def get_oi_spurts_data_selenium():
    """
    Fetch OI Spurts data using Selenium with Brave or Chrome browser
    Returns DataFrame with columns matching NSE website:
    - Symbol
    - Open Interest (Current Date -1)
    - Open Interest (Current Date)
    - Chng in OI
    - %Chng in OI
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Selenium not installed. Install with: pip install selenium")
        return pd.DataFrame()
    
    try:
        # Setup browser options (works for Chrome/Brave)
        browser_options = Options()
        browser_options.add_argument("--headless=new")
        browser_options.add_argument("--no-sandbox")
        browser_options.add_argument("--disable-dev-shm-usage")
        browser_options.add_argument("--disable-blink-features=AutomationControlled")
        browser_options.add_argument("--disable-gpu")
        browser_options.add_argument("window-size=1920,1080")
        browser_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        # Prefer webdriver-manager to auto-download driver; fall back to local driver
        driver = None
        try:
            from selenium.webdriver.chrome.service import Service
            try:
                # Use webdriver-manager if installed
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=browser_options)
            except Exception:
                # webdriver-manager not available or failed; try default driver
                brave_path = find_brave_browser()
                chrome_path = find_chrome_browser()
                if brave_path:
                    browser_options.binary_location = brave_path
                elif chrome_path:
                    browser_options.binary_location = chrome_path
                driver = webdriver.Chrome(options=browser_options)
        except Exception as e:
            print(f"Could not initialize Chrome webdriver: {e}")
            return pd.DataFrame()

        try:
            # Load the OI Spurts page
            url = "https://www.nseindia.com/market-data/oi-spurts"
            driver.get(url)

            # Wait for table to load
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

            # Give additional time to ensure all data loads
            time.sleep(2)

            # Extract table rows
            rows = driver.find_elements(By.TAG_NAME, "tr")
            if len(rows) <= 1:
                print("No table rows found")
                return pd.DataFrame()

            # Parse headers
            headers = []
            header_row = rows[0]
            for th in header_row.find_elements(By.TAG_NAME, "th"):
                headers.append(th.text.strip())

            # If no headers found, try td
            if not headers:
                for td in header_row.find_elements(By.TAG_NAME, "td"):
                    headers.append(td.text.strip())

            # Parse data rows
            data = []
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    if len(row_data) >= 1:
                        data.append(row_data)

            if not data:
                print("No data rows found")
                return pd.DataFrame()

            # Create DataFrame
            df = pd.DataFrame(data, columns=headers[:len(data[0])])

            # Convert numeric-like columns where likely
            numeric_cols = [col for col in df.columns if any(x in col.lower() for x in ['interest', 'chng', 'chg', 'change', '%'])]
            for col in numeric_cols:
                try:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                except Exception:
                    pass

            print(f"Successfully extracted {len(df)} rows of OI Spurts data")
            return df
        finally:
            try:
                driver.quit()
            except Exception:
                pass
    
    except Exception as e:
        print(f"Error scraping OI Spurts data: {e}")
        return pd.DataFrame()


def get_oi_spurts_beautifulsoup():
    """
    Alternative approach using BeautifulSoup for static content
    (Limited since much of the page is dynamically loaded)
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
        return pd.DataFrame()
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Encoding": "identity",
        }
        
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        time.sleep(1)
        
        url = "https://www.nseindia.com/market-data/oi-spurts"
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return pd.DataFrame()
        
        # Extract headers
        headers = []
        for th in table.find_all('th'):
            headers.append(th.text.strip())
        
        # Extract rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            cells = []
            for td in tr.find_all('td'):
                cells.append(td.text.strip())
            if cells:
                rows.append(cells)
        
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
        # Try to normalize numeric columns
        for col in df.columns:
            try:
                if any(x in col.lower() for x in ['chng', 'chg', 'change', '%']):
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
            except Exception:
                pass
        # Normalize column names to canonical OI spurts columns
        return normalize_oi_spurts_df(df)
    
    except Exception as e:
        print(f"Error with BeautifulSoup approach: {e}")
        return pd.DataFrame()


def get_oi_spurts_requests():
    """
    Robust requests-based fetcher for OI Spurts using NSE session + possible API endpoints.
    Tries the public page and several likely JSON endpoints, returns a DataFrame.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("requests/BeautifulSoup not installed. Install with: pip install requests beautifulsoup4")
        return pd.DataFrame()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    try:
        # Seed cookies with proper headers
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        oi_spurts_last_debug.append("Seeded NSE session")
    except Exception:
        oi_spurts_last_debug.append("Failed to seed NSE session")
        pass

    # First, try direct API endpoint (might not exist, but worth trying)
    direct_api_urls = [
        "https://www.nseindia.com/api/oi-spurts",
        "https://www.nseindia.com/api/oi-spurts-data",
        "https://www.nseindia.com/api/derivative-oi-spurts",
    ]
    
    for url in direct_api_urls:
        try:
            r = session.get(url, headers=headers, timeout=10)
            oi_spurts_last_debug.append(f"Direct API {url.split('/')[-1]}: {r.status_code}")
            if r.status_code == 200:
                try:
                    j = r.json()
                    if isinstance(j, list) and j:
                        # Try to create DataFrame from JSON list
                        df = pd.DataFrame(j)
                        normalized = normalize_oi_spurts_df(df)
                        if not normalized.empty:
                            oi_spurts_last_debug.append(f"Fetched {len(normalized)} rows from {url}")
                            return normalized
                    elif isinstance(j, dict) and 'data' in j:
                        df = pd.DataFrame(j['data']) if isinstance(j['data'], list) else pd.DataFrame()
                        if not df.empty:
                            normalized = normalize_oi_spurts_df(df)
                            if not normalized.empty:
                                oi_spurts_last_debug.append(f"Fetched {len(normalized)} rows from {url} (data wrapper)")
                                return normalized
                except:
                    pass
        except Exception as e:
            oi_spurts_last_debug.append(f"Direct API {url.split('/')[-1]} failed: {str(e)[:50]}")

    # Try fetching and parsing the OI Spurts page itself
    try:
        # Try with different page variants
        urls_to_try = [
            "https://www.nseindia.com/market-data/oi-spurts",
            "https://nseindia.com/market-data/open-interest-spurts",
        ]
        
        for url_page in urls_to_try:
            try:
                r = session.get(url_page, headers=headers, timeout=15)
                oi_spurts_last_debug.append(f"GET {url_page.split('/')[-1]}: {r.status_code}")
                
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    
                    # Try finding table
                    table = soup.find('table')
                    if table:
                        headers_row = [th.text.strip() for th in table.find_all('th')]
                        rows = []
                        for tr in table.find_all('tr')[1:]:
                            cells = [td.text.strip() for td in tr.find_all('td')]
                            if cells:
                                rows.append(cells)
                        if rows:
                            oi_spurts_last_debug.append(f"Parsed table: {len(rows)} rows, {len(headers_row)} columns")
                            df = pd.DataFrame(rows, columns=headers_row[:len(rows[0])])
                            normalized = normalize_oi_spurts_df(df)
                            if not normalized.empty:
                                return normalized
                    
                    # Try looking for data in script tags (JSON embedded in page)
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and ('oi' in script.string.lower() or 'symbol' in script.string.lower()):
                            try:
                                # Try to extract JSON from script content
                                import json
                                import re
                                # Look for JSON arrays or objects
                                json_matches = re.findall(r'\[\s*\{[^}]*\}[^]]*\]', script.string)
                                for match in json_matches:
                                    try:
                                        data_list = json.loads(match)
                                        if data_list and isinstance(data_list, list):
                                            df = pd.DataFrame(data_list)
                                            normalized = normalize_oi_spurts_df(df)
                                            if not normalized.empty:
                                                oi_spurts_last_debug.append(f"Extracted JSON from script: {len(normalized)} rows")
                                                return normalized
                                    except:
                                        pass
                            except:
                                pass
            except Exception as e:
                oi_spurts_last_debug.append(f"Page fetch {url_page.split('/')[-1]}: {str(e)[:50]}")
                
    except Exception as e:
        oi_spurts_last_debug.append(f"Page parsing failed: {str(e)[:50]}")

    # Try BSE fallback
    try:
        bse_df = get_oi_spurts_bse()
        if bse_df is not None and not bse_df.empty:
            oi_spurts_last_debug.append(f"Using BSE fallback: {len(bse_df)} rows")
            return bse_df
    except Exception as e:
        oi_spurts_last_debug.append(f"BSE fallback error: {str(e)[:50]}")

    # If all else fails, return empty DataFrame
    oi_spurts_last_debug.append("No OI Spurts data available from NSE or BSE")
    return pd.DataFrame()


def get_oi_spurts_bse():
    """
    Try to fetch OI-like data from BSE public APIs as a fallback.
    This will try a set of candidate endpoints and normalize any JSON/tabular responses.
    """
    try:
        import requests
    except Exception as e:
        oi_spurts_last_debug.append(f"requests not available for BSE fetch: {e}")
        return pd.DataFrame()

    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    # Candidate BSE endpoints (best-effort list)
    bse_candidates = [
        "https://api.bseindia.com/BseIndiaAPI/api/DerivativesOI/w",
        "https://api.bseindia.com/BseIndiaAPI/api/DerivativesOI",
        "https://api.bseindia.com/BseIndiaAPI/api/Derivatives/ProActiveOI",
        "https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w",
    ]

    for ep in bse_candidates:
        try:
            r = session.get(ep, headers=headers, timeout=10)
            oi_spurts_last_debug.append(f"BSE GET {ep} -> {r.status_code}")
            if r.status_code != 200:
                continue

            # Try JSON
            try:
                j = r.json()
                # If it's dict with 'data' list, normalize
                if isinstance(j, dict) and 'data' in j and isinstance(j['data'], list):
                    df = pd.json_normalize(j['data'])
                    oi_spurts_last_debug.append(f"BSE JSON normalized from {ep}, rows={len(df)}")
                    return normalize_oi_spurts_df(df)
                # If it's a list of dicts
                if isinstance(j, list) and j and isinstance(j[0], dict):
                    df = pd.json_normalize(j)
                    oi_spurts_last_debug.append(f"BSE JSON list normalized from {ep}, rows={len(df)}")
                    return normalize_oi_spurts_df(df)
            except Exception as je:
                # Try to parse as table if HTML
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(r.text, 'html.parser')
                    table = soup.find('table')
                    if table:
                        headers_row = [th.text.strip() for th in table.find_all('th')]
                        rows = []
                        for tr in table.find_all('tr')[1:]:
                            cells = [td.text.strip() for td in tr.find_all('td')]
                            if cells:
                                rows.append(cells)
                        if rows:
                            df = pd.DataFrame(rows, columns=headers_row[:len(rows[0])])
                            oi_spurts_last_debug.append(f"BSE HTML table parsed from {ep}, rows={len(df)}")
                            return normalize_oi_spurts_df(df)
                except Exception as he:
                    oi_spurts_last_debug.append(f"BSE endpoint {ep} parse failed: {he}")
                    continue
        except Exception as e:
            oi_spurts_last_debug.append(f"BSE endpoint {ep} request failed: {e}")

    return pd.DataFrame()


# For backwards compatibility, make selenium-based function call the requests-based fetcher
def get_oi_spurts_data_selenium():
    return get_oi_spurts_requests()


def normalize_oi_spurts_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize various header formats to canonical columns:
    - Symbol
    - Chng in OI
    - %Chng in OI
    Returns dataframe with only available canonical columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    column_mapping = {}
    for col in df.columns:
        col_lower = str(col).lower()
        norm = re.sub(r"\s+", "", col_lower)
        norm = norm.replace('\u00a0', '')

        if 'symbol' in norm:
            column_mapping[col] = 'Symbol'
            continue

        # Absolute OI change
        if ('chng' in norm or 'chg' in norm or 'change' in norm) and 'oi' in norm and '%' not in norm and 'percent' not in norm:
            column_mapping[col] = 'Chng in OI'
            continue

        # Percent OI change
        if (('%' in norm or 'percent' in norm) and ('chng' in norm or 'chg' in norm or 'change' in norm) and 'oi' in norm):
            column_mapping[col] = '%Chng in OI'
            continue

    df = df.rename(columns=column_mapping)

    # Keep only canonical columns if present
    keep = [c for c in ['Symbol', 'Chng in OI', '%Chng in OI'] if c in df.columns]
    if not keep:
        return pd.DataFrame()

    df = df[keep].copy()

    # Clean Symbol and numeric columns
    if 'Symbol' in df.columns:
        df['Symbol'] = df['Symbol'].astype(str).str.upper().str.strip()
    if 'Chng in OI' in df.columns:
        df['Chng in OI'] = pd.to_numeric(df['Chng in OI'].astype(str).str.replace(',', ''), errors='coerce')
    if '%Chng in OI' in df.columns:
        df['%Chng in OI'] = pd.to_numeric(df['%Chng in OI'].astype(str).str.replace('%', '').str.replace(',', ''), errors='coerce')

    # Log final normalized columns
    try:
        oi_spurts_last_debug.append(f"Normalized columns: {list(df.columns)}; rows: {len(df)}")
    except Exception:
        pass

    return df

