import json
from datetime import datetime
from config import SHUTDOWN_REPORT_FILE, DATACENTERS, ensure_directories

def stop_all_systems() -> dict:
    ensure_directories()
    report = {
        "step": "Step 8 After event: Stop all systems",
        "stopped_at": datetime.now().isoformat(timespec="seconds"),
        "actions": [
            "Stop vote generator service",
            "Stop streaming service",
            "Stop map/reduce workers",
            "Keep result files in storage",
            "Destroy cloud VMs with terraform destroy if this is a real deployment",
        ],
        "datacenters": [
            {"name": name, "provider": info["provider"], "status": "stopped"}
            for name, info in DATACENTERS.items()
        ],
    }
    with open(SHUTDOWN_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("Step 8 Stop all systems completed")
    return report

if __name__ == "__main__":
    print(json.dumps(stop_all_systems(), indent=2))
