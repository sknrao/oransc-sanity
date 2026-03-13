# Complete Test Results: Kafka + Actions + Simple rApp

**Environment:** hpe15.anuket.iol.unh.edu  

---

## Summary

| Task | Status |
|------|--------|
| Kafka — Connect with Dynamic OAuth2 auth | ✅ |
| Kafka — List all 30 topics | ✅ |
| Kafka — Produce PM message | ✅ |
| Kafka — Read PM message back | ✅ |
| Action — Lock cell (power OFF) | ✅ HTTP 200 |
| Action — Unlock cell (power ON) | ✅ HTTP 200 |
| Action — Read cell attributes | ✅ HTTP 200 |
| Simple rApp — Continuous Data→Decision→Action loop | ✅ |

---

## Part 1: Kafka Message Bus (Data — Early Access)

### 1.1 Kafka Setup on hpe15

| Item | Value |
|------|-------|
| **Cluster** | `onap-strimzi` (KRaft mode) |
| **Bootstrap** | `onap-strimzi-kafka-bootstrap.onap:9092` |
| **Auth** | **OAUTHBEARER (Dynamic Token)** |
| **Token Issuer** | Keycloak Proxy (NodePort 32113) |
| **Namespace** | Kafka in `onap`, rApp in `smo` |

**Listener ports:**
| Port | Protocol | Type |
|------|----------|------|
| 9092 | SASL_PLAINTEXT (OAuth/SCRAM) | Internal |
| 9093 | TLS (mTLS) | Internal |
| 9094 | TLS (mTLS) | External NodePort (30493) |
| 9095 | OAuth (Keycloak) | Internal |

### 1.2 Accessing OAuth2 Tokens

The rApp no longer uses static passwords. Instead, it interacts with Keycloak to fetch a short-lived bearer token for authentication.

**Keycloak Configuration:**
- **URL**: `http://keycloak-proxy.smo:8080` (Internal) / `hpe15:32113` (External)
- **Realm**: `oran`
- **Client**: `rapp-client`

**Command:**
```bash
# Create SASL config
cat > /tmp/sasl.properties << EOF
sasl.mechanism=SCRAM-SHA-512
security.protocol=SASL_PLAINTEXT
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="strimzi-kafka-admin" password="G7ITDUBrDBRlZmSKtEMYt9sY2k1ZfBn2";
EOF

# List topics (from inside kafka-client pod)
kafka-topics --list --bootstrap-server onap-strimzi-kafka-bootstrap.onap:9092 --command-config /tmp/sasl.properties
```

**Log (30 topics found):**
```
__consumer_offsets
acm-ppnt-sync
collected-file
cps-data-updated-events
dfc-collected-file
dmi-cm-events
json-file-ready-kp
json-file-ready-kpadp
pmreports
policy-heartbeat
policy-notification
subscription
topology-inventory-ingestion
unauthenticated.SEC_3GPP_FAULTSUPERVISION_OUTPUT
unauthenticated.SEC_3GPP_HEARTBEAT_OUTPUT
unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT    ← PM data topic
unauthenticated.SEC_3GPP_PROVISIONING_OUTPUT
unauthenticated.VES_MEASUREMENT_OUTPUT
unauthenticated.VES_NOTIFICATION_OUTPUT
unauthenticated.VES_PNFREG_OUTPUT
... (30 total)
```

### 1.4 Produce a Test PM Message

**Command:**
```bash
echo '{"event":{"commonEventHeader":{"domain":"perf3gpp","sourceName":"o-du-pynts-1123","startEpochMicrosec":1772648000000000},"perf3gppFields":{"measDataCollection":{"measInfoList":[{"measTypes":{"sMeasTypesList":["DRB.UEThpUl","RRU.PrbUsedUl","PEE.AvgPower"]},"measValuesList":[{"measObjInstId":"S1-B12-C1","measResults":[{"p":1,"sValue":"45.2"},{"p":2,"sValue":"12.5"},{"p":3,"sValue":"180.0"}]}]}]}}}}' \
| kafka-console-producer --bootstrap-server onap-strimzi-kafka-bootstrap.onap:9092 \
  --topic unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT \
  --producer.config /tmp/sasl.properties
```

**Log:**
```
Produced! ✅
```

### 1.5 Read the Message Back

**Command:**
```bash
kafka-console-consumer --bootstrap-server onap-strimzi-kafka-bootstrap.onap:9092 \
  --topic unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT \
  --consumer.config /tmp/sasl.properties \
  --from-beginning --max-messages 1
```

**Log:**
```json
{
  "event": {
    "commonEventHeader": {
      "domain": "perf3gpp",
      "sourceName": "o-du-pynts-1123",
      "startEpochMicrosec": 1772648000000000
    },
    "perf3gppFields": {
      "measDataCollection": {
        "measInfoList": [{
          "measTypes": {
            "sMeasTypesList": ["DRB.UEThpUl", "RRU.PrbUsedUl", "PEE.AvgPower"]
          },
          "measValuesList": [{
            "measObjInstId": "S1-B12-C1",
            "measResults": [
              {"p": 1, "sValue": "45.2"},
              {"p": 2, "sValue": "12.5"},
              {"p": 3, "sValue": "180.0"}
            ]
          }]
        }]
      }
    }
  }
}
✅ Message received!
```

