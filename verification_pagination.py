
import requests
import json
import sys

BASE_URL = "http://localhost:5000/api/v1/public"

def test_pagination(endpoint, name):
    print(f"\n--- Testing {name} ({endpoint}) ---")
    
    # Test 1: Default Pagination
    try:
        url = f"{BASE_URL}/{endpoint}"
        print(f"1. Calling `{url}` (Default)...")
        r = requests.post(url) # Assuming POST as per routes
        if r.status_code == 200:
            data = r.json()
            if "pagination" in data:
                print(f"   ✅ Pagination metadata present: {data['pagination']}")
            else:
                print("   ❌ Pagination metadata MISSING")
        else:
            print(f"   ❌ Failed with status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test 2: Specific Page and Per Page
    try:
        url = f"{BASE_URL}/{endpoint}?page=1&per_page=1"
        print(f"2. Calling `{url}` (Page 1, Limit 1)...")
        r = requests.post(url)
        if r.status_code == 200:
            data = r.json()
            items_key = "categories" if "master" in endpoint else "subcategories"
            items = data.get(items_key, [])
            
            if len(items) == 1:
                 print(f"   ✅ Correctly returned 1 item")
            else:
                 print(f"   ❌ Returned {len(items)} items, expected 1")
                 
            if data.get("pagination", {}).get("per_page") == 1:
                print(f"   ✅ Metadata confirms per_page=1")
        else:
             print(f"   ❌ Failed with status {r.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test 3: All Items
    try:
        url = f"{BASE_URL}/{endpoint}?per_page=all"
        print(f"3. Calling `{url}` (All)...")
        r = requests.post(url)
        if r.status_code == 200:
            data = r.json()
            meta = data.get("pagination", {})
            if meta.get("per_page") == "all":
                 print(f"   ✅ Metadata confirms per_page='all'")
            else:
                 print(f"   ❌ Metadata per_page mismatch: {meta.get('per_page')}")
        else:
             print(f"   ❌ Failed with status {r.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("Starting Pagination Verification...")
    test_pagination("get-mastercategories", "Master Categories")
    test_pagination("get-subcategories", "Subcategories")
    print("\nVerification Complete.")
