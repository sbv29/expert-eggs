"""
Basic BestBuy scraper to extract product names from a search page.
"""
import time
import os
import random
from seleniumbase import sb_cdp

# Import configuration settings
from scraperconfig import COOKIE_FILE, PAGE_LOAD_WAIT

def scrape_bestbuy():
    """
    Basic function to scrape product names from BestBuy search page.
    """
    # URL for BestBuy search
    url = "https://www.bestbuy.ca/en-ca/collection/nvidia-graphic-cards-rtx-50-series/bltbd7cf78bd1d558ef?icmp=computing_evergreen_nvidia_graphics_cards_ssc_sbc_50_series"
    
    # Start a new browser instance
    print(f"Opening browser and navigating to {url}")
    sb = sb_cdp.Chrome(url)
    
    # Load cookies if available
    if os.path.exists(COOKIE_FILE):
        print(f"🍪 Loading cookies from {COOKIE_FILE}")
        sb.load_cookies(COOKIE_FILE)
        sb.open(url)  # Reload the page with cookies
        print("✅ Cookies loaded successfully")
    else:
        print(f"⚠️ Cookie file not found at {COOKIE_FILE}")
    
    # Continuous monitoring loop
    refresh_count = 0
    try:
        while True:
            refresh_count += 1
            print(f"\n===== Refresh #{refresh_count} =====")
            
            # Wait for page to load
            print(f"⏳ Waiting {PAGE_LOAD_WAIT} seconds for page to load...")
            sb.sleep(PAGE_LOAD_WAIT)
            
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
            
            # Select product names and prices
            print("Finding product names and prices...")
            product_name_selector = "h3.productItemName_3IZ3c"
            product_price_selector = "div.style-module_price__ql4Q1"
            product_availability_selector = "div.availabilityMessageSearch_1KfqF"
            
            names = sb.select_all(product_name_selector)
            prices = sb.select_all(product_price_selector)
            availabilities = sb.select_all(product_availability_selector)
            
            # Display the results
            if not names:
                print("No products found.")
            else:
                print(f"\nFound {len(names)} products:")
                print("=" * 80)
                
                for i, (name, price) in enumerate(zip(names, prices), 1):
                    product_name = name.text
                    product_price = price.text
                    
                    # Get availability status
                    stock_status = "Unknown"
                    stock_icon = "❓"
                    
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
                    
                    print(f"{i}. {stock_icon} {product_name}")
                    print(f"   Price: {product_price}")
                    print(f"   Status: {stock_status}")
                    print("-" * 80)
            
            # Random refresh interval between 3 and 5 seconds
            refresh_time = random.uniform(3, 5)
            print(f"\n⏱️  Refreshing in {refresh_time:.2f} seconds...")
            time.sleep(refresh_time)
            print("\n" + "=" * 80)
            print(f"🔄 Refreshing page: {url}")
            print("=" * 80 + "\n")
            
            # Refresh the page
            sb.open(url)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user.")
    
    # Close the browser when done
    try:
        sb.driver.quit()
        print("\nBrowser closed.")
    except:
        pass

if __name__ == "__main__":
    scrape_bestbuy()