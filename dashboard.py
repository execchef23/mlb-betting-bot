import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(page_title="MLB Betting AI Dashboard", layout="wide")
st.title("⚾ MLB Betting AI Dashboard")

# 🚀 Run Prediction Section
st.markdown("## 🚀 Run Predictions")

days_ahead = st.selectbox("Select how many days ahead to predict:", list(range(0, 8)), index=1)

if st.button("🧠 Run Bot for Selected Day"):
    with st.spinner(f"Running prediction pipeline for {days_ahead} days ahead..."):
        subprocess.run(["python", "scripts/scrape_odds.py", "--days-ahead", str(days_ahead)])
        subprocess.run(["python", "scripts/enhance_features.py"])
        subprocess.run(["python", "run_bot.py", "--days-ahead", str(days_ahead)])
    st.success("✅ Done! Refresh the dashboard to see new results.")

# 🔁 Track Win/Loss Results
st.markdown("## 🎯 Update Win/Loss Results")

if st.button("🔁 Track Results Now"):
    with st.spinner("Updating bet results with final scores..."):
        subprocess.run(["python", "scripts/track_results.py"])
    st.success("✅ Win/loss results updated.")

# --- File paths ---
bet_path = "data/bet_results.csv"
history_path = "data/prediction_history.csv"
odds_path = "data/raw_odds.csv"

# 🔔 Recent Value Bets
st.markdown("## 🔔 Recent Value Bets (Last 24 Hours)")

if os.path.exists(bet_path):
    try:
        bets = pd.read_csv(bet_path)
        bets["timestamp"] = pd.to_datetime(bets["timestamp"])
        recent = bets[bets["timestamp"] > pd.Timestamp.now() - pd.Timedelta(hours=24)]

        if recent.empty:
            st.info("📭 No value bets placed in the last 24 hours.")
        else:
            for _, row in recent.iterrows():
                st.markdown(
                    f"""
                    <div style="border:1px solid #ddd;padding:10px;margin:10px 0;border-radius:5px;">
                        <b>{row['home_team']} vs {row['away_team']}</b><br>
                        📅 <b>Game Date:</b> {row['game_date']}<br>
                        💰 <b>Odds:</b> {row['home_odds']}<br>
                        📊 <b>Edge:</b> {float(row['edge']):.2%}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"Error loading bet history: {e}")
else:
    st.warning("⚠️ No bet history found. Run run_bot.py to create bet_results.csv.")

# 🔮 Prediction History
st.markdown("## 🔮 Prediction History")

if os.path.exists(history_path):
    try:
        hist = pd.read_csv(history_path)
        hist["timestamp"] = pd.to_datetime(hist["timestamp"])
        hist["game_date"] = pd.to_datetime(hist["game_date"])
        recent = hist.sort_values("timestamp", ascending=False).head(50)

        st.dataframe(recent[[
            "timestamp", "game_date", "home_team", "away_team", "predicted_home_win_prob"
        ]].round(3), use_container_width=True)
    except Exception as e:
        st.error(f"Error loading prediction history: {e}")
else:
    st.warning("⚠️ prediction_history.csv not found. Run run_bot.py to generate predictions.")

# ✅ Win/Loss Summary
st.markdown("## ✅ Win/Loss Summary")

if os.path.exists(bet_path):
    try:
        df = pd.read_csv(bet_path)
        if "actual_result" in df.columns:
            summary = df["actual_result"].value_counts()
            total = summary.sum()
            wins = summary.get("WIN", 0)
            losses = summary.get("LOSS", 0)
            win_rate = wins / total if total > 0 else 0.0

            st.metric("🏆 Wins", wins)
            st.metric("❌ Losses", losses)
            st.metric("📊 Win Rate", f"{win_rate:.2%}")
        else:
            st.info("📭 Waiting for game results... Run track_results.py.")
    except Exception as e:
        st.error(f"Error reading bet results: {e}")

# 🏆 Team Leaderboard by Confidence
st.markdown("## 🏆 Team Leaderboard (Top Predicted Wins)")

if os.path.exists(history_path):
    try:
        top_preds = hist.sort_values("predicted_home_win_prob", ascending=False).head(10)
        st.dataframe(top_preds[[
            "game_date", "home_team", "away_team", "predicted_home_win_prob"
        ]].round(3), use_container_width=True)
    except Exception as e:
        st.error(f"Error generating leaderboard: {e}")

# 📊 Confidence Distribution Chart
st.markdown("## 📊 Confidence Distribution (Model Predictions)")

if os.path.exists(history_path):
    try:
        confidence_bins = hist["predicted_home_win_prob"].round(1).value_counts().sort_index()
        st.bar_chart(confidence_bins)
    except Exception as e:
        st.error(f"Error generating chart: {e}")

# 🧠 Upcoming Games with Model Predictions
st.markdown("## 🧠 Upcoming Games + Model Predictions")

if os.path.exists(odds_path) and os.path.exists(history_path):
    try:
        upcoming = pd.read_csv(odds_path)
        upcoming["game_date"] = pd.to_datetime(upcoming["game_date"])

        preds = pd.read_csv(history_path)
        preds["game_date"] = pd.to_datetime(preds["game_date"])

        merged = pd.merge(
            upcoming,
            preds[["game_date", "home_team", "away_team", "predicted_home_win_prob"]],
            on=["game_date", "home_team", "away_team"],
            how="left"
        )

        merged = merged.sort_values("game_date")
        merged["predicted_home_win_prob"] = merged["predicted_home_win_prob"].round(3)
        merged.rename(columns={
            "home_odds": "🏠 Home Odds",
            "away_odds": "🆚 Away Odds",
            "predicted_home_win_prob": "🤖 Home Win Prob"
        }, inplace=True)

        st.dataframe(merged[[
            "game_date", "home_team", "away_team", "🏠 Home Odds", "🆚 Away Odds", "🤖 Home Win Prob"
        ]], use_container_width=True)

    except Exception as e:
        st.error(f"Error combining odds and predictions: {e}")
else:
    st.info("📊 Run scrape_odds.py and run_bot.py to see predictions with odds.")