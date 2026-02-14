# Near-RT RIC + E2 Simulator: Removal & Fresh Install Guide

**Scope**: Remove existing Near-RT RIC & E2 Sim from hpe16, then reinstall from scratch  
**Works on**: Any clean Ubuntu 20.04 / 22.04 / 24.04 server  
**Server password**: `1234`

---

## Part A: REMOVAL (hpe16)

SSH into hpe16:
```bash
ssh agnikmisra@hpe16.anuket.iol.unh.edu
# password: 1234
```

### Step 1: Remove E2 Simulator
```bash
# Check if e2sim helm release exists
sudo helm list -n ricplt | grep e2sim

# Uninstall e2sim
sudo helm uninstall e2sim -n ricplt

# Verify e2sim pod is gone
sudo kubectl get pods -n ricplt | grep e2sim
# Should return nothing
```

### Step 2: Remove Near-RT RIC Platform
```bash
# Option A: If you have the ric-dep repo
cd ~/ric-dep/bin
sudo ./uninstall

# Option B: If ric-dep repo is not available, manually remove all helm releases
sudo helm list -n ricplt --short | xargs -I {} sudo helm uninstall {} -n ricplt
sudo helm list -n ricinfra --short | xargs -I {} sudo helm uninstall {} -n ricinfra

# Delete the namespaces (this removes everything inside them)
sudo kubectl delete namespace ricplt --timeout=120s
sudo kubectl delete namespace ricinfra --timeout=120s
sudo kubectl delete namespace ricxapp --timeout=120s
```

### Step 3: Verify Clean State
```bash
# All should return "No resources found" or "not found"
sudo kubectl get pods -n ricplt
sudo kubectl get pods -n ricinfra
sudo kubectl get pods -n ricxapp
sudo kubectl get ns | grep -E "ricplt|ricinfra|ricxapp"
sudo helm list -A | grep -E "ricplt|ricinfra"
```

### Step 4: Clean Up Docker/Containerd Images (Optional)
```bash
# Remove old e2sim images
sudo ctr -n=k8s.io images ls | grep e2sim
sudo ctr -n=k8s.io images rm docker.io/library/e2simul:0.0.2

# Remove RIC platform images (optional, they'll be re-pulled on install)
sudo ctr -n=k8s.io images ls | grep nexus3.o-ran-sc.org
```

---

## Part B: FRESH INSTALL (Any Server)

### Prerequisites
- Ubuntu 20.04 / 22.04 / 24.04
- Minimum 4GB RAM (8GB recommended)
- 20GB+ disk space
- Internet connectivity
- `sudo` access

### Phase 1: Install Kubernetes + Helm (Skip if already installed)

If the server already has K8s running (like hpe16), **skip to Phase 2**.

```bash
# 1. Clone the ric-dep repository
git clone "https://gerrit.o-ran-sc.org/r/ric-plt/ric-dep"
cd ric-dep

# 2. Run the K8s + Helm install script
cd bin
sudo ./install_k8s_and_helm.sh
cd ..

# 3. Fix containerd for Ubuntu 24.04 (skip on 20.04/22.04)
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd

# 4. Initialize K8s cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 5. Install Flannel CNI
sudo kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/v0.18.1/Documentation/kube-flannel.yml
sudo kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule-

# 6. Verify K8s is ready
sudo kubectl get nodes
# Should show: Ready
```

### Phase 2: Install Near-RT RIC Platform (Automated)

The most reliable way to install the Near-RT RIC platform is using the automated script. This script handles cloning the repository, setting up the local Helm repo, patching the recipe with the server IP, and triggering the installation.

```bash
cd ~
# If script is not present, create it using Section 2 of Part C
chmod +x deploy_ric_platform.sh
./deploy_ric_platform.sh
```

---

