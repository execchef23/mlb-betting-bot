import os
import pandas as pd
from tqdm import tqdm

RAW_PATH = "data"
ENGINEERED_PATH = "data/engineered"
os.makedirs(ENGINEERED_PATH, exist_ok=True)

def engineer_batter_features(year):
    player_dir = f"{RAW_PATH}/player_stats_{year}"
    records = []

    batter_files = [f for f in os.listdir(player_dir) if f.startswith("batter_") and f.endswith(".csv")]
    if not batter_files:
        print(f"❌ No batter data found in {player_dir}")
        return

    for file in tqdm(batter_files, desc=f"🧢 Batters ({year})"):
        path = os.path.join(player_dir, file)
        try:
            df = pd.read_csv(path)
            df = df.sort_values("game_date")
            df["hit"] = df["events"].isin(["single", "double", "triple", "home_run"]).astype(int)
            df["rolling_avg_hits_5"] = df["hit"].rolling(5).mean()
            df["rolling_avg_hits_10"] = df["hit"].rolling(10).mean()
            df["rolling_hits_sum_5"] = df["hit"].rolling(5).sum()
            records.append(df)
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

    if records:
        all_hits = pd.concat(records, ignore_index=True)
        all_hits.to_csv(f"{ENGINEERED_PATH}/player_hits_features_{year}.csv", index=False)
        print(f"✅ Saved: player_hits_features_{year}.csv")
    else:
        print(f"⚠️ No valid batter records for {year}")

def engineer_pitcher_features(year):
    player_dir = f"{RAW_PATH}/player_stats_{year}"
    records = []

    pitcher_files = [f for f in os.listdir(player_dir) if f.startswith("pitcher_") and f.endswith(".csv")]
    if not pitcher_files:
        print(f"❌ No pitcher data found in {player_dir}")
        return

    for file in tqdm(pitcher_files, desc=f"🎯 Pitchers ({year})"):
        path = os.path.join(player_dir, file)
        try:
            df = pd.read_csv(path)
            df = df.sort_values("game_date")
            df["strikeout"] = df["events"].isin(["strikeout", "strikeout_double_play"]).astype(int)
            df["rolling_avg_k_5"] = df["strikeout"].rolling(5).mean()
            df["rolling_avg_k_10"] = df["strikeout"].rolling(10).mean()
            df["rolling_k_sum_5"] = df["strikeout"].rolling(5).sum()
            records.append(df)
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

    if records:
        all_ks = pd.concat(records, ignore_index=True)
        all_ks.to_csv(f"{ENGINEERED_PATH}/player_strikeout_features_{year}.csv", index=False)
        print(f"✅ Saved: player_strikeout_features_{year}.csv")
    else:
        print(f"⚠️ No valid pitcher records for {year}")

if __name__ == "__main__":
    for year in [2024, 2025]:
        print(f"\n📦 Processing {year} features from: data/player_stats_{year}")
        engineer_batter_features(year)
        engineer_pitcher_features(year)