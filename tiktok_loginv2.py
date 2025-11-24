import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
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

        # Buka halaman profile
        profile_url = f"https://www.tiktok.com/@{username}"
        driver.get(profile_url)
        time.sleep(3)

        # Check if profile exists
        page_source = driver.page_source.lower()
        if "couldn't find this account" in page_source or "tidak dapat menemukan" in page_source:
            print(f"❌ Akun @{username} tidak ditemukan!")
            return None

        print("✓ Profil ditemukan!")
        print("📊 Mengambil data...")

        # Wait for profile to load
        time.sleep(2)

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

        # Method 2: Try to extract from visible elements
        if stats['followers'] == 'N/A':
            try:
                # Find all strong tags that might contain numbers
                strong_elements = driver.find_elements(By.CSS_SELECTOR, 'strong[data-e2e="followers-count"], strong[data-e2e="following-count"], strong[data-e2e="likes-count"]')

                for elem in strong_elements:
                    data_e2e = elem.get_attribute('data-e2e')
                    value = elem.text.strip()

                    if data_e2e == 'followers-count':
                        stats['followers'] = value
                    elif data_e2e == 'following-count':
                        stats['following'] = value
                    elif data_e2e == 'likes-count':
                        stats['likes'] = value
            except:
                pass

        # Method 3: Try alternative selectors
        if stats['followers'] == 'N/A':
            try:
                # Look for numbers in specific containers
                containers = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-page"] strong, [class*="count"] strong')

                numbers = []
                for container in containers:
                    text = container.text.strip()
                    # Check if it's a number or formatted number (like 1.2M, 10K, etc)
                    if re.match(r'^[\d.,]+[KMB]?$', text, re.IGNORECASE):
                        numbers.append(text)

                # Usually the order is: Following, Followers, Likes
                if len(numbers) >= 3:
                    stats['following'] = numbers[0]
                    stats['followers'] = numbers[1]
                    stats['likes'] = numbers[2]
                elif len(numbers) == 2:
                    stats['followers'] = numbers[0]
                    stats['following'] = numbers[1]
            except:
                pass

        return stats

    except Exception as e:
        print(f"❌ Error saat scraping profil: {e}")
        return None

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
                print(f"✅ PROFIL DITEMUKAN - @{stats['username']}")
                print("="*60)
                print(f"👥 Followers  : {stats['followers']}")
                print(f"➕ Following  : {stats['following']}")
                print(f"❤️  Likes      : {stats['likes']}")
                print("="*60)
                print(f"🔗 URL: https://www.tiktok.com/@{username}")
                print(f"📊 Total pencarian: {search_count}")
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


def check_for_otp(driver):
    """Cek apakah halaman OTP muncul dengan parsing yang lebih akurat"""
    try:
        page_source = driver.page_source.lower()
        current_url = driver.current_url

        # Cek URL pattern untuk OTP
        if 'verify' in current_url or 'otp' in current_url or 'code' in current_url:
            return True

        # Cek text indikator OTP di halaman
        otp_keywords = [
            'enter code',
            'masukkan kode',
            'verification code',
            'kode verifikasi',
            'aktivitas mencurigakan',
            'suspicious activity',
            '6 digit',
            'sent to',
            'dikirim ke'
        ]

        for keyword in otp_keywords:
            if keyword in page_source:
                return True

        # Cek apakah ada input field untuk OTP
        try:
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
            visible_inputs = [inp for inp in otp_inputs if inp.is_displayed()]

            # Jika ada 1 atau 6 input text field yang visible, kemungkinan OTP
            if len(visible_inputs) in [1, 6]:
                # Pastikan bukan login form (cek placeholder)
                for inp in visible_inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    if 'code' in placeholder.lower() or 'digit' in placeholder.lower():
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

        # Cek pattern URL yang menandakan sudah login
        success_patterns = [
            'foryou',
            'following',
            'tiktok.com/@',
            '/explore',
            '/live'
        ]

        # Jika sudah tidak ada /login di URL dan ada pattern sukses
        if '/login' not in current_url:
            for pattern in success_patterns:
                if pattern in current_url:
                    return True

            # Atau jika sudah di homepage tiktok.com tanpa path /login
            if current_url == 'https://www.tiktok.com/' or current_url == 'https://www.tiktok.com':
                return True

        # Cek cookies untuk validasi tambahan
        try:
            cookies = driver.get_cookies()
            # Cek apakah ada session cookie dari TikTok
            for cookie in cookies:
                if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard']:
                    if cookie.get('value'):
                        return True
        except:
            pass

        return False
    except:
        return False