### Phase 3: Install Near-RT RIC Platform (Manual Steps)
If you prefer manual installation, follow these steps:
```bash
cd ~
git clone "https://gerrit.o-ran-sc.org/r/ric-plt/ric-dep"
cd ric-dep

# Package the common templates
sudo helm package ric-common/Common-Template/helm/ric-common

# Set up local Helm repo
# IMPORTANT: Charts must be in a "charts/" subdirectory because
# the install script looks for http://127.0.0.1:8879/charts/
mkdir -p /tmp/local-repo/charts
cp ric-common-*.tgz /tmp/local-repo/charts/
cd /tmp/local-repo/charts && sudo helm repo index .
cd ~/ric-dep

# Kill any old HTTP server on port 8879
pkill -f "http.server 8879" 2>/dev/null || true
sleep 1

# Start local repo server (background)
python3 -m http.server 8879 --directory /tmp/local-repo &

# Add to Helm (use /charts path)
sudo helm repo remove local 2>/dev/null || true
sudo helm repo add local http://127.0.0.1:8879/charts
sudo helm repo update

# Verify — must show ric-common
sudo helm search repo local/ric-common
# Should show: local/ric-common  3.3.2

# Quick test — this URL must return 200:
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8879/charts/index.yaml
```

#### Step 3: Configure the recipe
```bash
cd ~/ric-dep

# Get your server IP
MY_IP=$(hostname -I | awk '{print $1}')
echo "Server IP: $MY_IP"

# Edit the recipe file
nano RECIPE_EXAMPLE/example_recipe_latest_stable.yaml
```

**In the recipe file, find and update these lines**:
```yaml
extsvcplt:
  ricip: "YOUR_IP_HERE"    # ← Replace with $MY_IP
  auxip: "YOUR_IP_HERE"    # ← Replace with $MY_IP (same value)
```

**Quick sed command** (alternative to manual editing):
```bash
MY_IP=$(hostname -I | awk '{print $1}')
sed -i "s/ricip: .*/ricip: \"${MY_IP}\"/" RECIPE_EXAMPLE/example_recipe_latest_stable.yaml
sed -i "s/auxip: .*/auxip: \"${MY_IP}\"/" RECIPE_EXAMPLE/example_recipe_latest_stable.yaml

# Verify
grep -E "ricip|auxip" RECIPE_EXAMPLE/example_recipe_latest_stable.yaml
```

#### Step 4: Install Near-RT RIC
```bash
cd ~/ric-dep/bin
sudo ./install -f ../RECIPE_EXAMPLE/example_recipe_latest_stable.yaml
```

#### Step 5: Wait and verify deployment (5-10 minutes for images to pull)
```bash
# Watch pods come up
watch sudo kubectl get pods -n ricplt

# Expected: All pods should be Running or Completed
# Key pods to look for:
#   deployment-ricplt-a1mediator     1/1   Running
#   deployment-ricplt-appmgr         2/2   Running
#   deployment-ricplt-dbaas          1/1   Running
#   deployment-ricplt-e2mgr          1/1   Running
#   deployment-ricplt-e2term-alpha   1/1   Running
#   deployment-ricplt-rtmgr          1/1   Running
#   deployment-ricplt-submgr         1/1   Running
#   r4-infrastructure-kong           2/2   Running
```

```bash
# Check all namespaces
sudo kubectl get pods -n ricplt
sudo kubectl get pods -n ricinfra
sudo kubectl get svc -n ricplt
sudo helm list -n ricplt
```

#### Step 6: Expose A1 Mediator (for SMO access)
```bash
# Patch A1 Mediator to NodePort 30803
sudo kubectl patch svc service-ricplt-a1mediator-http -n ricplt \
  -p '{"spec": {"type": "NodePort", "ports": [{"port": 10000, "nodePort": 30803, "name": "http"}]}}'

# Verify
sudo kubectl get svc service-ricplt-a1mediator-http -n ricplt
# Should show: NodePort  30803

# Test A1 Mediator
curl -v http://$(hostname -I | awk '{print $1}'):30803/A1-P/v2/policytypes
# Expected: [] (empty array)
```

