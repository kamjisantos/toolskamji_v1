import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json

def scrape_user_profile(driver, username):
    """Scrape user profile data (followers, following, likes)"""
    try:
        print(f"\n🔍 Mencari profil: @{username}")
        print("   ⏳ Loading...")

        # Ensure window size is consistent
        try:
            driver.set_window_size(1920, 1080)
            driver.maximize_window()
        except:
            pass

        # Buka halaman profile
        profile_url = f"https://www.tiktok.com/@{username}"
        driver.get(profile_url)

        print("   ⏳ Waiting for page to fully load...")

        # Wait for either profile content OR error message to appear
        wait = WebDriverWait(driver, 20)

        try:
            # Try to wait for user-title (profile name) which appears on valid profiles
            print("   🔍 Checking if profile exists...")
            try:
                user_title = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-e2e="user-title"], h1[class*="ShareTitle"]'))
                )
                print(f"   ✓ Profile found: {user_title.text}")
            except TimeoutException:
                # Check if it's a "not found" page
                time.sleep(2)
                page_source = driver.page_source.lower()
                if "couldn't find this account" in page_source or "tidak dapat menemukan" in page_source:
                    print(f"   ❌ Akun @{username} tidak ditemukan!")
                    return None
                else:
                    print("   ⚠️ Profile element timeout but page loaded - continuing...")

        except Exception as e:
            print(f"   ⚠️ Error checking profile: {e}")

        print("   📊 Mengambil data stats...")

        # Scroll to make sure stats are in viewport
        try:
            driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(1)
        except:
            pass

        # CRITICAL: Wait for H3CountInfos element to be present
        try:
            print("   ⏳ Waiting for stats container...")
            stats_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[class*="H3CountInfos"], h3.css-17tvrad-5e6d46e3--H3CountInfos'))
            )
            print("   ✓ Stats container loaded!")

            # Scroll to stats container to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", stats_container)
            time.sleep(2)  # Extra wait for content to populate
        except TimeoutException:
            print("   ⚠️ Stats container timeout - trying anyway...")
            time.sleep(3)

        # Method 1: Try to find stats from page elements
        stats = {
            'username': username,
            'followers': 'N/A',
            'following': 'N/A',
            'likes': 'N/A'
        }

        try:
            # Get page source and try to extract from JSON data
            page_source = driver.page_source

            # Try to find __UNIVERSAL_DATA_FOR_REHYDRATION__ or similar
            if '__UNIVERSAL_DATA_FOR_REHYDRATION__' in page_source:
                match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>', page_source)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        user_info = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})
                        user_stats = user_info.get('stats', {})

                        stats['followers'] = user_stats.get('followerCount', 'N/A')
                        stats['following'] = user_stats.get('followingCount', 'N/A')
                        stats['likes'] = user_stats.get('heartCount', 'N/A')
                    except:
                        pass
        except:
            pass

        # Method 2: Try to extract from visible elements with EXPLICIT WAIT (PRIMARY METHOD)
        print("   🔍 Method 2: Searching data-e2e attributes with wait...")
        try:
            wait = WebDriverWait(driver, 10)

            # Wait and get FOLLOWERS
            try:
                print("   ⏳ Waiting for followers element...")
                followers_elem = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]'))
                )
                followers_text = followers_elem.text.strip()
                if followers_text:
                    stats['followers'] = followers_text
                    print(f"   ✓ Followers found: {stats['followers']}")
                else:
                    print("   ⚠️  Followers element empty")
            except TimeoutException:
                print("   ⚠️  Followers element timeout")
            except Exception as e:
                print(f"   ⚠️  Followers error: {e}")

            # Wait and get FOLLOWING
            try:
                following_elem = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="following-count"]'))
                )
                following_text = following_elem.text.strip()
                if following_text:
                    stats['following'] = following_text
                    print(f"   ✓ Following found: {stats['following']}")
                else:
                    print("   ⚠️  Following element empty")
            except TimeoutException:
                print("   ⚠️  Following element timeout")
            except Exception as e:
                print(f"   ⚠️  Following error: {e}")

            # Wait and get LIKES
            try:
                likes_elem = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="likes-count"]'))
                )
                likes_text = likes_elem.text.strip()
                if likes_text:
                    stats['likes'] = likes_text
                    print(f"   ✓ Likes found: {stats['likes']}")
                else:
                    print("   ⚠️  Likes element empty")
            except TimeoutException:
                print("   ⚠️  Likes element timeout")
            except Exception as e:
                print(f"   ⚠️  Likes error: {e}")

        except Exception as e:
            print(f"   ⚠️  Method 2 error: {e}")

        # Method 3: Fallback - scan for all strong tags with numbers
        if stats['followers'] == 'N/A' or stats['following'] == 'N/A' or stats['likes'] == 'N/A':
            print("   🔍 Method 3: Scanning all strong elements...")
            try:
                # Get ALL strong elements on the page
                all_strongs = driver.find_elements(By.TAG_NAME, 'strong')
                print(f"   📋 Found {len(all_strongs)} strong elements total")

                numbers = []
                for strong in all_strongs:
                    text = strong.text.strip()
                    # Check if it's a number or formatted number
                    if text and re.match(r'^\d+[.,]?\d*[KMBkmb]?$', text):
                        # Check data-e2e attribute
                        data_e2e = strong.get_attribute('data-e2e')
                        print(f"   🔢 Number found: '{text}' (data-e2e: {data_e2e})")

                        if data_e2e == 'followers-count':
                            stats['followers'] = text
                            print(f"   ✓ Followers by data-e2e: {text}")
                            continue
                        elif data_e2e == 'following-count':
                            stats['following'] = text
                            print(f"   ✓ Following by data-e2e: {text}")
                            continue
                        elif data_e2e == 'likes-count':
                            stats['likes'] = text
                            print(f"   ✓ Likes by data-e2e: {text}")
                            continue

                        # Get the parent's text to understand context
                        try:
                            parent_text = strong.find_element(By.XPATH, './following-sibling::*').text.lower()

                            if 'pengikut' in parent_text or 'follower' in parent_text:
                                stats['followers'] = text
                                print(f"   ✓ Followers by context: {text}")
                            elif 'mengikuti' in parent_text or 'following' in parent_text:
                                stats['following'] = text
                                print(f"   ✓ Following by context: {text}")
                            elif 'suka' in parent_text or 'like' in parent_text:
                                stats['likes'] = text
                                print(f"   ✓ Likes by context: {text}")
                            else:
                                numbers.append(text)
                        except:
                            # Just collect numbers if we can't determine context
                            numbers.append(text)

                # If still missing, use order-based detection
                if (stats['followers'] == 'N/A' or stats['following'] == 'N/A') and len(numbers) >= 2:
                    print(f"   📋 Unmatched numbers: {numbers}")
                    if len(numbers) >= 3:
                        stats['following'] = numbers[0]
                        stats['followers'] = numbers[1]
                        stats['likes'] = numbers[2]
                        print(f"   ℹ️ Using order-based: Following={numbers[0]}, Followers={numbers[1]}, Likes={numbers[2]}")

            except Exception as e:
                print(f"   ⚠️ Method 3 error: {e}")
                import traceback
                traceback.print_exc()

        # Method 4: Debug - show what we found
        print(f"   📊 Extracted - Followers: {stats['followers']}, Following: {stats['following']}, Likes: {stats['likes']}")

        return stats

    except Exception as e:
        print(f"   ❌ Error saat scraping profil: {e}")
        import traceback
        traceback.print_exc()
        return None

def keep_session_alive(driver):
    """
    Keep browser session alive to prevent DevTools disconnect
    Performs micro-actions that keep Chrome's connection active
    """
    try:
        # Micro scroll to keep renderer active
        driver.execute_script("window.scrollBy(0, 1); window.scrollBy(0, -1);")
        # Ping current URL to keep session alive
        _ = driver.current_url
    except:
        pass

def ensure_window_focus(driver):
    """
    Ensure browser window is focused and active to prevent lazy loading issues
    This forces the browser to render elements properly even in background
    """
    try:
        # Keep session alive first
        keep_session_alive(driver)

        # Maximize window to ensure elements are visible
        driver.maximize_window()

        # Switch to window to ensure it's active
        driver.switch_to.window(driver.current_window_handle)

        # Execute JS to focus window and trigger rendering
        driver.execute_script("""
            window.focus();
            document.body.focus();
            window.scrollTo(0, 0);
        """)

        time.sleep(0.5)
        print("   ✓ Window focused and viewport refreshed")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not ensure window focus: {e}")

