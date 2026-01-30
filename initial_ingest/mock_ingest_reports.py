import csv
import time
import json

# URLs identified as already existing in the archive
SKIPPED_URLS = {
    "https://files-profile.medicine.yale.edu/documents/001a93f9-1c99-4437-a023-bac1294d3d0e",
    "https://files-profile.medicine.yale.edu/documents/45e77af9-a3cb-4bae-9bc2-61efe1d1595f"
}

CSV_FILE = "clean_yhlr_reports.csv"
API_ENDPOINT = "https://api.sudandigitalarchive.com/sda-api/api/v1/accessions"

def mock_process_reports():
    print(f"Starting mock ingestion from {CSV_FILE}...")
    
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            processed_count = 0
            skipped_count = 0
            
            for row in reader:
                url = row.get('url')
                if not url:
                    continue
                    
                if url in SKIPPED_URLS:
                    print(f"[SKIP] URL already exists in archive: {url}")
                    skipped_count += 1
                    continue
                
                # Construct the payload based on the OpenAPI schema and CSV data
                payload = {
                    "url": url,
                    "metadata_title": row.get('title', ''),
                    "metadata_description": row.get('description', ''),
                    "metadata_time": row.get('iso_format_date'),
                    "metadata_language": "english", # Enum: ['english', 'arabic']
                    "metadata_format": "wacz",      # Enum: ['wacz']
                    "metadata_subjects": [],        # Required array of integers. Unknown IDs, sending empty.
                    "is_private": False
                }
                
                # Mock POST Request
                print(f"\n[MOCK POST] Sending request to {API_ENDPOINT}")
                print(f"Payload: {json.dumps(payload, indent=2)}")
                
                # Mock Blocking Polling
                print(f"[MOCK POLL] Starting blocking poll for {url}...")
                # Simulate a loop that waits for the record to appear
                # In the real script, this would be a while loop calling check_url_in_archive
                for attempt in range(1, 4):
                    print(f"   [Attempt {attempt}] Checking availability via GET /accessions?url_filter=...")
                    time.sleep(0.5) # Simulate API latency
                    print("   -> Not found yet. Waiting...")
                
                print(f"   [Attempt 4] Checking availability...")
                print("   -> [SUCCESS] Record found in archive. Proceeding to next.")
                
                processed_count += 1
                
            print("\n--- Mock Ingestion Summary ---")
            print(f"Total Processed (Mocked): {processed_count}")
            print(f"Skipped (Existing): {skipped_count}")

    except FileNotFoundError:
        print(f"Error: File {CSV_FILE} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    mock_process_reports()
