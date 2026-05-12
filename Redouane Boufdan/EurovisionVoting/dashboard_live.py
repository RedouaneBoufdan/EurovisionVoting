from pathlib import Path
import json
import subprocess
import sys
import time

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
LIVE_RESULTS_FILE = RESULTS_DIR / "live_results.csv"
LIVE_METRICS_FILE = RESULTS_DIR / "live_metrics.json"
LIVE_EVENTS_FILE = RESULTS_DIR / "live_events.csv"

st.set_page_config(page_title="Eurovision Real-Time Voting", layout="wide")
st.title("🎤 Eurovision Real-Time Voting Simulation")
st.caption("Votes arrive in irregular waves: quiet start, spikes, normal flow, and final rush.")

st.sidebar.header("Live Simulation")
total_votes = st.sidebar.number_input(
    "Target total votes",
    min_value=1_000,
    max_value=500_000_000,
    value=200_000_000,
    step=1_000_000,
)
duration_minutes = st.sidebar.slider("Duration in minutes", 1, 60, 10)
auto_refresh = st.sidebar.toggle("Auto-refresh every second", value=True)

if "process" not in st.session_state:
    st.session_state.process = None

start = st.sidebar.button("🚀 Start live simulation", use_container_width=True)
stop = st.sidebar.button("🛑 Stop simulation", use_container_width=True)

if start:
    RESULTS_DIR.mkdir(exist_ok=True)
    if st.session_state.process and st.session_state.process.poll() is None:
        st.sidebar.warning("A simulation is already running.")
    else:
        st.session_state.process = subprocess.Popen([
            sys.executable,
            str(BASE_DIR / "live_vote_engine.py"),
            str(int(total_votes)),
            str(int(duration_minutes * 60)),
        ])
        st.sidebar.success("Live simulation started.")

if stop and st.session_state.process and st.session_state.process.poll() is None:
    st.session_state.process.terminate()
    st.sidebar.warning("Simulation stopped.")

metrics = {}
if LIVE_METRICS_FILE.exists():
    with open(LIVE_METRICS_FILE, "r", encoding="utf-8") as f:
        metrics = json.load(f)

if metrics:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Current leader", metrics.get("current_leader", ""))
    c2.metric("Votes so far", f"{metrics.get('total_votes_so_far', 0):,}")
    c3.metric("Incoming last second", f"{metrics.get('incoming_votes_last_second', 0):,}")
    c4.metric("Progress", f"{metrics.get('progress_percent', 0)}%")
    c5.metric("Elapsed", f"{metrics.get('elapsed_seconds', 0)}s")

    st.progress(min(metrics.get("progress_percent", 0) / 100, 1.0))

if LIVE_RESULTS_FILE.exists():
    df = pd.read_csv(LIVE_RESULTS_FILE)
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("🥇 Live Ranking")
        view = df[["rank", "flag", "country", "total_votes"]].copy()
        view.columns = ["Rank", "Flag", "Country", "Votes"]
        st.dataframe(view, use_container_width=True, height=500)

    with right:
        st.subheader("📊 Top 10 live")
        top10 = df.head(10).copy()
        top10["label"] = top10["flag"] + " " + top10["country"]
        st.bar_chart(top10.set_index("label")["total_votes"])

if LIVE_EVENTS_FILE.exists():
    events = pd.read_csv(LIVE_EVENTS_FILE)
    if not events.empty:
        st.subheader("⚡ Incoming votes per second")
        st.line_chart(events.set_index("second")["incoming_votes"])

if auto_refresh:
    time.sleep(1)
    st.rerun()
