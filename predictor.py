# predictor.py

import pandas as pd
import joblib
import nfl_data_py as nfl
# from pathlib import Path
from data_processor import calculate_team_averages

model = joblib.load("nfl_lr_model.pkl")

def get_week_matchups(year, week_num):
    schedule = nfl.import_schedules([year])
    return schedule[schedule['week'] == week_num][['home_team', 'away_team']]

def predict_weekly_scores(year, week_num):
    calculate_team_averages()
    team_averages = pd.read_csv("nfl_team_current_year_averages.csv")
    weekly_matchups = get_week_matchups(year, week_num)
    predictions = []

    for _, game in weekly_matchups.iterrows():
        home_team = game['home_team']
        away_team = game['away_team']

        # Get stats for home and away teams
        home_stats = team_averages[team_averages['posteam'] == home_team].iloc[0]
        away_stats = team_averages[team_averages['posteam'] == away_team].iloc[0]

        # Prepare features for both teams
        match_data = {
            'passing_yards': [(home_stats['avg_passing_yards'] + away_stats['avg_passing_yards_allowed']) / 2, (away_stats['avg_passing_yards'] + home_stats['avg_passing_yards_allowed']) / 2],
            'rushing_yards': [(home_stats['avg_rushing_yards'] + away_stats['avg_rushing_yards_allowed']) / 2, (away_stats['avg_rushing_yards'] + home_stats['avg_rushing_yards_allowed']) / 2],
            'first_downs': [home_stats['avg_first_downs'], away_stats['avg_first_downs']],
            'giveaways': [home_stats['avg_giveaways'], away_stats['avg_giveaways']],
            'takeaways': [home_stats['avg_takeaways'], away_stats['avg_takeaways']],
            'passing_yards_allowed': [away_stats['avg_passing_yards_allowed'], home_stats['avg_passing_yards_allowed']],
            'rushing_yards_allowed': [away_stats['avg_rushing_yards_allowed'], home_stats['avg_rushing_yards_allowed']]
        }
        
        # Convert to DataFrame
        match_df = pd.DataFrame(match_data)

        # Predict scores
        predicted_scores = model.predict(match_df)
        home_team_score = round(predicted_scores[0] * 2) / 2
        away_team_score = round(predicted_scores[1] * 2) / 2
        total_score = round((home_team_score + away_team_score) * 2) / 2

        predictions.append({
            'home_team': home_team,
            'home_team_score': home_team_score,
            'away_team': away_team,
            'away_team_score': away_team_score,
            'total': total_score
        })

    predictions = pd.DataFrame(predictions)

    # Format predictions as desired
    formatted_predictions = {
        i: {
            'home_team': row['home_team'],
            'home_team_score': row['home_team_score'],
            'away_team': row['away_team'],
            'away_team_score': row['away_team_score'],
            'total': row['total']
        } for i, row in predictions.iterrows()
    }

    return formatted_predictions