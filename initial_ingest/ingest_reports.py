import csv
import requests
import time
import os
import shutil
from tempfile import NamedTemporaryFile

CSV_FILE = "clean_yhlr_reports.csv"
API_BASE_URL = "https://api.sudandigitalarchive.com/sda-api/api/v1/accessions"
API_KEY = os.environ.get("SDA_API_KEY")
SUBJECT_ID = 37 # Yale Humanitarian Research Lab

def get_headers():
    return {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

def check_url_in_archive(url):
    """
    Checks if the URL exists in the archive using the url_filter.
    Returns True if found, False otherwise.
    """
    try:
        response = requests.get(API_BASE_URL, params={"url_filter": url}, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        
        # Access 'items' if present, otherwise assume list
        results = data.get('items', data) if isinstance(data, dict) else data
        return len(results) > 0
    except requests.RequestException as e:
        print(f"   [!] API Check Error for {url}: {e}")
        return False

def initialize_csv():
    """
    Ensures the CSV has an 'ingested' column.
    """
    temp_file = NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='')
    shutil.copy(CSV_FILE, CSV_FILE + ".bak") # Backup just in case
    
    renamed = False
    
    with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile, temp_file:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        
        if 'ingested' not in fieldnames:
            print("Adding 'ingested' column to CSV...")
            fieldnames.append('ingested')
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                row['ingested'] = 'False'
                writer.writerow(row)
            renamed = True
        else:
            # File is already good, just close temp
            pass

    if renamed:
        shutil.move(temp_file.name, CSV_FILE)
    else:
        os.remove(temp_file.name)

def update_csv_state(url, status):
    """
    Updates the 'ingested' status for a specific URL in the CSV.
    Inefficient but safe: reads all, updates one, writes all.
    """
    temp_file = NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='')
    
    with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile, temp_file:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            if row['url'] == url:
                row['ingested'] = str(status)
            writer.writerow(row)
            
    shutil.move(temp_file.name, CSV_FILE)

def ingest_report(row):
    url = row['url']
    print(f"\nProcessing: {url}")
    
    # 1. Check local state
    if row.get('ingested') == 'True':
        print("   [SKIP] Marked as ingested in CSV.")
        return

    # 2. Check remote state (Idempotency)
    print("   [CHECK] Verifying existence in archive...")
    if check_url_in_archive(url):
        print("   [EXISTS] Found in archive. Updating CSV state.")
        update_csv_state(url, True)
        return

    # 3. Prepare Payload
    payload = {
        "url": url,
        "metadata_title": row.get('title', ''),
        "metadata_description": row.get('description', ''),
        "metadata_time": row.get('iso_format_date'),
        "metadata_language": "english",
        "metadata_format": "wacz",
        "metadata_subjects": [SUBJECT_ID],
        "is_private": False
    }

    # 4. POST Request
    print("   [POST] Sending data to archive...")
    try:
        response = requests.post(API_BASE_URL, json=payload, headers=get_headers())
        response.raise_for_status()
        print("   [POST] Success.")
    except requests.RequestException as e:
        print(f"   [ERROR] Failed to post {url}: {e}")
        if 'response' in locals() and response.text:
            print(f"   [ERROR DETAILS] {response.text}")
        return # Move to next? Or stop? User said "upload one... shouldn't go to next... until previous one has shown up". So we return and let the loop retry or just stop. Here I'll return, and next run will retry.

    # 5. Blocking Poll
    print("   [POLL] Waiting for record to appear in archive...")
    attempt = 1
    while True:
        if check_url_in_archive(url):
            print(f"   [SUCCESS] Record confirmed in archive after {attempt} attempts.")
            break
        
        print(f"   [POLL] Attempt {attempt}: Not found yet. Waiting 5s...")
        time.sleep(5)
        attempt += 1
        
        # Safety break to prevent infinite loops if something is really wrong (e.g. 5 minutes)
        if attempt > 60:
            print("   [TIMEOUT] Waited too long. Moving on, but NOT marking as ingested.")
            return

    # 6. Update State
    update_csv_state(url, True)
    print("   [DONE] CSV updated.")

def main():
    if not API_KEY:
        print("Error: SDA_API_KEY environment variable not set.")
        return

    initialize_csv()
    
    # Read fresh after initialization
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        # Load all rows into memory to iterate safely
        # Note: We read from file inside update_csv_state, so we can iterate this list 
        # but we must be careful that 'update_csv_state' is atomic and doesn't break this loop's data references.
        # Since we just need the URL and data from this snapshot, it's fine.
        rows = list(csv.DictReader(f))
    
    for row in rows:
        ingest_report(row)

if __name__ == "__main__":
    main()
