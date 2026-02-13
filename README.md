# NFL Fantasy Football Article Data Analysis Project

This project investigates whether sentiment expressed in fantasy football player outlook articles can help predict NFL player fantasy performance. We apply natural language processing techniques to expert writeups and combine those insights with player performance data to evaluate whether overall sentiment adds predictive value beyond traditional statistics.

## Software and Platform:
This project was developed using the following tools and environment:

## Programming Language
- Python
## Python Packages
- pandas - data manipulation and analysis
- beautifulsoup4 - web scraping and HTML parsing
- requests - retrieving web page content
- ntlk (VADER Sentiment Analyzer) - sentiment scoring of text
- json - handling structured text data
- re (regular expressions) - text cleaning and preprocessing
- csv - reading and writing structured data files
## Platform
- Used macOS

## Repository Structure
This repository follows a simplified structure inspired by the TIER Protocol 4.0 to promote reproducibility and clarity. 

```
project-1-fantasy-football/
│
├── .gitignore                      # Specifies intentionally untracked files
├── LICENSE.md                      # MIT License
├── README.md                       # Project overview and instructions
│
├── DATA/                           # Raw and processed datasets used throughout the pipeline
│   ├── 1_fantasypros_articles.csv
│   ├── 2_ffballers_articles.csv
│   ├── 3_text_dataset.json
│   ├── 4_fantasy_sentiment_scores_2025.csv
│   ├── fantasy_dataset_final.csv
│   └── stats_dataset_2025_cleaned.csv
│
├── OUTPUT/                         # Final analysis notebooks and results
│   ├── DS4002_Project_1_Methodology_and_Evaluation.ipynb
│   └── eda_plots.ipynb
│
└── SCRIPTS/                        # Python scripts implementing the full data pipeline
    ├── 1_scrape_fantasypros.py
    ├── 2_scrape_ffballers.py
    ├── 3_parse_csv_fantasypros.py
    ├── 4_parse_csv_ffballers.py
    ├── 5_filter_json_by_date.py
    ├── 6_analyses_by_name.py
    ├── 7_clean_player_names.py
    ├── 8_sentiment_analysis.py
    ├── 9_merge_sentiment_stats.py
    └── fantasy_25_master_dataset.py
```


## Folder Descriptions

SCRIPTS/
Contains Python scripts and/or notebooks used to:
Collect fantasy football outlook articles
Clean and preprocess text data
Perform sentiment analysis using VADER
Merge sentiment data with player performance statistics
Build and evaluate predictive models

DATA/
Stores all datasets used in the project, which may include:
Raw scraped article text
Cleaned sentiment-scored datasets
Fantasy football player performance data

OUTPUT/
Contains generated results such as:
Processed datasets ready for modeling
Model predictions
Tables, charts, or figures used in analysis


## Reproducing Results

To reproduce the results of our analysis, follow these steps.
**NOTE**: We ran the sentiment analysis BEFORE we created our final dataset, so you will not be able to reproduce the results without recreating the entire dataset. Check out SCRIPTS/sentiment_analysis.py to see the analysis.

1. Clone the git reposity
2. Open the OUTPUT directory, which contains two files:
   - eda_plots.ipynb: Exploratory data analysis and plots we investigated
   - DS4002_Project_1_Methodology_and_Evaluation.ipynb: Full output of our analysis
3. Run the files described above cell by cell to see the results from our analysis

Alternatively,
1. Download the following files:
  - DATA/fantasy_dataset_final.csv
  - DATA/text_dataset.json
  - OUTPUTS/eda_plots.ipynb
  - OUTPUTS/DS4002_Project_1_Methodology_and_Evaluation.ipynb
2. Before Running the notebook files, you will have to adjust the following lines to point to your downloaded datasets.
```python
# Located in the first cell:
INPUT_FILE = "../DATA/3_text_dataset.json"

# Located in the last cell:
df = pd.read_csv('../DATA/fantasy_dataset_final.csv')
```
3. Run the notebook files cell by cell to see the results of the analysis




