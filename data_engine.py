import pandas as pd
from nsepython import nsefetch
import streamlit as st
import time

# ==========================================
# 1. SECTOR DATA
# ==========================================
@st.cache_data(ttl=5)
def get_all_sectors():
    """Fetches global sector list with Last Price and % Change."""
    try:
        data = nsefetch("https://www.nseindia.com/api/allIndices")
        df = pd.DataFrame(data['data'])
        sector_df = df[df['key'] == 'SECTORAL INDICES'].copy()
        
        final_df = sector_df[['index', 'last', 'percentChange']].rename(columns={
            "index": "Sector Name",
            "last": "Last Price",
            "percentChange": "% Change"
        })
        return final_df
    except Exception:
        return pd.DataFrame()

# ==========================================
# 2. DERIVATIVES (F&O) DATA CACHE
# ==========================================
@st.cache_data(ttl=5)
def get_fno_data():
    """Fetches F&O data ONCE and includes a debug check."""
    try:
        url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut"
        oi_payload = nsefetch(url)
        
        if oi_payload and 'data' in oi_payload:
            df_oi = pd.DataFrame(oi_payload['data'])
            
            # --- DEBUGGER: Look for this in your Streamlit Sidebar! ---
            st.sidebar.write("🔍 **Raw F&O Columns Found:**", df_oi.columns.tolist())
            st.sidebar.write("📊 **F&O Rows Fetched:**", len(df_oi))
            # ----------------------------------------------------------

            if not df_oi.empty and 'underlying' in df_oi.columns:
                df_oi['underlying'] = df_oi['underlying'].astype(str).str.strip().str.upper()
                df_oi = df_oi.drop_duplicates(subset=['underlying'], keep='first')
                return df_oi
                
        st.sidebar.error("❌ F&O Payload Empty. NSE blocked the derivatives request.")
        return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"❌ F&O Fetch Error: {e}")
        return pd.DataFrame()

# ==========================================
# 3. STOCK & OI MERGE LOGIC
# ==========================================
@st.cache_data(ttl=5)
def get_stock_data(sector_name):
    """Fetches and merges Equity and F&O data for a specific sector."""
    try:
        # 1. Fetch Lightweight Equity Data
        sector_slug = sector_name.strip().replace(' ', '%20').replace('&', '%26')
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={sector_slug}"
        
        payload = nsefetch(url)
        if not payload or 'data' not in payload:
            return pd.DataFrame()
            
        df_eq = pd.DataFrame(payload['data'])
        
        # Remove the index aggregate row
        if 'symbol' in df_eq.columns:
            df_eq = df_eq[df_eq['symbol'] != sector_name.strip()]
            df_eq['symbol'] = df_eq['symbol'].astype(str).str.strip().str.upper()
        else:
            return pd.DataFrame()

        # 2. Retrieve globally cached F&O data
        df_oi = get_fno_data()

        # 3. Safely Merge Data
        if not df_oi.empty:
            merged = pd.merge(df_eq, df_oi, left_on='symbol', right_on='underlying', how='left')
        else:
            merged = df_eq.copy()

        # 4. Map the requested columns using a fallback scan
        final = pd.DataFrame({
            "Symbol": merged['symbol'],
            "Price": merged.get('lastPrice_x', merged.get('lastPrice', 0)),
            "Volume": merged.get('totalTradedVolume', 0),
            
            # If the standard keys aren't found, it falls back to 0
            "OI": merged.get('openInterest', merged.get('OI', 0)),
            "OI Change": merged.get('changeinOpenInterest', merged.get('chnginOpenInterest', 0)),
            "OI % Change": merged.get('pchangeinOpenInterest', merged.get('pChange', 0))
        })
        
        final.fillna(0, inplace=True)
        return final
    except Exception as e:
        st.sidebar.error(f"❌ Merging Error: {e}")
        return pd.DataFrame()