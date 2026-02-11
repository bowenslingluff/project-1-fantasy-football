import json
from datetime import datetime

# --- Configuration ---
INPUT_FILE = "ffballers_data.json"
OUTPUT_FILE = "ffballers_data_filtered.json"

# Define the Date Range for the active NFL Season
# Format: Year, Month, Day
SEASON_START = datetime(2025, 8, 15)   # Start of Season (approx)
SEASON_END = datetime(2026, 1, 20)    # End of Season / Playoffs

def parse_date(date_str):
    """
    Parses date strings from the JSON.
    Handles standard "YYYY-MM-DD HH:MM:SS" and ISO format "YYYY-MM-DDTHH:MM:SS..."
    """
    if not date_str:
        return None
    
    try:
        # Clean up the string to handle ISO format with 'T' and timezone info
        # Example: "2025-12-11T11:30:41+00:00" -> "2025-12-11 11:30:41"
        clean_str = date_str.replace("T", " ").split("+")[0].strip()
        
        # Parse standard format
        return datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Fallback for just dates "YYYY-MM-DD" if time is missing
            return datetime.strptime(clean_str, "%Y-%m-%d")
        except ValueError:
            return None

def filter_json():
    try:
        # 1. Load the JSON data
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"Loaded {len(articles)} articles from {INPUT_FILE}.")
        
        filtered_articles = []
        skipped_count = 0
        
        # 2. Iterate and Filter
        for article in articles:
            date_str = article.get("meta_date", "")
            article_date = parse_date(date_str)
            
            if article_date:
                # Check if date is within range
                if SEASON_START <= article_date <= SEASON_END:
                    filtered_articles.append(article)
                else:
                    skipped_count += 1
                    # Optional: Print what was skipped to verify
                    # print(f"Skipping (Out of Season): {article.get('meta_title')} [{date_str}]")
            else:
                # If no valid date, you can decide to keep or skip. 
                # Here we skip articles with invalid/missing dates.
                print(f"Skipping (No Date): {article.get('meta_title')}")
                skipped_count += 1

        # 3. Save to new JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(filtered_articles, f, indent=4, ensure_ascii=False)
            
        # 4. Print Statistics
        print("\n--- Filtering Complete ---")
        print(f"Original Count: {len(articles)}")
        print(f"Kept (In Season): {len(filtered_articles)}")
        print(f"Removed (Out of Range): {skipped_count}")
        print(f"Date Range Applied: {SEASON_START.date()} to {SEASON_END.date()}")
        print(f"Saved to: {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILE}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    filter_json()