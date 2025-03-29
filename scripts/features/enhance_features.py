import pandas as pd
import os
import random

# Simulated team stats (replace with real if available)
def get_win_pct(team):
    return round(random.uniform(0.40, 0.65), 3)

def get_momentum(team):
    return round(random.uniform(-0.2, 0.2), 3)

def get_avg_run_diff(team):
    return round(random.uniform(-2, 2), 2)

def team_to_code(team):
    return abs(hash(team)) % 1000  # simple team-to-integer encoder

def main():
    raw_path = "data/raw_odds.csv"
    if not os.path.exists(raw_path):
        print("⚠️ raw_odds.csv not found. Run scrape_odds.py first.")
        return

    df = pd.read_csv(raw_path)
    enhanced_rows = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        game_date = row["game_date"]

        enhanced_rows.append({
            "game_date": game_date,
            "home_team_code": team_to_code(home),
            "away_team_code": team_to_code(away),
            "home_win_pct": get_win_pct(home),
            "away_win_pct": get_win_pct(away),
            "home_momentum": get_momentum(home),
            "away_momentum": get_momentum(away),
            "home_avg_run_diff": get_avg_run_diff(home),
            "away_avg_run_diff": get_avg_run_diff(away),
            "run_diff": get_avg_run_diff(home) - get_avg_run_diff(away),
            "home_team": home,
            "away_team": away
        })

    out_df = pd.DataFrame(enhanced_rows)
    out_df.to_csv("data/live_game_features.csv", index=False)
    print(f"✅ Saved {len(out_df)} enhanced games to data/live_game_features.csv")

if __name__ == "__main__":
    main()