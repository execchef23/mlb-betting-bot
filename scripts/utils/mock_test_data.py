import pandas as pd
import os

os.makedirs("data", exist_ok=True)

# Mock bet results
bets = pd.DataFrame([
    {
        "timestamp": "2025-03-27T12:00:00",
        "game_date": "2025-03-27",
        "home_team": "Yankees",
        "away_team": "Red Sox",
        "predicted_home_win_prob": 0.65,
        "home_odds": -120,
        "edge": 0.08,
        "actual_result": "WIN"
    },
    {
        "timestamp": "2025-03-27T12:00:00",
        "game_date": "2025-03-27",
        "home_team": "Dodgers",
        "away_team": "Giants",
        "predicted_home_win_prob": 0.58,
        "home_odds": -135,
        "edge": 0.06,
        "actual_result": "LOSS"
    },
    {
        "timestamp": "2025-03-27T12:00:00",
        "game_date": "2025-03-27",
        "home_team": "Mets",
        "away_team": "Braves",
        "predicted_home_win_prob": 0.51,
        "home_odds": +105,
        "edge": 0.04,
        "actual_result": "WIN"
    }
])
bets.to_csv("data/bet_results.csv", index=False)

# Mock prediction history
preds = pd.DataFrame([
    {
        "timestamp": "2025-03-27T11:55:00",
        "game_date": "2025-03-27",
        "home_team": "Yankees",
        "away_team": "Red Sox",
        "home_team_code": 110,
        "away_team_code": 111,
        "home_win_pct": 0.61,
        "away_win_pct": 0.57,
        "home_momentum": 2,
        "away_momentum": 1,
        "home_avg_run_diff": 1.2,
        "away_avg_run_diff": 0.5,
        "run_diff": 0.7,
        "predicted_home_win_prob": 0.65
    },
    {
        "timestamp": "2025-03-27T11:55:00",
        "game_date": "2025-03-27",
        "home_team": "Dodgers",
        "away_team": "Giants",
        "home_team_code": 118,
        "away_team_code": 119,
        "home_win_pct": 0.59,
        "away_win_pct": 0.55,
        "home_momentum": 3,
        "away_momentum": 2,
        "home_avg_run_diff": 1.8,
        "away_avg_run_diff": 0.9,
        "run_diff": 0.9,
        "predicted_home_win_prob": 0.58
    },
    {
        "timestamp": "2025-03-27T11:55:00",
        "game_date": "2025-03-27",
        "home_team": "Mets",
        "away_team": "Braves",
        "home_team_code": 112,
        "away_team_code": 113,
        "home_win_pct": 0.52,
        "away_win_pct": 0.50,
        "home_momentum": 0,
        "away_momentum": -1,
        "home_avg_run_diff": 0.2,
        "away_avg_run_diff": -0.3,
        "run_diff": 0.5,
        "predicted_home_win_prob": 0.51
    }
])
preds.to_csv("data/prediction_history.csv", index=False)