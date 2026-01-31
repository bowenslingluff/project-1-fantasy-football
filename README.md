# NFL Fantasy Football Article Data Analysis Project

DS 4002: NBA All Stars – Bowen Slingluff, Nick Larson, Andrew Patterson – 1/30/2026

## Goal Statement:
Evaluate how sentiment in fantasy football media contributes to real world performance for NFL players.

## Research Question:
Can sentiment in player outlook writeups/articles predict fantasy football performance for NFL players in a moderately positively correlated way (R=0.40-0.59)?

## Motivation:
Fantasy football is a major way fans engage with the NFL, with millions of participants relying on expert analysis to make their roster decisions. Every week, reporters and journalists provide predictions about NFL player performance for the upcoming week and suggestions for fantasy football players. As a group, we are all interested in football and have played fantasy football before. 

We are constantly looking for ways to accurately predict the outcome of NFL games. A positive correlation could impact specific platforms/writers that are able to predict performance and could impact NFL media, sports betting, and prediction markets. We are curious whether positive sentiment towards a player correlates with better performance (TDs, Yards, Receptions, etc.).

## Modeling Approach:
First, we will collect weekly player outlook articles from fantasy football media sources. [1,2] Using natural language processing techniques, we will quantify sentiment toward individual players within these articles. This analysis will include rule based sentiment scoring using tools such as VADER [3], and transformer based models like BERT [4] to classify sports specific text and capture dimensions such as confidence and subjectivity. For VADER analysis, sentiment scores will be interpreted on a continuous scale ranging from −1 (most negative) to +1 (most positive), with compound scores between −0.05 and 0.05 classified as neutral sentiment. BERT outputs will be used to generate probabilistic sentiment classifications, allowing for comparison between discrete sentiment categories and continuous sentiment scores. The resulting sentiment metrics will then be integrated with player performance data, including offensive statistics, fantasy points, and  usage rates. Regression based models will then be used to compare actual player statistics against analysts sentiment. 

## References:
[1] “Fantasy Football Articles,” Fantasy Footballers Podcast, Fantasy Football Articles, https://www.thefantasyfootballers.com/fantasy-football-articles/ (accessed Jan. 29, 2026).
[2] “NFL Fantasy Articles,” FantasyPros, Fantasy Football Articles and Advice, https://www.fantasypros.com/nfl/articles/ (accessed Jan. 29, 2026).
[3] “Welcome to Vadersentiment’s documentation!,” VaderSentiment 3.3.1 documentation,
https://vadersentiment.readthedocs.io/en/latest/ (accessed Jan. 28, 2026).
[4] “BERT,” Hugging Face Transformers documentation, https://huggingface.co/docs/transformers/main/model_doc/bert  (accessed Jan. 30, 2026).
