import requests
import time
import datetime
import json
import os
import sys
import random
import threading
import webbrowser  # Add import for opening web browser
import queue  # For thread-safe communication between threads

# Import configuration settings from scraperconfig.py if available, otherwise use defaults
try:
    from scraperconfig import (
        # Discord notification settings
        DISCORD_WEBHOOK_URL, DISCORD_USER_ID, 
        ENABLE_DISCORD_STOCK_NOTIFICATIONS, ENABLE_DISCORD_STATUS_UPDATES,
        STATUS_UPDATE_INTERVAL, LOG_DIRECTORY,
        # Proxy configuration
        USE_PROXY, PROXY_URL, PROXY_USERNAME, PROXY_PASSWORD,
        ROTATE_PROXIES, PROXY_LIST
    )
    print("✅ Successfully loaded configuration from scraperconfig.py")
except ImportError:
    print("⚠️ Could not import scraperconfig.py, using default settings")
    # Default configuration
    DISCORD_WEBHOOK_URL = ""
    DISCORD_USER_ID = ""
    ENABLE_DISCORD_STOCK_NOTIFICATIONS = True
    ENABLE_DISCORD_STATUS_UPDATES = True
    STATUS_UPDATE_INTERVAL = 300  # 5 minutes
    LOG_DIRECTORY = "logs"
    # Default proxy configuration
    USE_PROXY = False
    PROXY_URL = ""  # Format: "http://ip:port" or "http://username:password@ip:port"
    PROXY_USERNAME = ""
    PROXY_PASSWORD = ""
    ROTATE_PROXIES = False
    PROXY_LIST = []  # List of proxy URLs to rotate through

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create a unique log filename with timestamp
log_filename = os.path.join(LOG_DIRECTORY, f"bestbuy_api_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Global variables
status_update_running = True
start_time = datetime.datetime.now()
refresh_count = {}  # Track refresh count per API URL
previously_available_skus = {}  # Track previously available SKUs per API URL
browser_open_times = {}  # Track when browser tabs were last opened for each SKU
api_lock = threading.Lock()  # Lock for thread-safe access to shared data

# Create a custom stdout class to capture terminal output
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log_file = open(filename, 'w', encoding='utf-8')
        self.lock = threading.Lock()  # Add lock for thread safety
        
    def write(self, message):
        with self.lock:  # Use lock to prevent interleaved output
            self.terminal.write(message)
            self.log_file.write(message)
            self.log_file.flush()  # Ensure output is written immediately
        
    def flush(self):
        with self.lock:
            self.terminal.flush()
            self.log_file.flush()

# Redirect stdout to our custom logger
sys.stdout = Logger(log_filename)
print(f"🔄 Logging started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log file: {log_filename}")

def format_time_elapsed(start_time):
    """
    Format the elapsed time since start_time in a human-readable format.
    
    Args:
        start_time (datetime): The start time
        
    Returns:
        str: Formatted time string (e.g., "2 hours, 15 minutes, 30 seconds")
    """
    now = datetime.datetime.now()
    elapsed = now - start_time
    
    # Calculate days, hours, minutes, seconds
    days, seconds = divmod(int(elapsed.total_seconds()), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    # Build the time string
    time_parts = []
    if days > 0:
        time_parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not time_parts:  # Always include seconds if no other units or if < 1 minute
        time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(time_parts)

def send_discord_notification(message, title=None, color=5814783):
    """
    Sends a notification to Discord using a webhook.
    
    Args:
        message (str): The message to send
        title (str, optional): The title of the embed
        color (int, optional): The color of the embed
    """
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN":
        print("⚠️ Discord webhook URL not configured. Notification not sent.")
        return
    
    # Create the payload
    payload = {
        "content": f"<@{DISCORD_USER_ID}>" if DISCORD_USER_ID else "",
        "embeds": [
            {
                "title": title if title else "BestBuy API Monitor Notification",
                "description": message,
                "color": color,
                "footer": {
                    "text": f"BestBuy API Monitor • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
        ]
    }
    
    # Send the request
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print(f"✅ Discord notification sent successfully")
    except Exception as e:
        print(f"❌ Error sending Discord notification: {e}")

def send_status_update():
    """
    Send a status update to Discord with the elapsed runtime and refresh count.
    """
    global refresh_count
    elapsed_time = format_time_elapsed(start_time)
    
    # Calculate total refresh count across all APIs
    total_refresh_count = sum(refresh_count.values())
    
    # Create status message with details for each API
    api_details = []
    for api_url, count in refresh_count.items():
        # Extract SKUs from the URL for display
        try:
            skus_param = api_url.split("skus=")[1].split("&")[0]
            num_skus = len(skus_param.replace("%7C", "|").split("|"))
            api_details.append(f"• API #{list(refresh_count.keys()).index(api_url) + 1}: {count} checks ({num_skus} SKUs)")
        except:
            api_details.append(f"• API #{list(refresh_count.keys()).index(api_url) + 1}: {count} checks")
    
    api_status = "\n".join(api_details)
    message = f"🕒 **Status Update**\n\n• Monitoring has been running for {elapsed_time}\n• Total API checks: {total_refresh_count}\n\n**API Details:**\n{api_status}"
    
    # Only send Discord notification if enabled
    if ENABLE_DISCORD_STATUS_UPDATES:
        send_discord_notification(message, title="BestBuy API Monitor Status", color=3447003)  # Blue color
    
    print(f"\n📊 Status update: Running for {elapsed_time}, total API checks: {total_refresh_count}")

def status_update_thread():
    """
    Thread function to send periodic status updates.
    """
    global status_update_running
    
    # Send initial status update
    send_status_update()
    
    while status_update_running:
        # Sleep for the specified interval
        for _ in range(STATUS_UPDATE_INTERVAL):
            if not status_update_running:
                break
            time.sleep(1)
        
        # Send status update if still running
        if status_update_running:
            send_status_update()

def get_proxy():
    """
    Get a proxy configuration for the request.
    
    Returns:
        dict: Proxy configuration for requests library or None if proxies are disabled
    """
    if not USE_PROXY:
        return None
        
    if ROTATE_PROXIES and PROXY_LIST:
        # Select a random proxy from the list
        proxy_url = random.choice(PROXY_LIST)
        print(f"🔄 Using proxy: {proxy_url.replace(PROXY_PASSWORD, '****') if PROXY_PASSWORD else proxy_url}")
    else:
        # Use the single configured proxy
        proxy_url = PROXY_URL
        
    # If username and password are provided separately, add them to the URL
    if PROXY_USERNAME and PROXY_PASSWORD and '@' not in proxy_url:
        # Split the URL into protocol and address
        if '://' in proxy_url:
            protocol, address = proxy_url.split('://', 1)
            proxy_url = f"{protocol}://{PROXY_USERNAME}:{PROXY_PASSWORD}@{address}"
        else:
            proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{proxy_url}"
    
    # Return the proxy configuration
    return {
        'http': proxy_url,
        'https': proxy_url
    }

def check_bestbuy_availability(api_url, api_index):
    """
    Check product availability using the BestBuy API.
    
    Args:
        api_url (str): The BestBuy API URL to query
        api_index (int): Index of this API URL for identification
        
    Returns:
        list: List of product dictionaries with availability information
    """
    global refresh_count, browser_open_times
    
    # Initialize tracking for this API URL if not already done
    with api_lock:
        if api_url not in refresh_count:
            refresh_count[api_url] = 0
        if api_url not in previously_available_skus:
            previously_available_skus[api_url] = set()
        
        refresh_count[api_url] += 1
    
    print(f"\n{'=' * 80}")
    print(f"🔄 Checking BestBuy API #{api_index} ⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")
    
    try:
        # Set up headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/vnd.bestbuy.simpleproduct.v1+json',
            'Accept-Language': 'en-CA',
            'Referer': 'https://www.bestbuy.ca/',
            'Origin': 'https://www.bestbuy.ca'
        }
        
        # Get proxy configuration
        proxies = get_proxy()
        
        # Make the API request with proxy if configured
        if proxies:
            print(f"🌐 Using proxy for this request")
            response = requests.get(api_url, headers=headers, proxies=proxies, timeout=30)
        else:
            response = requests.get(api_url, headers=headers, timeout=30)
            
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Print raw response for debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response content type: {response.headers.get('Content-Type', 'unknown')}")
        
        # Parse the JSON response
        data = response.json()
        
        # Debug: Print the structure of the response
        print(f"Response data type: {type(data)}")
        print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")
        
        # For deeper debugging, print a sample of the first product
        if isinstance(data, dict) and 'availabilities' in data and len(data['availabilities']) > 0:
            sample_product = data['availabilities'][0]
            print(f"Sample product structure:")
            print(f"  Keys: {list(sample_product.keys())}")
            if 'pickup' in sample_product:
                print(f"  Pickup type: {type(sample_product['pickup'])}")
                if isinstance(sample_product['pickup'], list) and len(sample_product['pickup']) > 0:
                    print(f"  First pickup item type: {type(sample_product['pickup'][0])}")
            if 'shipping' in sample_product:
                print(f"  Shipping type: {type(sample_product['shipping'])}")
        
        # Extract availability information for each product
        products = []
        available_products = []
        shipping_available_products = []  # Track products available for shipping
        
        if isinstance(data, dict) and 'availabilities' in data:
            for product in data['availabilities']:
                sku = product.get('sku', 'Unknown')
                name = product.get('name', 'Unknown Product')
                
                # Check pickup availability across all locations
                pickup_available = False
                shipping_available = False
                available_locations = []
                
                # Check pickup availability - handle both string and dictionary locations
                if 'pickup' in product:
                    if isinstance(product['pickup'], list):
                        for location in product['pickup']:
                            # Handle case where location is a string
                            if isinstance(location, str):
                                # Can't determine purchasability from a string, so skip
                                continue
                            # Handle case where location is a dictionary
                            elif isinstance(location, dict):
                                if location.get('purchasable', False):
                                    pickup_available = True
                                    store_name = location.get('storeName', 'Unknown Store')
                                    available_locations.append(store_name)
                    elif isinstance(product['pickup'], dict):
                        # Handle case where pickup is a single dictionary
                        if product['pickup'].get('purchasable', False):
                            pickup_available = True
                            store_name = product['pickup'].get('storeName', 'Unknown Store')
                            available_locations.append(store_name)
                
                # Check shipping availability
                if 'shipping' in product:
                    if isinstance(product['shipping'], dict):
                        shipping_available = product['shipping'].get('purchasable', False)
                    elif isinstance(product['shipping'], bool):
                        shipping_available = product['shipping']
                
                # Determine overall availability
                is_available = pickup_available or shipping_available
                
                # Create status text
                status_parts = []
                if pickup_available:
                    status_parts.append(f"Pickup: ✅ ({len(available_locations)} stores)")
                else:
                    status_parts.append("Pickup: ❌")
                    
                if shipping_available:
                    status_parts.append("Shipping: ✅")
                else:
                    status_parts.append("Shipping: ❌")
                
                status_text = " | ".join(status_parts)
                
                # Create product dictionary
                product_info = {
                    'sku': sku,
                    'name': name,
                    'available': is_available,
                    'pickup_available': pickup_available,
                    'shipping_available': shipping_available,
                    'available_locations': available_locations,
                    'status_text': status_text,
                    'api_index': api_index  # Add API index for identification
                }
                
                products.append(product_info)
                
                # Track available products for notifications
                if is_available:
                    available_products.append(product_info)
                
                # Track products available for shipping specifically
                if shipping_available:
                    shipping_available_products.append(product_info)
        
        # Display results
        print(f"\nAPI #{api_index} - Found {len(products)} products:")
        print("-" * 80)
        
        for product in products:
            availability_icon = "✅" if product['available'] else "❌"
            print(f"{availability_icon} SKU: {product['sku']} - {product['name']}")
            print(f"   Status: {product['status_text']}")
            
            if product['available'] and product['available_locations']:
                print(f"   Available at: {', '.join(product['available_locations'][:3])}" + 
                      (f" and {len(product['available_locations']) - 3} more stores" if len(product['available_locations']) > 3 else ""))
            
            print("-" * 80)
        
        # Check for newly available products
        newly_available_skus = set()
        with api_lock:  # Use lock for thread safety
            for product in available_products:
                if product['sku'] not in previously_available_skus[api_url]:
                    newly_available_skus.add(product['sku'])
        
        # Open browser for products available for shipping, but only if not opened recently
        current_time = datetime.datetime.now()
        for product in shipping_available_products:
            sku = product['sku']
            
            # Thread-safe check and update of browser_open_times
            with api_lock:
                # Check if we've opened this product recently (within the last 2 minutes)
                if sku in browser_open_times:
                    last_open_time = browser_open_times[sku]
                    time_since_last_open = (current_time - last_open_time).total_seconds()
                    
                    if time_since_last_open < 120:  # 2 minutes = 120 seconds
                        print(f"⏱️ Not opening browser for SKU {sku} - last opened {time_since_last_open:.1f} seconds ago")
                        continue
                
                # If we reach here, we should open the browser
                product_url = f"https://www.bestbuy.ca/en-ca/product/{sku}"
                print(f"🌐 Opening browser for in-stock product: {product['name']} (SKU: {sku})")
                webbrowser.open(product_url)
                
                # Update the last open time for this SKU
                browser_open_times[sku] = current_time
                
                # Send a Discord notification about the browser opening
                if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                    browser_message = f"🌐 **Browser Window Opened**\n\n**Product:** {product['name']}\n**SKU:** {product['sku']}\n**Status:** {product['status_text']}\n**API:** #{api_index}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n🔗 [View on BestBuy](https://www.bestbuy.ca/en-ca/product/{sku})"
                    send_discord_notification(browser_message, title="🌐 Browser Window Opened", color=16753920)  # Orange color
        
        # Send notifications for newly available products
        if newly_available_skus and ENABLE_DISCORD_STOCK_NOTIFICATIONS:
            for product in available_products:
                if product['sku'] in newly_available_skus:
                    # Create notification message
                    message = f"🚨 **IN STOCK ALERT!**\n\n**Product:** {product['name']}\n**SKU:** {product['sku']}\n**Status:** {product['status_text']}\n**API:** #{api_index}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    if product['available_locations']:
                        message += f"\n\n**Available at:** {', '.join(product['available_locations'][:5])}"
                        if len(product['available_locations']) > 5:
                            message += f" and {len(product['available_locations']) - 5} more stores"
                    
                    message += f"\n\n🔗 [View on BestBuy](https://www.bestbuy.ca/en-ca/product/{product['sku']})"
                    
                    # Send Discord notification
                    print(f"📱 Sending Discord notification for SKU {product['sku']}...")
                    send_discord_notification(message, title="✅ BestBuy Stock Alert!", color=5814783)
        
        # Update previously available SKUs
        with api_lock:  # Use lock for thread safety
            previously_available_skus[api_url].clear()
            for product in available_products:
                previously_available_skus[api_url].add(product['sku'])
        
        return products
        
    except Exception as e:
        print(f"❌ Error checking BestBuy API #{api_index}: {e}")
        import traceback
        traceback.print_exc()  # Print the full stack trace for better debugging
        return []

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
            print(f"API #{api_index} - Monitoring {len(skus)} SKUs: {', '.join(skus[:5])}" + (f" and {len(skus) - 5} more" if len(skus) > 5 else ""))
        except:
            print(f"API #{api_index} - Could not extract SKUs from URL")
        
        # Initial check
        check_bestbuy_availability(api_url, api_index)
        
        # Continuous monitoring with random refresh interval
        while status_update_running:  # Use global flag to control all threads
            # Random refresh interval between 0.1 and 0.2 seconds
            refresh_time = random.uniform(0.1, 0.2)
            print(f"\n⏱️  API #{api_index} - Next check in {refresh_time:.2f} seconds...")
            time.sleep(refresh_time)
            
            # Check availability
            check_bestbuy_availability(api_url, api_index)
            
    except Exception as e:
        print(f"\n❌ API #{api_index} - Unhandled exception: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Main function to run the BestBuy API availability checker.
    """
    global status_update_running
    
    # List of API URLs to monitor
    api_urls = [
        # Default API URL (original)
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.standardproduct.v1%2Bjson&accept-language=en-CA&locations=172%7C936%7C246%7C173%7C174%7C980&postalCode=N5P&skus=16566911",
        
        # New API URL (additional)
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.simpleproduct.v1%2Bjson&accept-language=en-CA&locations=223%7C925%7C959%7C937%7C943%7C188%7C182%7C613%7C965%7C180%7C192%7C956%7C194%7C237%7C179%7C187%7C931%7C195%7C985%7C193%7C927%7C197%7C196%7C977%7C198%7C259%7C200%7C203%7C199%7C260%7C617%7C932%7C178%7C949%7C163%7C233%7C938%7C164&postalCode=L1X&skus=18938753%7C18938754%7C18938755%7C18938757%7C18934247%7C18934177%7C18938756%7C18938758%7C19190988%7C18931628%7C18931627"
    ]
    
    # Get API URLs from command line if provided
    if len(sys.argv) > 1:
        api_urls = [sys.argv[1]]
        if len(sys.argv) > 2:
            api_urls.append(sys.argv[2])
    
    print(f"Starting BestBuy API availability monitoring for {len(api_urls)} API endpoints")
    
    # Start the status update thread
    status_thread = threading.Thread(target=status_update_thread, daemon=True)
    status_thread.start()
    
    # Create and start a thread for each API URL
    api_threads = []
    for i, api_url in enumerate(api_urls):
        api_index = i + 1
        print(f"Starting monitor thread for API #{api_index}")
        thread = threading.Thread(target=api_monitor_thread, args=(api_url, api_index), daemon=True)
        thread.start()
        api_threads.append(thread)
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
            
            # Check if any API threads have died
            for i, thread in enumerate(api_threads):
                if not thread.is_alive():
                    print(f"⚠️ API thread #{i+1} has died. Restarting...")
                    # Restart the thread
                    api_index = i + 1
                    api_url = api_urls[i]
                    new_thread = threading.Thread(target=api_monitor_thread, args=(api_url, api_index), daemon=True)
                    new_thread.start()
                    api_threads[i] = new_thread
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user.")
    
    except Exception as e:
        print(f"\n❌ Unhandled exception in main thread: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop all threads
        status_update_running = False
        
        # Send final status update
        elapsed_time = format_time_elapsed(start_time)
        total_refresh_count = sum(refresh_count.values())
        final_message = f"🛑 **Monitoring Ended**\n\n• Total runtime: {elapsed_time}\n• Total API checks: {total_refresh_count}"
        if ENABLE_DISCORD_STATUS_UPDATES:
            send_discord_notification(final_message, title="BestBuy API Monitor Stopped", color=15158332)  # Red color
        print(f"\n📊 Final status: Total runtime {elapsed_time}, total API checks: {total_refresh_count}")
        
        # Log termination time
        print(f"\n🔄 Logging ended at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Log saved to: {log_filename}")
        
        # Restore original stdout and close log file
        if isinstance(sys.stdout, Logger):
            sys.stdout.log_file.close()
            sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main() 