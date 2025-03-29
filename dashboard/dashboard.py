import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -- Disclaimer Popup --
if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    with st.modal("⚠️ Disclaimer"):
        st.markdown("""
        #### This dashboard is for testing and educational purposes only.
        - Do not use this for actual gambling decisions.
        - Any gambling should be done responsibly and only by persons **21+** years old.
        """)
        if st.button("I Acknowledge and Accept"):
            st.session_state.disclaimer_accepted = True
        st.stop()

st.set_page_config(page_title="MLB Betting AI", layout="wide")
st.title("⚾️ MLB Betting AI Dashboard")

# --- Load paths ---
props_path = "data/player_prop_predictions.csv"
history_path = "data/prediction_history.csv"
results_path = "data/bet_results.csv"

# --- 🔍 Player Search ---
st.sidebar.markdown("### 🔍 Search Player Predictions")
player_search = st.sidebar.text_input("Player Name (e.g., Shohei Ohtani)")
date_search = st.sidebar.date_input("Prediction Date", datetime.today())
if player_search:
    try:
        df = pd.read_csv(props_path)
        df["prediction_date"] = pd.to_datetime(df["prediction_date"])
        filtered = df[
            (df["player_name"].str.lower().str.contains(player_search.lower())) &
            (df["prediction_date"] == pd.to_datetime(date_search))
        ]
        st.subheader(f"🔎 Predictions for **{player_search.title()}** on {date_search.strftime('%Y-%m-%d')}")
        st.dataframe(filtered, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load predictions: {e}")

# --- 📈 Value Bets ---
st.subheader("🔔 Recent Value Bets (Last 24 Hours)")
try:
    results = pd.read_csv(results_path)
    results["timestamp"] = pd.to_datetime(results["timestamp"])
    recent = results[results["timestamp"] > datetime.now() - pd.Timedelta(hours=24)]
    st.dataframe(recent, use_container_width=True)
except:
    st.warning("⚠️ bet_results.csv not found. Run run_bot.py to create it.")

# --- 🔮 Prediction History ---
st.subheader("🔮 Prediction History")
try:
    history = pd.read_csv(history_path)
    st.dataframe(history.tail(100), use_container_width=True)
except:
    st.warning("⚠️ prediction_history.csv not found. Run run_bot.py to generate predictions.")

# --- ✅ Win/Loss Summary ---
st.subheader("✅ Win/Loss Summary")
try:
    win_loss = pd.read_csv(results_path)
    wins = (win_loss["result"] == "win").sum()
    losses = (win_loss["result"] == "loss").sum()
    st.metric("Wins", wins)
    st.metric("Losses", losses)
except:
    st.warning("⚠️ bet_results.csv not found. Run run_bot.py to create it.")

# --- 🏆 Leaderboard ---
st.subheader("🏆 Team Leaderboard (Top Predicted Wins)")
try:
    df = pd.read_csv(history_path)
    leaderboard = df.groupby("team")["prediction"].mean().sort_values(ascending=False).reset_index()
    st.dataframe(leaderboard.head(10), use_container_width=True)
except:
    st.warning("⚠️ prediction_history.csv not found.")

# --- 📊 Confidence Distribution ---
st.subheader("📊 Confidence Distribution (Model Predictions)")
try:
    st.bar_chart(df["prediction"])
except:
    st.warning("⚠️ prediction_history.csv not found.")

# --- 🧠 Upcoming Predictions ---
st.subheader("🧠 Upcoming Games + Model Predictions")
try:
    upcoming = pd.read_csv("data/upcoming_predictions.csv")
    st.dataframe(upcoming, use_container_width=True)
except:
    st.warning("📊 Run scrape_odds.py and run_bot.py to see predictions with odds.")

# --- 🎯 Player Prop Predictions ---
st.subheader("🎯 Player Prop Predictions")
try:
    props_df = pd.read_csv(props_path)
    st.markdown("##### 🧢 Predicted Hits")
    st.dataframe(
        props_df[props_df["prop_type"] == "hits"].sort_values("prediction", ascending=False),
        use_container_width=True,
    )

    st.markdown("##### 🎯 Predicted Strikeouts")
    st.dataframe(
        props_df[props_df["prop_type"] == "strikeouts"].sort_values("prediction", ascending=False),
        use_container_width=True,
    )
except:
    st.warning("⚠️ player_prop_predictions.csv not found. Run predict_player_props.py.")