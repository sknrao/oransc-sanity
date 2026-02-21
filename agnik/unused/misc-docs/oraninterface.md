# O-RAN Interface Audit Report

---

## Summary

| Server | Interfaces Tested | Working | Requires Auth | Issues |
|--------|-------------------|---------|---------------|--------|
| **HPE15** | 12 | 11 | 4 | 1 (Topology 404) |
| **HPE16** | 4 | 4 | 0 | 0 |

---

## HPE15 (SMO) Interfaces

### 1. ✅ SDNC Web UI
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:30205 |
| **Port** | 30205 |
| **Username** | `admin` |
| **Password** | `Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U` |
| **Status** | ✅ **Working** |

**Observations**:
- Successfully logged in
- Connected network functions visible:
  - `o-du` (10.200.105.252:31654) - Connected
  - `o-du-pynts-1122` (10.244.72.210:830) - Connected
  - `o-du-pynts-1123` (10.244.72.209:830) - Connected

---

### 2. ✅ SDNC API (RESTCONF)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:30267 |
| **Port** | 30267 |
| **Username** | `admin` |
| **Password** | `Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U` |
| **Status** | ✅ **Working** (requires Basic Auth) |

**Observations**:
- Requires Basic Auth header for all requests
- **Tested RESTCONF Endpoints**:
  - `GET /rests/data/network-topology:network-topology` → ✅ 200 — Returns 3 connected NETCONF nodes
  - `GET /rests/data/network-topology:network-topology/topology=topology-netconf/node=o-du-pynts-1122` → ✅ 200 — Node details (host: 10.244.72.210, port: 830)
  - `GET /rests/data/ietf-yang-library:modules-state` → ✅ 200 — 128 YANG modules loaded
  - `PUT .../node=<id>` — Mount NETCONF device (template ready)
  - `DELETE .../node=<id>` — Unmount NETCONF device (template ready)

---

### 3. ✅ A1PMS (Policy Management Service)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:30094 |
| **Port** | 30094 |
| **Auth** | None |
| **Status** | ✅ **Working** (full CRUD tested) |

