import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="MLB Betting AI Dashboard", layout="wide")
st.title("⚾ MLB Betting AI Dashboard")

# Paths
bet_path = "data/bet_results.csv"
history_path = "data/prediction_history.csv"

# 🔔 Value Bet Alerts
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

# 🔮 Prediction History Section
st.markdown("## 🔮 Model Prediction History")

if os.path.exists(history_path):
    try:
        history = pd.read_csv(history_path)
        history["timestamp"] = pd.to_datetime(history["timestamp"])
        history = history.sort_values("timestamp", ascending=False).head(50)

        st.dataframe(
            history[[
                "timestamp", "game_date", "home_team", "away_team", "predicted_home_win_prob"
            ]].round(3),
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error loading prediction history: {e}")
else:
    st.warning("⚠️ prediction_history.csv not found. Run run_bot.py to generate predictions.")