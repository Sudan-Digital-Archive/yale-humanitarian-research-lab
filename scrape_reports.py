import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_yale_reports():
    url = "https://medicine.yale.edu/lab/khoshnood/publications/reports/"
    output_file = "yale_reports.csv"
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Base URL for relative links (though the target ones are absolute)
    
    reports = []
    
    # The user specifically wants links to files-profile.medicine.yale.edu/documents/
    target_pattern = re.compile(r"https://files-profile\.medicine\.yale\.edu/documents/")
    
    # Find all 'a' tags matching the pattern
    # We find all and then traverse up to find context if needed
    links = soup.find_all('a', href=target_pattern)
    
    print(f"Found {len(links)} matching report links.")
    
    for link in links:
        report_url = link['href']
        title = link.get_text(" ", strip=True)
        description = ""
        date_str = ""
        
        # Strategy 1: The 'link-list' style (most common 2025/2024 reports)
        # Structure A: 
        # <div class="document-link-with-description">
        #   <a ...><span class="link__label">Title (Date)</span></a>
        #   <div class="document-link-with-description__description">...</div>
        # </div>
        # Structure B:
        # <div class="link-with-description">
        #   <a ...><span class="link__label">Title (Date)</span></a>
        #   <span class="link-with-description__description">...</span>
        # </div>
        
        # Check if we are inside a link-with-description style container
        container = link.find_parent(class_=["document-link-with-description", "link-with-description"])
        
        if container:
            # Title often has date in parens at the end: "Title (Month DD, YYYY)"
            # Let's try to extract date from title first
            # We relax the regex to not strictly require end of string, but looking for the pattern in parens
            date_match = re.search(r"\((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\)", title)
            if date_match:
                date_str = date_match.group(0).strip("()")
                # Remove the date from the title if it was found at the end
                if title.strip().endswith(date_match.group(0)):
                     title = title[:date_match.start()].strip()
            
            # Description
            # Check for both possible description classes
            desc_elem = container.find(class_=["document-link-with-description__description", "link-with-description__description"])
            if desc_elem:
                description = desc_elem.get_text(" ", strip=True)
                
        else:
            # Strategy 2: The 'multi-column-list' style (e.g. 2026 reports top of page)
            # Structure:
            # <div class="content-list-item__content">
            #   <h4><a ...>Title</a></h4>
            #   <p><strong>Situation Report | Date</strong></p>
            #   <p>Citation...</p>
            # </div>
            
            content_div = link.find_parent(class_="content-list-item__content")
            if content_div:
                # Description often in the p tags
                # Date might be in a strong tag
                
                # Look for date in strong tag
                strong_tag = content_div.find("strong")
                if strong_tag:
                    strong_text = strong_tag.get_text(strip=True)
                    # format: "Situation Report | January 16, 2026"
                    date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", strong_text)
                    if date_match:
                        date_str = date_match.group(0)
                
                # Look for description (Citation)
                # It's usually the p tag starting with "Citation"
                p_tags = content_div.find_all("p")
                for p in p_tags:
                    text = p.get_text(" ", strip=True)
                    if text.startswith("Citation"):
                        description = text
                        break
        
        # Fallback date extraction if empty and citation contains date
        if not date_str and description:
             # Look for "Month DD, YYYY" OR "DD Month YYYY"
             # We look for the month name, and check if there's a day before or after
             
             # Regex for "Month DD, YYYY"
             date_match_1 = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", description)
             
             # Regex for "DD Month YYYY" (e.g. 23 May 2024)
             date_match_2 = re.search(r"\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", description)
             
             if date_match_1:
                 date_str = date_match_1.group(0)
             elif date_match_2:
                 date_str = date_match_2.group(0)

        reports.append({
            "url": report_url,
            "title": title,
            "description": description,
            "date": date_str
        })

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'title', 'description', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for report in reports:
            writer.writerow(report)
            
    print(f"Successfully wrote {len(reports)} reports to {output_file}")

if __name__ == "__main__":
    scrape_yale_reports()
