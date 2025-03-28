import pandas as pd
import numpy as np
import datetime
import xgboost as xgb
from stable_baselines3 import PPO
from betting_env import BettingEnv
import joblib
import os

# Load model
model = xgb.XGBClassifier()
model.load_model("models/xgb_model_smart.json")

# Load features
df = pd.read_csv("data/live_game_features.csv")

# Predict
model_input = df[["home_team_code", "away_team_code", "home_win_pct", "away_win_pct",
                  "home_momentum", "away_momentum", "home_avg_run_diff", "away_avg_run_diff"]]
pred_probs = model.predict_proba(model_input)[:, 1]  # Home win

df["predicted_home_win_prob"] = pred_probs

# Implied probability from moneyline odds
def implied_prob(odds):
    return 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

df["implied_home_prob"] = df["home_odds"].apply(implied_prob)
df["edge"] = df["predicted_home_win_prob"] - df["implied_home_prob"]

# --- BANKROLL TRACKING ---
bankroll = 1000  # starting bankroll
bet_size = 50    # fixed bet per game

value_bets = []
for _, row in df.iterrows():
    edge = row["edge"]
    if edge > 0.05:  # Only log bets with positive value
        bankroll -= bet_size
        bet = {
            "timestamp": datetime.datetime.now().isoformat(),
            "game_date": row["game_date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "predicted_home_win_prob": round(row["predicted_home_win_prob"], 4),
            "home_odds": row["home_odds"],
            "edge": round(edge, 4),
            "bet_size": bet_size,
            "bankroll_after": round(bankroll, 2)
        }
        value_bets.append(bet)

# Save bets
os.makedirs("data", exist_ok=True)
bet_results_path = "data/bet_results.csv"

if os.path.exists(bet_results_path):
    existing = pd.read_csv(bet_results_path)
    updated = pd.concat([existing, pd.DataFrame(value_bets)], ignore_index=True)
else:
    updated = pd.DataFrame(value_bets)

updated.to_csv(bet_results_path, index=False)

if value_bets:
    print(f"📈 Value Bets Found: {len(value_bets)}")
else:
    print("📭 No value bets found today.")