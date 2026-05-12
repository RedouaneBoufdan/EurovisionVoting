# Eurovision Voting Simulation – Full Pipeline

Project adapted to the requested **PIPELINE**:

1. **Preparation**
2. **Provisioning (VMs): Proxmox + AWS Instance (HashiCorp Terraform)**
3. **Deployment**
4. **Services: Docker + Kubernetes**
5. **Streaming + Storage**
6. **Voting simulation**
7. **Results per datacenter**
8. **Global results**
9. **Announce winners**
10. **After event: stop all systems**

The project remains runnable locally for the demo, but it also contains infrastructure and deployment files to explain how it would run on real VMs.

---

## Quick local demo

```bash
pip install -r requirements.txt
python pipeline.py --votes 100000 --duration 30
streamlit run dashboard.py
```

The command executes the full simulated pipeline and writes all outputs in `results/`.

---

## Step commands

### Step 1 – Preparation
```bash
python pipeline.py --step preparation
```
Checks folders, input data, configuration, and resets old run files.

### Step 2 – Provisioning
For a real deployment, edit variables in:

- `infrastructure/aws_ec2.tf`
- `infrastructure/proxmox_vm.tf`
- `infrastructure/variables.tf`

Then run:

```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

For the classroom demo, the pipeline simulates this step and writes `results/provisioning_plan.json`.

### Step 3 – Deployment
```bash
python pipeline.py --step deployment
```
Creates a deployment manifest with the services that need to be started.

### Step 3A – Services
Docker:
```bash
docker compose up --build
```

Kubernetes:
```bash
kubectl apply -f kubernetes/
```

### Step 3B – Streaming + Storage
```bash
python pipeline.py --step streaming
```
Creates/validates the local stream file and storage folders.

### Step 4 – Voting simulation
```bash
python pipeline.py --step voting --votes 100000 --duration 30
```
Generates realistic votes with spikes and country bias.

### Step 5 – Results per datacenter
```bash
python pipeline.py --step datacenter-results
```
Aggregates votes by datacenter.

### Step 6 – Global results
```bash
python pipeline.py --step global-results
```
Combines all datacenter results into one ranking.

### Step 7 – Announce winners
```bash
python pipeline.py --step announce
```
Writes the winner file.

### Step 8 – Stop all systems
```bash
python pipeline.py --step stop
```
Stops the simulated systems and writes the shutdown report.

---

## Important files

| File | Purpose |
|---|---|
| `pipeline.py` | Main orchestrator for all professor steps |
| `config.py` | Shared configuration: countries, datacenters, paths |
| `vote_generator.py` | Generates voting events |
| `streaming_storage.py` | Simulates streaming + storage |
| `map_datacenter.py` | Calculates results per datacenter |
| `reduce_results.py` | Calculates global ranking |
| `announce_winner.py` | Announces the winner |
| `shutdown_systems.py` | Simulates shutdown after event |
| `dashboard.py` | Streamlit dashboard |
| `Dockerfile` / `docker-compose.yml` | Container deployment |
| `kubernetes/` | Kubernetes deployment/service/volume files |
| `infrastructure/` | Terraform examples for AWS + Proxmox |

---

## Results generated

After running the pipeline, the `results/` folder contains:

- `votes_stream.csv`
- `votes_storage.csv`
- `datacenter_results.csv`
- `global_results.csv`
- `winner.txt`
- `pipeline_metrics.json`
- `provisioning_plan.json`
- `deployment_manifest.json`
- `shutdown_report.json`

---

## Project explanation in simple words

The system simulates a Eurovision voting night. Votes arrive from different countries, are sent to datacenters, are stored, then counted first per datacenter and finally globally. At the end the system announces the winner and shuts down all simulated services.
