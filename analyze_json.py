#!/usr/bin/env python3
"""
Analyze TikTok JSON structure to find region/country data
"""
import json
import sys
from pathlib import Path

def find_keys_recursive(data, target_keys=['region', 'country', 'location', 'language', 'createTime'], prefix=''):
    """Recursively find keys in nested JSON"""
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key

            # Check if key matches target
            if any(target.lower() in key.lower() for target in target_keys):
                results.append({
                    'path': current_path,
                    'key': key,
                    'value': value,
                    'type': type(value).__name__
                })

            # Recurse into nested structures
            if isinstance(value, (dict, list)):
                results.extend(find_keys_recursive(value, target_keys, current_path))

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            current_path = f"{prefix}[{idx}]"
            if isinstance(item, (dict, list)):
                results.extend(find_keys_recursive(item, target_keys, current_path))

    return results

def analyze_user_detail(data):
    """Focus analysis on user detail section"""
    print("=" * 80)
    print("🔍 ANALYZING USER DETAIL SECTION")
    print("=" * 80)

    user_detail = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
    user_info = user_detail.get('userInfo', {})
    user_data = user_info.get('user', {})

    print("\n📊 Available fields in user_data:")
    for key in sorted(user_data.keys()):
        value = user_data[key]
        if isinstance(value, str) and len(str(value)) > 100:
            print(f"  - {key}: {str(value)[:100]}...")
        else:
            print(f"  - {key}: {value}")

    print("\n📊 Available fields in user_info:")
    for key in sorted(user_info.keys()):
        if key != 'user':  # Skip user data (already shown)
            value = user_info[key]
            if isinstance(value, str) and len(str(value)) > 100:
                print(f"  - {key}: {str(value)[:100]}...")
            else:
                print(f"  - {key}: {value}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_json.py <debug_json_file.json>")

        # Try to find debug files
        debug_files = list(Path('.').glob('debug_json_*.json'))
        if debug_files:
            print(f"\nFound {len(debug_files)} debug files:")
            for f in debug_files:
                print(f"  - {f}")
            print(f"\nUsing: {debug_files[-1]}")
            json_file = debug_files[-1]
        else:
            print("\nNo debug JSON files found!")
            return
    else:
        json_file = sys.argv[1]

    print(f"\n📁 Loading: {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Focus on user detail section
    analyze_user_detail(data)

    # Find all relevant keys
    print("\n" + "=" * 80)
    print("🔍 SEARCHING FOR REGION/COUNTRY/LOCATION FIELDS")
    print("=" * 80)

    results = find_keys_recursive(data)

    if results:
        print(f"\n✅ Found {len(results)} matching fields:\n")
        for result in results:
            print(f"Path: {result['path']}")
            print(f"  Type: {result['type']}")
            if isinstance(result['value'], str) and len(result['value']) > 200:
                print(f"  Value: {str(result['value'])[:200]}...")
            else:
                print(f"  Value: {result['value']}")
            print()
    else:
        print("\n❌ No matching fields found!")

    print("=" * 80)

if __name__ == '__main__':
    main()
