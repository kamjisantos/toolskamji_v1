#!/usr/bin/env python3
"""
Instagram Login Cookie Extractor
Opens a browser for manual Instagram login, then extracts and saves cookies
"""

import json
import os
import time

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("\n❌ Required packages not installed!")
    print("\n📌 Install requirements:")
    print("   pip install undetected-chromedriver selenium")
    print("\n   Or if you have requirements.txt:")
    print("   pip install -r requirements.txt\n")
    exit(1)

COOKIE_FILE = 'instagram_cookies.json'

class InstagramCookieExtractor:
    """Extract Instagram cookies after manual login"""

    def __init__(self):
        """Initialize Chrome WebDriver with undetected_chromedriver"""
        try:
            print("\n⏳ Initializing browser (this may take a moment)...")

            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')

            self.driver = uc.Chrome(options=options, version_main=None)
            print("✅ Browser initialized successfully!")

        except Exception as e:
            print(f"\n❌ Error initializing Chrome: {e}")
            print("\n📌 Troubleshooting:")
            print("   1. Make sure Google Chrome is installed")
            print("   2. Install/update undetected-chromedriver:")
            print("      pip install --upgrade undetected-chromedriver")
            print("   3. Try running as administrator\n")
            raise

    def extract_cookies(self) -> bool:
        """
        Open Instagram login page, wait for manual login, then extract cookies

        Returns:
            True if cookies extracted successfully, False otherwise
        """
        try:
            print("\n" + "="*60)
            print("INSTAGRAM COOKIE EXTRACTOR")
            print("="*60)
            print("\n📌 Opening Instagram login page...")
            print("   Please login manually in the browser window")
            print("="*60 + "\n")

            self.driver.get('https://www.instagram.com/accounts/login/')

            print("⏳ Waiting for you to login...")
            print("   1. Enter your Instagram username/email")
            print("   2. Enter your password")
            print("   3. Complete 2FA if enabled")
            print("   4. Wait until you see your Instagram feed/homepage")
            print("\n   Script will automatically detect when you're logged in...\n")

            timeout = 300
            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    print("\n❌ Timeout! Login took too long (5 minutes limit)")
                    return False

                current_url = self.driver.current_url

                if 'instagram.com/accounts/login' not in current_url:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[aria-label="Home"]'))
                        )
                        print("\n✅ Login detected successfully!")
                        break
                    except:
                        pass

                cookies = self.driver.get_cookies()
                has_sessionid = any(cookie['name'] == 'sessionid' for cookie in cookies)

                if has_sessionid and 'instagram.com/accounts/login' not in current_url:
                    print("\n✅ Login detected successfully!")
                    break

                time.sleep(1)

            time.sleep(2)

            cookies = self.driver.get_cookies()

            if not cookies:
                print("❌ No cookies found!")
                return False

            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']

            important_cookies = ['sessionid', 'csrftoken', 'mid', 'ds_user_id', 'rur']
            found_cookies = [name for name in important_cookies if name in cookie_dict]

            print(f"\n📊 Cookies extracted: {len(cookies)} total")
            print(f"   Important cookies found: {', '.join(found_cookies)}")

            if 'sessionid' not in cookie_dict:
                print("\n⚠️  Warning: 'sessionid' cookie not found!")
                print("   Login might not be successful. Please try again.")
                return False

            with open(COOKIE_FILE, 'w') as f:
                json.dump(cookie_dict, f, indent=2)

            print(f"\n✅ Cookies saved to: {COOKIE_FILE}")
            print("\n" + "="*60)
            print("SUCCESS!")
            print("="*60)
            print(f"\nYou can now use these cookies in versiig.py")
            print("The browser will close in 5 seconds...\n")

            time.sleep(5)
            return True

        except Exception as e:
            print(f"\n❌ Error during cookie extraction: {e}")
            return False

        finally:
            self.driver.quit()

def main():
    """Main function"""
    if os.path.exists(COOKIE_FILE):
        response = input(f"\n⚠️  {COOKIE_FILE} already exists. Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return

    try:
        extractor = InstagramCookieExtractor()
        success = extractor.extract_cookies()

        if success:
            print("="*60)
            print("NEXT STEPS:")
            print("="*60)
            print(f"1. Cookies are saved in: {COOKIE_FILE}")
            print("2. Run versiig.py to use these cookies")
            print("3. Cookies will expire after some time (re-run this script)")
            print("="*60 + "\n")
        else:
            print("\n❌ Failed to extract cookies. Please try again.\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == '__main__':
    main()
