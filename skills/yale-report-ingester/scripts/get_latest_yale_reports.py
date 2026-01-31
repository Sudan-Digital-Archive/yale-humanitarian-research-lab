import requests
import re
import json
import sys
from datetime import datetime

URL = "https://medicine.yale.edu/lab/khoshnood/publications/reports/"

def get_latest_report():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(json.dumps({"error": f"Failed to fetch page: {str(e)}"}))
        sys.exit(1)

    # Split by "Citation |" to find report blocks
    # This assumes the most recent report is at the top of the list/first found
    # The structure seems to be: Title ... Citation | Authors ... "Title" Date. ...
    
    # We will look for the "Citation |" markers. The text *before* the citation often contains the title, 
    # but the Citation itself contains the title in quotes and the date.
    
    # Regex to find the first "Citation |" block and extract details
    # We look for the pattern: Citation | [Authors] "[Title]" [Date].
    
    # Let's try to capture the first occurrence.
    # It usually looks like: Citation | ... “Title” ... Date.
    
    pattern = re.compile(r'Citation\s*\|\s*.*?[“"](.*?)[”"].*?(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})', re.DOTALL | re.IGNORECASE)
    
    matches = pattern.findall(html_content)
    
    if not matches:
        # Fallback/Debug: try to just find the first link to a document as a proxy if citation parsing fails
        print(json.dumps({"error": "Could not parse reports from page structure."}))
        sys.exit(0)

    # Get the first match (most recent)
    title, date_str = matches[0]
    
    # Clean up title
    title = title.strip()
    
    # Parse Date
    try:
        # Expected formats: "16 January 2026", "21 November 2025"
        date_obj = datetime.strptime(date_str.strip(), "%d %B %Y")
        iso_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        iso_date = date_str.strip()

    # Find the URL. We assume the "Copy Link" or the report title links to the PDF.
    # We'll look for the first 'href' that contains 'documents' or 'pdf' appearing *near* the start of the report list.
    # A simple reliable way for this specific page (based on previous observations) is that 
    # the "Copy Link" or title href is usually the one we want.
    
    # Let's find all links and pick the first one that looks like a document
    link_pattern = re.compile(r'href=["\"](https://files-profile\.medicine\.yale\.edu/documents/[^"\\]+)["\"]', re.IGNORECASE)
    link_matches = link_pattern.findall(html_content)
    
    if not link_matches:
         print(json.dumps({"error": "Could not find any document links."}))
         sys.exit(0)
         
    latest_url = link_matches[0]

    result = {
        "title": title,
        "date": iso_date,
        "url": latest_url
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    get_latest_report()
