import streamlit as st
import pandas as pd
import time
import random
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import pytz

# Import our custom connection engine from data_engine.py
from data_engine import NSEConnection
from oi_spurts_scraper import get_oi_spurts_requests, normalize_oi_spurts_df, oi_spurts_last_debug

# ==========================================
# SECTION 0: MARKET STATUS UTILITIES
# ==========================================
def is_market_open():
    """Check if NSE market is currently open"""
    # NSE is in IST (UTC+5:30)
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Market closed on weekends
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    
    # Market hours: 9:15 AM to 3:30 PM IST
    market_open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    if market_open_time <= now <= market_close_time:
        return True
    
    return False

def get_data_date():
    """Get the date for which data should be fetched"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # If market is open, use today's date
    if is_market_open():
        return now.date()
    
    # If market is closed on weekend, use previous business day
    if now.weekday() >= 5:  # Saturday or Sunday
        # For Saturday, go back 1 day; for Sunday, go back 2 days
        days_back = 1 if now.weekday() == 5 else 2
        return (now - timedelta(days=days_back)).date()
    
    # If market is closed (after hours), use today's data (still valid from today's session)
    return now.date() 

# ==========================================
# SECTION 1: PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Intraday Trading Terminal", layout="wide", initial_sidebar_state="expanded")

# Professional CSS for the entire application
professional_css = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
        color: #333;
    }
    
    /* Streamlit main container */
    .stMainBlockContainer {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Headers and Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        color: #1a1a2e;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    h2 {
        font-size: 1.75rem;
        margin: 24px 0 16px 0;
        border-bottom: 3px solid #667eea;
        padding-bottom: 8px;
    }
    
    h3 {
        font-size: 1.25rem;
        margin: 16px 0 12px 0;
    }
    
    /* Buttons */
    button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* Cards and Containers */
    .css-1r6slb0, [data-testid="stVerticalBlock"] {
        gap: 16px;
    }
    
    /* Metrics */
    [data-testid="stMetricContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
    }
    
    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    /* Dividers */
    hr {
        margin: 24px 0 !important;
        border: none !important;
        border-top: 2px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Data Tables */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Download Button */
    [data-testid="stDownloadButton"] {
        width: 100%;
    }
    
    /* Success/Info/Error messages */
    [data-testid="stAlert"] {
        border-radius: 8px;
        border-left: 4px solid;
        padding: 16px;
        margin: 12px 0;
    }
    
    .stSuccess {
        border-left-color: #28a745 !important;
        background-color: rgba(40, 167, 69, 0.1) !important;
    }
    
    .stInfo {
        border-left-color: #0066cc !important;
        background-color: rgba(0, 102, 204, 0.1) !important;
    }
    
    .stWarning {
        border-left-color: #ffc107 !important;
        background-color: rgba(255, 193, 7, 0.1) !important;
    }
    
    .stError {
        border-left-color: #dc3545 !important;
        background-color: rgba(220, 53, 69, 0.1) !important;
    }
    
    /* Input fields */
    input, select, textarea {
        border-radius: 8px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0 !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)

# ==========================================
# SECTION 2: INITIALIZE NSE ENGINE
# ==========================================
if 'nse' not in st.session_state:
    st.session_state.nse = NSEConnection()

if 'last_oi_fields' not in st.session_state:
    st.session_state.last_oi_fields = []

if 'df_oi_spurts' not in st.session_state:
    st.session_state.df_oi_spurts = pd.DataFrame()

nse = st.session_state.nse

# ==========================================
# SECTION 3: DATA FETCHING LOGIC
# ==========================================
@st.cache_data(ttl=30)  # Shorter TTL for sector data - more frequent updates
def get_all_sectors_data():
    """Fetch all sector indices with LTP, Change, and % change"""
    try:
        url = "https://www.nseindia.com/api/allIndices"
        data = nse.fetch_data(url, cache_ttl=30)
        
        sectors = []
        if data and 'data' in data and isinstance(data['data'], list):
            for item in data['data']:
                try:
                    # Filter for SECTORAL INDICES only
                    if item.get('key', '') == 'SECTORAL INDICES':
                        index_name = item.get('index', '')
                        last_price = float(item.get('last', 0))
                        prev_close = float(item.get('previousClose', last_price))
                        point_change = last_price - prev_close
                        pct_change = float(item.get('percentChange', (point_change / prev_close * 100) if prev_close else 0))
                        
                        sectors.append({
                            "Sector Name": index_name,
                            "LTP": last_price,
                            "Change": point_change,
                            "% Change": pct_change,
                            "Prev Close": prev_close,
                            "High": float(item.get('high', last_price)),
                            "Low": float(item.get('low', last_price)),
                            "Volume": float(item.get('totalTradedVolume', item.get('volume', 0)))
                        })
                except (ValueError, TypeError) as e:
                    continue
        
        if sectors:
            df = pd.DataFrame(sectors)
            # Sort by % Change in descending order (highest to lowest)
            df = df.sort_values('% Change', ascending=False)
            return df.reset_index(drop=True)
        else:
            return pd.DataFrame()
        
    except Exception as e:
        st.error(f"❌ Error parsing sectors data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=45)  # Slightly longer TTL for derivative data
def get_options_oi():
    """Fetch options open interest data for all stocks"""
    try:
        # Use stock_opt endpoint which provides options data
        url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt"
        data = nse.fetch_data(url, cache_ttl=45)
        
        oi_dict = {}
        if data and 'data' in data:
            # Log actual fields for debugging
            if data['data']:
                st.session_state.last_oi_fields = list(data['data'][0].keys())
            
            # Group by underlying to aggregate OI across all contracts
            for item in data['data']:
                underlying = item.get('underlying', '')
                if underlying:
                    # Flexible extraction: find current and previous OI fields if present
                    oi_value = 0.0
                    prev_oi_value = None
                    for k, v in item.items():
                        lk = k.lower()
                        if 'openinterest' in lk and 'prev' not in lk and 'previous' not in lk and 'day' not in lk:
                            try:
                                oi_value = float(v or 0)
                            except Exception:
                                oi_value = 0.0
                        if 'openinterest' in lk and ('prev' in lk or 'previous' in lk or 'day' in lk or 'yesterday' in lk):
                            try:
                                prev_oi_value = float(v or 0)
                            except Exception:
                                prev_oi_value = None

                    if underlying not in oi_dict:
                        oi_dict[underlying] = {
                            "Current OI": oi_value,
                            "Prev OI": prev_oi_value if prev_oi_value is not None else 0.0,
                            "OI Count": 1
                        }
                    else:
                        oi_dict[underlying]["Current OI"] += oi_value
                        if prev_oi_value is not None:
                            oi_dict[underlying]["Prev OI"] = oi_dict[underlying].get("Prev OI", 0.0) + prev_oi_value
                        oi_dict[underlying]["OI Count"] += 1
            
            # Convert to dataframe with proper structure
            if oi_dict:
                rows = []
                for symbol, oi_info in oi_dict.items():
                    current = int(oi_info.get("Current OI", 0))
                    prev = int(oi_info.get("Prev OI", 0)) if oi_info.get("Prev OI", None) is not None else None
                    chng = None
                    pct = None
                    if prev is not None:
                        chng = current - prev
                        try:
                            pct = (chng / prev) * 100 if prev != 0 else None
                        except Exception:
                            pct = None

                    rows.append({
                        "Symbol": symbol,
                        "Current OI": current,
                        "Prev OI": prev if prev is not None else None,
                        "Chng in OI": chng,
                        "%Chng in OI": pct,
                        "OI Contracts": oi_info["OI Count"],
                        "Avg OI/Contract": round(oi_info["Current OI"] / oi_info["OI Count"], 0) if oi_info.get("OI Count") else 0
                    })
                
                df_oi = pd.DataFrame(rows)
                return df_oi
        
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ Could not fetch options OI data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=120)  # OI Spurts data, longer TTL since scraping takes time
def get_oi_spurts_data_cached():
    """
    Fetch OI Spurts data from NSE website (cached version)
    Uses modern requests-based approach with fallback chain.
    Returns a clean dataframe with Symbol and OI change columns
    """
    try:
        # Use the modern requests-based fetcher that handles:
        # 1. NSE public page HTML parsing
        # 2. NSE JSON API endpoints
        # 3. BSE fallback endpoints
        df = get_oi_spurts_requests()
        
        if not df.empty:
            # Columns should already be normalized by get_oi_spurts_requests
            # But ensure we have the right ones
            canonical_cols = [c for c in ['Symbol', 'Chng in OI', '%Chng in OI'] if c in df.columns]
            if canonical_cols:
                return df[canonical_cols].copy()
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"Error in get_oi_spurts_data_cached: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=120)  # OI Spurts data, longer TTL since scraping takes time
def get_oi_spurts_data():
    """
    Fetch OI Spurts data from NSE website (with visual feedback)
    This uses web scraping since the data is dynamically loaded
    """
    try:
        st.info("📊 Fetching OI Spurts data...")
        
        # Try Selenium first (more reliable for dynamically loaded content)
        df = get_oi_spurts_data_selenium()
        
        if df.empty:
            # Fallback to BeautifulSoup if Selenium fails
            st.info("Trying alternative method...")
            df = get_oi_spurts_beautifulsoup()
        
        if not df.empty:
            st.success(f"✅ Loaded {len(df)} OI Spurts records")
            return df
        else:
            st.warning("⚠️ Could not load OI Spurts data from website")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"❌ Error fetching OI Spurts: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)  # Standard 60s TTL for individual sector stocks
def get_sector_stocks(sector_name):
    """Fetch stocks in a specific sector with error handling"""
    try:
        import urllib.parse
        encoded_sector = urllib.parse.quote(sector_name)
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={encoded_sector}"
        data = nse.fetch_data(url, cache_ttl=60)
        
        stocks = []
        if data and 'data' in data:
            for item in data['data']:
                # Include only actual stocks (priority=0), exclude the index itself (priority=1)
                if item.get('priority') == 0: 
                    stocks.append({
                        "Symbol": item.get('symbol'),
                        "Prev Close": item.get('previousClose', 0),
                        "LTP": item.get('lastPrice', 0),
                        "Change": item.get('change', 0),
                        "% Change": item.get('pChange', 0),
                        "Volume": item.get('totalTradedVolume', 0),
                        "52W High": item.get('yearHigh', 0),
                        "52W Low": item.get('yearLow', 0)
                    })
        return pd.DataFrame(stocks)
    except Exception as e:
        st.error(f"❌ Error fetching stocks for {sector_name}: {e}")
        return pd.DataFrame()


# ==========================================
# SECTION 4: STYLING FUNCTIONS
# ==========================================

def highlight_performance(val):
    """Color code based on positive/negative change"""
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: #00C851; font-weight: bold'
        elif val < 0:
            return 'color: #ff4444; font-weight: bold'
        else:
            return 'color: gray'
    return ''

def create_sector_performance_chart(df):
    """Create an interactive chart showing sector performance"""
    if df.empty:
        return None
    
    try:
        # Sort by % Change to show top/bottom performers
        df_sorted = df.sort_values('% Change')
        
        # Create color array based on positive/negative change
        colors = ['#ef553b' if x < 0 else '#00cc96' for x in df_sorted['% Change']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=df_sorted['% Change'],
                y=df_sorted['Sector Name'],
                orientation='h',
                marker=dict(
                    color=colors,
                    line=dict(width=0)
                ),
                text=df_sorted['% Change'].apply(lambda x: f"  {x:+.2f}%"),
                textposition='outside',
                textfont=dict(size=12, family="Arial", color='#333'),
                hovertemplate='<b>%{y}</b><br>Change: %{x:.2f}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': "📊 Sector Performance - % Change",
                'font': {'size': 20, 'color': '#333', 'family': 'Arial'}
            },
            xaxis_title="% Change",
            yaxis_title="Sector",
            height=500,
            template="plotly",
            showlegend=False,
            font=dict(size=12, family="Arial", color='#333'),
            plot_bgcolor='rgba(240, 240, 245, 0.5)',
            margin=dict(l=150, r=100, t=80, b=60)
        )
        
        return fig
    except Exception as e:
        st.warning(f"⚠️ Could not generate chart: {e}")
        return None


# ==========================================
# SECTION 5: AUTO-REFRESH SETUP
# ==========================================
humanized_refresh_time = st_autorefresh(interval=random.randint(20000, 30000), key="dashboard_refresh")

# ==========================================
# SECTION 6: MAIN UI LAYOUT
# ==========================================

# Professional header styling
header_html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; margin-bottom: 24px; color: white; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);">
    <h1 style="margin: 0; font-size: 32px; font-weight: 700;">📈 NSE Intraday Trading Dashboard</h1>
    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.95;">Real-time Market Analysis | Sector Performance | Open Interest Tracking</p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Market status display
market_open = is_market_open()
data_date = get_data_date()
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

# Status cards
col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    status_icon = "🟢" if market_open else "🔴"
    status_text = "LIVE" if market_open else "CLOSED"
    st.markdown(f"""
    <div style="background: {'#d4edda' if market_open else '#f8d7da'}; padding: 15px; border-radius: 8px; border-left: 4px solid {'#28a745' if market_open else '#dc3545'};">
        <div style="font-weight: 700; color: {'#155724' if market_open else '#721c24'}; font-size: 14px;">
            {status_icon} Market {status_text}
        </div>
        <div style="font-size: 12px; color: {'#155724' if market_open else '#721c24'}; margin-top: 4px;">
            {now.strftime('%d-%b-%Y %H:%M:%S IST')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_status2:
    st.markdown(f"""
    <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #0066cc;">
        <div style="font-weight: 700; color: #003d99; font-size: 14px;">
            📅 Data Date
        </div>
        <div style="font-size: 12px; color: #003d99; margin-top: 4px;">
            {data_date.strftime('%d-%b-%Y')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_status3:
    st.markdown(f"""
    <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
        <div style="font-weight: 700; color: #856404; font-size: 14px;">
            🔄 Auto Refresh
        </div>
        <div style="font-size: 12px; color: #856404; margin-top: 4px;">
            Every 20-30 sec
        </div>
    </div>
    """, unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🌐 Sector Overview", "📋 Stock Analysis", "📊 OI Spurts", "⚙️ Settings"])

# Fetch sector data once and cache it
with st.spinner("📡 Fetching sectors..."):
    df_all_sectors = get_all_sectors_data()

# Fetch OI data globally (once) - applies to all sectors
with st.spinner("📡 Fetching options data globally..."):
    df_oi_global = get_options_oi()

with tab1:
    if not df_all_sectors.empty:
        # Visualization
        chart = create_sector_performance_chart(df_all_sectors)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        st.markdown("---")
        
        # Market Sectors - Professional Display
        st.subheader("📊 Market Sectors (Click to view stocks)")
        
        df_display = df_all_sectors.copy()
        
        # Calculate color gradient based on min-max % change (green = high, red = low)
        def get_gradient_color(value, min_val, max_val):
            """Convert value to color gradient (green=high, red=low)"""
            if max_val == min_val:
                ratio = 0.5
            else:
                ratio = (value - min_val) / (max_val - min_val)
            
            red = int(235 - (235 - 17) * ratio)
            green = int(51 + (153 - 51) * ratio)
            blue = int(73 + (142 - 73) * ratio)
            
            return f"#{red:02x}{green:02x}{blue:02x}"
        
        min_change = df_display['% Change'].min()
        max_change = df_display['% Change'].max()
        
        # Create sector cards in a grid
        cols = st.columns(4, gap="small")
        col_idx = 0
        
        for idx, row in df_display.iterrows():
            sector_name = row['Sector Name']
            ltp = row['LTP']
            pct_change = row['% Change']
            
            card_color = get_gradient_color(pct_change, min_change, max_change)
            arrow = "▲" if pct_change >= 0 else "▼"
            pct_sign = "+" if pct_change >= 0 else ""
            
            with cols[col_idx % 4]:
                # Display colored card for sector
                html_card = f'<div style="background: linear-gradient(135deg, {card_color} 0%, {card_color} 100%); padding: 14px; border-radius: 8px; text-align: center; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.12); margin-bottom: 8px;"><div style="font-size: 12px; margin-bottom: 4px; font-weight: 700;">{sector_name}</div><div style="font-size: 13px; font-weight: 700; margin-bottom: 3px;">₹{ltp:.0f}</div><div style="font-size: 11px;">{arrow} {pct_sign}{pct_change:.2f}%</div></div>'
                st.markdown(html_card, unsafe_allow_html=True)
                
                # Button to navigate
                if st.button("SELECT", key=f"sector_{idx}", use_container_width=True, help=f"View {sector_name} stocks"):
                    st.session_state['sector_select_tab2'] = sector_name
                    try:
                        st.switch_tab("📋 Stock Analysis")
                    except AttributeError:
                        st.rerun()
            
            col_idx += 1
        
        st.markdown("---")
        
        # Download section
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Sector Data (CSV)",
            data=csv,
            file_name=f"sector_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_sectors"
        )
        
    else:
        st.error("❌ Failed to fetch sector data. Please refresh in a moment.")

with tab2:
    # Professional header
    st.markdown("<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; margin-bottom: 16px;'><h2 style='margin: 0; color: white; border: none; padding: 0;'>📋 Stock Analysis by Sector</h2><p style='margin: 6px 0 0 0; opacity: 0.9; color: white; font-size: 13px;'>Select a sector to view detailed stock performance metrics</p></div>", unsafe_allow_html=True)
    
    if not df_all_sectors.empty:
        sector_names_list = df_all_sectors['Sector Name'].tolist()
        
        # Initialize session state if not present
        if 'sector_select_tab2' not in st.session_state:
            st.session_state['sector_select_tab2'] = sector_names_list[0]
        
        # Get current selected sector from session state
        current_sector = st.session_state.get('sector_select_tab2', sector_names_list[0])
        
        # Ensure current sector is in the list, otherwise use first one
        if current_sector not in sector_names_list:
            current_sector = sector_names_list[0]
            st.session_state['sector_select_tab2'] = current_sector
        
        # Sector selector without key parameter
        col_sel1, col_sel2 = st.columns([3, 1])
        with col_sel1:
            selected_sector = st.selectbox(
                "Select a Sector:", 
                sector_names_list, 
                index=sector_names_list.index(current_sector),
                label_visibility="collapsed"
            )
            # Update session state with new selection
            st.session_state['sector_select_tab2'] = selected_sector
        
        # Fetch sector stocks
        with st.spinner(f"📡 Fetching {selected_sector} stocks..."):
            df_equity = get_sector_stocks(selected_sector)
        
        if not df_equity.empty:
            # For stock analysis we only show price and volume columns.
            final_df = df_equity[['Symbol', 'Prev Close', 'LTP', 'Change', '% Change', 'Volume']].copy()

            # Info cards
            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
            
            with col_info1:
                st.metric("Total Stocks", len(final_df), help="Number of stocks in this sector")
            
            with col_info2:
                gainers = len(final_df[final_df['% Change'] > 0])
                st.metric("Gainers", gainers, f"{gainers} 📈", help="Stocks with positive return")
            
            with col_info3:
                losers = len(final_df[final_df['% Change'] < 0])
                st.metric("Losers", losers, f"{losers} 📉", help="Stocks with negative return")
            
            with col_info4:
                avg_return = final_df['% Change'].mean()
                st.metric("Avg Return", f"{avg_return:+.2f}%", help="Average percentage change")
            
            st.markdown("---")
            
            # Data table header
            st.subheader("📊 Stock Details")

            # Highlight performance on Change and % Change columns
            styled_df = final_df.style.map(highlight_performance, subset=['Change', '% Change'])

            # Format numeric columns
            format_dict = {}
            for col in final_df.columns:
                if col in ["Prev Close", "LTP"]:
                    format_dict[col] = "{:.2f}"
                elif col == "Change":
                    format_dict[col] = "{:,.2f}"
                elif col == "% Change":
                    format_dict[col] = "{:.2f}%"
                elif col == "Volume":
                    format_dict[col] = "{:,.0f}"

            st.dataframe(
                styled_df.format(format_dict, na_rep="-"),
                width="stretch",
                hide_index=True
            )

            # Download section
            csv_stocks = final_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Stock Data (CSV)",
                data=csv_stocks,
                file_name=f"{selected_sector}_stocks_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_stocks"
            )
        else:
            st.warning(f"⚠️ No stocks found for {selected_sector} or data unavailable.")
    else:
        st.info("ℹ️ Please wait while sector data loads...")

with tab3:
    # Professional header
    st.markdown("<div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 8px; margin-bottom: 16px;'><h2 style='margin: 0; color: white; border: none; padding: 0;'>📊 Open Interest Spurts</h2><p style='margin: 6px 0 0 0; opacity: 0.9; color: white; font-size: 13px;'>Stocks with highest change in open interest - Options trading surge indicator</p></div>", unsafe_allow_html=True)
    
    st.markdown("**What is OI Spurts?**")
    st.markdown("Stocks showing the largest increase in open interest, indicating heightened options trading activity and potential significant price movements.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("#### Highest OI Changes")
    with col2:
        fetch_button = st.button("🔄 Refresh", key="refresh_oi_spurts")

    # Use the cached normalized OI spurts fetcher
    if fetch_button or 'df_oi_spurts' not in st.session_state:
        with st.spinner("📡 Fetching OI Spurts data..."):
            st.session_state.df_oi_spurts = get_oi_spurts_data_cached()

    df_oi_spurts = st.session_state.get('df_oi_spurts', pd.DataFrame())
    # Also load aggregated options OI (from derivatives API) as fallback
    df_oi_from_options = get_options_oi()

    # Choose source: scraped OI Spurts table preferred, fallback to aggregated options OI
    if not df_oi_spurts.empty:
        cols = [c for c in ['Symbol', 'Chng in OI', '%Chng in OI'] if c in df_oi_spurts.columns]
        display_df = df_oi_spurts[cols].copy()
    elif not df_oi_from_options.empty:
        display_df = df_oi_from_options[['Symbol', 'Chng in OI', '%Chng in OI']].copy()
    else:
        display_df = pd.DataFrame()

    if not display_df.empty:
        # Convert numeric columns
        if 'Chng in OI' in display_df.columns:
            display_df['Chng in OI'] = pd.to_numeric(display_df['Chng in OI'], errors='coerce')
        if '%Chng in OI' in display_df.columns:
            display_df['%Chng in OI'] = pd.to_numeric(display_df['%Chng in OI'], errors='coerce')

        # UI controls: top N and sort
        sort_options = [c for c in ['%Chng in OI', 'Chng in OI', 'Symbol'] if c in display_df.columns]
        default_sort = '%Chng in OI' if '%Chng in OI' in display_df.columns else (sort_options[0] if sort_options else None)
        col_ctrl_1, col_ctrl_2 = st.columns([2, 1])
        with col_ctrl_1:
            sort_by = st.selectbox("Sort by", sort_options, index=sort_options.index(default_sort) if default_sort in sort_options else 0)
        with col_ctrl_2:
            top_n = st.number_input("Top N", min_value=5, max_value=200, value=20, step=5)

        if sort_by:
            ascending = False
            display_sorted = display_df.sort_values(by=sort_by, ascending=ascending).head(top_n)
        else:
            display_sorted = display_df.head(top_n)

        # Style and format
        styled = display_sorted.copy()
        format_dict = {}
        if 'Chng in OI' in styled.columns:
            format_dict['Chng in OI'] = '{:,.0f}'
        if '%Chng in OI' in styled.columns:
            format_dict['%Chng in OI'] = '{:.2f}%'

        # Apply color highlighting to OI columns
        styled_df = styled.style.format(format_dict, na_rep='-')
        if 'Chng in OI' in styled.columns:
            styled_df = styled_df.map(highlight_performance, subset=['Chng in OI'])
        if '%Chng in OI' in styled.columns:
            styled_df = styled_df.map(highlight_performance, subset=['%Chng in OI'])

        st.dataframe(styled_df, width="stretch", hide_index=True)

        # Download button
        csv = display_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Download OI Spurts as CSV",
            data=csv,
            file_name=f"oi_spurts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        # Summary
        st.markdown("### Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Stocks (in view)", len(display_sorted))
        with col2:
            st.info(f"Data fetched at {datetime.now().strftime('%H:%M:%S')} IST")
        with col3:
            st.caption("Note: This is live data from NSE website")
    else:
        st.warning("⚠️ Could not fetch OI Spurts data from NSE website")
        st.markdown("""
        **What's OI Spurts?**
        OI Spurts shows stocks with the highest change in Open Interest, indicating surge in options trading activity.
        
        **Why no data?**
        - The NSE OI Spurts page table is dynamically rendered with JavaScript (not available in static HTML)
        - API endpoints for OI data are not publicly accessible
        - Network or temporary NSE unavailability
        
        **Alternative Actions:**
        1. Check the [NSE OI Spurts page directly](https://www.nseindia.com/market-data/oi-spurts) in your browser
        2. Try refreshing this tab using the Refresh button above
        3. Check your network connectivity
        
        **For Developers:**
        - The current implementation uses `requests + BeautifulSoup` (pure Python, no Selenium needed)
        - If you have access to a working OI data source, update `get_oi_spurts_requests()` in `oi_spurts_scraper.py`
        """)
        
        # Show scraper debug log for diagnostics
        if oi_spurts_last_debug:
            with st.expander("📋 Debug: Fetch Diagnostics"):
                for msg in oi_spurts_last_debug[-15:]:
                    st.code(msg, language=None)
        
        # Show available derivatives data as alternative
        st.markdown("---")
        st.markdown("### Available Alternative: Options Contracts Data")
        st.markdown("While full OI Spurts data is not available, here are the latest options contracts we can access:")
        
        try:
            url = "https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt"
            data = nse.fetch_data(url, cache_ttl=45)
            
            if data and 'data' in data and data['data']:
                # Get unique underlying symbols and their contract counts
                contract_summary = {}
                for item in data['data']:
                    underlying = item.get('underlying', 'Unknown')
                    if underlying not in contract_summary:
                        contract_summary[underlying] = {
                            'contracts': 0,
                            'lastPrice': item.get('lastPrice', 0),
                            'expiry': item.get('expiryDate', 'N/A')
                        }
                    contract_summary[underlying]['contracts'] += 1
                
                summary_df = pd.DataFrame([
                    {
                        'Symbol': k,
                        'Contracts': v['contracts'],
                        'Sample Price': v['lastPrice'],
                        'Nearest Expiry': v['expiry']
                    }
                    for k, v in sorted(contract_summary.items(), key=lambda x: x[1]['contracts'], reverse=True)
                ])
                
                st.dataframe(summary_df, width="stretch", hide_index=True)
                st.caption(f"✓ Found {len(summary_df)} underlyings with {sum(summary_df['Contracts'])} total contracts")
        except Exception as e:
            st.info(f"Could not load alternative data: {e}")

with tab4:
    # Professional header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 24px; border-radius: 10px; margin-bottom: 24px; color: white;">
        <h2 style="margin: 0; color: white; border: none; padding: 0;">⚙️ Settings & Documentation</h2>
        <p style="margin: 8px 0 0 0; opacity: 0.9;">Dashboard configuration, data glossary, and system information</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Information cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div style="background: #f0f4ff; padding: 12px; border-radius: 6px; border-left: 3px solid #667eea;"><div style="font-weight: 700; color: #667eea; margin-bottom: 6px;">🔄 Refresh</div><div style="font-size: 12px; color: #333;">20-30 sec randomized</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="background: #f0fff4; padding: 12px; border-radius: 6px; border-left: 3px solid #38ef7d;"><div style="font-weight: 700; color: #38ef7d; margin-bottom: 6px;">📊 Data Source</div><div style="font-size: 12px; color: #333;">NSE Live Feeds</div></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div style="background: #fff0f6; padding: 12px; border-radius: 6px; border-left: 3px solid #f5576c;"><div style="font-weight: 700; color: #f5576c; margin-bottom: 6px;">🎯 Status</div><div style="font-size: 12px; color: #333;">Active</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data documentation
    col_doc1, col_doc2 = st.columns(2)
    
    with col_doc1:
        with st.expander("📖 Price Data Glossary", expanded=True):
            st.write("**LTP** - Last Traded Price")
            st.write("**Prev Close** - Previous session close")
            st.write("**Change** - Absolute rupee change")
            st.write("**% Change** - Percentage change")
            st.write("**Volume** - Shares traded today")
            st.write("**52W High/Low** - 52-week range")
    
    with col_doc2:
        with st.expander("📖 Open Interest (OI) Data", expanded=True):
            st.write("**Current OI** - Total contracts outstanding")
            st.write("**OI Spurts** - Unusual surge in open interest")
            st.write("**Chng in OI** - Absolute change from previous day")
            st.write("**% Chng in OI** - Percentage change")
            st.write("**OI Contracts** - Active option contracts")
            st.write("**Avg OI/Contract** - Liquidity measure")
    
    st.markdown("---")
    
    st.markdown("### Important Notes")
    st.info("**OI Explanation**: OI = Total volume of options contracts outstanding. Shows market activity & sentiment. Higher OI = More trading interest. Only liquid stocks have OI (typically NIFTY 50+ stocks).")
    
    st.markdown("### What's New")
    st.success("✨ **Dashboard Features**: Live OI Data • Contract Analysis • Market Status Detection • Real-time Charts • CSV Export • Enhanced Error Handling")
    
    st.markdown("### System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Market Status", "🟢 LIVE" if market_open else "🔴 CLOSED")
    with col2:
        st.metric("Data Date", data_date.strftime('%d-%b-%Y'))
    
    st.markdown("### Debug Info")
    with st.expander("🔧 API Field Detection"):
        if 'last_oi_fields' in st.session_state and st.session_state.last_oi_fields:
            st.write("**OI API Response Fields:**")
            st.write(st.session_state.last_oi_fields)
        else:
            st.write("Wait for data fetch to see API fields...")
    
    st.caption(f"Last updated: {time.strftime('%H:%M:%S')} | Data delayed per NSE rules")
