import os
import time
import signal
from seleniumbase import sb_cdp

# Constants
COOKIE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies")
COOKIE_FILE = os.path.join(COOKIE_DIR, "cookies.json")  # Path to cookie file
BROWSER_WAIT_TIME = 20  # Time in seconds to keep the browser open for manual login

# Create a temporary HTML file for the browser to load
def create_dummy_html():
    """Creates a simple HTML file for the browser to load initially."""
    dummy_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_dummy.html")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Login Helper</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #333; }}
        .instructions {{
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 20px 0;
        }}
        .highlight {{
            font-weight: bold;
            color: #d63384;
        }}
    </style>
</head>
<body>
    <h1>Cookie Capture Tool</h1>
    <div class="instructions">
        <p>This browser window has been opened to help you capture cookies for automated access.</p>
        <p>Instructions:</p>
        <ol>
            <li>Navigate to the site you want to access (e.g., <code>https://example.com</code>)</li>
            <li>Log in with your credentials</li>
            <li><span class="highlight">Close this browser window when you're done</span></li>
        </ol>
        <p>This window will automatically close after {BROWSER_WAIT_TIME} seconds</p>
    </div>
</body>
</html>
    """
    
    with open(dummy_html_path, "w") as f:
        f.write(html_content)
    
    return dummy_html_path

def cleanup_temp_files(dummy_html_path):
    """Removes temporary files created by the script."""
    try:
        if os.path.exists(dummy_html_path):
            os.remove(dummy_html_path)
    except Exception as e:
        print(f"Warning: Could not remove temporary file: {e}")

def get_and_save_cookies():
    """Launches a browser, allows manual login, and saves cookies."""
    
    # Ensure the cookies directory exists
    if not os.path.exists(COOKIE_DIR):
        os.makedirs(COOKIE_DIR)
    
    # Create temporary HTML file
    dummy_html_path = create_dummy_html()
    dummy_html_url = f"file://{os.path.abspath(dummy_html_path)}"
    
    print("\n🌐 Opening browser...")

    # Set up Chrome options to bypass bot detection
    chrome_options = {
        "disable_blink_features": "AutomationControlled",
        "enable_undetected": True,
    }

    # Start browser session on dummy HTML file with undetected mode
    sb = sb_cdp.Chrome(dummy_html_url, uc=True, undetected=True, chrome_options=chrome_options)

    # Load existing cookies if available
    if os.path.exists(COOKIE_FILE):
        print(f"🍪 Loading existing cookies from {COOKIE_FILE}")
        sb.load_cookies(COOKIE_FILE)
        sb.refresh()  # Refresh to apply cookies
        print("✅ Cookies loaded. You may already be logged in.")
    else:
        print("⚠️ No existing cookies found. Please log in manually.")

    print(f"\n⏳ Please navigate to the site you need, log in if needed, then close the browser when done (or wait {BROWSER_WAIT_TIME} seconds)...\n")

    try:
        sb.sleep(BROWSER_WAIT_TIME)

        try:
            sb.save_cookies(COOKIE_FILE)
            print(f"\n✅ Cookies saved to {COOKIE_FILE}\n")
        except Exception as e:
            print(f"\n❌ Error saving cookies: {e}")
    finally:
        # Clean up temporary files
        cleanup_temp_files(dummy_html_path)

    print("Exiting script...\n")

if __name__ == "__main__":
    # Handle termination signals
    signal.signal(signal.SIGINT, lambda x, y: os._exit(0))
    signal.signal(signal.SIGTERM, lambda x, y: os._exit(0))

    get_and_save_cookies()