#### Step 7: Health check
```bash
# Get Kong proxy port
KONG_PORT=$(sudo kubectl get svc -n ricplt | grep kong-proxy | awk '{print $5}' | grep -oP '32\d+')
echo "Kong port: $KONG_PORT"

# Test App Manager health
curl -v http://localhost:${KONG_PORT}/appmgr/ric/v1/health/ready
# Expected: HTTP 200
```

---

### Phase 3: Install E2 Simulator (Automated)

The most reliable way to install the E2 Simulator is using the automated script. This script handles the build fixes, image importing, and dynamic IP patching.

```bash
cd ~
# If script is not present, create it using Section 3 of Part C
chmod +x deploy_e2sim_automated.sh
./deploy_e2sim_automated.sh
```

---

### Phase 4: Install E2 Simulator (Manual Steps)
If you prefer manual installation, follow these steps:
```bash
sudo apt-get update
sudo apt-get install -y cmake libsctp-dev autoconf automake libtool \
  mercurial git build-essential docker.io pkg-config libboost-all-dev
```

#### Step 2: Create the Robust Dockerfile
This Dockerfile includes fixes for missing headers (`nlohmann/json`), broken `make install` paths, and library linking.

```bash
cd ~
rm -rf e2sim_build
mkdir -p e2sim_build
cd e2sim_build

cat <<EOF > Dockerfile
FROM ubuntu:22.04 as build-env
ARG DEBIAN_FRONTEND=noninteractive

# 1. Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential git cmake libsctp-dev autoconf automake libtool bison flex \
    libboost-all-dev wget pkg-config

# 2. Install nlohmann/json
RUN mkdir -p /usr/local/include/nlohmann && \
    wget https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp \
    -O /usr/local/include/nlohmann/json.hpp

WORKDIR /playpen

# 3. Clone fresh repo
RUN git clone "https://gerrit.o-ran-sc.org/r/sim/e2-interface" .

# 4. Build Core E2Sim Library
WORKDIR /playpen/e2sim
RUN mkdir build && cd build && cmake .. && make && make install

# 5. FIX: Manually copy headers (make install is incomplete)
RUN cp -f src/base/*.hpp /usr/local/include/ 2>/dev/null || true
RUN cp -f src/SCTP/*.hpp src/SCTP/*.h /usr/local/include/ 2>/dev/null || true
RUN cp -f src/DEF/*.hpp src/DEF/*.h /usr/local/include/ 2>/dev/null || true
RUN cp -f src/messagerouting/*.hpp /usr/local/include/ 2>/dev/null || true
RUN cp -f src/encoding/*.hpp /usr/local/include/ 2>/dev/null || true
RUN cp -f src/asn1c/*.h /usr/local/include/ 2>/dev/null || true

# 6. FIX: Manually copy library and link
RUN cp -f build/libe2sim_shared.so /usr/local/lib/libe2sim_shared.so 2>/dev/null || \
    cp -f build/src/base/libe2sim_shared.so /usr/local/lib/libe2sim_shared.so 2>/dev/null || true
RUN ln -sf /usr/local/lib/libe2sim_shared.so /usr/local/lib/libe2sim.so
RUN ldconfig

# 7. Build KPM Simulator
WORKDIR /playpen/e2sim/e2sm_examples/kpm_e2sm
RUN cp -r ../../asn1c .
RUN mkdir build && cd build && cmake .. && make

# 8. Runtime Stage
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y libsctp1 && rm -rf /var/lib/apt/lists/*

# Fix: Copy binary and shared library
COPY --from=build-env /playpen/e2sim/e2sm_examples/kpm_e2sm/build/src/kpm/kpm_sim /usr/local/bin/kpm_sim
COPY --from=build-env /usr/local/lib/libe2sim_shared.so /usr/local/lib/libe2sim_shared.so
RUN ln -sf /usr/local/lib/libe2sim_shared.so /usr/local/lib/libe2sim.so && ldconfig
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

ENTRYPOINT ["kpm_sim"]
EOF
```

