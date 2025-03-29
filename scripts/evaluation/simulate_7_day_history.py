import pandas as pd
import os
import random
import datetime

# Create /data folder if missing
os.makedirs("data", exist_ok=True)

teams = ["Yankees", "Red Sox", "Dodgers", "Giants", "Mets", "Braves", "Cubs", "Cardinals"]

prediction_rows = []
bet_rows = []

for i in range(7):  # Simulate 7 days
    game_date = (datetime.date.today() - datetime.timedelta(days=i))
    timestamp = datetime.datetime.now().isoformat()

    for _ in range(5):  # 5 games per day
        home, away = random.sample(teams, 2)
        prob = round(random.uniform(0.45, 0.75), 3)  # random model confidence
        odds = random.choice([-110, -120, +100, +110])
        edge = round(prob - 0.5, 3)
        result = random.choice(["WIN", "LOSS"])

        prediction_rows.append({
            "timestamp": timestamp,
            "game_date": game_date,
            "home_team": home,
            "away_team": away,
            "home_team_code": random.randint(100, 200),
            "away_team_code": random.randint(100, 200),
            "home_win_pct": round(random.uniform(0.4, 0.7), 3),
            "away_win_pct": round(random.uniform(0.4, 0.7), 3),
            "home_momentum": random.randint(-2, 3),
            "away_momentum": random.randint(-2, 3),
            "home_avg_run_diff": round(random.uniform(-1, 2), 2),
            "away_avg_run_diff": round(random.uniform(-1, 2), 2),
            "run_diff": round(random.uniform(-1.5, 2.5), 2),
            "predicted_home_win_prob": prob
        })

        if edge > 0.05:
            bet_rows.append({
                "timestamp": timestamp,
                "game_date": game_date,
                "home_team": home,
                "away_team": away,
                "predicted_home_win_prob": prob,
                "home_odds": odds,
                "edge": edge,
                "actual_result": result
            })

# Save predictions
pd.DataFrame(prediction_rows).to_csv("data/prediction_history.csv", index=False)

# Save bets
pd.DataFrame(bet_rows).to_csv("data/bet_results.csv", index=False)

print("✅ Simulated 7-day prediction and result history saved.")