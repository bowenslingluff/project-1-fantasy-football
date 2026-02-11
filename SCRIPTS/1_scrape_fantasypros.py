import requests
from bs4 import BeautifulSoup
import csv
import time
import sys

# --- Configuration ---
BASE_LIST_URL = "https://www.fantasypros.com/nfl/articles/?page={}"
START_PAGE = 246
OUTPUT_FILE = "fantasypros_articles.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 1. POSITIVE FILTERS
REQUIRED_TITLE_PHRASE = "Fantasy Football"
KEYWORDS = [
    "buy",
    "sell", "boom", "bust",
    "trade", "trades",
    "value",
    "waiver",
    "sleeper", "start", "sit", "starts", "sits", "players", "advice", "primer", "questions"
]

# 2. NEGATIVE FILTERS (Exclusions)
EXCLUDE_KEYWORDS = ["DFS", "Dynasty", "2026"]

def clean_text(text):
    """Cleans up whitespace and newlines."""
    if not text:
        return ""
    return text.strip()

def contains_keyword(text, keywords):
    """Checks if any keyword exists in the text (case-insensitive)."""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def get_article_content(url):
    """Fetches the article and parses title, date, and formatted body text."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"  Error: Status {response.status_code} for {url}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Title
        title_tag = soup.select_one('h1.general-article__title')
        title = clean_text(title_tag.get_text()) if title_tag else "N/A"

        # 2. Publish Date
        date_meta = soup.select_one('meta[property="article:published_time"]')
        if date_meta:
            publish_date = date_meta.get('content')
        else:
            date_visual = soup.select_one('.general-article__date-container')
            publish_date = clean_text(date_visual.get_text()) if date_visual else "N/A"

        # 3. Body Text
        content_div = soup.select_one('div.general-article__content')
        body_text_parts = []

        if content_div:
            # Iterate through child elements to preserve order
            for element in content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol']):
                
                text = clean_text(element.get_text(separator=' '))
                if not text:
                    continue

                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    player_link = element.select_one('a.fp-player-link')
                    if player_link:
                        body_text_parts.append(f"\n### PLAYER SECTION: {text}")
                    else:
                        body_text_parts.append(f"\n### {text}")
                
                elif element.name == 'p':
                    body_text_parts.append(text)
                
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        body_text_parts.append(f"* {clean_text(li.get_text())}")

        body_text = "\n\n".join(body_text_parts)

        return {
            "url": url,
            "title": title,
            "publish_date": publish_date,
            "body_text": body_text
        }

    except Exception as e:
        print(f"  Exception parsing {url}: {e}")
        return None

def main():
    page_num = START_PAGE
    articles_found_count = 0
    
    with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['url', 'title', 'publish_date', 'body_text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)


        while True:
            print(f"Scraping List Page {page_num}...")
            list_url = BASE_LIST_URL.format(page_num)
            
            try:
                response = requests.get(list_url, headers=HEADERS, timeout=30)
                if response.status_code != 200:
                    print("  Failed to retrieve list page. Stopping.")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                
                article_urls = []
                link_elements = soup.select('div.eight.columns span a')
                
                for link_el in link_elements:
                    href = link_el.get('href')
                    if href:
                        if href.startswith('/'):
                            href = "https://www.fantasypros.com" + href
                        if href not in article_urls:
                            article_urls.append(href)

                if not article_urls:
                    print("  No articles found on this page. Scrape complete.")
                    break

                # Print specific count message as requested
                print(f"Page {page_num}: found {len(article_urls)} candidate articles.")

                for article_url in article_urls:
                    article_data = get_article_content(article_url)
                    
                    if article_data:
                        title_lower = article_data['title'].lower()
                        
                        # --- FILTER 1: Exclusions (DFS, Dynasty, 2026) ---
                        if contains_keyword(article_data['title'], EXCLUDE_KEYWORDS):
                            print(f"    [SKIP] Title contained excluded keyword: {article_data['title']}")
                            continue

                        # --- FILTER 2: Required Phrase "Fantasy Football" ---
                        if REQUIRED_TITLE_PHRASE.lower() not in title_lower:
                            print(f"    [SKIP] Title missing '{REQUIRED_TITLE_PHRASE}': {article_data['title']}")
                            continue
                            
                        # --- FILTER 3: Positive Keywords (Title Only) ---
                        title_match = contains_keyword(article_data['title'], KEYWORDS)

                        if title_match:
                            print(f"    [MATCH] Saving: {article_data['title']}")
                            writer.writerow(article_data)
                            articles_found_count += 1
                        else:
                            print(f"    [SKIP] No positive keywords found in title: {article_data['title']}")
                    
                    time.sleep(2)

                page_num += 1
                time.sleep(2)

            except KeyboardInterrupt:
                print("\nScraping interrupted by user.")
                sys.exit()
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    print(f"Finished. Saved {articles_found_count} articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()