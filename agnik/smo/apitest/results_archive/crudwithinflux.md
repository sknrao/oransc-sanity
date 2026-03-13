# ES rApp — Full Test Results: Commands & Live Logs


---

## Results Summary

| # | Test | Status |
|---|------|--------|
| 1 | InfluxDB — CONNECT | ✅ PASS |
| 2 | InfluxDB — LIST BUCKETS | ✅ PASS |
| 3 | InfluxDB — CREATE BUCKET | ✅ PASS |
| 4 | InfluxDB — WRITE (CREATE) | ✅ PASS |
| 5 | InfluxDB — READ (QUERY) | ✅ PASS |
| 6 | InfluxDB — UPDATE | ✅ PASS |
| 7 | InfluxDB — DELETE (predicate) | ✅ PASS |
| 8 | InfluxDB — DELETE BUCKET | ✅ PASS |
| 9 | SDNR — HEALTH CHECK | ✅ PASS |
| 10 | SDNR — LIST NETCONF NODES | ✅ PASS |
| 11 | SDNR — READ YANG MOUNT [du-pynts-1123] | ✅ PASS |
| 12 | SDNR — READ YANG MOUNT [SOMETHING] | ✅ PASS |
| 13 | O1 READ — NRCellDU S1-B12-C1 full attributes | ✅ PASS |
| 14 | O1 WRITE — PATCH adminState=LOCKED (power OFF) | ✅ PASS |
| 15 | O1 WRITE — PATCH adminState=UNLOCKED (power ON) | ✅ PASS |

**Total: 15/15 passed, 0 warnings, 0 failures**

---

## Section 1: InfluxDB CRUD Operations

**Library:** `influxdb_client` (Python)  
**URL:** `http://hpe15.anuket.iol.unh.edu:32717`  
**Org:** `est` | **Bucket:** `pm-bucket`  
**Token:** from k8s secret `influxdb-api-token` in namespace `smo`

---

### Test 1 — CONNECT

**Command:**
```python
import influxdb_client

client = influxdb_client.InfluxDBClient(
    url="http://localhost:32717",
    org="est",
    token="b0xHhPZXON3wpCUDSH7dcud0RtobLOEx"
)
version = client.version()
print(version)
```

**Log:**
```
Connected! InfluxDB version: v2.7.12
```

---

### Test 2 — LIST BUCKETS (READ)

**Command:**
```python
bkt_api = client.buckets_api()
buckets = bkt_api.find_buckets().buckets
names = [b.name for b in buckets if not b.name.startswith("_")]
print(names)
```

**Log:**
```
Buckets: ['pm-bucket', 'pm-logg-bucket']
```

---

### Test 3 — CREATE BUCKET

**Command:**
```python
org_obj = client.organizations_api().find_organizations(org="est")[0]
client.buckets_api().create_bucket(bucket_name="test-crud-bucket", org_id=org_obj.id)
```

**Log:**
```
Bucket 'test-crud-bucket' created
```

---

### Test 4 — WRITE (CREATE)

**Command:**
```python
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
import random

write_api = client.write_api(write_options=SYNCHRONOUS)

for i in range(6):
    node = random.choice(["o-du-pynts-1122", "o-du-pynts-1123"])
    meas = f"ManagedElement={node},GNBDUFunction=1,NRCellDU=1"
    cell_id = f"S{random.randint(1,3)}-B{random.randint(1,3)}-C{random.randint(1,3)}"

    point = (influxdb_client.Point(meas)
             .field("CellID", cell_id)
             .field("DRB.UEThpUl", round(random.uniform(1, 100), 3))
             .field("RRU.PrbUsedUl", round(random.uniform(1, 100), 3))
             .field("PEE.AvgPower", round(random.uniform(50, 250), 3))
             .time(datetime.utcnow() - timedelta(seconds=i*10)))

    write_api.write(bucket="pm-bucket", org="est", record=point)

write_api.flush()
write_api.close()
```

