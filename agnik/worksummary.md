# LFX Internship — Final Summary & Handoff

**Intern**: Agnik Misra  
**Program**: Linux Foundation Mentorship (LFX) — O-RAN SC Pre-Release Quality Checks  
**Repository**: [`oransc-sanity/agnik`](https://github.com/sknrao/oransc-sanity/tree/main/agnik)  
**Lab Environment**: HPE15 (SMO) + HPE16 (Near-RT RIC) at Anuket IOL, UNH  

---

## Part 1: Comprehensive Summary Table of All Work


### A. Pre-Release Quality Automation (T01, T03, T04)

| # | Task | Activity | What I Built / Did | Key Numbers | Result / Outcome |
|---|------|----------|---------------------|-------------|------------------|
| 1 | T01 | Dockerfile build testing automation | Built `dockerfile_build_checker.py` (507 lines Python) — scrapes GitHub API for all O-RAN SC repos, clones each, finds every Dockerfile variant, runs `docker build`, logs results, generates summary | **90+ repos** tested, **151 repo logs**, **45 per-repo build reports** | ✅ Complete — Fully automated, reusable for each release |
| 2 | T01 | Fix broken Dockerfiles | Identified failing Dockerfiles and patched them — deprecated base images, missing dependencies, wrong COPY paths, Go module issues | **19 repos fixed** — patches in `FixedDocker/` | ✅ 19 patches ready for upstream |
| 3 | T03 | Repository metadata analysis automation | Built `fetch_repos.py` (633 lines Python) — GitHub API analyzer for branches, tags, releases, naming patterns, with 12-week improvement roadmap | **77 repos** analyzed, **97 KB** report generated | ✅ Complete |
| 4 | T03 | Key findings from repo analysis | Discovered: all repos use `master` (not `main`), zero GitHub Releases, 19 repos with no tags, inconsistent naming | Standardization roadmap with priorities produced | ✅ Findings documented |
| 5 | T04 | Release notes coverage matrix | Built matrix of **117 repos × 12 releases** (Amber through L-release) checking release note existence | **117 repos** mapped | ✅ Complete |
| 6 | T04 | Missing release notes cross-reference analysis | Cross-referenced T03 branch data with T04 release notes — flagged repos with branches but no corresponding notes | **80 repos** with gaps (out of 95 with branches), only **16 fully covered** | ✅ Complete |

### B. Deployment & Installation Evaluation (T06)

| # | Task | Activity | What I Built / Did | Key Numbers | Result / Outcome |
|---|------|----------|---------------------|-------------|------------------|
| 7 | T06 | Near-RT RIC platform deployment | Built `deploy_ric_platform.sh` (197 lines) — automated 5-step deploy with embedded custom recipe using CVE-fixed images from `mdimado` | Deploys **12+ RIC services** (A1Med, E2Mgr, AppMgr, RtMgr, DBAAS, etc.) | ✅ Deployed on HPE16 |
| 8 | T06 | Near-RT RIC standard installation | Followed official docs, created `deploy_ric_platform_default.sh` and 21 KB updated installation guide | Cross-validated with custom approach | ✅ Deployed |
| 9 | T06 | xApp deployment automation | Built `deploy_all_xapps.sh` (222 lines) — deploys 5 xApps with dynamic service discovery and auto-generated RMR routing tables | **5 xApps**: KPIMON-GO, AD, QP, TS, RC | ✅ All 5 deployed |
| 10 | T06 | Bouncer xApp performance testing | Tested Bouncer xApp, generated comprehensive performance analysis | 32 KB performance report | ✅ Complete |
| 11 | T06 | E2 Simulator deployment | Built `deploy_e2sim_automated.sh` (208 lines) — multi-stage Docker build, auto E2Term IP detection, nerdctl/buildkit fallback | Fixed **3 bugs**: missing JSON header, binary path, image pull | ✅ E2 Sim connected to RIC |
| 12 | T06 | SMO official deployment script | Built `deploy_smo_official.sh` (423 lines) — full prereq check (CPU, RAM, disk), K8s setup, Helm plugins, SMO deploy, verification | Validates: 64GB RAM, 20 CPU, K8s 1.30+, Helm 3.12+ | ✅ Deployed on HPE15 |
| 13 | T06 | SMO simplified deployment | Built `deploy_smo_simple.sh` (6.7 KB) — streamlined version for quick redeployment | 3-step deploy | ✅ Deployed |
| 14 | T06 | SMO deployment variations | Tested 5 deployment variations with named override files for each | 5 variations: ONAP-only, no CPS/TEIV, +O-RAN, +NonRT-RIC only, no A1 controller | ✅ All 5 tested |
| 15 | T06 | SMO M-release deployment guide | Wrote `smodeployemntguide.md` (451 lines) — 7-step guide with verification checks and troubleshooting for 5 common issues | Step-by-step with expected outputs | ✅ Complete |
| 16 | T06 | Near-RT RIC guides | Wrote `ric-removal-and-install.md` (20 KB) and `new-installation-guides(1).md` (21 KB) | Comprehensive removal + reinstall docs | ✅ Complete |
| 17 | T06 | E2 Simulator issues documentation | Wrote `e2sim.md` — documented 3 issues found and authentic fixes applied | 3 issues fixed | ✅ Complete |
| 18 | T06 | RIC ↔ SMO registration | Patched A1 Mediator service to NodePort 30803, ran `register-ric.sh`, verified RIC shows as AVAILABLE in A1PMS | HPE16 registered with HPE15 successfully | ✅ RIC AVAILABLE |
| 19 | T06 | SMO integration documentation | Wrote `SMO_INTEGRATION_COMPLETE_FINAL_REPORT.md` (19 KB) and `UPDATEDSMOINT.md` (5 KB) | Full integration walkthrough | ✅ Complete |
| 20 | T06 | ArgoCD feasibility evaluation | Set up ArgoCD, created parent app manifest, tested deploying SMO — identified `helm deploy` plugin as blocker | Feasibility: ❌ for SMO (works for RIC) | ✅ Evaluated |
| 21 | T06 | Devtron feasibility evaluation | Set up Devtron, tested deployment approach — same `helm deploy` limitation as ArgoCD | Feasibility: ❌ for SMO | ✅ Evaluated |
| 22 | T06 | Ansible automation | Developed Ansible playbooks for K8s setup + SMO deployment roles | Partial automation achieved | ⚠️ Partial |
| 23 | T06 | Helm override experiments | Created and tested multiple Helm override files for different SMO component combinations | Multiple override files maintained | ✅ Complete |
| 24 | T06 | Documented Helm image update procedures | Wrote `helmimageupdate.md` (4.9 KB) | Image override procedures | ✅ Complete |
| 25 | T06 | Documented full OOM deployment | Wrote `fulloom.md` (7 KB) | ONAP Operations Manager guide | ✅ Complete |
| 26 | T06 | Operator error troubleshooting | Debugged and documented operator errors in `OPERATOR_error.md` (5.9 KB) | Troubleshooting notes | ✅ Documented |
| 27 | T06 | Production InfluxDB deployment | Built `deploy-influxdb-production.sh` (6.6 KB) | Production-grade InfluxDB deploy | ✅ Deployed |
| 28 | T06 | Production xApp deployment | Built `deploy-xapps-production.sh` (9.4 KB) | Production xApp configs | ✅ Deployed |

### C. API Evaluation & Testing (T07)

| # | Task | Activity | What I Built / Did | Key Numbers | Result / Outcome |
|---|------|----------|---------------------|-------------|------------------|
| 29 | T07 | O-RAN interface audit | Manually tested **13 interfaces** on HPE15 (SMO) and HPE16 (RIC) — documented every port, credential, endpoint, and observation | **12/13 working**, 1 (Topology) returned 404 | ✅ Complete |
| 30 | T07 | Comprehensive curl-based API tests | Ran extensive curl tests against all O-RAN APIs | `api_curl_test_results.md` (17 KB) + HPE16 results | ✅ All documented |
| 31 | T07 | O-RAN Health Check App (Go) | Built `main.go` (414 lines Go) — single-command health checker testing 5 categories: Kafka, gNBs, Policies, Metrics, 7 Interfaces | Color-coded output with pre-compiled binary | ✅ Complete |
| 32 | T07 | SDNR automated test suite | Built `test_sdnr.py` (259 lines) — 7 RESTCONF tests: topology, nodes, device config, YANG mount, mount/unmount test device | **7 tests** | ✅ Complete |
| 33 | T07 | Kafka automated test suite | Built `test_kafka.py` (154 lines) — 5 tests via SSH→kubectl exec: list, create, produce, consume, VES subscribe (SCRAM-SHA-512 auth) | **5 tests** | ✅ Complete |
| 34 | T07 | InfluxDB automated test suite | Built `test_influxdb.py` (161 lines) — 6 tests: health, buckets, orgs, write data, query data, query PM data | **6 tests** | ✅ Complete |
| 35 | T07 | MinIO automated test suite | Built `test_minio.py` — S3 bucket and file tests | MinIO S3 tests | ✅ Complete |
| 36 | T07 | Test runner orchestrator | Built `run_all_tests.py` — runs all 4 test suites | Runs 22+ tests in sequence | ✅ Complete |
| 37 | T07 | Bruno API collections | Created exported API collections for manual interactive testing | Bruno collections for RIC and SMO | ✅ Complete |
| 38 | T07 | Traffic steering documentation | Documented traffic steering mechanisms | `trafficsteering.md` (40 KB) | ✅ Complete |
| 39 | T07 | xApp deployment documentation | Comprehensive xApp installation guide | `xapp.md` (46 KB) | ✅ Complete |

### D. End-to-End Integration & Automation (T11, T12, T13)

| # | Task | Activity | What I Built / Did | Key Numbers | Result / Outcome |
|---|------|----------|---------------------|-------------|------------------|
| 40 | T12 | **Integration rApp — Backend** | Built `backend.py` (675 lines Flask) — 8 REST APIs connecting SDNR, Kafka, MinIO, InfluxDB, A1PMS, E2Mgr into one tool | **8 endpoints**, integrates **6 O-RAN components** | ✅ Complete |
| 41 | T12 | **Integration rApp — CLI** | Built `cli.py` (221 lines) — 9 terminal commands with ANSI color output | 9 commands | ✅ Complete |
| 42 | T12 | **Integration rApp — Web Dashboard** | Built `templates/index.html` (1204 lines, 42 KB) — production GUI with cards, tree views, JSON highlighting, loading spinners, responsive design | 8 panels, Inter/Fira Code fonts, animated indicators | ✅ Complete |
| 43 | T12 | Integration rApp — K8s deployment | Built `k8s-deployment.yaml` (86 lines) — Deployment + NodePort 31001 in `smo` namespace with ConfigMap-based code delivery | Deploys in `smo` namespace | ✅ Complete |
| 44 | T12 | Integration rApp — Dockerfile | Built `Dockerfile` (30 lines) — python:3.11-slim + kubectl + sshpass | Container-ready | ✅ Complete |
| 45 | T12 | Integration rApp — Kafka helper | Built `kafka_consume.sh` (60 lines) — SASL_SCRAM-SHA-512 auth via kubectl exec | SASL auth consumer | ✅ Complete |
| 46 | T13 | Kafka + Actions + rApp testing | Tested full data pipeline: OAuth2 Kafka connect, list 30 topics, produce/consume PM, lock/unlock cell actions | **8/8 tests** all passing | ✅ All passing |
| 47 | T13 | **Simple Energy Saving rApp** | Built `simple_rapp.py` (11.6 KB) — continuous Data→Decision→Action loop: OAuth2→Kafka consumer→threshold check→SDNR RESTCONF cell lock/unlock | Real PM data, real SDNR actions | ✅ Deployed & working |
| 48 | T13 | RIC registration scripts and guide | Built `register-ric.sh` (3.4 KB) + `config.env` + comprehensive `Readme.md` (34 KB) for cross-server RIC registration | HPE16↔HPE15 integration | ✅ Complete |

### E. Documentation & Organization

| # | Task | Activity | What I Built / Did | Key Numbers | Result / Outcome |
|---|------|----------|---------------------|-------------|------------------|
| 49 | — | End-to-end detailed walkthrough | Wrote `agnikdetailedworkthough.md` — comprehensive folder-by-folder analysis of all work | Full code-level documentation | ✅ Complete |
| 50 | — | Final summary & handoff preparation | This document — summary table + repo walkthrough + Integration rApp overview | 3 deliverables | ✅ Complete |
| 51 | — | Integration rApp technical deep-dive | Separate document: `INTEGRATION_RAPP_DEEPDIVE.md` — every API, data flow, architecture diagram | Full technical reference | ✅ Complete |

### Aggregate Statistics

| Metric | Count |
|--------|-------|
| **Total custom lines of code** | **~5,500+** (Python, Go, Shell, YAML, HTML) |
| **Total activities documented** | **51** |
| **Repositories analyzed (T01 Dockerfiles)** | 90+ |
| **Repositories analyzed (T03 metadata)** | 77 |
| **Repositories analyzed (T04 release notes)** | 117 |
| **Dockerfile patches created** | 19 |
| **O-RAN interfaces audited** | 13 (12 working) |
| **Deployment scripts created** | 8 |
| **Automated test cases written** | 22+ (across 4 test suites) |
| **Custom tools built** | 3 (Go health checker, Integration rApp, ES rApp) |
| **SMO deployment variations tested** | 5 |
| **Alternative deployment approaches evaluated** | 3 (ArgoCD, Devtron, Ansible) |
| **Documentation pages created** | 15+ guides/reports |
| **Total documentation volume** | ~400 KB+ of markdown |

---

## Part 2: Repository Organization

The repo follows the **clean-up structure** defined in the mentor meetings:

```
agnik/
│
├── T1/                          ← Dockerfile Testing & Fixing (T01)
│   ├── dockerfile_build_checker.py
│   ├── dockertable.md
│   ├── FixedDocker/ (19 repos)
│   ├── dockerreports/ (45 files)
│   └── logs/ (151 repo dirs)
│
├── T3/                          ← Repo Analysis (T03)
│   ├── fetch_repos.py
│   └── O-RAN_SC_*.md (97 KB)
│
├── T4/                          ← Release Notes (T04)
│   ├── ReleaseNotes.md
│   └── missingreleasenotes.md
│
├── near-rt-ric/                 ← Near-RT RIC (matches mentor's structure)
│   ├── platform-installation/   ← Platform Install
│   ├── standered-installation/  ← Standard (docs-based) Install
│   ├── xapps-installation/      ← xApps Install
│   ├── integration/             ← Integration (RIC ↔ SMO)
│   └── api-testing-old/         ← API Testing [Dashboard]
│
├── smo/                         ← SMO (matches mentor's structure)
│   ├── standard-installation/   ← Standard Installation
│   ├── argo-installation/       ← Argo Installation
│   ├── devtron-installation/    ← Devtron
│   ├── overrides-experiments/   ← Override Experiments
│   ├── apitest/                 ← API Testing [pytest suite]
│   ├── api-testing/             ← Manual API Testing
│   ├── Kafka+simplerapp/        ← Kafka + Simple Energy Saving rApp
│   └── it-dep/                  ← Local it-dep clone
│
├── e2-simulator/                ← E2 Simulator
│   └── installation/
│
├── api-testing-app/             ← Go Health Check Tool
│
├── integration-rapp/            ← ★ Integration rApp
│
├── T6/t6-ric-dep/              ← Deployment docs, guides, interface audit
│
└── unused/                      ← Archived materials
```


---

## Part 3: Integration rApp — Overview


### What It Is

The Integration rApp is a **unified verification tool** for O-RAN SC deployments. It connects to 6 different O-RAN components — SDNR, Kafka, MinIO, InfluxDB, A1PMS, and E2 Manager — through a single interface, allowing an operator to verify that the entire stack is functioning correctly without running manual `curl` commands against each service.

It provides **three interfaces**: a Web Dashboard (GUI), a CLI, and a REST API — all backed by a Python/Flask backend.

### Why It Was Built

After deploying the SMO on HPE15 and the Near-RT RIC on HPE16, each component has its own API, port, and authentication method. Verifying whether the full O-RAN stack is connected end-to-end requires checking SDNR nodes, Kafka data flow, MinIO file storage, InfluxDB metrics, A1 policy delivery, and E2 node connectivity — all separately. The Integration rApp consolidates these into one tool, making pre-release verification fast and repeatable.

### Architecture


<img width="2444" height="1196" alt="image" src="https://github.com/user-attachments/assets/15c07d94-4eec-43df-8e4f-86e734ed729a" />


### The 6 O-RAN Components It Connects To

| Component | Server | Port | Protocol | Auth | What It Provides |
|-----------|--------|------|----------|------|------------------|
| **SDNR** | HPE15 | 30267 | RESTCONF | Basic Auth | Network device management — O-DU status, cell control |
| **Kafka** | HPE15 | 30385 | REST / SCRAM-SHA-512 | Redpanda Console (REST) or SASL (broker) | Message bus — PM data topics, VES events |
| **MinIO** | HPE15 | 9000 | S3 | Access Key | Object storage — PM files (XML raw, JSON converted) |
| **InfluxDB** | HPE15 | 32717 | Flux Query | Token | Time-series DB — PM metrics for dashboards |
| **A1PMS** | HPE15 | 30094 | REST v2 | None | Policy management — RIC registration, policy delivery |
| **E2 Manager** | HPE16 | 30850 | REST | None | E2 node status — base station connectivity |

### All 8 Features

| # | Feature | API Endpoint | What It Verifies |
|---|---------|-------------|------------------|
| 1 | **List SDNR Nodes** | `GET /api/nodes` | Queries SDNR RESTCONF topology — returns all NETCONF-managed devices with connection status. Proves the O1 interface is working. |
| 2 | **Reset Cell** | `POST /api/nodes/<cell_id>/reset` | Performs a 4-step admin state cycle (READ → LOCK → UNLOCK → VERIFY) on an NRCellDU via SDNR. This is one of the Top 5 rApp actions (Slide 14). Auto-detects the node if not specified. |
| 3 | **List Kafka Topics** | `GET /api/kafka/topics` | Lists all Kafka topics with partition counts and data sizes. Uses Redpanda Console REST API first, falls back to `kubectl exec` with SCRAM-SHA-512 auth. Shows whether the data pipeline is active. |
| 4 | **Read Latest Message** | `GET /api/kafka/topics/<name>/latest` | Retrieves the most recent message from a topic via `kafka_consume.sh` (runs inside the broker pod). Useful for debugging PM data flow. |
| 5 | **Integration Check** | `GET /api/integration-check` | Runs 3 checks: (a) SDNR nodes connected + Kafka `pmreports` has data, (b) A1PMS has registered RICs, (c) E2Mgr has connected E2 nodes. Returns PASS/WARN/FAIL for each. If all 3 pass, the entire O-RAN stack is connected end-to-end. |
| 6 | **MinIO File Inventory** | `GET /api/minio/files` | Connects via S3 SDK, lists buckets and counts XML (raw PM) and JSON (converted PM) files. Verifies steps 2-4 of the RANPM pipeline. |
| 7 | **InfluxDB Bucket Audit** | `GET /api/influxdb/buckets` | Checks InfluxDB health, lists buckets, runs Flux queries to detect recent data in `pm-bucket` and `pm-logg-bucket`. Verifies the final stage of the PM pipeline. |
| 8 | **Send A1 Policy** | `POST /api/policy` | Creates and sends an A1 policy from Non-RT RIC to Near-RT RIC via A1PMS. Auto-discovers RICs and policy types, generates a unique policy ID, sends via PUT, and verifies with GET. |


### Web Dashboard

The GUI is a single-page HTML application (1204 lines, 42 KB) with:
- **8 cards** — one per feature, each with a description, action button, and collapsible result area
- **Formatted tree views** for structured data + raw JSON toggle with syntax highlighting
- **Loading spinners** and animated status indicators
- **Responsive design** — works on desktop and mobile
- **Design**: Inter + Fira Code fonts, light-blue theme, card hover animations

### Deployment Options

| Method | How | Access URL |
|--------|-----|------------|
| **Local** | `python backend.py --port 5001` | `http://localhost:5001` |
| **Kubernetes** | Deployment + NodePort Service via `k8s-deployment.yaml` | `http://hpe15:31001` |
| **Docker** | `docker build -t integration-rapp . && docker run -p 5001:5001 integration-rapp` | `http://localhost:5001` |

The K8s deployment uses a ConfigMap for code delivery and mounts the host kubeconfig for `kubectl exec` access to Kafka.

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Flask** (not FastAPI/Django) | Lightweight; no ORM or async needed — the rApp just makes HTTP calls and returns JSON |
| **Redpanda Console + kubectl exec fallback** for Kafka | Avoids needing Kafka client libraries, TLS certs, and SASL config in the rApp container |
| **Single config.yaml** | All hosts, ports, and credentials in one file — swap it to point at a different deployment |
| **Vanilla HTML** (no React/Vue) | Zero build tooling, runs anywhere, easy to modify |
| **ConfigMap-based K8s deploy** | Code updates don't require rebuilding the Docker image |

### Connection to Internship Tasks

- **T07** (API Evaluation): The rApp is the culmination of all API testing work — every API that was tested manually (curl, Bruno, pytest) is now accessible through one tool
- **T12** (End-to-End O-RAN): The Integration Check feature (Feature 5) is a direct implementation of the end-to-end pre-release check
- **T13** (API Checks): All 8 features serve as automated API checks for pre-release verification

### Companion Document

A full technical deep-dive covering every API's exact HTTP calls, data flows, Mermaid sequence diagrams, and Q&A is available in **`INTEGRATION_RAPP_DEEPDIVE.md`**.

---

*Prepared by Agnik Misra — LFX Mentorship, O-RAN SC Pre-Release Quality Checks*
