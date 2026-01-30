import requests
import os
import sys

API_BASE_URL = "https://api.sudandigitalarchive.com/sda-api/api/v1/metadata-subjects"
API_KEY = os.environ.get("SDA_API_KEY")

TARGET_SUBJECT = "Yale Humanitarian Research Lab"
LANG = "english"

def get_headers():
    return {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

def get_subject_id():
    # 1. Search for the subject
    print(f"Searching for subject: '{TARGET_SUBJECT}'...")
    try:
        response = requests.get(
            API_BASE_URL, 
            params={"query_term": TARGET_SUBJECT, "lang": LANG},
            headers=get_headers()
        )
        response.raise_for_status()
        data = response.json()
        
        # Check if items exist
        items = data.get('items', [])
        for item in items:
            if item.get('subject') == TARGET_SUBJECT:
                print(f"Found existing subject ID: {item.get('id')}")
                return item.get('id')
        
        print("Subject not found.")
        
    except requests.RequestException as e:
        print(f"Error searching for subject: {e}")
        return None

    # 2. Create if not found
    print(f"Creating subject: '{TARGET_SUBJECT}'...")
    payload = {
        "metadata_subject": TARGET_SUBJECT,
        "lang": LANG
    }
    
    try:
        response = requests.post(API_BASE_URL, json=payload, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        new_id = data.get('id')
        print(f"Successfully created subject. ID: {new_id}")
        return new_id
    except requests.RequestException as e:
        print(f"Error creating subject: {e}")
        if response.text:
            print(f"Error details: {response.text}")
        return None

if __name__ == "__main__":
    if not API_KEY:
        print("Error: SDA_API_KEY environment variable not set.")
        sys.exit(1)
        
    subject_id = get_subject_id()
    if subject_id:
        print(f"\nFinal Subject ID: {subject_id}")
    else:
        print("\nFailed to get or create subject ID.")
        sys.exit(1)