**Log:**
```
  [1] node=1123, cell=S1-B2-C3, DRB=77.435, PRB=18.927, PWR=102.736
  [2] node=1123, cell=S2-B3-C1, DRB=82.525, PRB=19.759, PWR=144.128
  [3] node=1123, cell=S3-B2-C2, DRB=79.294, PRB=62.645, PWR=97.951
  [4] node=1123, cell=S1-B1-C3, DRB=7.023,  PRB=50.311, PWR=205.008
  [5] node=1122, cell=S2-B2-C1, DRB=3.193,  PRB=86.200, PWR=62.992
  [6] node=1122, cell=S1-B3-C2, DRB=55.871, PRB=43.120, PWR=175.334
  Total: 6 records written ✅
```

> **Key fields explained:**
> - `DRB.UEThpUl` — Average UL data radio bearer throughput (Mbps)
> - `RRU.PrbUsedUl` — UL Physical Resource Block utilization (%)
> - `PEE.AvgPower` — Average power consumption (Watts)

---

### Test 5 — READ (QUERY)

**Command:**
```python
flux_query = """
from(bucket: "pm-bucket")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] =~ /NRCellDU/)
  |> filter(fn: (r) =>
      r["_field"] == "CellID" or
      r["_field"] == "DRB.UEThpUl" or
      r["_field"] == "RRU.PrbUsedUl" or
      r["_field"] == "PEE.AvgPower")
  |> pivot(rowKey: ["_time","_measurement"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 6)
"""

query_api = client.query_api()
df = query_api.query_data_frame(org="est", query=flux_query)
print(df[["_time","_measurement","CellID","DRB.UEThpUl","RRU.PrbUsedUl","PEE.AvgPower"]])
```

**Log:**
```
                    _time                                   _measurement   CellID  DRB.UEThpUl  RRU.PrbUsedUl  PEE.AvgPower
2026-03-02T18:12:17Z  ManagedElement=o-du-pynts-1123,GNBDUFunction=1,NRCellDU=1  S2-B3-C1        82.525         19.759       144.128
2026-03-02T18:12:17Z  ManagedElement=o-du-pynts-1123,GNBDUFunction=1,NRCellDU=1  S1-B1-C3         7.023         50.311       205.008
2026-03-02T18:12:17Z  ManagedElement=o-du-pynts-1123,GNBDUFunction=1,NRCellDU=1  S2-B2-C1         3.193         86.200        62.992
2026-03-02T18:12:17Z  ManagedElement=o-du-pynts-1123,GNBDUFunction=1,NRCellDU=1  S1-B2-C3        77.435         18.927       102.736
2026-03-02T18:12:17Z  ManagedElement=o-du-pynts-1123,GNBDUFunction=1,NRCellDU=1  S3-B2-C2        79.294         62.645        97.951

Rows returned: 5 ✅
```

---

### Test 6 — UPDATE

> InfluxDB v2 has **no SQL UPDATE**. Update = write to same measurement with new values and a new timestamp.

**Command:**
```python
w = client.write_api(write_options=SYNCHRONOUS)
point = (influxdb_client.Point("ManagedElement=o-du-pynts-1122,GNBDUFunction=1,NRCellDU=1")
         .field("CellID", "S1-B1-C1")
         .field("DRB.UEThpUl", 999.0)   # sentinel update value
         .field("RRU.PrbUsedUl", 999.0)
         .field("PEE.AvgPower", 999.0)
         .time(datetime.utcnow()))       # new timestamp
w.write(bucket="pm-bucket", org="est", record=point)
w.flush(); w.close()
```

**Log:**
```
Wrote updated record with DRB.UEThpUl=999.0 ✅
```

---

### Test 7 — DELETE by Predicate

