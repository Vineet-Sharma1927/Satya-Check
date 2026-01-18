from GoogleNews import GoogleNews
import pandas as pd
import time

print("--- STARTING LIVE NEWS SCRAPING ---")

# 1. Setup Scrapers
# English News (India Region)
googlenews_en = GoogleNews(lang='en', region='IN')
# Hindi News (India Region)
googlenews_hi = GoogleNews(lang='hi', region='IN')

def fetch_news(scraper, query, label_value, count=500):
    print(f"Fetching {count} articles for: '{query}'...")
    scraper.search(query)
    
    all_results = []
    # Loop pages (each page has ~10 results)
    for i in range(1, int(count/10) + 2):
        results = scraper.results()
        if not results:
            break
        
        for item in results:
            title = item.get('title', '')
            desc = item.get('desc', '')
            # Combine title + description for better context
            full_text = f"{title}. {desc}".strip()
            
            if len(full_text) > 20: # Filter short garbage
                all_results.append({'text': full_text, 'label': label_value})
        
        scraper.getpage(i) # Next page
        print(f"   Collected {len(all_results)} so far...")
        time.sleep(1) # Be polite to Google servers
        
    scraper.clear() # Reset for next search
    return all_results

# 2. Execution (Fetch recent Real News = Label 0)
# Topics to ensure variety
topics_en = ["India Politics", "Indian Economy", "ISRO", "Indian Cricket", "Bollywood"]
topics_hi = ["भारत समाचार", "चुनाव", "मौसम", "भारतीय रेलवे", "फिल्म"]

data = []

# Fetch English
for topic in topics_en:
    data.extend(fetch_news(googlenews_en, topic, 0, count=50)) # 50 per topic

# Fetch Hindi
for topic in topics_hi:
    data.extend(fetch_news(googlenews_hi, topic, 0, count=50)) # 50 per topic

# 3. Save
if len(data) > 0:
    df = pd.DataFrame(data)
    # Remove duplicates
    df.drop_duplicates(subset=['text'], inplace=True)
    
    filename = 'dataset/live_real_news.csv'
    df.to_csv(filename, index=False)
    
    print(f"\n[SUCCESS] Scraped {len(df)} unique REAL news articles.")
    print(f"Saved to {filename}")
    print("Now run 'final_data_prep.py' again to include this new data!")
else:
    print("[FAIL] No news found. Check internet connection.")