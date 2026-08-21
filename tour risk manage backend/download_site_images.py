import csv
import os
import time
import re
import requests

HEADERS = {'User-Agent': 'SafeJourneyAI-SLIIT-Project/1.0 (student research project)'}
CSV_PATH = r"C:\Users\ASUS\OneDrive - Sri Lanka Institute of Information Technology\Desktop\tourism_risk_system\data\tourist_sites.csv"
OUTPUT_DIR = r"C:\Users\ASUS\Videos\tourism-unified\public\images"

SUFFIX_WORDS = ["National Park", "Forest Reserve", "Rock Temple", "Beach", "Fort",
                "Temple", "Island", "Lagoon", "Reservoir", "Sacred City", "Ancient City",
                "Tower", "Museum", "Gardens", "Orphanage", "Monastery"]

def filename_for(site_name):
    return site_name.lower().replace(" ", "_") + ".jpg"

def core_name(site_name):
    """Strip common generic suffix words to get a simpler search term."""
    name = site_name
    for suffix in SUFFIX_WORDS:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
            break
    return name

def search_wikipedia_title(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {"action": "opensearch", "search": query, "limit": 1, "namespace": 0, "format": "json"}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        titles = data[1]
        if titles:
            return titles[0].replace(" ", "_")
        return None
    except Exception as e:
        print(f"    search error for '{query}': {e}")
        return None

def get_summary_image(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        thumb = data.get("thumbnail") or data.get("originalimage")
        return thumb["source"] if thumb else None
    except Exception:
        return None

def wiki_image_url(site_name):
    # Try 1: direct title match
    direct_title = site_name.replace(" ", "_")
    img = get_summary_image(direct_title)
    if img:
        return img

    # Try 2: search using the full site name (no country suffix)
    found = search_wikipedia_title(site_name)
    if found:
        img = get_summary_image(found)
        if img:
            return img

    # Try 3: search using a simplified core name (strip generic suffix words)
    simplified = core_name(site_name)
    if simplified != site_name:
        found2 = search_wikipedia_title(simplified)
        if found2:
            img = get_summary_image(found2)
            if img:
                return img

    return None

def download_image(url, out_path, retries=4):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"    rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"    download status={r.status_code} bytes={len(r.content)}")
            return False
        except Exception as e:
            print(f"    ERROR downloading: {e}")
            return False
    return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sites = list(reader)

    print(f"Loaded {len(sites)} sites from CSV\n")

    success = []
    failed = []

    for i, row in enumerate(sites, 1):
        site_name = row["site_name"]
        out_filename = filename_for(site_name)
        out_path = os.path.join(OUTPUT_DIR, out_filename)

        if os.path.exists(out_path):
            print(f"[{i}/{len(sites)}] {site_name} -> already exists, skipping")
            success.append(site_name)
            continue

        print(f"[{i}/{len(sites)}] {site_name} -> {out_filename}")

        img_url = wiki_image_url(site_name)
        if not img_url:
            print(f"    NOT FOUND on Wikipedia (all strategies exhausted)")
            failed.append(site_name)
            time.sleep(4)
            continue

        ok = download_image(img_url, out_path)
        if ok:
            print(f"    OK: saved ({os.path.getsize(out_path)} bytes)")
            success.append(site_name)
        else:
            print(f"    FAILED to download")
            failed.append(site_name)

        time.sleep(4)

    print("\n" + "=" * 50)
    print(f"SUCCESS: {len(success)}/{len(sites)}")
    print(f"FAILED:  {len(failed)}/{len(sites)}")
    if failed:
        print("\nSites needing manual images:")
        for name in failed:
            print(f"  - {name}")

if __name__ == "__main__":
    main()