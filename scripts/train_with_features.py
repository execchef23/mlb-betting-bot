import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load original historical data (for labels)
raw = pd.read_csv("data/mlb_historical_games.csv")
raw = raw.dropna(subset=["home_score", "away_score"])
raw["home_win"] = (raw["home_score"] > raw["away_score"]).astype(int)

# Build basic features + label from historical
raw["run_diff"] = raw["home_score"] - raw["away_score"]
raw["home_team"] = raw["home_team"].astype("category").cat.codes
raw["away_team"] = raw["away_team"].astype("category").cat.codes

# We'll simulate some stats like what you're using now
# (In real scenario, you'd use the same enhanced feature generator)
X = raw[["home_team", "away_team", "run_diff"]]
y = raw["home_win"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
model.fit(X_train, y_train)

# Accuracy check
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model trained with basic features. Accuracy: {acc:.2%}")

# Save it
model.save_model("data/xgb_model_basic.json")
print("✅ Model saved to data/xgb_model_basic.json")