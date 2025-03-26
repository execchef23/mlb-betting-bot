import requests
import pandas as pd
import os

API_KEY = "b666b3390e3028180cc3b53ab0fa1934"  # Replace with your real key

def get_odds():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american"
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print("⚠️ API error:", resp.status_code, resp.text)
        return []

    games = resp.json()
    all_data = []

    for game in games:
        try:
            home = game["home_team"]
            away = game["away_team"]
            game_date = game["commence_time"][:10]

            bookmaker = game["bookmakers"][0]
            outcomes = bookmaker["markets"][0]["outcomes"]

            home_odds = next(o["price"] for o in outcomes if o["name"] == home)
            away_odds = next(o["price"] for o in outcomes if o["name"] == away)

            all_data.append({
                "game_date": game_date,
                "home_team": home,
                "away_team": away,
                "home_odds": home_odds,
                "away_odds": away_odds
            })
        except:  # noqa: E722
            continue

    return all_data

def main():
    print("📡 Fetching real odds from OddsAPI...")
    games = get_odds()
    if not games:
        print("❌ No games fetched.")
        return

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(games)
    df.to_csv("data/raw_odds.csv", index=False)
    print(f"✅ Saved {len(df)} games to data/raw_odds.csv")

if __name__ == "__main__":
    main()