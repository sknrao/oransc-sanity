# Near-RT RIC + E2 Simulator: Removal & Fresh Install Guide

**Scope**: Remove existing Near-RT RIC & E2 Sim from hpe16, then reinstall from scratch  
**Works on**: Any clean Ubuntu 20.04 / 22.04 / 24.04 server  
**Server password**: `1234`

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
