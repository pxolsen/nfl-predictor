# data_processor.py

import nfl_data_py as nfl
import pandas as pd

def generate_team_stats_for_years(years):
    all_team_game_stats = []

    for year in years:
        pbp_data = nfl.import_pbp_data([year])

        # Filter the data to relevant columns
        stats_df = pbp_data[['game_id', 'posteam', 'defteam', 'passing_yards', 'rushing_yards', 'first_down', 'interception', 'fumble_lost', 'posteam_score']]

        # Aggregate offensive stats by game and team
        team_game_stats = stats_df.groupby(['game_id', 'posteam']).agg(
            passing_yards=('passing_yards', 'sum'),
            rushing_yards=('rushing_yards', 'sum'),
            first_downs=('first_down', 'sum'),
            interceptions=('interception', 'sum'),
            fumbles=('fumble_lost', 'sum'),
            total_score=('posteam_score', 'max')
        ).reset_index()

        # Calculate giveaways
        team_game_stats['giveaways'] = team_game_stats['interceptions'] + team_game_stats['fumbles']

        # Aggregate defensive stats by game and opponent
        defense_stats = stats_df.groupby(['game_id', 'defteam']).agg(
            passing_yards_allowed=('passing_yards', 'sum'),
            rushing_yards_allowed=('rushing_yards', 'sum')
        ).reset_index()

        # Rename 'defteam' to 'posteam' to merge with team_game_stats
        defense_stats = defense_stats.rename(columns={'defteam': 'posteam'})

        # Merge offensive and defensive stats
        team_game_stats = team_game_stats.merge(defense_stats, on=['game_id', 'posteam'], how='left')

        # Calculate takeaways based on opponent turnovers
        opponent_turnovers = stats_df.groupby(['game_id', 'defteam']).agg(
            opponent_interceptions=('interception', 'sum'),
            opponent_fumbles=('fumble_lost', 'sum')
        ).reset_index()

        opponent_turnovers = opponent_turnovers.rename(columns={'defteam': 'posteam'})
        team_game_stats = team_game_stats.merge(opponent_turnovers, on=['game_id', 'posteam'], how='left')
        team_game_stats['takeaways'] = team_game_stats['opponent_interceptions'] + team_game_stats['opponent_fumbles']

        # Append data for the year
        all_team_game_stats.append(team_game_stats)

    # Concatenate data from all years and save as a single CSV
    all_team_game_stats = pd.concat(all_team_game_stats, ignore_index=True)
    all_team_game_stats.to_csv("nfl_team_game_stats_combined.csv", index=False)

def calculate_team_averages():
    # Load the team stats CSV
    team_game_stats = pd.read_csv("nfl_team_game_stats_combined.csv")

    # Get the current year
    current_year = 2024

    # Filter data for the current year only
    team_game_stats['year'] = pd.to_datetime(team_game_stats['game_id'].astype(str).str[:4]).dt.year
    current_year_stats = team_game_stats[team_game_stats['year'] == current_year]

    # Group by 'posteam' to get average stats for the current year
    average_stats = current_year_stats.groupby('posteam').agg(
        avg_passing_yards=('passing_yards', 'mean'),
        avg_rushing_yards=('rushing_yards', 'mean'),
        avg_first_downs=('first_downs', 'mean'),
        avg_giveaways=('giveaways', 'mean'),
        avg_takeaways=('takeaways', 'mean'),
        avg_passing_yards_allowed=('passing_yards_allowed', 'mean'),
        avg_rushing_yards_allowed=('rushing_yards_allowed', 'mean'),
        avg_total_score=('total_score', 'mean')
    ).reset_index()

    # Save the averages to the new CSV file for the current year
    average_stats.to_csv("nfl_team_current_year_averages.csv", index=False)

# pbp_data = nfl.import_pbp_data([2024])
# print(pbp_data['first_down'])