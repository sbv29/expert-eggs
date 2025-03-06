"""
Basic BestBuy scraper to extract product names from a search page.
"""
import time
import os
import random
from seleniumbase import sb_cdp
import sys
import datetime
import json
import requests

# Import configuration settings
from scraperconfig import (
    COOKIE_FILE, BESTBUY_PAGE_LOAD_WAIT, BESTBUY_MIN_RANDOM_REFRESH, BESTBUY_MAX_RANDOM_REFRESH,
    BESTBUY_MIN_REFRESH_COUNT, BESTBUY_MAX_REFRESH_COUNT, BESTBUY_ORDERS_PAGE_URL, 
    BESTBUY_PASSWORD, BESTBUY_CVV, BESTBUY_BASE_URL, BESTBUY_CART_URL, BESTBUY_SEARCH_URL,
    HEADLESS_MODE, DISCORD_WEBHOOK_URL, DISCORD_USER_ID, ENABLE_DISCORD_STOCK_NOTIFICATIONS,
    BESTBUY_ATC, BESTBUY_PLACE_ORDER
)

def get_timestamp():
    """Return a formatted timestamp string."""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def capture_screenshot(sb, prefix="screenshot"):
    """
    Captures a screenshot of the current browser window.
    
    Args:
        sb: SeleniumBase instance
        prefix (str): Prefix for the screenshot filename
        
    Returns:
        str: Path to the saved screenshot file
    """
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    screenshot_path = f"{prefix}_{timestamp}.png"
    try:
        # Take the screenshot - use the standard method without full_page parameter
        # as it might not be supported in this version of SeleniumBase
        sb.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved to: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"❌ Error capturing screenshot: {e}")
        return None

