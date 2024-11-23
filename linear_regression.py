# linear_regression.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from data_processor import generate_team_stats_for_years

# Generate team stats for multiple years (2022-present)
generate_team_stats_for_years([2022, 2023, 2024])

# Load the combined dataset
df = pd.read_csv("nfl_team_game_stats_combined.csv")

# Define features, including opponent's defensive stats
X = df[['passing_yards', 'rushing_yards', 'first_downs', 'giveaways', 'takeaways', 'passing_yards_allowed', 'rushing_yards_allowed']]
y = df['total_score']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Print model details
print("Intercept:", model.intercept_)
print("Coefficients:", model.coef_)
print("Feature names:", X.columns)

# Test the model
y_pred = model.predict(X_test)
print("R-squared:", r2_score(y_test, y_pred))
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))

# Save model
joblib.dump(model, 'nfl_lr_model.pkl')
print("Model saved to 'nfl_lr_model.pkl'")
