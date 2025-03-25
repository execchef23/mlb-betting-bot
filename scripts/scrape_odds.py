from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def get_draftkings_odds():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://sportsbook.draftkings.com/leagues/baseball/mlb")

    time.sleep(5)

    teams = driver.find_elements(By.CLASS_NAME, "event-cell__name-text")
    odds = driver.find_elements(By.CLASS_NAME, "sportsbook-odds")

    games = []

    for i in range(0, len(teams) - 1, 2):
        try:
            games.append({
                "away_team": teams[i].text,
                "home_team": teams[i+1].text,
                "away_odds": odds[i].text,
                "home_odds": odds[i+1].text,
            })
        except IndexError:
            continue

    driver.quit()

    df = pd.DataFrame(games)
    df.to_csv("data/live_odds.csv", index=False)
    print("✅ DraftKings odds saved to data/live_odds.csv")

if __name__ == "__main__":
    get_draftkings_odds()