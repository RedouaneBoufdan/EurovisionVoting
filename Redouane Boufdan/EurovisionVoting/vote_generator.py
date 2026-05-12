from pathlib import Path
import csv
import random
import sys
import time
from datetime import datetime

from config import SONGS_FILE, DIAL_PREFIX, COUNTRY_CODES, FRIEND_BIAS, get_datacenter_for_country, ensure_directories
from streaming_storage import append_events, initialise_streaming_storage

DEFAULT_VOTES = 10000
RANDOM_SEED = 42

def load_songs() -> list[dict]:
    songs = []
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "song_id": int(row["song_id"]),
                "country": row["country"],
                "flag": row["flag"],
                "code": COUNTRY_CODES[row["country"]],
            })
    return songs

def generate_phone(country_code: str) -> str:
    prefix = DIAL_PREFIX[country_code]
    return prefix + str(random.randint(100000000, 999999999))

def choose_song(voter_code: str, songs: list[dict]) -> dict:
    available = [song for song in songs if song["code"] != voter_code]
    weights = []
    friends = set(FRIEND_BIAS.get(voter_code, []))
    for song in available:
        weight = 1.0
        if song["code"] in friends:
            weight += 2.5
        # Small show effect: some songs are naturally more popular during the evening.
        if song["code"] in {"SE", "UA", "IT", "FR"}:
            weight += 0.7
        weights.append(weight)
    return random.choices(available, weights=weights, k=1)[0]

def votes_for_second(total_votes: int, duration_sec: int, sec: int, remaining: int) -> int:
    # The final second always sends every remaining vote so the target is reached exactly.
    if sec >= duration_sec - 1:
        return remaining

    progress = sec / max(duration_sec, 1)
    base = total_votes / max(duration_sec, 1)
    if progress < 0.15:
        multiplier = 0.35
    elif progress < 0.55:
        multiplier = 0.95
    elif progress < 0.85:
        multiplier = 1.45
    else:
        multiplier = 2.40
    jitter = random.uniform(0.75, 1.25)
    return max(1, min(int(base * multiplier * jitter), remaining))

def generate_votes(num_votes: int, duration_sec: int, realtime: bool = False) -> int:
    random.seed(RANDOM_SEED)
    ensure_directories()
    initialise_streaming_storage()
    songs = load_songs()
    generated = 0
    remaining = num_votes

    for sec in range(duration_sec):
        if remaining <= 0:
            break
        amount = votes_for_second(num_votes, duration_sec, sec, remaining)
        batch = []
        now = datetime.now().isoformat(timespec="seconds")

        for _ in range(amount):
            voter = random.choice(songs)
            from_code = voter["code"]
            chosen = choose_song(from_code, songs)
            event_id = f"EVT-{generated + len(batch) + 1:09d}"
            batch.append([
                event_id,
                generate_phone(from_code),
                from_code,
                get_datacenter_for_country(from_code),
                chosen["song_id"],
                now,
            ])

        append_events(batch)
        generated += amount
        remaining -= amount
        print(f"[Voting simulation] second={sec + 1} +{amount} votes | total={generated} | remaining={remaining}")
        if realtime:
            time.sleep(1)

    print(f"Step 4 Voting simulation completed: {generated} votes generated")
    return generated

if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VOTES
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    realtime = "--realtime" in sys.argv
    generate_votes(total, duration, realtime=realtime)
