# O-RAN API Integration Test Results

**Date**: February 11, 2026 — 14:20 IST  
**Servers**: hpe15 (SMO), hpe16 (Near-RT RIC)  
**Run from**: `/home/agnik/Desktop/deployoran/apitest/`  
**Python**: 3.12 with venv (minio, influxdb-client, kafka-python, requests)

---

## ✅ Overall: 25/26 Tests Passed (96%)

| Service | Script | Tests | Passed | Failed | Access |
|---------|--------|-------|--------|--------|--------|
| InfluxDB | `test_influxdb.py` | 6 | ✅ 6 | 0 | Direct NodePort :31814 |
| MinIO | `test_minio.py` | 8 | ✅ 8 | 0 | kubectl port-forward :9000 |
| Kafka | `test_kafka.py` | 5 | ✅ 5 | 0 | kubectl exec into broker pod |






| SDNR | `test_sdnr.py` | 7 | ✅ 6 | ❌ 1 | Direct NodePort :30267 |

---

## 1. InfluxDB — 6/6 PASSED ✅

**Script**: `test_influxdb.py`  
**Endpoint**: `http://hpe15.anuket.iol.unh.edu:31814`  
**Auth**: Token `xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ` | Org: `est`

### Test 1: Health Check ✅
```
GET /health
```
**Actual Response**:
```json
{"name":"influxdb", "message":"ready for queries and writes", "status":"pass", "checks":[], "version": "v2.7.12", "commit": "ec9dcde5d6"}
```

### Test 2: List Buckets ✅
```
GET /api/v2/buckets
```
**Actual Response** (4 buckets):
```
['pm-logg-bucket', '_monitoring', '_tasks', 'pm-bucket']
```

### Test 3: List Organizations ✅
```
GET /api/v2/orgs
```
**Actual Response**:
```
Orgs: ['est']
```

### Test 4: Write Data ✅
```
POST /api/v2/write?bucket=pm-bucket&org=est
Body: api_test,source=python_test_script,test_run=mentor_validation value=42.0,message="Hello from InfluxDB API test"
```
**Result**: Successfully wrote test point to `pm-bucket` (measurement: `api_test`)

### Test 5: Query Data ✅
```
POST /api/v2/query?org=est
Body (Flux):
  from(bucket: "pm-bucket")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "api_test")
    |> filter(fn: (r) => r.source == "python_test_script")
    |> last()
```
**Actual Response** (2 records):
```
→ Field: message, Value: Hello from InfluxDB API test, Time: 2026-02-11 08:51:59.058774+00:00
→ Field: value, Value: 42.0, Time: 2026-02-11 08:51:59.058774+00:00
```

### Test 6: Query Existing PM Data ✅
```
POST /api/v2/query?org=est
Body (Flux):
  from(bucket: "pm-bucket") |> range(start: -24h) |> limit(n: 5)
```
**Actual Response**: Found 4 records, measurements: `{'api_test'}`  
(No production PM data yet — pipeline not active, only our test data exists)

---

## 2. MinIO S3 API — 8/8 PASSED ✅

**Script**: `test_minio.py`  
**Endpoint**: `hpe15.anuket.iol.unh.edu:9000` (via kubectl port-forward)  
**Auth**: AccessKey `admin` / SecretKey `adminadmin`

**Prerequisite** (run once on hpe15):
```bash
sudo kubectl --kubeconfig /etc/kubernetes/admin.conf \
  port-forward -n smo svc/minio 9000:9000 --address=0.0.0.0 &
```

### Test 1: List Buckets ✅
```
GET / (S3 ListBuckets)
```
**Actual Response**:
```
Found 1 bucket: ['ropfiles']
```

### Test 2: Create Bucket ✅
```
PUT /test-api-bucket (S3 CreateBucket)
```
**Result**: Created `test-api-bucket`

