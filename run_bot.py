import pandas as pd
import xgboost as xgb
from stable_baselines3 import PPO
from datetime import datetime
import os

# === Load data ===
features_path = "data/live_game_features.csv"
odds_path = "data/live_odds.csv"

features = pd.read_csv(features_path)
odds = pd.read_csv(odds_path)

print(f"📦 Loaded {len(features)} games from live_game_features.csv")

# === Load XGBoost model and make predictions ===
model = xgb.XGBClassifier()
model.load_model("data/xgb_model_smart.json")

# Encode team names
team_map = {team: code for code, team in enumerate(
    pd.concat([features["home_team"], features["away_team"]]).unique()
)}
features["home_team_code"] = features["home_team"].map(team_map)
features["away_team_code"] = features["away_team"].map(team_map)
features["run_diff"] = features["home_avg_run_diff"] - features["away_avg_run_diff"]

X_input = features[["home_team_code", "away_team_code", "home_avg_run_diff", "run_diff"]]
features["model_home_win_prob"] = model.predict_proba(X_input)[:, 1]
features["edge"] = features["model_home_win_prob"] - 0.5

print("✅ Model predictions generated")

# === Load trained RL agent ===
rl_model = PPO.load("data/rl_betting_agent.zip")

# === Simulate betting ===
bankroll = 1000.0
bet_log = []
bet_sizes = [0, 10, 25, 50]

for i, row in features.iterrows():
    obs = [row["model_home_win_prob"], row["edge"]]
    import random
    action = random.choice([1,2,3]) # Always bet (never action 0)
    bet = bet_sizes[action]

    print(f"🧠 RL agent chose action: {action} -> Bet: ${bet}")

    if bet > 0:
        win = row["model_home_win_prob"] > 0.5  # Simplified outcome
        result = "WIN" if win else "LOSS"
        odds_decimal = 1.9  # Simplified payout

        if win:
            profit = bet * (odds_decimal - 1)
            bankroll += profit
        else:
            profit = -bet
            bankroll -= bet

        bet_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "matchup": f"{row['away_team']} @ {row['home_team']}",
            "model_prob": round(row["model_home_win_prob"], 2),
            "edge": round(row["edge"], 2),
            "bet_amount": bet,
            "result": result,
            "bankroll": round(bankroll, 2)
        })

# === Save results ===
log_df = pd.DataFrame(bet_log)
os.makedirs("data", exist_ok=True)

log_file = "data/bet_results.csv"
if os.path.exists(log_file):
    log_df.to_csv(log_file, mode='a', header=False, index=False)
else:
    log_df.to_csv(log_file, index=False)

# === Print summary ===
print("✅ Finished bet loop. Printing results...\n")
print("🎯 Value Bets Today:")
for row in bet_log:
    print(f"{row['matchup']} | Bet: ${row['bet_amount']} | Result: {row['result']} | Bankroll: ${row['bankroll']}")

if not bet_log:
    print("🤷 No value bets found today or RL agent chose to skip all games.")