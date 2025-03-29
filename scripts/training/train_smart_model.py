import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load historical data
df = pd.read_csv("data/mlb_historical_games.csv")
df = df.dropna(subset=["home_score", "away_score"])
df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)

# Encode team names
df["home_team_code"] = df["home_team"].astype("category").cat.codes
df["away_team_code"] = df["away_team"].astype("category").cat.codes
df["run_diff"] = df["home_score"] - df["away_score"]

# Simulate enhanced features (like real-time ones)
df["home_avg_run_diff"] = df["run_diff"]  # For training, reuse run_diff
df["away_avg_run_diff"] = -df["run_diff"]

# Final input features
X = df[["home_team_code", "away_team_code", "home_avg_run_diff", "run_diff"]]
y = df["home_win"]

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Smart model accuracy: {acc:.2%}")

# Save it
model.save_model("data/xgb_model_smart.json")
print("✅ Smart model saved to data/xgb_model_smart.json")