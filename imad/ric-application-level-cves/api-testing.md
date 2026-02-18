# Near-RT RIC — CVE-Fix Image Verification & Comprehensive API Test Results

> **Server**: hpe26.anuket.iol.unh.edu  
> **Date**: 2026-02-18  
> **RIC Deployment**: Custom CVE-Fix Images (`mdimado/*:cve-fix`)

---

## 1. Custom CVE-Fix Image Verification

All **4 custom images** are deployed and running with **0 restarts**. No issues.

| Component | Image | Status | Restarts |
|-----------|-------|--------|----------|
| **AppMgr** | `docker.io/mdimado/ric-plt-appmgr:cve-fix` | ✅ Running | 0 |
| **E2Mgr** | `docker.io/mdimado/ric-plt-e2mgr:cve-fix` | ✅ Running | 0 |
| **E2Term** | `docker.io/mdimado/ric-plt-e2:cve-fix` | ✅ Running | 0 |
| **SubMgr** | `docker.io/mdimado/ric-plt-submgr:cve-fix` | ✅ Running | 0 |

---

## 2. NodePort Services (Exposed for External Access)

| Service | NodePort | Internal Port | Status |
|---------|----------|--------------|--------|
| A1 Mediator | **30803** | 10000 | ✅ Active |
| E2Mgr | **30850** | 3800 | ✅ Active |
| AppMgr | **30851** | 8080 | ✅ Active |
| RtMgr | **30852** | 3800 | ✅ Active |
| Kong Proxy | **32080** | 80 | ✅ Active |
| Kong Manager | **30780** | 8002 | ✅ Active |
| E2Term SCTP | **32222** | 36422 | ✅ Active |
| O1 Mediator NETCONF | **30830** | 830 | ✅ Active |

---

## 3. E2Mgr APIs (Port 30850)

### 3.1 Health Check

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30850/v1/health
```

**Response**: *(empty body)*  
**HTTP Status**: `200 OK` ✅

---

### 3.2 Get NodeB States

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30850/v1/nodeb/states
```

**Response**:
```json
[
  {
    "inventoryName": "gnb_734_373_16b8cef1",
    "globalNbId": {
      "plmnId": "373437",
      "nbId": "10110101110001100111011110001"
    },
    "connectionStatus": "DISCONNECTED"
  }
]
```

**HTTP Status**: `200 OK` ✅

> Shows the E2 Simulator's gNB is registered. `DISCONNECTED` status is normal — the simulator sends a single E2 Setup Request and then idles.

---

### 3.3 Get NodeB Detail (by inventory name)

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30850/v1/nodeb/gnb_734_373_16b8cef1
```

**Response**:
```json
{
  "ranName": "gnb_734_373_16b8cef1",
  "connectionStatus": "DISCONNECTED",
  "globalNbId": {
    "plmnId": "373437",
    "nbId": "10110101110001100111011110001"
  },
  "nodeType": "GNB",
  "gnb": {
    "ranFunctions": [
      {
        "ranFunctionId": 1,
        "ranFunctionDefinition": "...",
        "ranFunctionRevision": 1,
        "ranFunctionOid": "OID123"
      }
    ],
    "gnbType": "GNB",
    "nodeConfigs": [
      {
        "e2nodeComponentInterfaceTypeNG": {
          "amfName": "nginterf"
        },
        "e2nodeComponentRequestPart": "NzI2NTcxNzA2MTcyNzQ=",
        "e2nodeComponentResponsePart": "NzI2NTczNzA2MTcyNzQ="
      }
    ]
  },
  "setupFromNetwork": true,
  "gnbNodeType": "gNB"
}
```

**HTTP Status**: `200 OK` ✅

---

## 4. AppMgr APIs (Port 30851)

### 4.1 Health Alive

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30851/ric/v1/health/alive
```

**Response**: *(empty body)*  
**HTTP Status**: `200 OK` ✅

---

### 4.2 Health Ready

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30851/ric/v1/health/ready
```

**Response**: *(empty body)*  
**HTTP Status**: `200 OK` ✅

---

### 4.3 List xApps

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30851/ric/v1/xapps
```

**Response**:
```json
[]
```

**HTTP Status**: `200 OK` ✅

> Empty because xApps were deployed via kubectl directly, not through the AppMgr API.

---

