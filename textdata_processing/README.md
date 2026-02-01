# Fantasy Football Article Scraper & Data Pipeline

This project is a multi-stage data pipeline designed to scrape, parse, filter, and clean fantasy football analysis articles. The goal is to transform unstructured HTML text into a structured JSON dataset where every object represents a specific player and their associated expert analysis.

## 🔄 Pipeline Overview

### 1. The Scraper (`scrape_fantasypros.py`)

**Input:** Target Website URLs (e.g., FantasyPros)
**Output:** `fantasypros_articles.csv`

The entry point of the pipeline. It navigates through paginated article lists and visits individual article links.

* **Logic:** Uses `requests` and `BeautifulSoup` to extract the Title, Author, Date, and Body Text.
* **Keyword Filtering:** Applies "Positive" keywords (e.g., "Buy", "Sell", "Sleeper") to include articles and "Negative" keywords (e.g., "DFS", "Dynasty") to exclude them.
* **Formatting:** Inserts custom tags (`### PLAYER SECTION:`) into the raw text whenever it detects a player header in the HTML, prepping the data for the parser.

### 2. CSV Parser (`parse_csv.py`)

**Input:** `fantasypros_articles.csv`
**Output:** `fantasypros_data.json`

Converts the flat CSV output into a hierarchical JSON format.

* **Structure Creation:** Separates the article's "Intro Text" from individual "Player Analyses."
* **Noise Removal:** Filters out navigation noise (e.g., "Subscribe to Podcast", "Draft Kit links") using a blacklist of phrases.
* **Tag Handling:** Uses the `### PLAYER SECTION:` tags injected by the scraper to create distinct player objects.

### 3. Date Filter (`filter_json_by_date.py`)

**Input:** `fantasypros_data.json`
**Output:** `fantasypros_data_filtered.json`

Ensures the dataset only contains relevant, in-season advice.

* **Logic:** Parses ISO-8601 and standard date strings.
* **Constraint:** Removes any article falling outside the defined "active season" window (e.g., Sept 1st to Jan 20th), discarding off-season speculation and draft content.

### 4. Entity Extraction & Cleaning (`clean_and_combine.py`)

**Input:** Multiple filtered JSON files
**Output:** `all_fantasy_data_cleaned.json`

The most complex logic step. It transforms messy headers into clean player entities.

* **Command Stripping:** Removes actionable advice verbs from names (e.g., "Buy Stefon Diggs"  "Stefon Diggs").
* **Metadata Removal:** Strips roster percentages, matchups, and team codes (e.g., "Daniel Jones | 7% Rostered"  "Daniel Jones").
* **"Or" Handling:** Detects decision headers (e.g., "Alec Pierce or Christian Watson?") and duplicates the analysis object for *both* players so the advice is searchable by either name.
* **Positional Splits:** Takes generic headers (e.g., "Tight Ends") and uses Regex to identify embedded player names within the analysis block, splitting them into separate objects.

### 5. Final Sanitation (`clean_final.py`)

**Input:** `all_fantasy_data_cleaned.json`
**Output:** `all_fantasy_data.json`

A final pass to ensure data integrity.

* **Empty Analysis Check:** Removes any player object that ended up with empty text after processing.
* **Ghost Article Removal:** If an article ends up with `players: []` (because it was an IDP list with no recognized format, or all players were filtered out), the entire article object is removed from the dataset.

---
