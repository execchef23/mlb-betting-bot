import pandas as pd

# Load raw historical data
df = pd.read_csv("data/mlb_historical_games.csv")

# 🧹 Clean: Remove rows without final scores
df = df.dropna(subset=["home_score", "away_score"])

# 🧮 Add new features
df["home_win"] = df["home_score"] > df["away_score"]
df["run_diff"] = df["home_score"] - df["away_score"]

# Convert team names into categorical variables
df["home_team"] = df["home_team"].astype("category").cat.codes
df["away_team"] = df["away_team"].astype("category").cat.codes

# 🔍 Select final features
features = ["home_team", "away_team", "run_diff"]
target = "home_win"

X = df[["home_team", "away_team", "run_diff"]]
y = df["home_win"].astype(int)

# Save cleaned data for modeling
X.to_csv("data/features.csv", index=False)
y.to_csv("data/target.csv", index=False)

print("✅ Data preprocessed and saved.")