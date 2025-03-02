"""
Basic BestBuy scraper to extract product names from a search page.
"""
import time
import os
import random
from seleniumbase import sb_cdp
import sys
import datetime

# Import configuration settings
from scraperconfig import COOKIE_FILE, PAGE_LOAD_WAIT, MIN_RANDOM_REFRESH, MAX_RANDOM_REFRESH

def get_timestamp():
    """Return a formatted timestamp string."""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def scrape_bestbuy():
    """
    Basic function to scrape product names from BestBuy search page.
    """
    # URL for BestBuy search
    url = "https://www.bestbuy.ca/en-ca/collection/nvidia-graphic-cards-rtx-50-series/bltbd7cf78bd1d558ef?icmp=computing_evergreen_nvidia_graphics_cards_ssc_sbc_50_series"
    base_url = "https://www.bestbuy.ca"
    cart_url = "https://www.bestbuy.ca/en-ca/basket"
    
    # Start a new browser instance
    print(f"Opening browser and navigating to {url}")
    sb = sb_cdp.Chrome()
    
    # Load cookies if available
    if os.path.exists(COOKIE_FILE):
        print(f"🍪 Loading cookies from {COOKIE_FILE}")
        sb.load_cookies(COOKIE_FILE)
        print("✅ Cookies loaded successfully")
    else:
        print(f"⚠️ Cookie file not found at {COOKIE_FILE}")
    
    # Navigate to the URL after loading cookies
    print(f"Navigating to {url}")
    try:
        sb.open(url)
        print("✅ Page loaded successfully")
    except Exception as e:
        print(f"❌ Error loading page: {e}")
        print("Trying again with a longer timeout...")
        try:
            sb.driver.set_page_load_timeout(30)  # Increase timeout
            sb.open(url)
            print("✅ Page loaded successfully on second attempt")
        except Exception as e2:
            print(f"❌ Error loading page on second attempt: {e2}")
            print("Trying one more time with a different approach...")
            try:
                # Try a different approach - navigate to BestBuy homepage first
                sb.open("https://www.bestbuy.ca/")
                time.sleep(3)
                print("✅ Homepage loaded, now navigating to search URL")
                sb.open(url)
                print("✅ Search page loaded successfully")
            except Exception as e3:
                print(f"❌ All attempts to load page failed: {e3}")
                print("Please check your internet connection or if BestBuy is blocking automated access")
                sb.driver.quit()
                return
    
    # Continuous monitoring loop
    refresh_count = 0
    try:
        while True:
            refresh_count += 1
            scan_start_time = get_timestamp()
            print(f"\n===== Refresh #{refresh_count} | Started: {scan_start_time} =====")
            
            # Wait for page to load
            print(f"⏳ Waiting {PAGE_LOAD_WAIT} seconds for page to load...")
            sb.sleep(PAGE_LOAD_WAIT)
            
            # Check if page loaded correctly
            try:
                # Check if we can find any product elements
                product_check = sb.select_all("h3.productItemName_3IZ3c", timeout=5)
                if not product_check:
                    print("⚠️ No product elements found. Page may not have loaded correctly.")
                    print("Reloading page...")
                    sb.open(url)
                    sb.sleep(3)  # Wait a bit longer for reload
                    continue
            except Exception as e:
                print(f"⚠️ Error checking page content: {e}")
                print("Reloading page...")
                sb.open(url)
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
                                product_url = href if href.startswith("http") else f"{base_url}{href}"
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
                    
                    # Ask user which in-stock item to open
                    if len(in_stock_items) > 1:
                        print("\n🔍 Multiple in-stock items found. Opening the first one...")
                    
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
                                
                                # Wait for cart to update
                                print("⏳ Waiting for cart to update...")
                                sb.sleep(1)
                                
                                # Navigate to cart page
                                print(f"🛒 Navigating to cart page: {cart_url}")
                                sb.open(cart_url)
                                print("✅ Cart page loaded successfully")
                            else:
                                print("❌ Add to Cart button not found")
                            
                            # Pause the script until user decides to continue
                            print("\n" + "=" * 80)
                            print("⏸️  SCRIPT PAUSED - IN-STOCK ITEM FOUND!")
                            print("=" * 80)
                            print(f"Product: {first_item['name']}")
                            print(f"Price: {first_item['price']}")
                            print(f"URL: {product_url}")
                            print("\nThe browser is now showing the cart page.")
                            input("Press Enter to continue monitoring or Ctrl+C to exit...")
                            
                            # Return to search page after user continues
                            print("\n🔄 Returning to search page...")
                            sb.open(url)
                            sb.sleep(2)
                            
                        except Exception as e:
                            print(f"❌ Error processing product page: {e}")
                            # Return to search page if there was an error
                            sb.open(url)
                            sb.sleep(2)
                    else:
                        print("⚠️ Could not open product page: URL not available")
            
            # Record scan end time
            scan_end_time = get_timestamp()
            scan_duration = datetime.datetime.strptime(scan_end_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.strptime(scan_start_time, '%Y-%m-%d %H:%M:%S.%f')
            
            print(f"\n===== Scan completed | Started: {scan_start_time} | Ended: {scan_end_time} | Duration: {scan_duration.total_seconds():.2f} seconds =====")
            
            # Random refresh interval between MIN_RANDOM_REFRESH and MAX_RANDOM_REFRESH seconds
            refresh_time = random.uniform(MIN_RANDOM_REFRESH, MAX_RANDOM_REFRESH)
            print(f"\n⏱️  Refreshing in {refresh_time:.2f} seconds...")
            time.sleep(refresh_time)
            print("\n" + "=" * 80)
            print(f"🔄 Refreshing page: {url}")
            print("=" * 80 + "\n")
            
            # Refresh the page
            try:
                sb.open(url)
            except Exception as e:
                print(f"❌ Error refreshing page: {e}")
                print("Trying to recover...")
                try:
                    # Try a different approach - navigate to BestBuy homepage first
                    sb.open("https://www.bestbuy.ca/")
                    time.sleep(2)
                    print("✅ Homepage loaded, now navigating back to search URL")
                    sb.open(url)
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

if __name__ == "__main__":
    scrape_bestbuy()