### Test 3: Upload Object ✅
```
PUT /test-api-bucket/test-data.json (S3 PutObject)
Content-Type: application/json
Body: {"message": "Hello from API test", "timestamp": "2026-02-11"}
```
**Result**: Uploaded `test-data.json` (61 bytes)

### Test 4: List Objects ✅
```
GET /test-api-bucket (S3 ListObjects)
```
**Actual Response**:
```
Objects: ['test-data.json']
```

### Test 5: Download & Verify ✅
```
GET /test-api-bucket/test-data.json (S3 GetObject)
```
**Actual Response**:
```json
{"message": "Hello from API test", "timestamp": "2026-02-11"}
```
**Verification**: Data matches original ✅

### Test 6: Object Stat ✅
```
HEAD /test-api-bucket/test-data.json (S3 StatObject)
```
**Actual Response**:
```
Size: 61B, Type: application/json, Modified: 2026-02-11 08:52:15+00:00
```

### Test 7: Delete Object ✅
```
DELETE /test-api-bucket/test-data.json (S3 DeleteObject)
```
**Result**: Deleted

### Test 8: Delete Bucket ✅
```
DELETE /test-api-bucket (S3 DeleteBucket)
```
**Result**: Deleted

---

## 3. Kafka (Strimzi) — 5/5 PASSED ✅

**Script**: `test_kafka.py`  
**Broker**: `onap-strimzi-onap-strimzi-broker-0` pod (namespace `onap`)  
**Auth**: SCRAM-SHA-512 — `strimzi-kafka-admin` / `NCgQTlFIoaJijnVv5dZ5MQwM8ci99KAc`  
**Access**: `kubectl exec` (external NodePort :30493 requires TLS client certs)

### Test 1: Broker Connection & Topic Listing ✅
```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --command-config /tmp/client.properties --list
```
**Actual Response**: 29 topics found, 14 O-RAN related:
```
- unauthenticated.SEC_3GPP_FAULTSUPERVISION_OUTPUT
- unauthenticated.SEC_3GPP_HEARTBEAT_OUTPUT
- unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT
- unauthenticated.SEC_3GPP_PROVISIONING_OUTPUT
- unauthenticated.SEC_FAULT_OUTPUT
- unauthenticated.SEC_HEARTBEAT_OUTPUT
- unauthenticated.VES_MEASUREMENT_OUTPUT
- unauthenticated.VES_NOTIFICATION_OUTPUT
- unauthenticated.VES_PNFREG_OUTPUT
- policy-pdp-pap
- policy-notification
- policy-heartbeat
- policy-acruntime-participant
- acm-ppnt-sync
```

### Test 2: Create Topic ✅
```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --command-config /tmp/client.properties \
  --create --topic oran-api-test --partitions 1 --replication-factor 1
```
**Actual Response**: `Created topic oran-api-test.`

### Test 3: Produce Message ✅
```
echo '{"event":"test","value":42,"ts":"2026-02-11T14:20:00Z"}' | \
  bin/kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --producer.config /tmp/client.properties --topic oran-api-test
```
**Result**: Message sent successfully

### Test 4: Consume Message ✅
```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --consumer.config /tmp/client.properties --topic oran-api-test \
  --from-beginning --max-messages 1
```
**Actual Response**:
```json
{"event":"test","value":42,"ts":"2026-02-11T14:20:00Z"}
```

### Test 5: VES Topic Subscribe ✅
```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --consumer.config /tmp/client.properties \
  --topic unauthenticated.SEC_HEARTBEAT_OUTPUT --from-beginning --max-messages 1
```
**Result**: Subscription successful, no new messages (expected — no active VES producers)

### Cleanup ✅
```
Deleted test topic: oran-api-test
```

---

## 4. SDNR RESTCONF — 6/7 PASSED (1 expected failure)

**Script**: `test_sdnr.py`  
**Endpoint**: `http://hpe15.anuket.iol.unh.edu:30267`  
**Auth**: Basic Auth `admin` / `Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U`

