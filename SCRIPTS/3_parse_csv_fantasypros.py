import csv
import json

# --- Configuration ---
INPUT_CSV = "fantasypros_articles.csv"
OUTPUT_JSON = "fantasypros_data.json"

# Phrases that indicate a line is "junk" or navigation noise to be removed
NOISE_PHRASES = [
    "Fantasy Football Draft Kit",
    "Fantasy Football Rankings",
    "Dynasty Fantasy Football Draft Kit",
    "Mock Draft Simulator",
    "Expert Accuracy Rankings",
    "Apple Podcasts",
    "Spotify",
    "SoundCloud",
    "iHeartRadio",
    "Consensus Rankings",
    "Subscribe",
    "Check out the",
    "Contact us"
]

def is_noise_line(line):
    """
    Checks if a line is likely unwanted navigation/footer text.
    """
    for phrase in NOISE_PHRASES:
        if phrase.lower() in line.lower():
            return True
    return False

def clean_player_name(raw_header):
    """
    Extracts the player name from the header.
    Example: "Chris Rodriguez Jr., RB,Washington Commanders" -> "Chris Rodriguez Jr."
    """
    text = raw_header.replace("PLAYER SECTION:", "").strip()
    if "," in text:
        parts = text.split(",")
        return parts[0].strip()
    return text.strip()

def parse_csv_to_json():
    articles_data = []
    
    try:
        with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Basic Metadata
                url = row.get("url", "")
                title = row.get("title", "")
                date = row.get("publish_date", "")
                body_text = row.get("body_text", "")
                
                # --- Reset variables for the new article ---
                intro_text_lines = []
                players_list = []
                current_player = None  # Always starts as None
                
                # Split body text by lines
                lines = body_text.split("\n")
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # 1. Filter Noise
                    if line.startswith("*") and is_noise_line(line):
                        continue
                    if is_noise_line(line) and len(line) < 50: # strict check for short noise lines
                        continue

                    # 2. Detect Player Section
                    if "### PLAYER SECTION:" in line:
                        # --- SAVE PREVIOUS PLAYER ---
                        if current_player is not None:
                            # Safety check: Ensure current_player is a dict before assignment
                            if isinstance(current_player, dict):
                                full_analysis = "\n\n".join(current_player.get("analysis_lines", [])).strip()
                                current_player["analysis"] = full_analysis
                                # Cleanup temporary key
                                if "analysis_lines" in current_player:
                                    del current_player["analysis_lines"]
                                players_list.append(current_player)
                            else:
                                print(f"Warning: current_player was not a dict: {type(current_player)}")
                        
                        # --- START NEW PLAYER ---
                        raw_header = line.split("### PLAYER SECTION:", 1)[1].strip()
                        current_player = {
                            "name": clean_player_name(raw_header),
                            "raw_header": raw_header,
                            "analysis_lines": [], # Initialize list to hold text lines
                            "type": "Standard"
                        }
                        continue

                    # 3. Detect Other Headers (preserve structure)
                    if line.startswith("###"):
                        clean_line = line.replace("###", "").strip()
                        # Add bold header to whichever section we are in
                        formatted_line = f"\n**{clean_line}**"
                        
                        if current_player and isinstance(current_player, dict):
                            current_player["analysis_lines"].append(formatted_line)
                        else:
                            intro_text_lines.append(formatted_line)
                        continue

                    # 4. Standard Text Content
                    if current_player and isinstance(current_player, dict):
                        current_player["analysis_lines"].append(line)
                    else:
                        intro_text_lines.append(line)

                # --- SAVE LAST PLAYER (After loop finishes) ---
                if current_player is not None and isinstance(current_player, dict):
                    full_analysis = "\n\n".join(current_player.get("analysis_lines", [])).strip()
                    current_player["analysis"] = full_analysis
                    if "analysis_lines" in current_player:
                        del current_player["analysis_lines"]
                    players_list.append(current_player)

                # Construct Final Article Object
                article_obj = {
                    "meta_title": title,
                    "meta_url": url,
                    "meta_date": date,
                    "intro_text": "\n\n".join(intro_text_lines).strip(),
                    "players": players_list
                }
                
                articles_data.append(article_obj)

        # Write to JSON
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(articles_data, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully processed {len(articles_data)} articles into {OUTPUT_JSON}")

    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parse_csv_to_json()