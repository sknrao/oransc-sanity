# Simple Energy Saving rApp

A simple rApp that reads PM data from Kafka, applies a threshold decision, and controls cell power via SDNR RESTCONF.

```
Kafka (PM data) → Threshold (PRB < 20%?) → SDNR RESTCONF (LOCK/UNLOCK cell)
```

## How It Works

| Phase | What | How |
|-------|------|-----|
| **Data** | Read processed PM JSON from Kafka message bus | `confluent_kafka` consumer reading from `pmreports` |
| **Decision** | If PRB usage < 20% → cell is idle | Simple threshold evaluating `RRU.PrbUsedUl` metric |
| **Action** | Power off/on the cell via O1 interface | PATCH `NRCellDU/attributes/administrativeState` via SDNR |

## Files

| File | Purpose |
|------|---------|
| `simple_rapp.py` | The rApp code (~170 lines Python) |
| `Dockerfile` | Container image |
| `rapp-job.yaml` | Kubernetes Job spec to deploy in `smo` namespace |

## Deploy

```bash
# 1. Create ConfigMap from the script
kubectl create configmap simple-rapp-code -n smo --from-file=simple_rapp.py --dry-run=client -o yaml | kubectl apply -f -

# 2. Deploy as a Job
kubectl delete job simple-es-rapp -n smo --ignore-not-found
kubectl apply -f rapp-job.yaml

# 3. Check logs
kubectl logs -n smo job/simple-es-rapp --tail=100
```

## Configuration (via environment variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP` | `onap-strimzi-kafka-bootstrap.onap:9092` | Kafka server |
| `KAFKA_TOPIC` | `pmreports` | Processed JSON PM data topic |
| `KAFKA_USER` | `strimzi-kafka-admin` | SASL username |
| `KAFKA_PASS` | *(from k8s secret)* | SASL password |
| `SDNR_URL` | `http://sdnc.onap:8282` | SDNR RESTCONF endpoint |
| `NODE` | `SOMETHING` | Netconf node ID |
| `ME` | `ManagedElement-002` | ManagedElement ID |
| `GNB` | `GNBDUFunction-001` | GNBDUFunction ID |
| `PRB_THRESHOLD` | `20.0` | PRB % below which cell is considered idle |

## Test Output (from live O-RAN cluster)

```text
--- PHASE 1: DATA (Kafka) ---
[INFO] Kafka consumer created, topic: pmreports
[INFO] [DATA] Message #1 | partition=5 offset=0
[INFO] [DATA] Total: 1 messages in 1.1s

--- PHASE 2: DECISION (Threshold) ---
[INFO] [DECISION] S10-B9-C1: PRB=0.1% -> LOCKED
[INFO] [DECISION] S10-B9-C1: PRB=79.2% -> UNLOCKED

--- PHASE 3: ACTION (SDNR) ---
[INFO]   S10-B9-C1: current=?, target=LOCKED
[INFO] [ACTION] Cell S10-B9-C1 -> LOCKED: HTTP 500
[INFO]   Verified: S10-B9-C1 = ?
```
