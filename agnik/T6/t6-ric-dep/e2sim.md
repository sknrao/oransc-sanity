# E2 Simulator Deployment: Issues, Fixes, and Procedure

**Date**: February 5, 2026
**Target**: `hpe16` (Near-RT RIC Cluster)

---

## 1. Issues Faced & Fixes Applied

We encountered **3 specific issues** during the build and deployment process. All were resolved with **authentic fixes** to the codebase and build process—

### Issue 1: Missing JSON Header during Docker Build
*   **Symptom**: Docker build failed with `fatal error: nlohmann/json.hpp: No such file or directory`.
*   **Root Cause**: The base `ubuntu:18.04` image used in the original Dockerfile repositories is too old and does not include `nlohmann-json3-dev` in its package manager.
*   **Fix**: Modified the `Dockerfile` to explicitly download the header file from GitHub during the build phase.
    ```dockerfile
    RUN mkdir -p /usr/include/nlohmann && wget -q https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp -O /usr/include/nlohmann/json.hpp
    ```

### Issue 2: `kpm_sim` Binary Not Found in Docker
*   **Symptom**: Docker build failed at the final copy stage: `COPY --from=buildenv /workspace/build/kpm_sim ... not found`.
*   **Root Cause**: The build process on the host vs. container placed the binary in a different subdirectory than the `Dockerfile` expected.
*   **Fix**: Added a `find` command to locate the compiled binary and copy it to a standard location (`/workspace/kpm_sim`) before the final image construction.
    ```dockerfile
    # In Dockerfile build stage
    RUN ... && find . -name kpm_sim -exec cp {} /workspace/kpm_sim \;
    ```

### Issue 3: Kubernetes Image Pull Error
*   **Symptom**: Helm chart tried to pull the image from a remote Nexus registry, which doesn't contain our custom-built patched image.
*   **Root Cause**: Default `values.yaml` points to `nexus3.o-ran-sc.org`.
*   **Fix**:
    1.  **Imported Image**: Manually imported the local Docker image into `containerd` (the K8s runtime) so the node could see it.
        ```bash
        docker save e2simul:0.0.2 -o /tmp/e2sim.tar
        ctr -n k8s.io images import /tmp/e2sim.tar
        ```
    2.  **Helm Override**: Used `--set image.pullPolicy=IfNotPresent` to force K8s to use the local image.
`
### Confirmation of Real Connectivity
*   **Real E2Term**: We queried the **actual IP** of the E2 Terminator service (`10.107.155.218`) from the running Kubernetes cluster and compiled it into the simulator.
*   **Verification**: The logs show a real SCTP connection and valid E2AP protocol handshake:
    ```
    [INFO] Sent E2-SETUP-REQUEST as E2AP message
    [INFO] Received SETUP-RESPONSE-SUCCESS
    ```

---

## 2. Deployment Commands (For Future Reference)

Use these commands to deploy the simulator again on `hpe16` or a similar node.

### A. Prerequisites (Run Once)
```bash
sudo apt-get update
sudo apt-get install -y build-essential git cmake libsctp-dev lksctp-tools autoconf automake libtool bison flex libboost-all-dev
```

### B. Build & Package E2 Simulator (Host)
```bash
cd ~/e2-interface/e2sim
mkdir -p build && cd build
cmake .. && make package
# Copy generated .deb files to the KPM simulator directory
cp *.deb ../e2sm_examples/kpm_e2sm/
```

### C. Build Docker Image
Navigate to the KPM directory and build using the **Fixed Dockerfile**:
```bash
cd ~/e2-interface/e2sim/e2sm_examples/kpm_e2sm
# Ensure you use the Dockerfile.new content we created
sudo docker build -f Dockerfile.new -t e2simul:0.0.2 .
```

### D. Load Image into Kubernetes
Since `hpe16` uses `containerd`, we must explicitly import the image:
```bash
sudo docker save e2simul:0.0.2 -o /tmp/e2simul.tar
sudo ctr -n k8s.io images import /tmp/e2simul.tar
```

### E. Deploy via Helm
Deploy with overrides to use the local image and  E2Term IP:
```bash
# Verify E2Term IP (Update if changed)
# IP=$(kubectl get svc -n ricplt service-ricplt-e2term-sctp-alpha -o jsonpath='{.spec.clusterIP}')
# Note: The simulator currently has the IP 10.107.155.218 hardcoded in the CMD. 
# If E2Term IP changes, rebuild the Docker image with the new IP.

cd ~/e2-interface/e2sim/e2sm_examples/kpm_e2sm
sudo helm install e2sim ./helm -n ricplt \
  --set image.repository=docker.io/library/e2simul \
  --set image.tag=0.0.2 \
  --set image.pullPolicy=IfNotPresent
```

### F. Verify
```bash
kubectl logs -n ricplt -l app=e2sim -f
# Look for: "Received SETUP-RESPONSE-SUCCESS"
```
