#!/bin/bash
# ==================================================================================
# Near-RT RIC Platform Automated Deployment Script (Standard/Stable)
# Target: Generic K8s Cluster (Ubuntu-based)
# Uses the default deployment recipe from ric-dep.
# ==================================================================================
set -e

# --- Variables ---
RIC_DEP_REPO="https://gerrit.o-ran-sc.org/r/ric-plt/ric-dep"
RECIPE_DIR="RECIPE_EXAMPLE"
# Default stable recipe from the repository
RECIPE_FILE="example_recipe_latest_stable.yaml"
LOCAL_REPO_DIR="/tmp/local-repo"
LOCAL_REPO_PORT=8879

echo ">>> [1/5] Cloning and Preparing ric-dep repository..."
cd ~
if [ -d "ric-dep" ]; then
    echo "Existing ric-dep found. Backing up and re-cloning..."
    mv ric-dep "ric-dep_backup_$(date +%Y%m%d_%H%M%S)"
fi

git clone "$RIC_DEP_REPO"
cd ric-dep

echo ">>> [2/5] Setting up Local Helm Repository..."
# Package common templates
sudo helm package ric-common/Common-Template/helm/ric-common

# Set up directory structure
mkdir -p "$LOCAL_REPO_DIR/charts"
cp ric-common-*.tgz "$LOCAL_REPO_DIR/charts/"
cd "$LOCAL_REPO_DIR/charts" && sudo helm repo index .
cd ~/ric-dep

# Cleanup old server
pkill -f "http.server $LOCAL_REPO_PORT" 2>/dev/null || true
sleep 2

# Start background server
echo "Starting local Helm repo server on port $LOCAL_REPO_PORT..."
nohup python3 -m http.server "$LOCAL_REPO_PORT" --directory "$LOCAL_REPO_DIR" > /tmp/helm_repo.log 2>&1 &
sleep 2

# Add to Helm
sudo helm repo remove local 2>/dev/null || true
sudo helm repo add local "http://127.0.0.1:$LOCAL_REPO_PORT/charts"
sudo helm repo update

# Verify
if ! sudo helm search repo local/ric-common | grep -q "ric-common"; then
    echo "ERROR: Local helm repo registration failed."
    exit 1
fi
echo "Local Helm repository is ready."

echo ">>> [3/5] Configuring Recipe with Server IP..."
MY_IP=$(hostname -I | awk '{print $1}')
echo "Detected Server IP: $MY_IP"

# Patch the default recipe with the current server IP
sed -i "s/ricip: .*/ricip: \"${MY_IP}\"/" "$RECIPE_DIR/$RECIPE_FILE"
sed -i "s/auxip: .*/auxip: \"${MY_IP}\"/" "$RECIPE_DIR/$RECIPE_FILE"

# Verify patching
grep -E "ricip|auxip" "$RECIPE_DIR/$RECIPE_FILE"

echo ">>> [4/5] Initiating Near-RT RIC Installation (Default Recipe)..."
cd ~/ric-dep/bin
sudo ./install -f "../$RECIPE_DIR/$RECIPE_FILE"

echo ">>> [5/5] Installation Triggered. Verifying Deployment..."
echo "Waiting for pods to reach Running/Completed state (this may take 10+ minutes)..."

# Polling loop for verification
for i in {1..30}; do
    echo "Status Check #$i: $(sudo kubectl get pods -n ricplt --no-headers | grep -v "Running\|Completed" | wc -l) pods still initializing..."
    if [ $(sudo kubectl get pods -n ricplt --no-headers | grep -v "Running\|Completed" | wc -l) -eq 0 ]; then
        echo "SUCCESS: All Near-RT RIC pods are Running or Completed!"
        sudo kubectl get pods -n ricplt
        exit 0
    fi
    sleep 30
done

echo "WARNING: Deployment is taking longer than expected. Please check manually with:"
echo "sudo kubectl get pods -n ricplt"
