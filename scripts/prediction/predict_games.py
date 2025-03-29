import pandas as pd
import xgboost as xgb

# Simulated "today's games" data
# In the real version, you’ll fetch this from live APIs or scrape it
today_games = pd.DataFrame([
    {"home_team": "Yankees", "away_team": "Red Sox", "home_odds": -120, "away_odds": +100},
    {"home_team": "Dodgers", "away_team": "Giants", "home_odds": -150, "away_odds": +130},
])

# Convert team names into the same category codes used in training
team_codes = pd.read_csv("data/features.csv")[["home_team", "away_team"]].apply(pd.Series).stack().unique()
team_code_map = {team: code for code, team in enumerate(sorted(team_codes))}

# Simulate feature engineering
def prepare_game_features(row):
    home = team_code_map.get(row["home_team"], 0)
    away = team_code_map.get(row["away_team"], 0)
    return pd.Series([home, away, 0])  # Run diff unknown pre-game, so use 0

X_new = today_games.apply(prepare_game_features, axis=1)
X_new.columns = ["home_team", "away_team", "run_diff"]

# Load trained model
model = xgb.XGBClassifier()
model.load_model("data/xgb_model.json")

# Predict home win probability
home_win_probs = model.predict_proba(X_new)[:, 1]

# Convert sportsbook odds to implied probability
def implied_prob(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

# Compare model probabilities to sportsbook implied probs
value_bets = []
for i, game in today_games.iterrows():
    model_prob = home_win_probs[i]
    book_prob = implied_prob(game["home_odds"])
    edge = model_prob - book_prob

    if edge > 0.05:  # At least 5% edge
        value_bets.append({
            "Matchup": f"{game['away_team']} @ {game['home_team']}",
            "Model_Prob_HomeWin": round(model_prob, 2),
            "Implied_Prob_HomeWin": round(book_prob, 2),
            "Edge": round(edge, 2),
            "Recommended_Bet": "Home"
        })

# Show results
print("\n📈 Value Bets Found:\n")
if value_bets:
    for bet in value_bets:
        print(bet)
else:
    print("No value bets found today.")