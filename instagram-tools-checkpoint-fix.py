# Tambahkan import tambahan di atas
import time
import base64
import re
from urllib.parse import urlparse, parse_qs


def solve_instagram_checkpoint(checkpoint_url, session, solver):
    """
    Handle Instagram checkpoint verification dengan 2Captcha
    """
    print(f"\n🔐 Navigating to checkpoint: {checkpoint_url}")
    
    try:
        # Step 1: Fetch checkpoint page
        response = session.get(checkpoint_url, allow_redirects=True, timeout=10)
        print(f"[DEBUG] Checkpoint page status: {response.status_code}")
        
        # Step 2: Extract reCAPTCHA sitekey dari halaman checkpoint
        sitekey_match = re.search(r'"sitekey":"([a-zA-Z0-9_-]+)"', response.text)
        if not sitekey_match:
            print("⚠️  Tidak bisa extract sitekey dari checkpoint page")
            return False
        
        sitekey = sitekey_match.group(1)
        print(f"[DEBUG] Found sitekey: {sitekey}")
        
        # Step 3: Solve reCAPTCHA v2 via 2Captcha
        print("🤖 Solving reCAPTCHA checkpoint...")
        captcha_token = solver.recaptcha(
            sitekey=sitekey,
            url=checkpoint_url,
            version='v2'
        )
        print(f"✅ Captcha solved: {captcha_token[:20]}...")
        
        # Step 4: Submit solved CAPTCHA token
        # Extract form data dan submit
        csrf_token_match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', response.text)
        
        submit_data = {
            'csrfmiddlewaretoken': csrf_token_match.group(1) if csrf_token_match else '',
            'g-recaptcha-response': captcha_token,
            'submit': 'Verify'
        }
        
        # Determine submit URL (usually same as checkpoint)
        submit_response = session.post(
            checkpoint_url,
            data=submit_data,
            allow_redirects=True,
            timeout=10
        )
        
        print(f"[DEBUG] Submit status: {submit_response.status_code}")
        
        # Step 5: Check if checkpoint passed
        if submit_response.status_code == 200 and 'checkpoint' not in submit_response.url:
            print("✅ Checkpoint verification PASSED!")
            return True
        else:
            print("❌ Checkpoint verification FAILED")
            print(f"[DEBUG] Response URL: {submit_response.url}")
            return False
            
    except Exception as e:
        print(f"❌ Error solving checkpoint: {str(e)}")
        return False


def get_phone_number(session, solver):
    """
    Get phone number dengan proper checkpoint handling
    """
    try:
        reset_url = "https://www.instagram.com/accounts/password/reset/"
        
        print("\n📱 Attempting to retrieve phone number...")
        response = session.get(reset_url, timeout=10)
        
        # Extract CSRF dan MID
        csrf_match = re.search(r'"csrf_token":"([^"]+)"', response.text)
        mid_match = re.search(r'"mid":"([^"]+)"', response.text)
        
        csrf_token = csrf_match.group(1) if csrf_match else ""
        mid_cookie = mid_match.group(1) if mid_match else ""
        
        print(f"[DEBUG] CSRF Token: {csrf_token[:20]}...")
        print(f"[DEBUG] MID Cookie: {mid_cookie[:20]}...")
        
        # Attempt recovery
        recovery_url = "https://www.instagram.com/api/v1/accounts/account_recovery/"
        
        recovery_data = {
            "email_or_username": username,
            "_csrftoken": csrf_token
        }
        
        print("⚠️  Requesting recovery for username:", username)
        response = session.post(recovery_url, json=recovery_data, timeout=10)
        
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        print(f"[DEBUG] Response Content-Type: {response.headers.get('content-type')}")
        
        response_json = response.json()
        print(f"[DEBUG] Response JSON:\n{json.dumps(response_json, indent=2)}")
        
        if response_json.get('message') == 'checkpoint_required':
            checkpoint_url = response_json.get('checkpoint_url')
            if checkpoint_url:
                print(f"\n⚠️  Instagram checkpoint detected!")
                time.sleep(2)
                
                # Try to solve checkpoint
                if solve_instagram_checkpoint(checkpoint_url, session, solver):
                    # Retry recovery setelah checkpoint solved
                    print("\n🔄 Retrying recovery after checkpoint...")
                    time.sleep(2)
                    response = session.post(recovery_url, json=recovery_data, timeout=10)
                    response_json = response.json()
                else:
                    print("❌ Failed to solve checkpoint, aborting...")
                    return None
        
        # Extract phone dari response
        recovery_message = response_json.get('message', '')
        if 'recovery_options' in response_json:
            options = response_json.get('recovery_options', [])
            for option in options:
                if option.get('type') == 'phone_sms':
                    phone = option.get('target')
                    # Censor phone number
                    censored = f"{phone[:3]}****{phone[-3:]}"
                    return censored
        
        return None
        
    except Exception as e:
        print(f"❌ Error getting phone number: {str(e)}")
        return None


# ... rest existing code ...
