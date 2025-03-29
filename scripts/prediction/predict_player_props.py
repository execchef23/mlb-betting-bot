import pandas as pd
import joblib
import os
from datetime import datetime

# === Paths ===
hits_model_path = "models/player_hits_model.pkl"
strikeouts_model_path = "models/player_strikeouts_model.pkl"
hits_features_path = "data/engineered/player_hits_features_2024.csv"
strikeouts_features_path = "data/engineered/player_strikeout_features_2024.csv"
schedule_path = "data/live_game_features.csv"
output_path = "data/player_prop_predictions.csv"

# === Load trained models ===
print("📥 Loading trained models...")
hits_model = joblib.load(hits_model_path)
strikeouts_model = joblib.load(strikeouts_model_path)

# === Load player features ===
print("📄 Loading player features...")
hits_df = pd.read_csv(hits_features_path)
strikeouts_df = pd.read_csv(strikeouts_features_path)

# === Load today’s scheduled matchups ===
print("📅 Loading today’s scheduled matchups...")
try:
    schedule = pd.read_csv(schedule_path)
    teams_today = set(schedule["home_team"]).union(set(schedule["away_team"]))
except Exception as e:
    print(f"❌ Failed to load schedule: {e}")
    teams_today = set()

# === Predict Hits (Batters) ===
print("🔮 Predicting hits...")
hits_df = hits_df[hits_df["team"].isin(teams_today)]
hits_features = ["total_hits", "at_bats", "obp", "bb_rate", "k_rate"]
hits_X = hits_df[hits_features]
hits_preds = hits_model.predict(hits_X)
hits_df["prediction"] = hits_preds
hits_df["prop_type"] = "hits"

# Add opponent team
hits_df = hits_df.merge(schedule[["home_team", "away_team"]], how="left", left_on="team", right_on="away_team")
hits_df["opponent"] = hits_df["home_team"]
hits_df.drop(columns=["home_team", "away_team"], inplace=True)

# === Predict Strikeouts (Pitchers) ===
print("🔥 Predicting strikeouts...")
strikeouts_df = strikeouts_df[strikeouts_df["team"].isin(teams_today)]
strikeout_features = ["total_strikeouts", "batters_faced", "era", "k_per_9", "bb_per_9"]
strikeouts_X = strikeouts_df[strikeout_features]
strikeout_preds = strikeouts_model.predict(strikeouts_X)
strikeouts_df["prediction"] = strikeout_preds
strikeouts_df["prop_type"] = "strikeouts"

# Add opponent team
strikeouts_df = strikeouts_df.merge(schedule[["home_team", "away_team"]], how="left", left_on="team", right_on="home_team")
strikeouts_df["opponent"] = strikeouts_df["away_team"]
strikeouts_df.drop(columns=["home_team", "away_team"], inplace=True)

# === Combine Predictions ===
print("🧩 Merging predictions...")
combined = pd.concat([
    hits_df[["player_name", "team", "opponent", "prop_type", "prediction"]],
    strikeouts_df[["player_name", "team", "opponent", "prop_type", "prediction"]]
], ignore_index=True)

combined["prediction_date"] = datetime.today().strftime("%Y-%m-%d")

# === Save Output ===
os.makedirs("data", exist_ok=True)
combined.to_csv(output_path, index=False)
print(f"✅ Saved player prop predictions to {output_path}")