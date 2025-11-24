"""
STEP 2: CARI DATA INSTAGRAM
============================
Setelah login, jalankan ini untuk cari data user termasuk phone number.
Menggunakan session dari instagram_cookies.json

Command:
python 2_CARI_DATA.py evasswnd
"""

import requests
import json
import sys

def load_cookies():
    try:
        with open('instagram_cookies.json', 'r') as f:
            return json.load(f)
    except:
        print("❌ File instagram_cookies.json tidak ada!")
        print("Jalankan: python 1_LOGIN_DULU.py username password")
        sys.exit(1)

def search_user(username):
    cookies = load_cookies()
    session = requests.Session()
    session.cookies.update(cookies)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"[*] Searching: {username}")
    
    # Get user info
    url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
    resp = session.get(url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        user = data.get('data', {}).get('user', {})
        
        print("\n✅ DATA INSTAGRAM")
        print("=" * 50)
        print(f"Username: @{user.get('username')}")
        print(f"Nama: {user.get('full_name')}")
        print(f"Followers: {user.get('edge_followed_by', {}).get('count', 0)}")
        print(f"Following: {user.get('edge_follow', {}).get('count', 0)}")
        print(f"Bio: {user.get('biography')}")
        
        return user
    else:
        print(f"❌ Error: {resp.status_code}")
        print(resp.text)
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python 2_CARI_DATA.py username")
        sys.exit(1)
    
    username = sys.argv[1]
    search_user(username)
