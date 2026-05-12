import csv
from datetime import datetime
from config import GLOBAL_RESULTS_FILE, WINNER_FILE

def announce_winner() -> dict:
    if not GLOBAL_RESULTS_FILE.exists():
        raise FileNotFoundError("Run Step 6 first: no global_results.csv found.")

    with open(GLOBAL_RESULTS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        winner = next(reader)

    text = (
        "EUROVISION VOTING RESULT\n"
        "========================\n"
        f"Winner: {winner['flag']} {winner['country']}\n"
        f"Song ID: {winner['song_id']}\n"
        f"Votes: {int(winner['total_votes']):,}\n"
        f"Announced at: {datetime.now().isoformat(timespec='seconds')}\n"
    )

    with open(WINNER_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    print(text)
    return winner

if __name__ == "__main__":
    announce_winner()
