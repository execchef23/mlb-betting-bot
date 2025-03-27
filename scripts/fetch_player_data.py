from pybaseball import (
    statcast_batter,
    statcast_pitcher,
    batting_stats,
    pitching_stats,
)
import pandas as pd
from datetime import date
import os
import time

def sanitize(name):
    return name.replace(" ", "_").replace(".", "").replace("'", "")

def fetch_players(year, save_dir, top_n=100):
    os.makedirs(save_dir, exist_ok=True)
    print(f"\n📆 Fetching top {top_n} players for {year}...")

    # Get top hitters and pitchers
    try:
        batters = batting_stats(year).sort_values("H", ascending=False).head(top_n)
        pitchers = pitching_stats(year).sort_values("SO", ascending=False).head(top_n)
    except Exception as e:
        print(f"❌ Failed to fetch stats for {year}: {e}")
        return

    # Date range
    start_date = f"{year}-03-28"
    end_date = date.today().strftime("%Y-%m-%d") if year == date.today().year else f"{year}-10-01"

    # Fetch batter statcast data
    for _, row in batters.iterrows():
        name = row["Name"]
        player_id = row["IDfg"]
        try:
            print(f"📥 Batter ({year}): {name}")
            df = statcast_batter(start_date, end_date, player_id)
            df.to_csv(f"{save_dir}/batter_{sanitize(name)}.csv", index=False)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Skipping batter {name}: {e}")

    # Fetch pitcher statcast data
    for _, row in pitchers.iterrows():
        name = row["Name"]
        player_id = row["IDfg"]
        try:
            print(f"📥 Pitcher ({year}): {name}")
            df = statcast_pitcher(start_date, end_date, player_id)
            df.to_csv(f"{save_dir}/pitcher_{sanitize(name)}.csv", index=False)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Skipping pitcher {name}: {e}")

    print(f"✅ Completed fetching for {year}.")

if __name__ == "__main__":
    fetch_players(2024, "data/player_stats_2024")
    fetch_players(2025, "data/player_stats_2025")