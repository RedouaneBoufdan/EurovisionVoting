import argparse
import json
import time
from datetime import datetime

from preparation import run_preparation
from provisioning import run_provisioning
from deployment import run_deployment
from streaming_storage import initialise_streaming_storage
from vote_generator import generate_votes
from map_datacenter import run_map
from reduce_results import run_reduce
from announce_winner import announce_winner
from shutdown_systems import stop_all_systems
from config import PIPELINE_METRICS_FILE, ensure_directories

VALID_STEPS = {
    "preparation", "provisioning", "deployment", "streaming", "voting",
    "datacenter-results", "global-results", "announce", "stop", "all"
}

def run_pipeline(total_votes: int, duration: int, realtime: bool = False, step: str = "all") -> None:
    if step not in VALID_STEPS:
        raise ValueError(f"Unknown step: {step}")

    ensure_directories()
    start = time.time()
    executed = []

    def mark(name: str):
        executed.append({"step": name, "completed_at": datetime.now().isoformat(timespec="seconds")})

    if step in {"preparation", "all"}:
        run_preparation(reset=True)
        mark("Step 1 Preparation")
        if step != "all": return

    if step in {"provisioning", "all"}:
        run_provisioning()
        mark("Step 2 Provisioning")
        if step != "all": return

    if step in {"deployment", "all"}:
        run_deployment()
        mark("Step 3 Deployment")
        if step != "all": return

    if step in {"streaming", "all"}:
        initialise_streaming_storage()
        mark("Step 3B Streaming and Storage")
        if step != "all": return

    generated = None
    if step in {"voting", "all"}:
        generated = generate_votes(total_votes, duration, realtime=realtime)
        mark("Step 4 Voting Simulation")
        if step != "all": return

    if step in {"datacenter-results", "all"}:
        run_map()
        mark("Step 5 Results per datacenter")
        if step != "all": return

    if step in {"global-results", "all"}:
        run_reduce()
        mark("Step 6 Global Results")
        if step != "all": return

    if step in {"announce", "all"}:
        winner = announce_winner()
        mark("Step 7 Announce winners")
        if step != "all": return

    if step in {"stop", "all"}:
        stop_all_systems()
        mark("Step 8 Stop all systems")
        if step != "all": return

    metrics = {
        "requested_votes": total_votes,
        "generated_votes": generated,
        "duration_seconds": duration,
        "total_pipeline_time_seconds": round(time.time() - start, 4),
        "steps_executed": executed,
    }
    with open(PIPELINE_METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eurovision voting full pipeline")
    parser.add_argument("--votes", type=int, default=10000)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--step", choices=sorted(VALID_STEPS), default="all")
    parser.add_argument("--realtime", action="store_true", help="Sleep one second between generation batches")
    args = parser.parse_args()
    run_pipeline(args.votes, args.duration, realtime=args.realtime, step=args.step)
