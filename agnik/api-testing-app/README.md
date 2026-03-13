# O-RAN Health Check App (Golang)

Single-command tool to verify the health of a deployed O-RAN system (SMO + Near-RT RIC).

## Quick Start

### 1. Configure
Edit `config.yaml` to match your cluster's settings. The current file is pre-configured for the `hpe15`/`hpe16` environment.

### 2. Run
The tool is written in Golang. 

```bash
# If you have Go installed:
go run main.go

# Or run the pre-compiled binary:
chmod +x api-tester
./api-tester
```

## What It Checks

| Category | Description |
|----------|-------------|
| **Kafka Flow** | Connects to Redpanda Console API to verify topic generation. |
| **gNB Count** | Cross-references SDNC (OAM) and E2Mgr (RIC) gNB registration. |
| **A1 Policies** | Checks A1PMS for active policies and A1 Mediator for policy types. |
| **Metrics** | Queries InfluxDB `pm-bucket` for recent PM data entries. |
| **Interfaces** | Verifies 7 core O-RAN interfaces (A1, E2, O1, etc.) are responsive. |

## Important Configuration
- **SMO Host**: `hpe15.anuket.iol.unh.edu`
- **RIC Host**: `hpe16.anuket.iol.unh.edu`
- **InfluxDB Port**: `32717` (NodePort)
- **Kafka Admin**: `30385` (Redpanda Console NodePort)

## Sample Output

```text
============================================================
  O-RAN SYSTEM HEALTH CHECK (Golang)
============================================================
  SMO  : hpe15.anuket.iol.unh.edu
  RIC  : hpe16.anuket.iol.unh.edu
  Time : 2026-03-12 18:33:07
============================================================

════════════════════════════════════════════════════════════
  1. Message Flow — Kafka / Strimzi
════════════════════════════════════════════════════════════
  Kafka topics discovered                       ✅ PASS  → Total: 30

════════════════════════════════════════════════════════════
  2. gNB Count — OAM (SDNC) + Near-RT RIC (E2Mgr)
════════════════════════════════════════════════════════════
  OAM gNBs connected (SDNC)                     ✅ PASS  → 4 connected / 4 total
  Near-RT RIC E2Mgr NodeB list                  ✅ PASS  → 1 gNBs registered

════════════════════════════════════════════════════════════
  3. Policies — A1 Mediator + A1PMS
════════════════════════════════════════════════════════════
  A1PMS active policies                         ✅ PASS  → 0 policies
  A1 Mediator policy types                      ✅ PASS  → 1 types registered by xApps

════════════════════════════════════════════════════════════
  4. Metrics — InfluxDB
════════════════════════════════════════════════════════════
  InfluxDB ping                                 ✅ PASS  → hpe15.anuket.iol.unh.edu:32717
  InfluxDB buckets                              ✅ PASS  → 4 found
  PM data in 'pm-bucket'                        ✅ PASS  → 4 data rows found

════════════════════════════════════════════════════════════
  5. Interface Accessibility — Health Endpoints
════════════════════════════════════════════════════════════
  A1 Mediator                                   ✅ PASS  → HTTP 200
  E2Mgr                                         ✅ PASS  → HTTP 200
  AppMgr                                        ✅ PASS  → HTTP 200
  RtMgr                                         ✅ PASS  → HTTP 200
  A1PMS                                         ✅ PASS  → HTTP 200
  InfluxDB                                      ✅ PASS  → HTTP 204
  SDNC RESTCONF                                 ✅ PASS  → HTTP 200

============================================================
  SUMMARY
============================================================
  Kafka topics:                                 30
  gNBs (E2Mgr):                                 1
  gNBs (OAM/SDNC):                              4
  Active A1 Policies:                           0
  Interfaces passed:                            7 / 7
```
