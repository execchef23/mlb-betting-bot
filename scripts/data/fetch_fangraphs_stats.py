# scripts/fetch_fangraphs_stats_pybaseball.py
from pybaseball import batting_stats, pitching_stats
import pandas as pd

def save_fangraphs_stats(season):
    print(f"📥 Fetching FanGraphs batting stats for {season}...")
    batting = batting_stats(season)
    batting.to_csv(f"data/fangraphs_batting_{season}.csv", index=False)

    print(f"📥 Fetching FanGraphs pitching stats for {season}...")
    pitching = pitching_stats(season)
    pitching.to_csv(f"data/fangraphs_pitching_{season}.csv", index=False)

    print(f"✅ Saved FanGraphs stats for {season}.")

if __name__ == "__main__":
    save_fangraphs_stats(2024)
    save_fangraphs_stats(2025)