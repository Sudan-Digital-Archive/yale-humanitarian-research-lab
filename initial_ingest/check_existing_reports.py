import csv
import requests
import time

API_BASE_URL = "https://api.sudandigitalarchive.com/sda-api/api/v1/accessions"
CSV_FILE = "clean_yhlr_reports.csv"

def check_url_in_archive(url):
    try:
        response = requests.get(API_BASE_URL, params={"url_filter": url})
        response.raise_for_status()
        data = response.json()
        
        # Depending on the API structure, the results might be in a list directly or under a 'items'/'results' key.
        # OpenAPI spec usually defines this. Assuming typical list response or paginated response.
        # If the web_fetch summary didn't specify the exact response structure, I'll print it for the first one to debug if needed,
        # but typically "list accessions" returns a list of items.
        # Let's assume if 'items' exists use that, otherwise assume data itself is the list.
        
        results = data.get('items', data) if isinstance(data, dict) else data
        
        return len(results) > 0
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False

def main():
    print(f"Reading from {CSV_FILE}...")
    
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            total_checked = 0
            found_count = 0
            missing_count = 0
            
            for row in reader:
                url = row.get('url')
                if not url:
                    continue
                
                exists = check_url_in_archive(url)
                total_checked += 1
                
                if exists:
                    print(f"[EXISTS] {url}")
                    found_count += 1
                else:
                    print(f"[MISSING] {url}")
                    missing_count += 1
                
                # Be nice to the API
                time.sleep(0.1)

            print("\n--- Summary ---")
            print(f"Total Checked: {total_checked}")
            print(f"Found in Archive: {found_count}")
            print(f"Missing from Archive: {missing_count}")

    except FileNotFoundError:
        print(f"Error: File {CSV_FILE} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
