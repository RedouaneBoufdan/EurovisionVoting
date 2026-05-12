from pathlib import Path
import json
import subprocess
import sys

import pandas as pd
import streamlit as st

from config import RESULTS_DIR, GLOBAL_RESULTS_FILE, DATACENTER_RESULTS_FILE, WINNER_FILE, PIPELINE_METRICS_FILE

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Eurovision Voting Pipeline", layout="wide")
st.title("🎤 Eurovision Voting – Full Pipeline Dashboard")
st.caption("Adapted to the requested preparation → provisioning → deployment → services → streaming/storage → voting → results → shutdown pipeline.")

with st.sidebar:
    st.header("Run pipeline")
    votes = st.number_input("Total votes", min_value=1000, max_value=5_000_000, value=100_000, step=1000)
    duration = st.slider("Simulation duration", min_value=5, max_value=120, value=30)
    if st.button("🚀 Run full pipeline", use_container_width=True):
        subprocess.run([sys.executable, str(BASE_DIR / "pipeline.py"), "--votes", str(int(votes)), "--duration", str(int(duration))])
        st.success("Pipeline finished. Refresh if needed.")

st.header("Pipeline steps")
steps = [
    "Step 1 Preparation",
    "Step 2 Provisioning: Proxmox + AWS Instance with HashiCorp Terraform",
    "Step 3 Deployment",
    "Step 3A Services: Docker + Kubernetes",
    "Step 3B Streaming + Storage",
    "Step 4 Voting simulation",
    "Step 5 Results per datacenter",
    "Step 6 Global results",
    "Step 7 Announce winners",
    "Step 8 After event: Stop all systems",
]
st.table(pd.DataFrame({"Required step": steps}))

if PIPELINE_METRICS_FILE.exists():
    metrics = json.loads(PIPELINE_METRICS_FILE.read_text(encoding="utf-8"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Requested votes", f"{metrics.get('requested_votes', 0):,}")
    c2.metric("Generated votes", f"{metrics.get('generated_votes', 0):,}")
    c3.metric("Pipeline time", f"{metrics.get('total_pipeline_time_seconds', 0)}s")

if WINNER_FILE.exists():
    st.subheader("🏆 Winner announcement")
    st.code(WINNER_FILE.read_text(encoding="utf-8"))

left, right = st.columns([1.2, 1])

with left:
    st.subheader("🌍 Global results")
    if GLOBAL_RESULTS_FILE.exists():
        df = pd.read_csv(GLOBAL_RESULTS_FILE)
        st.dataframe(df, use_container_width=True, height=420)
        top10 = df.head(10).copy()
        top10["label"] = top10["flag"] + " " + top10["country"]
        st.bar_chart(top10.set_index("label")["total_votes"])
    else:
        st.info("Run the pipeline first.")

with right:
    st.subheader("🏢 Results per datacenter")
    if DATACENTER_RESULTS_FILE.exists():
        dc = pd.read_csv(DATACENTER_RESULTS_FILE)
        summary = dc.groupby("datacenter")["votes"].sum().reset_index().sort_values("votes", ascending=False)
        st.dataframe(summary, use_container_width=True)
        st.bar_chart(summary.set_index("datacenter")["votes"])
    else:
        st.info("No datacenter results yet.")

st.subheader("📁 Output files")
if RESULTS_DIR.exists():
    files = sorted([p.name for p in RESULTS_DIR.iterdir() if p.is_file()])
    st.write(files)
