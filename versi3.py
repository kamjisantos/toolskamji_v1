import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json
from datetime import datetime, timezone
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows support
init(autoreset=True)

# Color shortcuts
SUCCESS = Fore.GREEN
ERROR = Fore.RED
WARNING = Fore.YELLOW
INFO = Fore.CYAN
HEADER = Fore.MAGENTA
BOLD = Style.BRIGHT
DIM = Style.DIM
RESET = Style.RESET_ALL

def print_banner():
    """Print hacker-style banner"""
    banner = f"""
{Fore.GREEN + Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║  {Fore.CYAN}████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗        {Fore.GREEN}║
║  {Fore.CYAN}╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝        {Fore.GREEN}║
║  {Fore.CYAN}   ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝         {Fore.GREEN}║
║  {Fore.CYAN}   ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗         {Fore.GREEN}║
║  {Fore.CYAN}   ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗        {Fore.GREEN}║
║  {Fore.CYAN}   ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝        {Fore.GREEN}║
║  {Fore.YELLOW}███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ {Fore.GREEN}║
║  {Fore.YELLOW}██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗{Fore.GREEN}║
║  {Fore.YELLOW}███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝{Fore.GREEN}║
║  {Fore.YELLOW}╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗{Fore.GREEN}║
║  {Fore.YELLOW}███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║{Fore.GREEN}║
║  {Fore.YELLOW}╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝{Fore.GREEN}║
╠══════════════════════════════════════════════════════════════╣
║  {Fore.WHITE + Style.BRIGHT}Version: {Fore.CYAN}v3.0 {Fore.GREEN}│ {Fore.WHITE}Mode: {Fore.YELLOW}STEALTH{Fore.GREEN} │ {Fore.WHITE}Status: {Fore.GREEN}ACTIVE     {Fore.GREEN}║
║  {Fore.WHITE + Style.BRIGHT}Author:  {Fore.CYAN}MCP-Agent {Fore.GREEN}│ {Fore.WHITE}Region: {Fore.YELLOW}GLOBAL{Fore.GREEN} │ {Fore.WHITE}SSL: {Fore.GREEN}SECURE  {Fore.GREEN}║
╚══════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

def get_country_name(country_code):
    """Convert country code to full country name"""
    country_map = {
        'US': 'United States',
        'ID': 'Indonesia',
        'UK': 'United Kingdom',
        'GB': 'United Kingdom',
        'CA': 'Canada',
        'AU': 'Australia',
        'IN': 'India',
        'PH': 'Philippines',
        'MY': 'Malaysia',
        'SG': 'Singapore',
        'TH': 'Thailand',
        'VN': 'Vietnam',
        'JP': 'Japan',
        'KR': 'South Korea',
        'CN': 'China',
        'BR': 'Brazil',
        'MX': 'Mexico',
        'DE': 'Germany',
        'FR': 'France',
        'IT': 'Italy',
        'ES': 'Spain',
        'RU': 'Russia',
        'NL': 'Netherlands',
        'TR': 'Turkey',
        'SA': 'Saudi Arabia',
        'AE': 'United Arab Emirates',
        'EG': 'Egypt',
        'ZA': 'South Africa',
        'NG': 'Nigeria',
        'AR': 'Argentina',
        'CL': 'Chile',
        'CO': 'Colombia',
        'PE': 'Peru',
        'PL': 'Poland',
        'SE': 'Sweden',
        'NO': 'Norway',
        'DK': 'Denmark',
        'FI': 'Finland',
        'BE': 'Belgium',
        'AT': 'Austria',
        'CH': 'Switzerland',
        'IE': 'Ireland',
        'PT': 'Portugal',
        'GR': 'Greece',
        'CZ': 'Czech Republic',
        'RO': 'Romania',
        'HU': 'Hungary',
        'NZ': 'New Zealand',
        'PK': 'Pakistan',
        'BD': 'Bangladesh',
        'LK': 'Sri Lanka',
        'MM': 'Myanmar',
        'KH': 'Cambodia',
        'LA': 'Laos',
    }
    return country_map.get(country_code.upper(), country_code)

def extract_region_from_homepage(driver):
    """
    NEW METHOD: Extract region directly from TikTok homepage
    Based on bash script reference - TikTok exposes region in homepage JSON
    This is MORE RELIABLE than extracting from profile!
    """
    try:
        print("   🔍 NEW Method: Extract region from TikTok homepage...")
        
        # Save current URL to return later
        current_url = driver.current_url
        
        # Go to TikTok homepage
        driver.get("https://www.tiktok.com/")
        time.sleep(3)
        
        # Get page source
        page_source = driver.page_source
        
        # Method 1: Look for "region" in page source (most reliable)
        region_match = re.search(r'"region"\s*:\s*"([A-Z]{2})"', page_source)
        if region_match:
            region = region_match.group(1)
            print(f"   ✅ Region from homepage: {region}")
            
            # Return to previous page
            driver.get(current_url)
            time.sleep(2)
            return region
        
        # Return to previous page
        driver.get(current_url)
        time.sleep(2)
        
        print("   ⚠️ Region not found in homepage")
        return None
        
    except Exception as e:
        print(f"   ⚠️ Error extracting region from homepage: {e}")
        try:
            driver.get(current_url)
            time.sleep(2)
        except:
            pass
        return None


def try_get_region_from_video(driver, username):
    """
    Fallback: Try to get region from user's first video metadata
    TikTok includes 'region' in video author object even if not in profile
    Returns: (region_code, oldest_video_date_unix) tuple
    """
    try:
        print("   🔍 Trying to get region and oldest video date...")

        # Scroll down MULTIPLE times to trigger lazy loading
        try:
            print("   ⏳ Scrolling to load videos...")
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(1)
        except:
            pass

        # Look for video links on profile page - try multiple selectors
        video_links = []

        # Try selector 1: Standard video links
        try:
            video_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
            if len(video_links) > 0:
                print(f"   ℹ️ Found {len(video_links)} videos using selector 1")
        except:
            pass

        # Try selector 2: Video items with data-e2e
        if len(video_links) == 0:
            try:
                video_items = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a')
                video_links = [item for item in video_items if item.get_attribute('href') and '/video/' in item.get_attribute('href')]
                if len(video_links) > 0:
                    print(f"   ℹ️ Found {len(video_links)} videos using selector 2")
            except:
                pass

        # Try selector 3: Video container divs
        if len(video_links) == 0:
            try:
                video_containers = driver.find_elements(By.CSS_SELECTOR, 'div[class*="DivItemContainer"]')
                for container in video_containers:
                    try:
                        link = container.find_element(By.TAG_NAME, 'a')
                        href = link.get_attribute('href')
                        if href and '/video/' in href:
                            video_links.append(link)
                    except:
                        continue
                if len(video_links) > 0:
                    print(f"   ℹ️ Found {len(video_links)} videos using selector 3")
            except:
                pass

        # Try selector 4: Any link with video pattern (last resort)
        if len(video_links) == 0:
            try:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                video_links = [link for link in all_links if link.get_attribute('href') and '/video/' in link.get_attribute('href')]
                if len(video_links) > 0:
                    print(f"   ℹ️ Found {len(video_links)} videos using selector 4")
            except:
                pass

        if len(video_links) > 0:
            # Get LAST video URL (oldest video is usually last)
            last_video_url = video_links[-1].get_attribute('href') if len(video_links) > 0 else video_links[0].get_attribute('href')
            print(f"   ✓ Found {len(video_links)} videos, checking oldest...")

            # Navigate to video page
            driver.get(last_video_url)
            time.sleep(3)

            # Try to extract region and createTime from video page JSON
            page_source = driver.page_source

            region = None
            video_create_time = None

            # Try __UNIVERSAL_DATA_FOR_REHYDRATION__
            if '__UNIVERSAL_DATA_FOR_REHYDRATION__' in page_source:
                match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>', page_source)
                if match:
                    data = json.loads(match.group(1))
                    video_detail = data.get('__DEFAULT_SCOPE__', {}).get('webapp.video-detail', {})
                    item_info = video_detail.get('itemInfo', {})
                    item_struct = item_info.get('itemStruct', {})
                    author = item_struct.get('author', {})

                    # Get region from author - try multiple paths
                    region = author.get('region', None)
                    if not region:
                        region = author.get('country', None)

                    if region:
                        print(f"   ✓ Region from video: {region}")

                    # Get video createTime as account age estimate
                    video_create_time = item_struct.get('createTime', None)
                    if video_create_time:
                        try:
                            dt = datetime.fromtimestamp(int(video_create_time), tz=timezone.utc)
                            print(f"   ℹ️ Oldest video date (estimate): {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                        except:
                            pass

            # Try __NEXT_DATA__
            elif '__NEXT_DATA__' in page_source:
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', page_source)
                if match:
                    data = json.loads(match.group(1))
                    props = data.get('props', {}).get('pageProps', {})
                    video_object = props.get('videoObject', {})
                    author = video_object.get('author', {})

                    region = author.get('region', None)
                    if region:
                        print(f"   ✓ Region from video: {region}")

                    # Get video createTime
                    video_create_time = video_object.get('createTime', None) or video_object.get('uploadDate', None)

            return (region, video_create_time)

        return (None, None)
    except Exception as e:
        print(f"   ⚠️ Error getting data from video: {e}")
        return (None, None)


def scrape_user_profile_detailed(driver, username):
    """
    Scrape comprehensive user profile data from TikTok
    Returns detailed stats including followers, following, likes, videos, bio, etc.
    """
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

        print("   📊 Mengambil data comprehensive...")

        # Scroll to make sure stats are in viewport
        try:
            driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(1)
        except:
            pass

        # Initialize comprehensive stats dictionary
        stats = {
            'username': username,
            'nickname': 'N/A',
            'bio': 'N/A',
            'followers': 'N/A',
            'following': 'N/A',
            'likes': 'N/A',
            'videos': 'N/A',
            'verified': False,
            'private': False,
            'avatar_url': 'N/A',
            'uid': 'N/A',
            'region': 'N/A',
            'create_time': 'N/A',
            'create_time_unix': 'N/A',
            'profile_url': profile_url
        }

        # Wait for stats container
        try:
            print("   ⏳ Waiting for stats container...")
            stats_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[class*="H3CountInfos"], h3.css-17tvrad-5e6d46e3--H3CountInfos'))
            )
            print("   ✓ Stats container loaded!")

            # Scroll to stats container to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", stats_container)
            time.sleep(2)
        except TimeoutException:
            print("   ⚠️ Stats container timeout - trying anyway...")
            time.sleep(3)

        # Method 1: Try to extract from __NEXT_DATA__ or __UNIVERSAL_DATA_FOR_REHYDRATION__
        print("   🔍 Method 1: Extracting from page JSON data...")
        try:
            page_source = driver.page_source

            # Try __UNIVERSAL_DATA_FOR_REHYDRATION__
            if '__UNIVERSAL_DATA_FOR_REHYDRATION__' in page_source:
                match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>', page_source)
                if match:
                    try:
                        data = json.loads(match.group(1))

                        # DEBUG: Save full JSON to analyze structure
                        debug_filename = f"debug_json_{username}_{int(time.time())}.json"
                        with open(debug_filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"   🐛 DEBUG: Full JSON saved to {debug_filename}")

                        user_detail = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
                        user_info = user_detail.get('userInfo', {})
                        user_data = user_info.get('user', {})
                        user_stats = user_info.get('stats', {})

                        # Extract comprehensive data
                        stats['followers'] = user_stats.get('followerCount', 'N/A')
                        stats['following'] = user_stats.get('followingCount', 'N/A')

                        # Fix negative likes (int32 overflow for large numbers)
                        heart_count = user_stats.get('heartCount', 'N/A')
                        if heart_count != 'N/A' and isinstance(heart_count, int) and heart_count < 0:
                            # Convert negative int32 to unsigned int64
                            heart_count = heart_count + 2**32
                        stats['likes'] = heart_count

                        stats['videos'] = user_stats.get('videoCount', 'N/A')
                        stats['nickname'] = user_data.get('nickname', 'N/A')
                        stats['bio'] = user_data.get('signature', 'N/A')
                        stats['verified'] = user_data.get('verified', False)
                        stats['private'] = user_data.get('privateAccount', False)
                        stats['avatar_url'] = user_data.get('avatarLarger', 'N/A')
                        stats['uid'] = user_data.get('id', 'N/A')

                        # Extract REGION (country) - AVAILABLE in user_data!
                        region_code = user_data.get('region', None)
                        if region_code and region_code != '':
                            stats['region'] = region_code
                            print(f"   ✅ Region found in profile: {region_code}")
                        else:
                            stats['region'] = 'N/A'
                            print(f"   ⚠️ Region not in profile data (will check video metadata)")

                        # Extract CREATE TIME (account creation date)
                        # NOTE: TikTok does NOT expose account creation date in public API!
                        # user.createTime is often 0 or doesn't exist
                        create_time_unix = user_data.get('createTime', 0)
                        if create_time_unix and create_time_unix != 0:
                            stats['create_time_unix'] = create_time_unix
                            try:
                                dt = datetime.fromtimestamp(int(create_time_unix), tz=timezone.utc)
                                stats['create_time'] = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                                print(f"   ⚠️ Found createTime but likely video timestamp: {stats['create_time']}")
                            except:
                                stats['create_time'] = f"Unix: {create_time_unix}"
                        else:
                            stats['create_time'] = 'Not Available (TikTok API Limitation)'
                            stats['create_time_unix'] = 0
                            print(f"   ⚠️ Account creation date NOT exposed by TikTok API")

                        print("   ✓ Data extracted from JSON!")
                    except Exception as e:
                        print(f"   ⚠️ JSON parsing error: {e}")

            # Try __NEXT_DATA__ (alternative structure)
            elif '__NEXT_DATA__' in page_source:
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', page_source)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        user_info = data.get('props', {}).get('pageProps', {}).get('userInfo', {})
                        user_data = user_info.get('user', {})
                        user_stats = user_info.get('stats', {})

                        stats['followers'] = user_stats.get('followerCount', 'N/A')
                        stats['following'] = user_stats.get('followingCount', 'N/A')

                        # Fix negative likes (int32 overflow for large numbers)
                        heart_count = user_stats.get('heartCount', 'N/A')
                        if heart_count != 'N/A' and isinstance(heart_count, int) and heart_count < 0:
                            # Convert negative int32 to unsigned int64
                            heart_count = heart_count + 2**32
                        stats['likes'] = heart_count

                        stats['videos'] = user_stats.get('videoCount', 'N/A')
                        stats['nickname'] = user_data.get('nickname', 'N/A')
                        stats['bio'] = user_data.get('signature', 'N/A')
                        stats['verified'] = user_data.get('verified', False)
                        stats['private'] = user_data.get('privateAccount', False)
                        stats['avatar_url'] = user_data.get('avatarLarger', 'N/A')
                        stats['uid'] = user_data.get('id', 'N/A')

                        # Extract REGION
                        region_code = user_data.get('region', None)
                        if region_code and region_code != '':
                            stats['region'] = region_code
                            print(f"   ✅ Region found in profile: {region_code}")
                        else:
                            stats['region'] = 'N/A'
                            print(f"   ⚠️ Region not in profile data (will check video metadata)")

                        # Extract CREATE TIME
                        create_time_unix = user_data.get('createTime', 0)
                        if create_time_unix and create_time_unix != 0:
                            stats['create_time_unix'] = create_time_unix
                            try:
                                dt = datetime.fromtimestamp(int(create_time_unix), tz=timezone.utc)
                                stats['create_time'] = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                                print(f"   ✓ Account created: {stats['create_time']}")
                            except:
                                stats['create_time'] = f"Unix: {create_time_unix}"
                        else:
                            print(f"   ⚠️ createTime is 0 or missing")

                        print("   ✓ Data extracted from __NEXT_DATA__!")
                    except Exception as e:
                        print(f"   ⚠️ __NEXT_DATA__ parsing error: {e}")
        except Exception as e:
            print(f"   ⚠️ Method 1 error: {e}")

        # Method 2: Extract from visible elements (fallback)
        print("   🔍 Method 2: Extracting from visible elements...")
        try:
            wait = WebDriverWait(driver, 10)

            # Get FOLLOWERS
            if stats['followers'] == 'N/A':
                try:
                    followers_elem = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]'))
                    )
                    followers_text = followers_elem.text.strip()
                    if followers_text:
                        stats['followers'] = followers_text
                        print(f"   ✓ Followers: {stats['followers']}")
                except:
                    pass

            # Get FOLLOWING
            if stats['following'] == 'N/A':
                try:
                    following_elem = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="following-count"]'))
                    )
                    following_text = following_elem.text.strip()
                    if following_text:
                        stats['following'] = following_text
                        print(f"   ✓ Following: {stats['following']}")
                except:
                    pass

            # Get LIKES
            if stats['likes'] == 'N/A':
                try:
                    likes_elem = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="likes-count"]'))
                    )
                    likes_text = likes_elem.text.strip()
                    if likes_text:
                        stats['likes'] = likes_text
                        print(f"   ✓ Likes: {stats['likes']}")
                except:
                    pass

            # Get NICKNAME
            if stats['nickname'] == 'N/A':
                try:
                    nickname_elem = driver.find_element(By.CSS_SELECTOR, 'h1[data-e2e="user-title"]')
                    stats['nickname'] = nickname_elem.text.strip()
                    print(f"   ✓ Nickname: {stats['nickname']}")
                except:
                    pass

            # Get BIO
            if stats['bio'] == 'N/A':
                try:
                    bio_elem = driver.find_element(By.CSS_SELECTOR, 'h2[data-e2e="user-bio"]')
                    stats['bio'] = bio_elem.text.strip()
                    print(f"   ✓ Bio: {stats['bio'][:50]}...")
                except:
                    pass

            # Get AVATAR
            if stats['avatar_url'] == 'N/A':
                try:
                    avatar_elem = driver.find_element(By.CSS_SELECTOR, 'img[data-e2e="user-avatar"]')
                    stats['avatar_url'] = avatar_elem.get_attribute('src')
                    print(f"   ✓ Avatar URL found")
                except:
                    pass

            # Check VERIFIED badge
            try:
                verified_elem = driver.find_elements(By.CSS_SELECTOR, 'svg[class*="verified"]')
                if len(verified_elem) > 0:
                    stats['verified'] = True
                    print(f"   ✓ Account is VERIFIED")
            except:
                pass

        except Exception as e:
            print(f"   ⚠️ Method 2 error: {e}")

        # Method 3: Count videos from page
        print("   🔍 Method 3: Counting videos...")
        if stats['videos'] == 'N/A':
            try:
                # Try to count video elements on page
                video_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="user-post-item"]')
                if len(video_elements) > 0:
                    stats['videos'] = f"{len(video_elements)}+ (visible)"
                    print(f"   ✓ Videos: {stats['videos']}")
            except:
                pass

        # Method 4: NEW! Try to get region from HOMEPAGE first (most reliable!)
        print("   🔍 Method 4: Getting region from homepage...")
        try:
            region_from_homepage = extract_region_from_homepage(driver)
            if region_from_homepage:
                stats['region'] = region_from_homepage
                print(f"   ✅ Region detected from homepage: {region_from_homepage}")
        except Exception as e:
            print(f"   ⚠️ Homepage region extraction failed: {e}")

        # Method 5: Fallback - try to get region from video metadata (if Method 4 failed)
        if stats['region'] == 'N/A':
            print("   🔍 Method 5: Getting region from video metadata (fallback)...")
            try:
                # Store current URL to return later
                profile_url_backup = driver.current_url

                # Always call this to get region (required!)
                region_from_video, oldest_video_time = try_get_region_from_video(driver, username)

                # Update region if found
                if region_from_video:
                    stats['region'] = region_from_video
                    print(f"   ✓ Region extracted: {region_from_video}")
                else:
                    print(f"   ⚠️ Region not found (no videos or private account)")

                # Update account age ESTIMATE from oldest video
                if oldest_video_time:
                    try:
                        dt = datetime.fromtimestamp(int(oldest_video_time), tz=timezone.utc)
                        stats['create_time'] = f"{dt.strftime('%Y-%m-%d %H:%M:%S UTC')} (Estimated from oldest video)"
                        stats['create_time_unix'] = oldest_video_time
                        print(f"   ℹ️ Account age estimated from oldest video")
                    except Exception as e:
                        print(f"   ⚠️ Error parsing video date: {e}")
                else:
                    # Keep the warning message
                    if stats['create_time'] != 'Not Available (TikTok API Limitation)':
                        # We got a createTime from profile but it's likely wrong
                        stats['create_time'] = f"{stats['create_time']} (WARNING: Likely incorrect - see LIMITATIONS.md)"

                # Return to profile page
                try:
                    driver.get(profile_url_backup)
                    time.sleep(2)
                except:
                    pass

            except Exception as e:
                print(f"   ⚠️ Method 5 error: {e}")
                import traceback
                traceback.print_exc()

        print(f"   📊 Scraping completed!")
        return stats

    except Exception as e:
        print(f"   ❌ Error saat scraping profil: {e}")
        import traceback
        traceback.print_exc()
        return None



def search_users_interactive(driver):
    """Interactive search loop untuk scrape multiple users"""
    print(f"\n{Fore.GREEN + Style.BRIGHT}{'='*70}{RESET}")
    print(f"{Fore.CYAN + Style.BRIGHT}                🔍  SCRAPING MODE ACTIVATED  🔍{RESET}")
    print(f"{Fore.GREEN + Style.BRIGHT}{'='*70}{RESET}")
    print(f"\n{INFO}[i]{RESET} {BOLD}Commands:{RESET}")
    print(f"   {SUCCESS}>{RESET} Enter username (without @) to scrape data")
    print(f"   {WARNING}>{RESET} Type 'exit' or 'quit' to terminate session")
    print(f"   {INFO}>{RESET} Type 'clear' to clear screen")
    print(f"{Fore.GREEN + Style.BRIGHT}{'='*70}{RESET}")

    search_count = 0

    while True:
        try:
            # Get username input (reset color after prompt)
            username_input = input(f"\n{Fore.CYAN + Style.BRIGHT}[TARGET]{RESET} Username: ").strip()
            # Reset terminal color
            print(RESET, end='')

            # CRITICAL: Remove any ANSI color codes that might have leaked into input
            username_input = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', username_input)
            username_input = username_input.strip()

            if not username_input:
                continue

            # Check for exit commands
            if username_input.lower() in ['exit', 'quit', 'q']:
                print(f"\n{WARNING}[!]{RESET} {BOLD}Terminating scraping session...{RESET}")
                break

            # Check for clear command
            if username_input.lower() == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n" + "="*60)
                print("🔍 MODE SCRAPING PROFIL TIKTOK")
                print("="*60)
                continue

            # Remove @ if user includes it
            username = username_input.lstrip('@')

            if not username:
                print("❌ Username tidak valid!")
                continue

            # Scrape the profile
            print(f"\n🔍 Scraping profil @{username}...")
            stats = scrape_user_profile_detailed(driver, username)

            if stats:
                search_count += 1

                # Get country name from code
                region_display = stats['region']
                if stats['region'] != 'N/A':
                    country_name = get_country_name(stats['region'])
                    region_display = f"{stats['region']} ({country_name})"

                print(f"\n{Fore.GREEN + Style.BRIGHT}{'═'*80}{RESET}")
                print(f"{Fore.GREEN + Style.BRIGHT}║{RESET} {SUCCESS}✓{RESET} {BOLD}DATA EXTRACTION COMPLETE{RESET} - {Fore.CYAN}@{stats['username']}{RESET}")
                print(f"{Fore.GREEN + Style.BRIGHT}{'═'*80}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Nickname    :{RESET} {Fore.CYAN + Style.BRIGHT}{stats['nickname']}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}UID         :{RESET} {Fore.YELLOW}{stats['uid']}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Region      :{RESET} {Fore.GREEN + Style.BRIGHT}{region_display}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Created     :{RESET} {Fore.MAGENTA}{stats['create_time']}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Followers   :{RESET} {Fore.CYAN + Style.BRIGHT}{stats['followers']}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Following   :{RESET} {Fore.CYAN}{stats['following']}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Likes       :{RESET} {Fore.RED + Style.BRIGHT}❤ {stats['likes']}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Videos      :{RESET} {Fore.YELLOW}{stats['videos']}{RESET}")
                verified_display = f"{SUCCESS}YES ✓{RESET}" if stats['verified'] else f"{Fore.RED}NO{RESET}"
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Verified    :{RESET} {verified_display}")
                private_display = f"{WARNING}PRIVATE 🔒{RESET}" if stats['private'] else f"{SUCCESS}PUBLIC 🔓{RESET}"
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Privacy     :{RESET} {private_display}")
                bio_display = stats['bio'] if stats['bio'] != 'N/A' and stats['bio'] else f"{DIM}(No bio){RESET}"
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Bio         :{RESET} {Fore.LIGHTWHITE_EX}{bio_display}{RESET}")
                avatar_short = stats['avatar_url'][:60] + '...' if len(stats['avatar_url']) > 60 else stats['avatar_url']
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Avatar URL  :{RESET} {DIM}{avatar_short}{RESET}")
                print(f"{INFO}[•]{RESET} {Fore.WHITE}Profile URL :{RESET} {Fore.BLUE}{stats['profile_url']}{RESET}")
                print(f"{Fore.GREEN + Style.BRIGHT}{'═'*80}{RESET}")

                # Save to JSON option
                save_option = input(f"\n{INFO}[?]{RESET} {BOLD}Save to JSON?{RESET} (y/n): ").strip().lower()
                if save_option == 'y':
                    filename = f"tiktok_{username}_{int(time.time())}.json"
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(stats, f, indent=4, ensure_ascii=False)
                        print(f"   {SUCCESS}[+]{RESET} {BOLD}Saved:{RESET} {Fore.CYAN}{filename}{RESET}")
                    except Exception as e:
                        print(f"   ❌ Error saving file: {e}")

            else:
                print("\n⚠️  Gagal mengambil data profil")

        except KeyboardInterrupt:
            print("\n\n⚠️  Scraping dibatalkan (Ctrl+C)")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n✓ Selesai!")
    print(f"📊 Total profil di-scrape: {search_count}")


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
        current_url = driver.current_url

        # CRITICAL: If we have valid session cookies, we're DEFINITELY logged in (not OTP!)
        try:
            cookies = driver.get_cookies()
            session_cookies = []
            for cookie in cookies:
                if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard', 'sessionid_ss']:
                    value = cookie.get('value', '')
                    if value and len(value) > 10:
                        session_cookies.append(cookie.get('name'))

            if len(session_cookies) >= 1:
                return False
        except:
            pass

        if '/login' not in current_url:
            return False

        try:
            driver.execute_script("window.scrollBy(0, 1);")
            time.sleep(0.5)
        except:
            pass

        page_source = driver.page_source.lower()

        if 'verify' in current_url or 'otp' in current_url or 'code' in current_url:
            return True

        otp_keywords = [
            'enter code',
            'enter the code',
            'masukkan kode',
            'verification code',
            'kode verifikasi',
            'aktivitas mencurigakan',
            'suspicious activity'
        ]

        matches = 0
        for keyword in otp_keywords:
            if keyword in page_source:
                matches += 1

        if matches >= 2:
            return True

        try:
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][maxlength="1"], input[placeholder*="code" i], input[placeholder*="digit" i]')
            visible_inputs = [inp for inp in otp_inputs if inp.is_displayed()]

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

        try:
            cookies = driver.get_cookies()
            session_cookies = []
            important_cookies = []

            for cookie in cookies:
                cookie_name = cookie.get('name')
                value = cookie.get('value', '')

                if cookie_name in ['sessionid', 'sid_tt', 'sid_guard', 'sessionid_ss']:
                    if value and len(value) > 10:
                        session_cookies.append(cookie_name)

                if cookie_name in ['tt_csrf_token', 'odin_tt', 'tt_chain_token']:
                    if value and len(value) > 5:
                        important_cookies.append(cookie_name)

            if len(session_cookies) >= 1:
                all_cookies = session_cookies + important_cookies
                print(f"   ✓ Login cookies found: {', '.join(all_cookies[:5])}")
                return True
        except Exception as cookie_error:
            print(f"   ⚠️  Cookie check error: {cookie_error}")

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

        if 'tiktok.com' in current_url:
            if '/login' not in current_url and '/phone-or-email' not in current_url and '/email' not in current_url:
                clean_url = current_url.split('?')[0]
                if clean_url.rstrip('/').endswith('tiktok.com') or '/foryou' in current_url:
                    print(f"   ✓ On homepage (not login page)")
                    return True

        print(f"   ✗ Login not detected")
        return False
    except Exception as e:
        print(f"   ✗ Error checking login: {e}")
        return False



def tiktok_login():
    # Print hacker banner
    print_banner()

    print(f"{SUCCESS}[+]{RESET} {BOLD}Initializing TikTok Scraper...{RESET}")
    print(f"{INFO}[i]{RESET} Mode: {BOLD}BROWSER VISIBLE{RESET} - Stealth scraping enabled\n")

    # Baca akun
    email, password = read_account()
    if not email or not password:
        return

    print(f"{INFO}[i]{RESET} Email: {Fore.CYAN}{email}{RESET}")
    print(f"{INFO}[i]{RESET} Password: {Fore.YELLOW}{'*' * len(password)}{RESET}\n")

    # Setup Chrome dengan VISIBLE mode
    print(f"{WARNING}[~]{RESET} {BOLD}Launching stealth browser...{RESET}")
    options = uc.ChromeOptions()

    # Anti-detection
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Window size
    options.add_argument('--window-size=1920,1080')

    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        driver = uc.Chrome(options=options)

        # Maximize window
        print("📐 Maximizing window...")
        driver.maximize_window()
        print("   ✓ Window maximized")

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
        email_filled = False
        for attempt in range(5):
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt}/5...")
                    time.sleep(1.5)

                email_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"], input[type="text"]'))
                )
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"], input[type="text"]')))

                email_input.clear()
                time.sleep(0.3)
                email_input.click()
                time.sleep(0.3)
                email_input.send_keys(email)
                time.sleep(0.5)

                if email_input.get_attribute('value'):
                    print(f"   ✅ Email berhasil diisi!")
                    email_filled = True
                    break

            except TimeoutException:
                if attempt < 4:
                    print(f"   ⚠️  Timeout attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Timeout saat mencari input email!")
                    return

        if not email_filled:
            print("❌ Gagal mengisi email!")
            return

        time.sleep(1)

        # Input password
        print(f"🔐 Mengisi password...")
        password_filled = False
        for attempt in range(5):
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt}/5...")
                    time.sleep(1.5)

                password_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                )
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))

                password_input.clear()
                time.sleep(0.3)
                password_input.click()
                time.sleep(0.3)
                password_input.send_keys(password)
                time.sleep(0.5)

                if password_input.get_attribute('value'):
                    print(f"   ✅ Password berhasil diisi!")
                    password_filled = True
                    break

            except (NoSuchElementException, TimeoutException):
                if attempt < 4:
                    print(f"   ⚠️  Error attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Input password tidak ditemukan!")
                    return

        if not password_filled:
            print("❌ Gagal mengisi password!")
            return

        time.sleep(1)

        # Klik tombol login
        print("🖱️  Menunggu tombol login aktif...")
        login_clicked = False
        for attempt in range(5):
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt}/5...")
                    time.sleep(1)

                login_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]:not([disabled]), button[data-e2e="login-button"]:not([disabled])'))
                )

                is_disabled = login_button.get_attribute('disabled')
                if is_disabled:
                    print(f"   ⚠️  Button still disabled on attempt {attempt + 1}")
                    if attempt < 4:
                        time.sleep(2)
                        continue
                    else:
                        print("❌ Tombol login masih disabled!")
                        return

                print("🖱️  Klik tombol login...")
                time.sleep(0.5)
                login_button.click()
                login_clicked = True
                print("   ✅ Login button clicked!")
                break

            except TimeoutException:
                if attempt < 4:
                    print(f"   ⚠️  Timeout attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print("❌ Tombol login tidak ditemukan!")
                    return

        if not login_clicked:
            print("❌ Gagal mengklik tombol login!")
            return

        print("⏳ Menunggu respons dari TikTok...")
        time.sleep(8)

        # Cek kondisi: OTP atau langsung berhasil
        max_checks = 25
        otp_detected = False

        for i in range(max_checks):
            if i > 0:
                time.sleep(2)

            if is_login_successful(driver):
                print("\n" + "="*60)
                print("✅ BERHASIL LOGIN!")
                print("="*60)
                print(f"🎉 URL: {driver.current_url}")

                cookies = driver.get_cookies()
                print(f"\n🍪 Session cookies tersimpan: {len(cookies)} cookies")

                session_found = False
                for cookie in cookies:
                    if cookie.get('name') in ['sessionid', 'sid_tt', 'sid_guard']:
                        session_found = True
                        print(f"   ✓ {cookie.get('name')}: {cookie.get('value')[:20]}...")

                if session_found:
                    print("\n✓ Session valid - Login berhasil!")

                print("\n" + "="*60)
                print("🎉 LOGIN BERHASIL - Starting scraping mode...")
                print("="*60)

                # Start interactive scraping mode
                search_users_interactive(driver)
                return

            if check_for_otp(driver):
                otp_detected = True
                break

            time.sleep(1)

        # Handle OTP
        if otp_detected:
            print("\n" + "="*60)
            print("📬 VERIFIKASI OTP DIPERLUKAN")
            print("="*60)

            try:
                page_source = driver.page_source

                if 'mencurigakan' in page_source.lower() or 'suspicious' in page_source.lower():
                    print("⚠️  Alasan: Aktivitas mencurigakan terdeteksi")

                masked_emails = re.findall(r'\w[*]+\w+@[\w.]+', page_source)

                if masked_emails:
                    print(f"📧 Kode OTP dikirim ke: {masked_emails[0]}")
                elif email:
                    masked = f"{email[:2]}***{email[-10:]}" if len(email) > 12 else f"{email[0]}***{email[-5:]}"
                    print(f"📧 Kode OTP dikirim ke: {masked}")

                print(f"🌐 Current URL: {driver.current_url}")
            except:
                pass

            print("="*60)

            # Input OTP
            otp_code = input("\n🔢 Masukkan kode OTP (6 digit): ").strip()

            if len(otp_code) != 6 or not otp_code.isdigit():
                print("❌ Kode OTP harus 6 digit angka!")
                input("\n⏸️  Tekan ENTER untuk close browser...")
                return

            print("\n📝 Mengisi kode OTP ke form...")
            try:
                time.sleep(2)

                print(f"   Current URL: {driver.current_url}")
                print(f"   Page title: {driver.title[:50]}")

                otp_selectors = [
                    'input[placeholder*="code" i]',
                    'input[placeholder*="verification" i]',
                    'input[placeholder*="otp" i]',
                    'input[name*="code" i]',
                    'input[autocomplete="one-time-code"]',
                    'input[type="tel"]',
                    'input[inputmode="numeric"]',
                    'input[type="number"]',
                    'input[type="text"]',
                ]

                all_otp_inputs = []
                for selector in otp_selectors:
                    try:
                        inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                        all_otp_inputs.extend(inputs)
                    except:
                        continue

                seen = set()
                unique_inputs = []
                for inp in all_otp_inputs:
                    elem_id = id(inp)
                    if elem_id not in seen:
                        seen.add(elem_id)
                        unique_inputs.append(inp)

                visible_inputs = []
                for inp in unique_inputs:
                    try:
                        if not inp.is_displayed():
                            continue

                        inp_type = inp.get_attribute('type')
                        inp_name = inp.get_attribute('name') or ''
                        inp_placeholder = inp.get_attribute('placeholder') or ''
                        inp_value = inp.get_attribute('value') or ''

                        if inp_type == 'password':
                            continue

                        if inp_name in ['username', 'email']:
                            continue

                        if 'email' in inp_placeholder.lower() or 'username' in inp_placeholder.lower():
                            continue

                        if '@' in inp_value:
                            continue

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

                if len(visible_inputs) == 0:
                    print("\n❌ Tidak menemukan input field OTP!")
                    return

                if len(visible_inputs) == 1:
                    visible_inputs[0].click()
                    time.sleep(0.2)
                    visible_inputs[0].clear()
                    time.sleep(0.2)

                    for i, char in enumerate(otp_code):
                        visible_inputs[0].send_keys(char)
                        time.sleep(0.15)
                        print(f"   ✓ Digit {i+1}/6 terisi")

                    print("\n✓ OTP berhasil dimasukkan")

                elif len(visible_inputs) >= 6:
                    for i in range(6):
                        visible_inputs[i].click()
                        time.sleep(0.1)
                        visible_inputs[i].clear()
                        visible_inputs[i].send_keys(otp_code[i])
                        time.sleep(0.12)
                        print(f"   ✓ Digit {i+1}/6 terisi")

                    print("\n✓ OTP berhasil dimasukkan")

                time.sleep(2)

                # Cari tombol submit
                print("\n🔍 Mencari tombol submit...")
                try:
                    submit_selectors = [
                        'button.email-view-wrapper__button',
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
                                    print(f"   ✓ Tombol submit diklik")
                                    button_found = True
                                    break
                            if button_found:
                                break
                        except:
                            continue

                    if not button_found:
                        print("   ⚠️  Auto-submit...")
                except:
                    print("   ℹ️  Auto-submit")

                print("\n⏳ Memproses verifikasi OTP...")
                print("⏳ Menunggu login berhasil (solve CAPTCHA manual jika ada)...")
                print("💡 Jangan close browser! Solve captcha manual jika muncul...")
                time.sleep(5)

                # LOOP CHECK sampai login berhasil (user bisa solve captcha manual!)
                max_wait_attempts = 120  # 120 x 3 = 360 detik = 6 menit
                login_success = False

                for attempt in range(max_wait_attempts):
                    if is_login_successful(driver):
                        login_success = True
                        print("\n" + "="*60)
                        print("✅ BERHASIL LOGIN!")
                        print("="*60)
                        print(f"🎉 URL: {driver.current_url}")

                        cookies = driver.get_cookies()
                        print(f"\n🍪 Session cookies tersimpan: {len(cookies)} cookies")

                        print("\n" + "="*60)
                        print("🎉 LOGIN BERHASIL - Starting scraping mode...")
                        print("="*60)

                        search_users_interactive(driver)
                        return

                    # Show progress every 10 attempts
                    if attempt > 0 and attempt % 10 == 0:
                        elapsed = attempt * 3
                        remaining = (max_wait_attempts - attempt) * 3
                        print(f"   ⏳ Waiting... ({elapsed}s elapsed, {remaining}s remaining)")

                    time.sleep(3)

                # Timeout - masih belum login setelah 6 menit
                if not login_success:
                    print("\n⚠️  TIMEOUT - Belum berhasil login setelah 6 menit")
                    print("💡 Kemungkinan:")
                    print("   - CAPTCHA belum diselesaikan")
                    print("   - Kode OTP salah")
                    print("   - Masalah koneksi")
                    print("\n⏸️  Browser tetap terbuka - silakan coba manual login...")

            except Exception as e:
                print(f"\n❌ Error saat input OTP: {e}")

        else:
            print("\n⚠️  TIDAK TERDETEKSI OTP")
            print(f"📍 Current URL: {driver.current_url}")

    except Exception as e:
        print("\n❌ ERROR TERJADI")
        print(f"⚠️  Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Keep browser open for manual inspection
        if driver:
            input("\n⏸️  Tekan ENTER untuk close browser...")
            try:
                driver.quit()
                print("\n✓ Browser ditutup")
            except:
                pass

        print("\n👋 Selesai!")


if __name__ == "__main__":
    tiktok_login()
