import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="MLB Betting AI Dashboard", layout="wide")
st.title("⚾️ MLB Betting AI Dashboard")

# === Bet History Section ===
bet_path = "data/bet_results.csv"
if os.path.exists(bet_path):
    try:
        bets = pd.read_csv(bet_path)

        if bets.empty:
            st.warning("✅ Found bet_results.csv, but it's empty. Run `run_bot.py` and place some bets!")
        else:
            st.subheader("📊 Bet History")
            st.dataframe(bets.sort_values("timestamp", ascending=False), use_container_width=True)

            st.subheader("📈 Bankroll Over Time")
            bankroll_chart = bets[["timestamp", "bankroll"]].copy()
            bankroll_chart["timestamp"] = pd.to_datetime(bankroll_chart["timestamp"])
            st.line_chart(bankroll_chart.set_index("timestamp"))

            st.subheader("🎯 Summary Stats")
            wins = (bets["result"] == "WIN").sum()
            losses = (bets["result"] == "LOSS").sum()
            final_bankroll = bets["bankroll"].iloc[-1]
            roi = ((final_bankroll - 1000) / 1000) * 100
            st.markdown(f"**✅ Wins:** {wins}  \n❌ Losses: {losses}")
            st.markdown(f"**💰 Final Bankroll:** ${final_bankroll:.2f}  \n📈 ROI: {roi:.2f}%")

    except pd.errors.EmptyDataError:
        st.warning("⚠️ bet_results.csv exists but is empty. Run `run_bot.py` to simulate some bets!")

else:
    st.warning("⚠️ No bet history found. Run `run_bot.py` to create bet_results.csv.")

# === Today's Games & Model Predictions ===
features_path = "data/live_game_features.csv"
if os.path.exists(features_path):
    try:
        games = pd.read_csv(features_path)

        st.subheader("📅 Today's Matchups & Model Predictions")
        if "model_home_win_prob" in games.columns:
            display_cols = [
                "away_team", "home_team",
                "model_home_win_prob", "home_avg_run_diff", "away_avg_run_diff"
            ]
            st.dataframe(games[display_cols], use_container_width=True)
        else:
            st.info("ℹ️ Run `run_bot.py` to generate model predictions for today's games.")

    except pd.errors.EmptyDataError:
        st.warning("⚠️ live_game_features.csv is empty. Run `enhance_features.py` after `scrape_odds.py`.")
else:
    st.warning("⚠️ live_game_features.csv not found. Run `scrape_odds.py` and `enhance_features.py`.")