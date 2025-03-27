import streamlit as st
import pandas as pd
import os
import subprocess
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="MLB Betting AI Dashboard", layout="wide")
st.title("⚾ MLB Betting AI Dashboard")

# 🧠 Auto-detect next MLB game day
def get_next_game_day():
    today = datetime.today().date()
    for i in range(0, 7):
        check_date = today + timedelta(days=i)
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={check_date}"
        try:
            games = requests.get(url).json().get("dates", [])
            if games and games[0].get("games"):
                return check_date
        except Exception:
            pass
    return None

# 🚀 Run Prediction Section
st.markdown("## 🚀 Run Predictions")

next_game_day = get_next_game_day()
today = datetime.today().date()
default_days_ahead = (next_game_day - today).days if next_game_day else 1

st.write(f"🧠 Auto-detected next game day: **{next_game_day.strftime('%A, %B %d')}**")

col1, col2 = st.columns(2)

with col1:
    if st.button(f"🎯 Run Bot for {next_game_day.strftime('%b %d')}"):
        with st.spinner("Running bot for next available game day..."):
            subprocess.run(["python", "scripts/scrape_odds.py", "--days-ahead", str(default_days_ahead)])
            subprocess.run(["python", "scripts/enhance_features.py"])
            subprocess.run(["python", "run_bot.py", "--days-ahead", str(default_days_ahead)])
        st.success("✅ Done! Refresh to view results.")

with col2:
    manual_days = st.selectbox("📅 Or select manually:", list(range(0, 8)), index=default_days_ahead)
    if st.button(f"📊 Run Bot for +{manual_days} days"):
        with st.spinner(f"Running bot for {manual_days} days ahead..."):
            subprocess.run(["python", "scripts/scrape_odds.py", "--days-ahead", str(manual_days)])
            subprocess.run(["python", "scripts/enhance_features.py"])
            subprocess.run(["python", "run_bot.py", "--days-ahead", str(manual_days)])
        st.success("✅ Done! Refresh to view results.")

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

# 🏆 Team Leaderboard
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

# 🧠 Upcoming Games + Model Predictions
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

        # Calculate edge and format for display
        merged["implied_home_prob"] = merged["home_odds"].apply(
            lambda odds: 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)
        )
        merged["edge"] = merged["predicted_home_win_prob"] - merged["implied_home_prob"]
        merged["Edge %"] = (merged["edge"] * 100).round(2)
        merged["🤖 Home Win Prob"] = merged["predicted_home_win_prob"].round(3)

        st.markdown("### 🎯 Filter: Only Show Value Bets?")
        show_value_only = st.toggle("Show only bets with edge > 5%", value=False)

        display_df = merged.copy()
        if show_value_only:
            display_df = display_df[display_df["edge"] > 0.05]

        display_df = display_df[[
            "game_date", "home_team", "away_team",
            "home_odds", "away_odds", "🤖 Home Win Prob", "Edge %"
        ]].rename(columns={
            "home_odds": "🏠 Home Odds",
            "away_odds": "🆚 Away Odds"
        }).sort_values("game_date")

        # Style high-confidence predictions
        def highlight_confidence(val):
            if isinstance(val, float) and val > 0.65:
                return "background-color: #d2f8d2; font-weight: bold"
            return ""

        styled = display_df.style.applymap(highlight_confidence, subset=["🤖 Home Win Prob"])

        st.dataframe(styled, use_container_width=True)

        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Table as CSV", data=csv, file_name="predicted_value_bets.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error combining odds and predictions: {e}")
else:
    st.info("📊 Run scrape_odds.py and run_bot.py to see predictions with odds.")

# 💰 Bankroll Over Time
st.markdown("## 💰 Bankroll Over Time")

if os.path.exists(bet_path):
    try:
        df = pd.read_csv(bet_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[df["bankroll_after"].notnull()]
        df = df.sort_values("timestamp")

        if df.empty:
            st.info("📭 No bankroll data yet. Run some bets first.")
        else:
            chart_data = df[["timestamp", "bankroll_after"]].set_index("timestamp")
            st.line_chart(chart_data)
    except Exception as e:
        st.error(f"Error displaying bankroll chart: {e}")