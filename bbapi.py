import requests
import time
import datetime
import json
import os
import sys
import random
import threading
import random
import traceback

# Try to import browserforge, but provide fallback if it fails
try:
    import browserforge
    HAS_BROWSERFORGE = True
except ImportError:
    HAS_BROWSERFORGE = False

# Create logs directory if it doesn't exist
LOG_DIRECTORY = "logs"
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create a unique log filename with timestamp
log_filename = os.path.join(LOG_DIRECTORY, f"bestbuy_api_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Global variables
status_update_running = True
start_time = datetime.datetime.now()
refresh_count = {}
api_lock = threading.Lock()
last_proxy_index = -1  # Track the last used proxy index

# Try to import configuration from scraperconfig.py
try:
    from scraperconfig import (
        USE_PROXY, ROTATE_PROXIES, PROXY_LIST, 
        PROXY_USERNAME, PROXY_PASSWORD,
        DISCORD_WEBHOOK_URL, DISCORD_USER_ID,
        ENABLE_DISCORD_STOCK_NOTIFICATIONS, ENABLE_DISCORD_STATUS_UPDATES
    )
    print("✅ Successfully loaded configuration from scraperconfig.py")
    
    # Log proxy configuration
    if USE_PROXY:
        if ROTATE_PROXIES and PROXY_LIST:
            print(f"✅ Proxy status: Enabled, Rotation: Enabled ({len(PROXY_LIST)} proxies available)")
        else:
            print("✅ Proxy status: Enabled, Rotation: Disabled")
    else:
        print("✅ Proxy status: Disabled")
        
except ImportError:
    print("⚠️ Could not import scraperconfig.py, using default settings")
    USE_PROXY = False
    ROTATE_PROXIES = False
    PROXY_LIST = []
    PROXY_USERNAME = ""
    PROXY_PASSWORD = ""
    DISCORD_WEBHOOK_URL = ""
    DISCORD_USER_ID = ""
    ENABLE_DISCORD_STOCK_NOTIFICATIONS = False
    ENABLE_DISCORD_STATUS_UPDATES = False

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log_file = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
        
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

# Redirect stdout to our custom logger
sys.stdout = Logger(log_filename)

def get_browserforge_headers():
    """
    Generate realistic browser headers using BrowserForge if available,
    otherwise use a predefined set of headers.
    
    Returns:
        tuple: (headers, browser_instance, fingerprint)
    """
    try:
        if not HAS_BROWSERFORGE:
            raise ImportError("BrowserForge module not available")
            
        # Check if Browser class exists in browserforge
        if not hasattr(browserforge, 'Browser'):
            raise AttributeError("module 'browserforge' has no attribute 'Browser'")
            
        # Generate a realistic browser fingerprint
        browser = browserforge.Browser()
        
        # Create headers with BrowserForge
        headers = {
            'User-Agent': browser.user_agent,
            'Accept': 'application/vnd.bestbuy.simpleproduct.v1+json',
            'Accept-Language': browser.language,
            'Sec-CH-UA': browser.sec_ch_ua,
            'Sec-CH-UA-Mobile': browser.sec_ch_ua_mobile,
            'Sec-CH-UA-Platform': browser.sec_ch_ua_platform,
            'Referer': 'https://www.bestbuy.ca/',
            'Origin': 'https://www.bestbuy.ca',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            **browser.additional_headers
        }
        
        # Get browser fingerprint for logging
        fingerprint = browser.get_fingerprint()
        
        return headers, browser, fingerprint
    
    except Exception as e:
        print(f"❌ Error generating BrowserForge headers: {e}")
        
        # Fallback to predefined headers
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/vnd.bestbuy.simpleproduct.v1+json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.bestbuy.ca/',
            'Origin': 'https://www.bestbuy.ca',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        print(f"ℹ️ Using fallback headers with User-Agent: {headers['User-Agent']}")
        return headers, None, None

def get_proxy():
    """
    Get proxy configuration based on settings in scraperconfig.py.
    
    Returns:
        dict or None: Proxy configuration for requests
    """
    global last_proxy_index
    
    if not USE_PROXY:
        return None
        
    proxy_url = None
    
    # Use rotating proxies if enabled and available
    if ROTATE_PROXIES and PROXY_LIST:
        # Select next proxy in rotation
        last_proxy_index = (last_proxy_index + 1) % len(PROXY_LIST)
        proxy_url = PROXY_LIST[last_proxy_index]
        print(f"🔄 Using rotating proxy #{last_proxy_index + 1}/{len(PROXY_LIST)}")
    
    if not proxy_url:
        print("⚠️ No proxy URL available")
        return None
        
    # Create proxy configuration for requests
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    # Mask password in logs for security
    masked_url = proxy_url
    if '@' in proxy_url:
        # Format: http://username:password@host:port
        protocol, rest = proxy_url.split('://', 1)
        auth, host = rest.split('@', 1)
        if ':' in auth:
            username, password = auth.split(':', 1)
            masked_url = f"{protocol}://{username}:****@{host}"
    
    print(f"🌐 Using proxy: {masked_url}")
    return proxies

def send_discord_notification(title, message, color=0x00FF00):
    """
    Send a notification to Discord using a webhook.
    
    Args:
        title (str): Title of the notification
        message (str): Content of the notification
        color (int): Color of the embed (default: green)
    """
    if not DISCORD_WEBHOOK_URL:
        return
        
    try:
        # Create embed for Discord
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.datetime.now().isoformat(),
            "footer": {
                "text": f"BestBuy API Monitor"
            }
        }
        
        # Add user mention if ID is provided
        content = ""
        if DISCORD_USER_ID:
            content = f"<@{DISCORD_USER_ID}>"
            
        # Prepare payload
        payload = {
            "content": content,
            "embeds": [embed]
        }
        
        # Send webhook request
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 204:
            print(f"✅ Discord notification sent: {title}")
        else:
            print(f"❌ Failed to send Discord notification: {response.status_code} {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending Discord notification: {e}")

