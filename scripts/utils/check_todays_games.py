# scripts/utils/check_todays_games.py

import pandas as pd
from pybaseball import schedule_and_record
from datetime import datetime

today = datetime.today().strftime("%Y-%m-%d")
teams = [
    "LAD", "ATL", "NYY", "SDP", "SEA", "HOU", "CHC", "BOS",
    "TBR", "TOR", "NYM", "STL", "PHI", "SFG", "MIL", "MIN"
]

all_schedules = []
for team in teams:
    try:
        sched = schedule_and_record(2024, team)
        sched["Team"] = team
        all_schedules.append(sched)
    except Exception as e:
        print(f"Error loading {team}: {e}")

# Combine all schedules
all_games = pd.concat(all_schedules, ignore_index=True)

# Parse dates safely
all_games["Date"] = pd.to_datetime(all_games["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
all_games = all_games.dropna(subset=["Date"])

# Filter to today's games
todays_games = all_games[all_games["Date"] == today]

# Show results
if not todays_games.empty:
    print("\n📅 Today's MLB Games:")
    print(todays_games[["Date", "Team", "Home_Away", "Opp", "W/L"]])
else:
    print(f"\n🚫 No MLB games found for {today}.")