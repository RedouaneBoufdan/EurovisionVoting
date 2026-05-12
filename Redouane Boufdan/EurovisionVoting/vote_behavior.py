from pathlib import Path
import csv
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SONGS_FILE = DATA_DIR / "songs.csv"
MAP_RESULTS_FILE = RESULTS_DIR / "map_results.csv"
VOTE_BEHAVIOR_FILE = RESULTS_DIR / "vote_behavior.csv"

COUNTRY_CODES = {
    "SE": "Sweden",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "DE": "Germany",
    "BE": "Belgium",
    "NL": "Netherlands",
    "NO": "Norway",
    "DK": "Denmark",
    "FI": "Finland",
    "PT": "Portugal",
    "GR": "Greece",
    "PL": "Poland",
    "UA": "Ukraine",
    "GB": "United Kingdom",
    "CH": "Switzerland",
    "AT": "Austria",
    "IE": "Ireland",
    "CZ": "Czechia",
    "EE": "Estonia",
}


def load_song_mapping():
    mapping = {}
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[int(row["song_id"])] = row["country"]
    return mapping


def run_vote_behavior() -> None:
    song_map = load_song_mapping()
    behavior = defaultdict(int)

    with open(MAP_RESULTS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_country = COUNTRY_CODES[row["datacenter_country_code"]]
            to_country = song_map[int(row["song_id"])]
            votes = int(row["votes"])
            behavior[(from_country, to_country)] += votes

    ranked = sorted(behavior.items(), key=lambda x: x[1], reverse=True)

    with open(VOTE_BEHAVIOR_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["from_country", "to_country", "votes"])

        for (from_country, to_country), votes in ranked:
            writer.writerow([from_country, to_country, votes])

    print(f"Vote behavior completed: {VOTE_BEHAVIOR_FILE}")


if __name__ == "__main__":
    run_vote_behavior()