def click_report_button(driver):
    """
    Click 3-dot menu button and then report button (language agnostic)
    Returns True if report was submitted successfully, False otherwise
    """
    try:
        # CRITICAL: Ensure window is focused and active first
        print("\n🔍 Ensuring browser window is active...")
        ensure_window_focus(driver)

        # CRITICAL: Close any open modals/menus first by pressing ESC
        try:
            print("🔍 Checking for open modals/menus...")
            driver.execute_script("""
                // Close any open modals
                const modals = document.querySelectorAll('[role="dialog"], [class*="modal"]');
                modals.forEach(m => m.remove());
            """)
            # Press ESC key to close any menus
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(0.8)
            print("   ✓ Cleared any open menus")
        except:
            pass

        print("\n🖱️  Attempting to click 3-dot menu...")

        wait = WebDriverWait(driver, 15)  # Increased timeout for background tabs

        # Step 1: Click the 3-dot menu button (using data-e2e attribute - language independent!)
        try:
            three_dot_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="user-more"]'))
            )
            three_dot_btn.click()
            print("   ✅ Successfully clicked 3-dot menu!")
            time.sleep(2)  # Increased wait for menu to fully appear
        except TimeoutException:
            print("   ❌ 3-dot menu button not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking 3-dot menu: {e}")
            return False

        # Step 2: Click the Report button (using data-e2e attribute - works for both languages!)
        try:
            print("🖱️  Attempting to click Report button...")

            # CRITICAL: Trigger viewport refresh to ensure menu is rendered
            driver.execute_script("window.scrollBy(0, 1);")
            time.sleep(0.5)

            # Try multiple times with viewport refresh
            report_clicked = False
            for attempt in range(3):
                try:
                    report_btn = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="user-report"]'))
                    )

                    # Verify element is actually visible
                    if report_btn.is_displayed():
                        # Scroll into view and click
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", report_btn)
                        time.sleep(0.3)
                        report_btn.click()
                        print("   ✅ Successfully clicked Report button!")
                        report_clicked = True
                        break
                    else:
                        print(f"   ⚠️  Report button not visible, attempt {attempt + 1}/3")
                        if attempt < 2:
                            driver.execute_script("window.scrollBy(0, 1);")
                            time.sleep(1)
                except:
                    print(f"   ⚠️  Report button not found, attempt {attempt + 1}/3")
                    if attempt < 2:
                        driver.execute_script("window.scrollBy(0, 1);")
                        time.sleep(1)

            if not report_clicked:
                print("   ❌ Report button not found in menu after 3 attempts!")
                return False

            time.sleep(2.5)  # Wait for report dialog to fully load
        except TimeoutException:
            print("   ❌ Report button not found in menu!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking Report button: {e}")
            return False

        # Step 2.5: Wait for "Laporkan akun" button and click it
        try:
            print("🖱️  Waiting for 'Laporkan akun' option...")

            # CRITICAL: Force viewport refresh to trigger rendering
            driver.execute_script("window.scrollBy(0, 100); setTimeout(() => window.scrollBy(0, -100), 100);")
            time.sleep(1.5)  # Increased wait for modal to render

            # Find "Laporkan akun" option (it's a label with data-e2e="report-card-reason")
            laporkan_akun_options = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label[data-e2e="report-card-reason"]'))
            )

            if len(laporkan_akun_options) > 0:
                # Click the FIRST option which is "Laporkan akun"
                laporkan_akun_btn = laporkan_akun_options[0]
                print(f"   ✓ Found 'Laporkan akun' option (text: {laporkan_akun_btn.text[:30]})")

                # Scroll and click
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", laporkan_akun_btn)
                time.sleep(0.5)

                # Try JS click first
                try:
                    driver.execute_script("arguments[0].click();", laporkan_akun_btn)
                    print("   ✅ Successfully clicked 'Laporkan akun'! (JS click)")
                except:
                    laporkan_akun_btn.click()
                    print("   ✅ Successfully clicked 'Laporkan akun'! (regular click)")

                time.sleep(2)  # Wait for next screen
            else:
                print("   ❌ No 'Laporkan akun' option found!")
                return False

        except TimeoutException:
            print("   ❌ 'Laporkan akun' options not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking 'Laporkan akun': {e}")
            import traceback
            traceback.print_exc()
            return False

        # Step 3: Wait for ALL 4 report reasons to appear, then click "Lainnya"
        try:
            print("🖱️  Waiting for report reason options to load...")

            # CRITICAL: Force viewport refresh before checking
            driver.execute_script("window.scrollBy(0, 50);")
            time.sleep(0.3)
            driver.execute_script("window.scrollBy(0, -50);")

            # Wait up to 15 seconds for all 4 options to appear (increased for background tabs)
            for attempt in range(15):
                report_reasons = driver.find_elements(By.CSS_SELECTOR, 'label[data-e2e="report-card-reason"]')
                print(f"   📋 Attempt {attempt + 1}: Found {len(report_reasons)} report options")

                if len(report_reasons) >= 4:
                    print("   ✓ All 4 report options loaded!")
                    break

                # Trigger viewport recalculation on each attempt
                driver.execute_script("window.scrollBy(0, 1);")
                time.sleep(1)

            if len(report_reasons) < 4:
                print(f"   ❌ Timeout: Only found {len(report_reasons)} options after 10 seconds")
                return False

            # Now click "Lainnya" (LAST option)
            print("🖱️  Attempting to click 'Lainnya' option...")
            report_reasons = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label[data-e2e="report-card-reason"]'))
            )

            if len(report_reasons) >= 4:
                print(f"   📋 Found {len(report_reasons)} report options")
                # Click the LAST option (Lainnya)
                lainnya_option = report_reasons[-1]  # Last element

                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lainnya_option)
                time.sleep(0.5)

                # Try JavaScript click first (more reliable)
                try:
                    driver.execute_script("arguments[0].click();", lainnya_option)
                    print("   ✅ Successfully clicked 'Lainnya' option! (JS click)")
                except:
                    # Fallback to regular click
                    lainnya_option.click()
                    print("   ✅ Successfully clicked 'Lainnya' option! (regular click)")

                time.sleep(3)  # Wait for next screen to load
            else:
                print(f"   ❌ Expected at least 4 report options, found {len(report_reasons)}")
                return False

        except TimeoutException:
            print("   ❌ Report reason options not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking 'Lainnya' option: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Step 4: Wait for new options to load, then click "Konten seksual dan ketelanjangan"
        try:
            print("🖱️  Waiting for detailed report options...")

            # CRITICAL: Force viewport refresh to trigger lazy loading
            driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(0.5)
            driver.execute_script("window.scrollBy(0, -100);")

            # Wait up to 15 seconds for new options to appear (increased for background tabs)
            for attempt in range(15):
                detailed_reasons = driver.find_elements(By.CSS_SELECTOR, 'label[data-e2e="report-card-reason"]')
                print(f"   📋 Attempt {attempt + 1}: Found {len(detailed_reasons)} detailed options")

                if len(detailed_reasons) >= 10:  # Should have many options now
                    print("   ✓ All detailed options loaded!")
                    break

                # Trigger viewport recalculation on each attempt
                driver.execute_script("window.scrollBy(0, 1);")
                time.sleep(1)

            if len(detailed_reasons) < 5:
                print(f"   ⚠️  Only found {len(detailed_reasons)} detailed options")

            # Find and click "Konten seksual dan ketelanjangan"
            print("🖱️  Searching for 'Konten seksual dan ketelanjangan'...")

            sexual_content_option = None
            for reason in detailed_reasons:
                text = reason.text.strip()
                if 'konten seksual' in text.lower() or 'ketelanjangan' in text.lower():
                    sexual_content_option = reason
                    print(f"   ✓ Found option: {text}")
                    break

            if sexual_content_option:
                # Scroll and click
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sexual_content_option)
                time.sleep(0.5)

                try:
                    driver.execute_script("arguments[0].click();", sexual_content_option)
                    print("   ✅ Successfully clicked 'Konten seksual dan ketelanjangan'! (JS click)")
                except:
                    sexual_content_option.click()
                    print("   ✅ Successfully clicked 'Konten seksual dan ketelanjangan'! (regular click)")

                time.sleep(3)  # Wait for next options
            else:
                print("   ❌ 'Konten seksual dan ketelanjangan' option not found!")
                return False

        except TimeoutException:
            print("   ❌ Detailed report options not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking 'Konten seksual dan ketelanjangan': {e}")
            import traceback
            traceback.print_exc()
            return False

        # Step 5: Wait for sub-options, then click "Ketelanjangan dewasa"
        try:
            print("🖱️  Waiting for sub-category options...")

            # Wait for new options to appear
            for attempt in range(10):
                sub_options = driver.find_elements(By.CSS_SELECTOR, 'label[data-e2e="report-card-reason"]')
                print(f"   📋 Attempt {attempt + 1}: Found {len(sub_options)} sub-options")

                if len(sub_options) >= 3:  # Should have at least 3 options
                    print("   ✓ Sub-options loaded!")
                    break

                time.sleep(1)

            if len(sub_options) < 2:
                print(f"   ⚠️  Only found {len(sub_options)} sub-options")

            # Find and click "Ketelanjangan dewasa"
            print("🖱️  Searching for 'Ketelanjangan dewasa'...")

            adult_nudity_option = None
            for option in sub_options:
                text = option.text.strip()
                if 'ketelanjangan dewasa' in text.lower():
                    adult_nudity_option = option
                    print(f"   ✓ Found option: {text}")
                    break

            if adult_nudity_option:
                # Scroll and click
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", adult_nudity_option)
                time.sleep(0.5)

                try:
                    driver.execute_script("arguments[0].click();", adult_nudity_option)
                    print("   ✅ Successfully clicked 'Ketelanjangan dewasa'! (JS click)")
                except:
                    adult_nudity_option.click()
                    print("   ✅ Successfully clicked 'Ketelanjangan dewasa'! (regular click)")

                time.sleep(3)  # Wait for submit button
            else:
                print("   ❌ 'Ketelanjangan dewasa' option not found!")
                return False

        except TimeoutException:
            print("   ❌ Sub-category options not found!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking 'Ketelanjangan dewasa': {e}")
            import traceback
            traceback.print_exc()
            return False

        # Step 6: Click "Kirim" (Submit) button
        try:
            print("🖱️  Searching for 'Kirim' button...")

            # Try multiple selectors for submit button
            submit_button = None

            # Try CSS selector
            try:
                submit_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-1all3tm-0be0dc34--ButtonSubmit'))
                )
                print("   ✓ Found 'Kirim' button (CSS selector)")
            except:
                pass

            # Try by text content
            if not submit_button:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    for btn in buttons:
                        if 'kirim' in btn.text.lower() or 'submit' in btn.text.lower():
                            submit_button = btn
                            print(f"   ✓ Found button with text: {btn.text}")
                            break
                except:
                    pass

            if submit_button:
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                time.sleep(0.5)

                # Click using JS
                try:
                    driver.execute_script("arguments[0].click();", submit_button)
                    print("   ✅ Successfully clicked 'Kirim' button! (JS click)")
                except:
                    submit_button.click()
                    print("   ✅ Successfully clicked 'Kirim' button! (regular click)")

                time.sleep(3)  # Wait for success message
            else:
                print("   ❌ 'Kirim' button not found!")
                return False

        except TimeoutException:
            print("   ❌ 'Kirim' button not found (timeout)!")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking 'Kirim' button: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Step 7: Click "Selesai" (Done) button to close dialog
        try:
            print("🖱️  Searching for 'Selesai' button...")

            # Try multiple selectors for done button
            done_button = None

            # Try CSS selector
            try:
                done_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-1ob5qbl-0be0dc34--ButtonFinish'))
                )
                print("   ✓ Found 'Selesai' button (CSS selector)")
            except:
                pass

            # Try by text content
            if not done_button:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    for btn in buttons:
                        if 'selesai' in btn.text.lower() or 'done' in btn.text.lower():
                            done_button = btn
                            print(f"   ✓ Found button with text: {btn.text}")
                            break
                except:
                    pass

            if done_button:
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", done_button)
                time.sleep(0.5)

                # Click using JS
                try:
                    driver.execute_script("arguments[0].click();", done_button)
                    print("   ✅ Successfully clicked 'Selesai' button! (JS click)")
                except:
                    done_button.click()
                    print("   ✅ Successfully clicked 'Selesai' button! (regular click)")

                time.sleep(2)  # Wait for dialog to close
                print("   🎉 Report submitted successfully!")
                return True
            else:
                print("   ⚠️  'Selesai' button not found, but report was submitted")
                return True  # Still return True since report was submitted

        except TimeoutException:
            print("   ⚠️  'Selesai' button timeout, but report was submitted")
            return True  # Still return True since report was submitted
        except Exception as e:
            print(f"   ⚠️  Error clicking 'Selesai' button: {e}")
            print("   ℹ️  Report was submitted, just couldn't close dialog")
            return True  # Still return True since report was submitted

    except Exception as e:
        print(f"   ❌ Error in click_report_button: {e}")
        import traceback
        traceback.print_exc()
        return False

