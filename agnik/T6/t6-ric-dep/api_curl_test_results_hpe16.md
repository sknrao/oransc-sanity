# Near-RT RIC (Default Images) — API Test Results on hpe16

> **Server**: hpe16.anuket.iol.unh.edu  
> **Date**: 2026-02-19  
> **RIC Deployment**: Default O-RAN SC Images (Nexus Registry)

---

## 1. Image Verification (Default O-RAN SC)

Confirmed that the deployment is using the standard O-RAN SC images, **NOT** the custom CVE-fix images.

| Component | Image Source | Status |
|-----------|--------------|--------|
| **AppMgr** | `nexus3.o-ran-sc.org:10002/o-ran-sc/ric-plt-appmgr:0.5.9` | ✅ Running |
| **E2Mgr** | `nexus3.o-ran-sc.org:10002/o-ran-sc/ric-plt-e2mgr:6.0.7` | ✅ Running |
| **E2Term** | `nexus3.o-ran-sc.org:10002/o-ran-sc/ric-plt-e2:6.0.7` | ✅ Running |
| **SubMgr** | `nexus3.o-ran-sc.org:10002/o-ran-sc/ric-plt-submgr:0.10.3` | ✅ Running |

---

## 2. NodePort Services (Exposed for Testing)

| Service | NodePort | Use Case |
|---------|----------|----------|
| A1 Mediator | **30093** | Policy Management (SMO Interface) |
| E2Mgr | **30850** | NodeB/RAN Management |
| AppMgr | **30851** | xApp Management |
| RtMgr | **30852** | Route Management |
| SubMgr | **30853** | Subscription Management |

---

## 3. API Test Results (Curled Locally on hpe16)

### 3.1 A1 Mediator (Port 30093)
Matches `bruno-api-collection/ric/a1-mediator`

| Endpoint | Result | HTTP |
|----------|--------|------|
| `GET /A1-P/v2/healthcheck` | ✅ PASS | 200 |
| `GET /A1-P/v2/policytypes` | ✅ PASS | 200 |
| **Status**: Empty list `[]` (No xApps with policies deployed yet) | | |

### 3.2 E2 Manager (Port 30850)
Matches `bruno-api-collection/ric/e2-manager`

| Endpoint | Result | HTTP |
|----------|--------|------|
| `GET /v1/health` | ✅ PASS | 200 |
| `GET /v1/nodeb/states` | ✅ PASS | 200 |

### 3.3 App Manager (Port 30851)
Matches `bruno-api-collection/ric/app-manager`

| Endpoint | Result | HTTP |
|----------|--------|------|
| `GET /ric/v1/health/alive` | ✅ PASS | 200 |
| `GET /ric/v1/health/ready` | ✅ PASS | 200 |
| `GET /ric/v1/xapps` | ✅ PASS | 200 |
| `GET /ric/v1/config` | ✅ PASS | 200 |

### 3.4 Routing Manager (Port 30852)

| Endpoint | Result | HTTP |
|----------|--------|------|
| `GET /ric/v1/health/alive` | ✅ PASS | 200 |
| `GET /ric/v1/getdebuginfo` | ✅ PASS | 200 |

### 3.5 A1PMS / SMO Connectivity (from hpe16 to hpe15)

| Endpoint | Result | HTTP |
|----------|--------|------|
| `GET http://hpe15...:30094/a1-policy/v2/status` | ✅ PASS | 200 |

---

## 4. Test Summary

All core RIC Platform components are running, exposed, and responding correctly to API health checks. The A1 Mediator is reachable and ready for policy operations. The connection to the SMO (hpe15) is verified.
