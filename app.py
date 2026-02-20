import streamlit as st
import random
import time
from streamlit_autorefresh import st_autorefresh

# IMPORT the backend logic from your other file
from data_engine import get_all_sectors, get_stock_data

# ==========================================
# PAGE CONFIG & REFRESH
# ==========================================
st.set_page_config(page_title="NSE Pro Terminal", layout="wide")

refresh_interval = random.randint(1500, 4500)
st_autorefresh(interval=refresh_interval, key="terminal_pulse")

st.title("⚡ NSE Pro Live Terminal")

# Create the Left and Right panels
col_left, col_right = st.columns([1, 3])

# ==========================================
# LEFT COLUMN: SECTOR WATCH
# ==========================================
with col_left:
    st.subheader("🌐 Sectors")
    
    # Call the backend function
    df_sectors = get_all_sectors()
    
    if not df_sectors.empty:
        # User selects a sector
        selected_sector = st.radio(
            "Select Sector:",
            df_sectors['Sector Name'].tolist(),
            index=0
        )
        st.markdown("---")
        
        # Styling for Sector Dataframe
        def color_sector(val):
            if isinstance(val, (int, float)):
                color = '#00C851' if val > 0 else '#ff4444' if val < 0 else 'white'
                return f'color: {color}; font-weight: bold'
            return ''
            
        # Display the Sector Data (Last Price, % Change)
        st.dataframe(
            df_sectors.set_index('Sector Name').style.map(color_sector, subset=['% Change'])\
            .format({"Last Price": "{:.2f}", "% Change": "{:.2f}%"}),
            use_container_width=True
        )
    else:
        st.error("Connecting to NSE...")
        selected_sector = None

# ==========================================
# RIGHT COLUMN: STOCK ANALYTICS
# ==========================================
with col_right:
    if selected_sector:
        st.subheader(f"📊 {selected_sector} Components")
        
        with st.spinner(f"Loading live data for {selected_sector}..."):
            
            # Call the backend function for specific stocks
            df_stocks = get_stock_data(selected_sector)
            
            if not df_stocks.empty:
                def color_logic(val):
                    if isinstance(val, (int, float)):
                        color = '#00C851' if val > 0 else '#ff4444' if val < 0 else 'white'
                        return f'color: {color}; font-weight: bold'
                    return ''

                # Display the Stock Data (Volume, OI Change, OI % Change, Price)
                st.dataframe(
                    df_stocks.style.map(color_logic, subset=['OI % Change', 'OI Change'])\
                    .format({
                        "Price": "{:.2f}", 
                        "Volume": "{:,.0f}", 
                        "OI Change": "{:,.0f}",
                        "OI % Change": "{:.2f}%"
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=700
                )
                st.caption(f"Pulse: {time.strftime('%H:%M:%S')} | Note: Stocks with 0 OI are not listed in F&O.")
            else:
                st.warning(f"⚠️ Market data unavailable for '{selected_sector}'.")