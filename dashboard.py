import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="MLB Betting AI Dashboard", layout="wide")
st.title("⚾ MLB Betting AI Dashboard")

# =========================
# 📢 Disclaimer & Consent
# =========================
st.markdown("### 📢 Disclaimer")
st.markdown("""
**This tool is for educational and testing purposes only.**

- It does not constitute gambling advice or guarantees of success.  
- All wagering should be done **responsibly** and **only by persons 21 years or older** in jurisdictions where sports betting is legal.  
- By using this dashboard, you acknowledge that any decisions based on this information are your own responsibility.
""")

agreed = st.checkbox("✅ I acknowledge the disclaimer above and confirm I am 21+.")

if not agreed:
    st.warning("🚫 Please acknowledge the disclaimer to access the dashboard.")
    st.stop()

# ========================
# 🔔 Recent Value Bets
# ========================
st.subheader("🔔 Recent Value Bets (Last 24 Hours)")

try:
    bet_df = pd.read_csv("data/bet_results.csv", parse_dates=["timestamp"])
    recent = bet_df[bet_df["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=1)]
    if not recent.empty:
        st.dataframe(recent.sort_values("timestamp", ascending=False), use_container_width=True)
    else:
        st.info("📭 No bet history found in the last 24 hours.")
except Exception as e:
    st.warning(f"Error loading bet history: {e}")

# ========================
# 🔮 Prediction History
# ========================
st.subheader("🔮 Prediction History")

history_path = "data/prediction_history.csv"
if os.path.exists(history_path):
    hist = pd.read_csv(history_path)
    hist["timestamp"] = pd.to_datetime(hist["timestamp"])
    st.dataframe(hist.sort_values("timestamp", ascending=False), use_container_width=True)
else:
    st.warning("⚠️ prediction_history.csv not found. Run run_bot.py to generate predictions.")

# ========================
# ✅ Win/Loss Summary
# ========================
st.subheader("✅ Win/Loss Summary")

if os.path.exists("data/bet_results.csv"):
    df = pd.read_csv("data/bet_results.csv")
    if "result" in df.columns:
        wins = (df["result"] == "WIN").sum()
        losses = (df["result"] == "LOSS").sum()
        bankroll = df["bankroll"].iloc[-1] if "bankroll" in df.columns else "N/A"
        st.markdown(f"""
        - ✅ Wins: **{wins}**  
        - ❌ Losses: **{losses}**  
        - 💰 Current Bankroll: **${bankroll}**
        """)
    else:
        st.info("📭 No win/loss results found.")
else:
    st.warning("⚠️ bet_results.csv not found. Run run_bot.py to create it.")

# ========================
# 📈 Bankroll Over Time
# ========================
if os.path.exists("data/bet_results.csv"):
    df = pd.read_csv("data/bet_results.csv")
    if "timestamp" in df.columns and "bankroll" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        fig, ax = plt.subplots()
        ax.plot(df["timestamp"], df["bankroll"], marker="o")
        ax.set_title("📈 Bankroll Over Time")
        ax.set_ylabel("Bankroll ($)")
        ax.set_xlabel("Date")
        st.pyplot(fig)

# ========================
# 🏆 Team Leaderboard
# ========================
st.subheader("🏆 Team Leaderboard (Top Predicted Wins)")

if os.path.exists("data/prediction_history.csv"):
    hist = pd.read_csv("data/prediction_history.csv")
    top = hist["home_team"].value_counts().head(10).reset_index()
    top.columns = ["Team", "Predicted Wins"]
    st.dataframe(top, use_container_width=True)

# ========================
# 📊 Confidence Distribution
# ========================
st.subheader("📊 Confidence Distribution (Model Predictions)")

if os.path.exists("data/prediction_history.csv"):
    hist = pd.read_csv("data/prediction_history.csv")
    if "edge" in hist.columns:
        fig, ax = plt.subplots()
        ax.hist(hist["edge"], bins=20, edgecolor='black')
        ax.set_title("Model Edge % Distribution")
        ax.set_xlabel("Edge %")
        ax.set_ylabel("Number of Games")
        st.pyplot(fig)

# ========================
# 🧠 Upcoming Games + Model Predictions
# ========================
st.subheader("🧠 Upcoming Games + Model Predictions")

upcoming_path = "data/live_game_predictions.csv"
if os.path.exists(upcoming_path):
    df = pd.read_csv(upcoming_path)
    df["edge %"] = (df["model_prob"] - df["implied_prob"]) * 100
    df["edge %"] = df["edge %"].round(2)

    show_only_edges = st.toggle("Only show bets with edge > 5%")
    if show_only_edges:
        df = df[df["edge %"] > 5]

    st.dataframe(df.sort_values("edge %", ascending=False), use_container_width=True)
    st.download_button("📥 Download Predictions (CSV)", df.to_csv(index=False), "upcoming_predictions.csv")
else:
    st.info("📊 Run scrape_odds.py and run_bot.py to see predictions with odds.")

# ========================
# 🎯 Player Prop Predictions
# ========================
st.subheader("🎯 Player Prop Predictions")

prop_path = "data/player_prop_predictions.csv"
if os.path.exists(prop_path):
    props_df = pd.read_csv(prop_path)
    props_today = props_df[props_df["game_date"] == str(date.today())]

    if not props_today.empty:
        st.dataframe(
            props_today.sort_values("hit_prob", ascending=False),
            use_container_width=True
        )
    else:
        st.info("📭 No player props for today yet. Run predict_player_props.py.")
else:
    st.warning("⚠️ player_prop_predictions.csv not found. Run predict_player_props.py.")