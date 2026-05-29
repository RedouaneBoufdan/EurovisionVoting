from __future__ import annotations

import argparse
import csv
import json
import os
import random
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import Request, urlopen

from config import COUNTRY_CODES, DATACENTERS, DIAL_PREFIX, FRIEND_BIAS, SONGS_FILE

RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
WORKER_HOST = os.getenv("WORKER_HOST", "0.0.0.0")
WORKER_PORT = int(os.getenv("WORKER_PORT", "9000"))

run_lock = threading.Lock()
run_state = {
    "running": False,
    "datacenter": os.getenv("DATACENTER", "dc-belgium"),
    "generated": 0,
    "target_votes": 0,
    "duration_sec": 0,
    "started_at": None,
    "finished_at": None,
    "last_error": None,
}


def load_songs() -> list[dict]:
    songs = []
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(
                {
                    "song_id": int(row["song_id"]),
                    "country": row["country"],
                    "flag": row.get("flag", ""),
                    "code": COUNTRY_CODES[row["country"]],
                }
            )
    return songs


def generate_phone(country_code: str) -> str:
    return DIAL_PREFIX[country_code] + str(random.randint(100000000, 999999999))


def choose_song(voter_code: str, songs: list[dict]) -> dict:
    # Eurovision rule: a country cannot vote for itself.
    available = [song for song in songs if song["code"] != voter_code]
    if not available:
        available = songs[:]
    friends = set(FRIEND_BIAS.get(voter_code, []))
    weights = []
    for song in available:
        weight = 1.0
        if song["code"] in friends:
            weight += 2.3
        if song["code"] in {"SE", "UA", "IT", "FR", "DE"}:
            weight += 0.6
        weights.append(weight)
    return random.choices(available, weights=weights, k=1)[0]


def votes_for_second(total_votes: int, duration_sec: int, second_index: int, remaining: int) -> int:
    # Realistic live effect: not flat; the middle/end is a bit busier.
    if duration_sec <= 1:
        return remaining
    progress = second_index / max(1, duration_sec - 1)
    wave = 0.65 + 0.85 * (1 - abs(progress - 0.68))
    jitter = random.uniform(0.55, 1.45)
    base = total_votes / max(1, duration_sec)
    amount = max(1, int(base * wave * jitter))

    seconds_left = duration_sec - second_index
    if seconds_left <= 1:
        return remaining
    # Keep enough votes for the remaining seconds.
    return min(remaining, max(1, min(amount, remaining - (seconds_left - 1))))


def post_json(url: str, payload: dict, timeout: int = 10) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_central(central_url: str, attempts: int = 60) -> None:
    health_url = central_url.rstrip("/") + "/health"
    for _ in range(attempts):
        try:
            with urlopen(health_url, timeout=3) as response:
                if response.status == 200:
                    return
        except URLError:
            pass
        time.sleep(1)
    raise RuntimeError("central aggregator did not become ready")


