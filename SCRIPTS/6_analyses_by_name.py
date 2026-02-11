import json
import re

# --- Configuration ---
INPUT_FILES = [
    "fantasypros_data_filtered.json", 
    "ffballers_data_filtered.json"
]
OUTPUT_FILE = "all_fantasy_data_cleaned.json"

# Stop Words and Commands to strip
COMMANDS = {"Add", "Buy", "Sell", "Drop", "Hold", "Start", "Sit"}
STOP_WORDS = {
    "Is", "Are", "Do", "Does", "Should", "Can", "Will", "Too", "Risky", "Safe", "Bet", 
    "Against", "With", "Without", "In", "For", "The", "A", "An", "Vs", 
    "Week", "Fantasy", "Football", "Trade", "Target", "Waiver", "Wire", 
    "Low", "High", "You", "Why", "On", "Rankings", "Advice", "Draft", "Mock", "Sleepers", 
    "Busts", "Or", "And", "Players", "To", "From", "Of", "Be", 
    "Treated", "As", "Locked-In", "Option", "ADP", "Rostered", "Gamers", "Trust", "Go", "Back", "Well"
}

POSITIONS = {
    "Quarterbacks", "Running Backs", "Wide Receivers", "Tight Ends", 
    "Defenses", "Kickers", "Sleepers", "Busts", "Streamers", "Rankings", "Flex"
}

# Metadata terms that indicate a split part is NOT a player name
METADATA_INDICATORS = {"rostered", "adp", "%", "owned"}

def clean_single_name(text):
    """
    Cleans a single name string. e.g. "Add Kimani Vidal" -> "Kimani Vidal"
    """
    if not text: return "Unknown"
    text = text.strip()
    
    # Strip numbering "1. Name"
    text = re.sub(r'^\d+\.\s*', '', text)
    # Strip Parentheses
    text = re.sub(r'\s*\([^)]*\).*', '', text) 
    # Strip vs/@
    text = re.split(r'\s+(?:vs\.?|@)\s+', text, flags=re.IGNORECASE)[0]
    
    words = text.split()
    # Remove leading command word if present
    if words and words[0] in COMMANDS:
        words.pop(0)
    
    # Reassemble and clean
    text = " ".join(words).strip()
    
    # Heuristic for "Sentence" headers
    if len(text.split()) > 3 or "?" in text:
        cap_sequences = []
        current_seq = []
        words = text.split()
        for w in words:
            clean_w = re.sub(r'[^\w\-\.]', '', w)
            if not clean_w: continue
            
            if w[0].isupper() and clean_w not in STOP_WORDS and clean_w not in COMMANDS:
                current_seq.append(clean_w)
            else:
                if current_seq:
                    cap_sequences.append(" ".join(current_seq))
                    current_seq = []
        if current_seq: cap_sequences.append(" ".join(current_seq))
        
        for seq in cap_sequences:
            if " " in seq: return seq 
        if cap_sequences: return cap_sequences[0]

    return text.strip()

def split_complex_header(text):
    """
    Splits headers like:
    - "Add Jordan Whittington & Jarquez Hunter" -> ["Jordan Whittington", "Jarquez Hunter"]
    - "Daniel Jones | 29.7% Rostered" -> ["Daniel Jones"] (Filters out Rostered)
    """
    text = text.replace("?", "")
    
    # Define delimiters: |, &, " or ", " vs "
    parts = re.split(r'\s+(?:\||&|or|vs\.?)\s+', text, flags=re.IGNORECASE)
    
    cleaned_names = []
    for p in parts:
        # --- NEW FILTER ---
        # Check if this part contains metadata keywords BEFORE cleaning
        if any(indicator in p.lower() for indicator in METADATA_INDICATORS):
            continue

        name = clean_single_name(p)
        
        # Valid name checks:
        # 1. Must be longer than 2 chars
        # 2. Must not be just a digit or symbol
        if name and name != "Unknown" and len(name) > 2 and not name.replace(".","").isdigit():
            cleaned_names.append(name)
            
    return cleaned_names

def split_positional_analysis(raw_analysis, position_header):
    """
    Splits a big block of text (e.g. under "Tight Ends") into individual player objects.
    """
    players_found = []
    lines = raw_analysis.split('\n')
    current_player_name = None
    current_player_text = []
    
    embedded_header_re = re.compile(r'^([A-Z][a-zA-Z\.\s]+)(QB|RB|WR|TE|DEF|K)\s*-\s*[A-Z]{2,3}')

    for line in lines:
        line = line.strip()
        if not line: continue
        
        match = embedded_header_re.match(line)
        if match:
            if current_player_name:
                players_found.append({
                    "name": current_player_name,
                    "raw_header": position_header,
                    "analysis": "\n".join(current_player_text).strip(),
                    "type": "Standard"
                })
            current_player_name = match.group(1).strip()
            current_player_text = [line]
        else:
            if current_player_name:
                current_player_text.append(line)

    if current_player_name:
        players_found.append({
            "name": current_player_name,
            "raw_header": position_header,
            "analysis": "\n".join(current_player_text).strip(),
            "type": "Standard"
        })
        
    return players_found

def process_and_combine():
    all_articles_combined = []
    
    for input_file in INPUT_FILES:
        try:
            print(f"Processing {input_file}...")
            with open(input_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            for article in articles:
                if "players" not in article: continue
                    
                new_players_list = []
                
                for player in article["players"]:
                    original_name = player.get("name", "")
                    analysis_text = player.get("analysis", "")
                    
                    # 1. Positional Groups
                    if original_name in POSITIONS:
                        extracted = split_positional_analysis(analysis_text, original_name)
                        if extracted:
                            new_players_list.extend(extracted)
                        else:
                            new_players_list.append(player)
                            
                    # 2. Complex Headers / Splits
                    elif any(sep in original_name.lower() for sep in ["|", "&", " or ", " vs "]):
                        names_found = split_complex_header(original_name)
                        
                        if len(names_found) >= 1:
                            for n in names_found:
                                new_p = player.copy()
                                new_p["name"] = n
                                new_players_list.append(new_p)
                        else:
                            # Fallback if everything was filtered out (unlikely, but safe)
                            # or if cleaning returned nothing valid
                            if not names_found:
                                # Try basic cleaning on original name just in case
                                cleaned = clean_single_name(original_name)
                                if cleaned and cleaned != "Unknown":
                                    new_p = player.copy()
                                    new_p["name"] = cleaned
                                    new_players_list.append(new_p)
                            
                    # 3. Standard
                    else:
                        cleaned = clean_single_name(original_name)
                        new_p = player.copy()
                        new_p["name"] = cleaned
                        new_players_list.append(new_p)
                
                article["players"] = new_players_list
                all_articles_combined.append(article)

        except Exception as e:
            print(f"  Error processing {input_file}: {e}")

    # Save Combined Output
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_articles_combined, f, indent=4, ensure_ascii=False)
        print(f"\nSuccess! All data combined and saved to {OUTPUT_FILE}")
        print(f"Total Articles: {len(all_articles_combined)}")
    except Exception as e:
        print(f"Error saving output file: {e}")

if __name__ == "__main__":
    process_and_combine()