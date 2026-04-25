import os
import requests
import shutil

# This script scrapes the local Django server to create a static HTML preview for Firebase Hosting.
# The server must be running at http://127.0.0.1:8000/

BASE_URL = "http://127.0.0.1:8000"
DIST_DIR = "dist"
STATIC_DIR = "staticfiles"

# Pages to export (URL path, output file path)
PAGES = [
    ("/", "index.html"),
    ("/admission/", "admission/index.html"),
    ("/directory/", "directory/index.html"),
    ("/staff/", "staff/index.html"),
    ("/staff/add/", "staff/add/index.html"),
    ("/leaves/", "leaves/index.html"),
    ("/attendance/", "attendance/index.html"),
]

def export():
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)
    
    # Copy static files
    dist_static = os.path.join(DIST_DIR, "static")
    if os.path.exists(dist_static):
        shutil.rmtree(dist_static)
    shutil.copytree(STATIC_DIR, dist_static)
    
    # Scrape pages
    for url_path, output_path in PAGES:
        full_url = BASE_URL + url_path
        print(f"Scraping {full_url}...")
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                # Ensure output directory exists
                out_file = os.path.join(DIST_DIR, output_path)
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                
                content = response.text
                # Fix static URL paths in HTML for relative hosting if needed
                # However, if we host at root, /static/ will work fine since we copied it to dist/static
                
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Saved to {out_file}")
            else:
                print(f"Failed to fetch {full_url}: Status {response.status_code}")
        except Exception as e:
            print(f"Error fetching {full_url}: {e}")

if __name__ == "__main__":
    export()
