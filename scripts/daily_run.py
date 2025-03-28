import subprocess

print("🚀 Running full daily prediction pipeline...")

scripts = [
    "scripts/scrape_odds.py",
    "scripts/enhance_features.py",
    "run_bot.py",
    "scripts/track_results.py",
    "scripts/fetch_player_data.py",
    "scripts/engineer_player_features.py",
    "scripts/predict_player_props.py"
]

for script in scripts:
    print(f"▶️ Running {script}")
    subprocess.run(["python", script])