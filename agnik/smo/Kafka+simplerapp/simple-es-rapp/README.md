# Simple Energy Saving rApp

A simple rApp that reads PM data from Kafka, applies a threshold decision, and controls cell power via SDNR RESTCONF.

```
Kafka (PM data) → Threshold (PRB < 20%?) → SDNR RESTCONF (LOCK/UNLOCK cell)
```

## How It Works

| Phase | What | How |
|-------|------|-----|
| **Data** | Read PM counters from Kafka message bus | `confluent_kafka` consumer, SASL/SCRAM-SHA-512 auth |
| **Decision** | If PRB usage < 20% → cell is idle | Simple threshold (no ML) |
| **Action** | Power off/on the cell via O1 interface | PATCH `NRCellDU/attributes/administrativeState` via SDNR |

## Files

| File | Purpose |
|------|---------|
| `simple_rapp.py` | The rApp code (~170 lines Python) |
| `Dockerfile` | Container image (python:3.11-slim + confluent-kafka + requests) |
| `rapp-job.yaml` | Kubernetes Job spec to deploy in `smo` namespace |

## Deploy

```bash
# 1. Create ConfigMap from the script
kubectl create configmap simple-rapp-code -n smo --from-file=simple_rapp.py

# 2. Deploy as a Job
kubectl apply -f rapp-job.yaml

# 3. Check logs
kubectl logs -n smo job/simple-es-rapp
```

## Configuration (via environment variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP` | `onap-strimzi-kafka-bootstrap.onap:9092` | Kafka server |
| `KAFKA_TOPIC` | `unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT` | PM data topic |
| `KAFKA_USER` | `strimzi-kafka-admin` | SASL username |
| `KAFKA_PASS` | *(from k8s secret)* | SASL password |
| `SDNR_URL` | `http://sdnc.onap:8282` | SDNR RESTCONF endpoint |
| `NODE` | `SOMETHING` | Netconf node ID |
| `ME` | `ManagedElement-002` | ManagedElement ID |
| `GNB` | `GNBDUFunction-001` | GNBDUFunction ID |
| `PRB_THRESHOLD` | `20.0` | PRB % below which cell is considered idle |

## Test Output (from k8s pod)

```
--- PHASE 1: DATA (Kafka) ---
[INFO] Kafka consumer created, topic: unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT
[INFO] [DATA] Message #1 | partition=1 offset=798
[INFO] [DATA] Message #2 | partition=1 offset=799
[INFO] [DATA] Message #3 | partition=0 offset=802
[INFO] [DATA] Total: 3 messages in 3.2s

--- PHASE 2: DECISION (Threshold) ---
[INFO] [DECISION] S1-B12-C1: PRB=8.3% -> LOCKED

--- PHASE 3: ACTION (SDNR) ---
[INFO]   S1-B12-C1: current=UNLOCKED, target=LOCKED
[INFO] [ACTION] Cell S1-B12-C1 -> LOCKED: HTTP 200
[INFO]   Verified: S1-B12-C1 = LOCKED
```
