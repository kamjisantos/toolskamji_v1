import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows support
init(autoreset=True)

def print_hacker_banner():
    """Print epic hacker-style ASCII banner"""
    banner = f"""{Fore.GREEN + Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  {Fore.CYAN}████████╗ ██████╗  ██████╗ ██╗     ███████╗                  {Fore.GREEN}║
║  {Fore.CYAN}╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝                  {Fore.GREEN}║
║  {Fore.CYAN}   ██║   ██║   ██║██║   ██║██║     ███████╗                  {Fore.GREEN}║
║  {Fore.CYAN}   ██║   ██║   ██║██║   ██║██║     ╚════██║                  {Fore.GREEN}║
║  {Fore.CYAN}   ██║   ╚██████╔╝╚██████╔╝███████╗███████║                  {Fore.GREEN}║
║  {Fore.CYAN}   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                  {Fore.GREEN}║
║                                                                   ║
║  {Fore.YELLOW}██╗  ██╗██╗███╗   ██╗██████╗  █████╗                        {Fore.GREEN}║
║  {Fore.YELLOW}██║ ██╔╝██║████╗  ██║██╔══██╗██╔══██╗                       {Fore.GREEN}║
║  {Fore.YELLOW}█████╔╝ ██║██╔██╗ ██║██║  ██║███████║                       {Fore.GREEN}║
║  {Fore.YELLOW}██╔═██╗ ██║██║╚██╗██║██║  ██║██╔══██║                       {Fore.GREEN}║
║  {Fore.YELLOW}██║  ██╗██║██║ ╚████║██████╔╝██║  ██║                       {Fore.GREEN}║
║  {Fore.YELLOW}╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝                       {Fore.GREEN}║
║                                                                   ║
║  {Fore.RED}███████╗ ██████╗ ██╗     ██╗   ██╗███████╗██╗                {Fore.GREEN}║
║  {Fore.RED}██╔════╝██╔═══██╗██║     ██║   ██║██╔════╝██║                {Fore.GREEN}║
║  {Fore.RED}███████╗██║   ██║██║     ██║   ██║███████╗██║                {Fore.GREEN}║
║  {Fore.RED}╚════██║██║   ██║██║     ██║   ██║╚════██║██║                {Fore.GREEN}║
║  {Fore.RED}███████║╚██████╔╝███████╗╚██████╔╝███████║██║                {Fore.GREEN}║
║  {Fore.RED}╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═╝                {Fore.GREEN}║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  {Fore.WHITE + Style.BRIGHT}Version: {Fore.CYAN}DEBUG v2.0{Fore.GREEN}  │  {Fore.WHITE}Mode: {Fore.RED + Style.BRIGHT}[RECON]{Fore.GREEN}  │  {Fore.WHITE}Status: {Fore.GREEN + Style.BRIGHT}ACTIVE{Fore.GREEN}     ║
║  {Fore.WHITE + Style.BRIGHT}Purpose: {Fore.YELLOW}JSON Structure Analysis & Data Extraction{Fore.GREEN}          ║
╚═══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_section_header(title):
    """Print section header with hacker style"""
    print(f"\n{Fore.GREEN + Style.BRIGHT}{'═' * 70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║{Style.RESET_ALL} {Fore.CYAN + Style.BRIGHT}[{title}]{Style.RESET_ALL}")
    print(f"{Fore.GREEN + Style.BRIGHT}{'═' * 70}{Style.RESET_ALL}")

def debug_tiktok_json(username):
    """
    Debug script to print entire JSON structure from TikTok profile
    This will help us find the ACTUAL location of region and createTime fields
    """
    print_hacker_banner()

    print(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}TARGET:{Style.RESET_ALL} {Fore.CYAN}@{username}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}STATUS:{Style.RESET_ALL} {Fore.YELLOW}Initializing reconnaissance...{Style.RESET_ALL}")

    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')

    print(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}STEALTH MODE:{Style.RESET_ALL} {Fore.GREEN}Enabled{Style.RESET_ALL}")

    driver = uc.Chrome(options=options)

    try:
        url = f"https://www.tiktok.com/@{username}"
        print(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}CONNECTING:{Style.RESET_ALL} {Fore.BLUE}{url}{Style.RESET_ALL}")

        driver.get(url)

        # Animated loading
        print(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}LOADING:{Style.RESET_ALL}", end="")
        for i in range(5):
            print(f"{Fore.YELLOW}.{Style.RESET_ALL}", end="", flush=True)
            time.sleep(1)
        print(f" {Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}")

        page_source = driver.page_source

        # Try __UNIVERSAL_DATA_FOR_REHYDRATION__
        if '__UNIVERSAL_DATA_FOR_REHYDRATION__' in page_source:
            print_section_header("JSON DATA FOUND")
            print(f"{Fore.GREEN}[{Fore.GREEN + Style.BRIGHT}✓{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Found:{Style.RESET_ALL} {Fore.CYAN}__UNIVERSAL_DATA_FOR_REHYDRATION__{Style.RESET_ALL}")

            match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>', page_source)
            if match:
                data = json.loads(match.group(1))

                # Save full JSON to file
                filename = f'debug_{username}_UNIVERSAL.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"{Fore.GREEN}[{Fore.GREEN + Style.BRIGHT}✓{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Saved:{Style.RESET_ALL} {Fore.YELLOW}{filename}{Style.RESET_ALL}")

                # Print structure with hacker style
                print_section_header("JSON STRUCTURE ANALYSIS")
                print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}Root keys:{Style.RESET_ALL} {Fore.GREEN}{list(data.keys())}{Style.RESET_ALL}")

                if '__DEFAULT_SCOPE__' in data:
                    scope = data['__DEFAULT_SCOPE__']
                    print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}__DEFAULT_SCOPE__ keys:{Style.RESET_ALL} {Fore.GREEN}{list(scope.keys())}{Style.RESET_ALL}")

                    if 'webapp.user-detail' in scope:
                        user_detail = scope['webapp.user-detail']
                        print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}webapp.user-detail keys:{Style.RESET_ALL} {Fore.GREEN}{list(user_detail.keys())}{Style.RESET_ALL}")

                        if 'userInfo' in user_detail:
                            user_info = user_detail['userInfo']
                            print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}userInfo keys:{Style.RESET_ALL} {Fore.GREEN}{list(user_info.keys())}{Style.RESET_ALL}")

                            if 'user' in user_info:
                                user = user_info['user']
                                print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}user keys:{Style.RESET_ALL} {Fore.GREEN}{list(user.keys())}{Style.RESET_ALL}")

                                print_section_header("USER OBJECT DATA")
                                for key, value in user.items():
                                    if isinstance(value, (str, int, bool, float)):
                                        # Color code different data types
                                        if isinstance(value, bool):
                                            value_color = Fore.MAGENTA
                                        elif isinstance(value, int):
                                            value_color = Fore.YELLOW
                                        elif isinstance(value, str):
                                            value_color = Fore.CYAN
                                        else:
                                            value_color = Fore.WHITE

                                        # Highlight important fields
                                        if key in ['language', 'region', 'createTime', 'id', 'uniqueId']:
                                            print(f"{Fore.GREEN}[{Fore.RED + Style.BRIGHT}!{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}{key:20s}:{Style.RESET_ALL} {value_color + Style.BRIGHT}{value}{Style.RESET_ALL}")
                                        else:
                                            print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}{key:20s}:{Style.RESET_ALL} {value_color}{value}{Style.RESET_ALL}")

                            if 'stats' in user_info:
                                stats = user_info['stats']
                                print_section_header("STATS OBJECT DATA")
                                print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}Available stats:{Style.RESET_ALL} {Fore.GREEN}{list(stats.keys())}{Style.RESET_ALL}\n")
                                for key, value in stats.items():
                                    print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}{key:20s}:{Style.RESET_ALL} {Fore.YELLOW + Style.BRIGHT}{value:,}{Style.RESET_ALL}")

        # Try __NEXT_DATA__
        elif '__NEXT_DATA__' in page_source:
            print_section_header("JSON DATA FOUND")
            print(f"{Fore.GREEN}[{Fore.GREEN + Style.BRIGHT}✓{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Found:{Style.RESET_ALL} {Fore.CYAN}__NEXT_DATA__{Style.RESET_ALL}")

            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', page_source)
            if match:
                data = json.loads(match.group(1))

                # Save full JSON to file
                filename = f'debug_{username}_NEXT_DATA.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"{Fore.GREEN}[{Fore.GREEN + Style.BRIGHT}✓{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Saved:{Style.RESET_ALL} {Fore.YELLOW}{filename}{Style.RESET_ALL}")

                # Print structure
                print_section_header("JSON STRUCTURE ANALYSIS")
                print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}Root keys:{Style.RESET_ALL} {Fore.GREEN}{list(data.keys())}{Style.RESET_ALL}")

                if 'props' in data:
                    props = data['props']
                    print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}props keys:{Style.RESET_ALL} {Fore.GREEN}{list(props.keys())}{Style.RESET_ALL}")

                    if 'pageProps' in props:
                        page_props = props['pageProps']
                        print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}pageProps keys:{Style.RESET_ALL} {Fore.GREEN}{list(page_props.keys())}{Style.RESET_ALL}")

                        if 'userInfo' in page_props:
                            user_info = page_props['userInfo']
                            print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}userInfo keys:{Style.RESET_ALL} {Fore.GREEN}{list(user_info.keys())}{Style.RESET_ALL}")

                            if 'user' in user_info:
                                user = user_info['user']
                                print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}user keys:{Style.RESET_ALL} {Fore.GREEN}{list(user.keys())}{Style.RESET_ALL}")

                                print_section_header("USER OBJECT DATA")
                                for key, value in user.items():
                                    if isinstance(value, (str, int, bool, float)):
                                        if isinstance(value, bool):
                                            value_color = Fore.MAGENTA
                                        elif isinstance(value, int):
                                            value_color = Fore.YELLOW
                                        elif isinstance(value, str):
                                            value_color = Fore.CYAN
                                        else:
                                            value_color = Fore.WHITE

                                        if key in ['language', 'region', 'createTime', 'id', 'uniqueId']:
                                            print(f"{Fore.GREEN}[{Fore.RED + Style.BRIGHT}!{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}{key:20s}:{Style.RESET_ALL} {value_color + Style.BRIGHT}{value}{Style.RESET_ALL}")
                                        else:
                                            print(f"{Fore.CYAN}[{Fore.YELLOW}•{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE}{key:20s}:{Style.RESET_ALL} {value_color}{value}{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}[{Fore.RED + Style.BRIGHT}✗{Fore.RED}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}ERROR:{Style.RESET_ALL} {Fore.RED}No JSON data found!{Style.RESET_ALL}")

        print_section_header("RECON COMPLETE")
        print(f"{Fore.GREEN}[{Fore.GREEN + Style.BRIGHT}✓{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Status:{Style.RESET_ALL} {Fore.GREEN}Mission accomplished{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Next:{Style.RESET_ALL} {Fore.CYAN}Check saved JSON file for complete structure{Style.RESET_ALL}\n")

        # Wait for manual close
        input(f"{Fore.YELLOW}[{Fore.CYAN}⏸{Fore.YELLOW}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Press ENTER to close browser...{Style.RESET_ALL}")

    finally:
        driver.quit()
        print(f"{Fore.GREEN}[{Fore.GREEN + Style.BRIGHT}✓{Fore.GREEN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Browser closed{Style.RESET_ALL}")

if __name__ == "__main__":
    # Test dengan akun yang ada
    username = input(f"{Fore.CYAN}[{Fore.YELLOW}>{Fore.CYAN}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Enter TikTok username (without @):{Style.RESET_ALL} ").strip()
    if username:
        debug_tiktok_json(username)
    else:
        print(f"{Fore.RED}[{Fore.RED + Style.BRIGHT}✗{Fore.RED}]{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}ERROR:{Style.RESET_ALL} {Fore.RED}Username required!{Style.RESET_ALL}")
