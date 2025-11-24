"""
STEP 1: LOGIN KE INSTAGRAM DULU
================================
Jalankan ini terlebih dahulu untuk simpan session yang sudah login.
Hasilnya: instagram_cookies.json (token session Instagram kamu)

Command:
python 1_LOGIN_DULU.py your_instagram_username your_instagram_password
"""

import requests
import json
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def session_with_retries():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def login_instagram(username, password):
    session = session_with_retries()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Get CSRF token
    print("[*] Getting CSRF token...")
    resp = session.get('https://www.instagram.com/', headers=headers)
    csrf_token = resp.cookies.get('csrftoken')
    
    # Login
    print(f"[*] Logging in as {username}...")
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    
    login_data = {
        'username': username,
        'password': password,
        'queryParams': {},
        'optIntoOneTap': 'false'
    }
    
    login_headers = {
        **headers,
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.instagram.com/'
    }
    
    resp = session.post(login_url, data=login_data, headers=login_headers)
    
    if resp.status_code == 200 and 'authenticated' in resp.text:
        print("✅ LOGIN BERHASIL!")
        cookies = session.cookies.get_dict()
        with open('instagram_cookies.json', 'w') as f:
            json.dump(cookies, f)
        print("✅ Cookies disimpan ke instagram_cookies.json")
        return True
    else:
        print("❌ LOGIN GAGAL")
        print(resp.text)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python 1_LOGIN_DULU.py username password")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    login_instagram(username, password)