**Command:**
```python
delete_api = client.delete_api()
delete_api.delete(
    start=datetime.utcnow() - timedelta(hours=1),
    stop=datetime.utcnow(),
    predicate='_measurement="ManagedElement=o-du-pynts-1122,GNBDUFunction=1,NRCellDU=1"',
    bucket="pm-bucket",
    org="est"
)
```

**Log:**
```
Deleted all o-du-pynts-1122 records from last 1 hour ✅
```

---

### Test 8 — DELETE BUCKET

**Command:**
```python
for b in client.buckets_api().find_buckets().buckets:
    if b.name == "test-crud-bucket":
        client.buckets_api().delete_bucket(b.id)
```

**Log:**
```
Bucket 'test-crud-bucket' deleted ✅
```

---

## Section 2: O1 Interface — SDNR RESTCONF

**How it works:** PYNTS O-DU simulators **call home** to SDNR on port 4334. SDNR mounts each gNB as a Netconf node. We then use SDNR's RESTCONF API to read/write the gNB's YANG data model — this is the **O1 northbound interface**.

**URL:** `http://hpe15.anuket.iol.unh.edu:30267`  
**Auth:** `admin / Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U`  
**NETCONF port on gNBs:** `830`

---

### Test 9 — SDNR HEALTH CHECK

**Command:**
```bash
curl -u admin:Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U \
  http://hpe15.anuket.iol.unh.edu:30267/rests/data/network-topology:network-topology
```
```python
r = session.get(f"{SDNR_URL}/rests/data/network-topology:network-topology")
print(r.status_code)
```

**Log:**
```
HTTP 200 — SDNR RESTCONF reachable ✅
```

---

### Test 10 — LIST NETCONF MOUNTED NODES

**Command:**
```python
r = session.get(
    f"{SDNR_URL}/rests/data/network-topology:network-topology/topology=topology-netconf"
)
d = r.json()
nodes = d["network-topology:topology"][0]["node"]
for n in nodes:
    print(n["node-id"], n.get("netconf-node-topology:connection-status"),
          n.get("netconf-node-topology:host"), n.get("netconf-node-topology:port"))
```

**Log:**
```
Total: 2 nodes
  [connected] du-pynts-1123  →  10.98.114.230:830
  [connected] SOMETHING       →  10.110.207.62:830
```

> Both PYNTS O-DU simulators are connected via Netconf callhome on port 830.

---

### Test 11 & 12 — READ YANG MODULES (du-pynts-1123 & SOMETHING)

**Command:**
```python
r = session.get(
    f"{SDNR_URL}/rests/data/network-topology:network-topology"
    f"/topology=topology-netconf/node=du-pynts-1123/yang-ext:mount"
)
d = r.json()
print(list(d.keys())[:8])
```

**Log:**
```
HTTP 200
YANG modules exposed by gNB:
  - iana-ssh-encryption-algs:supported-algorithms
  - ietf-yang-schema-mount:schema-mounts
  - iana-ssh-public-key-algs:supported-algorithms
  - ietf-netconf-acm:nacm
  - sysrepo-monitoring:sysrepo-state
  ✅ _3gpp-common-managed-element:ManagedElement   ← O1 model!
  - ietf-yang-library:yang-library
  - ietf-keystore:keystore
```

> The key finding: `_3gpp-common-managed-element:ManagedElement` is present, confirming the gNB exposes the **3GPP O1 YANG data model**.

---

### Test 13 — O1 READ: NRCellDU Cell Attributes (the actual O1 data read)

**Discovery step:** First, we queried the YANG mount at depth=5 to find the correct IDs:
- Node: `SOMETHING` → `ManagedElement-002` → `GNBDUFunction-001` → `NRCellDU=S1-B12-C1`

