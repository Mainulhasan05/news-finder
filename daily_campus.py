from dotenv import load_dotenv
import os
import requests
import pandas as pd
import re
from datetime import datetime
load_dotenv()  # take environment variables

def search_daily_campus(query, api_key, cx, max_results=100):
    
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    # Initialize variables
    all_results = []
    start_index = 1
    
    # Google CSE allows max 10 results per request, and up to 100 total
    while start_index <= max_results and start_index <= 100:
        # Set up parameters
        params = {
            'q': query,
            'key': api_key,
            'cx': cx,
            'start': start_index
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
                
            all_results.extend(items)
            print(f"Fetched {len(items)} results. Total so far: {len(all_results)}")
            
            # Update start index for next batch (each page has 10 results)
            start_index += 10
            
        except Exception as e:
            print(f"Error fetching results: {e}")
            break
    
    return all_results

def extract_date_from_snippet(snippet):
    """
    Extract date from snippet text
    
    Sample formats:
    - "Dec 9, 2024 ..."
    - "Jan 15, 2023 ..."
    - "May 3, 2025 ..."
    """
    if not snippet:
        return None
        
    # Pattern to match month, day, year at the beginning of text
    date_pattern = r'^([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})'
    match = re.search(date_pattern, snippet)
    
    if match:
        date_str = match.group(1)
        try:
            # Parse the date string
            date_obj = datetime.strptime(date_str, '%b %d, %Y')
            return date_obj
        except ValueError:
            pass
    
    return None

def process_search_data(results):
    """Process raw search results into a pandas DataFrame"""
    processed_data = []
    
    for item in results:
        title = item.get('title', '')
        url = item.get('link', '')
        snippet = item.get('snippet', '')
        
        # Extract date from snippet
        last_updated = extract_date_from_snippet(snippet)
        
        # Format fields
        processed_data.append({
            'Title': title,
            'URL': url,
            'Last Updated': last_updated
            # Removed 'Snippet' as per your request
        })
    
    return pd.DataFrame(processed_data)

def main():
    # You need to obtain these:
    api_key = os.getenv('GOOGLE_API_KEY')
    cx = os.getenv('DAILY_CAMPUS_CX')
    if not api_key or not cx:
        print("Please set the GOOGLE_API_KEY and DAILY_CAMPUS_CX environment variables.")
        return

    
          
    # Get search keyword from user
    # keyword = input("Enter your search keyword: ")
    keyword="ছাত্রদল"
    max_results = int(input("Enter maximum number of results to fetch (default: 50): ") or "50")
    
    print(f"Searching for '{keyword}'...")
    results = search_daily_campus(keyword, api_key, cx, max_results)
    
    if not results:
        print("No results found.")
        return
    
    print(f"Found {len(results)} articles. Processing data...")
    df = process_search_data(results)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"daily_campus_search_{keyword}_{timestamp}.xlsx"
    
    # Save to Excel
    df.to_excel(filename, index=False)
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()