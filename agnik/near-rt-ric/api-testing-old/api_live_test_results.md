# O-RAN API Live Test Results


---

## 1. A1 Policy Management Service (SMO — :30094)

### 1.1 GET /a1-policy/v2/rics — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/rics
```
```json
{
  "rics": [
    {
      "ric_id": "hpe16-ric",
      "managed_element_ids": [],
      "state": "AVAILABLE",
      "policytype_ids": []
    }
  ]
}
```

### 1.2 GET /a1-policy/v2/rics/ric?ric_id=hpe16-ric — ✅ 200
```bash
curl 'http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/rics/ric?ric_id=hpe16-ric'
```
```json
{
  "ric_id": "hpe16-ric",
  "managed_element_ids": [],
  "state": "AVAILABLE",
  "policytype_ids": []
}
```

### 1.3 GET /a1-policy/v2/policy-types — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/policy-types
```
```json
{
  "policytype_ids": []
}
```
> No policy types registered yet — requires xApp deployment on RIC

### 1.4 GET /a1-policy/v2/policies — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/policies
```
```json
{
  "policy_ids": []
}
```

### 1.5 GET /a1-policy/v2/services — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/services
```
```json
{
  "service_list": [
    {
      "callback_url": "",
      "service_id": "test-service",
      "keep_alive_interval_seconds": 0,
      "time_since_last_activity_seconds": 306
    }
  ]
}
```

### 1.6 GET /a1-policy/v2/status — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/status
```
```json
{
  "status": "success"
}
```

### 1.7 GET /a1-policy/v2/configuration — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/configuration
```
```json
{
  "config": {
    "ric": [
      {
        "name": "hpe16-ric",
        "baseUrl": "http://10.200.105.60:30803",
        "managedElementIds": [],
        "customAdapterClass": "org.onap.ccsdk.oran.a1policymanagementservice.clients.StdA1ClientVersion2"
      }
    ],
    "controller": []
  }
}
```

### 1.8 PUT /a1-policy/v2/services (Register Service) — ✅ 201
```bash
curl -X PUT -H 'Content-Type: application/json' \
  -d '{"service_id":"test-rapp","keep_alive_interval_seconds":0,"callback_url":""}' \
  http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/services
```
```
HTTP 201 Created (empty body — service registered successfully)
```

### 1.9 DELETE /a1-policy/v2/services/{id} — ✅ 204
```bash
curl -X DELETE http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/services/test-rapp
```
```
HTTP 204 No Content (service deleted successfully)
```

### 1.10 PUT /a1-policy/v2/policies (Create Policy) — ⚠️ 423
```bash
curl -X PUT -H 'Content-Type: application/json' \
  -d '{"ric_id":"hpe16-ric","policy_id":"test-1","service_id":"","policytype_id":"","policy_data":{}}' \
  http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/policies
```
```
HTTP 423 Locked — no policy types available on this RIC yet
```
> Expected: No xApp has registered a policy type. Will work after xApp deployment.

### 1.11 PUT /a1-policy/v2/services/{id}/keepalive — ✅ 200
```bash
curl -X PUT http://hpe15.anuket.iol.unh.edu:30094/a1-policy/v2/services/test-service/keepalive
```
```
HTTP 200 OK (heartbeat acknowledged)
```

---

## 2. SDNC RESTCONF (SMO — :30267)

**Auth**: `admin` / `Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U`

### 2.1 GET /rests/data/network-topology:network-topology — ✅ 200
```bash
curl -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  -H 'Accept: application/json' \
  http://hpe15.anuket.iol.unh.edu:30267/rests/data/network-topology:network-topology
```
```json
[
  {"node-id": "o-du-pynts-1122", "status": "connected"},
  {"node-id": "o-du",            "status": "connected"},
  {"node-id": "o-du-pynts-1123", "status": "connected"}
]
```

### 2.2 GET .../node=o-du-pynts-1122 — ✅ 200
```bash
curl -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  -H 'Accept: application/json' \
  'http://hpe15.anuket.iol.unh.edu:30267/rests/data/network-topology:network-topology/topology=topology-netconf/node=o-du-pynts-1122'
```
```json
{
  "node-id": "o-du-pynts-1122",
  "host": "10.244.72.210",
  "port": 830,
  "connection-status": "connected"
}
```

### 2.3 GET /rests/data/ietf-yang-library:modules-state — ✅ 200
```bash
curl -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  -H 'Accept: application/json' \
  http://hpe15.anuket.iol.unh.edu:30267/rests/data/ietf-yang-library:modules-state
```
```
128 YANG modules loaded
```

