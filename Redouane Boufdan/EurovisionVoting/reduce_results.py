import csv
from collections import defaultdict
from config import SONGS_FILE, DATACENTER_RESULTS_FILE, GLOBAL_RESULTS_FILE, ensure_directories

def load_song_mapping() -> dict[int, dict]:
    mapping = {}
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[int(row["song_id"])] = {"country": row["country"], "flag": row["flag"]}
    return mapping

def run_reduce() -> list[dict]:
    ensure_directories()
    if not DATACENTER_RESULTS_FILE.exists():
        raise FileNotFoundError("Run Step 5 first: no datacenter_results.csv found.")

    songs = load_song_mapping()
    totals = defaultdict(int)
    datacenter_breakdown = defaultdict(lambda: defaultdict(int))

    with open(DATACENTER_RESULTS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song_id = int(row["song_id"])
            votes = int(row["votes"])
            totals[song_id] += votes
            datacenter_breakdown[song_id][row["datacenter"]] += votes

    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    results = []
    with open(GLOBAL_RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["rank", "song_id", "country", "flag", "total_votes", "dc_west", "dc_north", "dc_central", "dc_south"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rank, (song_id, total_votes) in enumerate(ranked, start=1):
            row = {
                "rank": rank,
                "song_id": song_id,
                "country": songs[song_id]["country"],
                "flag": songs[song_id]["flag"],
                "total_votes": total_votes,
                "dc_west": datacenter_breakdown[song_id].get("dc-west", 0),
                "dc_north": datacenter_breakdown[song_id].get("dc-north", 0),
                "dc_central": datacenter_breakdown[song_id].get("dc-central", 0),
                "dc_south": datacenter_breakdown[song_id].get("dc-south", 0),
            }
            writer.writerow(row)
            results.append(row)

    print(f"Step 6 Global results completed: {GLOBAL_RESULTS_FILE}")
    return results

if __name__ == "__main__":
    run_reduce()
