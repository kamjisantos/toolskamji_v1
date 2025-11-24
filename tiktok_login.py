import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

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
    """Cek apakah ada CAPTCHA yang perlu diselesaikan"""
    try:
        # Cek berbagai jenis CAPTCHA TikTok
        captcha_selectors = [
            'iframe[id*="captcha"]',
            'div[class*="captcha"]',
            'div[id*="captcha"]',
            '.secsdk-captcha-drag-icon',
            'div[class*="verify"]',
            'div[class*="puzzle"]'
        ]

        for selector in captcha_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    return True
            except:
                pass

        return False
    except:
        return False

def check_for_otp(driver):
    """Cek apakah halaman OTP muncul"""
    try:
        # Cek berbagai indikator OTP
        otp_indicators = [
            'input[placeholder*="code"]',
            'input[placeholder*="Code"]',
            'input[placeholder*="digit"]',
            'input[type="text"][maxlength="6"]',
            'div:contains("Masukkan kode")',
            'div:contains("Enter code")',
            'div:contains("Verification")'
        ]

        for selector in otp_indicators:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            except:
                pass

        # Cek text di halaman
        page_text = driver.page_source.lower()
        if 'masukkan kode' in page_text or 'enter code' in page_text or 'verification' in page_text:
            return True

        return False
    except:
        return False

def is_login_successful(driver):
    """Cek apakah login berhasil"""
    try:
        current_url = driver.current_url
        # Jika URL sudah tidak ada /login, berarti kemungkinan berhasil
        if '/login' not in current_url and ('foryou' in current_url or 'following' in current_url or 'tiktok.com/@' in current_url):
            return True
        return False
    except:
        return False

def tiktok_login():
    print("🚀 Memulai TikTok Login Bot v2...")
    print("📋 Fitur: Auto-detect CAPTCHA vs OTP\n")

    # Baca akun
    email, password = read_account()
    if not email or not password:
        return

    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)}\n")

    # Setup Chrome (headless dulu untuk cek kondisi)
    print("🌐 Membuka browser...")
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = uc.Chrome(options=options)
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
        time.sleep(3)

        # Cek kondisi: CAPTCHA, OTP, atau langsung berhasil
        max_checks = 30
        captcha_detected = False
        otp_detected = False

        for i in range(max_checks):
            # Cek apakah sudah berhasil login
            if is_login_successful(driver):
                print("\n" + "="*60)
                print("✅ BERHASIL LOGIN! (Tanpa verifikasi tambahan)")
                print("="*60)
                print(f"🎉 URL: {driver.current_url}")

                cookies = driver.get_cookies()
                print(f"🍪 Total cookies: {len(cookies)}")

                input("\n⏸️  Tekan ENTER untuk close browser...")
                return

            # Cek CAPTCHA
            if check_for_captcha(driver):
                captcha_detected = True
                print("\n" + "="*60)
                print("🧩 CAPTCHA TERDETEKSI!")
                print("="*60)
                print("👉 Silakan selesaikan CAPTCHA di browser")
                print("   (Puzzle slider, rotate, dll)\n")
                print("⏳ Menunggu kamu selesai...")
                print("="*60 + "\n")

                # Tunggu sampai CAPTCHA selesai atau OTP muncul
                for j in range(120):  # Max 2 menit
                    time.sleep(1)

                    if check_for_otp(driver):
                        otp_detected = True
                        break

                    if is_login_successful(driver):
                        print("\n✅ BERHASIL LOGIN!")
                        print(f"🎉 URL: {driver.current_url}")
                        input("\n⏸️  Tekan ENTER untuk close browser...")
                        return

                if otp_detected:
                    break
                else:
                    print("\n❌ Timeout menunggu CAPTCHA selesai!")
                    input("\n⏸️  Tekan ENTER untuk close browser...")
                    return

            # Cek OTP (tanpa CAPTCHA)
            if check_for_otp(driver):
                otp_detected = True
                break

            time.sleep(1)

        # Handle OTP
        if otp_detected:
            print("\n" + "="*60)
            print("📬 OTP TERDETEKSI!")
            print("="*60)

            # Cek pesan di halaman
            try:
                page_source = driver.page_source
                if 'mencurigakan' in page_source.lower() or 'suspicious' in page_source.lower():
                    print("⚠️  Aktivitas mencurigakan terdeteksi")
                if email[:5] in page_source or email[-10:] in page_source:
                    print(f"📧 Kode OTP dikirim ke: {email}")
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
            print("📝 Mengisi kode OTP...")
            try:
                # Coba berbagai selector untuk input OTP
                otp_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

                # Filter hanya input yang visible
                visible_inputs = [inp for inp in otp_inputs if inp.is_displayed()]

                if len(visible_inputs) == 1:
                    # Single input field (masukkan semua digit sekaligus)
                    visible_inputs[0].clear()
                    time.sleep(0.3)
                    for char in otp_code:
                        visible_inputs[0].send_keys(char)
                        time.sleep(0.1)
                    print("✓ OTP berhasil dimasukkan (1 field)")

                elif len(visible_inputs) >= 6:
                    # 6 separate input fields
                    for i in range(6):
                        visible_inputs[i].clear()
                        visible_inputs[i].send_keys(otp_code[i])
                        time.sleep(0.1)
                    print("✓ OTP berhasil dimasukkan (6 fields)")
                else:
                    print(f"⚠️  Ditemukan {len(visible_inputs)} input fields")
                    # Coba isi ke input pertama
                    if visible_inputs:
                        visible_inputs[0].clear()
                        for char in otp_code:
                            visible_inputs[0].send_keys(char)
                            time.sleep(0.1)

                time.sleep(2)

                # Cek dan klik tombol submit jika ada
                try:
                    submit_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], button:contains("Submit"), button:contains("Verify")')
                    for btn in submit_buttons:
                        if btn.is_displayed():
                            btn.click()
                            print("🖱️  Klik tombol submit OTP")
                            break
                except:
                    print("ℹ️  Auto-submit (tidak ada tombol submit)")

                # Tunggu hasil
                print("⏳ Memproses OTP...")
                time.sleep(5)

                # Cek hasil login
                if is_login_successful(driver):
                    print("\n" + "="*60)
                    print("✅ BERHASIL LOGIN!")
                    print("="*60)
                    print(f"🎉 URL: {driver.current_url}")

                    cookies = driver.get_cookies()
                    print(f"🍪 Total cookies: {len(cookies)}")

                    input("\n⏸️  Tekan ENTER untuk close browser...")
                else:
                    # Cek apakah masih di halaman OTP (kode salah)
                    if check_for_otp(driver):
                        print("\n❌ Kode OTP salah! Masih di halaman verifikasi.")
                    else:
                        print("\n❌ Login gagal! Cek status di browser.")

                    input("\n⏸️  Tekan ENTER untuk close browser...")

            except Exception as e:
                print(f"\n❌ Error saat input OTP: {e}")
                input("\n⏸️  Tekan ENTER untuk close browser...")

        else:
            print("\n❌ Tidak terdeteksi OTP atau CAPTCHA dalam 30 detik!")
            print("ℹ️  Mungkin ada masalah lain. Cek browser!")
            input("\n⏸️  Tekan ENTER untuk close browser...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\n⏸️  Tekan ENTER untuk close browser...")

    finally:
        driver.quit()
        print("\n👋 Browser ditutup. Selesai!")

if __name__ == "__main__":
    tiktok_login()
