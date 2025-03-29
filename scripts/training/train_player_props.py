import pandas as pd
import xgboost as xgb
import joblib
import os

# Paths
hits_features_path = "data/engineered/player_hits_features_2024.csv"
strikeouts_features_path = "data/engineered/player_strikeout_features_2024.csv"
os.makedirs("models", exist_ok=True)

# Train Hits Model
def train_hits_model():
    print("🎯 Training Hits Model...")
    df = pd.read_csv(hits_features_path)
    features = ["total_hits", "at_bats", "obp", "bb_rate", "k_rate"]
    X = df[features]
    y = df["total_hits"]  # You can optionally bucket this into classes if desired

    model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1)
    model.fit(X, y)
    joblib.dump(model, "models/player_hits_model.pkl")
    print("✅ Saved player_hits_model.pkl")

# Train Strikeouts Model
def train_strikeouts_model():
    print("🎯 Training Strikeouts Model...")
    df = pd.read_csv(strikeouts_features_path)
    features = ["total_strikeouts", "batters_faced", "era", "k_per_9", "bb_per_9"]
    X = df[features]
    y = df["total_strikeouts"]  # You can optionally bucket this into classes

    model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1)
    model.fit(X, y)
    joblib.dump(model, "models/player_strikeouts_model.pkl")
    print("✅ Saved player_strikeouts_model.pkl")

if __name__ == "__main__":
    train_hits_model()
    train_strikeouts_model()