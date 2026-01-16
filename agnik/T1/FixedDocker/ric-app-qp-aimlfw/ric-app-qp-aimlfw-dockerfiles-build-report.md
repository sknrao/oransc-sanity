# O-RAN-SC ric-app-qp-aimlfw Dockerfiles Build Report

**Repository:** [o-ran-sc/ric-app-qp-aimlfw](https://github.com/o-ran-sc/ric-app-qp-aimlfw)  
**Date:** 2025-09-17

## 1. Repository Overview
- **Description:** QoE AIML Assist xApp (Go) with RMR integration.
- **Languages:** Go, Dockerfile
- **License:** Apache 2.0

## 2. Dockerfiles Discovered
1 Dockerfile found:
- `Dockerfile`

## 3. Build Results
| Dockerfile | Status | Notes |
|------------|--------|-------|
| `Dockerfile` | ✅ SUCCESS (after minimal fix) | Built as `ric-app-qp-aimlfw:main`; unit tests executed in build stage |

### Commands Used
```bash
cd /home/agnik/Desktop && git clone --depth=1 https://github.com/o-ran-sc/ric-app-qp-aimlfw.git
cd ric-app-qp-aimlfw
sudo docker build --network=host -t ric-app-qp-aimlfw:main -f Dockerfile .
```

## 4. Issues Found and Minimal Fixes
- **Read-only filesystem when editing `/etc/hosts` during tests**
  - Error: `/bin/sh: 1: cannot create /etc/hosts: Read-only file system`.
  - Fix: Removed the `/etc/hosts` modification; ran `go test` directly. Tests passed and coverage generated.

## 5. Observations
- Builder base: `nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu20-c-go:1.1.0`.
- Installs RMR 4.7.0 (stretch) successfully in builder stage.
- Uses `go mod tidy -compat=1.17`, vendors deps, builds binary, runs tests for `./influx` and `./control`.
- Final image: `ubuntu:20.04`; copies coverage outputs to `/tmp`.

## 6. Recommendations
- Consider using JSON-form `ENV key=value` formatting and JSON-form CMD/ENTRYPOINT.
- Optional: pin Go toolchain in base or builder for reproducibility.

## 7. Outcome
- Build successful after minimal fix; image `ric-app-qp-aimlfw:main` available.

## 8. Reference
- Repo: `https://github.com/o-ran-sc/ric-app-qp-aimlfw`
