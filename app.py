import requests
import pandas as pd
import urllib.parse
import time
from datetime import datetime

def search_prothom_alo(keyword, max_results=100):
    """
    Search Prothom Alo news with a keyword and return all results
    
    Parameters:
        keyword (str): Search keyword
        max_results (int): Maximum number of results to fetch
    
    Returns:
        list: List of news articles
    """
    # URL encode the keyword
    encoded_keyword = urllib.parse.quote(keyword)
    
    # Base URL with parameters
    base_url = "https://www.prothomalo.com/api/v1/advanced-search"
    section_ids = "17532,17533,17535,17536,17538,17552,17553,17555,17556,17560,17562,17563,17566,17567,17568,17569,17570,17571,17572,17573,17584,17585,17586,17587,17588,17589,17591,17599,17600,17602,17606,17678,17679,17680,17681,17682,17683,17684,17685,17686,17687,17688,17689,17690,17691,17693,17694,17695,17696,17697,17698,17699,17700,17701,17702,17704,17705,17706,17708,17709,17714,17717,17736,17737,17738,17739,17743,19182,19183,19184,19185,19195,19196,19197,19198,19199,19200,22236,22237,22321,22323,22324,22325,22326,22327,22328,22329,22330,22332,22333,22334,22335,22336,22337,22338,22339,22340,22341,22342,22349,22350,22351,22352,22362,22363,22364,22365,22368,22515,22516,22517,22518,22519,22520,22575,22701,23230,23382,23383,23426,24541,26653,29465,35621,35622,35623,35624,35625,35626,35867,35868,35871,67467,95322"
    fields = "headline,url,last-published-at"
    
    # Initialize variables
    all_results = []
    offset = 0
    limit = 25  # API seems to use this as default batch size
    
    while offset < max_results:
        # Construct the complete URL
        url = f"{base_url}?section-id={section_ids}&q={encoded_keyword}&offset={offset}&limit={limit}&fields={fields}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            items = data.get('items', [])
            total_results = data.get('total', 0)
            
            # Break if no more results
            if not items:
                break
                
            all_results.extend(items)
            print(f"Fetched {len(items)} results. Total so far: {len(all_results)} of {total_results}")
            
            # Update offset for next batch
            offset += limit
            
            # Check if we've reached the max_results limit or total available results
            if len(all_results) >= max_results or len(all_results) >= total_results:
                all_results = all_results[:max_results]
                break
                
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching results: {e}")
            break
    
    return all_results

def process_article_data(articles):
    """Process raw article data into a pandas DataFrame"""
    processed_data = []
    
    for article in articles:
        # Extract the specific fields we need
        title = article.get('headline', '')
        url = article.get('url', '')
        
        # Process the last-published-at timestamp
        last_updated_timestamp = article.get('last-published-at')
        last_updated = None
        if last_updated_timestamp:
            try:
                # Convert milliseconds timestamp to datetime
                last_updated = datetime.fromtimestamp(last_updated_timestamp / 1000)
            except:
                # Fallback if the timestamp format is different
                try:
                    last_updated = datetime.fromisoformat(str(last_updated_timestamp).replace('Z', '+00:00'))
                except:
                    last_updated = str(last_updated_timestamp)
        
        # Add to processed data
        processed_data.append({
            'Title': title,
            'URL': url,
            'Last Updated': last_updated
        })
    
    return pd.DataFrame(processed_data)

def main():
    # Get search keyword from user
    # keyword = input("Enter your search keyword: ")
    keyword = "ছাত্রদল"
    max_results = int(input("Enter maximum number of results to fetch (default: 100): ") or "100")
    
    print(f"Searching for '{keyword}'...")
    articles = search_prothom_alo(keyword, max_results)
    
    if not articles:
        print("No results found.")
        return
    
    print(f"Found {len(articles)} articles. Processing data...")
    df = process_article_data(articles)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prothomalo_search_{keyword}_{timestamp}.xlsx"
    
    # Save to Excel
    df.to_excel(filename, index=False)
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()