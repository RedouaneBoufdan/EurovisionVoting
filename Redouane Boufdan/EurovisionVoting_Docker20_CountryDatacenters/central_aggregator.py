from __future__ import annotations

import csv
import json
import os
import threading
from collections import Counter, deque
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from config import (
    DATACENTERS,
    DISTRIBUTED_DATACENTER_FILE,
    DISTRIBUTED_GLOBAL_FILE,
    DISTRIBUTED_STATUS_FILE,
    DISTRIBUTED_VOTES_FILE,
    RESULTS_DIR,
    SONGS_FILE,
    STATIC_DIR,
    ensure_directories,
)

HOST = os.getenv("CENTRAL_HOST", "0.0.0.0")
PORT = int(os.getenv("CENTRAL_PORT", "8501"))
WORKER_PORT = int(os.getenv("WORKER_PORT", "9000"))

FIELDNAMES = ["event_id", "phone_number", "from_country_code", "datacenter", "song_id", "timestamp"]

worker_urls = {name: f"http://{name}:{WORKER_PORT}" for name in DATACENTERS}

lock = threading.Lock()
songs_by_id: dict[int, dict] = {}
raw_votes: list[dict] = []
recent_events: deque[dict] = deque(maxlen=30)
datacenter_totals: Counter[str] = Counter()
song_totals: Counter[int] = Counter()
datacenter_song_totals: dict[str, Counter[int]] = {}
worker_totals: Counter[str] = Counter()
started_at = datetime.now().isoformat(timespec="seconds")


def load_songs() -> None:
    global songs_by_id
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        songs_by_id = {
            int(row["song_id"]): {
                "song_id": int(row["song_id"]),
                "country": row["country"],
                "flag": row.get("flag", ""),
            }
            for row in reader
        }


def reset_storage_locked() -> None:
    global raw_votes, recent_events, datacenter_totals, song_totals, datacenter_song_totals, worker_totals, started_at
    ensure_directories()
    raw_votes = []
    recent_events = deque(maxlen=30)
    datacenter_totals = Counter()
    song_totals = Counter()
    datacenter_song_totals = {name: Counter() for name in DATACENTERS}
    worker_totals = Counter()
    started_at = datetime.now().isoformat(timespec="seconds")

    with open(DISTRIBUTED_VOTES_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(FIELDNAMES)
    write_result_files_locked()


def append_votes_locked(events: list[dict], worker_name: str) -> int:
    cleaned: list[dict] = []
    for event in events:
        try:
            row = {
                "event_id": str(event["event_id"]),
                "phone_number": str(event["phone_number"]),
                "from_country_code": str(event["from_country_code"]),
                "datacenter": str(event["datacenter"]),
                "song_id": int(event["song_id"]),
                "timestamp": str(event["timestamp"]),
            }
        except (KeyError, TypeError, ValueError):
            continue
        cleaned.append(row)

    if not cleaned:
        return 0

    with open(DISTRIBUTED_VOTES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerows(cleaned)

    raw_votes.extend(cleaned)
    for row in cleaned:
        dc = row["datacenter"]
        song_id = int(row["song_id"])
        datacenter_totals[dc] += 1
        song_totals[song_id] += 1
        datacenter_song_totals.setdefault(dc, Counter())[song_id] += 1
        worker_totals[worker_name or dc] += 1
        song = songs_by_id.get(song_id, {})
        recent_events.appendleft(
            {
                "event_id": row["event_id"],
                "from_country_code": row["from_country_code"],
                "datacenter": dc,
                "song_id": song_id,
                "song_country": song.get("country", "Unknown"),
                "flag": song.get("flag", ""),
                "timestamp": row["timestamp"],
            }
        )

    write_result_files_locked()
    return len(cleaned)


def global_rows_locked() -> list[dict]:
    rows = []
    for rank, (song_id, total) in enumerate(song_totals.most_common(), start=1):
        song = songs_by_id.get(int(song_id), {})
        rows.append(
            {
                "rank": rank,
                "song_id": int(song_id),
                "country": song.get("country", "Unknown"),
                "flag": song.get("flag", ""),
                "total_votes": int(total),
            }
        )
    return rows


def datacenter_rows_locked() -> list[dict]:
    rows = []
    for name, info in DATACENTERS.items():
        top_song_id = None
        top_votes = 0
        if datacenter_song_totals.get(name):
            top_song_id, top_votes = datacenter_song_totals[name].most_common(1)[0]
        top_song = songs_by_id.get(int(top_song_id), {}) if top_song_id else {}
        rows.append(
            {
                "datacenter": name,
                "display_name": info.get("display_name", name),
                "country": info.get("country", ""),
                "country_code": info.get("country_code", ""),
                "provider": info.get("provider", ""),
                "region": info.get("region", ""),
                "container": info.get("container", ""),
                "description": info.get("description", ""),
                "votes": int(datacenter_totals.get(name, 0)),
                "top_country": top_song.get("country", "-"),
                "top_flag": top_song.get("flag", ""),
                "top_votes": int(top_votes),
            }
        )
    return rows


def status_locked() -> dict:
    global_rows = global_rows_locked()
    dc_rows = datacenter_rows_locked()
    return {
        "service": "central-aggregator-web",
        "started_at": started_at,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "total_votes": int(sum(datacenter_totals.values())),
        "active_datacenters": sum(1 for row in dc_rows if row["votes"] > 0),
        "datacenters": dc_rows,
        "workers": [{"worker": k, "votes": int(v)} for k, v in worker_totals.most_common()],
        "global_results": global_rows,
        "winner": global_rows[0] if global_rows else None,
        "recent_events": list(recent_events),
        "available_songs": list(songs_by_id.values()),
        "raw_votes_preview": list(reversed(raw_votes[-25:])),
        "test_control": {
            "worker_urls": worker_urls,
            "minimum_selected_songs": 2,
            "note": "Choose votes, duration and at least 2 Eurovision countries/songs. Central resets storage and starts each selected Docker datacenter worker.",
        },
        "docker": {
            "entry_url": "http://localhost:8501",
            "api_stats": "/api/stats",
            "compose_file": "docker-compose.yml",
            "network_note": "The browser uses localhost:8501. Docker services communicate internally with http://central-aggregator:8501 and the selected dc-* services on port 9000. central-aggregator is internal Docker DNS; do not open it directly in the browser.",
        },
    }


def write_result_files_locked() -> None:
    global_rows = global_rows_locked()
    dc_rows = datacenter_rows_locked()

    with open(DISTRIBUTED_GLOBAL_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "song_id", "country", "flag", "total_votes"])
        writer.writeheader()
        writer.writerows(global_rows)

    with open(DISTRIBUTED_DATACENTER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "datacenter", "display_name", "country", "country_code", "provider", "region",
                "container", "description", "votes", "top_country", "top_flag", "top_votes",
            ],
        )
        writer.writeheader()
        writer.writerows(dc_rows)

    DISTRIBUTED_STATUS_FILE.write_text(json.dumps(status_locked(), indent=2), encoding="utf-8")


