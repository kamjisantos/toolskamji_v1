#!/usr/bin/env python3
"""
Instagram Tools - Multi-purpose Instagram Information Tool with 2Captcha Integration
- Search username and display complete user information
- Check if email/phone is registered on Instagram
- Automatically solve CAPTCHA challenges using 2Captcha
"""

import json
import sys
import requests
import time
import re
import os
from typing import Optional, Dict, Any

try:
    from twocaptcha import TwoCaptcha
except ImportError:
    print("⚠️  2Captcha library not installed. Install with: pip install 2captcha-python")
    TwoCaptcha = None

COOKIE_FILE = 'instagram_cookies.json'

TWOCAPTCHA_API_KEY = '0ffd29027a459d20ee4085a8b9b8b055'
TWOCAPTCHA_CONFIG = {
    'server': '2captcha.com',
    'apiKey': TWOCAPTCHA_API_KEY,
    'defaultTimeout': 120,
    'pollingInterval': 10,
}


class InstagramTools:
    """
    Multi-purpose Instagram tools for username search and email/phone verification
    with automatic CAPTCHA solving using 2Captcha
    """

    def __init__(self, use_cookies: bool = True):
        """
        Initialize the tools

        Args:
            use_cookies: Load cookies from file if available
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        self.logged_in = False
        
        self.solver = None
        if TwoCaptcha:
            try:
                self.solver = TwoCaptcha(**TWOCAPTCHA_CONFIG)
                print("✅ 2Captcha solver initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize 2Captcha: {e}")
                self.solver = None

        if use_cookies and os.path.exists(COOKIE_FILE):
            self.load_cookies()
        else:
            self.session.get('https://www.instagram.com/', timeout=10)
            time.sleep(0.5)

    def load_cookies(self) -> bool:
        """
        Load cookies from saved file

        Returns:
            True if cookies loaded successfully, False otherwise
        """
        try:
            with open(COOKIE_FILE, 'r') as f:
                cookies = json.load(f)

            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='.instagram.com')

            if 'sessionid' in cookies:
                self.logged_in = True
                print(f"✅ Loaded cookies from {COOKIE_FILE} (logged in session)")
                return True
            else:
                print(f"⚠️  Cookies loaded but no sessionid found")
                return False

        except FileNotFoundError:
            print(f"⚠️  Cookie file not found: {COOKIE_FILE}")
            print("   Run loginig.py first to extract cookies")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid cookie file format")
            return False
        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            return False

    def solve_recaptcha(self, sitekey: str, page_url: str = 'https://www.instagram.com/', captcha_type: str = 'v2') -> Optional[str]:
        """
        Solve reCAPTCHA using 2Captcha service

        Args:
            sitekey: reCAPTCHA sitekey from page
            page_url: URL of the page containing the CAPTCHA
            captcha_type: Type of CAPTCHA ('v2' or 'v3')

        Returns:
            CAPTCHA solution token or None if failed
        """
        if not self.solver:
            print("❌ 2Captcha not initialized")
            return None

        try:
            print(f"🔄 Solving {captcha_type} reCAPTCHA...")
            
            if captcha_type.lower() == 'v3':
                result = self.solver.recaptcha(sitekey=sitekey, url=page_url, version='v3', action='verify', min_score=0.3)
            else:
                result = self.solver.recaptcha(sitekey=sitekey, url=page_url)
            
            print(f"✅ CAPTCHA solved: {result['code'][:50]}...")
            return result['code']
        except Exception as e:
            print(f"❌ Failed to solve CAPTCHA: {e}")
            return None

    def solve_hcaptcha(self, sitekey: str, page_url: str = 'https://www.instagram.com/') -> Optional[str]:
        """
        Solve hCaptcha using 2Captcha service

        Args:
            sitekey: hCaptcha sitekey from page
            page_url: URL of the page containing the CAPTCHA

        Returns:
            CAPTCHA solution token or None if failed
        """
        if not self.solver:
            print("❌ 2Captcha not initialized")
            return None

        try:
            print("🔄 Solving hCaptcha...")
            result = self.solver.hcaptcha(sitekey=sitekey, url=page_url)
            print(f"✅ hCaptcha solved: {result['code'][:50]}...")
            return result['code']
        except Exception as e:
            print(f"❌ Failed to solve hCaptcha: {e}")
            return None

    def extract_captcha_details(self, html: str) -> Optional[Dict[str, str]]:
        """
        Extract CAPTCHA sitekey and type from HTML response

        Args:
            html: HTML response content

        Returns:
            Dictionary with captcha_type and sitekey, or None
        """
        # Check for reCAPTCHA v2
        recaptcha_v2_match = re.search(r'data-sitekey=["\']([a-zA-Z0-9_-]+)["\']', html)
        if recaptcha_v2_match:
            return {
                'type': 'recaptcha_v2',
                'sitekey': recaptcha_v2_match.group(1)
            }
        
        # Check for hCaptcha
        hcaptcha_match = re.search(r'h-captcha[^>]*data-sitekey=["\']([a-zA-Z0-9_-]+)["\']', html)
        if hcaptcha_match:
            return {
                'type': 'hcaptcha',
                'sitekey': hcaptcha_match.group(1)
            }
        
        return None

    def search_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Search for a user by username using Instagram's public API

        Args:
            username: Instagram username to search for

        Returns:
            User information dictionary or None if not found
        """
        username = username.strip().lstrip('@')

        try:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"

            self.session.headers.update({
                'X-IG-App-ID': '936619743392459',
                'X-Requested-With': 'XMLHttpRequest'
            })

            response = self.session.get(url, timeout=10)

            if response.status_code == 429 or 'challenge' in response.text.lower():
                print("⚠️  CAPTCHA challenge detected!")
                captcha_details = self.extract_captcha_details(response.text)
                if captcha_details:
                    captcha_token = None
                    if captcha_details['type'] == 'recaptcha_v2':
                        captcha_token = self.solve_recaptcha(captcha_details['sitekey'], url)
                    elif captcha_details['type'] == 'hcaptcha':
                        captcha_token = self.solve_hcaptcha(captcha_details['sitekey'], url)
                    
                    if captcha_token:
                        print("✅ CAPTCHA solved, retrying request...")
                        time.sleep(2)
                        response = self.session.get(url, timeout=10)
                    else:
                        print("❌ Failed to solve CAPTCHA")
                        return None

            if response.status_code == 200:
                data = response.json()

                if data.get('data') and data['data'].get('user'):
                    user = data['data']['user']

                    user_info = {
                        "friendship_status": None,
                        "full_name": user.get('full_name', ''),
                        "is_verified": user.get('is_verified', False),
                        "pk": user.get('id', ''),
                        "profile_pic_url": user.get('profile_pic_url_hd') or user.get('profile_pic_url', ''),
                        "username": user.get('username', ''),
                        "is_private": user.get('is_private', False),
                        "supervision_info": None,
                        "social_context": user.get('full_name', ''),
                        "live_broadcast_visibility": None,
                        "live_broadcast_id": None,
                        "hd_profile_pic_url_info": user.get('profile_pic_url_hd'),
                        "is_unpublished": None,
                        "id": user.get('id', ''),
                        "biography": user.get('biography', ''),
                        "follower_count": user.get('edge_followed_by', {}).get('count', 0),
                        "following_count": user.get('edge_follow', {}).get('count', 0),
                        "media_count": user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        "external_url": user.get('external_url', ''),
                        "business_email": user.get('business_email', ''),
                        "business_phone_number": user.get('business_phone_number', ''),
                        "business_category_name": user.get('business_category_name', ''),
                    }

                    return user_info

            elif response.status_code == 404:
                return None
            else:
                print(f"Error: Instagram returned status code {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def check_email(self, email: str) -> Dict[str, Any]:
        """
        Check if an email is registered on Instagram

        Args:
            email: Email address to check

        Returns:
            Dictionary with check results
        """
        url = 'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/'

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'pragma': 'no-cache',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-model': '"Nexus 5"',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
            'x-asbd-id': '129477',
            'x-ig-app-id': '936619743392459',
            'x-requested-with': 'XMLHttpRequest'
        }

        data = {
            'enc_password': '#PWD_INSTAGRAM_BROWSER:10:1726419038:AeFQAJKDDYIf0N4r2MOuseJ50oNOvyCQ4tVhYsIdqELT+V4S5q0TgUEI8OG1zBEa3vr7+ReGttjU/s0H6uWdRxcIuYtrRMnCdMsPMfGnoro0p4NIo0yV/SbsFXC9CnAAEowyn94eKzFCubnDJznb+Kp2Fw==',
            'email': email,
            'first_name': 'test',
            'username': 'testuser' + str(abs(hash(email)))[-8:],
            'client_id': '',
            'seamless_login_enabled': '1',
            'opt_into_one_tap': 'false',
            'use_new_suggested_user_name': 'true'
        }

        try:
            response = self.session.post(url, headers=headers, data=data, timeout=10)

            if response.status_code == 429 or 'challenge' in response.text.lower():
                print("⚠️  CAPTCHA challenge detected during email check!")
                captcha_details = self.extract_captcha_details(response.text)
                if captcha_details:
                    captcha_token = None
                    if captcha_details['type'] == 'recaptcha_v2':
                        captcha_token = self.solve_recaptcha(captcha_details['sitekey'], url)
                    elif captcha_details['type'] == 'hcaptcha':
                        captcha_token = self.solve_hcaptcha(captcha_details['sitekey'], url)
                    
                    if captcha_token:
                        print("✅ CAPTCHA solved, retrying email check...")
                        time.sleep(2)
                        response = self.session.post(url, headers=headers, data=data, timeout=10)

            try:
                response_json = response.json()
            except requests.exceptions.JSONDecodeError:
                return {
                    'email': email,
                    'exists': False,
                    'error': 'Failed to parse response',
                    'message': 'There was a problem checking this email'
                }

            if 'errors' in response_json and 'email' in response_json['errors']:
                email_error = response_json['errors']['email'][0]['code']
                if email_error == 'email_is_taken':
                    return {
                        'email': email,
                        'exists': True,
                        'message': 'This email is associated with an Instagram account'
                    }
                else:
                    return {
                        'email': email,
                        'exists': False,
                        'message': 'This email is not associated with an Instagram account'
                    }
            else:
                return {
                    'email': email,
                    'exists': False,
                    'message': 'This email is not associated with an Instagram account'
                }

        except requests.exceptions.RequestException as e:
            return {
                'email': email,
                'exists': False,
                'error': str(e),
                'message': f'Network error: {e}'
            }
        except Exception as e:
            return {
                'email': email,
                'exists': False,
                'error': str(e),
                'message': f'Unexpected error: {e}'
            }

    def get_phone_number(self, username: str, debug: bool = False) -> Dict[str, Any]:
        """
        Try to get phone number (censored) from Instagram challenge/reset endpoint

        Args:
            username: Instagram username or email
            debug: Enable debug output

        Returns:
            Dictionary with phone number if available
        """
        try:
            reset_page_url = 'https://www.instagram.com/accounts/password/reset/'
            reset_url = 'https://www.instagram.com/accounts/account_recovery_send_ajax/'

            if debug:
                print(f"\n[DEBUG] Fetching reset page: {reset_page_url}")

            reset_page_response = self.session.get(reset_page_url, timeout=10)
            time.sleep(0.5)

            if reset_page_response.status_code == 429 or 'challenge' in reset_page_response.text.lower():
                print("⚠️  CAPTCHA challenge detected on reset page!")
                captcha_details = self.extract_captcha_details(reset_page_response.text)
                if captcha_details:
                    captcha_token = None
                    if captcha_details['type'] == 'recaptcha_v2':
                        captcha_token = self.solve_recaptcha(captcha_details['sitekey'], reset_page_url)
                    elif captcha_details['type'] == 'hcaptcha':
                        captcha_token = self.solve_hcaptcha(captcha_details['sitekey'], reset_page_url)
                    
                    if captcha_token:
                        print("✅ CAPTCHA solved, retrying reset page...")
                        time.sleep(2)
                        reset_page_response = self.session.get(reset_page_url, timeout=10)

            csrf_token = self.session.cookies.get('csrftoken', '')

            if not csrf_token:
                for cookie in reset_page_response.cookies:
                    if cookie.name == 'csrftoken':
                        csrf_token = cookie.value
                        break

            rollout_hash = ''
            mid_cookie = self.session.cookies.get('mid', '')

            match = re.search(r'"rollout_hash":"([^"]+)"', reset_page_response.text)
            if match:
                rollout_hash = match.group(1)

            if debug:
                print(f"[DEBUG] CSRF Token: {csrf_token[:20]}..." if csrf_token else "[DEBUG] CSRF Token: None")
                print(f"[DEBUG] MID Cookie: {mid_cookie[:20]}..." if mid_cookie else "[DEBUG] MID Cookie: None")
                print(f"[DEBUG] Rollout Hash: {rollout_hash[:20]}..." if rollout_hash else "[DEBUG] Rollout Hash: None")
                print(f"[DEBUG] Requesting recovery for username: {username}")

            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/password/reset/',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'x-asbd-id': '129477',
                'x-csrftoken': csrf_token,
                'x-ig-app-id': '936619743392459',
                'x-instagram-ajax': rollout_hash if rollout_hash else '1',
                'x-requested-with': 'XMLHttpRequest'
            }

            data = {
                'email_or_username': username,
                'recaptcha_challenge_field': ''
            }

            time.sleep(0.5)
            response = self.session.post(reset_url, headers=headers, data=data, timeout=10)

            if response.status_code == 429 or 'challenge' in response.text.lower():
                print("⚠️  CAPTCHA challenge detected during phone retrieval!")
                captcha_details = self.extract_captcha_details(response.text)
                if captcha_details:
                    captcha_token = None
                    if captcha_details['type'] == 'recaptcha_v2':
                        captcha_token = self.solve_recaptcha(captcha_details['sitekey'], reset_url)
                    elif captcha_details['type'] == 'hcaptcha':
                        captcha_token = self.solve_hcaptcha(captcha_details['sitekey'], reset_url)
                    
                    if captcha_token:
                        print("✅ CAPTCHA solved, retrying phone retrieval...")
                        time.sleep(2)
                        response = self.session.post(reset_url, headers=headers, data=data, timeout=10)

            if debug:
                print(f"[DEBUG] Response Status Code: {response.status_code}")
                print(f"[DEBUG] Response Content-Type: {response.headers.get('Content-Type')}")

            try:
                response_json = response.json()
                if debug:
                    print(f"[DEBUG] Response JSON:")
                    print(json.dumps(response_json, indent=2))
            except Exception as parse_error:
                if debug:
                    print(f"[DEBUG] JSON Parse Error: {parse_error}")
                    print(f"[DEBUG] Raw Response Text: {response.text[:500]}")
                return {
                    'username': username,
                    'phone_number': None,
                    'email': None,
                    'success': False,
                    'message': 'Instagram returned HTML instead of JSON - request detected as bot'
                }

            result = {
                'username': username,
                'phone_number': None,
                'email': None,
                'success': False,
                'message': ''
            }

            if response_json.get('status') == 'ok':
                fields = response_json.get('fields', {})

                if debug:
                    print(f"[DEBUG] Fields found: {fields}")

                phone = fields.get('phone_number', '')
                email = fields.get('email', '')

                if phone:
                    result['phone_number'] = phone
                    result['success'] = True
                    result['message'] = 'Phone number found (censored)'

                if email:
                    result['email'] = email
                    result['success'] = True
                    if result['message']:
                        result['message'] = 'Phone number and email found (censored)'
                    else:
                        result['message'] = 'Email found (censored)'

                if not phone and not email:
                    result['message'] = 'No contact information available'
                    if debug:
                        print("[DEBUG] No phone or email in fields")
            else:
                error_msg = response_json.get('message', 'Unknown error')
                result['message'] = f'Error: {error_msg}'
                if debug:
                    print(f"[DEBUG] API returned non-ok status: {response_json.get('status')}")
                    print(f"[DEBUG] Error message: {error_msg}")

            return result

        except requests.exceptions.RequestException as e:
            if debug:
                print(f"[DEBUG] Request Exception: {e}")
            return {
                'username': username,
                'phone_number': None,
                'email': None,
                'success': False,
                'error': str(e),
                'message': f'Network error: {e}'
            }
        except Exception as e:
            if debug:
                print(f"[DEBUG] Unexpected Exception: {e}")
            return {
                'username': username,
                'phone_number': None,
                'email': None,
                'success': False,
                'error': str(e),
                'message': f'Unexpected error: {e}'
            }

    def display_user_info(self, user_info: Dict[str, Any]) -> None:
        """
        Display user information in a formatted way

        Args:
            user_info: User information dictionary
        """
        print("\n" + "="*60)
        print("INSTAGRAM USER INFORMATION")
        print("="*60)
        print(f"\nUsername: @{user_info['username']}")
        print(f"Full Name: {user_info['full_name']}")
        print(f"User ID: {user_info['id']}")
        print(f"PK: {user_info['pk']}")
        print(f"Verified: {'Yes' if user_info['is_verified'] else 'No'}")
        print(f"Private Account: {'Yes' if user_info['is_private'] else 'No'}")

        if user_info.get('biography'):
            print(f"\nBiography: {user_info['biography']}")

        print(f"\nFollowers: {user_info.get('follower_count', 0):,}")
        print(f"Following: {user_info.get('following_count', 0):,}")
        print(f"Posts: {user_info.get('media_count', 0):,}")

        if user_info.get('external_url'):
            print(f"Website: {user_info['external_url']}")

        if user_info.get('business_email'):
            print(f"\nBusiness Email: {user_info['business_email']}")

        if user_info.get('business_phone_number'):
            print(f"Business Phone: {user_info['business_phone_number']}")

        if user_info.get('business_category_name'):
            print(f"Business Category: {user_info['business_category_name']}")

        if user_info.get('recovery_phone'):
            print(f"\nRecovery Phone (Censored): {user_info['recovery_phone']}")

        if user_info.get('recovery_email'):
            print(f"Recovery Email (Censored): {user_info['recovery_email']}")

        print(f"\nProfile Picture URL:")
        print(f"{user_info['profile_pic_url']}")

        print("\n" + "="*60)
        print("RAW JSON DATA")
        print("="*60)
        print(json.dumps(user_info, indent=4))
        print("="*60 + "\n")

    def search_and_display(self, username: str, include_phone: bool = True, debug: bool = False) -> bool:
        """
        Search for user and display information

        Args:
            username: Instagram username to search for
            include_phone: Try to get phone number from reset endpoint
            debug: Enable debug output

        Returns:
            True if user found, False otherwise
        """
        print(f"\nSearching for username: {username}")
        user_info = self.search_user(username)

        if user_info:
            if include_phone:
                if not self.logged_in:
                    print("\n⚠️  Not logged in - phone/email retrieval may fail")
                    print("   Run 'python loginig.py' to extract cookies for better results\n")

                print("Attempting to retrieve phone number...")
                phone_data = self.get_phone_number(username, debug=debug)
                if phone_data['success']:
                    user_info['recovery_phone'] = phone_data['phone_number']
                    user_info['recovery_email'] = phone_data['email']
                elif 'checkpoint_required' in phone_data.get('message', ''):
                    print("\n⚠️  Instagram requires checkpoint verification")
                    print("   This usually means you need to login first")
                    print("   Run: python loginig.py\n")
                elif debug:
                    print(f"[DEBUG] Phone retrieval failed: {phone_data['message']}")

            self.display_user_info(user_info)
            return True
        else:
            print(f"\nUser '@{username}' not found!")
            print("Please check the username and try again.\n")
            return False


def main():
    """Main function to run the tools"""
    tools = InstagramTools(use_cookies=True)  # Force load cookies
    
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    no_phone = '--no-phone' in sys.argv or '--skip-phone' in sys.argv

    print("\n" + "="*60)
    print("INSTAGRAM USER SEARCH TOOL + 2CAPTCHA INTEGRATION")
    print("="*60)
    print("Loaded from saved cookies - automatically fetching data")
    print("="*60)
    if tools.logged_in:
        print("🟢 Status: Logged in (using saved cookies)")
    else:
        print("🔴 Status: Not logged in")
        print("   Run: python loginig.py first to generate cookies")
        sys.exit(1)
    
    if tools.solver:
        print("✅ 2Captcha SOLVER READY")
    else:
        print("⚠️  2Captcha solver not available")
    print("="*60)

    non_flag_args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    if non_flag_args:
        username = non_flag_args[0]
    else:
        username = input("\nEnter Instagram username to search: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            sys.exit(1)

    print(f"\n🔍 Searching for: @{username}")
    print("-" * 60)
    
    tools.search_and_display(username, include_phone=not no_phone, debug=debug_mode)


if __name__ == "__main__":
    main()
