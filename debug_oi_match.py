"""
Debug script to check why OI data is not matching with stocks
"""
import requests
import json
import time
import urllib.parse

session = requests.Session()
base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive',
}

api_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/market-data/oi-spurts',
    'X-Requested-With': 'XMLHttpRequest',
}

print("Initializing session...")
session.get('https://www.nseindia.com', headers=base_headers, timeout=10)
time.sleep(1.5)

# Get sector stocks
print("\n" + "="*100)
print("FETCHING SECTOR STOCKS")
print("="*100)

sector_name = "NIFTY AUTO"
encoded_sector = urllib.parse.quote(sector_name)
url_stocks = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded_sector}"

resp_stocks = session.get(url_stocks, headers=api_headers, timeout=15)
if resp_stocks.status_code == 200:
    stocks_data = resp_stocks.json()
    stocks = []
    if 'data' in stocks_data:
        for item in stocks_data['data']:
            if item.get('priority') == 0:  # Only main index entry
                pass
            else:
                stocks.append(item.get('symbol'))
    
    print(f"Stocks in {sector_name}: {len(stocks_data['data']) if 'data' in stocks_data else 0}")
    print(f"Symbols: {stocks_data['data'][0].get('symbol') if stocks_data.get('data') else 'N/A'}")
    print("\nAll stock symbols:")
    for i, item in enumerate(stocks_data['data'][:10]):
        print(f"  {i+1}. {item.get('symbol')} (priority: {item.get('priority')})")

# Get OI data
print("\n" + "="*100)
print("FETCHING OPTIONS OI DATA")
print("="*100)

url_oi = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt"
resp_oi = session.get(url_oi, headers=api_headers, timeout=15)

if resp_oi.status_code == 200:
    oi_data = resp_oi.json()
    if 'data' in oi_data:
        print(f"Total options records: {len(oi_data['data'])}")
        
        # Group by underlying
        underlying_set = {}
        for item in oi_data['data']:
            underlying = item.get('underlying', '')
            if underlying:
                if underlying not in underlying_set:
                    underlying_set[underlying] = 0
                underlying_set[underlying] += 1
        
        print(f"Unique stocks with options: {len(underlying_set)}")
        print("\nStocks with OI data (first 20):")
        for i, (stock, count) in enumerate(list(underlying_set.items())[:20]):
            print(f"  {i+1}. {stock} (contracts: {count})")
        
        # Check overlap
        print("\n" + "="*100)
        print("CHECKING OVERLAP")
        print("="*100)
        
        if stocks_data.get('data'):
            sector_stocks_set = set([item.get('symbol') for item in stocks_data['data']])
            print(f"Stocks in sector: {len(sector_stocks_set)}")
            print(f"Stocks with OI: {len(underlying_set)}")
            
            overlap = sector_stocks_set.intersection(set(underlying_set.keys()))
            print(f"Overlapping stocks: {len(overlap)}")
            
            print("\nStocks in sector WITH OI:")
            for stock in sorted(overlap):
                print(f"  ✓ {stock}")
            
            print("\nStocks in sector WITHOUT OI:")
            no_oi = sector_stocks_set - set(underlying_set.keys())
            for stock in sorted(no_oi)[:10]:
                print(f"  ✗ {stock}")
            if len(no_oi) > 10:
                print(f"  ... and {len(no_oi)-10} more")