def json_response(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def post_json(url: str, payload: dict, timeout: int = 5) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
}


class AggregatorWebHandler(BaseHTTPRequestHandler):
    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body.decode("utf-8"))

    def send_static(self, path: str) -> None:
        if path in {"/", ""}:
            path = "/index.html"
        target = (STATIC_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists() or not target.is_file():
            self.send_error(404, "File not found")
            return
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/health":
            json_response(self, {"status": "ok", "service": "central-aggregator-web"})
            return
        if path == "/api/stats":
            with lock:
                json_response(self, status_locked())
            return
        if path == "/api/config":
            json_response(self, {"datacenters": DATACENTERS})
            return
        if path == "/api/raw-votes":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["200"])[0])
            with lock:
                rows = list(reversed(raw_votes[-limit:]))
            json_response(self, {"rows": rows, "count": len(rows), "total": len(raw_votes)})
            return
        if path == "/api/votes.csv":
            data = DISTRIBUTED_VOTES_FILE.read_bytes() if DISTRIBUTED_VOTES_FILE.exists() else b""
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=distributed_votes.csv")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/results.csv":
            data = DISTRIBUTED_GLOBAL_FILE.read_bytes() if DISTRIBUTED_GLOBAL_FILE.exists() else b""
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_static(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/start-test":
            try:
                payload = self.read_json()
                total_votes = max(1, int(payload.get("total_votes", 12000)))
                duration = max(5, int(payload.get("duration", 120)))
                selected_datacenters = payload.get("datacenters") or list(DATACENTERS.keys())
                selected_datacenters = [dc for dc in selected_datacenters if dc in DATACENTERS]
                song_ids = [int(x) for x in payload.get("song_ids", [])]
                if len(song_ids) < 2:
                    raise ValueError("Select at least 2 participating countries/songs before starting a test.")
                if not selected_datacenters:
                    raise ValueError("Select at least 1 datacenter.")

                with lock:
                    reset_storage_locked()

                base = total_votes // len(selected_datacenters)
                remainder = total_votes % len(selected_datacenters)
                started = []
                errors = []
                for index, dc in enumerate(selected_datacenters):
                    votes = base + (1 if index < remainder else 0)
                    try:
                        response = post_json(
                            worker_urls[dc].rstrip("/") + "/start",
                            {
                                "datacenter": dc,
                                "votes": votes,
                                "duration": duration,
                                "batch_size": max(20, min(200, votes // max(1, duration) + 20)),
                                "central_url": f"http://central-aggregator:{PORT}",
                                "song_ids": song_ids,
                            },
                        )
                        started.append({"datacenter": dc, "votes": votes, "response": response})
                    except Exception as exc:
                        errors.append({"datacenter": dc, "error": str(exc)})

                status = status_locked()
                json_response(self, {"status": "started", "started": started, "errors": errors, "stats": status}, status=200 if started else 500)
            except Exception as exc:
                json_response(self, {"status": "error", "message": str(exc)}, status=400)
            return
        if path == "/api/reset":
            with lock:
                reset_storage_locked()
                payload = status_locked()
            json_response(self, payload)
            return
        if path == "/api/votes":
            try:
                payload = self.read_json()
                worker = str(payload.get("worker", "unknown-worker"))
                events = payload.get("events", [])
                if not isinstance(events, list):
                    raise ValueError("events must be a list")
                with lock:
                    accepted = append_votes_locked(events, worker)
                    stats = status_locked()
                json_response(self, {"status": "accepted", "accepted": accepted, "total_votes": stats["total_votes"]})
            except Exception as exc:
                json_response(self, {"status": "error", "message": str(exc)}, status=400)
            return
        json_response(self, {"error": "not found"}, status=404)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[central-web] {self.address_string()} - {fmt % args}")


def main() -> None:
    ensure_directories()
    load_songs()
    with lock:
        reset_storage_locked()
    server = ThreadingHTTPServer((HOST, PORT), AggregatorWebHandler)
    print(f"Central aggregator + web dashboard running on http://{HOST}:{PORT}")
    print("Open http://localhost:8501 on Windows. Datacenters send votes to /api/votes.")
    server.serve_forever()


if __name__ == "__main__":
    main()
