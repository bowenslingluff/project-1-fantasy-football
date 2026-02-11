import json
import re

# --- Configuration ---
INPUT_FILE = "all_fantasy_textdata.json"
OUTPUT_FILE = "text_dataset.json"

# List of strings to filter out if they appear as the "Name"
# Includes Full Names and Nicknames just in case
NFL_TEAMS = {
    "Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills",
    "Carolina Panthers", "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns",
    "Dallas Cowboys", "Denver Broncos", "Detroit Lions", "Green Bay Packers",
    "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Kansas City Chiefs",
    "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
    "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants",
    "New York Jets", "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers",
    "Seattle Seahawks", "Tampa Bay Buccaneers", "Tennessee Titans", "Washington Commanders"
}

def clean_name_string(name):
    """
    Cleans formatting: removes periods and suffixes.
    """
    if not name: return ""
    
    # 1. Remove Periods (e.g. "A.J." -> "AJ")
    # Doing this before suffix check handles "Jr." -> "Jr" automatically
    clean_name = name.replace(".", "")
    
    # 2. Remove Suffixes using Regex
    # Matches word boundaries (\b) for specific suffixes
    # Case insensitive to catch "jr", "JR", "Jr"
    # Suffixes: Jr, Sr, II, III, IV, V
    suffix_pattern = r'\b(jr|sr|ii|iii|iv|v)\b'
    clean_name = re.sub(suffix_pattern, '', clean_name, flags=re.IGNORECASE)
    
    # 3. Final whitespace strip (in case removing suffix left trailing space)
    return clean_name.strip()

def run_cleaning_pipeline():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cleaned_articles = []
        stats = {
            "teams_removed": 0,
            "names_cleaned": 0
        }

        for article in data:
            valid_players = []
            
            for player in article.get("players", []):
                original_name = player.get("name", "")
                
                # Apply text cleaning
                new_name = clean_name_string(original_name)
                
                # --- FILTER 1: Check if it's an NFL Team ---
                # Check case-insensitive match against team list
                if new_name in NFL_TEAMS or new_name.title() in NFL_TEAMS:
                    stats["teams_removed"] += 1
                    continue # Skip this player object entirely
                
                # Update stats if name changed (for logging)
                if new_name != original_name:
                    stats["names_cleaned"] += 1
                
                # Update the player object
                player["name"] = new_name
                valid_players.append(player)
            
            # Only keep article if it still has players
            if valid_players:
                article["players"] = valid_players
                cleaned_articles.append(article)

        # Save to new file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_articles, f, indent=4, ensure_ascii=False)

        print("-" * 30)
        print("Cleaning Complete.")
        print(f"Names Modified (Periods/Suffixes): {stats['names_cleaned']}")
        print(f"Team Entries Removed:              {stats['teams_removed']}")
        print(f"Final Article Count:               {len(cleaned_articles)}")
        print(f"Saved to:                          {OUTPUT_FILE}")
        print("-" * 30)

    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_cleaning_pipeline()