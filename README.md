# NSE Intraday Trading Dashboard

A comprehensive real-time trading dashboard for NSE (National Stock Exchange) market data with sector analysis, stock performance tracking, and Open Interest (OI) monitoring.

## Features

### 1. **Sector Overview Dashboard** 
- Live LTP, Change, and % Change for 20+ NSE sector indices
- Sector performance chart with color-coded gainers/losers
- Automatic market status detection (LIVE/CLOSED)
- CSV export functionality

### 2. **Stock Analysis by Sector**
- Detailed stock metrics for each sector
- Open Interest data for stocks with active options trading
- Multi-sector sorting and filtering
- Real-time price updates with 20-30 second auto-refresh

### 3. **OI Spurts (New!)**
- Open Interest Spurts data directly from NSE website
- Matching exact NSE website columns:
  - Open Interest (Previous Date)
  - Open Interest (Current Date)
  - Change in OI (Absolute)
  - % Change in OI
- Individual stock OI analysis
- CSV export for analysis

### 4. **Performance Features**
- Smart caching with TTL (30-60 seconds)
- Brotli compression fix for NSE API compatibility
- Anti-detection headers for reliable data fetching
- Error handling and recovery mechanisms
- Weekend awareness (shows previous business day data)

## Installation

### Requirements
- Python 3.8+
- Windows/Linux/Mac

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Chrome & ChromeDriver (For OI Spurts Feature)

The **OI Spurts** feature requires Chrome browser and ChromeDriver to scrape the dynamic NSE website content.

#### **On Windows:**

1. **Download Chrome** (if not already installed):
   - Visit https://www.google.com/chrome/
   - Install Chrome in the default location

2. **Download ChromeDriver**:
   - Go to https://chromedriver.chromium.org/
   - Download the version matching your Chrome version
   - Extract and place `chromedriver.exe` in:
     - `C:\Windows\System32\` (easiest)
     - Or any folder in your PATH
   - Or put it in the project directory

3. **Verify Installation**:
   ```bash
   chromedriver --version
   ```

#### **On Linux:**

```bash
# Ubuntu/Debian
sudo apt-get install -y chromium-browser chromium-chromedriver

# Or use pip to install chromedriver-binary
pip install chromedriver-binary
```

#### **On Mac:**

```bash
# Using Homebrew
brew install chromedriver
```

### Step 3: Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501` in your browser.

## Usage

### Tab 1: Sector Overview
- View all 20+ sector indices
- See LTP, absolute change, percentage change
- Toggle sector performance chart
- Download sector data as CSV

### Tab 2: Stock Analysis
1. Select a sector from the dropdown
2. View all stocks in that sector
3. Sort by any column (click header)
4. See Open Interest for stocks with active options
5. Download sector stocks data as CSV

### Tab 3: OI Spurts (Open Interest Spurts)
- View the official NSE OI Spurts data
- Shows stocks with highest OI activity
- Click "Refresh OI Spurts" to fetch latest data
- Download as CSV for offline analysis

### Tab 4: Settings
- View system status and data information
- Understand metrics and data fields
- Check market open/close status
- See API response field detection

## Data Explained

### Price Data
- **LTP**: Last Traded Price - the price of the last transaction
- **Prev Close**: Previous closing price
- **Change**: Absolute change in points from previous close
- **% Change**: Percentage change from previous close
- **Volume**: Total volume traded in rupees
- **52W High/Low**: 52-week high and low prices

### Open Interest Data
- **Current OI**: Total open interest for the stock
- **OI Contracts**: Number of active contract types available
- **Avg OI/Contract**: Average OI per contract type

> **Note**: Only stocks with active options trading show OI data. Typically limited to NIFTY 50 + liquid stocks.

### OI Spurts Columns
- **Open Interest (Current Date -1)**: Previous trading day's OI (or Friday if weekend)
- **Open Interest (Current Date)**: Today's OI
- **Chng in OI**: Absolute change in OI
- **%Chng in OI**: Percentage change in OI

## How It Works

### Data Sources
- **Sector Data**: NSE `/api/allIndices` endpoint
- **Stock Data**: NSE `/api/equity-stockIndices` endpoint
- **OI Data**: NSE `/api/liveEquity-derivatives?index=stock_opt` endpoint
- **OI Spurts**: NSE website (dynamic content via Selenium)

