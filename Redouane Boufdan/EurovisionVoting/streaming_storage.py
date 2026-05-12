import csv
import json
from datetime import datetime
from pathlib import Path
from config import VOTES_STREAM_FILE, VOTES_STORAGE_FILE, RESULTS_DIR, ensure_directories

HEADER = ["event_id", "phone_number", "from_country_code", "datacenter", "song_id", "timestamp"]

def initialise_streaming_storage() -> dict:
    ensure_directories()
    for file in (VOTES_STREAM_FILE, VOTES_STORAGE_FILE):
        if not file.exists():
            with open(file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(HEADER)

    report = {
        "step": "Step 3B Streaming and Storage",
        "status": "ready",
        "stream_file": str(VOTES_STREAM_FILE),
        "storage_file": str(VOTES_STORAGE_FILE),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "explanation": "votes_stream.csv simulates an incoming stream; votes_storage.csv simulates persisted storage.",
    }
    with open(RESULTS_DIR / "streaming_storage_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report

def append_events(events: list[list[str]]) -> None:
    ensure_directories()
    files_need_header = [file for file in (VOTES_STREAM_FILE, VOTES_STORAGE_FILE) if not file.exists()]
    for file in files_need_header:
        with open(file, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

    for file in (VOTES_STREAM_FILE, VOTES_STORAGE_FILE):
        with open(file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(events)

if __name__ == "__main__":
    print(json.dumps(initialise_streaming_storage(), indent=2))
