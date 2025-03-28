import os
import pandas as pd
from pybaseball import statcast_batter, statcast_pitcher, batting_stats, pitching_stats
from datetime import datetime

# Set the season years
YEARS = [2024, 2025]
START_DATE = "03-01"
END_DATE = "10-31"

BATTER_PATH = "data/player_stats_{year}"
PITCHER_PATH = "data/player_stats_{year}"

os.makedirs("logs", exist_ok=True)

def fetch_statcast_data():
    for year in YEARS:
        print(f"📦 Fetching data for year: {year}")
        batter_ids = batting_stats(year)["IDfg"].dropna().unique().tolist()
        pitcher_ids = pitching_stats(year)["IDfg"].dropna().unique().tolist()

        # Prep output folders
        batter_path = BATTER_PATH.format(year=year)
        pitcher_path = PITCHER_PATH.format(year=year)
        os.makedirs(batter_path, exist_ok=True)
        os.makedirs(pitcher_path, exist_ok=True)

        start = f"{year}-{START_DATE}"
        end = f"{year}-{END_DATE}"

        print(f"🧢 Batters ({len(batter_ids)}):")
        for player_id in batter_ids:
            try:
                df = statcast_batter(start, end, player_id)
                if df.shape[0] > 0:
                    name = df["player_name"].iloc[0].replace(" ", "_")
                    df.to_csv(f"{batter_path}/batter_{name}.csv", index=False)
                    print(f"✅ Saved: {name}")
                else:
                    print(f"⚠️ Skipped {player_id}: no rows")
            except Exception as e:
                print(f"❌ Failed batter {player_id}: {e}")

        print(f"🎯 Pitchers ({len(pitcher_ids)}):")
        for player_id in pitcher_ids:
            try:
                df = statcast_pitcher(start, end, player_id)
                if df.shape[0] > 0:
                    name = df["player_name"].iloc[0].replace(" ", "_")
                    df.to_csv(f"{pitcher_path}/pitcher_{name}.csv", index=False)
                    print(f"✅ Saved: {name}")
                else:
                    print(f"⚠️ Skipped {player_id}: no rows")
            except Exception as e:
                print(f"❌ Failed pitcher {player_id}: {e}")

if __name__ == "__main__":
    fetch_statcast_data()