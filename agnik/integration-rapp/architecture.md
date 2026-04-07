# O-RAN Integration rApp: Technical Architecture

This document provides a detailed technical overview of the Integration rApp's internal architecture, component interactions, and data flows within the O-RAN Service Management and Orchestration (SMO) layer.

---

## 1. System Topology

The Integration rApp serves as a centralized gateway for O-RAN SMO verification. It is deployed as a Kubernetes-native service within the `smo` namespace, utilizing internal ClusterIP DNS for all southbound communication.

```mermaid
flowchart TB
    classDef smo fill:#1e40af,stroke:#60a5fa,stroke-width:2px,color:#fff
    classDef app fill:#059669,stroke:#34d399,stroke-width:2px,color:#fff
    classDef edge fill:#7c2d12,stroke:#fcd34d,stroke-width:2px,color:#fff
    classDef db fill:#9333ea,stroke:#f472b6,stroke-width:2px,color:#fff

    User((Web GUI / CLI))

    subgraph "SMO / Non-RT-RIC (Kubernetes Fabric)"
        direction TB
        RAPP["Integration rApp Pod (Flask)"]:::app

        subgraph "Non-RT RIC Services"
            A1PMS["A1PMS (Policy Mgmt)"]:::smo
        end

        subgraph "OAM & Data Services"
            SDNR["SDNR (RESTCONF Interface)"]:::smo
            Kafka["Strimzi Kafka Broker"]:::db
            MinIO["MinIO (S3 Object Store)"]:::db
            Influx["InfluxDB (TSDB)"]:::db
        end
    end

    subgraph "RAN Infrastructure"
        NearRIC["Near-RT RIC"]:::edge
        PNF["O-DU/O-RU Simulators"]:::edge
    end

    User -- "HTTP :5001" --> RAPP

    %% Southbound Logic
    RAPP -- "REST (/a1-policy)" --> A1PMS
    RAPP -- "RESTCONF" --> SDNR
    RAPP -- "S3 API" --> MinIO
    RAPP -- "Flux/HTTP" --> Influx
    RAPP -- "Native (9092/9093)" --> Kafka

    %% External Control
    A1PMS -. "A1-P" .-> NearRIC
    SDNR -. "NETCONF" .-> PNF
```

---

## 2. Feature Data Flows

### A. SDNR: Node Inventory & Topology
Retrieves the real-time status of all registered NETCONF nodes (O-DUs/O-RUs) from the SDNR inventory.

**API Endpoint:** `GET /api/nodes`  
**Internal Path:** `.../network-topology:network-topology/topology=topology-netconf`

```mermaid
sequenceDiagram
    participant UI as Browser/CLI
    participant App as Integration rApp
    participant SDNR as SDNR (ODL)

    UI->>App: GET /api/nodes
    App->>SDNR: GET /rests/data/network-topology:network-topology
    Note right of SDNR: Polls topology-netconf database
    SDNR->>App: JSON Node List (host, port, status)
    App->>UI: 200 OK (Structured Node Table)
```

### B. SDNR: Cell Administration (LOCK/UNLOCK)
Automates the lifecycle management of NRCellDU entities via RESTCONF PATCH operations.

**API Endpoint:** `POST /api/nodes/<cell>/reset`

```mermaid
sequenceDiagram
    participant UI as Browser/CLI
    participant App as Integration rApp
    participant SDNR as SDNR (RESTCONF)
    participant ODU as O-DU (SIM)

    UI->>App: POST /api/nodes/Cell-01/reset
    App->>SDNR: GET .../NRCellDU=Cell-01/attributes
    SDNR->>App: administrativeState: UNLOCKED
    
    rect rgb(200, 230, 255)
    Note over App, ODU: Phase 1: Locking Cell
    App->>SDNR: PATCH {administrativeState: LOCKED}
    SDNR-->>ODU: NETCONF edit-config (LOCKED)
    SDNR->>App: 200 OK
    end
    
    rect rgb(200, 255, 230)
    Note over App, ODU: Phase 2: Unlocking Cell
    App->>SDNR: PATCH {administrativeState: UNLOCKED}
    SDNR-->>ODU: NETCONF edit-config (UNLOCKED)
    SDNR->>App: 200 OK
    end
    
    App->>UI: {status: "success", final_state: "UNLOCKED"}
```

### C. Kafka: Native PM Data Consumption
Utilizes a native `kafka-python` consumer to verify performance management (PM) data packets on the internal message bus.

**API Endpoint:** `GET /api/kafka/topics/<name>/latest`

```mermaid
sequenceDiagram
    participant UI as User
    participant App as Integration rApp
    participant K8s as K8s DNS
    participant Kafka as Kafka Broker

    UI->>App: GET /api/kafka/topics/pmreports/latest
    App->>K8s: Resolve onap-strimzi-kafka-bootstrap
    K8s->>App: Port 9092 (Plain) / 9093 (SCRAM)
    
    rect rgb(230, 230, 250)
    Note over App, Kafka: SASL/SCRAM Handshake (if 9093)
    App->>Kafka: Authenticate (dcae-ves-collector-ku)
    end

    App->>Kafka: Create Consumer (topic: pmreports)
    App->>Kafka: SeekToEnd() & Fetch(Offset-1)
    Kafka->>App: Latest PM event (JSON)
    
    App->>UI: 200 OK (JSON Payload)
```

### D. MinIO: PM Persistence Audit (S3)
Scans MinIO buckets for both legacy XML and modern compressed JSON (`.json.gz`) PM logs.

**API Endpoint:** `GET /api/minio/files`

```mermaid
sequenceDiagram
    participant UI as Dashboard
    participant App as Integration rApp
    participant S3 as MinIO (S3 API)

    UI->>App: GET /api/minio/files
    App->>S3: list_buckets()
    S3->>App: [bucket1, bucket2, ...]
    
    loop For each Bucket
        App->>S3: list_objects_v2(prefix="")
        S3->>App: [A1.xml, B2.json.gz, ...]
        App->>App: Regex Classification (.xml vs .json.gz)
    end
    
    App->>UI: 200 OK (Categorized metrics)
```

### E. A1PMS: Policy Management Lifecycle
Orchestrates the deployment and verification of intent-based policies via the Non-RT RIC.

**API Endpoint:** `POST /api/policy`

```mermaid
sequenceDiagram
    participant UI as Web GUI
    participant App as Integration rApp
    participant A1 as A1PMS (Non-RT RIC)
    participant RIC as Near-RT RIC

    UI->>App: POST /api/policy (Trigger Test)
    App->>A1: GET /a1-policy/v2/rics (Discovery)
    A1->>App: [hpe1122-ric]
    
    App->>A1: PUT /a1-policy/v2/policies/test-id (Type: 20000)
    Note right of A1: Dispatches via A1-P interface
    A1-->>RIC: Policy Data (JSON Intent)
    RIC-->>A1: 201 Created
    A1->>App: 201 Created
    
    App->>UI: 201 Created (Policy Deployed)
```

---
*Production Documentation • O-RAN Integration rApp • v2.1*