#### Step 3: Build and Import Image
```bash
# Build (takes ~10 mins)
sudo docker build -t e2simul:0.0.2 .

# Import to K8s containerd
sudo docker save -o e2simul.tar e2simul:0.0.2
sudo ctr -n=k8s.io images import e2simul.tar
```

#### Step 4: Deploy via Helm (with Dynamic IP Injection)
**CRITICAL**: The simulator only supports IP addresses, not hostnames. We must inject the E2Term ClusterIP.

```bash
cd ~
if [ ! -d "e2-interface" ]; then
    git clone "https://gerrit.o-ran-sc.org/r/sim/e2-interface"
fi
cd e2-interface/e2sim/e2sm_examples/kpm_e2sm/helm

# Revert previous patches
git reset --hard HEAD 2>/dev/null || true

# Patch: Remove invalid restartPolicy and inject E2Term IP
E2TERM_IP=$(sudo kubectl get svc -n ricplt service-ricplt-e2term-sctp-alpha -o jsonpath='{.spec.clusterIP}')
sed -i '/restartPolicy: Never/d' templates/deployment.yaml
sed -i "s|imagePullPolicy: IfNotPresent|imagePullPolicy: IfNotPresent\n          args: [\"$E2TERM_IP\", \"36422\"]|" templates/deployment.yaml

# Install
sudo helm install e2sim . -n ricplt \
  --set image.repository=e2simul \
  --set image.tag=0.0.2 \
  --set image.pullPolicy=IfNotPresent
```

#### Step 5: Verify E2 connection
```bash
# Check logs for successful E2 setup
# If it says "Waiting for SCTP data", restart e2term and e2sim to clear stale state
sudo kubectl logs -n ricplt -l app=e2sim --tail=20
```

**Expected success log**:
```
[INFO] Sent E2-SETUP-REQUEST as E2AP message
[INFO] Received SETUP-RESPONSE-SUCCESS
```

> [!TIP]
> If connection is not established immediately:
> 1. `kubectl rollout restart deployment deployment-ricplt-e2term-alpha -n ricplt`
> 2. `kubectl rollout restart deployment deployment-ricplt-e2mgr -n ricplt`
> 3. `kubectl delete pod -n ricplt -l app=e2simulator`

---

## Part C: POST-INSTALL VERIFICATION CHECKLIST

Run these after the full install to confirm everything works:

```bash
MY_IP=$(hostname -I | awk '{print $1}')

echo "=== 1. RIC Platform Pods ==="
sudo kubectl get pods -n ricplt
echo

echo "=== 2. RIC Services ==="
sudo kubectl get svc -n ricplt
echo

echo "=== 3. Helm Releases ==="
sudo helm list -n ricplt
echo

echo "=== 4. A1 Mediator ==="
curl -s http://${MY_IP}:30803/A1-P/v2/policytypes
echo

echo "=== 5. E2 Manager — Connected gNBs ==="
sudo kubectl exec -n ricplt deployment/deployment-ricplt-e2mgr -- \
  curl -s http://service-ricplt-e2mgr-http.ricplt:3800/v1/nodeb/states
echo

echo "=== 6. E2 Simulator Logs ==="
sudo kubectl logs -n ricplt -l app=e2sim --tail=5
echo

echo "=== DONE ==="
```

**Expected results**:
| Check | Expected |
|-------|----------|
| RIC pods | All `Running` or `Completed` |
| A1 Mediator | Returns `[]` on port 30803 |
| E2 Sim logs | `SETUP-RESPONSE-SUCCESS` |
| E2 Manager | Shows gNB `CONNECTED` |

---

## Quick Reference: Key Commands

