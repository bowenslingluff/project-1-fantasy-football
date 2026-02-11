import csv
import json
import re

INPUT_CSV = "ffballers_articles.csv"
OUTPUT_JSON = "ffballers_data.json"

# Regex patterns for fallback parsing
# Matches: "Michael Wilson– 16 targets" or "Michael Wilson - 16 targets"
TARGET_TRENDS_RE = re.compile(r"^(.+?)[–-]\s*\d+\s*targets", re.IGNORECASE)
# Matches: "QB – Matthew Stafford" or "RB - James Robinson"
STARTS_RE = re.compile(r"^(QB|RB|WR|TE|DEF|K)\s*[–-]\s*(.+)", re.IGNORECASE)

def clean_name_from_starts(raw_text):
    """
    Cleans messy scraping like 'Matthew Stafford@ SEA' -> 'Matthew Stafford'
    """
    parts = re.split(r'\s(?:vs\.?|@)\s?', raw_text, maxsplit=1, flags=re.IGNORECASE)
    return parts[0].strip()

def clean_header_standard(header_text):
    """
    Parses 'Player Name, Position, Team' -> 'Player Name'
    """
    header_text = header_text.strip()
    if "," in header_text:
        parts = header_text.split(",")
        return parts[0].strip(), header_text
    return header_text, header_text

def convert_csv_to_json():
    articles_data = []
    
    stats = {"standard": 0, "targets": 0, "starts": 0, "skipped": 0}

    try:
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                title = row["title"]
                
                # SKIP DFS Articles
                if any(x in title.upper() for x in ["DRAFTKINGS", "FANDUEL", "DFS", "BETTING"]):
                    stats["skipped"] += 1
                    continue

                full_text = row["body_text"]
                players_list = []
                intro_text = ""

                # --- STRATEGY 1: Standard ### PLAYER SECTION ---
                if "### PLAYER SECTION:" in full_text:
                    stats["standard"] += 1
                    segments = full_text.split("### PLAYER SECTION:")
                    intro_text = segments[0].strip()

                    for segment in segments[1:]:
                        parts = segment.strip().split("\n", 1)
                        raw_header = parts[0].strip()
                        analysis_text = parts[1].strip() if len(parts) > 1 else ""
                        
                        name, _ = clean_header_standard(raw_header)
                        
                        if any(x in name for x in ["Week", "Takeaways", "Players to"]):
                            continue

                        players_list.append({
                            "name": name,
                            "raw_header": raw_header,
                            "analysis": analysis_text,
                            "type": "Standard"
                        })

                # --- STRATEGY 2: Line-by-Line Scanning (Fallbacks) ---
                else:
                    lines = full_text.split("\n")
                    current_player = None  # Keep as None to track Intro vs Player
                    current_analysis = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line: continue

                        target_match = TARGET_TRENDS_RE.match(line)
                        start_match = STARTS_RE.match(line)

                        if target_match:
                            # SAVE PREVIOUS PLAYER (Safety check added)
                            if current_player is not None:
                                current_player["analysis"] = "\n".join(current_analysis).strip()
                                players_list.append(current_player)
                            
                            # START NEW PLAYER
                            name = target_match.group(1).strip()
                            current_player = {
                                "name": name,
                                "raw_header": line,
                                "analysis": "",
                                "type": "Target Trend"
                            }
                            current_analysis = []
                            stats["targets"] += 1

                        elif start_match:
                            # SAVE PREVIOUS PLAYER (Safety check added)
                            if current_player is not None:
                                current_player["analysis"] = "\n".join(current_analysis).strip()
                                players_list.append(current_player)

                            # START NEW PLAYER
                            raw_name_part = start_match.group(2).strip()
                            name = clean_name_from_starts(raw_name_part)
                            
                            current_player = {
                                "name": name,
                                "raw_header": line,
                                "analysis": "",
                                "type": "Start/Sit"
                            }
                            current_analysis = []
                            stats["starts"] += 1
                        
                        else:
                            # APPEND TEXT
                            if current_player is not None:
                                current_analysis.append(line)
                            else:
                                # If current_player is None, we are in the Intro
                                intro_text += line + "\n"

                    # SAVE FINAL PLAYER (Safety check added)
                    if current_player is not None:
                        current_player["analysis"] = "\n".join(current_analysis).strip()
                        players_list.append(current_player)

                # Add to final dataset if we found players
                if players_list:
                    articles_data.append({
                        "meta_title": title,
                        "meta_url": row["url"],
                        "meta_date": row["publish_date"],
                        "intro_text": intro_text.strip(),
                        "players": players_list
                    })

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(articles_data, f, indent=4, ensure_ascii=False)

        print(f"Processed {len(articles_data)} articles.")
        print(f"Stats: Standard={stats['standard']}, TargetTrends={stats['targets']}, Starts={stats['starts']}, Skipped(DFS)={stats['skipped']}")

    except FileNotFoundError:
        print("CSV file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    convert_csv_to_json()