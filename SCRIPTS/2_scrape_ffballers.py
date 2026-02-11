import time
import csv
import re
import requests
from bs4 import BeautifulSoup

BASE_LIST_URL = "https://www.thefantasyfootballers.com/fantasy-football-articles/page/{page}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}

# Keywords to identify predictive / start-sit style articles
KEYWORDS = [
    "start", "sit", "picks", "options", "target", "consider",
    "starts", "sits", "start/sit", "smash", "bust", "boom", "fade", "fades", "streamers", "sleepers"
]
KEYWORD_RE = re.compile(r"|".join(KEYWORDS), re.IGNORECASE)

def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def extract_article_links_from_list_page(soup):
    links = []
    
    # Updated selector to target the specific grid used on their site
    # We also keep 'article a' just in case they mix formats, but the grid is the priority
    selectors = "div.ffb-post-grid--post > a, article a"
    
    for a in soup.select(selectors):
        href = a.get("href")
        
        # In the HTML provided, the title is inside an <h3> inside the <a> tag
        # .get_text(strip=True) will correctly pull "Title" from <h3>Title</h3> inside the link
        title = a.get_text(strip=True)

        if "DFS" in title.upper():
            continue
        
        if not href or not href.startswith("https://www.thefantasyfootballers.com/"):
            continue
            
        # Filter by keyword in title
        if KEYWORD_RE.search(title):
            links.append((title, href))
            
    return links

def extract_article_text(soup):
    # Target the container
    content_area = soup.select_one("div.ffb-dynamic-ads") or soup.select_one("section.article")
    
    if not content_area:
        return ""

    # Clean up ads/scripts
    for tag in content_area.find_all(["script", "style", "div.ffb-ad"]):
        tag.decompose()
    
    text_parts = []
    
    # Loop through all child elements (paragraphs, headers, divs)
    for element in content_area.find_all(recursive=False):
        # IF we find a Header (Player Name), add a special marker
        if element.name in ['h2', 'h3', 'h4']:
            # "### PLAYER SECTION: " is a unique string we can split on later
            header_text = element.get_text(strip=True)
            text_parts.append(f"\n### PLAYER SECTION: {header_text}\n")
            
        # IF we find a Paragraph, just add the text
        elif element.name == 'p':
            text_parts.append(element.get_text(strip=True))
            
        # IF we find a list (bullet points), handle items
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                text_parts.append(f" - {li.get_text(strip=True)}")
                
    # Join everything with newlines
    return "\n".join(text_parts)

def extract_publish_date(soup):
    # Method 1: Try the reliable meta tag first (ISO format)
    meta_date = soup.find("meta", property="article:published_time")
    if meta_date and meta_date.get("content"):
        return meta_date["content"]
    
    # Method 2: Fallback to the visible <time> tag
    time_tag = soup.select_one(".author--date time")
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"]
        
    return "N/A"

def crawl_articles(max_pages=10, delay=2.0, output_csv="ffballers_articles.csv"):
    seen_urls = set()
    rows = []

    for page in range(1, max_pages + 1):
        list_url = BASE_LIST_URL.format(page=page)
        try:
            soup = get_soup(list_url)
        except Exception as e:
            print(f"Error fetching list page {page}: {e}")
            break

        article_links = extract_article_links_from_list_page(soup)

        print(f"Page {page}: found {len(article_links)} candidate articles.")

        for title, url in article_links:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            time.sleep(delay)  # be polite

            try:
                article_soup = get_soup(url)
                body_text = extract_article_text(article_soup)
                pub_date = extract_publish_date(article_soup)
            except Exception as e:
                print(f"Error fetching article {url}: {e}")
                continue

            rows.append({
                "url": url,
                "title": title,
                "publish_date": pub_date,
                "body_text": body_text
            })
            print(f"Scraped: {title} | Date: {pub_date}")

    # Write to CSV
    fieldnames = ["url", "title", "publish_date", "body_text"]
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for row in rows:
            writer.writerow(row)

    print(f"Saved {len(rows)} articles to {output_csv}")

if __name__ == "__main__":
    crawl_articles(max_pages=10, delay=3.0)
