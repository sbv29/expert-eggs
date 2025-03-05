"""
Configuration settings for web scrapers.
Contains all configurable parameters and constants.
"""
import os

# ===== UNIVERSAL SETTINGS =====

# File paths
COOKIE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies")
COOKIE_FILE = os.path.join(COOKIE_DIR, "cookies.json")  # Path to cookie file
LOG_DIRECTORY = "logs"  # Directory to store log files

# Browser settings
HEADLESS_MODE = False # Set to True to run browsers without UI (headless mode)
BROWSER_WINDOW_WIDTH = 2920  # Default browser window width in pixels
BROWSER_WINDOW_HEIGHT = 3080  # Default browser window height in pixels

# Discord notification settings
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1345475006058205194/XhCEXuvoOWtqO_7WS9XiIy_LLJwRcPPFmvcPoTS0772R1iaMSnMC1N-aO41oLRParlBD"
DISCORD_USER_ID = "78875182906748928"
ENABLE_DISCORD_STOCK_NOTIFICATIONS = True  # Set to False to disable in-stock notifications
ENABLE_DISCORD_STATUS_UPDATES = False  # Set to False to disable periodic status updates
STATUS_UPDATE_INTERVAL = 15 * 60  # Status updates in Discord (15 * 60 = 900 seconds = 15 minutes)
# Monitoring Configuration
LOG_DIRECTORY = "logs"  # Directory to store log files

# Proxy Configuration
USE_PROXY = False  # Set to True to enable proxy
PROXY_URL = "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:823"  # Your proxy server URL

# If your proxy requires authentication, you can specify credentials:
PROXY_USERNAME = ""  # Your proxy username
PROXY_PASSWORD = ""  # Your proxy password

# For proxy rotation (multiple proxies)
ROTATE_PROXIES = False  # Set to True to rotate through multiple proxies
PROXY_LIST = [
    # List of proxy URLs to rotate through
    # "http://proxy1.example.com:8080",
    # "http://proxy2.example.com:8080",
    # "http://username:password@proxy3.example.com:8080"
]

# Example of how to set up a proxy with authentication:
# 
# Method 1: Include credentials in the URL
# PROXY_URL = "http://username:password@proxy.example.com:8080"
# 
# Method 2: Specify credentials separately
# PROXY_URL = "http://proxy.example.com:8080"
# PROXY_USERNAME = "username"
# PROXY_PASSWORD = "password"

# ===== NEWEGG SPECIFIC SETTINGS =====

# Newegg URLs
NEWEGG_ORDERS_PAGE_URL = "https://secure.newegg.ca/account/settings"
NEWEGG_SEARCH_PAGE_URL = "https://www.newegg.ca/p/pl?d=cable&LeftPriceRange=4.99+4.99"

# Newegg product filtering settings
NEWEGG_SHOW_COMBO_PRODUCTS = False  # Set to True to include combo products in search results

# Newegg checkout settings
NEWEGG_ATC = True  # Set to False for "scan only" mode (no automatic add to cart)
NEWEGG_PLACE_ORDER = False  # Set to True to enable automatic order placement (click the Place Order button)
NEWEGG_PASSWORD = r'eRR")@KoDe:Y4$`'  # Your Newegg account password (using raw string)
NEWEGG_CVV = "1234"  # Your credit card CVV code

# Newegg timing settings
NEWEGG_PAGE_LOAD_WAIT = 0  # Time in seconds to wait for page to load
NEWEGG_MIN_RANDOM_REFRESH = 0.25  # Minimum time in seconds between page refreshes
NEWEGG_MAX_RANDOM_REFRESH = 1  # Maximum time in seconds between page refreshes
NEWEGG_MIN_REFRESH_COUNT = 250  # Minimum number of refreshes before session refresh
NEWEGG_MAX_REFRESH_COUNT = 300  # Maximum number of refreshes before session refresh

# Newegg browser settings
NEWEGG_BROWSER_WIDTH = 1920  # Newegg browser window width in pixels
NEWEGG_BROWSER_HEIGHT = 1080  # Newegg browser window height in pixels

# ===== BESTBUY SPECIFIC SETTINGS =====

# BestBuy URLs
BESTBUY_BASE_URL = "https://www.bestbuy.ca"
BESTBUY_CART_URL = "https://www.bestbuy.ca/en-ca/basket"
BESTBUY_SEARCH_URL = "https://www.bestbuy.ca/en-ca/collection/nvidia-graphic-cards-rtx-50-series/bltbd7cf78bd1d558ef?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bcategory%253AGraphics%2BCards%253Bcustom0graphicscardmodel%253AGeForce%2BRTX%2B5090%257CGeForce%2BRTX%2B5080"
BESTBUY_ORDERS_PAGE_URL = "https://www.bestbuy.ca/order/en-ca/order-history"

# BestBuy checkout settings
BESTBUY_ATC = False  # Set to False for "scan only" mode (no automatic add to cart)
BESTBUY_PLACE_ORDER = False  # Set to True to enable automatic order placement (click the Place Order button)
BESTBUY_PASSWORD = "MSIPerformance1!"  # Password for BestBuy account
BESTBUY_CVV = "1234"  # Your credit card CVV code

# BestBuy timing settings
BESTBUY_PAGE_LOAD_WAIT = 0  # Time in seconds to wait for page to load
BESTBUY_MIN_RANDOM_REFRESH = .25  # Minimum time in seconds between page refreshes
BESTBUY_MAX_RANDOM_REFRESH = .85  # Maximum time in seconds between page refreshes
BESTBUY_MIN_REFRESH_COUNT = 150  # Minimum number of refreshes before session refresh
BESTBUY_MAX_REFRESH_COUNT = 200  # Maximum number of refreshes before session refresh

# BestBuy browser settings
BESTBUY_BROWSER_WIDTH = 1920  # BestBuy browser window width in pixels
BESTBUY_BROWSER_HEIGHT = 1080  # BestBuy browser window height in pixels

# ===== DIRECTORY CREATION =====

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create cookies directory if it doesn't exist
if not os.path.exists(COOKIE_DIR):
    os.makedirs(COOKIE_DIR)