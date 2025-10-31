# O-RAN Multi-Cluster LCM Architecture  
### Rancher + ArgoCD + O2IMS Solution

---

## 🎯 Objective

To design and implement a **fully automated, O-RAN–compliant Multi-Cluster Lifecycle Management (LCM) Platform** using:
- **Rancher** for Cluster Management  
- **ArgoCD** for Application Delivery (GitOps)  
- **O2IMS** for O-RAN Infrastructure Exposure and Inventory  

This architecture enables complete control of multiple **Edge Clusters** running RAN workloads, managed centrally from a **Management Cluster**.

---

## 🏗️ High-Level Overview

The architecture is divided into three main zones:

1. **Management Cluster (LCM Platform)**  
   - Hosts Rancher, ArgoCD, O2IMS, SMO, Non-RT RIC, and OAM.
2. **Edge Clusters (RAN Deployments)**  
   - Run Near-RT RIC, CU, DU, and RU components.
3. **External Interfaces & Systems**  
   - CI/CD, and standard O-RAN interfaces (O1, O2, A1).

Each zone plays a critical role in automating, observing, and orchestrating the RAN stack.

---

## 🧩 Management Cluster Components

### 🟣 Rancher
**Role:** Multi-Cluster Manager  
**Functions:**
- Cluster provisioning and registration  
- Role-Based Access Control (RBAC) and authentication  
- Centralized monitoring for all clusters  
- Interface for cluster operations  

Rancher integrates directly with **O2IMS** to provide cluster inventory and lifecycle state data.

---

### 🟣 ArgoCD
**Role:** GitOps Engine for Continuous Delivery  
**Functions:**
- ApplicationSets for deploying workloads across multiple clusters  
- Automatic synchronization between Git and cluster state  
- Rollback and drift detection  
- Policy-based deployments for O-RAN stacks  

ArgoCD continuously pulls manifests from the **Git Repository** and applies them to registered clusters.

---

### 🟣 Git Repository
**Role:** Source of Truth  
**Contains:**
- O-RAN Helm charts and Kubernetes manifests  
- Configuration for CU/DU/RU workloads  
- ArgoCD ApplicationSet definitions  

It drives all configuration and deployment workflows in a declarative, version-controlled manner.

---

### 🟣 O2IMS
**Role:** O-RAN Infrastructure Management Service  
**Functions:**
- Provides the **O2 interface** between the SMO and the infrastructure (Rancher)  
- Implements **DMS** (Deployment Management Service) and **IMS** (Infrastructure Management Service) APIs  
- Exposes cluster inventory, status, and deployment endpoints to SMO  
- Enables the SMO to query infrastructure readiness and lifecycle states  

Essentially acts as the **adapter** connecting SMO to Rancher, removing the need for any external adapter.

---

### 🟢 SMO (Service Management and Orchestration)
**Role:** Core orchestrator for O-RAN workloads  
**Functions:**
- Policy and service orchestration  
- RAN lifecycle management through ArgoCD and O2IMS APIs  
- Dashboarding and topology management  
- Integration point for Non-RT RIC and OAM  

The SMO consumes O2IMS APIs to manage infrastructure and uses A1/O1 interfaces for RAN control.

---

### 🟢 Non-RT RIC
**Role:** Policy Optimization and AI/ML Training  
**Functions:**
- Generates rApps and A1 policies for the Near-RT RIC  
- Performs long-term policy optimization  
- Enables Non-Real-Time (Non-RT) control loops (>1s latency)  

It communicates via the **A1 interface** with the Near-RT RICs in the edge clusters.

---

### 🟢 OAM (Operations, Administration, and Maintenance)
**Role:** O1 Interface and FCAPS Management  
**Functions:**
- Fault, Configuration, Accounting, Performance, and Security management (FCAPS)  
- Provides telemetry and control over RAN components  
- Uses O1 interface to connect to O-RU, O-DU, O-CU components  

---

## 🟠 Edge Clusters

Each Edge Cluster hosts the actual **RAN components** and associated **Near-RT RIC**.  
They are fully managed and updated via **ArgoCD** from the Management Cluster.

### 🟢 Near-RT RIC
**Role:** Real-Time RAN Controller (<10ms loop)  
**Functions:**
- Runs xApps for traffic steering, QoS, and scheduling  
- Manages E2 termination for real-time control  
- Communicates with Non-RT RIC through **A1 interface**  
- Communicates with CU/DU/RU through **E2 interface**

---

### 🟢 O-CU (Control Plane & User Plane)
**O-CU-CP**
- Handles RRC and PDCP-C layers  
**O-CU-UP**
- Handles PDCP-U and SDAP layers  

---

### 🟢 O-DU (Distributed Unit)
- Implements MAC, RLC, and High-PHY layers  
- Interfaces with the O-RU over the fronthaul  
- Managed via O1 from OAM and E2 from Near-RT RIC  

---

### 🟢 O-RU (Radio Unit)
- Handles Low-PHY and RF functions  
- Exposed via O1 interface to OAM  

---

### 🟢 O-RAN Stack Deployment
All edge RAN components are deployed through **ArgoCD ApplicationSets**, enabling:
- Parallel, declarative deployment  
- Centralized GitOps-driven updates  
- Consistent environment provisioning across clusters  

---

## 🌐 External Systems & Interfaces

| Interface | Role | Connected Components |
|------------|------|----------------------|
| **O1** | Configuration & FCAPS Mgmt | OAM ↔ O-DU/O-RU |
| **O2** | Infrastructure Mgmt | O2IMS ↔ SMO |
| **A1** | Policy Control | Non-RT RIC ↔ Near-RT RIC |
| **E2** | Real-Time RAN Control | Near-RT RIC ↔ RAN Stack |

---

### 🔍 Observability Stack
- **Prometheus** – Metrics collection  
- **Grafana** – Visual dashboards  
- **Alertmanager** – Alerting rules and thresholds  

---

### ⚙️ CI/CD Pipeline
- **GitHub/GitLab** for source control and workflow automation  
- **Automated testing** pipelines for validation  
- **Image registry** for storing container images  

---

## 🧭 Deployment Phases

### **Phase 1: LCM Platform**
Deploy and integrate all management components:
- Rancher  
- ArgoCD  
- O2IMS  
- SMO, Non-RT RIC, OAM  

### **Phase 2: O-RAN Deploy**
- Register Edge Clusters via Rancher  
- Deploy Near-RT RIC, CU, DU, RU workloads via ArgoCD  
- Validate O1/A1/E2 interfaces  
- Test O2IMS exposure to SMO  

---

## 🔑 Key Benefits

- **End-to-End Automation** from infrastructure to workloads  
- **Open and Modular** (no vendor lock-in)  
- **GitOps-driven Consistency** across multiple clusters  
- **O-RAN Compliant** interfaces (O1, O2, A1, E2)  
- **Scalable & Extensible** for production-grade 5G/6G deployments  

---

## 🏁 Conclusion

This architecture successfully achieves a **complete O-RAN Multi-Cluster LCM solution** using only open-source components.  
It supports full lifecycle automation, observability, and standards-based interoperability — ideal for both research and real-world telecom environments.