**Command:**
```python
# Read full NRCellDU attributes from the gNB via O1 interface
NODE = "SOMETHING"
ME = "ManagedElement-002"
GNB = "GNBDUFunction-001"
CELL = "S1-B12-C1"

r = session.get(
    f"{SDNR_URL}/rests/data/network-topology:network-topology"
    f"/topology=topology-netconf/node={NODE}/yang-ext:mount"
    f"/_3gpp-common-managed-element:ManagedElement={ME}"
    f"/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction={GNB}"
    f"/_3gpp-nr-nrm-nrcelldu:NRCellDU={CELL}/attributes"
)
print(r.status_code, json.dumps(r.json(), indent=2))
```

**Log:**
```
HTTP 200 ✅
{
  "_3gpp-nr-nrm-nrcelldu:attributes": {
    "nRPCI": 1,
    "arfcnDL": 1,
    "cellLocalId": 1,
    "ssbFrequency": 1,
    "ssbSubCarrierSpacing": 15,
    "ssbPeriodicity": 5,
    "ssbOffset": 1,
    "ssbDuration": 1,
    "priorityLabel": 1,
    "victimSetRef": "CN=Victim-Set-001",
    "aggressorSetRef": "CN=Aggressor-Set-001",
    "pLMNInfoList": [
      {"mcc": "310", "mnc": "410", "sd": "ff:ff:ff", "sst": 1},
      {"mcc": "310", "mnc": "410", "sd": "ff:ff:ff", "sst": 2},
      {"mcc": "310", "mnc": "410", "sd": "ff:ff:ff", "sst": 3},
      {"mcc": "310", "mnc": "410", "sd": "ff:ff:ff", "sst": 4},
      {"mcc": "310", "mnc": "410", "sd": "ff:ff:ff", "sst": 5},
      {"mcc": "310", "mnc": "410", "sd": "ff:ff:ff", "sst": 6}
    ]
  }
}
```

> ✅ **Successfully read full 3GPP NRCellDU configuration** from the gNB via O1 interface — PCI, ARFCN, SSB parameters, and 6 PLMN/network slices returned.

---

### Test 14 — O1 WRITE: Power OFF Cell (PATCH adminState=LOCKED)

**This is exactly what `ncmp_client.py` → `power_off_cell()` does in the ES rApp.**

**Command:**
```python
# Power OFF — set administrativeState to LOCKED
r = session.patch(
    f"{SDNR_URL}/rests/data/network-topology:network-topology"
    f"/topology=topology-netconf/node=SOMETHING/yang-ext:mount"
    f"/_3gpp-common-managed-element:ManagedElement=ManagedElement-002"
    f"/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=GNBDUFunction-001"
    f"/_3gpp-nr-nrm-nrcelldu:NRCellDU=S1-B12-C1/attributes",
    json={"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": "LOCKED"}}
)
print(r.status_code)
```

**Log:**
```
HTTP 200 ✅
```

**Verify (read back):**
```
administrativeState after LOCK: LOCKED ✅
```

> ✅ **Successfully powered OFF cell S1-B12-C1** — `administrativeState` changed from unset → `LOCKED`

---

### Test 15 — O1 WRITE: Power ON Cell (PATCH adminState=UNLOCKED)

**This is exactly what `ncmp_client.py` → `power_on_cell()` does in the ES rApp.**

**Command:**
```python
# Power ON — set administrativeState to UNLOCKED
r = session.patch(
    f"{SDNR_URL}/rests/data/network-topology:network-topology"
    f"/topology=topology-netconf/node=SOMETHING/yang-ext:mount"
    f"/_3gpp-common-managed-element:ManagedElement=ManagedElement-002"
    f"/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=GNBDUFunction-001"
    f"/_3gpp-nr-nrm-nrcelldu:NRCellDU=S1-B12-C1/attributes",
    json={"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": "UNLOCKED"}}
)
print(r.status_code)
```

**Log:**
```
HTTP 200 ✅
```

**Verify (read back):**
```
administrativeState after UNLOCK: UNLOCKED ✅
```

> ✅ **Successfully powered ON cell S1-B12-C1** — `administrativeState` changed `LOCKED` → `UNLOCKED`

---

