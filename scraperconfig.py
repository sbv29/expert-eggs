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

# Browser and page loading settings
PAGE_LOAD_WAIT = 0  # Time in seconds to wait for page to load
MIN_RANDOM_REFRESH = 2  # Minimum time in seconds between page refreshes
MAX_RANDOM_REFRESH = 6  # Maximum time in seconds between page refreshes

# Session refresh settings
MIN_REFRESH_COUNT = 250  # Minimum number of refreshes before session refresh
MAX_REFRESH_COUNT = 300  # Maximum number of refreshes before session refresh

# Discord notification settings
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1345475006058205194/XhCEXuvoOWtqO_7WS9XiIy_LLJwRcPPFmvcPoTS0772R1iaMSnMC1N-aO41oLRParlBD"
DISCORD_USER_ID = "78875182906748928"
ENABLE_DISCORD_STOCK_NOTIFICATIONS = True  # Set to False to disable in-stock notifications
ENABLE_DISCORD_STATUS_UPDATES = False  # Set to False to disable periodic status updates
STATUS_UPDATE_INTERVAL = 15 * 60  # Status updates in Discord (15 * 60 = 900 seconds = 15 minutes)

# ===== NEWEGG SPECIFIC SETTINGS =====

# Newegg URLs
NEWEGG_ORDERS_PAGE_URL = "https://secure.newegg.ca/orders/list"  # Orders page URL for session refreshing
NEWEGG_SEARCH_PAGE_URL = "https://www.newegg.ca/p/pl?N=100007708%20601469153%20601469158"  # Search page URL for product search

# Newegg product filtering settings
NEWEGG_SHOW_COMBO_PRODUCTS = True  # Set to True to show products with "Combo" in the title

# Newegg checkout settings
NEWEGG_PLACE_ORDER = False  # Set to False to disable actual order placement (do not click place order button)
NEWEGG_PASSWORD = "JW5*lObuFv1#xM*"  # Password for Newegg account credentials
NEWEGG_CVV = "1234"  # CVV code for credit card

# ===== BESTBUY SPECIFIC SETTINGS =====

# BestBuy URLs
BESTBUY_BASE_URL = "https://www.bestbuy.ca"
BESTBUY_CART_URL = "https://www.bestbuy.ca/en-ca/basket"
BESTBUY_SEARCH_URL = "https://www.bestbuy.ca/en-ca/collection/nvidia-graphic-cards-rtx-50-series/bltbd7cf78bd1d558ef?icmp=computing_evergreen_nvidia_graphics_cards_ssc_sbc_50_series"
BESTBUY_ORDERS_PAGE_URL = "https://www.bestbuy.ca/order/en-ca/order-history"

# BestBuy account settings
BESTBUY_PASSWORD = "MSIPerformance1!"  # Password for BestBuy account

# ===== DIRECTORY CREATION =====

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create cookies directory if it doesn't exist
if not os.path.exists(COOKIE_DIR):
    os.makedirs(COOKIE_DIR) 