def report_user_with_retry(driver, username, max_attempts=3):
    """
    Wrapper function untuk report dengan retry mechanism
    Jika gagal, refresh halaman profil dan coba lagi dari awal

    Args:
        driver: Selenium WebDriver instance
        username: Username target (tanpa @)
        max_attempts: Maksimal percobaan (default: 3)

    Returns:
        True jika berhasil report, False jika gagal setelah max_attempts
    """
    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*60}")
        print(f"🔄 PERCOBAAN {attempt}/{max_attempts} - Report @{username}")
        print(f"{'='*60}")

        try:
            # If not first attempt, refresh the profile page first
            if attempt > 1:
                print(f"🔄 Refreshing profile page untuk retry...")
                profile_url = f"https://www.tiktok.com/@{username}"
                driver.get(profile_url)

                # Wait for profile to load
                print(f"   ⏳ Waiting for profile to load...")
                time.sleep(4)  # Longer wait for refresh

                # Verify page loaded
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-e2e="user-more"]'))
                    )
                    print(f"   ✅ Profile page loaded successfully")
                except:
                    print(f"   ⚠️  Profile might not be fully loaded, but continuing...")
                    time.sleep(2)

            # Try to execute the report flow
            print(f"🚀 Starting report flow...")
            success = click_report_button(driver)

            if success:
                print(f"\n{'='*60}")
                print(f"✅ PERCOBAAN {attempt} BERHASIL!")
                print(f"🎉 Report untuk @{username} telah disubmit!")
                print(f"{'='*60}")
                return True
            else:
                print(f"\n{'='*60}")
                print(f"❌ PERCOBAAN {attempt} GAGAL")
                print(f"{'='*60}")

                if attempt < max_attempts:
                    print(f"   ⏳ Menunggu 3 detik sebelum retry...")
                    time.sleep(3)
                else:
                    print(f"   ❌ Tidak ada percobaan lagi tersisa")

        except KeyboardInterrupt:
            print(f"\n\n⚠️  Report dibatalkan oleh user (Ctrl+C)")
            raise  # Re-raise to stop the whole process

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ERROR pada percobaan {attempt}")
            print(f"{'='*60}")
            print(f"   Error: {e}")

            if attempt < max_attempts:
                print(f"   ⏳ Menunggu 3 detik sebelum retry...")
                time.sleep(3)
            else:
                print(f"   ❌ Tidak ada percobaan lagi tersisa")

            # Print stack trace for debugging
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print(f"❌ SEMUA PERCOBAAN GAGAL")
    print(f"{'='*60}")
    print(f"   User: @{username}")
    print(f"   Total attempts: {max_attempts}")
    print(f"   Status: FAILED")
    print(f"{'='*60}")
    return False

def search_users_interactive(driver):
    """Interactive search loop untuk mencari multiple users"""
    print("\n" + "="*60)
    print("🔍 MODE PENCARIAN PROFIL TIKTOK")
    print("="*60)
    print("\n💡 Instruksi:")
    print("   - Ketik username (tanpa @) untuk mencari")
    print("   - Ketik 'exit' atau 'quit' untuk keluar")
    print("   - Ketik 'clear' untuk clear screen")
    print("="*60)

    search_count = 0

    while True:
        try:
            username_input = input("\n👤 Username: ").strip()

            if not username_input:
                continue

            # Check for exit commands
            if username_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Keluar dari mode pencarian...")
                break

            # Check for clear command
            if username_input.lower() == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n" + "="*60)
                print("🔍 MODE PENCARIAN PROFIL TIKTOK")
                print("="*60)
                continue

            # Remove @ if user includes it
            username = username_input.lstrip('@')

            if not username:
                print("❌ Username tidak valid!")
                continue

            # Scrape the profile
            stats = scrape_user_profile(driver, username)

            if stats:
                search_count += 1
                print("\n" + "="*60)
                print(f"✅ DATA PROFIL - @{stats['username']}")
                print("="*60)
                print(f"👥 Followers   : {stats['followers']}")
                print(f"➕ Following   : {stats['following']}")
                print(f"❤️  Likes       : {stats['likes']}")
                print("="*60)
                print(f"🔗 URL         : https://www.tiktok.com/@{username}")
                print(f"📊 Total search: {search_count}")
                print("="*60)

                # Now try to report with retry mechanism
                report_success = report_user_with_retry(driver, username, max_attempts=3)

                if report_success:
                    print("="*60)
                    print("✅ BERHASIL melaporkan user!")
                    print("="*60)
                else:
                    print("="*60)
                    print("❌ GAGAL melaporkan user setelah beberapa percobaan")
                    print("="*60)
            else:
                print("\n⚠️  Gagal mengambil data profil")

        except KeyboardInterrupt:
            print("\n\n⚠️  Pencarian dibatalkan (Ctrl+C)")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

    print(f"\n✓ Selesai! Total profil yang berhasil dicari: {search_count}")

def read_account():
    """Baca akun dari file akun.txt"""
    try:
        with open('akun.txt', 'r') as f:
            lines = f.read().strip().split('\n')
            if len(lines) >= 2:
                email = lines[0].strip()
                password = lines[1].strip()
                return email, password
            else:
                print("❌ Format akun.txt salah!")
                print("Format yang benar:")
                print("baris 1: email")
                print("baris 2: password")
                return None, None
    except FileNotFoundError:
        print("❌ File akun.txt tidak ditemukan!")
        print("Buat file akun.txt dengan format:")
        print("baris 1: email")
        print("baris 2: password")
        return None, None