**Observations**:
- Root path returns "Whitelabel Error Page" (Spring Boot default — expected)
- **Tested API Endpoints**:
  - `GET /a1-policy/v2/rics` → ✅ `hpe16-ric` is **AVAILABLE**
  - `GET /a1-policy/v2/rics/ric?ric_id=hpe16-ric` → ✅ RIC details (baseUrl: http://10.200.105.60:30803)
  - `GET /a1-policy/v2/policy-types` → ✅ Empty (no xApps deployed yet)
  - `GET /a1-policy/v2/policies` → ✅ Empty
  - `GET /a1-policy/v2/services` → ✅ `test-service` registered
  - `GET /a1-policy/v2/status` → ✅ `"success"`
  - `GET /a1-policy/v2/configuration` → ✅ Shows RIC config with StdA1ClientVersion2 adapter
  - `PUT /a1-policy/v2/services` → ✅ 201 — Service registration works
  - `DELETE /a1-policy/v2/services/{id}` → ✅ 204 — Service deletion works
  - `PUT /a1-policy/v2/services/{id}/keepalive` → ✅ 200 — Heartbeat works
  - `PUT /a1-policy/v2/policies` → ⚠️ 423 — No policy types yet (needs xApp)

---

### 4. ✅ Keycloak (IAM)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:30202 |
| **Port** | 30202 |
| **Username** | `admin` |
| **Password** | `admin` |
| **Status** | ✅ **Working** |

**Observations**:
- Full admin access to Keycloak console
- **2 Realms**: `master`, `nonrtric-realm`
- **13 Configured Clients in nonrtric-realm**:
  - `account`, `account-console` - User account management
  - `admin-cli`, `broker` - Admin tools
  - `console-setup` - Console configuration
  - `dfc` - Data File Collector (secret: `yI163T9pM3U1jtI2WqQKyN9pFaRZryFW`)
  - `kafka-producer-pm-json2influx`, `kafka-producer-pm-json2kafka`, `kafka-producer-pm-xml2json` - PM data pipeline
  - `nrt-pm-log` - Near-RT PM logging (secret: `u8AEJGDA6uSVGW1NpP4UFKhcd1MMtNlZ`)
  - `pm-producer-json2kafka` (secret: `5VKEaVU19XaqfuIDkDMD134wyYgKCvVp`)
  - `realm-management`, `security-admin-console`
- **Admin API Auth**: Use bearer token from master realm (not basic auth)
  ```
  TOKEN=$(curl -s -X POST -d 'grant_type=password&client_id=admin-cli&username=admin&password=admin' \
    http://hpe15.anuket.iol.unh.edu:30202/realms/master/protocol/openid-connect/token | jq -r '.access_token')
  curl -H "Authorization: Bearer $TOKEN" http://hpe15.anuket.iol.unh.edu:30202/admin/realms
  ```

---

### 5. ✅ MinIO (Object Storage)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:32208 |
| **Port** | 32208 |
| **Username** | `admin` |
| **Password** | `adminadmin` |
| **Status** | ✅ **Working** |

**Observations**:
- Successfully logged in to Object Browser
- Existing bucket: `ropfiles` (Created Feb 06, 2026, PRIVATE access)
- Bucket currently empty

---

### 6. ❌ Topology Service
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:32001 |
| **Port** | 32001 |
| **Status** | ❌ **404 Not Found** |

**Observations**:
- Service returns HTTP 404 on root path
- May require specific API path or may not be fully configured

---

### 7. ✅ Service Manager
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:31575 |
| **Port** | 31575 |
| **Auth** | None |
| **Status** | ✅ **Working** |

**Observations**:
- Returns: `Hello World, from Service Manager!`
- Basic health check confirms service is running

---

### 8. ✅ Redpanda Console (Kafka Dashboard)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:31504/overview |
| **Port** | 31504 |
| **Auth** | None |
| **Status** | ✅ **Working** |

**Observations**:
- Cluster Status: **Running**
- Cluster Version: v3.9
- Brokers Online: 1 of 1
- Storage: 200 MiB (Primary: 200 MiB, Replicated: 0 B)
- Security: 62 ACLs configured
- **28 Topics** (120 partitions, 120 replicas total):
  - **Policy & ACM**: 
    - `acm-ppnt-sync` (2 partitions, 497 KiB)
    - `policy-acruntime-participant` (2 partitions, 5.21 MiB)
    - `policy-pdp-pap` (10 partitions, 808 KiB)
    - `policy-heartbeat`, `policy-notification` (10 partitions each)
  - **PM Data Pipeline**:
    - `collected-file` (10 partitions)
    - `json-file-ready-kp`, `json-file-ready-kpadp` (10 partitions each)
    - `pmreports` (10 partitions)
  - **Topology & Inventory**:
    - `topology-inventory-ingestion` (2 partitions, 2.49 MiB)
  - **VES Events** (all 2 partitions):
    - `unauthenticated.VES_MEASUREMENT_OUTPUT`
    - `unauthenticated.VES_NOTIFICATION_OUTPUT`
    - `unauthenticated.VES_PNFREG_OUTPUT`
    - `unauthenticated.SEC_FAULT_OUTPUT`
    - `unauthenticated.SEC_HEARTBEAT_OUTPUT`
    - `unauthenticated.SEC_3GPP_FAULTSUPERVISION_OUTPUT`
    - `unauthenticated.SEC_3GPP_HEARTBEAT_OUTPUT`
    - `unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT`
    - `unauthenticated.SEC_3GPP_PROVISIONING_OUTPUT`
  - **CPS/NCMP**:
    - `cps-data-updated-events`, `dmi-cm-events`, `dmi-device-heartbeat`
    - `ncmp-async-m2m`, `ncmp-dmi-cm-avc-subscription`
  - **OPA**: `opa-pdp-data` (10 partitions)
  - `subscription` (2 partitions)
- **27 Consumer Groups** - All Stable:
  - **Policy Framework**: `policy-pap` (2 members), `policy-apex`, `policy-clamp-runtime-acm`, `policy-clamp-ac-a1pms-ppnt`, `policy-clamp-ac-http-ppnt`, `policy-clamp-ac-k8s-ppnt`, `policy-clamp-ac-kserve-ppnt`, `policy-clamp-ac-pf-ppnt`
  - **PM Pipeline**: `kafka-procon-json-file-data-from-filestore`, `kafka-procon-json-file-data-from-filestore-to-influx`, `kafka-procon-xml-file-data-to-filestore`
  - **CPS/NCMP**: `cps-core-group` (4 members), `ncmp-data-operation-event-group`, `ncmp-dmi-plugin-group`
  - **SDNR**: `sdnr-unauthenticated.SEC_3GPP_FAULTSUPERVISION_OUTPUT`, `sdnr-unauthenticated.SEC_3GPP_PROVISIONING_OUTPUT`, `sdnr-unauthenticated.SEC_FAULT_OUTPUT`, `sdnr-unauthenticated.VES_PNFREG_OUTPUT`
  - **Topology**: `topology-inventory-ingestion-consumer` (2 members, has lag)
  - **DME**: `dmeparticipant`
  - **DMAAP**: `osc-dmaap-adapter-unauthenticated.VES_NOTIFICATION_OUTPUT`
  - **Generic**: `kafkaGroupId`, 5 UUID-based groups
- **All consumer groups report 0 lag** except `topology-inventory-ingestion-consumer`

---

### 9. ✅ InfluxDB (Time Series DB)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:31814 |
| **Port** | 31814 |
| **Login** | `admin` / `mySuP3rS3cr3tT0keN` |
| **API Token** | `xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ` |
| **Status** | ✅ **Working** |

**Observations**:
- Version: v2.7.12
- Health: `pass` — ready for queries and writes
- Organization: `est` (id: `016ec2168b9eab4d`)
- **4 Configured buckets**:
  - `pm-bucket` (user, Retention: Forever)
  - `pm-logg-bucket` (user, Retention: Forever)
  - `_monitoring` (system, 7 days retention)
  - `_tasks` (system, 3 days retention)
- **API Auth**: Use `Authorization: Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ` header
- Flux queries working via POST `/api/v2/query?org=est`

---

### 10. ✅ Bundle Server (nginx)
| Property | Value |
|----------|-------|
| **URL** | http://hpe15.anuket.iol.unh.edu:32623 |
| **Port** | 32623 |
| **Auth** | None |
| **Status** | ✅ **Working** |

**Observations**:
- Returns nginx welcome page
- Server installed and running, requires further configuration for O-RAN bundles

---

### 11. ✅ Non-RT-RIC Control Panel
| Property | Value |
|----------|-------|
| **URL (Frontend)** | http://hpe15.anuket.iol.unh.edu:30091 |
| **URL (Backend)** | http://hpe15.anuket.iol.unh.edu:30092 |
| **Port** | 30091 (UI) / 30092 (API) |
| **Auth** | None |
| **Status** | ✅ **Working** |

**Observations**:
- Angular-based dashboard for managing Non-RT-RIC
- Supports Light/Dark theme toggle
- **Two main sections**: Policy Control, Information Coordinator

#### Policy Control
- **Policy Types**: None deployed yet
  - "There are no policy types to display."
  - Policy types are registered by xApps on the Near-RT RIC; will appear once xApps are deployed

#### Information Coordinator — Producers
| Producer | Status |
|----------|--------|
| `https://dmaapadapterservice.nonrtric:9088` | ✅ **ENABLED** |
| `http://pm-producer-json2kafka-0.pm-producer-json2kafka.smo:8084` | ✅ **ENABLED** |

- **DMAAP Adapter Service** — Bridges DMAAP (VES events, PM file notifications) to the Information Coordinator
- **PM Producer JSON2Kafka** — Produces PM data (type: `PmData`) from filestore to Kafka

#### Information Coordinator — Jobs
| Job ID | Info Type | Owner | Status |
|--------|-----------|-------|--------|
| `PmData_5b3f4db6-3d9e-11ed-b878-0242ac120002` | `xml-file-data-to-filestore` | `pmproducer` | ⚠️ DISABLED |
| `job-kp-influx-json-0` | `json-file-data-from-filestore-to-influx` | `console` | ⚠️ DISABLED |

- Both jobs are currently DISABLED — expected in default deployment, can be enabled when PM data collection is needed

---

## HPE16 (Near-RT RIC) Interfaces

### 12. ✅ Kong Manager (API Gateway)
| Property | Value |
|----------|-------|
| **URL** | http://hpe16.anuket.iol.unh.edu:30806 |
| **Port** | 30806 |
| **Auth** | None |
| **Status** | ✅ **Working** |

**Observations**:
- Kong Manager OSS UI accessible
- Gateway routes A1 Mediator API to backend services
- Admin REST API is ClusterIP-only (not exposed via NodePort)

---

### 13. ✅ A1 Mediator Interface
| Property | Value |
|----------|-------|
| **URL** | http://hpe16.anuket.iol.unh.edu:30803 |
| **Port** | 30803 (via Kong gateway) |
| **Auth** | None |
| **Status** | ✅ **Working** |

**Observations**:
- Root path returns: `{"code":404,"message":"path / was not found"}` (expected — use API paths)
- **Tested Endpoints**:
  - `GET /A1-P/v2/policytypes` → ✅ 200 — Returns `[]` (no xApps with policy types deployed yet)
  - `PUT /A1-P/v2/policytypes/{id}/policies/{pid}` — Create policy instance (template ready)
  - `DELETE /A1-P/v2/policytypes/{id}/policies/{pid}` — Delete policy instance (template ready)

---

## Credentials Summary

| Service | URL | Auth Method | Credentials |
|---------|-----|-------------|-------------|
| SDNC Web/API | :30205 / :30267 | Basic Auth | `admin` / `Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U` |
| Keycloak | :30202 | Bearer Token | `admin` / `admin` (via master realm) |
| MinIO | :32208 | Login | `admin` / `adminadmin` |
| InfluxDB | :31814 | Token Header | `Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ` |
| InfluxDB | :31814 | Login | `admin` / `mySuP3rS3cr3tT0keN` |

---