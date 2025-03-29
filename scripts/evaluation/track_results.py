import pandas as pd
import requests
import os
import datetime

def get_game_results(date):
    # Example using MLB stats API (public endpoint)
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    resp = requests.get(url)
    data = resp.json()
    results = {}

    for game in data.get("dates", [])[0].get("games", []):
        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]
        home_score = game["teams"]["home"]["score"]
        away_score = game["teams"]["away"]["score"]
        results[(home, away)] = "WIN" if home_score > away_score else "LOSS"
    
    return results

def update_bet_results():
    path = "data/bet_results.csv"
    if not os.path.exists(path):
        print("❌ bet_results.csv not found.")
        return

    df = pd.read_csv(path)
    if "actual_result" in df.columns:
        df = df[df["actual_result"].isnull()]  # only fill in missing

    game_dates = pd.to_datetime(df["game_date"]).dt.date.unique()
    all_results = {}

    for date in game_dates:
        result = get_game_results(date.strftime("%Y-%m-%d"))
        all_results.update(result)

    updated = 0
    results = []
    for idx, row in df.iterrows():
        matchup = (row["home_team"], row["away_team"])
        result = all_results.get(matchup)
        results.append(result if result else row.get("actual_result", None))
        if result:
            updated += 1

    df["actual_result"] = results
    df.to_csv(path, index=False)
    print(f"✅ Updated {updated} results in bet_results.csv")

if __name__ == "__main__":
    update_bet_results()