### 2.4 GET /rests/data/ietf-netconf-monitoring:netconf-state — ⚠️ 409
```bash
curl -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  http://hpe15.anuket.iol.unh.edu:30267/rests/data/ietf-netconf-monitoring:netconf-state
```
```
HTTP 409 Conflict — resource not available in this SDNC version
```

### 2.5 PUT .../node=test-device-1 (Mount Device) — Available
```bash
curl -X PUT -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"node":[{"node-id":"test-device-1","netconf-node-topology:host":"10.0.0.1","netconf-node-topology:port":830,"netconf-node-topology:username":"admin","netconf-node-topology:password":"admin","netconf-node-topology:tcp-only":false}]}' \
  'http://hpe15.anuket.iol.unh.edu:30267/rests/data/network-topology:network-topology/topology=topology-netconf/node=test-device-1'
```


### 2.6 DELETE .../node=test-device-1 (Unmount Device) — Available
```bash
curl -X DELETE -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  'http://hpe15.anuket.iol.unh.edu:30267/rests/data/network-topology:network-topology/topology=topology-netconf/node=test-device-1'
```


---

## 3. Keycloak (SMO — :30202)

**Auth**: Bearer token from `admin`/`admin` via master realm

### 3.1 GET /.well-known/openid-configuration — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30202/realms/nonrtric-realm/.well-known/openid-configuration
```
```json
{
  "issuer": "http://hpe15.anuket.iol.unh.edu:30202/realms/nonrtric-realm",
  "token_endpoint": "http://hpe15.anuket.iol.unh.edu:30202/realms/nonrtric-realm/protocol/openid-connect/token",
  "authorization_endpoint": "http://hpe15.anuket.iol.unh.edu:30202/realms/nonrtric-realm/protocol/openid-connect/auth",
  "grant_types_supported": [
    "authorization_code", "client_credentials", "implicit",
    "password", "refresh_token",
    "urn:ietf:params:oauth:grant-type:device_code",
    "urn:ietf:params:oauth:grant-type:token-exchange",
    "urn:ietf:params:oauth:grant-type:uma-ticket",
    "urn:openid:params:grant-type:ciba"
  ]
}
```

### 3.2 POST /realms/master/protocol/openid-connect/token — ✅ 200
```bash
curl -X POST \
  -d 'grant_type=password&client_id=admin-cli&username=admin&password=admin' \
  http://hpe15.anuket.iol.unh.edu:30202/realms/master/protocol/openid-connect/token
