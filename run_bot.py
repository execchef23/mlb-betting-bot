import pandas as pd
import xgboost as xgb
import datetime
import os
from stable_baselines3 import PPO
from betting_env import BettingEnv
from utils.send_telegram import send_telegram_message

# Config
DAYS_AHEAD = 1  # Predict for today + 1 day ahead
VALUE_THRESHOLD = 0.05  # Minimum model edge to place bet
BANKROLL = 1000  # Starting bankroll

# Load input features
data_path = "data/live_game_features.csv"
if not os.path.exists(data_path):
    print("⚠️ live_game_features.csv not found. Run enhance_features.py first.")
    exit()

df = pd.read_csv(data_path)
df["game_date"] = pd.to_datetime(df["game_date"])
today = datetime.date.today()
df = df[df["game_date"].dt.date <= today + datetime.timedelta(days=DAYS_AHEAD)]

if df.empty:
    print("📭 No games to predict.")
    exit()

print(f"📦 Loaded {len(df)} games from live_game_features.csv")

# Load XGBoost model
model = xgb.XGBClassifier()
model.load_model("models/xgb_model_smart.json")

# Predict home win probability
model_input = df[[
    "home_team_code", "away_team_code", "home_win_pct", "away_win_pct",
    "home_momentum", "away_momentum", "home_avg_run_diff", "away_avg_run_diff", "run_diff"
]]
pred_probs = model.predict_proba(model_input)[:, 1]  # Home win prob

# 🔁 Save all predictions for trend tracking
all_predictions = df.copy()
all_predictions["predicted_home_win_prob"] = pred_probs
all_predictions["timestamp"] = datetime.datetime.now().isoformat()

history_path = "data/prediction_history.csv"
os.makedirs("data", exist_ok=True)
if os.path.exists(history_path):
    all_predictions.to_csv(history_path, mode="a", header=False, index=False)
else:
    all_predictions.to_csv(history_path, index=False)

# Load RL agent or fall back
try:
    env = BettingEnv(df, pred_probs, bankroll=BANKROLL)
    rl_model = PPO.load("data/rl_betting_agent.zip")
    action = rl_model.predict(env.reset())[0]
except Exception:
    print("⚠️ RL model failed to load. Using default policy.")
    env = BettingEnv(df, pred_probs, bankroll=BANKROLL)
    action = [1] * len(df)

# Place value bets
placed_bets = []
for i, row in df.iterrows():
    predicted_prob = pred_probs[i]
    implied_prob = 100 / abs(row["home_odds"]) if row["home_odds"] > 0 else abs(row["home_odds"]) / (abs(row["home_odds"]) + 100)
    edge = predicted_prob - implied_prob

    if edge > VALUE_THRESHOLD:
        bet = {
            "timestamp": datetime.datetime.now().isoformat(),
            "game_date": row["game_date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "predicted_home_win_prob": round(predicted_prob, 4),
            "home_odds": row["home_odds"],
            "edge": round(edge, 4)
        }
        placed_bets.append(bet)

        # Send Telegram alert
        message = (
            f"📈 <b>Value Bet Found</b>\n"
            f"🏠 {row['home_team']} vs 🆚 {row['away_team']}\n"
            f"📅 Game Date: {row['game_date']}\n"
            f"💰 Odds: {row['home_odds']}\n"
            f"📊 Edge: {edge:.2%}"
        )
        send_telegram_message(message)

# Save placed bets
results_path = "data/bet_results.csv"
if placed_bets:
    df_bets = pd.DataFrame(placed_bets)
    if os.path.exists(results_path):
        df_bets.to_csv(results_path, mode="a", header=False, index=False)
    else:
        df_bets.to_csv(results_path, index=False)
    print(f"✅ {len(df_bets)} value bets placed and saved to bet_results.csv")
else:
    print("📉 No value bets found today.")