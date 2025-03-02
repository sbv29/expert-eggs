"""
Configuration settings for the Newegg scraper.
Contains all configurable parameters and constants.
"""
import os

# File paths
COOKIE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies")
COOKIE_FILE = os.path.join(COOKIE_DIR, "cookies.json")  # Path to cookie file
LOG_DIRECTORY = "logs"  # Directory to store log files

# Browser and page loading settings
PAGE_LOAD_WAIT = 0  # Wait time in seconds for page to load - increase if CAPTCHA is triggered
MIN_RANDOM_REFRESH = .25  # Minimum seconds to wait between page refreshes
MAX_RANDOM_REFRESH = 1.25  # Maximum seconds to wait between page refreshes

# Session refresh settings
MIN_REFRESH_COUNT = 50  # Minimum number of page refreshes before refreshing session
MAX_REFRESH_COUNT = 75  # Maximum number of page refreshes before refreshing session

# URLs
ORDERS_PAGE_URL = "https://secure.newegg.ca/orders/list"  # Orders page URL for session refreshing
SEARCH_PAGE_URL = "https://www.newegg.ca/p/pl?N=100007708%20601469156&d=5090&isdeptsrh=1"  # Search page URL for product search

# Discord notification settings
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1345475006058205194/XhCEXuvoOWtqO_7WS9XiIy_LLJwRcPPFmvcPoTS0772R1iaMSnMC1N-aO41oLRParlBD"
DISCORD_USER_ID = "78875182906748928"
ENABLE_DISCORD_STOCK_NOTIFICATIONS = True  # Set to False to disable in-stock notifications
ENABLE_DISCORD_STATUS_UPDATES = False  # Set to False to disable periodic status updates
STATUS_UPDATE_INTERVAL = 15 * 60  # Status updates in Discord (15 * 60 = 900 seconds = 15 minutes)

# Product filtering settings
SHOW_COMBO_PRODUCTS = True  # Set to True to show products with "Combo" in the title

# Checkout settings
PLACE_ORDER = False  # Set to False to disable actual order placement
NEWEGG_PASSWORD = "JW5*lObuFv1#xM*"  # Password for Newegg account credentials
NEWEGG_CVV = "1234"  # CVV code for credit card

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create cookies directory if it doesn't exist
if not os.path.exists(COOKIE_DIR):
    os.makedirs(COOKIE_DIR) 