def check_for_captcha(driver):
    """
    Check if CAPTCHA is present on the page (STRICT detection to avoid false positives)
    Returns dict with captcha info if found, None otherwise
    """
    try:
        page_source = driver.page_source

        # CRITICAL: STRICT CAPTCHA detection - need VISIBLE modal/container!
        # Check for actual CAPTCHA modal/container being displayed
        try:
            # Look for VISIBLE CAPTCHA elements
            captcha_modals = driver.find_elements(By.CSS_SELECTOR,
                '[class*="captcha"][style*="display"], [id*="captcha"][style*="display"], '
                '[class*="TUXModal"][class*="captcha"], '
                '.secsdk-captcha-drag-icon')

            visible_captcha = False
            for modal in captcha_modals:
                if modal.is_displayed():
                    visible_captcha = True
                    break

            if not visible_captcha:
                # No visible CAPTCHA modal found
                return None

        except:
            # If we can't find visible elements, it's probably not a CAPTCHA
            return None

        # ADDITIONAL CHECK: Must have CAPTCHA-specific elements
        captcha_specific = [
            'secsdk-captcha',
            'captcha-verify-container',
            'captcha_slide_button',
            'TUXModal captcha',
            'captcha-verify-container-main',
        ]

        has_specific = False
        for specific in captcha_specific:
            if specific in page_source:
                has_specific = True
                break

        if not has_specific:
            # Generic keywords found but no actual CAPTCHA elements
            return None

        # If we reach here, CAPTCHA is REALLY present!
        print("\n" + "="*60)
        print("🤖 CAPTCHA TERDETEKSI!")
        print("="*60)

        # Extract CAPTCHA details
        captcha_info = {
            'detected': True,
            'type': 'unknown',
            'captcha_service': 'unknown',
            'url': driver.current_url,
            '2captcha_method': None,
        }

        # DEEP ANALYSIS: Check all known CAPTCHA services
        print("\n🔍 DEEP CAPTCHA ANALYSIS:")
        print("-" * 60)

        # Check for specific CAPTCHA providers
        captcha_services = {
            'recaptcha': ['recaptcha', 'g-recaptcha', 'grecaptcha'],
            'hcaptcha': ['hcaptcha', 'h-captcha'],
            'funcaptcha': ['funcaptcha', 'arkose', 'fc-token'],
            'geetest': ['geetest', 'gt-captcha', 'gt_'],
            'turnstile': ['turnstile', 'cf-turnstile', 'cloudflare'],
            'mtcaptcha': ['mtcaptcha', 'mtcaptcha.com'],
            'datadome': ['datadome', 'dd_captcha'],
            'rotate': ['rotate', 'rotation', 'secsdk-captcha-drag-icon'],
            'slide': ['slide', 'slider', 'puzzle', 'jigsaw'],
        }

        detected_services = []
        for service, keywords in captcha_services.items():
            for keyword in keywords:
                if keyword.lower() in page_source.lower():
                    detected_services.append(service)
                    break

        if detected_services:
            print(f"✓ Detected services: {', '.join(detected_services)}")
            captcha_info['captcha_service'] = detected_services[0]
        else:
            print("⚠️  Unknown CAPTCHA service")

        # Determine 2Captcha method based on detected service
        if 'rotate' in detected_services:
            captcha_info['type'] = 'RotateCaptcha'
            captcha_info['2captcha_method'] = 'rotate'
            print("\n📋 CAPTCHA Type: ROTATE CAPTCHA")
            print("🔧 2Captcha Method: 'rotate'")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_rotatecaptcha")

        elif 'slide' in detected_services or 'secsdk-captcha' in page_source:
            captcha_info['type'] = 'RotateCaptcha'  # TikTok slide is actually rotate-based
            captcha_info['2captcha_method'] = 'rotate'
            print("\n📋 CAPTCHA Type: SLIDE/ROTATE PUZZLE (TikTok Style)")
            print("🔧 2Captcha Method: 'rotate'")
            print("💡 Note: TikTok's slide puzzle uses rotation mechanics")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_rotatecaptcha")

        elif 'recaptcha' in detected_services:
            if 'recaptcha/enterprise' in page_source.lower():
                captcha_info['type'] = 'ReCaptchaEnterprise'
                captcha_info['2captcha_method'] = 'userrecaptcha'
                print("\n📋 CAPTCHA Type: reCAPTCHA Enterprise")
            elif 'recaptcha/api2' in page_source.lower() or 'g-recaptcha' in page_source.lower():
                captcha_info['type'] = 'ReCaptchaV2'
                captcha_info['2captcha_method'] = 'userrecaptcha'
                print("\n📋 CAPTCHA Type: reCAPTCHA V2")
            else:
                captcha_info['type'] = 'ReCaptchaV3'
                captcha_info['2captcha_method'] = 'userrecaptcha'
                print("\n📋 CAPTCHA Type: reCAPTCHA V3")
            print("🔧 2Captcha Method: 'userrecaptcha'")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_recaptchav2_new")

        elif 'hcaptcha' in detected_services:
            captcha_info['type'] = 'HCaptcha'
            captcha_info['2captcha_method'] = 'hcaptcha'
            print("\n📋 CAPTCHA Type: hCaptcha")
            print("🔧 2Captcha Method: 'hcaptcha'")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_hcaptcha")

        elif 'funcaptcha' in detected_services:
            captcha_info['type'] = 'FunCaptcha'
            captcha_info['2captcha_method'] = 'funcaptcha'
            print("\n📋 CAPTCHA Type: FunCaptcha (Arkose Labs)")
            print("🔧 2Captcha Method: 'funcaptcha'")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_funcaptcha_new")

        elif 'geetest' in detected_services:
            captcha_info['type'] = 'GeeTest'
            captcha_info['2captcha_method'] = 'geetest'
            print("\n📋 CAPTCHA Type: GeeTest")
            print("🔧 2Captcha Method: 'geetest'")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_geetest")

        elif 'turnstile' in detected_services:
            captcha_info['type'] = 'Turnstile'
            captcha_info['2captcha_method'] = 'turnstile'
            print("\n📋 CAPTCHA Type: Cloudflare Turnstile")
            print("🔧 2Captcha Method: 'turnstile'")
            print("📖 Docs: https://2captcha.com/2captcha-api#turnstile")

        else:
            # Default to rotate for TikTok
            captcha_info['type'] = 'RotateCaptcha'
            captcha_info['2captcha_method'] = 'rotate'
            print("\n📋 CAPTCHA Type: UNKNOWN (defaulting to Rotate)")
            print("🔧 2Captcha Method: 'rotate' (best guess)")
            print("📖 Docs: https://2captcha.com/2captcha-api#solving_rotatecaptcha")

        print("-" * 60)

        # Try to extract CAPTCHA images
        try:
            images = driver.find_elements(By.CSS_SELECTOR, 'img[src*="data:image"]')
            if images:
                print(f"🖼️  Found {len(images)} CAPTCHA images")
                for i, img in enumerate(images[:3]):  # Max 3 images
                    src = img.get_attribute('src')
                    if src and src.startswith('data:image'):
                        img_type = 'webp' if 'webp' in src else 'png' if 'png' in src else 'jpg'
                        img_size = len(src)
                        print(f"   Image {i+1}: {img_type.upper()}, size: ~{img_size//1000}KB")
                        captcha_info[f'image_{i+1}'] = src[:100] + '...'  # Store first 100 chars
        except Exception as e:
            print(f"   ⚠️  Could not extract images: {e}")

        # Try to find CAPTCHA container
        try:
            captcha_containers = driver.find_elements(By.CSS_SELECTOR,
                '[class*="captcha"], [id*="captcha"], [data-e2e*="captcha"]')
            if captcha_containers:
                print(f"📦 Found {len(captcha_containers)} CAPTCHA container(s)")

                # Get container HTML for analysis
                for i, container in enumerate(captcha_containers[:1]):  # First container
                    try:
                        html = container.get_attribute('outerHTML')
                        if html:
                            # Extract useful info
                            if 'secsdk-captcha' in html:
                                print("   ✓ SecSDK CAPTCHA detected")
                                captcha_info['sdk'] = 'secsdk'
                            if 'captcha_slide_button' in html:
                                print("   ✓ Slide button found")
                            if 'captcha_refresh_button' in html:
                                print("   ✓ Refresh button found")

                            # Look for CAPTCHA ID/token
                            import re
                            token_match = re.search(r'[0-9A-F]{32,}', html)
                            if token_match:
                                token = token_match.group(0)
                                print(f"   🔑 Token/ID: {token[:20]}...")
                                captcha_info['token'] = token
                    except:
                        pass
        except Exception as e:
            print(f"   ⚠️  Could not analyze container: {e}")

        # Save page source for deep analysis
        try:
            import os
            dump_dir = "captcha_dumps"
            os.makedirs(dump_dir, exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            html_file = f"{dump_dir}/captcha_{timestamp}.html"

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)

            print(f"\n💾 Page source saved: {html_file}")
            print("   Use this file to analyze CAPTCHA structure!")
            captcha_info['html_dump'] = html_file
        except Exception as e:
            print(f"   ⚠️  Could not save page source: {e}")

        print("\n💡 CAPTCHA Solution Options:")
        print("   1. Manual solve (pause script, solve by hand)")
        print("   2. 2Captcha service ($2.99/1000 solves)")
        print("   3. CapSolver service (~$1/1000 solves)")
        print("   4. Anti-Captcha service (~$2/1000 solves)")
        print("\n📚 Integration guides:")
        print("   - 2Captcha: https://2captcha.com/2captcha-api")
        print("   - CapSolver: https://www.capsolver.com/")

        print("\n📄 Captcha Info (for API integration):")
        info_copy = captcha_info.copy()
        if 'html_dump' in info_copy:
            del info_copy['html_dump']  # Don't print file path in JSON
        print(json.dumps(info_copy, indent=2))

        print("\n🔑 YOUR 2CAPTCHA API KEY:")
        print("   0ffd29027a459d20ee4085a8b9b8b055")
        print("="*60)

        return captcha_info

        return None

    except Exception as e:
        print(f"   ⚠️  Error checking CAPTCHA: {e}")
        return None

