import pandas as pd
import xgboost as xgb

# Load enhanced features and odds
features = pd.read_csv("data/live_game_features.csv")
odds = pd.read_csv("data/live_odds.csv")

# Encode team names to match training
team_map = {team: code for code, team in enumerate(
    pd.concat([features["home_team"], features["away_team"]]).unique()
)}
features["home_team_code"] = features["home_team"].map(team_map)
features["away_team_code"] = features["away_team"].map(team_map)

# Load your real model
model = xgb.XGBClassifier()
model.load_model("data/xgb_model_smart.json")

# Prepare model input
model_input = features[["home_team_code", "away_team_code", "home_avg_run_diff"]].copy()
model_input["run_diff"] = features["home_avg_run_diff"] - features["away_avg_run_diff"]

# Predict probabilities
pred_probs = model.predict_proba(model_input)[:, 1]  # Home win prob
features["model_home_win_prob"] = pred_probs

# Convert sportsbook odds to implied probabilities
def implied_prob(odds):
    try:
        odds = int(odds)
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    except:
        return None

odds["implied_home_win_prob"] = odds["home_odds"].apply(implied_prob)

# Simulate betting
bankroll = 1000.0
bet_amount = 50.0  # Flat bet per game
min_edge = 0.05
wins = 0
losses = 0
bet_log = []

for i, row in features.iterrows():
    model_prob = row["model_home_win_prob"]
    implied = odds.iloc[i]["implied_home_win_prob"]
    edge = model_prob - implied if implied else 0

    if implied and edge > min_edge:
        # Convert odds to decimal for payout
        american = int(odds.iloc[i]["home_odds"])
        odds_decimal = (100 / abs(american)) + 1 if american > 0 else (abs(american) + 100) / 100

        import random
        won = random.random() < model_prob  # Simulated outcome

        result = "WIN" if won else "LOSS"
        if won:
            bankroll += bet_amount * (odds_decimal - 1)
            wins += 1
        else:
            bankroll -= bet_amount
            losses += 1

        bet_log.append({
            "Matchup": f"{odds.iloc[i]['away_team']} @ {odds.iloc[i]['home_team']}",
            "Model Prob": round(model_prob, 2),
            "Implied Prob": round(implied, 2),
            "Edge": round(edge, 2),
            "Bet": bet_amount,
            "Result": result,
            "New Bankroll": round(bankroll, 2)
        })

# Results summary
print("\n📊 BETTING SUMMARY (Real Model)")
print(f"Total Bets Placed: {wins + losses}")
print(f"Wins: {wins}, Losses: {losses}")
print(f"Final Bankroll: ${bankroll:.2f}")
print(f"ROI: {((bankroll - 1000) / 1000) * 100:.2f}%")

# Save betting history
pd.DataFrame(bet_log).to_csv("data/bet_results.csv", index=False)
print("✅ Betting log saved to data/bet_results.csv")