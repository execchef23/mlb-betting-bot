import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="MLB Betting AI Dashboard", layout="wide")

# ✅ DISCLAIMER
if "disclaimer_ack" not in st.session_state:
    st.session_state.disclaimer_ack = False

if not st.session_state.disclaimer_ack:
    with st.expander("⚠️ Disclaimer - Click to Acknowledge", expanded=True):
        st.markdown("""
        This dashboard is for **testing and educational purposes only**.

        🚫 It does **not constitute gambling advice**, and any betting should be done **responsibly** and only by persons **21 years or older**.

        ✅ By clicking below, you acknowledge this disclaimer.
        """)
        if st.button("I Acknowledge and Wish to Continue"):
            st.session_state.disclaimer_ack = True
    st.stop()

st.title("⚾️ MLB Betting AI Dashboard")

# 📂 Load Files
bet_path = "data/bet_results.csv"
history_path = "data/prediction_history.csv"
props_path = "data/player_prop_predictions.csv"

# 🔔 Recent Value Bets
st.subheader("🔔 Recent Value Bets (Last 24 Hours)")
try:
    bets = pd.read_csv(bet_path)
    bets["timestamp"] = pd.to_datetime(bets["timestamp"])
    recent_bets = bets[bets["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=1)]
    st.dataframe(recent_bets.sort_values("timestamp", ascending=False), use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ No bet history found. Run run_bot.py to create bet_results.csv.")

# 🔮 Prediction History
st.subheader("🔮 Prediction History")
try:
    history = pd.read_csv(history_path)
    st.dataframe(history.sort_values("timestamp", ascending=False), use_container_width=True)
except:
    st.warning("⚠️ prediction_history.csv not found. Run run_bot.py to generate predictions.")

# ✅ Win/Loss Summary
st.subheader("✅ Win/Loss Summary")
try:
    total_bets = len(bets)
    wins = (bets["result"] == "WIN").sum()
    losses = (bets["result"] == "LOSS").sum()
    bankroll = bets["bankroll"].iloc[-1] if total_bets > 0 else 1000
    roi = round(bets["roi"].mean(), 4) if "roi" in bets.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bets", total_bets)
    col2.metric("Wins", wins)
    col3.metric("Losses", losses)
    col4.metric("ROI per Bet", f"{roi*100:.2f}%")
except:
    st.warning("⚠️ bet_results.csv not found. Run run_bot.py to create it.")

# 🏆 Team Leaderboard
st.subheader("🏆 Team Leaderboard (Top Predicted Wins)")
try:
    leaderboard = history.groupby("home_team").agg({
        "model_prob": "mean",
        "edge": "mean"
    }).sort_values("model_prob", ascending=False).reset_index()
    st.dataframe(leaderboard, use_container_width=True)
except:
    pass

# 📊 Confidence Distribution
st.subheader("📊 Confidence Distribution (Model Predictions)")
try:
    st.bar_chart(history["model_prob"])
except:
    pass

# 🧠 Upcoming Games + Model Predictions
st.subheader("🧠 Upcoming Games + Model Predictions")
try:
    upcoming = pd.read_csv("data/live_game_features.csv")
    preds = pd.read_csv("data/predictions.csv")

    full = upcoming.merge(preds, on=["home_team", "away_team"])
    full = full[["home_team", "away_team", "model_prob", "implied_prob", "edge", "moneyline"]]

    edge_filter = st.checkbox("📈 Only show value bets (edge > 5%)", value=False)
    if edge_filter:
        full = full[full["edge"] > 0.05]

    st.dataframe(full.sort_values("edge", ascending=False), use_container_width=True)
except:
    st.warning("📊 Run scrape_odds.py and run_bot.py to see predictions with odds.")

# 🎯 Player Prop Predictions
st.subheader("🎯 Player Prop Predictions")

props_path = "data/player_prop_predictions.csv"  # ✅ Add this line

try:
    props_df = pd.read_csv(props_path)
    st.markdown("##### 🧢 Predicted Hits")
    st.dataframe(props_df[props_df["prop_type"] == "hits"].sort_values("prediction", ascending=False), use_container_width=True)

    st.markdown("##### 🎯 Predicted Strikeouts")
    st.dataframe(props_df[props_df["prop_type"] == "strikeouts"].sort_values("prediction", ascending=False), use_container_width=True)
except:
    st.warning("⚠️ player_prop_predictions.csv not found. Run predict_player_props.py.")