def check_for_errors(driver):
    """
    Check for TikTok error messages (rate limit, login failed, etc.)
    ONLY checks for VISIBLE/REAL errors, NOT keywords in page source!
    IGNORES: Privacy modals, notifications, success pages
    Returns dict with error info if found, None otherwise
    """
    try:
        page_source = driver.page_source
        current_url = driver.current_url

        # CRITICAL: If we're on SUCCESS pages, NO ERROR!
        success_urls = ['/foryou', '/following', '/explore', '/@']
        if any(url_part in current_url for url_part in success_urls):
            return None  # On main TikTok page - logged in!

        # CRITICAL: Check if we're on OTP page
        try:
            otp_input = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][maxlength="6"], input[placeholder*="code"], input[placeholder*="kode"]')
            if otp_input and any(elem.is_displayed() for elem in otp_input):
                return None  # On OTP page - not an error!
        except:
            pass

        # STEP 1: Check for VISIBLE error elements (but SKIP modals/notifications!)
        try:
            error_selectors = [
                '[class*="error-message"]',
                '[class*="Error"]',
                '[data-e2e*="error"]',
                '.toast-error',
                '[role="alert"]',
            ]

            # Keywords to IGNORE (not real errors)
            ignore_keywords = [
                'privacy',
                'kebijakan privasi',
                'pembaruan kebijakan',
                'policy update',
                'mengerti',
                'understand',
                'notification',
                'notifikasi',
                'cookie',
            ]

            for selector in error_selectors:
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in error_elements:
                        if elem.is_displayed():
                            error_text = elem.text.strip()

                            # Skip if too short or empty
                            if not error_text or len(error_text) < 10:
                                continue

                            # CRITICAL: Check if this is just a notification/modal
                            error_lower = error_text.lower()
                            is_notification = any(keyword in error_lower for keyword in ignore_keywords)

                            if is_notification:
                                continue  # Skip privacy/notification modals

                            # REAL ERROR FOUND!
                            print("\n" + "="*60)
                            print("❌ VISIBLE ERROR ON PAGE!")
                            print("="*60)
                            print(f"📝 Error: {error_text}")
                            print(f"🌐 URL: {current_url}")

                            if "frekuensi" in error_lower or "frequent" in error_lower:
                                print("\n⚠️  RATE LIMIT ERROR!")
                                print("💡 Solusi:")
                                print("   1. Wait 5-10 minutes")
                                print("   2. Clear cookies")
                                print("   3. Change IP (VPN)")

                            print("="*60)
                            return {
                                'detected': True,
                                'error_code': 'visible_error',
                                'description': error_text,
                                'url': current_url,
                            }
                except:
                    continue
        except:
            pass

        # STEP 2: Check for JSON error ONLY if error_code = 7 (rate limit)
        import re
        if '"error_code"' in page_source and '"message":"error"' in page_source:
            code_match = re.search(r'"error_code"\s*:\s*(\d+)', page_source)
            desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', page_source)

            if code_match and desc_match:
                error_code = code_match.group(1)
                description = desc_match.group(1)

                # ONLY return error if it's code 7 (rate limit)
                if error_code == "7":
                    print("\n" + "="*60)
                    print("❌ RATE LIMIT ERROR (API)")
                    print("="*60)
                    print(f"🔴 Error Code: {error_code}")
                    print(f"📝 Description: {description}")
                    print(f"🌐 URL: {current_url}")
                    print("\n💡 Solusi:")
                    print("   1. Wait 5-10 minutes")
                    print("   2. Clear cookies")
                    print("   3. Change IP (VPN)")
                    print("="*60)

                    return {
                        'detected': True,
                        'error_code': error_code,
                        'description': description,
                        'url': current_url,
                    }

        # No real error detected
        return None

    except Exception as e:
        print(f"⚠️  Error checking for errors: {e}")
        return None


def check_for_otp(driver):
    """Cek apakah halaman OTP muncul dengan parsing yang lebih akurat"""
    try:
        current_url = driver.current_url

        # CRITICAL: If we have valid session cookies, we're DEFINITELY logged in (not OTP!)
        try:
            cookies = driver.get_cookies()
            session_cookies = []
            for cookie in cookies:
                if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard', 'sessionid_ss']:
                    value = cookie.get('value', '')
                    if value and len(value) > 10:  # Session cookie should be long
                        session_cookies.append(cookie.get('name'))

            # If we have at least 2 valid session cookies, login is successful (NOT OTP!)
            if len(session_cookies) >= 2:
                return False  # No OTP needed - already logged in!
        except:
            pass

        # IMPORTANT: If we're NOT on login page, we're definitely NOT on OTP page!
        if '/login' not in current_url:
            return False

        # CRITICAL: Force viewport refresh to ensure page is fully loaded
        try:
            driver.execute_script("window.scrollBy(0, 1);")
            time.sleep(0.5)
        except:
            pass

        page_source = driver.page_source.lower()

        # Cek URL pattern untuk OTP
        if 'verify' in current_url or 'otp' in current_url or 'code' in current_url:
            return True

        # Cek text indikator OTP di halaman dengan STRICT matching
        otp_keywords = [
            'enter code',
            'enter the code',
            'masukkan kode',
            'verification code',
            'kode verifikasi',
            'aktivitas mencurigakan',
            'suspicious activity'
        ]

        # Count matches - need at least 2 keywords for confidence
        matches = 0
        for keyword in otp_keywords:
            if keyword in page_source:
                matches += 1

        if matches >= 2:  # Need multiple indicators to confirm OTP
            return True

        # Cek apakah ada input field untuk OTP dengan STRICT validation
        try:
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][maxlength="1"], input[placeholder*="code" i], input[placeholder*="digit" i]')
            visible_inputs = [inp for inp in otp_inputs if inp.is_displayed()]

            # Need at least 3 single-digit inputs or 1 code input
            if len(visible_inputs) >= 3:
                return True
        except:
            pass

        return False
    except:
        return False

def is_login_successful(driver):
    """Cek apakah login berhasil dengan parsing URL dan cookies"""
    try:
        current_url = driver.current_url
        print(f"   🔍 Checking URL: {current_url}")

        # Method 1: Cek cookies untuk validasi (MOST RELIABLE - check this first!)
        try:
            cookies = driver.get_cookies()
            session_cookies = []
            for cookie in cookies:
                if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard', 'sessionid_ss', 'tt_csrf_token', 'odin_tt']:
                    value = cookie.get('value', '')
                    if value and len(value) > 10:  # Session cookie should be long
                        session_cookies.append(cookie.get('name'))

            if len(session_cookies) >= 2:  # Need at least 2 session cookies for valid login
                print(f"   ✓ Session cookies found: {', '.join(session_cookies)}")
                return True
        except:
            pass

        # Method 2: Cek pattern URL yang menandakan sudah login
        success_patterns = [
            'foryou',
            'following',
            'tiktok.com/@',
            '/explore',
            '/live'
        ]

        for pattern in success_patterns:
            if pattern in current_url:
                print(f"   ✓ Success pattern found: {pattern}")
                return True

        # Method 3: Jika URL adalah homepage (just tiktok.com or tiktok.com/?lang=xx)
        # WITHOUT /login or /phone-or-email
        if 'tiktok.com' in current_url:
            # Check it's NOT a login page
            if '/login' not in current_url and '/phone-or-email' not in current_url and '/email' not in current_url:
                # Check if it's homepage-like
                clean_url = current_url.split('?')[0]  # Remove query params
                if clean_url.rstrip('/').endswith('tiktok.com') or '/foryou' in current_url:
                    print(f"   ✓ On homepage (not login page)")
                    return True

        print(f"   ✗ Login not detected")
        return False
    except Exception as e:
        print(f"   ✗ Error checking login: {e}")
        return False