### Caching Strategy
- **Sectors**: 30-second TTL (most volatile)
- **Stocks**: 60-second TTL (standard)
- **OI**: 45-second TTL
- **OI Spurts**: 120-second TTL (web scraping is slower)

### Refresh Mechanism
- Auto-refresh every 20-30 seconds (randomized to avoid detection)
- Randomization helps NSE rate limiting
- Manual refresh buttons available in each tab

### Market Hours
- **Trading Hours**: 9:15 AM - 3:30 PM IST (Monday-Friday)
- **Weekend**: Shows previous business day data
- **After Hours**: Shows latest day's session data

## Troubleshooting

### Issue: "No table rows found" or Empty OI Spurts

**Solution**: Ensure Chrome and ChromeDriver are installed:

```bash
# Check if chromedriver is accessible
chromedriver --version

# Add to PATH if needed (Windows)
set PATH=%PATH%;C:\path\to\chromedriver\directory
```

### Issue: "HTTP Error 404" from NSE API

**Possible causes**:
- NSE API endpoint changed
- Your IP is temporarily rate-limited
- Network connectivity issue

**Solution**: 
- Wait a few minutes and try again
- Check internet connection
- Try refreshing the page

### Issue: Data shows as "None" or "-"

**Possible causes**:
- Stock doesn't have options trading
- API response structure changed
- Network timeout

**Solution**:
- Only select stocks with active options (typically NIFTY 50)
- Check NSE website if data also missing there
- Increase cache TTL in settings

### Issue: Streamlit shows "ModuleNotFoundError"

**Solution**: Ensure all packages are installed:

```bash
pip install -r requirements.txt --upgrade
```

## API Information

### NSE Endpoints Used

#### 1. All Indices (Sectors)
```
GET /api/allIndices
Returns: List of all indices including sectors
TTL: 30 seconds
```

#### 2. Sector Stocks
```
GET /api/equity-stockIndices?index={SECTOR_NAME}
Returns: List of stocks in the sector
TTL: 60 seconds
```

#### 3. Options Open Interest
```
GET /api/liveEquity-derivatives?index=stock_opt
Returns: All option contracts with OI data
TTL: 45 seconds
```

#### 4. OI Spurts (Web Scraped)
```
URL: https://www.nseindia.com/market-data/oi-spurts
Method: Browser Automation (Selenium)
Returns: HTML table with OI spurts data
TTL: 120 seconds
```

## Performance Notes

- First load may take 20-30 seconds for OI Spurts due to browser automation
- Subsequent loads use cache (120-second TTL)
- Caching prevents excessive API calls to NSE
- Data updates automatically every 20-30 seconds

## Important Notes

⚠️ **Legal & Ethical Usage**:
- This dashboard is for personal use and analysis
- Follow NSE's Terms of Service for data usage
- Don't use for automated trading at scale without proper licensing
- Respect rate limits and avoid excessive queries

📊 **Data Accuracy**:
- All data sourced directly from NSE APIs/website
- Minor delays of 1-2 seconds are normal
- Weekend/Holiday data shows previous business day
- Always verify data against NSE website for trading decisions

🔐 **Security**:
- No credentials or sensitive data stored
- HTTP requests use randomized headers
- Local caching only, no data sharing

## Future Enhancements

- [ ] Historical OI comparison (previous 5 days)
- [ ] Option greeks integration (delta, gamma, etc.)
- [ ] FII/DII tracking
- [ ] Volatility index (VIX) monitoring
- [ ] Personalized alerts for OI spikes
- [ ] Portfolio tracking
- [ ] Backtesting support

## Support & Issues

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all dependencies are installed
3. Clear browser cache (`Ctrl+Shift+Delete`)
4. Restart Streamlit app

## License

This project is for educational and personal use.

## Disclaimer

This dashboard is for informational purposes only. The author assumes no responsibility for trading losses or decisions made using this tool. Always do your own research and consult with a financial advisor before trading.

---

**Last Updated**: February 2026  
**Version**: 2.0 (OI Spurts Integration)
