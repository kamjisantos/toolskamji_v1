import requests
import re
import time
import json
from urllib.parse import urlencode, quote

class TikTokLoginV3:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/login/phone-or-email/email',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        })

        self.email = None
        self.password = None

    def read_account(self):
        """Baca akun dari file akun.txt"""
        try:
            with open('akun.txt', 'r') as f:
                lines = f.read().strip().split('\n')
                if len(lines) >= 2:
                    self.email = lines[0].strip()
                    self.password = lines[1].strip()
                    return True
                else:
                    print("❌ Format akun.txt salah!")
                    print("Format yang benar:")
                    print("baris 1: email")
                    print("baris 2: password")
                    return False
        except FileNotFoundError:
            print("❌ File akun.txt tidak ditemukan!")
            print("Buat file akun.txt dengan format:")
            print("baris 1: email")
            print("baris 2: password")
            return False

    def get_csrf_token(self):
        """Ambil CSRF token dan cookies awal"""
        try:
            print("📡 Mengambil CSRF token...")
            response = self.session.get('https://www.tiktok.com/login/phone-or-email/email')

            # Ambil token dari cookies
            csrf_token = self.session.cookies.get('tt_csrf_token')
            if csrf_token:
                print(f"   ✓ CSRF token: {csrf_token[:20]}...")
                return csrf_token

            # Coba parse dari HTML jika tidak ada di cookies
            if 'csrfToken' in response.text:
                match = re.search(r'csrfToken["\s:]+([a-zA-Z0-9_-]+)', response.text)
                if match:
                    csrf_token = match.group(1)
                    print(f"   ✓ CSRF token (parsed): {csrf_token[:20]}...")
                    return csrf_token

            print("   ⚠️  CSRF token tidak ditemukan, lanjut tanpa token")
            return None
        except Exception as e:
            print(f"   ⚠️  Error getting CSRF token: {e}")
            return None

    def send_login_request(self, csrf_token):
        """Kirim request login ke TikTok"""
        try:
            print("\n🔐 Mengirim request login...")

            # Payload login - coba berbagai format
            payloads = [
                {
                    'username': self.email,
                    'password': self.password,
                    'mix_mode': 1
                },
                {
                    'email': self.email,
                    'password': self.password,
                },
                {
                    'account': self.email,
                    'password': self.password,
                    'type': 'email'
                }
            ]

            # Headers khusus untuk login request
            headers = self.session.headers.copy()
            if csrf_token:
                headers['X-Secsdk-Csrf-Token'] = csrf_token
                headers['X-Tt-Csrf-Token'] = csrf_token

            # Coba berbagai endpoint login TikTok
            endpoints = [
                'https://www.tiktok.com/passport/web/login/',
                'https://www.tiktok.com/api/user/login/',
                'https://www.tiktok.com/passport/web/login/email/',
                'https://www.tiktok.com/node/passport/web/login/',
                'https://www.tiktok.com/api/v1/login/',
            ]

            print(f"   📧 Username: {self.email}")
            print(f"   🔄 Mencoba {len(endpoints)} endpoints...\n")

            response = None
            successful_endpoint = None

            for endpoint in endpoints:
                for payload in payloads:
                    try:
                        endpoint_name = endpoint.split('/')[-2] if endpoint.split('/')[-1] == '' else endpoint.split('/')[-1]
                        payload_type = 'username' if 'username' in payload else 'email' if 'email' in payload else 'account'

                        print(f"   📤 Trying: {endpoint_name} (payload: {payload_type})")

                        response = self.session.post(
                            endpoint,
                            json=payload,
                            headers=headers,
                            timeout=10
                        )

                        print(f"      Response: {response.status_code}")

                        # Jika 200 atau 201, sukses
                        if response.status_code in [200, 201]:
                            print(f"      ✓ SUCCESS!")
                            successful_endpoint = endpoint
                            break

                        # Jika 400-499, endpoint benar tapi payload/auth salah
                        elif 400 <= response.status_code < 500:
                            print(f"      ⚠️  Client error - endpoint mungkin benar")
                            if response.status_code != 404:  # 404 = endpoint salah
                                successful_endpoint = endpoint
                                break

                    except requests.exceptions.Timeout:
                        print(f"      ⏱️  Timeout")
                        continue
                    except requests.exceptions.RequestException as e:
                        print(f"      ❌ Error: {str(e)[:30]}")
                        continue

                if successful_endpoint:
                    break

            if not response:
                print(f"\n❌ Semua endpoint gagal")
                return None

            if successful_endpoint:
                print(f"\n   ✓ Using endpoint: {successful_endpoint}")
            else:
                print(f"\n   ⚠️  No successful endpoint, using last response")

            print(f"   Final response code: {response.status_code}")

            # Parse response apapun status codenya (untuk debug)
            try:
                data = response.json()
                return data
            except:
                print("   ⚠️  Response bukan JSON")
                print(f"   Raw response: {response.text[:300]}")
                return {
                    'raw': response.text[:300],
                    'status_code': response.status_code,
                    'endpoint': successful_endpoint or 'unknown'
                }

        except Exception as e:
            print(f"\n❌ Error saat login: {e}")
            import traceback
            traceback.print_exc()
            return None

    def handle_login_response(self, data):
        """Handle response dari login request"""
        if not data:
            return False

        print("\n📊 Menganalisis response...")
        print("=" * 60)

        # Debug: print keys yang ada di response
        if isinstance(data, dict):
            print(f"Response keys: {list(data.keys())}")
            print(f"\nFull response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 60)

        # Format TikTok API: { "status_code": 0, "status_msg": "success", "log_pb": {...} }
        if isinstance(data, dict) and 'status_code' in data:
            status_code = data.get('status_code', -1)
            status_msg = data.get('status_msg', '')

            print(f"\n📍 Status code: {status_code}")
            print(f"📍 Status msg: {status_msg}")

            # Status code 0 = sukses/request diterima
            if status_code == 0:
                print("\n✅ Login request diterima oleh TikTok!")

                # Cek apakah ada redirect_url
                if 'redirect_url' in data:
                    redirect = data.get('redirect_url')
                    print(f"   🔗 Redirect URL: {redirect}")

                    # Follow redirect untuk mendapatkan cookies
                    if redirect:
                        print("\n   📡 Following redirect...")
                        try:
                            redirect_response = self.session.get(redirect, allow_redirects=True)
                            print(f"   ✓ Redirect response: {redirect_response.status_code}")
                        except:
                            print("   ⚠️  Gagal follow redirect")

                # Cek data field
                if 'data' in data:
                    inner_data = data.get('data', {})
                    print(f"\n   Data fields: {list(inner_data.keys())}")

                    # Cek apakah ada info redirect atau error
                    if 'redirect_url' in inner_data:
                        print(f"   🔗 Inner redirect: {inner_data['redirect_url']}")

                    if 'error_code' in inner_data:
                        error_code = inner_data.get('error_code', 0)
                        if error_code != 0:
                            print(f"   ⚠️  Inner error code: {error_code}")

                # Cek cookies setelah login
                print("\n🍪 Checking cookies...")
                session_cookies = ['sessionid', 'sid_tt', 'sid_guard', 'sessionid_ss', 'store-idc', 'store-country-code']
                cookies_found = []

                for cookie_name in session_cookies:
                    cookie_value = self.session.cookies.get(cookie_name)
                    if cookie_value:
                        cookies_found.append(cookie_name)
                        masked_value = f"{cookie_value[:10]}..." if len(cookie_value) > 10 else cookie_value
                        print(f"   ✓ {cookie_name}: {masked_value}")

                if cookies_found:
                    print(f"\n✅ Session cookies ditemukan: {len(cookies_found)} cookies")
                    return True
                else:
                    print("\n⚠️  Login diterima tapi TIDAK ADA session cookies")
                    print("   Kemungkinan TikTok perlu verifikasi tambahan:")
                    print("   - Browser/device verification")
                    print("   - CAPTCHA challenge")
                    print("   - Email/SMS OTP")
                    print("   - Risk control check")
                    return 'PENDING'

            # Status code untuk OTP/verification
            elif status_code in [1012, 2458, 2470, 2474, 1105]:
                print("\n📬 Verifikasi diperlukan!")
                print(f"   Status code: {status_code}")
                return 'OTP_REQUIRED'

            # Error codes
            else:
                print(f"\n❌ Login gagal")
                print(f"   Status code: {status_code}")
                if status_msg:
                    print(f"   Message: {status_msg}")

                # Common error codes
                error_messages = {
                    1001: 'Email/password salah',
                    1002: 'Akun tidak ditemukan',
                    1003: 'Password salah',
                    1004: 'Terlalu banyak percobaan login',
                    1005: 'Akun di-suspend',
                    2001: 'Parameter tidak valid',
                    2458: 'Perlu verifikasi email',
                    3001: 'Rate limit exceeded',
                }

                if status_code in error_messages:
                    print(f"   💡 Kemungkinan: {error_messages[status_code]}")

                return False

        # Format lama: { "data": { "error_code": 0 } }
        if isinstance(data, dict) and 'data' in data:
            inner_data = data.get('data', {})
            error_code = inner_data.get('error_code', -1)

            if error_code == 0:
                print("\n✓ Login berhasil!")
                return True

            if error_code == 1012 or 'verification' in str(inner_data).lower():
                print("\n📬 Verifikasi OTP diperlukan")
                return 'OTP_REQUIRED'

        print("\n❌ Format response tidak dikenali")
        return False

    def get_session_info(self):
        """Ambil informasi session setelah login"""
        print("\n📊 Session Info:")
        print("=" * 60)

        # Print semua cookies
        all_cookies = self.session.cookies.get_dict()
        print(f"Total cookies: {len(all_cookies)}\n")

        for name, value in all_cookies.items():
            masked_value = f"{value[:15]}..." if len(value) > 15 else value
            print(f"   {name}: {masked_value}")

        print("=" * 60)

        return len(all_cookies) > 0

    def run(self):
        """Main function untuk menjalankan login"""
        print("=" * 60)
        print("🚀 TikTok Login Bot v3 - Pure Terminal Mode")
        print("=" * 60)
        print("📋 Fitur: HTTP requests only, no browser needed\n")

        # Baca akun
        if not self.read_account():
            return

        print(f"\n📧 Email: {self.email}")
        print(f"🔑 Password: {'*' * len(self.password)}")

        # Get CSRF token
        csrf_token = self.get_csrf_token()
        time.sleep(1)

        # Send login request
        response_data = self.send_login_request(csrf_token)

        if not response_data:
            print("\n❌ Gagal mendapatkan response dari TikTok")
            return

        # Handle response
        result = self.handle_login_response(response_data)

        if result == True:
            print("\n" + "=" * 60)
            print("✅ LOGIN BERHASIL!")
            print("=" * 60)
            self.get_session_info()

        elif result == 'PENDING':
            print("\n" + "=" * 60)
            print("⏳ LOGIN PENDING - PERLU VERIFIKASI")
            print("=" * 60)
            print("\n💡 TikTok menerima request tapi memerlukan verifikasi tambahan")
            print("   Sayangnya, pure HTTP request tidak bisa handle ini.")
            print("\n   Solusi:")
            print("   1. Gunakan script dengan browser (tiktok_loginv2.py)")
            print("   2. Login manual sekali dari browser yang sama")
            print("   3. Gunakan proxy/residential IP")
            print("=" * 60)

        elif result == 'OTP_REQUIRED':
            print("\n" + "=" * 60)
            print("📬 VERIFIKASI OTP DIPERLUKAN")
            print("=" * 60)
            print("\n💡 TikTok memerlukan OTP verification")
            print("   Pure HTTP request belum support OTP flow.")
            print("\n   Gunakan script dengan browser (tiktok_loginv2.py)")
            print("=" * 60)

        else:
            print("\n" + "=" * 60)
            print("❌ LOGIN GAGAL")
            print("=" * 60)
            print("\n💡 Kemungkinan penyebab:")
            print("   1. Email/password salah")
            print("   2. TikTok memblokir login dari script/bot")
            print("   3. IP address di-flag sebagai suspicious")
            print("   4. Perlu browser verification")
            print("\n📝 Cek full response di atas untuk detail lebih lengkap")
            print("=" * 60)

if __name__ == "__main__":
    bot = TikTokLoginV3()
    bot.run()
