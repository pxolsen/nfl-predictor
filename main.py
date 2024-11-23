# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predictor import predict_weekly_scores

# Initialize FastAPI app
app = FastAPI()

# Define the request model
class PredictionRequest(BaseModel):
    year: int
    week_num: int

# Define the response model
class PredictionResponse(BaseModel):
    home_team: str
    home_team_score: float
    away_team: str
    away_team_score: float
    total: float

# Endpoint to get predictions for a specific week
@app.post("/predict", response_model=dict[int, PredictionResponse])
async def get_predictions(request: PredictionRequest):
    try:
        predictions = predict_weekly_scores(request.year, request.week_num)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