| Action | Command |
|--------|---------|
| **Remove E2 Sim** | `sudo helm uninstall e2sim -n ricplt` |
| **Remove RIC** | `cd ric-dep/bin && sudo ./uninstall` |
| **Install RIC** | `cd ric-dep/bin && sudo ./install -f ../RECIPE_EXAMPLE/example_recipe_latest_stable.yaml` |
| **Install E2 Sim** | `sudo helm install e2sim . -n ricplt --set image.repository=e2simul --set image.tag=0.0.2 --set image.pullPolicy=IfNotPresent` |
| **Expose A1** | `sudo kubectl patch svc service-ricplt-a1mediator-http -n ricplt -p '{"spec":{"type":"NodePort","ports":[{"port":10000,"nodePort":30803,"name":"http"}]}}'` |
| **Check pods** | `sudo kubectl get pods -n ricplt` |
| **Check E2 gNBs** | `sudo kubectl exec -n ricplt deploy/deployment-ricplt-e2mgr -- curl -s http://service-ricplt-e2mgr-http.ricplt:3800/v1/nodeb/states` |

---

## Part D: TROUBLESHOOTING & LESSONS LEARNED

### 1. Architecture Mismatch (ImagePullBackOff / Exec Format Error)
**Problem**: Pod keeps restarting or fails to start with `exec format error`.
**Cause**: Building images on an M1/M2 Mac (`arm64`) and trying to run them on `hpe16` or `hpe26` (`amd64`).
**Fix**:
- Rebuild images using `--platform linux/amd64`.
- On the server, check the architecture of a pulled image:
  ```bash
  sudo docker inspect <image_name> | grep Architecture
  # OR (for containerd)
  sudo nerdctl -n k8s.io inspect <image_name> | grep Architecture
  ```

### 2. Missing Docker on K8s Nodes
**Problem**: `sudo: docker: command not found` when running build scripts.
**Solution**: Use **`nerdctl`** + **`buildkit`**. These work directly with the `containerd` runtime used by Kubernetes and do not conflict with the existing setup.
**Manual Setup**:
```bash
# Install nerdctl
curl -L https://github.com/containerd/nerdctl/releases/download/v1.7.6/nerdctl-1.7.6-linux-amd64.tar.gz -o /tmp/nerdctl.tar.gz
sudo tar Cxzvf /usr/local/bin /tmp/nerdctl.tar.gz

# Use nerdctl instead of docker
sudo nerdctl -n k8s.io build -t my-image:tag .
```

### 3. Image ID Collisions (Strange logs in Pods)
**Problem**: The E2 Simulator pod shows logs from Subscription Manager (`submgr`) or another component.
**Cause**: The built image has the same ID as an existing image in the local cache, or `nerdctl` is using a cached layer from a different build.
**Fix**: 
1. Build with **`--no-cache`**.
2. Use a **Unique Tag** for every build (e.g., `sim:0.0.4`, `sim:1.0.0`).
3. Manually re-tag the image in the correct namespace:
   ```bash
   # Find the Image ID
   sudo nerdctl -n k8s.io images
   # Force tag it
   sudo nerdctl -n k8s.io tag <IMAGE_ID> my-image:new-tag
   ```

### 4. Hardcoded Images in Helm Charts
**Problem**: `helm install --set image.tag=1.0.0` has no effect; pod still pulls `0.0.2`.
**Cause**: Many O-RAN SC charts have image names hardcoded in `templates/deployment.yaml` instead of using `{{ .Values.image.tag }}`.
**Fix**: Patch the template before installing:
```bash
sed -i 's|image: e2simul:0.0.2|image: {{ .Values.image.repository }}:{{ .Values.image.tag }}|' templates/deployment.yaml
```

### 5. e2term storage failures (Pending Pods)
**Problem**: `deployment-ricplt-e2term-alpha` stays in `Pending` state.
**Cause**: The pod is requesting a Persistent Volume (PVC), but the server doesn't have a storage provisioner (like OpenEBS or Longhorn).
**Fix**: Patch the deployment to use `emptyDir` (ephemeral storage) instead:
```bash
kubectl patch deployment deployment-ricplt-e2term-alpha -n ricplt --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/volumes/2", "value": {"name": "vol-shared", "emptyDir": {}}}]'
```

