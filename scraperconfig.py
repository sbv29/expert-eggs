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
USE_PROXY = True  # Set to True to enable proxy
PROXY_URL = "socks5h://user-spjgdb1uj2-country-ca:bi1dpk70AZ0fuseHP~@gate.smartproxy.com:7000"  # Your proxy server URL

# If your proxy requires authentication, you can specify credentials:
PROXY_USERNAME = ""  # Your proxy username
PROXY_PASSWORD = ""  # Your proxy password

# For proxy rotation (multiple proxies)
ROTATE_PROXIES = False  # Set to True to rotate through multiple proxies
PROXY_LIST = [
    # List of proxy URLs to rotate throughz
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10000",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10001",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10002",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10003",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10004",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10005",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10006",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10007",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10008",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10009",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10010",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10011",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10012",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10013",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10014",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10015",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10016",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10017",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10018",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10019",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10020",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10021",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10022",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10023",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10024",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10025",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10026",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10027",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10028",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10029",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10030",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10031",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10032",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10033",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10034",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10035",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10036",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10037",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10038",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10039",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10040",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10041",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10042",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10043",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10044",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10045",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10046",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10047",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10048",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10049",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10050",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10051",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10052",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10053",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10054",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10055",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10056",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10057",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10058",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10059",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10060",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10061",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10062",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10063",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10064",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10065",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10066",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10067",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10068",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10069",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10070",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10071",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10072",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10073",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10074",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10075",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10076",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10077",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10078",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10079",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10080",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10081",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10082",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10083",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10084",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10085",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10086",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10087",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10088",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10089",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10090",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10091",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10092",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10093",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10094",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10095",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10096",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10097",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10098",
    "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:10099"
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