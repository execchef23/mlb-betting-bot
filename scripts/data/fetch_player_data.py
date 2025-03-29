from pybaseball import statcast
import os
import pandas as pd
from datetime import datetime

def fetch_and_save_player_data(year):
    start_date = f"{year}-03-01"
    end_date = f"{year}-11-30"

    print(f"📥 Fetching Statcast data for {year}...")
    data = statcast(start_dt=start_date, end_dt=end_date)

    output_folder = f"data/player_stats_{year}"
    os.makedirs(output_folder, exist_ok=True)

    for player_type, col in [("batter", "batter"), ("pitcher", "pitcher")]:
        grouped = data.groupby(col)
        for pid, df in grouped:
            name = df["player_name"].iloc[0].replace(" ", "_").replace(".", "")
            filename = f"{player_type}_{name}.csv"
            df.to_csv(os.path.join(output_folder, filename), index=False)

# Fetch for both years
fetch_and_save_player_data(2023)
fetch_and_save_player_data(2024)