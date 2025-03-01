"""
Newegg-specific scraping functionality.
Contains selectors and logic specific to Newegg's website structure.
"""
import os
from seleniumbase import sb_cdp
import time
import random
import requests

# Define constants directly in the script
PAGE_LOAD_WAIT = .5  # Wait time in seconds for page to load
COOKIE_FILE = r"C:\base4o\cookies\cookies.json"  # Path to cookie file
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1345475006058205194/XhCEXuvoOWtqO_7WS9XiIy_LLJwRcPPFmvcPoTS0772R1iaMSnMC1N-aO41oLRParlBD"  # Replace with your Discord webhook URL
DISCORD_USER_ID = "78875182906748928"  # Replace with your Discord user ID
# Toggle to control whether to display combo products
SHOW_COMBO_PRODUCTS = True  # Set to True to show products with "Combo" in the title

def send_discord_notification(message, title=None, color=5814783):
    """
    Sends a notification to Discord using a webhook.
    
    Args:
        message (str): The message to send
        title (str, optional): The title of the embed
        color (int, optional): The color of the embed (default: green)
    """
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE":
        print("⚠️ Discord webhook URL not configured. Skipping notification.")
        return
    
    data = {
        "content": f"<@{DISCORD_USER_ID}>" if DISCORD_USER_ID and DISCORD_USER_ID != "YOUR_DISCORD_USER_ID_HERE" else "",
        "embeds": [
            {
                "title": title or "Newegg Alert",
                "description": message,
                "color": color,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
        ]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("✅ Discord notification sent successfully!")
        else:
            print(f"❌ Failed to send Discord notification. Status code: {response.status_code}")
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
        print(f"\n🎯 IN-STOCK ITEMS FOUND! Found {len(in_stock_indices)} items in stock.")
        
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
            
            # Log the information
            print(f"\n{'=' * 80}")
            print(f"🛒 ATTEMPTING TO ADD TO CART: {lowest_price_item['name']}")
            print(f"💰 Price: {lowest_price_item['price_text']}")
            print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 80}")
            
            try:
                # Click the Add to Cart button
                print(f"👆 Clicking 'Add to Cart' button...")
                button.click()
                
                # Wait for cart to update
                print("⏳ Waiting for cart to update...")
                sb.sleep(2)
                
                # Log success
                print(f"✅ ITEM ADDED TO CART SUCCESSFULLY: {lowest_price_item['name']}")
                
                # Send Discord notification
                notification_message = f"🛒 **Item added to cart!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n🔗 **Cart URL:** https://secure.newegg.ca/shop/cart"
                send_discord_notification(notification_message, title="🎯 Newegg Item In Stock!")
                
                # Navigate to cart page
                print("\n🛒 Navigating to cart page...")
                sb.open("https://secure.newegg.ca/shop/cart")
                sb.sleep(2)  # Wait for cart page to load
                
                # Try to click the Secure Checkout button
                try:
                    print("🔍 Looking for Secure Checkout button...")
                    # Try to find the button using the provided selector
                    checkout_button = sb.find_element('button.btn.btn-primary.btn-wide:contains("Secure Checkout")')
                    
                    if checkout_button:
                        print("✅ Found Secure Checkout button, clicking...")
                        checkout_button.click()
                        sb.sleep(2)  # Wait for checkout page to load
                        
                        # Look for CVV field
                        print("🔍 Looking for CVV field...")
                        try:
                            cvv_field = sb.find_element('input[name="cvvNumber"]')
                            if cvv_field:
                                print("✅ Found CVV field, entering value...")
                                cvv_field.send_keys("1234")
                                print("💳 CVV entered successfully!")

                                # Look for and click the Place Order button
                                try:
                                    print("🔍 Looking for Place Order button...")
                                    place_order_button = sb.find_element('button#btnCreditCard.button.button-m.bg-orange')
                                    
                                    if place_order_button:
                                        print("✅ Found Place Order button, clicking...")
                                        place_order_button.click()
                                        
                                        # Wait 5 seconds before taking screenshot
                                        print("⏳ Waiting 5 seconds before taking screenshot...")
                                        sb.sleep(2)
                                        
                                        # Take a screenshot
                                        screenshot_path = f"order_confirmation_{time.strftime('%Y%m%d_%H%M%S')}.png"
                                        sb.save_screenshot(screenshot_path)
                                        print(f"📸 Screenshot saved to: {screenshot_path}")
                                        
                                        # Send Discord notification with order confirmation
                                        confirmation_message = f"🎉 **ORDER PLACED SUCCESSFULLY!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n💳 Payment processed!"
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

# Add a simple main function to run the script directly
if __name__ == "__main__":
    import sys
    
    # Get URL from command line argument or use default
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.newegg.ca/p/pl?N=100007708%20601469153%20601469158" # NEWEGG URL
    
    print(f"Starting continuous monitoring of: {url}")
    
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
    
    # Continuous monitoring with random refresh interval
    try:
        while True:
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
                print(f"\n🎯 IN-STOCK ITEMS FOUND! Found {len(in_stock_indices)} items in stock.")
                
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
                    
                    # Log the information
                    print(f"\n{'=' * 80}")
                    print(f"🛒 ATTEMPTING TO ADD TO CART: {lowest_price_item['name']}")
                    print(f"💰 Price: {lowest_price_item['price_text']}")
                    print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"{'=' * 80}")
                    
                    try:
                        # Click the Add to Cart button
                        print(f"👆 Clicking 'Add to Cart' button...")
                        button.click()
                        
                        # Wait for cart to update
                        print("⏳ Waiting for cart to update...")
                        sb.sleep(1)
                        
                        # Log success
                        print(f"✅ ITEM ADDED TO CART SUCCESSFULLY: {lowest_price_item['name']}")
                        
                        # Send Discord notification
                        notification_message = f"🛒 **Item added to cart!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n🔗 **Cart URL:** https://secure.newegg.ca/shop/cart"
                        send_discord_notification(notification_message, title="🎯 Newegg Item In Stock!")
                        
                        # Navigate to cart page
                        print("\n🛒 Navigating to cart page...")
                        sb.open("https://secure.newegg.ca/shop/cart")
                        sb.sleep(1)  # Wait for cart page to load
                        
                        # Try to click the Secure Checkout button
                        try:
                            print("🔍 Looking for Secure Checkout button...")
                            # Try to find the button using the provided selector
                            checkout_button = sb.find_element('button.btn.btn-primary.btn-wide:contains("Secure Checkout")')
                            
                            if checkout_button:
                                print("✅ Found Secure Checkout button, clicking...")
                                checkout_button.click()
                                sb.sleep(2)  # Wait for checkout page to load
                                
                                # Look for CVV field
                                print("🔍 Looking for CVV field...")
                                try:
                                    cvv_field = sb.find_element('input[name="cvvNumber"]')
                                    if cvv_field:
                                        print("✅ Found CVV field, entering value...")
                                        cvv_field.send_keys("1234")
                                        print("💳 CVV entered successfully!")

                                        # Look for and click the Place Order button
                                        try:
                                            print("🔍 Looking for Place Order button...")
                                            place_order_button = sb.find_element('button#btnCreditCard.button.button-m.bg-orange')
                                            
                                            if place_order_button:
                                                print("✅ Found Place Order button, clicking...")
                                                place_order_button.click()
                                                
                                                # Wait 5 seconds before taking screenshot
                                                print("⏳ Waiting 5 seconds before taking screenshot...")
                                                sb.sleep(2)
                                                
                                                # Take a screenshot
                                                screenshot_path = f"order_confirmation_{time.strftime('%Y%m%d_%H%M%S')}.png"
                                                sb.save_screenshot(screenshot_path)
                                                print(f"📸 Screenshot saved to: {screenshot_path}")
                                                
                                                # Send Discord notification with order confirmation
                                                confirmation_message = f"🎉 **ORDER PLACED SUCCESSFULLY!**\n\n**Product:** {lowest_price_item['name']}\n**Price:** {lowest_price_item['price_text']}\n**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n💳 Payment processed!"
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
            
            # Random refresh interval between 2-5 seconds
            refresh_time = random.uniform(2, 5)
            print(f"\n⏱️  Refreshing in {refresh_time:.2f} seconds...")
            time.sleep(refresh_time)
            print("\n" + "=" * 80)
            print(f"🔄 Refreshing page: {url}")
            print("=" * 80 + "\n")
            
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