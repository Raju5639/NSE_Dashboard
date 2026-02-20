import pandas as pd
from nsepython import nsefetch
import time
import streamlit as st

@st.cache_data(ttl=2)
def get_all_sectors():
    """Fetches global sector list with Last Price and % Change."""
    try:
        data = nsefetch("https://www.nseindia.com/api/allIndices")
        df = pd.DataFrame(data['data'])
        sector_df = df[df['key'] == 'SECTORAL INDICES'].copy()
        
        # Rename columns specifically for the UI requirements
        final_df = sector_df[['index', 'last', 'percentChange']].rename(columns={
            "index": "Sector Name",
            "last": "Last Price",
            "percentChange": "% Change"
        })
        return final_df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=2)
def get_stock_data(sector_name):
    """Fetches Volume, OI Change, OI % Change, and Price for a specific sector."""
    try:
        # 1. Fetch Equity Data
        sector_slug = sector_name.strip().replace(' ', '%20').replace('&', '%26')
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={sector_slug}"
        
        payload = nsefetch(url)
        if not payload or 'data' not in payload:
            return pd.DataFrame()
            
        df_eq = pd.DataFrame(payload['data'])
        
        # Remove the index aggregate row
        if 'symbol' in df_eq.columns:
            df_eq = df_eq[df_eq['symbol'] != sector_name.strip()]

        # Prevent NSE API throttling
        time.sleep(0.5)

        # 2. Fetch Derivatives Data (OI)
        oi_payload = nsefetch("https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut")
        df_oi = pd.DataFrame(oi_payload['data']) if oi_payload and 'data' in oi_payload else pd.DataFrame()

        # 3. Clean symbols and Merge Safely
        df_eq['symbol'] = df_eq['symbol'].astype(str).str.strip().str.upper()
        
        if not df_oi.empty and 'underlying' in df_oi.columns:
            df_oi['underlying'] = df_oi['underlying'].astype(str).str.strip().str.upper()
            
            # Drop far-month expiries to prevent duplicate rows
            df_oi = df_oi.drop_duplicates(subset=['underlying'], keep='first')
            merged = pd.merge(df_eq, df_oi, left_on='symbol', right_on='underlying', how='left')
        else:
            merged = df_eq.copy()

        # 4. Map the requested columns
        final = pd.DataFrame({
            "Symbol": merged['symbol'],
            "Price": merged.get('lastPrice_x', merged.get('lastPrice', 0)),
            "Volume": merged.get('totalTradedVolume', 0),
            "OI Change": merged.get('changeinOpenInterest', 0),
            "OI % Change": merged.get('pchangeinOpenInterest', 0)
        })
        
        # Replace NaNs with 0 for non-F&O stocks
        final.fillna(0, inplace=True)
        return final
    except Exception as e:
        return pd.DataFrame()