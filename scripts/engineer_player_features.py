import os
import pandas as pd
from glob import glob

def sanitize_name(file):
    return os.path.basename(file).replace(".csv", "").split("_", 1)[1].replace("_", " ")

def process_batter_files(folder):
    records = []
    for file in glob(f"{folder}/batter_*.csv"):
        name = sanitize_name(file)
        try:
            df = pd.read_csv(file, low_memory=False)
            df["game_date"] = pd.to_datetime(df["game_date"])
            df = df.sort_values("game_date")

            df["hit"] = df["events"].fillna("").str.contains("single|double|triple|home_run").astype(int)
            hits_per_game = df.groupby("game_date")["hit"].sum().reset_index()
            hits_per_game["player"] = name
            hits_per_game["rolling_avg_hits_5"] = hits_per_game["hit"].rolling(5).mean()
            hits_per_game["rolling_avg_hits_10"] = hits_per_game["hit"].rolling(10).mean()
            hits_per_game["rolling_hits_sum_5"] = hits_per_game["hit"].rolling(5).sum()

            records.append(hits_per_game)
        except Exception as e:
            print(f"⚠️ Skipping batter {name}: {e}")
    return pd.concat(records, ignore_index=True) if records else pd.DataFrame()

def process_pitcher_files(folder):
    records = []
    for file in glob(f"{folder}/pitcher_*.csv"):
        name = sanitize_name(file)
        try:
            df = pd.read_csv(file, low_memory=False)
            df["game_date"] = pd.to_datetime(df["game_date"])
            df = df.sort_values("game_date")

            if len(df) < 10:
                continue

            df["strikeout"] = df["events"].fillna("").str.contains("strikeout").astype(int)
            ks_per_game = df.groupby("game_date")["strikeout"].sum().reset_index()
            ks_per_game["player"] = name
            ks_per_game["rolling_avg_k_5"] = ks_per_game["strikeout"].rolling(5).mean()
            ks_per_game["rolling_avg_k_10"] = ks_per_game["strikeout"].rolling(10).mean()
            ks_per_game["rolling_k_sum_5"] = ks_per_game["strikeout"].rolling(5).sum()

            records.append(ks_per_game)
        except Exception as e:
            print(f"⚠️ Skipping pitcher {name}: {e}")
    return pd.concat(records, ignore_index=True) if records else pd.DataFrame()

def save_features(folder, label):
    print(f"\n📦 Processing {label} features from: {folder}")

    os.makedirs("data/engineered", exist_ok=True)

    hits_df = process_batter_files(folder)
    ks_df = process_pitcher_files(folder)

    if not hits_df.empty:
        hits_df.to_csv(f"data/engineered/player_hits_features_{label}.csv", index=False)
        print(f"✅ Saved: player_hits_features_{label}.csv")
    else:
        print(f"❌ No batter data found in {folder}")

    if not ks_df.empty:
        ks_df.to_csv(f"data/engineered/player_strikeout_features_{label}.csv", index=False)
        print(f"✅ Saved: player_strikeout_features_{label}.csv")
    else:
        print(f"❌ No pitcher data found in {folder}")

if __name__ == "__main__":
    save_features("data/player_stats_2024", "2024")  # For training
    save_features("data/player_stats_2025", "2025")  # For live prediction