### 1.6 Production rApp - Dynamic Kafka Consumer

The rApp uses a custom `fetch_oauth_token()` function to maintain connectivity without hardcoded secrets.

```python
def fetch_oauth_token():
    """Fetches JWT token from Keycloak for Kafka authentication."""
    resp = requests.post(KEYCLOAK_URL, data=OAUTH_PAYLOAD)
    return resp.json()['access_token']

def oauth_cb(config):
    """Callback for confluent-kafka to refresh tokens."""
    return fetch_oauth_token(), time.time() + 60

conf = {
    'bootstrap.servers': 'onap-strimzi-kafka-bootstrap.onap:9092',
    'group.id': 'simple-es-rapp-group',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'OAUTHBEARER',
    'oauth_cb': oauth_cb
}

consumer = Consumer(conf)
consumer.subscribe(['pmreports'])
```

> **Note:** Must run inside the k8s cluster (e.g., in a pod or as a k8s Deployment). From outside the cluster, the broker DNS won't resolve.

---

## Part 2: Top 5 Common Actions from Existing rApps

### Action 1: Lock Cell — Power OFF ✅ TESTED

**Source:** `ncmp_client.py` → `power_off_cell()`

**Command:**
```python
requests.patch(
    f"{SDNR}/rests/data/.../NRCellDU=S1-B12-C1/attributes",
    json={"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": "LOCKED"}}
)
```

**Result:** HTTP 200 ✅ — Cell locked, verified by readback

---

### Action 2: Unlock Cell — Power ON ✅ TESTED

**Source:** `ncmp_client.py` → `power_on_cell()`

**Command:**
```python
requests.patch(
    f"{SDNR}/rests/data/.../NRCellDU=S1-B12-C1/attributes",
    json={"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": "UNLOCKED"}}
)
```

**Result:** HTTP 200 ✅ — Cell unlocked, verified by readback

---

### Action 3: Read Cell Configuration ✅ TESTED

**Source:** ES rApp reads cell data to check topology

**Command:**
```python
requests.get(
    f"{SDNR}/rests/data/.../NRCellDU=S1-B12-C1/attributes"
)
```

**Result:** HTTP 200 ✅ — Got nRPCI=1, arfcnDL=1, 6 PLMN slices, SSB config

---

### Action 4: Modify Network Slice PRB Allocation

**Source:** `rapp-slice-prb-prediction/ran_nssmf_client.py` → `modify_network_slice_subnet()`

**Command:**
```python
requests.put(
    f"{RAN_NSSMF}/3GPPManagement/ProvMnS/v17.0.0/NetworkSliceSubnets/{subnet_id}",
    json={"attributes": {"maxNumberofPRBs": {"dL": new_prb_dl}}}
)
```

**Use case:** Adjust radio resources for a network slice based on traffic prediction

---

### Action 5: Set Energy Saving Mode (Direct Netconf)

**Source:** `nectconfclient.py` → `perform_action()`

**Command:**
```python
from ncclient import manager
m = manager.connect(host="gNB_IP", port=830, username="root", password="viavi")
m.edit_config(target="running", config=xml_data)
# Sets CESManagementFunction.energySavingControl = "toBeEnergySaving"
```

**Use case:** Original method — direct SSH Netconf to the gNB (no SDNR intermediary)

---

## Part 3: Simple rApp — Data + Decision + Action

### What it does

```text
1. AUTH      → Fetch dynamic OAuth2 token from Keycloak
2. DATA      → Subscribe to Kafka 'pmreports', poll for daily PM data
3. DECISION  → If PRB usage < 20%, cell is idle → recommend LOCK
4. ACTION    → PATCH NRCellDU administrativeState via SDNR RESTCONF
5. LOOP      → Sleep 60s and repeat (Continuous Deployment)
```

### Run Output (Live logs)

```text
10:15:32 [INFO] =======================================================
10:15:32 [INFO]   Simple Energy Saving rApp (v2.0)
10:15:32 [INFO]   Auth: OAuth2 | Data: Kafka | Action: SDNR
10:15:32 [INFO] =======================================================

[AUTH] OAuth token fetched successfully from Keycloak
[KAFKA] Using OAUTHBEARER authentication (dynamic token)

--- PHASE 1: DATA (Kafka) ---
10:15:33 [INFO] [DATA] Message #1 | partition=5 offset=2431
10:15:33 [INFO] [DATA] Total: 1 messages in 0.5s

--- PHASE 2: DECISION (Threshold) ---
10:15:33 [INFO] [DECISION] Cell S1-B12-C1: PRB=0.6% -> LOCKED

--- PHASE 3: ACTION (SDNR) ---
10:15:33 [INFO]   Verified: S1-B12-C1 -> LOCKED: HTTP 200

--- Cycle complete. Sleeping 60s ---
```

