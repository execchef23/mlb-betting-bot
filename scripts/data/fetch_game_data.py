import requests
import pandas as pd

def get_historical_data(start_year=2020, end_year=2024):
    all_games = []

    for year in range(start_year, end_year + 1):
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={year}&gameType=R"
        response = requests.get(url)

        if response.status_code == 200:
            games = response.json().get('dates', [])
            for date in games:
                for game in date['games']:
                    home_team_data = game['teams']['home']
                    away_team_data = game['teams']['away']

                    all_games.append({
                        'game_id': game['gamePk'],
                        'date': game['officialDate'],
                        'home_team': home_team_data['team']['name'],
                        'away_team': away_team_data['team']['name'],
                        'home_score': home_team_data.get('score'),  # Use .get() to avoid KeyError
                        'away_score': away_team_data.get('score'),
                        'venue': game['venue']['name']
        })       

    return pd.DataFrame(all_games)

if __name__ == "__main__":
    df = get_historical_data()
    df.to_csv("data/mlb_historical_games.csv", index=False)
    print("✅ Historical MLB data saved to data/mlb_historical_games.csv")