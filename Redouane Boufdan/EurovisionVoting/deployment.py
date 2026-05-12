import json
from datetime import datetime
from config import DATACENTERS, DEPLOYMENT_MANIFEST_FILE, ensure_directories

def run_deployment() -> dict:
    ensure_directories()
    manifest = {
        "step": "Step 3 Deployment",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "strategy": "Deploy the same Docker image on each VM/datacenter. Kubernetes can scale dashboard and workers.",
        "docker": {
            "build": "docker compose build",
            "run": "docker compose up",
        },
        "kubernetes": {
            "apply": "kubectl apply -f kubernetes/",
            "objects": ["Deployment", "Service", "PersistentVolumeClaim"],
        },
        "targets": [
            {"datacenter": name, "provider": info["provider"], "region": info["region"]}
            for name, info in DATACENTERS.items()
        ],
    }
    with open(DEPLOYMENT_MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest

if __name__ == "__main__":
    print(json.dumps(run_deployment(), indent=2))