### 4.4 List Subscriptions

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30851/ric/v1/subscriptions
```

**Response**:
```json
[
  {
    "data": {
      "eventType": "all",
      "maxRetries": 5,
      "retryTimer": 5,
      "targetUrl": "http://service-ricplt-vespamgr-http.ricplt.svc.cluster.local:8080/ric/v1/xappnotif"
    },
    "id": "39niDSuN0Z8ei1JTHIV1wSbcg7e"
  },
  {
    "data": {
      "eventType": "all",
      "maxRetries": 5,
      "retryTimer": 10,
      "targetUrl": "http://service-ricplt-rtmgr-http:3800/ric/v1/handles/xapp-handle/"
    },
    "id": "39niDgo59c2GqcZx0wX3HQgpJNk"
  }
]
```

**HTTP Status**: `200 OK` ✅

> Two internal subscriptions: VespaMgr and RtMgr are subscribed to AppMgr events.

---

### 4.5 Get Config

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30851/ric/v1/config
```

**Response**:
```json
[]
```

**HTTP Status**: `200 OK` ✅

---

## 5. RtMgr APIs (Port 30852)

### 5.1 Get Debug Info (Route Table)

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30852/ric/v1/getdebuginfo
```

**Response**:
```json
{
  "RouteConfigs": {
    "XApps": [],
    "E2Ts": {
      "10.97.150.16:38000": {
        "name": "E2TERMINST",
        "fqdn": "10.97.150.16:38000",
        "ranlist": []
      }
    },
    "MeidMap": [
      "mme_ar|10.97.150.16:38000|gnb_734_373_16b8cef1",
      "mme_del|gnb_734_373_16b8cef1"
    ],
    "Pcs": [
      {
        "name": "SUBMAN",
        "fqdn": "service-ricplt-submgr-rmr.ricplt",
        "port": 4560
      },
      {
        "name": "E2MAN",
        "fqdn": "service-ricplt-e2mgr-rmr.ricplt",
        "port": 3801
      },
      {
        "name": "A1MEDIATOR",
        "fqdn": "service-ricplt-a1mediator-rmr.ricplt",
        "port": 4562
      }
    ]
  },
  "RouteTable": [
    "mse|12010,service-ricplt-submgr-rmr.ricplt:4560|-1|%meid",
    "mse|12020,service-ricplt-submgr-rmr.ricplt:4560|-1|%meid",
    "mse|10060,service-ricplt-e2mgr-rmr.ricplt:3801|-1|%meid",
    "mse|20012|-1|service-ricplt-a1mediator-rmr.ricplt:4562",
    "mse|20011|-1|service-ricplt-a1mediator-rmr.ricplt:4562",
    "..."
  ]
}
```

**HTTP Status**: `200 OK` ✅

> Shows E2Term instance, MEID mapping for the gNB, platform components (SubMgr, E2Mgr, A1Mediator), and the full RMR routing table.

---

## 6. A1 Mediator APIs (Port 30803)

### 6.1 Health Check

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30803/A1-P/v2/healthcheck
```

**Response**: *(empty body)*  
**HTTP Status**: `200 OK` ✅

---

### 6.2 Get Policy Types

```bash
curl -s http://hpe26.anuket.iol.unh.edu:30803/A1-P/v2/policytypes
```

**Response**:
```json
[]
```

**HTTP Status**: `200 OK` ✅

> Empty because no xApps have registered A1 policy types yet.

---

## 7. A1PMS / SMO APIs (hpe15:30094)

### 7.1 A1PMS Status

```bash
curl -s http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/status
```

**Response**:
```json
{
  "status": "success"
}
```

**HTTP Status**: `200 OK` ✅

---

### 7.2 List Registered RICs

```bash
curl -s http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/rics
```

**Response**:
```json
{
  "rics": [
    {
      "ric_id": "hpe16-ric",
      "managed_element_ids": [],
      "state": "UNAVAILABLE",
      "policytype_ids": []
    },
    {
      "ric_id": "hpe26-ric",
      "managed_element_ids": [],
      "state": "AVAILABLE",
      "policytype_ids": []
    }
  ]
}
```

**HTTP Status**: `200 OK` ✅

---

### 7.3 Get A1PMS Configuration

```bash
curl -s http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/configuration
```

