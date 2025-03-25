import pandas as pd

# Load historical data
df = pd.read_csv("data/mlb_historical_games.csv")

# Drop rows without scores
df = df.dropna(subset=["home_score", "away_score"])

# Determine game winner
df["home_win"] = df["home_score"] > df["away_score"]

# Create win/loss for each team
def build_team_stats(df):
    team_stats = {}

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]

        # Init teams
        for team in [home, away]:
            if team not in team_stats:
                team_stats[team] = {
                    "games": 0,
                    "wins": 0,
                    "recent": [],
                    "run_diff": [],
                }

        # Update home team stats
        team_stats[home]["games"] += 1
        team_stats[home]["wins"] += int(row["home_win"])
        team_stats[home]["recent"].append(int(row["home_win"]))
        team_stats[home]["run_diff"].append(row["home_score"] - row["away_score"])

        # Update away team stats
        team_stats[away]["games"] += 1
        team_stats[away]["wins"] += int(not row["home_win"])
        team_stats[away]["recent"].append(int(not row["home_win"]))
        team_stats[away]["run_diff"].append(row["away_score"] - row["home_score"])

    return team_stats

# Compute advanced stats
team_stats = build_team_stats(df)

# Load today's matchups
matchups = pd.read_csv("data/live_odds.csv")

# Build feature set
rows = []

for _, row in matchups.iterrows():
    home = row["home_team"]
    away = row["away_team"]

    home_stats = team_stats.get(home, {})
    away_stats = team_stats.get(away, {})

    def avg_recent(team, n=5):
        recent = team.get("recent", [])[-n:]
        return sum(recent) / len(recent) if recent else 0

    def avg_run_diff(team):
        diffs = team.get("run_diff", [])
        return sum(diffs) / len(diffs) if diffs else 0

    row_data = {
        "home_team": home,
        "away_team": away,
        "home_win_pct": home_stats.get("wins", 0) / max(1, home_stats.get("games", 1)),
        "away_win_pct": away_stats.get("wins", 0) / max(1, away_stats.get("games", 1)),
        "home_momentum": avg_recent(home_stats),
        "away_momentum": avg_recent(away_stats),
        "home_avg_run_diff": avg_run_diff(home_stats),
        "away_avg_run_diff": avg_run_diff(away_stats)
    }

    rows.append(row_data)

# Save enhanced features
features_df = pd.DataFrame(rows)
features_df.to_csv("data/live_game_features.csv", index=False)
print("✅ Advanced features saved to data/live_game_features.csv")