import streamlit as st
import pandas as pd
import requests
import time
import random
from streamlit_autorefresh import st_autorefresh

# ==========================================
# SECTION 1: PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Intraday Trading Terminal", layout="wide")

# ==========================================
# SECTION 2: THE "ANTI-BLOCK" NSE ENGINE
# ==========================================
class NSEConnection:
    def __init__(self):
        # Fake browser headers to prevent NSE from blocking us
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.initialize_session()

    def initialize_session(self):
        try:
            self.session.get("https://www.nseindia.com", timeout=10)
        except:
            pass

    def fetch_data(self, url):
        # Humanized delay before requesting data (0.5 to 1.5 seconds)
        time.sleep(random.uniform(0.5, 1.5)) 
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 401:
                self.initialize_session()
                response = self.session.get(url, timeout=10)
            return response.json()
        except Exception as e:
            return None

# Initialize the connection once per session
if 'nse' not in st.session_state:
    st.session_state.nse = NSEConnection()

nse = st.session_state.nse

# ==========================================
# SECTION 3: DATA FETCHING LOGIC
# ==========================================
@st.cache_data(ttl=60) 
def get_all_sectors_data():
    """Fetches ALL sectors to show on the main page."""
    url = "https://www.nseindia.com/api/allIndices"
    data = nse.fetch_data(url)
    
    sectors = []
    if data and 'data' in data:
        for item in data['data']:
            if item.get('key') == 'SECTORAL INDICES':
                sectors.append({
                    "Sector Name": item.get('index'),
                    "Current Value": item.get('last'),
                    "Change %": item.get('percentChange')
                })
    return pd.DataFrame(sectors)

def get_sector_stocks(sector_name):
    """Fetches company details for the selected sector."""
    import urllib.parse
    encoded_sector = urllib.parse.quote(sector_name)
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded_sector}"
    data = nse.fetch_data(url)
    
    stocks = []
    if data and 'data' in data:
        for item in data['data']:
            if item.get('priority') == 0: 
                stocks.append({
                    "Company Name": item.get('symbol'),
                    "Price": item.get('lastPrice'),
                    "Change %": item.get('pChange'),
                    "Volume": item.get('totalTradedVolume')
                })
    return pd.DataFrame(stocks)

def get_futures_oi():
    """Fetches Open Interest for F&O stocks."""
    url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut"
    data = nse.fetch_data(url)
    
    oi_data = []
    if data and 'data' in data:
        for item in data['data']:
            if 'Fut' in item.get('instrumentType', '') and item.get('isCurrentExpiery'):
                oi_data.append({
                    "Company Name": item.get('underlying'),
                    "OI": item.get('openInterest'),
                    "OI Change %": item.get('pchangeinOpenInterest')
                })
    return pd.DataFrame(oi_data)

# ==========================================
# SECTION 4: THE DASHBOARD UI
# ==========================================

# 1. HUMANIZED BACKGROUND REFRESH (Randomized between 10 to 20 seconds)
humanized_refresh_time = random.randint(10000, 20000)
st_autorefresh(interval=humanized_refresh_time, key=f"refresh_{humanized_refresh_time}")

st.title("⚡ Live Intraday Terminal")

# --- PART 1: SHOW ALL SECTORS ---
df_all_sectors = get_all_sectors_data()

if not df_all_sectors.empty:
    st.subheader("🌐 Global Sector Performance")
    st.info("💡 **Tip:** You can click on the column headers (like 'Change %') to sort the table from High to Low!")
    
    def highlight_numbers(val):
        if isinstance(val, (int, float)):
            color = '#00C851' if val > 0 else '#ff4444' if val < 0 else 'gray'
            return f'color: {color}; font-weight: bold'
        return ''

    styled_sectors = df_all_sectors.style.map(highlight_numbers, subset=['Change %'])
    
    st.dataframe(
        styled_sectors.format({"Current Value": "{:.2f}", "Change %": "{:.2f}%"}, na_rep="-"),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # --- PART 2: DRILL DOWN INTO SPECIFIC SECTOR ---
    st.subheader("🔍 Stock List by Sector")
    
    refresh_seconds = humanized_refresh_time / 1000
    st.caption(f"🤖 Anti-Block Active: Next silent refresh in {refresh_seconds} seconds...")
    
    sector_names_list = df_all_sectors['Sector Name'].tolist()
    selected_sector = st.selectbox("Select a Sector to load its Companies:", sector_names_list)
    
    with st.spinner(f"Fetching live data for {selected_sector}..."):
        df_equity = get_sector_stocks(selected_sector)
        df_oi = get_futures_oi()
        
        if not df_equity.empty:
            if not df_oi.empty:
                # Merge the two datasets using the Company Name
                final_df = pd.merge(df_equity, df_oi, on="Company Name", how="left")
                final_df.fillna("Not in F&O", inplace=True)
            else:
                final_df = df_equity
                final_df["OI"] = "No Data"
                final_df["OI Change %"] = "No Data"

            # Display the Detailed Stock List
            st.markdown(f"### 📋 {selected_sector} Companies")
            st.info("💡 **Tip:** Click on 'Volume', 'OI', or 'Change %' at the top of the table to sort the stocks!")
            
            styled_df = final_df.style.map(highlight_numbers, subset=['Change %'])
            
            if "OI Change %" in final_df.columns and pd.api.types.is_numeric_dtype(final_df["OI Change %"]):
                 styled_df = styled_df.map(highlight_numbers, subset=['OI Change %'])

            st.dataframe(
                styled_df.format({"Price": "{:.2f}", "Change %": "{:.2f}%", "Volume": "{:,}"}, na_rep="-"),
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"Last updated: {time.strftime('%H:%M:%S')} | Data delayed by NSE rules.")
        else:
            st.warning("⚠️ No stocks found for this sector. The NSE API might be busy.")
else:
    st.error("Failed to fetch the sector list from NSE. Please wait a few moments and refresh the page.")
