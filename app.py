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
    fields = "headline,subheadline,slug,url,tags,hero-image-s3-key,hero-image-caption,hero-image-metadata,last-published-at,alternative,authors,author-name,author-id,sections,story-template,metadata,hero-image-attribution,access"
    
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
            
            # Break if no more results
            if not items:
                break
                
            all_results.extend(items)
            print(f"Fetched {len(items)} results. Total so far: {len(all_results)}")
            
            # Update offset for next batch
            offset += limit
            
            # Check if we've reached the max_results limit
            if len(all_results) >= max_results:
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
        # Extract basic information
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        url = article.get('url', '')
        
        # Extract publication date
        published_at = article.get('last-published-at', '')
        if published_at:
            try:
                # Convert to datetime for better Excel formatting
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except:
                pass
        
        # Extract author information
        authors = article.get('authors', [])
        author_names = []
        for author in authors:
            if isinstance(author, dict):
                author_name = author.get('name', '')
                if author_name:
                    author_names.append(author_name)
        author_string = ', '.join(author_names)
        
        # Extract tags
        tags = article.get('tags', [])
        tags_string = ', '.join(tags) if tags else ''
        
        # Add to processed data
        processed_data.append({
            'Headline': headline,
            'Subheadline': subheadline,
            'URL': url,
            'Published Date': published_at,
            'Authors': author_string,
            'Tags': tags_string
        })
    
    return pd.DataFrame(processed_data)

def main():
    # Get search keyword from user
    keyword = input("Enter your search keyword: ")
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