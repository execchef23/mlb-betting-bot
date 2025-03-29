import streamlit as st
import pandas as pd
import os
from datetime import datetime
import subprocess

st.set_page_config(page_title="⚾️ MLB Betting AI Dashboard", layout="wide")

# =======================
# 🔐 Disclaimer Section
# =======================
st.markdown("### ⚠️ Disclaimer")
with st.expander("Click to read and acknowledge the disclaimer", expanded=True):
    st.write("""
    This tool is for **testing purposes only**. Any gambling activity should be done responsibly and only by persons over the age of **21**. 
    Please comply with all applicable laws and regulations in your jurisdiction.
    """)
    agree = st.checkbox("I acknowledge and accept the disclaimer above.")
    if not agree:
        st.stop()

st.title("⚾️ MLB Betting AI Dashboard")

# Paths
prediction_history_path = "data/prediction_history.csv"
bet_results_path = "data/bet_results.csv"
player_props_path = "data/player_prop_predictions.csv"

# =======================
# 🔔 Recent Value Bets
# =======================
st.subheader("🔔 Recent Value Bets (Last 24 Hours)")
try:
    df = pd.read_csv(bet_results_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    recent_bets = df[df["timestamp"] > datetime.now() - pd.Timedelta(hours=24)]
    st.dataframe(recent_bets.sort_values("timestamp", ascending=False), use_container_width=True)
except Exception as e:
    st.warning(f"Error loading bet history: {e}")

# =======================
# 🔮 Prediction History
# =======================
st.subheader("🔮 Prediction History")
try:
    df = pd.read_csv(prediction_history_path)
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
except FileNotFoundError:
    st.warning("⚠️ prediction_history.csv not found. Run run_bot.py to generate predictions.")

# =======================
# ✅ Win/Loss Summary
# =======================
st.subheader("✅ Win/Loss Summary")
try:
    df = pd.read_csv(bet_results_path)
    total_bets = len(df)
    wins = (df["result"] == "win").sum()
    losses = (df["result"] == "loss").sum()
    roi = df["roi"].mean() * 100

    st.metric("Total Bets", total_bets)
    st.metric("Wins", wins)
    st.metric("Losses", losses)
    st.metric("Average ROI", f"{roi:.2f}%")
except:
    st.warning("⚠️ bet_results.csv not found. Run run_bot.py to create it.")

# =======================
# 🏆 Team Leaderboard
# =======================
st.subheader("🏆 Team Leaderboard (Top Predicted Wins)")
try:
    df = pd.read_csv(prediction_history_path)
    team_stats = df.groupby("team")["model_pred"].mean().sort_values(ascending=False).reset_index()
    st.dataframe(team_stats.rename(columns={"model_pred": "Avg Predicted Win %"}), use_container_width=True)
except:
    pass

# =======================
# 📊 Confidence Distribution
# =======================
st.subheader("📊 Confidence Distribution (Model Predictions)")
try:
    import matplotlib.pyplot as plt

    df = pd.read_csv(prediction_history_path)
    fig, ax = plt.subplots()
    ax.hist(df["model_pred"], bins=20, edgecolor="black")
    ax.set_title("Model Prediction Confidence Distribution")
    ax.set_xlabel("Predicted Win Probability")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)
except:
    pass

# =======================
# 🧠 Upcoming Games + Predictions
# =======================
st.subheader("🧠 Upcoming Games + Model Predictions")
try:
    from scripts.prediction.predict_with_features import load_upcoming_predictions
    upcoming_df = load_upcoming_predictions()
    st.dataframe(upcoming_df.sort_values("model_pred", ascending=False), use_container_width=True)
except:
    st.markdown("📊 Run the pipeline to see predictions with odds.")

# =======================
# 🎯 Player Prop Predictions
# =======================
st.subheader("🎯 Player Prop Predictions")
try:
    props_df = pd.read_csv(player_props_path)
    st.markdown("##### 🧢 Predicted Hits")
    st.dataframe(props_df[props_df["prop_type"] == "hits"].sort_values("prediction", ascending=False), use_container_width=True)

    st.markdown("##### 🎯 Predicted Strikeouts")
    st.dataframe(props_df[props_df["prop_type"] == "strikeouts"].sort_values("prediction", ascending=False), use_container_width=True)
except:
    st.warning("⚠️ player_prop_predictions.csv not found. Run predict_player_props.py.")

# =======================
# 🔍 Player Search
# =======================
st.subheader("🔍 Search Player Prop Prediction")

try:
    props_df = pd.read_csv(player_props_path)
    player_name_input = st.text_input("Enter Player Name (e.g. Mookie Betts):", "")
    search_date = datetime.today().strftime("%Y-%m-%d")  # default to today

    if player_name_input:
        filtered = props_df[
            (props_df["player_name"].str.lower().str.contains(player_name_input.lower())) &
            (props_df["prediction_date"] == search_date)
        ]
        if not filtered.empty:
            st.markdown(f"##### 🎯 Predictions for {player_name_input.title()} on {search_date}")
            st.dataframe(filtered[["player_name", "prop_type", "prediction", "prediction_date"]], use_container_width=True)
        else:
            st.warning(f"No predictions found for {player_name_input} on {search_date}.")
except:
    st.warning("⚠️ player_prop_predictions.csv not found. Run predict_player_props.py.")

# =======================
# ▶️ Run Full Daily Pipeline
# =======================
st.subheader("▶️ Run Full Daily Pipeline")

run_pipeline = st.checkbox("✅ I confirm I want to run the full prediction pipeline")

def run_script(script_path):
    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )
        st.success(f"✅ Ran {script_path}")
        st.text(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error running {script_path}")
        st.text(e.stderr)

if run_pipeline:
    if st.button("🚀 Run Pipeline Now"):
        with st.spinner("Running scripts..."):
            run_script("scripts/prediction/scrape_odds.py")
            run_script("scripts/features/enhance_features.py")
            run_script("scripts/run/run_bot.py")
            run_script("scripts/evaluation/track_results.py")
            run_script("scripts/data/fetch_player_data.py")
            run_script("scripts/features/engineer_player_features.py")
            run_script("scripts/prediction/predict_player_props.py")