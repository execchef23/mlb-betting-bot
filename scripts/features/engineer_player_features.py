import os
import pandas as pd
from tqdm import tqdm

# Directories
stats_dir_2024 = "data/player_stats_2024"
output_dir = "data/engineered"
os.makedirs(output_dir, exist_ok=True)

# === HITTERS ===
def engineer_batter_features(stats_dir, output_file):
    records = []
    for file in tqdm(os.listdir(stats_dir)):
        if not file.startswith("batter_") or not file.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(stats_dir, file))
        if df.empty or "player_name" not in df.columns:
            continue

        name = df["player_name"].iloc[0]
        hits = df["events"].isin(["single", "double", "triple", "home_run"]).sum()
        at_bats = df["at_bat_number"].count()
        obp = df.get("on_base_perc", pd.Series([None])).mean()
        bb_rate = df.get("bb_rate", pd.Series([None])).mean()
        k_rate = df.get("k_rate", pd.Series([None])).mean()
        team = df["team"].iloc[0] if "team" in df.columns else "Unknown"

        records.append({
            "player_name": name,
            "total_hits": hits,
            "at_bats": at_bats,
            "obp": obp,
            "bb_rate": bb_rate,
            "k_rate": k_rate,
            "team": team
        })

    if records:
        pd.DataFrame(records).to_csv(output_file, index=False)
        print(f"✅ Saved: {output_file}")
    else:
        print(f"❌ No batter data found in {stats_dir}")

# === PITCHERS ===
def engineer_pitcher_features(stats_dir, output_file):
    records = []
    for file in tqdm(os.listdir(stats_dir)):
        if not file.startswith("pitcher_") or not file.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(stats_dir, file))
        if df.empty or "player_name" not in df.columns:
            continue

        name = df["player_name"].iloc[0]
        strikeouts = df["events"].eq("strikeout").sum()
        batters_faced = len(df)
        era = df.get("earned_run_avg", pd.Series([None])).mean()
        k_per_9 = df.get("k_per_9", pd.Series([None])).mean()
        bb_per_9 = df.get("bb_per_9", pd.Series([None])).mean()
        team = df["team"].iloc[0] if "team" in df.columns else "Unknown"

        records.append({
            "player_name": name,
            "total_strikeouts": strikeouts,
            "batters_faced": batters_faced,
            "era": era,
            "k_per_9": k_per_9,
            "bb_per_9": bb_per_9,
            "team": team
        })

    if records:
        pd.DataFrame(records).to_csv(output_file, index=False)
        print(f"✅ Saved: {output_file}")
    else:
        print(f"❌ No pitcher data found in {stats_dir}")

# Run for 2024 only
print(f"📦 Processing 2024 features from: {stats_dir_2024}")
engineer_batter_features(stats_dir_2024, f"{output_dir}/player_hits_features_2024.csv")
engineer_pitcher_features(stats_dir_2024, f"{output_dir}/player_strikeout_features_2024.csv")