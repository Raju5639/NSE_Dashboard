import requests
import time
import random
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NSEConnection:
    def __init__(self):
        # Headers mimicking a user typing the URL in Chrome
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Headers mimicking a background JavaScript data fetch
        # NOTE: Using 'identity' for Accept-Encoding to avoid Brotli compression issues
        self.api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/market-data/live-equity-market",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        self.session = requests.Session()
        self.cache = {}  # In-memory cache with timestamp
        self.initialize_session()

    def initialize_session(self):
        """Visits the homepage mimicking a full browser load to acquire cookies."""
        try:
            self.session.get("https://www.nseindia.com", headers=self.base_headers, timeout=10)
            time.sleep(1.5) # Crucial: Let the cookies settle before hitting the API
            logger.info("NSE session initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize session: {e}")

    def fetch_data(self, url, retries=3, cache_ttl=60):
        """Tries to fetch data using API-specific headers with intelligent caching."""
        # Check cache first
        if url in self.cache:
            cached_data, timestamp = self.cache[url]
            if datetime.now() - timestamp < timedelta(seconds=cache_ttl):
                logger.info(f"Returning cached data for {url}")
                return cached_data
        
        # Human-like delay before requesting
        time.sleep(random.uniform(0.5, 1.5)) 
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.api_headers, timeout=15)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Cache the successful response
                        self.cache[url] = (data, datetime.now())
                        logger.info(f"Successfully fetched data from {url}")
                        return data
                    except ValueError as json_error:
                        logger.error(f"Invalid JSON response: {json_error}")
                        return None
                elif response.status_code in [401, 403]:
                    logger.warning(f"WAF block detected (status {response.status_code}), refreshing session...")
                    # If WAF blocks us, refresh cookies and try again in the loop
                    self.initialize_session()
                    time.sleep(2)  # Wait longer before retry
                elif response.status_code == 429:
                    logger.warning(f"Rate limited (429), waiting before retry...")
                    time.sleep(3)
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}/{retries}: {response.text[:100]}")
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{retries}")
                time.sleep(1)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}/{retries}")
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Error on attempt {attempt + 1}/{retries}: {e}")
                time.sleep(1)
                
        logger.error(f"Failed to fetch data from {url} after {retries} retries")
        return None