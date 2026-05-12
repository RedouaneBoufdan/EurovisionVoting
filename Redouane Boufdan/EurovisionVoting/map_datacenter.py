import csv
from collections import defaultdict
from datetime import datetime
from config import VOTES_STORAGE_FILE, DATACENTER_RESULTS_FILE, ensure_directories

def run_map() -> None:
    ensure_directories()
    if not VOTES_STORAGE_FILE.exists():
        raise FileNotFoundError("Run Step 3B and Step 4 first: no votes_storage.csv found.")

    counts = defaultdict(int)
    with open(VOTES_STORAGE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("song_id"):
                continue
            key = (row["datacenter"], row["from_country_code"], int(row["song_id"]))
            counts[key] += 1

    timestamp = datetime.now().isoformat(timespec="seconds")
    with open(DATACENTER_RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["datacenter", "from_country_code", "song_id", "votes", "calculated_at"])
        for (datacenter, country_code, song_id), votes in sorted(counts.items()):
            writer.writerow([datacenter, country_code, song_id, votes, timestamp])

    print(f"Step 5 Results per datacenter completed: {DATACENTER_RESULTS_FILE}")

if __name__ == "__main__":
    run_map()
