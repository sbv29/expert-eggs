import aiohttp
import asyncio
import time
import datetime
import json
import os
import sys
import random
import threading
import webbrowser
import atexit
import shutil
from browserforge.headers import HeaderGenerator

# Import configuration settings from scraperconfig.py if available
try:
    from scraperconfig import (
        DISCORD_WEBHOOK_URL, DISCORD_USER_ID,
        ENABLE_DISCORD_STOCK_NOTIFICATIONS, ENABLE_DISCORD_STATUS_UPDATES,
        STATUS_UPDATE_INTERVAL, LOG_DIRECTORY,
        USE_PROXY, PROXY_URL, PROXY_USERNAME, PROXY_PASSWORD,
        ROTATE_PROXIES, PROXY_LIST
    )
    print("✅ Successfully loaded configuration from scraperconfig.py")
except ImportError:
    print("⚠️ Could not import scraperconfig.py, using default settings")
    DISCORD_WEBHOOK_URL = ""
    DISCORD_USER_ID = ""
    ENABLE_DISCORD_STOCK_NOTIFICATIONS = True
    ENABLE_DISCORD_STATUS_UPDATES = True
    STATUS_UPDATE_INTERVAL = 300
    LOG_DIRECTORY = "logs"
    
    # Set proxy configuration directly in the script
    USE_PROXY = True  # Enable proxy usage
    PROXY_URL = "http://bebac9d48e9c5179beda:3a3afbe5ebf9f60a@gw.dataimpulse.com:823"  # Your proxy URL
    PROXY_USERNAME = ""  # Username is already in the URL
    PROXY_PASSWORD = ""  # Password is already in the URL
    ROTATE_PROXIES = False
    PROXY_LIST = []

# Print proxy configuration for confirmation
print(f"🌐 Proxy enabled: {USE_PROXY}")
if USE_PROXY:
    # Hide password in logs for security
    masked_proxy = PROXY_URL.replace(PROXY_URL.split('@')[0].split('//')[1].split(':')[1], '****') if '@' in PROXY_URL else PROXY_URL
    print(f"🌐 Using proxy: {masked_proxy}")

# Initialize BrowserForge Header Generator
headers_generator = HeaderGenerator(browser='chrome', os='windows', device='desktop', locale='en-US')

# Ensure log directory exists
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Create a unique log filename with timestamp
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = os.path.join(LOG_DIRECTORY, f"bestbuy_api_log_{timestamp}.txt")
# Also create a final output filename for when the script stops
final_output_filename = os.path.join(LOG_DIRECTORY, f"bestbuy_final_output_{timestamp}.txt")

