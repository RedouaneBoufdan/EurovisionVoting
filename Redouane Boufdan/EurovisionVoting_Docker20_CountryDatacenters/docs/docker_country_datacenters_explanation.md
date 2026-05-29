# Eurovision Voting - Docker Country Datacenter Demo

This version is fully Docker-based and simulates a distributed Eurovision voting system with **one Docker datacenter per country**.

## Architecture

- `central-aggregator`: central web/API server on `localhost:8501`
- 20 country datacenter workers, for example:
  - `dc-belgium`
  - `dc-france`
  - `dc-germany`
  - `dc-italy`
  - `dc-spain`
  - `dc-netherlands`
  - `dc-sweden`
  - `dc-ukraine`
  - ... up to 20

The browser only opens one URL:

```text
http://localhost:8501
```

Do **not** open `central-aggregator:8501` in the browser. That is an internal Docker service name used between containers.

## Start the project

From the project folder:

```powershell
docker compose down --remove-orphans
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

## Run a live test

In the website, open **Start test**.

You can choose:

- total number of votes;
- duration in seconds;
- datacenters to operate;
- participating Eurovision countries/songs.

Minimum rule: select at least 2 participating countries/songs.

For a smooth classroom demo, use **3 to 5 datacenters**. If the teacher asks, you can select all 20 datacenters to prove the full country-per-datacenter setup.

## Useful Docker commands

```powershell
docker compose ps
docker compose logs -f central-aggregator
docker compose logs -f dc-belgium
docker compose logs -f dc-france
docker compose logs -f dc-germany
docker compose logs -f dc-italy
docker compose down
```

## CSV proof

Open the **Raw CSV votes** page to see raw incoming events.

You can also download the CSV here:

```text
http://localhost:8501/api/votes.csv
```

## Explanation for the teacher

We changed the project into a Docker-based distributed architecture. The system has one central aggregator container and up to 20 country datacenter containers. Each country datacenter can run as its own Docker service. During the demo, I can choose only a few datacenters to keep the laptop stable, but the Docker architecture is ready for all 20. Each datacenter generates local vote events and sends them in batches to the central aggregator. The central aggregator stores all incoming votes in CSV, calculates the results per datacenter, and builds the global Eurovision ranking. The dashboard is one web interface and updates charts through API calls, so the whole page does not reload.