def tiktok_login():
    print("🚀 Memulai TikTok Login Bot v2...")
    print("📋 Fitur: Terminal-only, Auto-detect OTP\n")

    # Baca akun
    email, password = read_account()
    if not email or not password:
        return

    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)}\n")

    # Setup Chrome dengan headless mode
    print("🌐 Membuka browser (headless mode)...")
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"❌ Gagal membuat driver: {e}")
        return

    wait = WebDriverWait(driver, 15)

    try:
        # Buka halaman login
        print("📱 Membuka halaman login TikTok...")
        driver.get('https://www.tiktok.com/login/phone-or-email/email')
        time.sleep(3)

        # Input email
        print(f"📝 Mengisi email...")
        try:
            email_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"], input[type="text"]'))
            )
            email_input.clear()
            time.sleep(0.5)
            for char in email:
                email_input.send_keys(char)
                time.sleep(0.08)
        except TimeoutException:
            print("❌ Timeout saat mencari input email!")
            return

        time.sleep(1)

        # Input password
        print(f"🔐 Mengisi password...")
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_input.clear()
            time.sleep(0.5)
            for char in password:
                password_input.send_keys(char)
                time.sleep(0.08)
        except NoSuchElementException:
            print("❌ Input password tidak ditemukan!")
            return

        time.sleep(1)

        # Klik tombol login
        print("🖱️  Klik tombol login...")
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], button[data-e2e="login-button"]')
            login_button.click()
        except NoSuchElementException:
            print("❌ Tombol login tidak ditemukan!")
            return

        print("⏳ Menunggu respons dari TikTok...")
        time.sleep(4)

        # Cek kondisi: OTP atau langsung berhasil
        max_checks = 20
        otp_detected = False

        for i in range(max_checks):
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

                # Start interactive search mode
                search_users_interactive(driver)
                return

            # Cek OTP
            if check_for_otp(driver):
                otp_detected = True
                break

            time.sleep(1)

        # Handle OTP
        if otp_detected:
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

                                    # Try normal click first
                                    try:
                                        btn.click()
                                        print(f"   ✓ Tombol submit diklik: '{btn_text}'")
                                        button_found = True
                                    except:
                                        # Fallback: JavaScript click (works better in headless)
                                        try:
                                            driver.execute_script("arguments[0].click();", btn)
                                            print(f"   ✓ Tombol submit diklik (JS): '{btn_text}'")
                                            button_found = True
                                        except:
                                            continue

                                    if button_found:
                                        break
                            if button_found:
                                break
                        except Exception as e:
                            continue

                    if not button_found:
                        print("   ⚠️  Tombol submit tidak ditemukan, mencoba auto-submit...")
                    else:
                        # Wait a bit after button click for processing
                        time.sleep(1)

                except:
                    print("   ℹ️  Auto-submit (error mencari tombol)")

                # Tunggu hasil dengan progress indicator (increased for headless)
                print("\n⏳ Memproses verifikasi OTP...")
                max_wait = 15  # 15 seconds total wait
                check_interval = 1.5
                checks = int(max_wait / check_interval)

                login_success = False
                for i in range(checks):
                    time.sleep(check_interval)
                    progress = min(i+1, 6)
                    print(f"   {'▓' * progress}{'░' * (6-progress)} {progress}/6")

                    # Early exit if login successful
                    current_url = driver.current_url
                    if '/login' not in current_url or 'foryou' in current_url or 'following' in current_url:
                        print(f"\n   🎯 URL changed: {current_url}")
                        login_success = True
                        break

                # Extra wait if not detected yet
                if not login_success:
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

                    # Start interactive search mode
                    search_users_interactive(driver)
                    return
                else:
                    # Cek apakah masih di halaman OTP (kode salah)
                    if check_for_otp(driver):
                        print("\n" + "="*60)
                        print("❌ VERIFIKASI GAGAL")
                        print("="*60)
                        print("⚠️  Masih di halaman verifikasi")
                        print("💡 Kemungkinan:")
                        print("   - Kode OTP salah atau kadaluarsa")
                        print("   - Coba jalankan ulang script dan minta kode baru")
                        print("="*60)
                    else:
                        current_url = driver.current_url
                        print("\n" + "="*60)
                        print("❌ LOGIN GAGAL")
                        print("="*60)
                        print(f"📍 Current URL: {current_url}")
                        print("💡 Cek apakah ada masalah lain")
                        print("="*60)

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

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR TERJADI")
        print("="*60)
        print(f"⚠️  Error: {str(e)}")
        print("\n🔍 Stack trace:")
        import traceback
        traceback.print_exc()
        print("="*60)

    finally:
        if driver:
            try:
                # Close all windows first
                driver.close()
            except:
                pass

            try:
                # Then quit driver
                driver.quit()
                print("\n✓ Browser ditutup")
            except Exception as e:
                # Suppress common cleanup errors
                error_msg = str(e).lower()
                if "invalid" not in error_msg and "handle" not in error_msg:
                    print(f"\n⚠️  Warning saat cleanup: {e}")

            # Set to None to prevent destructor from trying again
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
