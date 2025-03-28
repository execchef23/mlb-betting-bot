import requests
import pandas as pd
import datetime
import argparse
import os

# --- CLI args ---
parser = argparse.ArgumentParser()
parser.add_argument("--days-ahead", type=int, default=1)
parser.add_argument("--date", type=str, help="Specific prediction date (YYYY-MM-DD)")
args = parser.parse_args()

# --- Determine target date ---
if args.date:
    target_date = pd.to_datetime(args.date).date()
else:
    target_date = datetime.date.today() + datetime.timedelta(days=args.days_ahead)

DATE_STR = target_date.strftime("%Y-%m-%d")

# --- API Config ---
API_KEY = "b666b3390e3028180cc3b53ab0fa1934"
url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?regions=us&markets=h2h&dateFormat=iso&date={DATE_STR}&apiKey={API_KEY}"

print(f"📡 Requesting odds for {DATE_STR}...")

# --- Request API ---
resp = requests.get(url)

if resp.status_code != 200:
    print(f"❌ API error: {resp.status_code} - {resp.text}")
    exit()

games = resp.json()
if not games:
    print("📭 No games returned from API.")
    exit()

# --- Parse results ---
rows = []
for game in games:
    try:
        home_team = game["home_team"]
        away_team = game["away_team"]
        game_date = pd.to_datetime(game["commence_time"]).date()

        # Grab the first bookmaker's odds
        bookmaker = game["bookmakers"][0]
        outcomes = bookmaker["markets"][0]["outcomes"]

        home_odds = None
        away_odds = None
        for o in outcomes:
            if o["name"] == home_team:
                home_odds = o["price"]
            elif o["name"] == away_team:
                away_odds = o["price"]

        if home_odds is not None and away_odds is not None:
            rows.append({
                "game_date": game_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_odds": home_odds,
                "away_odds": away_odds
            })
    except Exception as e:
        print(f"⚠️ Error parsing game: {e}")

# --- Save to CSV ---
df = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
df.to_csv("data/raw_odds.csv", index=False)

print(f"✅ Saved {len(df)} games to data/raw_odds.csv")