def send_discord_notification_with_file(message, file_path=None, title=None, color=5814783):
    """
    Sends a notification to Discord using a webhook with an optional file attachment.
    
    Args:
        message (str): The message to send
        file_path (str, optional): Path to a file to attach
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
                "title": title if title else "BestBuy Monitor Notification",
                "description": message,
                "color": color,
                "footer": {
                    "text": f"BestBuy Monitor • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
        ]
    }
    
    try:
        if file_path and os.path.exists(file_path):
            # Send with file attachment
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, 'image/png'),
                    'payload_json': (None, json.dumps(payload))
                }
                response = requests.post(DISCORD_WEBHOOK_URL, files=files)
        else:
            # Send without file attachment
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
        
        response.raise_for_status()
        print(f"✅ Discord notification sent successfully")
    except Exception as e:
        print(f"❌ Error sending Discord notification: {e}")

def refresh_session(sb):
    """
    Refresh the session by navigating to the orders page and signing in if needed.
    This helps prevent CAPTCHA and session timeouts.
    
    Args:
        sb: The SeleniumBase instance
    """
    print("\n" + "=" * 80)
    print(f"🔄 REFRESHING SESSION to prevent CAPTCHA... ⏰ Time: {get_timestamp()}")
    print("=" * 80)
    
    # Navigate to orders page
    print(f"📄 Navigating to orders page: {BESTBUY_ORDERS_PAGE_URL}")
    sb.open(BESTBUY_ORDERS_PAGE_URL)
    sb.sleep(2)  # Wait for page to load
    
    # Check if sign-in form appears - use a more general selector
    print("🔍 Checking if sign-in form appears...")
    try:
        # Try different selectors for the password field
        password_field = None
        selectors = [
            'input[data-automation="sign-in-password"]',
            'input#password[name="password"]',
            'input[type="password"]'
        ]
        
        for selector in selectors:
            try:
                password_field = sb.find_element(selector, timeout=1)
                if password_field:
                    print(f"✅ Found password field with selector: {selector}")
                    break
            except:
                continue
        
        if password_field:
            print("🔑 Sign-in form detected, entering credentials...")
            password_field.send_keys(BESTBUY_PASSWORD)
            
            # Find and click the sign-in button - try different selectors
            sign_in_button = None
            button_selectors = [
                'button[data-automation="sign-in-button"]',
                'button.signin-form-button_CqjFT',
                'button:contains("Sign In")',
                'button[type="submit"]'
            ]
            
            for selector in button_selectors:
                try:
                    sign_in_button = sb.find_element(selector, timeout=1)
                    if sign_in_button:
                        print(f"✅ Found sign-in button with selector: {selector}")
                        break
                except:
                    continue
            
            if sign_in_button:
                print("👆 Clicking 'Sign In' button...")
                sign_in_button.click()
                # Wait for sign-in to complete
                print("⏳ Waiting for sign-in to complete...")
                sb.sleep(2)
                print("✅ Sign-in completed")
            else:
                print("❌ Sign-in button not found")
        else:
            print("ℹ️ No password field found, may already be signed in")
    except Exception as e:
        print(f"ℹ️ No sign-in form detected or error: {e}")
    
    print("✅ Session refreshed successfully")

def scrape_bestbuy():
    """
    Basic function to scrape product names from BestBuy search page.
    """
    # Set up Chrome options to bypass bot detection
    chrome_options = {
        "disable_blink_features": "AutomationControlled",
        "enable_undetected": True,
    }
    
    # Start a new browser instance with undetected mode
    print(f"Opening browser and navigating to {BESTBUY_SEARCH_URL}")
    sb = sb_cdp.Chrome()
    
    # Load cookies if available
    if os.path.exists(COOKIE_FILE):
        print(f"🍪 Loading cookies from {COOKIE_FILE}")
        sb.load_cookies(COOKIE_FILE)
        print("✅ Cookies loaded successfully")
    else:
        print(f"⚠️ Cookie file not found at {COOKIE_FILE}")
    
    # Navigate to the search page first
    print(f"Navigating to search page: {BESTBUY_SEARCH_URL}")
    sb.open(BESTBUY_SEARCH_URL)
    
    # Add a 3-second pause to allow the search page to load completely
    print("⏳ Pausing for 3 seconds to allow search page to load completely...")
    sb.sleep(3)
    print("✅ Initial page load complete")
    
    # Initial session refresh
    print("🔄 Performing initial session refresh...")
    refresh_session(sb)
    
    # Navigate to the URL after loading cookies with retry mechanism
    print(f"Navigating back to {BESTBUY_SEARCH_URL}")
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            sb.open(BESTBUY_SEARCH_URL)
            print("✅ Page loaded successfully")
            break  # Exit the retry loop if successful
        except Exception as e:
            retry_count += 1
            print(f"❌ Error loading page (Attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                # Start with 5 seconds and add 5 more seconds with each retry
                timeout = 5 + (retry_count * 5)
                print(f"Trying again with a longer timeout ({timeout} seconds)...")
                try:
                    sb.driver.set_page_load_timeout(timeout)
                    continue  # Try again in the next iteration
                except Exception as e2:
                    print(f"❌ Error setting timeout: {e2}")
            else:
                print("⚠️ Maximum retries reached. Trying alternative approach...")
                try:
                    # Try a different approach - navigate to BestBuy homepage first
                    sb.open(BESTBUY_BASE_URL)
                    time.sleep(3)
                    print("✅ Homepage loaded, now navigating to search URL")
                    sb.open(BESTBUY_SEARCH_URL)
                    print("✅ Search page loaded successfully")
                except Exception as e3:
                    print(f"❌ All attempts to load page failed: {e3}")
                    print("Please check your internet connection or if BestBuy is blocking automated access")
                    sb.driver.quit()
                    return
    
    # Continuous monitoring loop
    refresh_count = 0
    # Calculate next refresh count (random between MIN and MAX)
    next_session_refresh_count = random.randint(BESTBUY_MIN_REFRESH_COUNT, BESTBUY_MAX_REFRESH_COUNT)
    print(f"⏰ Session will refresh after {next_session_refresh_count} page refreshes")
    
    try:
        while True:
            refresh_count += 1
            scan_start_time = get_timestamp()
            print(f"\n===== Refresh #{refresh_count} | Started: {scan_start_time} =====")
            
            # Check if we need to refresh the session
            if refresh_count >= next_session_refresh_count:
                refresh_session(sb)
                refresh_count = 0
                next_session_refresh_count = random.randint(BESTBUY_MIN_REFRESH_COUNT, BESTBUY_MAX_REFRESH_COUNT)
                print(f"⏰ Session will refresh after {next_session_refresh_count} page refreshes")
                # Return to the product page after session refresh
                print(f"🔄 Returning to product page after session refresh: {BESTBUY_SEARCH_URL}")
                sb.open(BESTBUY_SEARCH_URL)
                sb.sleep(1)
            
            # Wait for page to load
            print(f"⏳ Waiting {BESTBUY_PAGE_LOAD_WAIT} seconds for page to load...")
            sb.sleep(BESTBUY_PAGE_LOAD_WAIT)
            
            # Check if page loaded correctly
            try:
                # Check if we can find any product elements
                product_check = sb.select_all("h3.productItemName_3IZ3c", timeout=5)
                if not product_check:
                    print("⚠️ No product elements found. Page may not have loaded correctly.")
                    print("Reloading page...")
                    sb.open(BESTBUY_SEARCH_URL)
                    sb.sleep(3)  # Wait a bit longer for reload
                    continue
            except Exception as e:
                print(f"⚠️ Error checking page content: {e}")
                print("Reloading page...")
                sb.open(BESTBUY_SEARCH_URL)
                sb.sleep(3)
                continue
            
            # Click "Show more" button if it exists to load all products
            show_more_selector = "button[aria-label='Show more products']"
            try:
                # Keep clicking "Show more" until no more buttons are found
                while True:
                    show_more_buttons = sb.select_all(show_more_selector)
                    if not show_more_buttons or len(show_more_buttons) == 0:
                        print("No more 'Show more' buttons found.")
                        break
                    
                    print("🖱️ Clicking 'Show more' button to load additional products...")
                    show_more_buttons[0].click()
                    # Wait for new products to load
                    sb.sleep(2)
            except Exception as e:
                print(f"Note: Could not find or click 'Show more' button: {e}")
            
            # Select product names, prices, and URLs
            print("Finding product information...")
            product_name_selector = "h3.productItemName_3IZ3c"
            product_price_selector = "div.style-module_price__ql4Q1"
            product_availability_selector = "div.availabilityMessageSearch_1KfqF"
            product_link_selector = "a.link_3hcyN[itemprop='url']"
            
            names = sb.select_all(product_name_selector)
            prices = sb.select_all(product_price_selector)
            availabilities = sb.select_all(product_availability_selector)
            links = sb.select_all(product_link_selector)
            
            # Display the results
            if not names:
                print("No products found.")
            else:
                print(f"\nFound {len(names)} products:")
                print("=" * 80)
                
                in_stock_count = 0
                in_stock_items = []
                
                for i, (name, price) in enumerate(zip(names, prices), 1):
                    product_name = name.text
                    product_price = price.text
                    
                    # Get product URL
                    product_url = ""
                    if i-1 < len(links):
                        try:
                            href = links[i-1].get_attribute("href")
                            if href:
                                product_url = href if href.startswith("http") else f"{BESTBUY_BASE_URL}{href}"
                        except:
                            product_url = "URL not available"
                    
                    # Get availability status
                    stock_status = "Unknown"
                    stock_icon = "❓"
                    is_in_stock = False
                    
                    if i-1 < len(availabilities):
                        availability_text = availabilities[i-1].text.lower()
                        
                        if "sold out" in availability_text:
                            stock_status = "OUT OF STOCK"
                            stock_icon = "❌"
                        elif "coming soon" in availability_text:
                            stock_status = "COMING SOON"
                            stock_icon = "🔜"
                        elif "available" in availability_text:
                            stock_status = "IN STOCK"
                            stock_icon = "✅"
                            is_in_stock = True
                            in_stock_count += 1
                            in_stock_items.append({
                                'name': product_name,
                                'price': product_price,
                                'url': product_url,
                                'index': i-1
                            })
                    
                    print(f"{i}. {stock_icon} {product_name}")
                    print(f"   Price: {product_price}")
                    print(f"   Status: {stock_status}")
                    print(f"   URL: {product_url}")
                    print("-" * 80)
                
                # Print summary of in-stock items
                if in_stock_count > 0:
                    print(f"\n🎯 IN-STOCK ITEMS FOUND! Found {in_stock_count} items in stock. ⏰ Time: {get_timestamp()}")
                    print("\nIn-stock items summary:")
                    for idx, item in enumerate(in_stock_items, 1):
                        print(f"{idx}. {item['name']} - {item['price']}")
                        print(f"   URL: {item['url']}")
                    
                    # Take a screenshot of the in-stock items
                    screenshot_path = capture_screenshot(sb, "bestbuy_in_stock")
                    print(f"📸 Screenshot saved to: {screenshot_path}")
                    
                    # Send Discord notification with screenshot
                    if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                        stock_message = "🔍 **BestBuy items found in stock!**\n\n"
                        for i, item in enumerate(in_stock_items[:5]):  # Limit to first 5 items
                            stock_message += f"**{i+1}.** {item['name']}\n**Price:** {item['price']}\n\n"
                        stock_message += f"**Time:** {get_timestamp()}\n\n🔗 **URL:** {BESTBUY_SEARCH_URL}"
                        
                        # Send notification with screenshot
                        print(f"📤 Sending Discord notification with screenshot: {screenshot_path}")
                        send_discord_notification_with_file(stock_message, screenshot_path, title="🎯 BestBuy Items In Stock!")
                    
                    # Ask user which in-stock item to open
                    if len(in_stock_items) > 1:
                        print("\n🔍 Multiple in-stock items found. Opening the first one...")
                    
                    # Only proceed with add-to-cart if BESTBUY_ATC is True
                    if BESTBUY_ATC:
                        # Open the first in-stock item's URL
                        first_item = in_stock_items[0]
                        product_url = first_item['url']
                        
                        if product_url and product_url != "URL not available":
                            print(f"\n🌐 Opening product page: {product_url}")
                            print(f"⏳ Opening product page for: {first_item['name']}")
                            
                            try:
                                # Navigate to the product page
                                sb.open(product_url)
                                print("✅ Product page loaded successfully")
                                
                                # Try to click the Add to Cart button
                                print("🔍 Looking for Add to Cart button...")
                                
                                # Try different selectors for the Add to Cart button
                                add_to_cart_selectors = [
                                    "button.addToCartButton_3HRhU",
                                    "button.addToCartButton",
                                    "button[data-automation='addToCartButton']",
                                    "button:contains('Add to Cart')"
                                ]
                                
                                add_to_cart_button = None
                                for selector in add_to_cart_selectors:
                                    try:
                                        add_to_cart_button = sb.find_element(selector, timeout=2)
                                        if add_to_cart_button:
                                            print(f"✅ Found Add to Cart button with selector: {selector}")
                                            break
                                    except:
                                        continue
                                
                                if add_to_cart_button:
                                    print("👆 Clicking 'Add to Cart' button...")
                                    add_to_cart_button.click()
                                    print("✅ Add to Cart button clicked! Item added to cart.")
                                    
                                    # Wait for cart to update - increased to 2 seconds
                                    print("⏳ Waiting for cart to update (2 seconds)...")
                                    sb.sleep(2)
                                    
                                    # Navigate directly to checkout page instead of cart page
                                    print(f"🛒 Navigating directly to checkout page...")
                                    sb.open("https://www.bestbuy.ca/checkout/?qit=1#/en-ca/review")
                                    print("✅ Checkout page loaded successfully")

                                    # Wait for checkout page to load completely
                                    print("⏳ Waiting for checkout page elements to load...")
                                    sb.sleep(3)

                                    # Initialize variables for retry logic
                                    max_retries = 3
                                    retry_count = 0
                                    checkout_elements_found = False

                                    # Try to find checkout elements with retry logic
                                    while retry_count < max_retries and not checkout_elements_found:
                                        try:
                                            print(f"🔍 Looking for CVV field (Attempt {retry_count + 1}/{max_retries})...")
                                            cvv_field = sb.find_element('input#cvv[name="cvv"]')
                                            
                                            if cvv_field:
                                                print("✅ Found CVV field, entering value...")
                                                cvv_field.send_keys(BESTBUY_CVV)
                                                print("💳 CVV entered successfully!")
                                                
                                                # Look for Place Order button
                                                try:
                                                    print("🔍 Looking for Place Order button...")
                                                    place_order_button = sb.find_element('button.style-module_button__ucc8a.style-module_primary__UIjVC.order-now')
                                                    
                                                    if place_order_button:
                                                        print("✅ Place order button successfully located!")
                                                        
                                                        # Only click the Place Order button if BESTBUY_PLACE_ORDER is True
                                                        if BESTBUY_PLACE_ORDER:
                                                            print(f"🛒 Clicking Place Order button... ⏰ Time: {get_timestamp()}")
                                                            place_order_button.click()
                                                            print("🎉 ORDER PLACED SUCCESSFULLY!")
                                                            
                                                            # Wait for confirmation page
                                                            print("⏳ Waiting for confirmation page...")
                                                            sb.sleep(3)
                                                            
                                                            # Take a screenshot of the confirmation page
                                                            confirmation_screenshot = capture_screenshot(sb, "bestbuy_order_confirmation")
                                                            
                                                            # Send Discord notification with order confirmation
                                                            confirmation_message = f"🎉 **ORDER PLACED SUCCESSFULLY!**\n\n**Product:** {first_item['name']}\n**Price:** {first_item['price']}\n**Time:** {get_timestamp()}\n\n💳 Payment processed!"
                                                            if ENABLE_DISCORD_STOCK_NOTIFICATIONS:
                                                                send_discord_notification_with_file(confirmation_message, confirmation_screenshot, title="✅ BestBuy Order Confirmed!")
                                                        else:
                                                            print("⚠️ Order placement disabled - skipping final click")
                                                        
                                                        checkout_elements_found = True
                                                    else:
                                                        print("❌ Place Order button not found")
                                                except Exception as e:
                                                    print(f"❌ Error finding Place Order button: {e}")
                                                # Will retry if retry_count < max_retries
                                            else:
                                                print("❌ CVV field not found")
                                            # Will retry if retry_count < max_retries
                                        except Exception as e:
                                            print(f"❌ Error finding or entering CVV: {e}")
                                            # Will retry if retry_count < max_retries
                                        
                                        # If elements not found and we haven't reached max retries, refresh and try again
                                        if not checkout_elements_found and retry_count < max_retries - 1:
                                            retry_count += 1
                                            print(f"⏳ Sleeping 3 seconds before refreshing page (Attempt {retry_count + 1}/{max_retries})...")
                                            sb.sleep(3)
                                            print("🔄 Refreshing checkout page...")
                                            sb.refresh()
                                            sb.sleep(3)  # Wait for page to reload
                                        else:
                                            # Either we found the elements or reached max retries
                                            break

                                    if checkout_elements_found:
                                        print("✅ All checkout elements found successfully!")
                                    else:
                                        print("⚠️ Could not find all checkout elements after maximum retries")

                                    # Pause the script until user decides to continue
                                    print("\n" + "=" * 80)
                                    print("⏸️  SCRIPT PAUSED - IN-STOCK ITEM FOUND!")
                                    print("=" * 80)
                                    print(f"Product: {first_item['name']}")
                                    print(f"Price: {first_item['price']}")
                                    print(f"URL: {product_url}")
                                    print("\nThe browser is now showing the checkout page.")
                                    input("Press Enter to continue monitoring or Ctrl+C to exit...")
                                    
                                    # Return to search page after user continues
                                    print("\n🔄 Returning to search page...")
                                    sb.open(BESTBUY_SEARCH_URL)
                                    sb.sleep(2)
                                    
                            except Exception as e:
                                print(f"❌ Error processing product page: {e}")
                                # Return to search page if there was an error
                                sb.open(BESTBUY_SEARCH_URL)
                                sb.sleep(2)
                        else:
                            print("⚠️ Could not open product page: URL not available")
            
            # Record scan end time
            scan_end_time = get_timestamp()
            scan_duration = datetime.datetime.strptime(scan_end_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.strptime(scan_start_time, '%Y-%m-%d %H:%M:%S.%f')
            
            print(f"\n===== Scan completed | Started: {scan_start_time} | Ended: {scan_end_time} | Duration: {scan_duration.total_seconds():.2f} seconds =====")
            print(f"📊 Refreshes until next CAPTCHA check: {refresh_count}/{next_session_refresh_count}")
            
            # Random refresh interval between BESTBUY_MIN_RANDOM_REFRESH and BESTBUY_MAX_RANDOM_REFRESH seconds
            refresh_time = random.uniform(BESTBUY_MIN_RANDOM_REFRESH, BESTBUY_MAX_RANDOM_REFRESH)
            print(f"\n⏱️  Refreshing in {refresh_time:.2f} seconds...")
            time.sleep(refresh_time)
            print("\n" + "=" * 80)
            print(f"🔄 Refreshing page: {BESTBUY_SEARCH_URL}")
            print("=" * 80 + "\n")
            
            # Refresh the page
            try:
                sb.open(BESTBUY_SEARCH_URL)
            except Exception as e:
                print(f"❌ Error refreshing page: {e}")
                print("Trying to recover...")
                try:
                    # Try a different approach - navigate to BestBuy homepage first
                    sb.open(BESTBUY_BASE_URL)
                    time.sleep(2)
                    print("✅ Homepage loaded, now navigating back to search URL")
                    sb.open(BESTBUY_SEARCH_URL)
                except Exception as e2:
                    print(f"❌ Recovery attempt failed: {e2}")
                    print("Continuing with next refresh...")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Close the browser when done
        try:
            sb.driver.quit()
            print("\nBrowser closed.")
        except:
            pass

    # Save complete output to file
    output_file = f"logs/bestbuy_final_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w') as f:
        f.write(f"🔄 Script terminated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"📝 Saving complete output to: {output_file}\n")
        f.write(f"📄 Final output saved to: {output_file}\n")
        f.write(f"📄 Log file copied to: {output_file}\n")

if __name__ == "__main__":
    scrape_bestbuy()