import pandas as pd
import xgboost as xgb

# Load enhanced features and model
features = pd.read_csv("data/live_game_features.csv")
odds = pd.read_csv("data/live_odds.csv")

model = xgb.XGBClassifier()
model.load_model("data/xgb_model_basic.json")

# Encode team names for the model
team_map = {team: code for code, team in enumerate(
    pd.concat([features["home_team"], features["away_team"]]).unique()
)}
features["home_team_code"] = features["home_team"].map(team_map)
features["away_team_code"] = features["away_team"].map(team_map)

# Build input for model (same shape as training)
model_input = features[[
    "home_team_code",
    "away_team_code",
    "home_win_pct",
    "away_win_pct",
    "home_momentum",
    "away_momentum",
    "home_avg_run_diff",
    "away_avg_run_diff"
]]

# Predict home win probabilities
pred_probs = model.predict_proba(model_input)[:, 1]  # Home win

# Function to convert odds to implied probability
def implied_prob(odds):
    try:
        odds = int(odds)
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    except:
        return None

# Compare with sportsbook odds
value_bets = []
for i, row in features.iterrows():
    sportsbook_row = odds.iloc[i]
    model_prob = pred_probs[i]
    implied = implied_prob(sportsbook_row["home_odds"])
    edge = model_prob - implied if implied else 0

    if implied and edge > 0.05:
        value_bets.append({
            "Matchup": f"{row['away_team']} @ {row['home_team']}",
            "Model Home Win %": round(model_prob, 2),
            "Implied Home Win %": round(implied, 2),
            "Edge": round(edge, 2),
            "Recommended Bet": "Home"
        })

# Show results
print("\n📊 VALUE BETS:")
if value_bets:
    for bet in value_bets:
        print(bet)
else:
    print("No value bets found today.")