def run_worker(datacenter: str, total_votes: int, duration_sec: int, central_url: str, batch_size: int, song_ids: list[int] | None = None) -> None:
    random.seed(RANDOM_SEED + abs(hash(datacenter)) % 100000 + int(time.time()))
    all_songs = load_songs()
    allowed = set(song_ids or [])
    songs = [s for s in all_songs if not allowed or s["song_id"] in allowed]
    if len(songs) < 2:
        raise ValueError("A test needs at least 2 participating countries/songs.")

    info = DATACENTERS[datacenter]
    voter_code = info["country_code"]
    worker_name = f"worker-{datacenter}"
    post_url = central_url.rstrip("/") + "/api/votes"

    with run_lock:
        run_state.update({
            "running": True,
            "datacenter": datacenter,
            "generated": 0,
            "target_votes": total_votes,
            "duration_sec": duration_sec,
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": None,
            "last_error": None,
        })

    print("=" * 70)
    print(f"Datacenter started: {info['display_name']} ({datacenter})")
    print(f"Country handled: {info['country']} ({voter_code})")
    print(f"Test votes={total_votes}, duration={duration_sec}s, batch_size={batch_size}, songs={len(songs)}")
    print("=" * 70)

    try:
        wait_for_central(central_url)
        generated = 0
        remaining = total_votes
        local_buffer: list[dict] = []

        for sec in range(duration_sec):
            if remaining <= 0:
                break
            amount = votes_for_second(total_votes, duration_sec, sec, remaining)
            now = datetime.now().isoformat(timespec="seconds")
            for _ in range(amount):
                chosen = choose_song(voter_code, songs)
                generated += 1
                remaining -= 1
                local_buffer.append(
                    {
                        "event_id": f"{datacenter}-EVT-{int(time.time())}-{generated:09d}",
                        "phone_number": generate_phone(voter_code),
                        "from_country_code": voter_code,
                        "datacenter": datacenter,
                        "song_id": chosen["song_id"],
                        "timestamp": now,
                    }
                )
                if len(local_buffer) >= batch_size:
                    response = post_json(post_url, {"worker": worker_name, "events": local_buffer})
                    print(f"[{datacenter}] sent batch={len(local_buffer)} | central_total={response.get('total_votes')}")
                    local_buffer = []

            if local_buffer:
                response = post_json(post_url, {"worker": worker_name, "events": local_buffer})
                print(f"[{datacenter}] second={sec + 1:03d} sent={len(local_buffer)} | central_total={response.get('total_votes')}")
                local_buffer = []
            with run_lock:
                run_state["generated"] = generated
            time.sleep(1)

        print(f"[{datacenter}] finished: {generated} votes sent to central aggregator")
        with run_lock:
            run_state.update({"running": False, "generated": generated, "finished_at": datetime.now().isoformat(timespec="seconds")})
    except Exception as exc:
        print(f"[{datacenter}] ERROR: {exc}")
        with run_lock:
            run_state.update({"running": False, "last_error": str(exc), "finished_at": datetime.now().isoformat(timespec="seconds")})


class WorkerHandler(BaseHTTPRequestHandler):
    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body.decode("utf-8"))

    def json_response(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            with run_lock:
                payload = dict(run_state)
            payload["status"] = "ok"
            self.json_response(payload)
            return
        self.json_response({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/start":
            self.json_response({"error": "not found"}, status=404)
            return
        payload = self.read_json()
        with run_lock:
            if run_state["running"]:
                self.json_response({"status": "busy", "message": "worker already running"}, status=409)
                return
        datacenter = os.getenv("DATACENTER", payload.get("datacenter", "dc-belgium"))
        votes = int(payload.get("votes", 1000))
        duration = int(payload.get("duration", 60))
        batch_size = int(payload.get("batch_size", 80))
        central = payload.get("central_url", os.getenv("CENTRAL_URL", "http://central-aggregator:8501"))
        song_ids = [int(x) for x in payload.get("song_ids", [])]
        thread = threading.Thread(target=run_worker, args=(datacenter, votes, duration, central, batch_size, song_ids), daemon=True)
        thread.start()
        self.json_response({"status": "started", "datacenter": datacenter, "votes": votes, "duration": duration})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[worker-web] {self.address_string()} - {fmt % args}")


def serve_worker() -> None:
    dc = os.getenv("DATACENTER", "dc-belgium")
    with run_lock:
        run_state["datacenter"] = dc
    print(f"Datacenter worker API ready: {dc} on {WORKER_HOST}:{WORKER_PORT}")
    server = ThreadingHTTPServer((WORKER_HOST, WORKER_PORT), WorkerHandler)
    server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one Docker datacenter worker")
    parser.add_argument("--serve", action="store_true", help="Start the worker as an HTTP service controlled by the dashboard")
    parser.add_argument("--datacenter", default=os.getenv("DATACENTER", "dc-belgium"), choices=list(DATACENTERS.keys()))
    parser.add_argument("--votes", type=int, default=int(os.getenv("VOTES", "4000")))
    parser.add_argument("--duration", type=int, default=int(os.getenv("DURATION", "120")))
    parser.add_argument("--central", default=os.getenv("CENTRAL_URL", "http://localhost:8501"))
    parser.add_argument("--batch-size", type=int, default=int(os.getenv("BATCH_SIZE", "100")))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.serve or os.getenv("WORKER_SERVER", "true").lower() == "true":
        serve_worker()
    else:
        run_worker(args.datacenter, args.votes, args.duration, args.central, args.batch_size)