```
```json
{
  "access_token": "eyJhbGciOi...(JWT token)...",
  "token_type": "Bearer",
  "expires_in": 60
}
```

### 3.3 GET /admin/realms — ✅ 200
```bash
# First get token, then use it:
TOKEN=$(curl -s -X POST -d 'grant_type=password&client_id=admin-cli&username=admin&password=admin' \
  http://hpe15.anuket.iol.unh.edu:30202/realms/master/protocol/openid-connect/token | jq -r '.access_token')
curl -H "Authorization: Bearer $TOKEN" http://hpe15.anuket.iol.unh.edu:30202/admin/realms
```
```json
[
  {"realm": "master"},
  {"realm": "nonrtric-realm"}
]
```

### 3.4 GET /admin/realms/nonrtric-realm/clients — ✅ 200
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://hpe15.anuket.iol.unh.edu:30202/admin/realms/nonrtric-realm/clients
```
```json
[
  {"clientId": "account"},
  {"clientId": "account-console"},
  {"clientId": "admin-cli"},
  {"clientId": "broker"},
  {"clientId": "console-setup"},
  {"clientId": "dfc",                        "secret": "yI163T9pM3U1jtI2WqQKyN9pFaRZryFW"},
  {"clientId": "kafka-producer-pm-json2influx"},
  {"clientId": "kafka-producer-pm-json2kafka"},
  {"clientId": "kafka-producer-pm-xml2json"},
  {"clientId": "nrt-pm-log",                 "secret": "u8AEJGDA6uSVGW1NpP4UFKhcd1MMtNlZ"},
  {"clientId": "pm-producer-json2kafka",     "secret": "5VKEaVU19XaqfuIDkDMD134wyYgKCvVp"},
  {"clientId": "realm-management"},
  {"clientId": "security-admin-console"}
]
```

---

## 4. InfluxDB (SMO — :31814)

**Auth**: `Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ` (from k8s secret `influxdb-api-token`)  
**Login**: `admin` / `mySuP3rS3cr3tT0keN` (from k8s secret `influxdb2-secret`)

### 4.1 GET /health — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:31814/health
```
```json
{
  "name": "influxdb",
  "message": "ready for queries and writes",
  "status": "pass",
  "checks": [],
  "version": "v2.7.12",
  "commit": "ec9dcde5d6"
}
```

### 4.2 GET /api/v2/buckets — ✅ 200
```bash
curl -H "Authorization: Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ" \
  http://hpe15.anuket.iol.unh.edu:31814/api/v2/buckets
```
```json
[
  {"name": "pm-logg-bucket", "id": "13428d732dae5a8d", "type": "user"},
  {"name": "_monitoring",    "id": "2669c6d9cdb7c52e", "type": "system"},
  {"name": "_tasks",         "id": "9c46a0ba8d8e33f1", "type": "system"},
  {"name": "pm-bucket",      "id": "cccd7261e993727d", "type": "user"}
]
```

### 4.3 GET /api/v2/orgs — ✅ 200
```bash
curl -H "Authorization: Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ" \
  http://hpe15.anuket.iol.unh.edu:31814/api/v2/orgs
```
```json
{
  "orgs": [
    {
      "id": "016ec2168b9eab4d",
      "name": "est",
      "createdAt": "2026-02-05T19:08:10.014641596Z"
    }
  ]
}
```

### 4.4 POST /api/v2/query — ✅ 200
```bash
curl -H "Authorization: Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ" \
  -H "Content-Type: application/json" -H "Accept: application/csv" \
  -X POST "http://hpe15.anuket.iol.unh.edu:31814/api/v2/query?org=est" \
  -d '{"query":"buckets()","type":"flux"}'
```
```csv
,result,table,name,id,organizationID,retentionPolicy,retentionPeriod
,_result,0,_monitoring,2669c6d9cdb7c52e,016ec2168b9eab4d,,604800000000000
,_result,0,_tasks,9c46a0ba8d8e33f1,016ec2168b9eab4d,,259200000000000
,_result,0,pm-bucket,cccd7261e993727d,016ec2168b9eab4d,,0
,_result,0,pm-logg-bucket,13428d732dae5a8d,016ec2168b9eab4d,,0
```

---

## 5. MinIO (SMO — :32208)

**Auth**: `admin` / `adminadmin`

### 5.1 GET /minio/health/live — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:32208/minio/health/live
```
```
HTTP 200 OK (empty body — healthy)
```

---

## 6. Non-RT-RIC Control Panel (SMO — :30091 / :30092)

### 6.1 GET / — ✅ 200
```bash
curl http://hpe15.anuket.iol.unh.edu:30091/
```
```
HTTP 200 OK — Angular dashboard HTML returned
```

---

## 7. A1 Mediator (RIC — :30803 via Kong)

### 7.1 GET /A1-P/v2/policytypes — ✅ 200
```bash
curl http://hpe16.anuket.iol.unh.edu:30803/A1-P/v2/policytypes
```
```json
[]
```


### 7.2 GET /a1-p/healthcheck — ⚠️ 404
```bash
curl http://hpe16.anuket.iol.unh.edu:30803/a1-p/healthcheck
```
```
HTTP 404 — healthcheck path not routed through Kong
```

---

## 8. Kong Gateway (RIC — :30806)

### 8.1 GET / (Manager UI) — ✅ 200
```bash
curl http://hpe16.anuket.iol.unh.edu:30806/
```
```
HTTP 200 — Kong Manager OSS HTML UI served
```
> Port 30806 is the Manager UI, not the admin REST API.

---

## 9. E2 Manager (RIC — :3800 via kubectl exec)

**Access**: `kubectl exec -n ricplt deployment/deployment-ricplt-e2mgr -- curl http://localhost:3800/...`

### 9.1 GET /v1/health — ✅ 200
```bash
curl http://localhost:3800/v1/health
```
```
HTTP 200 OK
```

### 9.2 GET /v1/e2t/list — ✅ 200
```bash
curl http://localhost:3800/v1/e2t/list
```
```json
[
  {
    "e2tAddress": "10.107.227.26:38000",
    "ranNames": ["gnb_734_373_16b8cef1"]
  }
]
```

### 9.3 GET /v1/nodeb/states — ✅ 200
```bash
curl http://localhost:3800/v1/nodeb/states
```
```json
[
  {
    "inventoryName": "gnb_734_373_16b8cef1",
    "globalNbId": {
      "plmnId": "373437",
      "nbId": "10110101110001100111011110001"
    },
    "connectionStatus": "CONNECTED"
  }
]
```

### 9.4 GET /v1/nodeb/gnb_734_373_16b8cef1 — ✅ 200
```bash
curl http://localhost:3800/v1/nodeb/gnb_734_373_16b8cef1
```
```json
{
  "ranName": "gnb_734_373_16b8cef1",
  "connectionStatus": "CONNECTED",
  "globalNbId": {
    "plmnId": "373437",
    "nbId": "10110101110001100111011110001"
  },
  "nodeType": "GNB",
  "gnb": {
    "ranFunctions": [
      {
        "ranFunctionDefinition": "68304F52414E2D4532534D2D4B504D...",
        "ranFunctionRevision": 2,
        "ranFunctionOid": "OID123"
      }
    ],
    "gnbType": "GNB",
    "nodeConfigs": [...]
  },
  "associatedE2tInstanceAddress": "10.107.227.26:38000",
  "setupFrom": "E2_SETUP_PROCEDURE",
  "statusUpdateTimeStamp": 1739205123456
}
```
> **Note**: Confirmed that **E2 Simulator** is connected as a gNB with PLMN 373437.

---


## Summary Table

| # | Service | Endpoint | Method | Status | Result |
|---|---------|----------|--------|--------|--------|
| 1 | A1PMS | `/v2/rics` | GET | ✅ 200 | 1 RIC (hpe16-ric) AVAILABLE |
| 2 | A1PMS | `/v2/rics/ric?ric_id=...` | GET | ✅ 200 | RIC details returned |
| 3 | A1PMS | `/v2/policy-types` | GET | ✅ 200 | Empty (no xApps) |
| 4 | A1PMS | `/v2/policies` | GET | ✅ 200 | Empty |
| 5 | A1PMS | `/v2/services` | GET | ✅ 200 | test-service listed |
| 6 | A1PMS | `/v2/status` | GET | ✅ 200 | "success" |
| 7 | A1PMS | `/v2/configuration` | GET | ✅ 200 | RIC config returned |
| 8 | A1PMS | `/v2/services` | PUT | ✅ 201 | Service created |
| 9 | A1PMS | `/v2/services/{id}` | DELETE | ✅ 204 | Service deleted |
| 10 | A1PMS | `/v2/services/{id}/keepalive` | PUT | ✅ 200 | Heartbeat OK |
| 11 | A1PMS | `/v2/policies` | PUT | ⚠️ 423 | No policy types (expected) |
| 12 | SDNC | `/network-topology` | GET | ✅ 200 | 3 nodes connected |
| 13 | SDNC | `/node=o-du-pynts-1122` | GET | ✅ 200 | Node details |
| 14 | SDNC | `/ietf-yang-library` | GET | ✅ 200 | 128 YANG modules |
| 15 | SDNC | `/netconf-monitoring` | GET | ⚠️ 409 | Conflict |
| 16 | Keycloak | `/.well-known/openid-config` | GET | ✅ 200 | OIDC discovery |
| 17 | Keycloak | `/token` (master) | POST | ✅ 200 | Bearer token issued |
| 18 | Keycloak | `/admin/realms` | GET | ✅ 200 | master + nonrtric-realm |
| 19 | Keycloak | `/admin/.../clients` | GET | ✅ 200 | 13 clients listed |
| 20 | InfluxDB | `/health` | GET | ✅ 200 | pass (v2.7.12) |
| 21 | InfluxDB | `/api/v2/buckets` | GET | ✅ 200 | 4 buckets listed |
| 22 | InfluxDB | `/api/v2/orgs` | GET | ✅ 200 | org "est" |
| 23 | InfluxDB | `/api/v2/query` | POST | ✅ 200 | Flux query works |
| 24 | MinIO | `/minio/health/live` | GET | ✅ 200 | Healthy |
| 25 | Control Panel | `/` | GET | ✅ 200 | Dashboard served |
| 26 | A1 Mediator | `/A1-P/v2/policytypes` | GET | ✅ 200 | Empty array |
| 27 | A1 Mediator | `/a1-p/healthcheck` | GET | ⚠️ 404 | Not routed via Kong |
| 28 | Kong | `/` (Manager UI) | GET | ✅ 200 | UI served |
| 29 | E2Mgr | `/v1/health` | GET | ✅ 200 | Healthy |
| 30 | E2Mgr | `/v1/e2t/list` | GET | ✅ 200 | E2Term + 1 gNB |
| 31 | E2Mgr | `/v1/nodeb/states` | GET | ✅ 200 | gNB CONNECTED |
