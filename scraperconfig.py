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
HEADLESS_MODE = True # Set to True to run browsers without UI (headless mode)
BROWSER_WINDOW_WIDTH = 2920  # Default browser window width in pixels
BROWSER_WINDOW_HEIGHT = 3080  # De1ault browser window height in pixels

# Discord notification settings
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1345475006058205194/XhCEXuvoOWtqO_7WS9XiIy_LLJwRcPPFmvcPoTS0772R1iaMSnMC1N-aO41oLRParlBD"
DISCORD_USER_ID = "78875182906748928"
ENABLE_DISCORD_STOCK_NOTIFICATIONS = True  # Set to False to disable in-stock notifications
ENABLE_DISCORD_STATUS_UPDATES = False  # Set to False to disable periodic status updates
STATUS_UPDATE_INTERVAL = 15 * 60  # Status updates in Discord (15 * 60 = 900 seconds = 15 minutes)

# ===== NEWEGG SPECIFIC SETTINGS =====

# Newegg URLs
NEWEGG_ORDERS_PAGE_URL = "https://secure.newegg.ca/account/settings"
NEWEGG_SEARCH_PAGE_URL = "https://www.newegg.ca/p/pl?N=100007708%20601469153%20601469158%20601469157"

# Newegg product filtering settings
NEWEGG_SHOW_COMBO_PRODUCTS = False  # Set to True to include combo products in search results

# Newegg checkout settings
NEWEGG_ATC = True  # Set to False for "scan only" mode (no automatic add to cart)
NEWEGG_PLACE_ORDER = True  # Set to True to enable automatic order placement (click the Place Order button)
NEWEGG_PASSWORD = r'eRR")@KoDe:Y4$`'  # Your Newegg account password (using raw string)
NEWEGG_CVV = "1234"  # Your credit card CVV code

# Newegg timing settings
NEWEGG_PAGE_LOAD_WAIT = 0  # Time in seconds to wait for page to load
NEWEGG_MIN_RANDOM_REFRESH = 2.2  # Minimum time in seconds between page refreshes
NEWEGG_MAX_RANDOM_REFRESH = 3.8  # Maximum time in seconds between page refreshes
NEWEGG_MIN_REFRESH_COUNT = 250  # Minimum number of refreshes before session refresh
NEWEGG_MAX_REFRESH_COUNT = 300  # Maximum number of refreshes before session refresh

# Newegg browser settings
NEWEGG_BROWSER_WIDTH = 1920  # Newegg browser window width in pixels
NEWEGG_BROWSER_HEIGHT = 1080  # Newegg browser window height in pixels

# ===== BESTBUY SPECIFIC SETTINGS =====

# BestBuy URLs
BESTBUY_BASE_URL = "https://www.bestbuy.ca"
BESTBUY_CART_URL = "https://www.bestbuy.ca/en-ca/basket"
BESTBUY_SEARCH_URL = "https://www.bestbuy.ca/en-ca/search?path=currentPrice%253A%255B2%2BTO%2B3%255D%253Bcategory%253ABest%2BBuy%2BMobile%253BbrandName%253ABWOO&search=usb+cable&sort=priceLowToHigh"
BESTBUY_ORDERS_PAGE_URL = "https://www.bestbuy.ca/order/en-ca/order-history"

# BestBuy checkout settings
BESTBUY_ATC = False  # Set to False for "scan only" mode (no automatic add to cart)
BESTBUY_PLACE_ORDER = False  # Set to True to enable automatic order placement (click the Place Order button)
BESTBUY_PASSWORD = "MSIPerformance1!"  # Password for BestBuy account
BESTBUY_CVV = "1234"  # Your credit card CVV code

# BestBuy timing settings
BESTBUY_PAGE_LOAD_WAIT = 1  # Time in seconds to wait for page to load
BESTBUY_MIN_RANDOM_REFRESH = 1  # Minimum time in seconds between page refreshes
BESTBUY_MAX_RANDOM_REFRESH = 3  # Maximum time in seconds between page refreshes
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