# Logging mechanism
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log_file = open(filename, 'w', encoding='utf-8')
        self.lock = threading.Lock()
        self.all_output = []  # Store all output for final save

    def write(self, message):
        with self.lock:
            self.terminal.write(message)
            self.log_file.write(message)
            self.log_file.flush()
            self.all_output.append(message)  # Store message for final output

    def flush(self):
        with self.lock:
            self.terminal.flush()
            self.log_file.flush()
    
    def save_final_output(self, filename):
        """Save all captured output to a final file when the script exits"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(''.join(self.all_output))
            print(f"\n📄 Final output saved to: {filename}")
            
            # Also make a copy of the log file as a backup
            shutil.copy2(log_filename, filename)
            print(f"📄 Log file copied to: {filename}")
        except Exception as e:
            print(f"\n❌ Error saving final output: {e}")

# Create logger instance
logger = Logger(log_filename)
sys.stdout = logger

# Register function to save output when script exits
def save_output_on_exit():
    print(f"\n🔄 Script terminated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 Saving complete output to: {final_output_filename}")
    if isinstance(sys.stdout, Logger):
        sys.stdout.save_final_output(final_output_filename)

# Register the exit handler
atexit.register(save_output_on_exit)

print(f"🔄 Logging started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log file: {log_filename}")
print(f"📝 Final output will be saved to: {final_output_filename}")

async def send_discord_notification(message, title=None, color=5814783):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Discord webhook URL not configured. Notification not sent.")
        return

    payload = {
        "content": f"<@{DISCORD_USER_ID}>" if DISCORD_USER_ID else "",
        "embeds": [{
            "title": title if title else "BestBuy API Monitor Notification",
            "description": message,
            "color": color,
            "footer": {"text": f"BestBuy API Monitor • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }

    try:
        # Create a separate session just for Discord to avoid proxy issues with Discord
        async with aiohttp.ClientSession() as discord_session:
            async with discord_session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                print("✅ Discord notification sent successfully")
    except Exception as e:
        print(f"❌ Error sending Discord notification: {e}")

async def check_bestbuy_availability(session, api_url, api_index):
    headers = headers_generator.generate()
    
    # Set up proxy if enabled
    proxy = None
    if USE_PROXY:
        if ROTATE_PROXIES and PROXY_LIST:
            proxy = random.choice(PROXY_LIST)
        else:
            proxy = PROXY_URL
        print(f"🌐 API #{api_index} using proxy for request")
    
    try:
        # Print request details for debugging
        print(f"🔄 API #{api_index} - Sending request to {api_url[:50]}...")
        
        # Make the request with proxy if configured
        start_time = time.time()
        async with session.get(api_url, headers=headers, proxy=proxy, timeout=30) as response:
            elapsed = time.time() - start_time
            print(f"✅ API #{api_index} - Response received in {elapsed:.2f}s (Status: {response.status})")
            
            if response.status == 200:
                try:
                    data = await response.json()
                    # Process the data here
                    if isinstance(data, dict) and 'availabilities' in data:
                        products = data['availabilities']
                        print(f"📦 API #{api_index} - Found {len(products)} products")
                        
                        # Process each product
                        for product in products:
                            sku = product.get('sku', 'Unknown')
                            name = product.get('name', 'Unknown Product')
                            
                            # Check shipping availability
                            shipping_available = False
                            if 'shipping' in product:
                                if isinstance(product['shipping'], dict):
                                    shipping_available = product['shipping'].get('purchasable', False)
                                elif isinstance(product['shipping'], bool):
                                    shipping_available = product['shipping']
                            
                            # Print product status
                            status = "✅ IN STOCK" if shipping_available else "❌ Out of Stock"
                            print(f"{status} - SKU: {sku} - {name}")
                            
                            # Send notification if in stock
                            if shipping_available and ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                                message = f"🚨 **IN STOCK ALERT!**\n\n**Product:** {name}\n**SKU:** {sku}\n**Status:** Shipping Available\n**API:** #{api_index}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}"
                                message += f"\n\n🔗 [View on BestBuy](https://www.bestbuy.ca/en-ca/product/{sku})"
                                await send_discord_notification(message, title="✅ BestBuy Stock Alert!", color=5814783)
                    else:
                        print(f"⚠️ API #{api_index} - Unexpected response format: {json.dumps(data)[:200]}...")
                    
                    return data
                except Exception as e:
                    print(f"❌ API #{api_index} - Error parsing JSON: {e}")
                    response_text = await response.text()
                    print(f"❌ API #{api_index} - Raw response: {response_text[:500]}...")
                    return None
            else:
                print(f"❌ API #{api_index} - Error response: {response.status}")
                response_text = await response.text()
                print(f"❌ API #{api_index} - Error details: {response_text[:500]}...")
                return None
                
    except asyncio.TimeoutError:
        print(f"⏱️ API #{api_index} - Request timed out after 30 seconds")
        return None
    except Exception as e:
        print(f"❌ API #{api_index} - Error fetching {api_url}: {e}")
        return None

async def monitor_bestbuy_apis(api_urls):
    # Create a TCP connector with proxy support
    connector = aiohttp.TCPConnector(ssl=False)
    
    # Create a session with the connector
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"🚀 Starting monitoring of {len(api_urls)} BestBuy API endpoints")
        
        while True:
            try:
                # Create tasks for each API URL
                tasks = []
                for i, url in enumerate(api_urls):
                    task = asyncio.create_task(check_bestbuy_availability(session, url, i+1))
                    tasks.append(task)
                
                # Run all tasks concurrently
                await asyncio.gather(*tasks)
                
                # Random delay between checks
                delay = random.uniform(0.1, 0.2)
                print(f"\n⏱️ Next check in {delay:.2f} seconds...\n")
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                # Short delay before retrying
                await asyncio.sleep(1)


if __name__ == "__main__":
    API_URLS = [
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.simpleproduct.v1%2Bjson&accept-language=en-CA&locations=172%7C936%7C246&postalCode=N5P&skus=18934175%7C19190987",
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.simpleproduct.v1%2Bjson&accept-language=en-CA&locations=223%7C925%7C959&postalCode=L1X&skus=18938753%7C18938754",
        "https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.simpleproduct.v1%2Bjson&accept-language=en-CA&locations=613%7C965%7C180&postalCode=N2L&skus=18938756%7C18938758"
    ]
    
    try:
        print("📊 Script will save complete output when terminated")
        asyncio.run(monitor_bestbuy_apis(API_URLS))
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        print("\n💾 Saving final output before exit...")

