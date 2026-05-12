from pathlib import Path
import pandas as pd
import streamlit as st
import time

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

VOTES_FILE = DATA_DIR / "votes.csv"
SONGS_FILE = DATA_DIR / "songs.csv"

st.set_page_config(page_title="Live Voting CSV", layout="wide")

st.title("🎤 Eurovision Voting (CSV Live Mode)")
st.caption("Refresh manually to see updates")

# 🔄 bouton refresh manuel
if st.button("🔄 Refresh"):
    st.rerun()

# ⚠️ si pas de fichier
if not VOTES_FILE.exists():
    st.info("No votes yet...")
    st.stop()

# 📥 charger votes (ATTENTION gros fichier)
df = pd.read_csv(VOTES_FILE)

# 📊 métriques
total_votes = len(df)

st.subheader("📊 Metrics")
col1, col2 = st.columns(2)

col1.metric("Total Votes", f"{total_votes:,}")

# 📥 charger songs pour mapping pays
songs_df = pd.read_csv(SONGS_FILE)

# merge pour avoir pays
merged = df.merge(songs_df, on="song_id")

# 📊 ranking
ranking = (
    merged.groupby(["country", "flag"])
    .size()
    .reset_index(name="votes")
    .sort_values("votes", ascending=False)
)

# 🏆 classement
st.markdown("---")
st.subheader("🏆 Live Ranking")

st.dataframe(ranking, use_container_width=True)

# 📈 top 10
st.subheader("📊 Top 10")

top10 = ranking.head(10).copy()
top10["label"] = top10["flag"] + " " + top10["country"]

chart = top10.set_index("label")["votes"]
st.bar_chart(chart)

# 📡 derniers votes
st.markdown("---")
st.subheader("📡 Last 20 Votes")

last_votes = df.tail(20)

st.dataframe(last_votes, use_container_width=True)