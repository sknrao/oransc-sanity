# O-RAN Health Check App

Single-command tool to verify the health of a deployed O-RAN system (SMO + Near-RT RIC).

## Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Edit config.yaml to match your server IPs/ports
nano config.yaml

# 3. Run
python3 ric_health_check.py
```

## What It Checks

| # | Category | Details |
|---|----------|---------|
| 1 | **Message Flow (Kafka)** | Connects to Strimzi Kafka, lists topics, highlights PM/DMAAP topics |
| 2 | **gNB Count** | Queries SDNC RESTCONF (OAM path) AND E2Mgr NodeB states (Near-RT RIC path) |
| 3 | **Policies** | Lists active A1 policies via A1PMS + lists policy types from A1 Mediator |
| 4 | **Metrics (InfluxDB)** | Lists buckets, queries `pm-data` bucket for data in last 1 hour |
| 5 | **Interface Health** | HTTP health check on: A1 Mediator, E2Mgr, AppMgr, RtMgr, A1PMS, InfluxDB, SDNC |

## Default Config (config.yaml)

```yaml
smo:
  host: hpe15.anuket.iol.unh.edu   # SMO server
  a1pms_port: 30094
  influxdb_port: 31814
  sdnr_port: 30267

ric:
  host: hpe16.anuket.iol.unh.edu   # Near-RT RIC server
  a1_mediator_port: 30093
  e2mgr_port: 30850
```

## Example Output

```
════════════════════════════════════════════════════════════
  O-RAN SYSTEM HEALTH CHECK
  SMO  : hpe15.anuket.iol.unh.edu
  RIC  : hpe16.anuket.iol.unh.edu

════════════════════════════════════════════════════════════
  1. Message Flow — Kafka / Strimzi
  Kafka bootstrap reachable           ⚠️  WARN  → port up, no REST admin API

  2. gNB Count — OAM (SDNC) + Near-RT RIC (E2Mgr)
  OAM gNBs connected                   ✅ PASS  → 3 connected / 5 total
  Near-RT RIC E2Mgr NodeB list         ✅ PASS  → 1 gNBs registered

  3. Policies — A1 Mediator + A1PMS
  A1PMS active policies                ✅ PASS  → 0 policies
  A1 Mediator policy types             ⚠️  WARN  → 0 types registered by xApps

  4. Metrics — InfluxDB
  InfluxDB ping                        ✅ PASS  → hpe15:31814
  InfluxDB buckets                     ✅ PASS  → 3 found
  PM data in 'pm-data' (last 1h)       ✅ PASS  → 42 data rows found

  5. Interface Accessibility
  A1 Mediator        (hpe16:30093)     ✅ PASS  → HTTP 200
  E2Mgr              (hpe16:30850)     ✅ PASS  → HTTP 200
  ...

  SUMMARY
  Kafka topics discovered:             8
  gNBs (E2Mgr):                        1
  PM data rows (last 1h):              42
  Interfaces passed:                   7 / 7
```
