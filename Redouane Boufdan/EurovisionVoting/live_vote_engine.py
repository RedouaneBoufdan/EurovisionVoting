from pathlib import Path
import csv
import json
import random
import time
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SONGS_FILE = DATA_DIR / "songs.csv"
LIVE_RESULTS_FILE = RESULTS_DIR / "live_results.csv"
LIVE_METRICS_FILE = RESULTS_DIR / "live_metrics.json"
LIVE_EVENTS_FILE = RESULTS_DIR / "live_events.csv"

COUNTRY_CODES = {
    "Sweden": "SE", "France": "FR", "Italy": "IT", "Spain": "ES", "Germany": "DE",
    "Belgium": "BE", "Netherlands": "NL", "Norway": "NO", "Denmark": "DK", "Finland": "FI",
    "Portugal": "PT", "Greece": "GR", "Poland": "PL", "Ukraine": "UA", "United Kingdom": "GB",
    "Switzerland": "CH", "Austria": "AT", "Ireland": "IE", "Czechia": "CZ", "Estonia": "EE",
}

# Countries naturally vote a bit more for neighbours / culturally close countries.
FRIEND_BIAS = {
    "BE": ["FR", "NL"], "FR": ["BE", "CH"], "NL": ["BE", "DE"],
    "DE": ["AT", "CH", "NL"], "AT": ["DE", "CH"], "CH": ["FR", "DE", "AT"],
    "SE": ["NO", "DK", "FI"], "NO": ["SE", "DK"], "DK": ["SE", "NO"], "FI": ["SE", "EE"],
    "ES": ["PT", "FR"], "PT": ["ES"], "IE": ["GB"], "GB": ["IE"],
    "PL": ["UA", "CZ"], "UA": ["PL"], "CZ": ["PL", "AT"], "EE": ["FI"],
    "IT": ["CH", "FR"], "GR": ["IT"],
}


def load_songs():
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


def choose_song_for_voter(voter_code, songs):
    available = [s for s in songs if s["code"] != voter_code]

    # 65% normal random vote, 25% neighbour/cultural vote, 10% fan favourite effect.
    r = random.random()
    if r < 0.25:
        friends = FRIEND_BIAS.get(voter_code, [])
        friend_songs = [s for s in available if s["code"] in friends]
        if friend_songs:
            return random.choice(friend_songs)
    elif r > 0.90:
        # A few countries become public favourites, creating realistic dominance spikes.
        favourites = available[:5]
        return random.choice(favourites)

    return random.choice(available)


def wave_multiplier(progress):
    """Creates realistic waves: quiet start, spikes, calmer periods, final rush."""
    if progress < 0.08:
        return random.uniform(0.0, 0.12)      # first seconds/minutes: almost no votes
    if progress < 0.20:
        return random.uniform(1.5, 4.5)      # first big wave
    if progress < 0.70:
        return random.uniform(0.5, 1.8)      # normal voting
    if progress < 0.90:
        return random.uniform(2.0, 5.5)      # second big wave
    return random.uniform(4.0, 9.0)          # final rush


def create_schedule(total_votes, duration_seconds):
    weights = []
    for second in range(duration_seconds):
        progress = second / max(duration_seconds - 1, 1)
        weights.append(wave_multiplier(progress))

    total_weight = sum(weights)
    raw = [int(total_votes * w / total_weight) for w in weights]

    # Fix rounding difference so total is exact.
    diff = total_votes - sum(raw)
    for _ in range(abs(diff)):
        idx = random.randrange(duration_seconds)
        raw[idx] += 1 if diff > 0 else -1
    return raw


def write_live_files(totals, songs, elapsed, incoming_votes, total_target, duration_seconds, started_at, finished=False):
    by_song = {s["song_id"]: s for s in songs}
    ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    with open(LIVE_RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "song_id", "country", "flag", "total_votes"])
        for rank, (song_id, votes) in enumerate(ranked, start=1):
            song = by_song[song_id]
            writer.writerow([rank, song_id, song["country"], song["flag"], votes])

    total_so_far = sum(totals.values())
    leader = by_song[ranked[0][0]] if ranked else None
    metrics = {
        "started_at": started_at,
        "elapsed_seconds": elapsed,
        "duration_seconds": duration_seconds,
        "incoming_votes_last_second": incoming_votes,
        "total_votes_so_far": total_so_far,
        "target_votes": total_target,
        "progress_percent": round((total_so_far / total_target) * 100, 2) if total_target else 0,
        "current_leader": f"{leader['flag']} {leader['country']}" if leader else "",
        "finished": finished,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(LIVE_METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def run_live_simulation(total_votes=200_000_000, duration_seconds=600):
    random.seed()
    songs = load_songs()
    schedule = create_schedule(total_votes, duration_seconds)
    totals = defaultdict(int)
    started_at = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(LIVE_EVENTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["second", "incoming_votes"])

    # Initialize all songs at 0 so dashboard can display before votes arrive.
    for s in songs:
        totals[s["song_id"]] = 0
    write_live_files(totals, songs, 0, 0, total_votes, duration_seconds, started_at)

    for elapsed, incoming in enumerate(schedule, start=1):
        # Aggregate votes per second instead of writing 200M raw rows.
        for _ in range(min(incoming, 100_000)):
            voter = random.choice(songs)
            chosen = choose_song_for_voter(voter["code"], songs)
            # Scale if incoming is huge, to avoid looping millions in one second.
            scale = max(1, incoming // 100_000)
            totals[chosen["song_id"]] += scale

        # Correct possible undercount caused by scaling.
        current_total = sum(totals.values())
        expected_total = sum(schedule[:elapsed])
        missing = expected_total - current_total
        for _ in range(max(0, min(missing, 5000))):
            voter = random.choice(songs)
            chosen = choose_song_for_voter(voter["code"], songs)
            totals[chosen["song_id"]] += 1

        write_live_files(totals, songs, elapsed, incoming, total_votes, duration_seconds, started_at)
        with open(LIVE_EVENTS_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([elapsed, incoming])
        time.sleep(1)

    write_live_files(totals, songs, duration_seconds, 0, total_votes, duration_seconds, started_at, finished=True)


if __name__ == "__main__":
    import sys
    votes = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000_000
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    run_live_simulation(votes, seconds)
