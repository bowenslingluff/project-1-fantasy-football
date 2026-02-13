import json
import csv
import re
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# --- CONFIGURATION ---
INPUT_FILE = "text_dataset.json" # Ensure we use the non-draft file
OUTPUT_CSV = "fantasy_sentiment_scores_2025.csv"

# Date Fallback Configuration
DATASET_START = datetime(2025, 8, 15)
WEEK_2_START  = datetime(2025, 9, 9)

# Compiled Regex for speed
TITLE_WEEK_REGEX = re.compile(r'Week\s+(\d+)', re.IGNORECASE)

def get_week_from_title(title_str):
    """Priority Method: Extracts 'Week 16' directly from title."""
    if not title_str: return None
    match = TITLE_WEEK_REGEX.search(title_str)
    if match:
        week_num = int(match.group(1))
        if 1 <= week_num <= 18:
            return week_num
    return None

def get_week_from_date(date_str):
    """Fallback Method: Calculates week based on calendar date."""
    if not date_str: return None, None
    try:
        clean_date_str = date_str.replace("T", " ").split("+")[0].strip()
        if " " in clean_date_str:
            article_date = datetime.strptime(clean_date_str, "%Y-%m-%d %H:%M:%S")
        else:
            article_date = datetime.strptime(clean_date_str, "%Y-%m-%d")

        if article_date < DATASET_START: return None, article_date
        if article_date < WEEK_2_START: return 1, article_date

        delta = article_date - WEEK_2_START
        week_num = (delta.days // 7) + 2
        
        if week_num > 18: return "Postseason", article_date
        return week_num, article_date
    except:
        return None, None

def determine_week(article):
    """
    Orchestrator with Edge Case Handling.
    """
    title = article.get("meta_title", "")
    date_str = article.get("meta_date", "")

    # 1. Try Title First (Most Accurate)
    week_from_title = get_week_from_title(title)
    if week_from_title:
        return week_from_title, "Title"
    
    # 2. Try Date Fallback
    week_from_date, article_date = get_week_from_date(date_str)
    
    if week_from_date and week_from_date != "Postseason":
        # --- EDGE CASE: Waiver Wire Targets on Sun/Mon ---
        # If the title indicates "Waiver Wire" and the date is Sunday (6) or Monday (0),
        # it technically falls in the 'Previous Week' bucket by date logic,
        # but belongs to the 'Next Week' for fantasy purposes.
        if "waiver wire" in title.lower() and article_date:
            # Monday = 0, Sunday = 6
            if article_date.weekday() in [0, 6]: 
                # print(f"Bumped Waiver Article: {title} ({date_str}) -> Week {week_from_date + 1}")
                return week_from_date + 1, "Date_Fallback (Bumped)"

        return week_from_date, "Date_Fallback"
        
    return None, None

def process_data():
    sia = SentimentIntensityAnalyzer()
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        flattened_rows = []
        stats = {"Title": 0, "Date_Fallback": 0, "Date_Fallback (Bumped)": 0, "Dropped": 0}

        print(f"Processing {len(data)} articles...")

        for article in data:
            nfl_week, source = determine_week(article)
            
            if not nfl_week:
                stats["Dropped"] += 1
                continue
            
            # Track source stats
            if source in stats:
                stats[source] += 1
            else:
                stats[source] = 1

            for player in article.get("players", []):
                analysis_text = player.get("analysis", "")
                scores = sia.polarity_scores(analysis_text)
                
                row = {
                    "week": nfl_week,
                    "player_name": player.get("name", ""),
                    "sentiment_compound": scores['compound'], 
                    "sentiment_pos": scores['pos'],           
                    "sentiment_neg": scores['neg'],
                    "sentiment_neu": scores['neu'],
                    "word_count": len(analysis_text.split()),
                    "article_date": article.get("meta_date", ""),
                    "article_title": article.get("meta_title", ""),
                    "article_url": article.get("meta_url", "")
                }
                flattened_rows.append(row)

        if flattened_rows:
            keys = flattened_rows[0].keys()
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(flattened_rows)

            print("-" * 30)
            print("Processing Complete!")
            print(f"Week Source - Title:      {stats.get('Title', 0)}")
            print(f"Week Source - Date Calc:  {stats.get('Date_Fallback', 0)}")
            print(f"Week Source - WW Bumps:   {stats.get('Date_Fallback (Bumped)', 0)}")
            print(f"Articles Dropped:         {stats['Dropped']}")
            print(f"Total Rows Generated:     {len(flattened_rows)}")
            print(f"Saved to:                 {OUTPUT_CSV}")
            print("-" * 30)
        else:
            print("No valid data found.")

    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_data()