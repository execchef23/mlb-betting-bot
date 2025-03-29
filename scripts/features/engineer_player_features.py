import os
import pandas as pd
from tqdm import tqdm

def engineer_batter_features(input_folder, output_csv):
    records = []
    for filename in tqdm(os.listdir(input_folder), desc=f"🧢 Batters ({input_folder[-4:]})"):
        if not filename.startswith("batter_"):
            continue
        filepath = os.path.join(input_folder, filename)
        try:
            df = pd.read_csv(filepath)
            if df.empty or "player_name" not in df.columns:
                continue

            name = df["player_name"].iloc[0]
            # Try to get team from home/away columns
            if "home_team" in df.columns and "away_team" in df.columns:
                # Choose the most frequent team across home/away appearances
                teams = pd.concat([df["home_team"], df["away_team"]])
                team = teams.mode().iloc[0] if not teams.mode().empty else "Unknown"
            else:
                team = "Unknown"
                
            total_hits = df["events"].isin(["single", "double", "triple", "home_run"]).sum()
            at_bats = df["events"].isin(["single", "double", "triple", "home_run", "strikeout", "field_out"]).sum()
            obp = (df["events"].isin(["single", "double", "triple", "home_run", "walk"])).sum() / max(1, df["events"].notna().sum())
            bb_rate = df["events"].eq("walk").sum() / max(1, at_bats)
            k_rate = df["events"].eq("strikeout").sum() / max(1, at_bats)

            records.append({
                "player_name": name,
                "team": team,
                "total_hits": total_hits,
                "at_bats": at_bats,
                "obp": obp,
                "bb_rate": bb_rate,
                "k_rate": k_rate,
            })
        except Exception as e:
            print(f"⚠️ Skipped {filename}: {e}")

    if records:
        all_hits = pd.DataFrame(records)
        os.makedirs("data/engineered", exist_ok=True)
        all_hits.to_csv(output_csv, index=False)
        print(f"✅ Saved: {output_csv}")
    else:
        print("❌ No valid batter data processed.")

# Run manually when needed
if __name__ == "__main__":
    engineer_batter_features("data/player_stats_2024", "data/engineered/player_hits_features_2024.csv")