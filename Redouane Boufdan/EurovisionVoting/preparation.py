from pathlib import Path
import csv
import json
from config import DATA_DIR, RESULTS_DIR, LOG_DIR, SONGS_FILE, DATACENTERS, ensure_directories

REQUIRED_COLUMNS = {"song_id", "country", "flag"}

def run_preparation(reset: bool = True) -> dict:
    ensure_directories()

    if not SONGS_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {SONGS_FILE}")

    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"songs.csv missing columns: {sorted(missing)}")
        songs = list(reader)

    if reset:
        for file in RESULTS_DIR.glob("*.csv"):
            file.unlink()
        for file in RESULTS_DIR.glob("*.json"):
            file.unlink()
        for file in RESULTS_DIR.glob("*.txt"):
            file.unlink()

    report = {
        "step": "Step 1 Preparation",
        "status": "ready",
        "songs_loaded": len(songs),
        "datacenters": list(DATACENTERS.keys()),
        "data_dir": str(DATA_DIR),
        "results_dir": str(RESULTS_DIR),
        "log_dir": str(LOG_DIR),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "preparation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report

if __name__ == "__main__":
    print(json.dumps(run_preparation(), indent=2))
