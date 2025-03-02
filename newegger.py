import os
from seleniumbase import sb_cdp
import time
import random
import requests
import sys
import datetime
import threading
import json

# Import configuration settings
from scraperconfig import *

# Global variable to track if the status update thread should continue running
status_update_running = True
# Global variable to store the start time
start_time = datetime.datetime.now()
# Global variable to track refresh count
refresh_count = 0

# Create a unique log filename with timestamp
log_filename = os.path.join(LOG_DIRECTORY, f"newegg_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Create a custom stdout class to capture terminal output
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log_file = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()  # Ensure output is written immediately
        
    def flush(self):
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

def send_status_update():
    """
    Send a status update to Discord with the elapsed runtime and refresh count.
    """
    global refresh_count
    elapsed_time = format_time_elapsed(start_time)
    message = f"🕒 **Status Update**\n\n• Monitoring has been running for {elapsed_time}\n• Page refreshed {refresh_count} times\n\n🔗 URL: {url if 'url' in globals() else 'Unknown'}"
    
    # Only send Discord notification if enabled
    if ENABLE_DISCORD_STATUS_UPDATES:
        send_discord_notification(message, title="Newegg Monitor Status", color=3447003)  # Blue color
    
    print(f"\n📊 Status update: Running for {elapsed_time}, refreshed {refresh_count} times")

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
                "title": title if title else "Newegg Monitor Notification",
                "description": message,
                "color": color,
                "footer": {
                    "text": f"Newegg Monitor • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
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

def scrape_newegg(url):
    """
    Scrapes product information from a Newegg URL.
    
    Args:
        url (str): The Newegg URL to scrape
        
    Returns:
        list: List of product dictionaries containing name, price, and stock status
    """
    # Start a new browser instance
    sb = sb_cdp.Chrome(url)
    
    # Load cookies if available
    if os.path.exists(COOKIE_FILE):
        print(f"🍪 Loading cookies from {COOKIE_FILE}")
        sb.load_cookies(COOKIE_FILE)
        sb.open(url)  # Reload the page with cookies
        print("✅ Cookies loaded successfully")
    else:
        print(f"⚠️ Cookie file not found at {COOKIE_FILE}")

    # Wait for page load
    print(f"⏳ Waiting {PAGE_LOAD_WAIT} seconds for page to load...")
    sb.sleep(PAGE_LOAD_WAIT)

    # Select product names and prices
    print("Finding product names and prices...")
    names = sb.select_all('.item-cell .item-title')
    prices = sb.select_all('.item-cell .price-current')
    
    # Try to find buttons, but handle the case where they don't exist
    print("Looking for Add to Cart buttons...")
    try:
        all_buttons = sb.select_all('.item-cell .item-button-area button')
        print(f"Found {len(all_buttons)} buttons")
        buttons_found = True
    except Exception as e:
        print(f"No buttons found with primary selector: {e}")
        all_buttons = []
        buttons_found = False

    # Process stock status by analyzing button text
    stock_statuses = []
    in_stock_indices = []  # Track indices of in-stock items
    in_stock_buttons = []  # Store the actual buttons for in-stock items

    if buttons_found and all_buttons:
        for i, button in enumerate(all_buttons):
            try:
                button_text = button.text.strip().lower()
                if "add to cart" in button_text:
                    stock_statuses.append(("✅", "IN STOCK"))  # Add to Cart → IN STOCK
                    in_stock_indices.append(i)  # Track this index as in-stock
                    in_stock_buttons.append(button)  # Store the button for later use
                elif "auto notify" in button_text:
                    stock_statuses.append(("❌", "OUT OF STOCK"))  # Auto Notify → OUT OF STOCK
                else:
                    stock_statuses.append(("❌", "OUT OF STOCK"))  # Unknown button → OUT OF STOCK
            except:
                stock_statuses.append(("❌", "OUT OF STOCK"))  # Error with button → OUT OF STOCK
    
    # Compile results into a list of product dictionaries
    products = []
    if names and prices:
        for i, (name, price) in enumerate(zip(names, prices)):
            # Skip combo products if SHOW_COMBO_PRODUCTS is False
            product_name = name.text
            if not SHOW_COMBO_PRODUCTS and "Combo" in product_name:
                continue
                
            # If we have a stock status for this index, use it; otherwise, mark as OUT OF STOCK
            icon, stock_text = stock_statuses[i] if i < len(stock_statuses) else ("❌", "OUT OF STOCK")
            products.append({
                "name": product_name,
                "price": price.text,
                "stock_status": stock_text,
                "stock_icon": icon
            })

    # Check if any in-stock items were found
    if in_stock_indices and in_stock_buttons:
        print(f"\n🎯 IN-STOCK ITEMS FOUND! Found {len(in_stock_indices)} items in stock. ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create a list of in-stock items with their details
        in_stock_items = []
        for i, idx in enumerate(in_stock_indices):
            if idx < len(names) and idx < len(prices):
                product_name = names[idx].text.strip()
                product_price_text = prices[idx].text.strip()
                
                # Extract numeric price value (remove currency symbols, commas, etc.)
                # Example: "$129.99" -> 129.99
                try:
                    # Remove currency symbols, commas, and other non-numeric characters except decimal point
                    numeric_price = ''.join(c for c in product_price_text if c.isdigit() or c == '.')
                    if numeric_price:
                        price_value = float(numeric_price)
                    else:
                        price_value = float('inf')  # If we can't parse the price, set it to infinity
                except ValueError:
                    price_value = float('inf')  # If conversion fails, set to infinity
                
                # Skip combo products if SHOW_COMBO_PRODUCTS is False
                if not SHOW_COMBO_PRODUCTS and "Combo" in product_name:
                    continue
                
                in_stock_items.append({
                    'index': i,  # Index in the in_stock_indices/in_stock_buttons lists
                    'product_idx': idx,  # Original index in the product lists
                    'name': product_name,
                    'price_text': product_price_text,
                    'price_value': price_value
                })
        
        # Sort items by price (lowest first)
        in_stock_items.sort(key=lambda x: x['price_value'])
        
        # Display all in-stock items with their prices
        print("\nAvailable in-stock items (sorted by price):")
        for i, item in enumerate(in_stock_items):
            print(f"{i+1}. {item['name']} - {item['price_text']}")
        
        # Automatically select the lowest-priced item
        if in_stock_items:
            lowest_price_item = in_stock_items[0]
            print(f"\n🔍 Automatically selecting lowest-priced item: {lowest_price_item['name']} - {lowest_price_item['price_text']}")
            
            # Get the corresponding button and product index
            selection_idx = lowest_price_item['index']
            idx = in_stock_indices[selection_idx]
            button = in_stock_buttons[selection_idx]
            
            # Log the information with timestamp
            print(f"\n{'=' * 80}")
            print(f"🛒 ATTEMPTING TO ADD TO CART: {lowest_price_item['name']}")
            print(f"💰 Price: {lowest_price_item['price_text']}")
            print(f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 80}")
            
            try:
                # Click the Add to Cart button
                print(f"👆 Clicking 'Add to Cart' button...")
                button.click()
                
                # Wait for cart to update
                print("⏳ Waiting for cart to update...")
                sb.sleep(2)
                
                # Log success with timestamp
                print(f"✅ ITEM ADDED TO CART SUCCESSFULLY: {lowest_price_item['name']} ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Send Discord notification
                notification_message = f"🛒 **Item added to cart!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n🔗 **Cart URL:** https://secure.newegg.ca/shop/cart"
                if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                    send_discord_notification(notification_message, title="🎯 Newegg Item In Stock!")
                
                # Navigate to cart page with timestamp
                print(f"\n🛒 Navigating to cart page... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                sb.open("https://secure.newegg.ca/shop/cart")
                sb.sleep(2)  # Wait for cart page to load
                
                # Try to click the Secure Checkout button
                try:
                    print(f"✅ Found Secure Checkout button, clicking... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    # Try to find the button using the provided selector
                    checkout_button = sb.find_element('button.btn.btn-primary.btn-wide:contains("Secure Checkout")')
                    
                    if checkout_button:
                        print("✅ Found Secure Checkout button, clicking...")
                        checkout_button.click()
                        sb.sleep(2)  # Wait for checkout page to load
                        
                        # Check if sign-in form appears after clicking Secure Checkout
                        print("🔍 Checking if sign-in form appears...")
                        try:
                            password_field = sb.find_element('input#labeled-input-password[name="password"]', timeout=2)
                            if password_field:
                                print("🔑 Sign-in form detected, entering credentials...")
                                password_field.send_keys(NEWEGG_PASSWORD)
                                
                                # Find and click the sign-in button
                                sign_in_button = sb.find_element('button#signInSubmit[name="signIn"]')
                                if sign_in_button:
                                    print("👆 Clicking 'SIGN IN' button...")
                                    sign_in_button.click()
                                    
                                    # Wait for sign-in to complete
                                    print("⏳ Waiting for sign-in to complete...")
                                    sb.sleep(2)
                                    print("✅ Sign-in completed")
                        except Exception as e:
                            print(f"ℹ️ No sign-in form detected, continuing with checkout: {e}")
                        
                        # Look for CVV field
                        print("🔍 Looking for CVV field...")
                        try:
                            cvv_field = sb.find_element('input[name="cvvNumber"]')
                            if cvv_field:
                                print("✅ Found CVV field, entering value...")
                                cvv_field.send_keys(NEWEGG_CVV)
                                print("💳 CVV entered successfully!")

                                # Look for and click the Place Order button
                                try:
                                    print("🔍 Looking for Place Order button...")
                                    place_order_button = sb.find_element('button#btnCreditCard.button.button-m.bg-orange')
                                    
                                    if place_order_button:
                                        print(f"✅ Found Place Order button, clicking... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                                        if PLACE_ORDER:
                                            place_order_button.click()
                                            print("🛒 Order placed!")
                                        else:
                                            print("⚠️ Order placement disabled - skipping final click")
                                        
                                        # Wait before taking screenshot
                                        print("⏳ Waiting for confirmation page...")
                                        sb.sleep(2)
                                        
                                        # Take a screenshot
                                        screenshot_path = f"order_confirmation_{time.strftime('%Y%m%d_%H%M%S')}.png"
                                        sb.save_screenshot(screenshot_path)
                                        print(f"📸 Screenshot saved to: {screenshot_path}")
                                        
                                        # Send Discord notification with order confirmation
                                        confirmation_message = f"🎉 **ORDER PLACED SUCCESSFULLY!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n💳 Payment processed!"
                                        if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                                            send_discord_notification(confirmation_message, title="✅ Newegg Order Confirmed!")
                                    else:
                                        print("❌ Place Order button not found")
                                except Exception as e:
                                    print(f"❌ Error during order placement: {e}")
                        except:
                            print("❌ CVV field not found or not accessible yet")
                    else:
                        print("❌ Secure Checkout button not found")
                except Exception as e:
                    print(f"❌ Error during checkout process: {e}")
                
                # Pause for user to take action
                print("\n⏸️ Checkout initiated. Press Enter to continue...")
                input()
                
                # After user continues, go back to the product page
                sb.open(url)
                
            except Exception as e:
                print(f"❌ Error clicking Add to Cart button: {e}")
                # If there was an error, refresh the page
                sb.open(url)
    else:
        if not products:
            print("No products found.")
        else:
            print("No in-stock items found.")
    
    # Try to close the browser
    try:
        sb.driver.quit()
        print("Browser closed.")
    except:
        pass
    
    return products

def refresh_session(sb):
    """
    Refreshes the Newegg session by visiting the orders page to prevent CAPTCHA challenges.
    
    Args:
        sb: The SeleniumBase browser instance
    """
    print(f"\n{'=' * 80}")
    print(f"🔄 REFRESHING SESSION to prevent CAPTCHA... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")
    
    try:
        # Navigate to the orders page
        print(f"📄 Navigating to orders page: {ORDERS_PAGE_URL}")
        sb.open(ORDERS_PAGE_URL)
        sb.sleep(2)  # Wait for page to load
        
        # Check if sign-in form appears
        print("🔍 Checking if sign-in form appears...")
        try:
            password_field = sb.find_element('input#labeled-input-password[name="password"]', timeout=2)
            if password_field:
                print("🔑 Sign-in form detected, entering credentials...")
                password_field.send_keys(NEWEGG_PASSWORD)
                
                # Find and click the sign-in button
                sign_in_button = sb.find_element('button#signInSubmit[name="signIn"]')
                if sign_in_button:
                    print("👆 Clicking 'SIGN IN' button...")
                    sign_in_button.click()
                    
                    # Wait for sign-in to complete
                    print("⏳ Waiting for sign-in to complete...")
                    sb.sleep(2)
                    print("✅ Sign-in completed")
        except Exception as e:
            print(f"ℹ️ No sign-in form detected: {e}")
        
        print("✅ Session refreshed successfully")
        
    except Exception as e:
        print(f"❌ Error refreshing session: {e}")
    
    print(f"{'=' * 80}")

# Add a simple main function to run the script directly
if __name__ == "__main__":
    import sys
    
    try:
        # Get URL from command line argument or use default from constants
        url = sys.argv[1] if len(sys.argv) > 1 else SEARCH_PAGE_URL
        
        print(f"Starting continuous monitoring of: {url}")
        
        # Start the status update thread
        status_thread = threading.Thread(target=status_update_thread, daemon=True)
        status_thread.start()
        
        # Start a new browser instance
        sb = sb_cdp.Chrome(url)
        
        # Load cookies if available
        if os.path.exists(COOKIE_FILE):
            print(f"🍪 Loading cookies from {COOKIE_FILE}")
            sb.load_cookies(COOKIE_FILE)
            sb.open(url)  # Reload the page with cookies
            print("✅ Cookies loaded successfully")
        else:
            print(f"⚠️ Cookie file not found at {COOKIE_FILE}")
        
        # Initial session refresh
        print("🔄 Performing initial session refresh...")
        refresh_session(sb)
        
        # Return to the product page after initial session refresh
        print(f"🔄 Returning to product page after initial session refresh: {url}")
        sb.open(url)
        sb.sleep(1)
        
        # Track refresh count for session refresh
        refresh_count = 0
        # Calculate next refresh count (random between MIN and MAX)
        next_session_refresh_count = random.randint(MIN_REFRESH_COUNT, MAX_REFRESH_COUNT)
        print(f"⏰ Session will refresh after {next_session_refresh_count} page refreshes")
        
        # Continuous monitoring with random refresh interval
        try:
            while True:
                # Check if it's time to refresh the session based on refresh count
                if refresh_count >= next_session_refresh_count:
                    refresh_session(sb)
                    refresh_count = 0  # Reset the counter
                    next_session_refresh_count = random.randint(MIN_REFRESH_COUNT, MAX_REFRESH_COUNT)
                    print(f"⏰ Next session refresh after {next_session_refresh_count} page refreshes")
                    
                    # Return to the product page after refreshing session
                    print(f"🔄 Returning to product page: {url}")
                    sb.open(url)
                    sb.sleep(1)
                
                # Wait for page load
                print(f"⏳ Waiting {PAGE_LOAD_WAIT} seconds for page to load...")
                sb.sleep(PAGE_LOAD_WAIT)
                
                # Select product names and prices
                print("Finding product names and prices...")
                names = sb.select_all('.item-cell .item-title')
                prices = sb.select_all('.item-cell .price-current')
                
                # Try to find buttons, but handle the case where they don't exist
                print("Looking for Add to Cart buttons...")
                try:
                    all_buttons = sb.select_all('.item-cell .item-button-area button')
                    print(f"Found {len(all_buttons)} buttons")
                    buttons_found = True
                except Exception as e:
                    print(f"No buttons found with primary selector: {e}")
                    all_buttons = []
                    buttons_found = False
                
                # Process stock status by analyzing button text
                stock_statuses = []
                in_stock_indices = []  # Track indices of in-stock items
                in_stock_buttons = []  # Store the actual buttons for in-stock items
                
                if buttons_found and all_buttons:
                    for i, button in enumerate(all_buttons):
                        try:
                            button_text = button.text.strip().lower()
                            if "add to cart" in button_text:
                                stock_statuses.append(("✅", "IN STOCK"))  # Add to Cart → IN STOCK
                                in_stock_indices.append(i)  # Track this index as in-stock
                                in_stock_buttons.append(button)  # Store the button for later use
                            elif "auto notify" in button_text:
                                stock_statuses.append(("❌", "OUT OF STOCK"))  # Auto Notify → OUT OF STOCK
                            else:
                                stock_statuses.append(("❌", "OUT OF STOCK"))  # Unknown button → OUT OF STOCK
                        except:
                            stock_statuses.append(("❌", "OUT OF STOCK"))  # Error with button → OUT OF STOCK
                
                # Compile results into a list of product dictionaries
                products = []
                if names and prices:
                    for i, (name, price) in enumerate(zip(names, prices)):
                        # Get the product name
                        product_name = name.text
                        
                        # Skip combo products if SHOW_COMBO_PRODUCTS is False
                        if not SHOW_COMBO_PRODUCTS and "Combo" in product_name:
                            continue
                            
                        # If we have a stock status for this index, use it; otherwise, mark as OUT OF STOCK
                        icon, stock_text = stock_statuses[i] if i < len(stock_statuses) else ("❌", "OUT OF STOCK")
                        products.append({
                            "name": product_name,
                            "price": price.text,
                            "stock_status": stock_text,
                            "stock_icon": icon
                        })
                
                # Display the results
                if not products:
                    print("No products found.")
                else:
                    print(f"\nFound {len(products)} products:")
                    print("=" * 80)
                    
                    for i, product in enumerate(products, 1):
                        print(f"{i}. {product['stock_icon']} {product['name']}")
                        print(f"   Price: {product['price']}")
                        print(f"   Status: {product['stock_status']}")
                        print("-" * 80)
                
                # Check if any in-stock items were found
                if in_stock_indices and in_stock_buttons:
                    print(f"\n🎯 IN-STOCK ITEMS FOUND! Found {len(in_stock_indices)} items in stock. ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Create a list of in-stock items with their details
                    in_stock_items = []
                    for i, idx in enumerate(in_stock_indices):
                        if idx < len(names) and idx < len(prices):
                            product_name = names[idx].text.strip()
                            
                            # Skip combo products if SHOW_COMBO_PRODUCTS is False
                            if not SHOW_COMBO_PRODUCTS and "Combo" in product_name:
                                continue
                                
                            product_price_text = prices[idx].text.strip()
                            
                            # Extract numeric price value (remove currency symbols, commas, etc.)
                            try:
                                numeric_price = ''.join(c for c in product_price_text if c.isdigit() or c == '.')
                                if numeric_price:
                                    price_value = float(numeric_price)
                                else:
                                    price_value = float('inf')
                            except ValueError:
                                price_value = float('inf')
                            
                            in_stock_items.append({
                                'index': i,
                                'product_idx': idx,
                                'name': product_name,
                                'price_text': product_price_text,
                                'price_value': price_value
                            })
                    
                    # Sort items by price (lowest first)
                    in_stock_items.sort(key=lambda x: x['price_value'])
                    
                    # Display all in-stock items with their prices
                    print("\nAvailable in-stock items (sorted by price):")
                    for i, item in enumerate(in_stock_items):
                        print(f"{i+1}. {item['name']} - {item['price_text']}")
                    
                    # Automatically select the lowest-priced item
                    if in_stock_items:
                        lowest_price_item = in_stock_items[0]
                        print(f"\n🔍 Automatically selecting lowest-priced item: {lowest_price_item['name']} - {lowest_price_item['price_text']}")
                        
                        # Get the corresponding button and product index
                        selection_idx = lowest_price_item['index']
                        idx = in_stock_indices[selection_idx]
                        button = in_stock_buttons[selection_idx]
                        
                        # Log the information with timestamp
                        print(f"\n{'=' * 80}")
                        print(f"🛒 ATTEMPTING TO ADD TO CART: {lowest_price_item['name']}")
                        print(f"💰 Price: {lowest_price_item['price_text']}")
                        print(f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"{'=' * 80}")
                        
                        try:
                            # Click the Add to Cart button
                            print(f"👆 Clicking 'Add to Cart' button...")
                            button.click()
                            
                            # Wait for cart to update
                            print("⏳ Waiting for cart to update...")
                            sb.sleep(2)
                            
                            # Log success with timestamp
                            print(f"✅ ITEM ADDED TO CART SUCCESSFULLY: {lowest_price_item['name']} ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # Send Discord notification
                            notification_message = f"🛒 **Item added to cart!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n🔗 **Cart URL:** https://secure.newegg.ca/shop/cart"
                            if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                                send_discord_notification(notification_message, title="🎯 Newegg Item In Stock!")
                            
                            # Navigate to cart page with timestamp
                            print(f"\n🛒 Navigating to cart page... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                            sb.open("https://secure.newegg.ca/shop/cart")
                            sb.sleep(2)  # Wait for cart page to load
                            
                            # Try to click the Secure Checkout button
                            try:
                                print(f"✅ Found Secure Checkout button, clicking... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                                # Try to find the button using the provided selector
                                checkout_button = sb.find_element('button.btn.btn-primary.btn-wide:contains("Secure Checkout")')
                                
                                if checkout_button:
                                    print("✅ Found Secure Checkout button, clicking...")
                                    checkout_button.click()
                                    sb.sleep(2)  # Wait for checkout page to load
                                    
                                    # Check if sign-in form appears after clicking Secure Checkout
                                    print("🔍 Checking if sign-in form appears...")
                                    try:
                                        password_field = sb.find_element('input#labeled-input-password[name="password"]', timeout=2)
                                        if password_field:
                                            print("🔑 Sign-in form detected, entering credentials...")
                                            password_field.send_keys(NEWEGG_PASSWORD)
                                            
                                            # Find and click the sign-in button
                                            sign_in_button = sb.find_element('button#signInSubmit[name="signIn"]')
                                            if sign_in_button:
                                                print("👆 Clicking 'SIGN IN' button...")
                                                sign_in_button.click()
                                                
                                                # Wait for sign-in to complete
                                                print("⏳ Waiting for sign-in to complete...")
                                                sb.sleep(2)
                                                print("✅ Sign-in completed")
                                    except Exception as e:
                                        print(f"ℹ️ No sign-in form detected, continuing with checkout: {e}")
                                    
                                    # Look for CVV field
                                    print("🔍 Looking for CVV field...")
                                    try:
                                        cvv_field = sb.find_element('input[name="cvvNumber"]')
                                        if cvv_field:
                                            print("✅ Found CVV field, entering value...")
                                            cvv_field.send_keys(NEWEGG_CVV)
                                            print("💳 CVV entered successfully!")

                                            # Look for and click the Place Order button
                                            try:
                                                print("🔍 Looking for Place Order button...")
                                                place_order_button = sb.find_element('button#btnCreditCard.button.button-m.bg-orange')
                                                
                                                if place_order_button:
                                                    print(f"✅ Found Place Order button, clicking... ⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                                                    if PLACE_ORDER:
                                                        place_order_button.click()
                                                        print("🛒 Order placed!")
                                                    else:
                                                        print("⚠️ Order placement disabled - skipping final click")
                                                    
                                                    # Wait before taking screenshot
                                                    print("⏳ Waiting for confirmation page...")
                                                    sb.sleep(2)
                                                    
                                                    # Take a screenshot
                                                    screenshot_path = f"order_confirmation_{time.strftime('%Y%m%d_%H%M%S')}.png"
                                                    sb.save_screenshot(screenshot_path)
                                                    print(f"📸 Screenshot saved to: {screenshot_path}")
                                                    
                                                    # Send Discord notification with order confirmation
                                                    confirmation_message = f"🎉 **ORDER PLACED SUCCESSFULLY!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n💳 Payment processed!"
                                                    if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                                                        send_discord_notification(confirmation_message, title="✅ Newegg Order Confirmed!")
                                                    else:
                                                        print("❌ Payment processing disabled")
                                                else:
                                                    print("❌ Place Order button not found")
                                            except Exception as e:
                                                print(f"❌ Error during order placement: {e}")
                                    except:
                                        print("❌ CVV field not found or not accessible yet")
                                else:
                                    print("❌ Secure Checkout button not found")

                            except Exception as e:
                                print(f"❌ Error during checkout process: {e}")
                            
                            # Pause for user to take action
                            print("\n⏸️ Checkout initiated. Press Enter to continue...")
                            input()
                            
                            # After user continues, go back to the product page
                            sb.open(url)
                            
                        except Exception as e:
                            print(f"❌ Error clicking Add to Cart button: {e}")
                            # If there was an error, refresh the page
                            sb.open(url)
                
                # Random refresh interval between MIN_RANDOM_REFRESH and MAX_RANDOM_REFRESH seconds
                refresh_time = random.uniform(MIN_RANDOM_REFRESH, MAX_RANDOM_REFRESH)
                print(f"\n⏱️  Refreshing in {refresh_time:.2f} seconds...")
                time.sleep(refresh_time)
                print("\n" + "=" * 80)
                print(f"🔄 Refreshing page: {url}")
                print("=" * 80 + "\n")
                
                # Increment refresh counter
                refresh_count += 1
                print(f"📊 Refreshes until next CAPTCHA check: {refresh_count}/{next_session_refresh_count}")
                
                # Refresh the page instead of creating a new browser instance
                sb.open(url)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user.")
            # Close the browser when done
            try:
                sb.driver.quit()
                print("Browser closed.")
            except:
                pass
    
    except Exception as e:
        print(f"\n❌ Unhandled exception: {e}")
    
    finally:
        # Stop the status update thread
        status_update_running = False
        
        # Send final status update
        elapsed_time = format_time_elapsed(start_time)
        final_message = f"🛑 **Monitoring Ended**\n\n• Total runtime: {elapsed_time}\n• Pages refreshed: {refresh_count}\n\n🔗 URL: {url if 'url' in globals() else 'Unknown'}"
        if ENABLE_DISCORD_STATUS_UPDATES:
            send_discord_notification(final_message, title="Newegg Monitor Stopped", color=15158332)  # Red color
        print(f"\n📊 Final status: Total runtime {elapsed_time}, refreshed {refresh_count} times")
        
        # Log termination time
        print(f"\n🔄 Logging ended at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Log saved to: {log_filename}")
        
        # Restore original stdout and close log file
        if isinstance(sys.stdout, Logger):
            sys.stdout.log_file.close()
            sys.stdout = sys.stdout.terminal 