### Test 1: Get Topology ✅
```
GET /rests/data/network-topology:network-topology
```
**Actual Response** (3 NETCONF nodes):
```
Topology 'topology-netconf':
  → o-du-pynts-1122:  connected (10.244.72.210:830)
  → o-du:             connected (hpe15.anuket.iol.unh.edu:31654)
  → o-du-pynts-1123:  connected (10.244.72.209:830)
```

### Test 2: List Nodes ✅
```
GET /rests/data/network-topology:network-topology/topology=topology-netconf
```
**Result**: 3 connected nodes found

### Test 3: Read Device Config ✅
```
GET /rests/data/network-topology:network-topology/topology=topology-netconf/node=o-du-pynts-1122
```
**Actual Response**: Node `o-du-pynts-1122` — 154 NETCONF capabilities loaded

### Test 4: Read YANG Config (mount point) ❌
```
GET /rests/data/network-topology:network-topology/topology=topology-netconf/node=o-du-pynts-1122/yang-ext:mount/o-ran-sc-du-hello-world:network-function
```
**Actual Response**: HTTP 400  
**Reason**: The pynts simulator nodes don't have the `o-ran-sc-du-hello-world` YANG model. This is an **expected failure** — only the `o-du` node (E2 simulator) has this model.

### Test 5: Mount Test Device ✅
```
PUT /rests/data/network-topology:network-topology/topology=topology-netconf/node=test-api-device-1
```
**Request Body**:
```json
{
  "network-topology:node": [{
    "node-id": "test-api-device-1",
    "netconf-node-topology:host": "10.0.0.99",
    "netconf-node-topology:port": 830,
    "netconf-node-topology:username": "admin",
    "netconf-node-topology:password": "admin",
    "netconf-node-topology:tcp-only": false,
    "netconf-node-topology:keepalive-delay": 120
  }]
}
```
**Actual Response**: HTTP 201 — Mounted `test-api-device-1`

### Test 6: Verify Mounted Device ✅
```
GET /rests/data/network-topology:network-topology/topology=topology-netconf/node=test-api-device-1
```
**Actual Response**: `test-api-device-1` visible, status: `connecting` (10.0.0.99 is a fake IP — expected)

### Test 7: Unmount Test Device ✅
```
DELETE /rests/data/network-topology:network-topology/topology=topology-netconf/node=test-api-device-1
```
**Actual Response**: HTTP 204 — Cleaned up `test-api-device-1`

---

## Credentials Quick Reference

| Service | Endpoint | Auth | Credentials |
|---------|----------|------|-------------|
| InfluxDB | hpe15:31814 | Token Header | `Token xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ` |
| InfluxDB | hpe15:31814 | Web Login | `admin` / `mySuP3rS3cr3tT0keN` |
| MinIO S3 | hpe15:9000 (port-fwd) | S3 Access/Secret | `admin` / `adminadmin` |
| MinIO Console | hpe15:32208 | Web Login | `admin` / `adminadmin` |
| Kafka | kubectl exec | SCRAM-SHA-512 | `strimzi-kafka-admin` / `NCgQTlFIoaJijnVv5dZ5MQwM8ci99KAc` |
| SDNR API | hpe15:30267 | Basic Auth | `admin` / `Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U` |
| SDNR Web | hpe15:30205 | Web Login | same as API |
| Redpanda Console | hpe15:31504 | None | — |

---

## How to Re-run Tests

```bash
cd /home/agnik/Desktop/deployoran/apitest

# Activate venv (already created)
source .venv/bin/activate

# Prerequisite: MinIO port-forward (run on hpe15 once)
ssh agnikmisra@hpe15.anuket.iol.unh.edu
  sudo kubectl --kubeconfig /etc/kubernetes/admin.conf \
    port-forward -n smo svc/minio 9000:9000 --address=0.0.0.0 &

# Run individual tests
MINIO_ENDPOINT="hpe15.anuket.iol.unh.edu:9000" python test_minio.py
python test_influxdb.py
python test_sdnr.py
python test_kafka.py   # Runs via SSH → kubectl exec
```