def tiktok_login():
    print("🚀 Memulai TikTok Login Bot v4...")
    print("📋 Fitur: Browser visible, Manual close untuk debugging\n")

    # Baca akun
    email, password = read_account()
    if not email or not password:
        return

    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)}\n")

    # Setup Chrome dengan visible mode untuk debugging
    print("🌐 Membuka browser (visible mode)...")
    options = uc.ChromeOptions()
    # Remove headless - browser akan terlihat
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-background-timer-throttling')  # Prevent throttling
    options.add_argument('--disable-backgrounding-occluded-windows')  # Keep active in background
    options.add_argument('--disable-renderer-backgrounding')  # Prevent renderer from sleeping
    options.add_argument('--disable-features=CalculateNativeWinOcclusion')  # Prevent window occlusion detection
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        driver = uc.Chrome(options=options)

        # Set consistent window size for ALL pages
        print("📐 Setting consistent window size: 1920x1080...")
        driver.set_window_size(1920, 1080)
        driver.maximize_window()
        print("   ✓ Window size set and maximized")

    except Exception as e:
        print(f"❌ Gagal membuat driver: {e}")
        return

    wait = WebDriverWait(driver, 15)

    try:
        # Buka halaman login
        print("📱 Membuka halaman login TikTok...")
        driver.get('https://www.tiktok.com/login/phone-or-email/email')

        # CRITICAL: Ensure window focus for form rendering
        print("🔍 Ensuring page is fully loaded...")
        ensure_window_focus(driver)
        time.sleep(3)

        # Input email with retry mechanism
        print(f"📝 Mengisi email...")
        email_filled = False
        for attempt in range(5):  # Increased to 5 attempts
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt}/5 - Refreshing viewport...")
                    ensure_window_focus(driver)
                    time.sleep(1.5)

                email_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"], input[type="text"]'))
                )

                # Wait for element to be interactive
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"], input[type="text"]')))

                # NUCLEAR OPTION: Try 3 different methods
                success = False

                # Method 1: Regular send_keys (works in foreground)
                if attempt < 2:
                    try:
                        email_input.clear()
                        time.sleep(0.3)
                        # Click first to ensure focus
                        email_input.click()
                        time.sleep(0.3)
                        for char in email:
                            email_input.send_keys(char)
                            time.sleep(0.08)

                        # Verify
                        if email_input.get_attribute('value'):
                            success = True
                    except:
                        pass

                # Method 2: JavaScript setValue (works in background!)
                if not success and attempt >= 2:
                    try:
                        print(f"   🔧 Using JavaScript injection method...")
                        # Use JS to set value directly
                        driver.execute_script(f"""
                            const input = document.querySelector('input[name="username"], input[type="text"]');
                            if (input) {{
                                input.value = '{email}';
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        """)
                        time.sleep(0.5)

                        # Verify
                        if email_input.get_attribute('value'):
                            success = True
                    except Exception as e:
                        print(f"   ⚠️  JS method failed: {e}")

                # Method 3: Hybrid - click + JS
                if not success:
                    try:
                        print(f"   🔧 Using hybrid click+JS method...")
                        email_input.click()
                        time.sleep(0.2)
                        driver.execute_script(f"arguments[0].value = '{email}';", email_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", email_input)
                        time.sleep(0.3)

                        # Verify
                        if email_input.get_attribute('value'):
                            success = True
                    except:
                        pass

                if success:
                    print(f"   ✅ Email berhasil diisi!")
                    email_filled = True
                    break
                else:
                    print(f"   ⚠️  Email field masih kosong, retry...")

            except TimeoutException:
                if attempt < 4:
                    print(f"   ⚠️  Timeout attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Timeout saat mencari input email setelah 5 percobaan!")
                    return

        if not email_filled:
            print("❌ Gagal mengisi email setelah 5 percobaan!")
            return

        time.sleep(1)

        # Input password with retry mechanism
        print(f"🔐 Mengisi password...")
        password_filled = False
        for attempt in range(5):  # Increased to 5 attempts
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt}/5 - Refreshing viewport...")
                    driver.execute_script("window.scrollBy(0, 50); setTimeout(() => window.scrollBy(0, -50), 100);")
                    time.sleep(1.5)

                password_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                )

                # Wait for element to be interactive
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))

                # NUCLEAR OPTION: Try 3 different methods
                success = False

                # Method 1: Regular send_keys (works in foreground)
                if attempt < 2:
                    try:
                        password_input.clear()
                        time.sleep(0.3)
                        password_input.click()
                        time.sleep(0.3)
                        for char in password:
                            password_input.send_keys(char)
                            time.sleep(0.08)

                        # Verify
                        if password_input.get_attribute('value'):
                            success = True
                    except:
                        pass

                # Method 2: JavaScript setValue (works in background!)
                if not success and attempt >= 2:
                    try:
                        print(f"   🔧 Using JavaScript injection method...")
                        driver.execute_script(f"""
                            const input = document.querySelector('input[type="password"]');
                            if (input) {{
                                input.value = '{password}';
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        """)
                        time.sleep(0.5)

                        # Verify
                        if password_input.get_attribute('value'):
                            success = True
                    except Exception as e:
                        print(f"   ⚠️  JS method failed: {e}")

                # Method 3: Hybrid - click + JS
                if not success:
                    try:
                        print(f"   🔧 Using hybrid click+JS method...")
                        password_input.click()
                        time.sleep(0.2)
                        driver.execute_script(f"arguments[0].value = '{password}';", password_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", password_input)
                        time.sleep(0.3)

                        # Verify
                        if password_input.get_attribute('value'):
                            success = True
                    except:
                        pass

                if success:
                    print(f"   ✅ Password berhasil diisi!")
                    password_filled = True
                    break
                else:
                    print(f"   ⚠️  Password field masih kosong, retry...")

            except (NoSuchElementException, TimeoutException):
                if attempt < 4:
                    print(f"   ⚠️  Error attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Input password tidak ditemukan setelah 5 percobaan!")
                    return

        if not password_filled:
            print("❌ Gagal mengisi password setelah 5 percobaan!")
            return

        time.sleep(1)

        # Klik tombol login - wait for it to be ENABLED and CLICKABLE with retry
        print("🖱️  Menunggu tombol login aktif...")
        login_clicked = False
        for attempt in range(5):  # Try up to 5 times
            try:
                # CRITICAL: Keep session alive during wait
                keep_session_alive(driver)

                if attempt > 0:
                    print(f"   🔄 Retry {attempt}/5 - Checking login button...")
                    # Trigger viewport refresh AND keep alive
                    ensure_window_focus(driver)
                    time.sleep(1)

                # Keep session alive before wait
                keep_session_alive(driver)

                # Wait for button to be clickable (not disabled)
                login_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]:not([disabled]), button[data-e2e="login-button"]:not([disabled])'))
                )

                # Keep alive after finding button
                keep_session_alive(driver)

                # Verify button is really enabled
                is_disabled = login_button.get_attribute('disabled')
                if is_disabled:
                    print(f"   ⚠️  Button still disabled on attempt {attempt + 1}")
                    if attempt < 4:
                        keep_session_alive(driver)
                        time.sleep(2)
                        continue
                    else:
                        print("❌ Tombol login masih disabled setelah 5 percobaan!")
                        return

                print("🖱️  Klik tombol login...")
                keep_session_alive(driver)
                time.sleep(0.5)  # Small delay before click
                login_button.click()
                login_clicked = True
                print("   ✅ Login button clicked!")
                break

            except TimeoutException:
                keep_session_alive(driver)
                if attempt < 4:
                    print(f"   ⚠️  Timeout attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Tombol login tidak ditemukan setelah 5 percobaan!")
                    return
            except NoSuchElementException:
                keep_session_alive(driver)
                if attempt < 4:
                    print(f"   ⚠️  Button not found attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Tombol login tidak ditemukan!")
                    return
            except Exception as e:
                # Catch session disconnect
                if "invalid session" in str(e).lower() or "disconnected" in str(e).lower():
                    print(f"   ⚠️  Session lost on attempt {attempt + 1}, trying to recover...")
                    if attempt < 4:
                        try:
                            # Try to reconnect
                            driver.switch_to.window(driver.current_window_handle)
                            time.sleep(2)
                            continue
                        except:
                            print("❌ Cannot recover session!")
                            return
                raise

        if not login_clicked:
            print("❌ Gagal mengklik tombol login setelah 5 percobaan!")
            return

        print("⏳ Menunggu respons dari TikTok (redirect bisa memakan waktu)...")
        time.sleep(8)  # CRITICAL: Wait for TikTok redirect to complete

        # Cek kondisi: CAPTCHA, OTP, atau langsung berhasil
        max_checks = 25
        otp_detected = False
        captcha_detected = False
        error_detected = False

        for i in range(max_checks):
            # Give page time to stabilize between checks
            if i > 0:
                time.sleep(2)

            # Cek apakah sudah berhasil login
            if is_login_successful(driver):
                print("\n" + "="*60)
                print("✅ BERHASIL LOGIN!")
                print("="*60)
                print(f"🎉 URL: {driver.current_url}")

                # Ambil dan print cookies
                cookies = driver.get_cookies()
                print(f"\n🍪 Session cookies tersimpan: {len(cookies)} cookies")

                # Cari sessionid untuk validasi
                session_found = False
                for cookie in cookies:
                    if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard']:
                        session_found = True
                        print(f"   ✓ {cookie.get('name')}: {cookie.get('value')[:20]}...")

                if session_found:
                    print("\n✓ Session valid - Login berhasil tanpa verifikasi tambahan")

                print("\n" + "="*60)
                print("🎉 Browser tetap terbuka - Anda bisa inspect langsung")
                print("="*60)
                print("\n💡 Mode debugging:")
                print("   - Browser akan tetap terbuka")
                print("   - Anda bisa lihat halaman TikTok")
                print("   - Session cookies tersimpan")
                print("\n⏸️  Tekan ENTER untuk mulai mode search, atau close browser manual...")
                input()

                # Start interactive search mode
                search_users_interactive(driver)
                return

            # PRIORITY 0: Check for ERRORS FIRST! (Rate limit, login failed, etc.)
            error_info = check_for_errors(driver)
            if error_info:
                error_detected = True
                break

            # PRIORITY 1: Check for OTP (OTP page has generic keywords that trigger false CAPTCHA)
            if check_for_otp(driver):
                otp_detected = True
                break

            # PRIORITY 2: Check for CAPTCHA (only if not OTP or error)
            captcha_info = check_for_captcha(driver)
            if captcha_info:
                captcha_detected = True
                break

            time.sleep(1)

        # Handle ERROR (highest priority!)
        if error_detected:
            print("\n⛔ ERROR DETECTED - Cannot proceed with login")
            print("💡 Please check the error message above and take action")
            print(f"📄 Error info: {error_info}")
            print("\n⏸️  Browser will stay open for inspection...")
            print("   Tekan ENTER untuk close browser...")
            try:
                input()
            except KeyboardInterrupt:
                pass
            return

        # Handle CAPTCHA
        if captcha_detected:
            print("\n⏸️  CAPTCHA harus diselesaikan sebelum melanjutkan!")
            print("💡 Opsi:")
            print("   1. Solve manual di browser (script akan pause)")
            print("   2. Integrate dengan CAPTCHA solver service")
            print("\n⏸️  Tekan ENTER setelah CAPTCHA selesai (atau Ctrl+C untuk exit)...")
            try:
                input()
                print("\n✓ Melanjutkan setelah CAPTCHA solve...")

                # Re-check if we're now logged in or need OTP
                time.sleep(3)
                if is_logged_in(driver):
                    print("\n✅ Login berhasil setelah CAPTCHA solve!")
                    # Continue to success flow
                    otp_detected = False
                elif check_for_otp(driver):
                    print("\n📬 OTP verification diperlukan setelah CAPTCHA...")
                    otp_detected = True
                else:
                    print("\n⚠️  Status tidak jelas, silakan cek browser")
                    return
            except KeyboardInterrupt:
                print("\n❌ Script dibatalkan oleh user")
                return

        # Handle OTP
        if otp_detected and not captcha_detected:
            print("\n" + "="*60)
            print("📬 VERIFIKASI OTP DIPERLUKAN")
            print("="*60)

            # Parse informasi dari halaman
            try:
                page_source = driver.page_source

                # Deteksi alasan verifikasi
                if 'mencurigakan' in page_source.lower() or 'suspicious' in page_source.lower():
                    print("⚠️  Alasan: Aktivitas mencurigakan terdeteksi")

                # Cari email tujuan OTP dengan regex
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                masked_emails = re.findall(r'\w[*]+\w+@[\w.]+', page_source)

                if masked_emails:
                    print(f"📧 Kode OTP dikirim ke: {masked_emails[0]}")
                elif email:
                    # Tampilkan email yang digunakan untuk login
                    masked = f"{email[:2]}***{email[-10:]}" if len(email) > 12 else f"{email[0]}***{email[-5:]}"
                    print(f"📧 Kode OTP dikirim ke: {masked}")

                print(f"🌐 Current URL: {driver.current_url}")
            except:
                pass

            print("="*60)

            # Input OTP dari terminal
            otp_code = input("\n🔢 Masukkan kode OTP (6 digit): ").strip()

            if len(otp_code) != 6 or not otp_code.isdigit():
                print("❌ Kode OTP harus 6 digit angka!")
                input("\n⏸️  Tekan ENTER untuk close browser...")
                return

            # Cari input OTP dan isi
            print("\n📝 Mengisi kode OTP ke form...")
            try:
                # Tunggu form OTP muncul
                time.sleep(2)

                # Debug: print current page info
                print(f"   Current URL: {driver.current_url}")
                print(f"   Page title: {driver.title[:50]}")

                # Coba berbagai selector untuk input OTP - dari paling spesifik ke general
                otp_selectors = [
                    'input[placeholder*="code" i]',  # placeholder contains 'code'
                    'input[placeholder*="verification" i]',  # placeholder contains 'verification'
                    'input[placeholder*="otp" i]',  # placeholder contains 'otp'
                    'input[name*="code" i]',  # name contains 'code'
                    'input[autocomplete="one-time-code"]',  # OTP autocomplete
                    'input[type="tel"]',  # tel input
                    'input[inputmode="numeric"]',  # numeric input
                    'input[type="number"]',  # number input
                    'input[type="text"]',  # text input (fallback)
                ]

                all_otp_inputs = []
                for selector in otp_selectors:
                    try:
                        inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                        all_otp_inputs.extend(inputs)
                    except:
                        continue

                # Remove duplicates
                seen = set()
                unique_inputs = []
                for inp in all_otp_inputs:
                    elem_id = id(inp)
                    if elem_id not in seen:
                        seen.add(elem_id)
                        unique_inputs.append(inp)

                # Filter hanya input yang visible dan bukan password, dan bukan field email/username lama
                visible_inputs = []
                for inp in unique_inputs:
                    try:
                        if not inp.is_displayed():
                            continue

                        inp_type = inp.get_attribute('type')
                        inp_name = inp.get_attribute('name') or ''
                        inp_placeholder = inp.get_attribute('placeholder') or ''
                        inp_value = inp.get_attribute('value') or ''

                        # Skip password fields
                        if inp_type == 'password':
                            continue

                        # Skip email/username fields (yang sudah terisi atau placeholder nya email)
                        if inp_name in ['username', 'email']:
                            continue

                        if 'email' in inp_placeholder.lower() or 'username' in inp_placeholder.lower():
                            continue

                        # Skip if already filled with email
                        if '@' in inp_value:
                            continue

                        # Only accept OTP-related fields
                        is_otp_field = (
                            'code' in inp_placeholder.lower() or
                            'kode' in inp_placeholder.lower() or
                            'digit' in inp_placeholder.lower() or
                            'verification' in inp_placeholder.lower() or
                            'verifikasi' in inp_placeholder.lower() or
                            inp_type in ['tel', 'number'] or
                            'otp' in inp_name.lower()
                        )

                        if is_otp_field:
                            visible_inputs.append(inp)

                    except:
                        continue

                print(f"   Ditemukan {len(visible_inputs)} visible input field(s)")

                # Debug: print info tentang setiap input
                if len(visible_inputs) > 0:
                    print(f"\n   📋 Detail input fields:")
                    for idx, inp in enumerate(visible_inputs[:10]):  # max 10 untuk debug
                        try:
                            inp_type = inp.get_attribute('type') or 'N/A'
                            inp_name = inp.get_attribute('name') or 'N/A'
                            inp_placeholder = inp.get_attribute('placeholder') or 'N/A'
                            inp_class = inp.get_attribute('class') or 'N/A'
                            print(f"   [{idx+1}] type={inp_type}, name={inp_name[:20]}, placeholder={inp_placeholder[:30]}")
                        except:
                            pass

                if len(visible_inputs) == 0:
                    print("\n❌ Tidak menemukan input field OTP!")
                    print("\n📸 Debug info:")
                    print(f"   Saving screenshot to: otp_page_debug.png")
                    try:
                        driver.save_screenshot('otp_page_debug.png')
                        print("   ✓ Screenshot saved")
                    except:
                        pass

                    # Print page source untuk debug (first 500 chars)
                    try:
                        page_text = driver.find_element(By.TAG_NAME, 'body').text
                        print(f"\n   Page content (first 300 chars):")
                        print(f"   {page_text[:300]}")
                    except:
                        pass

                    print("\n💡 Kemungkinan:")
                    print("   1. OTP form belum muncul (perlu tunggu lebih lama)")
                    print("   2. TikTok menggunakan form OTP yang berbeda")
                    print("   3. Verifikasi tidak melalui OTP input")

                    input("\n⏸️  Tekan ENTER untuk close browser...")
                    return

                if len(visible_inputs) == 1:
                    # Single input field (masukkan semua digit sekaligus)
                    visible_inputs[0].click()
                    time.sleep(0.2)
                    visible_inputs[0].clear()
                    time.sleep(0.2)

                    for i, char in enumerate(otp_code):
                        visible_inputs[0].send_keys(char)
                        time.sleep(0.15)
                        print(f"   ✓ Digit {i+1}/6 terisi")

                    print("\n✓ OTP berhasil dimasukkan (1 field)")

                elif len(visible_inputs) >= 6:
                    # 6 separate input fields
                    for i in range(6):
                        visible_inputs[i].click()
                        time.sleep(0.1)
                        visible_inputs[i].clear()
                        visible_inputs[i].send_keys(otp_code[i])
                        time.sleep(0.12)
                        print(f"   ✓ Digit {i+1}/6 terisi")

                    print("\n✓ OTP berhasil dimasukkan (6 fields)")
                else:
                    # Fallback: coba isi ke semua input yang ada
                    print(f"   Mengisi {len(visible_inputs)} fields...")
                    for i, inp in enumerate(visible_inputs):
                        if i < len(otp_code):
                            inp.click()
                            time.sleep(0.1)
                            inp.clear()
                            inp.send_keys(otp_code[i])
                            time.sleep(0.1)

                time.sleep(2)

                # Cek dan klik tombol submit jika ada
                print("\n🔍 Mencari tombol submit...")
                try:
                    # Berbagai selector untuk tombol submit
                    submit_selectors = [
                        'button.email-view-wrapper__button',  # Tombol "Berikutnya"
                        'button.twv-component-button',
                        'button[type="submit"]',
                        'button[data-e2e="verify-button"]',
                        'div[role="button"]'
                    ]

                    button_found = False
                    for selector in submit_selectors:
                        try:
                            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                            for btn in buttons:
                                if btn.is_displayed() and btn.is_enabled():
                                    btn_text = btn.text.strip()
                                    print(f"   📍 Found button: '{btn_text}'")
                                    btn.click()
                                    print(f"   ✓ Tombol submit diklik: '{btn_text}'")
                                    button_found = True
                                    break
                            if button_found:
                                break
                        except Exception as e:
                            continue

                    if not button_found:
                        print("   ⚠️  Tombol submit tidak ditemukan, mencoba auto-submit...")
                except:
                    print("   ℹ️  Auto-submit (error mencari tombol)")

                # Tunggu hasil dengan progress indicator
                print("\n⏳ Memproses verifikasi OTP...")
                for i in range(6):
                    time.sleep(1)
                    print(f"   {'▓' * (i+1)}{'░' * (5-i)} {i+1}/6")

                # Cek hasil login
                time.sleep(2)

                if is_login_successful(driver):
                    print("\n" + "="*60)
                    print("✅ BERHASIL LOGIN!")
                    print("="*60)
                    print(f"🎉 URL: {driver.current_url}")

                    # Ambil dan display cookies
                    cookies = driver.get_cookies()
                    print(f"\n🍪 Session cookies tersimpan: {len(cookies)} cookies")

                    session_found = False
                    for cookie in cookies:
                        if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard', 'sessionid_ss']:
                            session_found = True
                            value = cookie.get('value', '')
                            masked_value = f"{value[:15]}..." if len(value) > 15 else value
                            print(f"   ✓ {cookie.get('name')}: {masked_value}")

                    if session_found:
                        print("\n✓ Session aktif - Kamu berhasil login!")

                    print("\n" + "="*60)
                    print("🎉 Browser tetap terbuka - Anda bisa inspect langsung")
                    print("="*60)
                    print("\n💡 Mode debugging:")
                    print("   - Browser akan tetap terbuka")
                    print("   - Anda bisa lihat halaman TikTok")
                    print("   - Session cookies tersimpan")
                    print("\n⏸️  Tekan ENTER untuk mulai mode search, atau close browser manual...")
                    input()

                    # Start interactive search mode
                    search_users_interactive(driver)
                    return
                else:
                    # LOGIN BELUM SUKSES - Cek kondisi lain!
                    print("\n⏳ Login belum sukses setelah OTP, checking kondisi lain...")
                    time.sleep(2)

                    # RE-CHECK semua kondisi dengan loop
                    max_recheck = 15
                    post_otp_success = False

                    for i in range(max_recheck):
                        print(f"\n🔍 Re-check #{i+1}/{max_recheck}...")

                        # Priority 1: Check for errors
                        error_info = check_for_errors(driver)
                        if error_info:
                            print("\n❌ ERROR DETECTED after OTP!")
                            print(f"📄 Error: {error_info['description']}")
                            print("\n⏸️  Browser tetap terbuka untuk inspection...")
                            print("   Tekan ENTER untuk close...")
                            input()
                            return

                        # Priority 2: Check for CAPTCHA
                        captcha_info = check_for_captcha(driver)
                        if captcha_info:
                            print("\n" + "="*60)
                            print("🤖 CAPTCHA MUNCUL SETELAH OTP!")
                            print("="*60)
                            print("⏸️  CAPTCHA harus diselesaikan...")
                            print("\n💡 Opsi:")
                            print("   1. Solve manual di browser (script akan pause)")
                            print("   2. Integrate dengan CAPTCHA solver service")
                            print("\n⏸️  Tekan ENTER setelah CAPTCHA selesai...")
                            try:
                                input()
                                print("\n✓ Melanjutkan setelah CAPTCHA solve...")
                                time.sleep(3)
                                # Continue loop to re-check
                                continue
                            except KeyboardInterrupt:
                                print("\n❌ Dibatalkan")
                                return

                        # Priority 3: Check if login successful
                        if is_login_successful(driver):
                            print("\n✅ LOGIN BERHASIL setelah re-check!")
                            post_otp_success = True
                            break

                        # Priority 4: Check if still on OTP (wrong code)
                        if check_for_otp(driver):
                            print("⚠️  Masih di halaman OTP (kode mungkin salah)")
                            break

                        # Wait before next check
                        time.sleep(2)

                    # Handle hasil re-check
                    if post_otp_success:
                        print("\n" + "="*60)
                        print("✅ BERHASIL LOGIN! (after re-check)")
                        print("="*60)
                        print(f"🎉 URL: {driver.current_url}")

                        # Show cookies
                        cookies = driver.get_cookies()
                        print(f"\n🍪 Session cookies: {len(cookies)} cookies")
                        session_found = False
                        for cookie in cookies:
                            if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard']:
                                session_found = True
                                value = cookie.get('value', '')
                                masked = f"{value[:15]}..." if len(value) > 15 else value
                                print(f"   ✓ {cookie.get('name')}: {masked}")

                        if session_found:
                            print("\n✓ Session aktif!")

                        print("\n" + "="*60)
                        print("🎉 Browser tetap terbuka")
                        print("="*60)
                        print("\n⏸️  Tekan ENTER untuk mulai search mode...")
                        input()

                        # Start search mode
                        search_users_interactive(driver)
                        return

                    elif check_for_otp(driver):
                        print("\n" + "="*60)
                        print("❌ KODE OTP SALAH")
                        print("="*60)
                        print("⚠️  Masih di halaman verifikasi")
                        print("💡 Solusi:")
                        print("   - Kode OTP salah atau expired")
                        print("   - Jalankan ulang script, minta kode baru")
                        print("="*60)
                        print("\n⏸️  Browser tetap terbuka, tekan ENTER...")
                        input()
                    else:
                        print("\n" + "="*60)
                        print("⚠️  STATUS TIDAK JELAS")
                        print("="*60)
                        print(f"📍 URL: {driver.current_url}")
                        print("💡 Cek browser untuk lihat kondisi page")
                        print("="*60)
                        print("\n⏸️  Browser tetap terbuka, tekan ENTER...")
                        input()

            except Exception as e:
                print(f"\n❌ Error saat input OTP: {e}")
                input("\n⏸️  Tekan ENTER untuk close browser...")

        else:
            print("\n" + "="*60)
            print("⚠️  TIDAK TERDETEKSI OTP")
            print("="*60)
            print(f"📍 Current URL: {driver.current_url}")
            print("\n💡 Kemungkinan:")
            print("   1. Login berhasil tanpa verifikasi (cek cookies di atas)")
            print("   2. TikTok meminta verifikasi dengan cara lain")
            print("   3. Timeout menunggu respons dari TikTok")
            print("\n🔍 Debug info:")
            print(f"   - URL saat ini: {driver.current_url}")

            # Cek cookies untuk validasi
            cookies = driver.get_cookies()
            session_exists = any(c.get('name') in ['sessionid', 'sid_tt'] for c in cookies)
            print(f"   - Session cookie: {'✓ Ada' if session_exists else '✗ Tidak ada'}")
            print("="*60)
            print("\n🔍 Mode debugging - Browser tetap terbuka")
            print("💡 Anda bisa inspect halaman untuk cek masalahnya")
            print("\n⏸️  Tekan ENTER untuk close browser...")
            input()

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR TERJADI")
        print("="*60)
        print(f"⚠️  Error: {str(e)}")
        print("\n🔍 Stack trace:")
        import traceback
        traceback.print_exc()
        print("="*60)
        print("\n🔍 Mode debugging - Browser tetap terbuka")
        print("💡 Anda bisa inspect halaman untuk cek masalahnya")
        print("\n⏸️  Tekan ENTER untuk close browser...")
        input()

    finally:
        # Dalam mode v4, kita masih cleanup tapi lebih graceful
        if driver:
            try:
                driver.quit()
                print("\n✓ Browser ditutup")
            except Exception as e:
                error_msg = str(e).lower()
                if "invalid" not in error_msg and "handle" not in error_msg:
                    print(f"\n⚠️  Warning saat cleanup: {e}")
            driver = None

        print("\n👋 Selesai!")

if __name__ == "__main__":
    import warnings
    import sys

    # Suppress undetected_chromedriver destructor warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)

    # Redirect stderr temporarily to suppress OSError from destructor
    original_stderr = sys.stderr

    try:
        tiktok_login()
    finally:
        # Suppress any remaining errors during cleanup
        sys.stderr = open('nul' if sys.platform == 'win32' else '/dev/null', 'w')
        import time
        time.sleep(0.2)  # Give time for destructor to finish
        sys.stderr.close()
        sys.stderr = original_stderr
