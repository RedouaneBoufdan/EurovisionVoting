import json
from datetime import datetime
from config import DATACENTERS, PROVISIONING_PLAN_FILE, ensure_directories

def run_provisioning() -> dict:
    ensure_directories()
    vm_plan = []
    for dc_name, dc in DATACENTERS.items():
        vm_plan.append({
            "datacenter": dc_name,
            "provider": dc["provider"],
            "region": dc["region"],
            "vm_name": f"eurovision-{dc_name}",
            "cpu": 2,
            "memory_mb": 4096,
            "disk_gb": 30,
            "services": ["vote-generator", "streaming-storage", "map-reducer"],
        })

    plan = {
        "step": "Step 2 Provisioning VMs: Proxmox + AWS Instance with HashiCorp Terraform",
        "mode": "simulation for local classroom run",
        "terraform_files": [
            "infrastructure/aws_ec2.tf",
            "infrastructure/proxmox_vm.tf",
            "infrastructure/variables.tf",
        ],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "vms": vm_plan,
    }

    with open(PROVISIONING_PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    return plan

if __name__ == "__main__":
    print(json.dumps(run_provisioning(), indent=2))
