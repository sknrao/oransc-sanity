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

## 9. `kubectl describe pod` — CVE-Fix Image Pods

The following outputs confirm that the 4 custom `mdimado/*:cve-fix` images are in use (not the default O-RAN SC images).

---

### 9.1 AppMgr Pod

```bash
kubectl describe pod -n ricplt -l app=ricplt-appmgr
```

```
Name:             deployment-ricplt-appmgr-7b66f7d574-kkcxj
Namespace:        ricplt
Priority:         0
Service Account:  default
Node:             aiml/10.200.105.55
Start Time:       Tue, 17 Feb 2026 14:20:02 +0000
Labels:           app=ricplt-appmgr
                  pod-template-hash=7b66f7d574
                  release=r4-appmgr
Status:           Running
IP:               10.244.249.214
Controlled By:    ReplicaSet/deployment-ricplt-appmgr-7b66f7d574

Containers:
  container-ricplt-appmgr:
    Container ID:   containerd://ea38bc3675ca015496b39ccb6ea3f853719bfd7c397027ba6d05ee1b73b8f165
    Image:          docker.io/mdimado/ric-plt-appmgr:cve-fix
    Image ID:       docker.io/mdimado/ric-plt-appmgr@sha256:b1c6055ad69a897c7bd8ecc1a2ad6c799ac2e30ea54532995f8821a2d9fec389
    Ports:          8080/TCP, 4561/TCP, 4560/TCP
    State:          Running
      Started:      Tue, 17 Feb 2026 14:20:23 +0000
    Ready:          True
    Restart Count:  0

Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
```

---

### 9.2 E2Mgr Pod

```bash
kubectl describe pod -n ricplt -l app=ricplt-e2mgr
```

```
Name:             deployment-ricplt-e2mgr-78f8cc4ff9-qsqmx
Namespace:        ricplt
Priority:         0
Service Account:  default
Node:             aiml/10.200.105.55
Start Time:       Wed, 18 Feb 2026 07:34:44 +0000
Labels:           app=ricplt-e2mgr
                  pod-template-hash=78f8cc4ff9
                  release=r4-e2mgr
Status:           Running
IP:               10.244.249.213
Controlled By:    ReplicaSet/deployment-ricplt-e2mgr-78f8cc4ff9

Containers:
  container-ricplt-e2mgr:
    Container ID:   containerd://48c41a9dffb37afe47d513ef19c79294eb446b5ae973534dd249a35aab819991
    Image:          docker.io/mdimado/ric-plt-e2mgr:cve-fix
    Image ID:       docker.io/mdimado/ric-plt-e2mgr@sha256:81289abb9e684dab37dd3c5e8cdd427edc67facc4a09b11500d8bdc675b7b0e0
    Ports:          3800/TCP, 4561/TCP, 3801/TCP
    State:          Running
      Started:      Wed, 18 Feb 2026 07:34:45 +0000
    Ready:          True
    Restart Count:  0
    Liveness:       http-get http://:3800/v1/health delay=3s timeout=1s period=10s #success=1 #failure=3
    Readiness:      http-get http://:3800/v1/health delay=3s timeout=1s period=10s #success=1 #failure=3

Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
```

---

### 9.3 E2Term Pod

```bash
kubectl describe pod -n ricplt -l app=ricplt-e2term-alpha
```

```
Name:             deployment-ricplt-e2term-alpha-7b58d8f944-5xlts
Namespace:        ricplt
Priority:         0
Service Account:  default
Node:             aiml/10.200.105.55
Start Time:       Wed, 18 Feb 2026 07:34:45 +0000
Labels:           app=ricplt-e2term-alpha
                  pod-template-hash=7b58d8f944
                  release=r4-e2term
Status:           Running
IP:               10.244.249.208
Controlled By:    ReplicaSet/deployment-ricplt-e2term-alpha-7b58d8f944

Containers:
  container-ricplt-e2term:
    Container ID:   containerd://5dba54823cf7d3e0f36557e10419cba1523ca174f76cdcdece151ed510b4e1f8
    Image:          docker.io/mdimado/ric-plt-e2:cve-fix
    Image ID:       docker.io/mdimado/ric-plt-e2@sha256:a27b0a0ee332979c8f4906dbc93d75e44d9fc344696271270bb84d80190c1b5c
    Ports:          4561/TCP, 38000/TCP, 36422/SCTP, 8088/TCP
    State:          Running
      Started:      Wed, 18 Feb 2026 07:34:45 +0000
    Ready:          True
    Restart Count:  0
    Liveness:       exec [/bin/sh -c ip=`hostname -i`;export RMR_SRC_ID=$ip;/opt/e2/rmr_probe -h $ip:38000] delay=10s timeout=1s period=10s #success=1 #failure=3
    Readiness:      exec [/bin/sh -c ip=`hostname -i`;export RMR_SRC_ID=$ip;/opt/e2/rmr_probe -h $ip:38000] delay=120s timeout=1s period=60s #success=1 #failure=3
    Environment:
      SYSTEM_NAME:      SEP
      CONFIG_MAP_NAME:  /etc/config/log-level
      SERVICE_NAME:     RIC_E2_TERM
      CONTAINER_NAME:   container-ricplt-e2term

Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
```

---

### 9.4 SubMgr Pod

```bash
kubectl describe pod -n ricplt -l app=ricplt-submgr
```

```
Name:             deployment-ricplt-submgr-668b97dbfd-gfcsr
Namespace:        ricplt
Priority:         0
Service Account:  default
Node:             aiml/10.200.105.55
Start Time:       Tue, 17 Feb 2026 14:21:39 +0000
Labels:           app=ricplt-submgr
                  pod-template-hash=668b97dbfd
                  release=r4-submgr
Status:           Running
IP:               10.244.249.236
Controlled By:    ReplicaSet/deployment-ricplt-submgr-668b97dbfd

Containers:
  container-ricplt-submgr:
    Container ID:   containerd://ace1a99c1904de2d5445e76dcf4fa657a80c4ae3538dd3c2f3d95bbd79e4c3e0
    Image:          docker.io/mdimado/ric-plt-submgr:cve-fix
    Image ID:       docker.io/mdimado/ric-plt-submgr@sha256:8a04b89f4abc2e8ba423e19f61b552e5dfad2f35713bf88c7aec03f46f2b718a
    Ports:          3800/TCP, 4561/TCP, 4560/TCP
    Command:        /submgr
    Args:           -f /cfg/submgr-config.yaml
    State:          Running
      Started:      Tue, 17 Feb 2026 14:21:40 +0000
    Ready:          True
    Restart Count:  0
    Liveness:       http-get http://:8080/ric/v1/health/alive delay=5s timeout=1s period=15s #success=1 #failure=3
    Readiness:      http-get http://:8080/ric/v1/health/ready delay=5s timeout=1s period=15s #success=1 #failure=3

Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
```

---

## 10. Test Summary

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