**Response**:
```json
{
  "config": {
    "ric": [
      {
        "name": "hpe16-ric",
        "baseUrl": "http://10.200.105.60:30803",
        "managedElementIds": [],
        "customAdapterClass": "org.onap.ccsdk.oran.a1policymanagementservice.clients.StdA1ClientVersion2"
      },
      {
        "name": "hpe26-ric",
        "baseUrl": "http://hpe26.anuket.iol.unh.edu:30803",
        "managedElementIds": [],
        "customAdapterClass": "org.onap.ccsdk.oran.a1policymanagementservice.clients.StdA1ClientVersion2"
      }
    ],
    "controller": []
  }
}
```

**HTTP Status**: `200 OK` ✅

---

### 7.4 List All Policies

```bash
curl -s http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/policies
```

**Response**:
```json
{
  "policy_ids": []
}
```

**HTTP Status**: `200 OK` ✅

---

### 7.5 List Registered Services

```bash
curl -s http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/services
```

**Response**:
```json
{
  "service_list": [
    {
      "callback_url": "",
      "service_id": "test-service",
      "keep_alive_interval_seconds": 0,
      "time_since_last_activity_seconds": 672438
    }
  ]
}
```

**HTTP Status**: `200 OK` ✅

---

### 7.6 Get Policy Types for hpe26-ric

```bash
curl -s "http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/policy-types?ric_id=hpe26-ric"
```

**Response**:
```json
{
  "policytype_ids": []
}
```

**HTTP Status**: `200 OK` ✅

---

## 8. Pod Status Summary

### 8.1 RIC Platform Pods (ricplt namespace) — 14 pods

| Pod | Ready | Status |
|-----|-------|--------|
| deployment-ricplt-a1mediator | 1/1 | ✅ Running |
| deployment-ricplt-alarmmanager | 1/1 | ✅ Running |
| deployment-ricplt-appmgr | 1/1 | ✅ Running |
| deployment-ricplt-e2mgr | 1/1 | ✅ Running |
| deployment-ricplt-e2term-alpha | 1/1 | ✅ Running |
| deployment-ricplt-o1mediator | 1/1 | ✅ Running |
| deployment-ricplt-rtmgr | 1/1 | ✅ Running |
| deployment-ricplt-submgr | 1/1 | ✅ Running |
| deployment-ricplt-vespamgr | 1/1 | ✅ Running |
| e2sim (E2 Simulator) | 1/1 | ✅ Running |
| r4-infrastructure-kong | 2/2 | ✅ Running |
| r4-infrastructure-prometheus-alertmanager | 2/2 | ✅ Running |
| r4-infrastructure-prometheus-server | 1/1 | ✅ Running |
| statefulset-ricplt-dbaas-server | 1/1 | ✅ Running |

### 8.2 xApp Pods (ricxapp namespace) — 5 pods

| Pod | Ready | Status |
|-----|-------|--------|
| deployment-ricxapp-ad | 1/1 | ✅ Running |
| deployment-ricxapp-kpimon-go | 1/1 | ✅ Running |
| deployment-ricxapp-qp | 1/1 | ✅ Running |
| deployment-ricxapp-rc | 1/1 | ✅ Running |
| deployment-ricxapp-ts | 1/1 | ✅ Running |

---

## 9. Test Summary

| # | API Endpoint | HTTP | Result |
|---|-------------|------|--------|
| 1 | E2Mgr: Health | 200 | ✅ PASS |
| 2 | E2Mgr: NodeB States | 200 | ✅ PASS |
| 3 | E2Mgr: NodeB Detail | 200 | ✅ PASS |
| 4 | AppMgr: Health Alive | 200 | ✅ PASS |
| 5 | AppMgr: Health Ready | 200 | ✅ PASS |
| 6 | AppMgr: List xApps | 200 | ✅ PASS |
| 7 | AppMgr: Subscriptions | 200 | ✅ PASS |
| 8 | AppMgr: Config | 200 | ✅ PASS |
| 9 | RtMgr: Debug Info | 200 | ✅ PASS |
| 10 | A1 Med: Healthcheck | 200 | ✅ PASS |
| 11 | A1 Med: Policy Types | 200 | ✅ PASS |
| 12 | A1PMS: Status | 200 | ✅ PASS |
| 13 | A1PMS: List RICs | 200 | ✅ PASS |
| 14 | A1PMS: Configuration | 200 | ✅ PASS |
| 15 | A1PMS: Policies | 200 | ✅ PASS |
| 16 | A1PMS: Services | 200 | ✅ PASS |
| 17 | A1PMS: Policy Types (hpe26) | 200 | ✅ PASS |

**Total: 17/17 PASSED** ✅
