import pandas as pd
import re
import unicodedata

# --- CONFIGURATION ---
STATS_FILE = "fantasy_2025_all_players_CLEANED_v2.csv"
SENTIMENT_FILE = "fantasy_sentiment_scores_2025.csv"
OUTPUT_FILE = "fantasy_dataset.csv"

def clean_name_nuclear(name):
    """
    Aggressive cleaning to handle edge cases like:
    - "Audric Estimé" -> "audric estime" (Removes accents)
    - "Wan'Dale Robinson" -> "wandale robinson" (Removes apostrophe)
    - "A.J. Brown" -> "aj brown" (Removes periods)
    - "Kenneth Walker III" -> "kenneth walker" (Removes suffixes)
    """
    if not isinstance(name, str): return ""
    
    # 1. Normalize Unicode characters (Decompose accents)
    # e.g., "é" becomes "e" + combining accent
    name = unicodedata.normalize('NFKD', name)
    
    # 2. Encode to ASCII and ignore errors (Strips the combining accents)
    # "Estimé" -> "Estime"
    name = name.encode('ASCII', 'ignore').decode('utf-8')
    
    # 3. Lowercase
    name = name.lower()
    
    # 4. Remove Suffixes (Jr, Sr, III, etc.) BEFORE removing punctuation
    # We use \b to ensure we don't match inside words
    suffix_pattern = r'\b(jr|sr|ii|iii|iv|v)\b'
    name = re.sub(suffix_pattern, '', name)
    
    # 5. Remove ALL non-alphanumeric characters except spaces
    # This removes apostrophes, periods, hyphens, etc.
    # "wan'dale" -> "wandale", "a.j." -> "aj"
    name = re.sub(r'[^a-z0-9\s]', '', name)
    
    # 6. Normalize whitespace (remove extra spaces created by deletions)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def merge_datasets():
    print("Loading datasets...")
    try:
        df_stats = pd.read_csv(STATS_FILE)
        df_sentiment = pd.read_csv(SENTIMENT_FILE)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # --- APPLY CLEANING TO BOTH DATASETS ---
    print("Applying 'Nuclear' name cleaning...")
    
    # Create temporary join columns
    df_stats['join_name'] = df_stats['PlayerName'].apply(clean_name_nuclear)
    df_sentiment['join_name'] = df_sentiment['player_name'].apply(clean_name_nuclear)
    
    # Ensure weeks are integers
    df_stats['week'] = pd.to_numeric(df_stats['week'], errors='coerce').fillna(0).astype(int)
    df_sentiment['week'] = pd.to_numeric(df_sentiment['week'], errors='coerce').fillna(0).astype(int)

    # --- PERFORM MERGE ---
    print(f"Merging {len(df_sentiment)} sentiment rows with stats...")
    
    merged_df = pd.merge(
        df_sentiment, 
        df_stats, 
        on=['join_name', 'week'], 
        how='left'
    )

    # --- DIAGNOSTICS ---
    missing_stats = merged_df['TotalPoints'].isna().sum()
    match_rate = ((len(merged_df) - missing_stats) / len(merged_df)) * 100

    if 'PlayerName' in merged_df.columns:
        merged_df = merged_df.drop(columns=['PlayerName'])

    print("-" * 30)
    print("MERGE COMPLETE")
    print("-" * 30)
    print(f"Total Rows:              {len(merged_df)}")
    print(f"Match Success Rate:      {match_rate:.1f}%")
    print(f"Missing Stats (NaN):     {missing_stats}")

    if missing_stats > 0:
        print("\nTop 10 Unmatched Names (Cleaned):")
        print(merged_df[merged_df['TotalPoints'].isna()]['join_name'].value_counts().head(10))

    # Clean up columns (remove the temporary 'join_name')
    if 'join_name' in merged_df.columns:
        merged_df = merged_df.drop(columns=['join_name'])

    merged_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_datasets()