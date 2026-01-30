import csv
import requests
import time
import os
import sys

API_BASE_URL = "https://api.sudandigitalarchive.com/sda-api/api/v1/accessions"
API_KEY = os.environ.get("SDA_API_KEY")
SUBJECT_ID = 37  # Yale Humanitarian Research Lab

def get_headers():
    return {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

def get_accession_by_url(url):
    """
    Returns the accession object if found, otherwise None.
    """
    try:
        response = requests.get(API_BASE_URL, params={"url_filter": url}, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
        for item in items:
            if item.get('seed_url') == url:
                return item
        return None
    except requests.RequestException as e:
        print(f"   [!] Error fetching accession for {url}: {e}")
        return None

def update_subjects_for_existing(accession):
    accession_id = accession['id']
    url = accession['seed_url']
    
    # Check if subject is already there
    existing_subject_ids = accession.get('subjects_en_ids', []) or []
    if SUBJECT_ID in existing_subject_ids:
        print(f"   [OK] Subject {SUBJECT_ID} already present for accession {accession_id}.")
        return True

    print(f"   [UPDATE] Adding subject {SUBJECT_ID} to existing accession {accession_id} ({url})...")
    
    # Prepare update payload
    # UpdateAccessionRequest requires: metadata_language, metadata_title, metadata_time, metadata_subjects, is_private
    new_subjects = list(set(existing_subject_ids + [SUBJECT_ID]))
    
    payload = {
        "metadata_language": "english" if accession.get('has_english_metadata') else "arabic",
        "metadata_title": accession.get('title_en') or accession.get('title_ar') or "",
        "metadata_time": accession.get('dublin_metadata_date'),
        "metadata_subjects": new_subjects,
        "is_private": accession.get('is_private', False),
        "metadata_description": accession.get('description_en') or accession.get('description_ar')
    }

    try:
        update_url = f"{API_BASE_URL}/{accession_id}"
        response = requests.put(update_url, json=payload, headers=get_headers())
        response.raise_for_status()
        print(f"   [SUCCESS] Updated accession {accession_id}.")
        return True
    except requests.RequestException as e:
        print(f"   [ERROR] Failed to update accession {accession_id}: {e}")
        if 'response' in locals() and response.text:
            print(f"   [DETAILS] {response.text}")
        return False

def main():
    if not API_KEY:
        print("Error: SDA_API_KEY not set.")
        sys.exit(1)

    # 1. Get the 2 existing URLs we know about
    existing_urls = [
        "https://files-profile.medicine.yale.edu/documents/001a93f9-1c99-4437-a023-bac1294d3d0e",
        "https://files-profile.medicine.yale.edu/documents/45e77af9-a3cb-4bae-9bc2-61efe1d1595f"
    ]

    print("Updating existing records in archive...")
    for url in existing_urls:
        print(f"\nChecking {url}")
        accession = get_accession_by_url(url)
        if accession:
            update_subjects_for_existing(accession)
        else:
            print(f"   [!] Could not find accession for {url}")

if __name__ == "__main__":
    main()
