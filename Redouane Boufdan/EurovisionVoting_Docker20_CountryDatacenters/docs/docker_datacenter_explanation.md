# Docker Datacenter Explanation

The project now runs as a distributed Docker demo.

## Services

- `central-aggregator`: receives vote batches, stores raw CSV data and calculates results.
- `dc-belgium`: Belgian datacenter worker.
- `dc-france`: French datacenter worker.
- `dc-germany`: German datacenter worker.

## Network

The user opens:

```text
http://localhost:8501
```

Inside Docker, containers talk to each other with service names:

```text
central-aggregator:8501
dc-belgium:9000
dc-france:9000
dc-germany:9000
```

## Test flow

1. The user chooses total votes, duration and participating songs in the web dashboard.
2. The central aggregator resets the CSV files.
3. The central aggregator starts the selected datacenter workers.
4. Each worker sends vote batches gradually.
5. The central aggregator updates stats, rankings and raw CSV views.

This proves the idea of multiple datacenters without needing three physical laptops for every test.