### 6. Summary of Automation Suite
All verified automation scripts are located at **`~/deploy/`** on `hpe16` and `hpe26`:
- `deploy_ric_platform_default.sh`: Stable Near-RT RIC.
- `deploy_e2sim_automated.sh`: E2 Sim with `nerdctl` & build fixes.
- `deploy_all_xapps.sh`: Dynamic xApp deployment.
- `deploy_ric_platform.sh`: Custom CVE-fix recipe (testing only).


# Manual Installation Guide: xApp Deployment

This guide explains how to manually deploy O-RAN SC xApps without using automated scripts or the App Manager's dashboard.

## Step 1: Discover RIC Platform RMR Services
xApps communicate via RMR and need to know the endpoints for E2Term, E2Mgr, and A1Mediator.

```bash
PLATFORM_NS="ricplt"
E2TERM_RMR=$(kubectl get svc -n $PLATFORM_NS --no-headers | grep "e2term-rmr" | awk '{print $1}')
E2MGR_RMR=$(kubectl get svc -n $PLATFORM_NS --no-headers | grep "e2mgr-rmr" | awk '{print $1}')
A1MED_RMR=$(kubectl get svc -n $PLATFORM_NS --no-headers | grep "a1mediator-rmr" | awk '{print $1}')
RTMGR_RMR=$(kubectl get svc -n $PLATFORM_NS --no-headers | grep "rtmgr-rmr" | awk '{print $1}')
```

## Step 2: Create local RMR Routing Table
Create a `local.rt` file to map message types to the discovered services.

```bash
cat <<EOF > local.rt
newrt|start
rte|10090|$E2TERM_RMR.$PLATFORM_NS:38000
rte|10091|$E2TERM_RMR.$PLATFORM_NS:38000
rte|12010|$E2MGR_RMR.$PLATFORM_NS:3801
rte|12011|$E2MGR_RMR.$PLATFORM_NS:3801
rte|12012|$E2MGR_RMR.$PLATFORM_NS:3801
rte|20011|$A1MED_RMR.$PLATFORM_NS:4562
rte|20012|$A1MED_RMR.$PLATFORM_NS:4562
# Self entry (replace XAPP_NAME with your xapp label)
rte|4560|service-ricxapp-XAPP_NAME-rmr.ricxapp:4560
newrt|end
EOF
```

## Step 3: Create ConfigMap
Combine your xApp's `config.json` and the `local.rt` into a ConfigMap.

```bash
kubectl create namespace ricxapp
kubectl create configmap configmap-ricxapp-XAPP_NAME -n ricxapp \
  --from-file=config-file.json=my_config.json \
  --from-file=local.rt=local.rt
```

## Step 4: Create Deployment Manifest
Define the pod spec with the necessary environment variables for RIC integration.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment-ricxapp-XAPP_NAME
  namespace: ricxapp
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: xapp
        image: <YOUR_IMAGE>
        env:
        - name: RMR_SEED_RT
          value: "/opt/route/local.rt"
        - name: RMR_RTG_SVC
          value: "$RTMGR_RMR.$PLATFORM_NS:4561"
        - name: RMR_SRC_ID
          value: "service-ricxapp-XAPP_NAME-rmr.ricxapp"
        - name: DBAAS_SERVICE_HOST
          value: "service-ricplt-dbaas-tcp.ricplt"
        - name: CONFIG_FILE
          value: "/opt/ric/config/config-file.json"
        volumeMounts:
        - name: config-volume
          mountPath: /opt/ric/config/config-file.json
          subPath: config-file.json
        - name: route-volume
          mountPath: /opt/route/local.rt
          subPath: local.rt
      volumes:
      - name: config-volume
        configMap:
          name: configmap-ricxapp-XAPP_NAME
      - name: route-volume
        configMap:
          name: configmap-ricxapp-XAPP_NAME
```

## Step 5: Verify xApp Integration
Check logs to ensure RMR is initialized and connected to the RIC platform.
```bash
kubectl logs -n ricxapp -l app=ricxapp-XAPP_NAME
```