def check_bestbuy_availability(api_url, api_index):
    """
    Check product availability using the BestBuy API.
    
    Args:
        api_url (str): The BestBuy API URL to query
        api_index (int): Index of this API URL for identification
    """
    # Initialize tracking for this API URL
    with api_lock:
        if api_url not in refresh_count:
            refresh_count[api_url] = 0
        refresh_count[api_url] += 1
    
    print(f"\n{'=' * 80}")
    print(f"🔄 Checking BestBuy API #{api_index} ⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")
    
    try:
        # Generate headers
        headers, browser, fingerprint = get_browserforge_headers()
        
        # Get proxy configuration
        proxies = get_proxy()
        
        # Prepare request parameters
        request_params = {
            'headers': headers,
            'timeout': 30
        }
        
        if proxies:
            request_params['proxies'] = proxies
        
        # Make the API request with retries
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"📡 API request attempt {attempt}/{max_retries}")
                response = requests.get(api_url, **request_params)
                response.raise_for_status()
                break  # Success, exit retry loop
            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    raise  # Re-raise the exception if all retries failed
                print(f"⚠️ Request failed (attempt {attempt}/{max_retries}): {e}")
                print(f"⏱️ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        # Parse the JSON response
        data = response.json()
        
        # Extract and display product availability
        if isinstance(data, dict) and 'availabilities' in data:
            print("\nProduct Availability:")
            for product in data['availabilities']:
                sku = product.get('sku', 'Unknown')
                name = product.get('name', 'Unknown Product')
                
                # Check pickup and shipping availability
                pickup_available = False
                shipping_available = False
                
                if 'pickup' in product:
                    pickup_available = any(
                        location.get('purchasable', False) 
                        for location in product['pickup'] 
                        if isinstance(location, dict)
                    )
                
                if 'shipping' in product:
                    shipping_available = product['shipping'].get('purchasable', False)
                
                # Print availability status
                status = []
                if pickup_available:
                    status.append("Pickup: ✅")
                else:
                    status.append("Pickup: ❌")
                
                if shipping_available:
                    status.append("Shipping: ✅")
                else:
                    status.append("Shipping: ❌")
                
                print(f"SKU: {sku} - {name}")
                print(f"Status: {' | '.join(status)}")
                print("-" * 40)
                
                # Send notification if product is available and notifications are enabled
                if (pickup_available or shipping_available) and ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                    availability_type = []
                    if pickup_available:
                        availability_type.append("Store Pickup")
                    if shipping_available:
                        availability_type.append("Shipping")
                    
                    notification_title = f"🚨 BestBuy Product Available!"
                    notification_message = (
                        f"**Product:** {name}\n"
                        f"**SKU:** {sku}\n"
                        f"**Available for:** {', '.join(availability_type)}\n"
                        f"**Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"**Link:** https://www.bestbuy.ca/en-ca/product/{sku}"
                    )
                    
                    send_discord_notification(notification_title, notification_message, 0x00FF00)  # Green color
        else:
            print(f"⚠️ Unexpected API response format:")
            print(json.dumps(data, indent=2))
        
    except requests.exceptions.RequestException as e:
        error_message = f"❌ Error checking BestBuy API #{api_index}: {e}"
        print(error_message)
        print(f"Full traceback:\n{traceback.format_exc()}")
        
        if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
            send_discord_notification(
                "⚠️ API Connection Error",
                f"Error checking BestBuy API #{api_index}:\n```\n{str(e)}\n```",
                0xFF0000  # Red color
            )
    
    except Exception as e:
        error_message = f"❌ Unexpected error checking BestBuy API #{api_index}: {e}"
        print(error_message)
        print(f"Full traceback:\n{traceback.format_exc()}")
        
        if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
            send_discord_notification(
                "⚠️ Unexpected Error",
                f"Unexpected error checking BestBuy API #{api_index}:\n```\n{str(e)}\n```",
                0xFF0000  # Red color
            )

def api_monitor_thread(api_url, api_index):
    """
    Thread function to continuously monitor a specific API URL.
    
    Args:
        api_url (str): The BestBuy API URL to monitor
        api_index (int): Index of this API URL for identification
    """
    try:
        # Extract SKUs from the URL for display
        try:
            skus_param = api_url.split("skus=")[1].split("&")[0]
            skus = skus_param.replace("%7C", "|").split("|")
            print(f"API #{api_index} - Monitoring {len(skus)} SKUs: {', '.join(skus[:5])}" + 
                  (f" and {len(skus) - 5} more" if len(skus) > 5 else ""))
        except:
            print(f"API #{api_index} - Could not extract SKUs from URL")
        
        # Initial check
        check_bestbuy_availability(api_url, api_index)
        
        # Continuous monitoring with random refresh interval
        while status_update_running:
            # Random refresh interval between 3.5 and 6 seconds
            refresh_time = random.uniform(3.5, 6)
            print(f"\n⏱️  API #{api_index} - Next check in {refresh_time:.2f} seconds...")
            time.sleep(refresh_time)
            
            # Check availability
            check_bestbuy_availability(api_url, api_index)
            
    except Exception as e:
        print(f"\n❌ API #{api_index} - Unhandled exception: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")

def status_update_thread():
    """
    Thread function to send periodic status updates to Discord.
    """
    if not ENABLE_DISCORD_STATUS_UPDATES or not DISCORD_WEBHOOK_URL:
        return
        
    try:
        while status_update_running:
            # Wait for 15 minutes
            for _ in range(15 * 60):
                if not status_update_running:
                    return
                time.sleep(1)
                
            # Calculate runtime and total checks
            elapsed_time = datetime.datetime.now() - start_time
            hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            with api_lock:
                total_checks = sum(refresh_count.values())
                checks_per_api = {f"API #{i+1}": count for i, count in enumerate(refresh_count.values())}
            
            # Create status message
            status_message = (
                f"**Runtime:** {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
                f"**Total API Checks:** {total_checks}\n"
                f"**Checks per API:**\n"
            )
            
            for api_name, count in checks_per_api.items():
                status_message += f"- {api_name}: {count} checks\n"
                
            if USE_PROXY and ROTATE_PROXIES and PROXY_LIST:
                status_message += f"\n**Proxy Configuration:**\n- Using {len(PROXY_LIST)} rotating proxies"
            
            # Send status update
            send_discord_notification(
                "📊 BestBuy API Monitor Status",
                status_message,
                0x3498DB  # Blue color
            )
            
    except Exception as e:
        print(f"❌ Error in status update thread: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")

def main():
    """
    Main function to run the BestBuy API availability checker.
    """
    global status_update_running
    
    print(f"🔄 Logging started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 Log file: {log_filename}")
    
    # List of API URLs to monitor
    api_urls = [
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.simpleproduct.v1%2Bjson&accept-language=en-CA&locations=197%7C198%7C977%7C259%7C193%7C203%7C199%7C931%7C194%7C195%7C617%7C192%7C196%7C965%7C927%7C180%7C188%7C938%7C943%7C164%7C237%7C179%7C163%7C233%7C932%7C956%7C187%7C200%7C202%7C176%7C260%7C937%7C926%7C329%7C503%7C764%7C795%7C916%7C1016%7C319%7C544%7C910%7C161%7C954%7C207%7C175%7C930%7C223%7C622%7C160%7C181%7C245%7C925%7C985%7C990%7C959%7C178%7C182%7C949&postalCode=M5A&skus=18934175%7C19190987%7C18934178%7C19183868%7C18931348%7C18931347%7C18931631%7C18969272%7C18938759%7C19177947%7C18934180%7C18938760%7C19177946%7C19177950%7C18931397%7C19183867%7C19183866%7C18931629%7C18934179%7C18931632%7C19186504%7C18971064%7C18938752%7C18938751",
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.simpleproduct.v1%2Bjson&accept-language=en-CA&locations=197%7C198%7C977%7C259%7C193%7C203%7C199%7C931%7C194%7C195%7C617%7C192%7C196%7C965%7C927%7C180%7C188%7C938%7C943%7C164%7C237%7C179%7C163%7C233%7C932%7C956%7C187%7C200%7C202%7C176%7C260%7C937%7C926%7C329%7C503%7C764%7C795%7C916%7C1016%7C319%7C544%7C910%7C161%7C954%7C207%7C175%7C930%7C223%7C622%7C160%7C181%7C245%7C925%7C985%7C990%7C959%7C178%7C182%7C949&postalCode=M5A&skus=19190988%7C18938758%7C18931628%7C18931627"
    ]
    
    print(f"Starting BestBuy API availability monitoring for {len(api_urls)} API endpoints")
    
    # Create and start a thread for each API URL
    api_threads = []
    for i, api_url in enumerate(api_urls):
        api_index = i + 1
        print(f"Starting monitor thread for API #{api_index}")
        thread = threading.Thread(target=api_monitor_thread, args=(api_url, api_index), daemon=True)
        thread.start()
        api_threads.append(thread)
    
    # Start status update thread if enabled
    if ENABLE_DISCORD_STATUS_UPDATES and DISCORD_WEBHOOK_URL:
        print("Starting status update thread")
        status_thread = threading.Thread(target=status_update_thread, daemon=True)
        status_thread.start()
    
    try:
        # Send initial status notification
        if ENABLE_DISCORD_STATUS_UPDATES and DISCORD_WEBHOOK_URL:
            send_discord_notification(
                "🚀 BestBuy API Monitor Started",
                f"Monitoring {len(api_urls)} API endpoints with {len(PROXY_LIST) if USE_PROXY and ROTATE_PROXIES else 'no'} proxies",
                0x3498DB  # Blue color
            )
        
        # Keep the main thread running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user.")
        status_update_running = False
    
    finally:
        # Calculate runtime and total checks
        elapsed_time = datetime.datetime.now() - start_time
        total_checks = sum(refresh_count.values())
        
        print(f"\n📊 Final status: Total runtime {elapsed_time}, total API checks: {total_checks}")
        print(f"🔄 Logging ended at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Log saved to: {log_filename}")
        
        # Send final status notification
        if ENABLE_DISCORD_STATUS_UPDATES and DISCORD_WEBHOOK_URL:
            hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            final_status = (
                f"**Runtime:** {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
                f"**Total API Checks:** {total_checks}\n"
                f"**Reason:** Stopped by user"
            )
            
            send_discord_notification(
                "🛑 BestBuy API Monitor Stopped",
                final_status,
                0xFF9900  # Orange color
            )
        
        # Restore original stdout and close log file
        if isinstance(sys.stdout, Logger):
            sys.stdout.log_file.close()
            sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()