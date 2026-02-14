#!/bin/bash
# ==================================================================================
# Near-RT RIC Platform Automated Deployment Script
# Target: Generic K8s Cluster (Ubuntu-based)
# ==================================================================================
set -e

# --- Variables ---
RIC_DEP_REPO="https://gerrit.o-ran-sc.org/r/ric-plt/ric-dep"
RECIPE_DIR="RECIPE_EXAMPLE"
RECIPE_FILE="custom_recipe.yaml"
LOCAL_REPO_DIR="/tmp/local-repo"
LOCAL_REPO_PORT=8879

# --- Custom Recipe Content ---
read -r -d '' CUSTOM_RECIPE_CONTENT << 'EOF' || true
################################################################################
#   Copyright (c) 2019 AT&T Intellectual Property.                             #
#   Licensed under the Apache License, Version 2.0                             #
###############################################################################

common:
  releasePrefix: r4

extsvcplt:
  ricip: "10.0.0.1"
  auxip: "10.0.0.1"

prometheus:
  enabled: true

a1mediator:
  image:
    registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
    name: ric-plt-a1
    tag: 3.2.3

appmgr:
  image:
   init:
     registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
     name: it-dep-init
     tag: 0.0.1
   appmgr:
     registry: "docker.io/mdimado"
     name: ric-plt-appmgr
     tag: cve-fix
   chartmuseum:
     registry: "docker.io"
     name: chartmuseum/chartmuseum
     tag: v0.8.2

dbaas:
  image:
    registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
    name: ric-plt-dbaas
    tag: 0.6.5

e2mgr:
  image:
    registry: "docker.io/mdimado"
    name: ric-plt-e2mgr
    tag: cve-fix
  privilegedmode: false
  globalRicId:
    ricId: "AACCE"
    mcc: "310"
    mnc: "411"

e2term:
  alpha:
    image:
      registry: "docker.io/mdimado"
      name: ric-plt-e2
      tag: cve-fix
    privilegedmode: false
    hostnetworkmode: false

jaegeradapter:
  image:
    registry: "docker.io"
    name: jaegertracing/all-in-one
    tag: 1.12

rtmgr:
  image:
    registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
    name: ric-plt-rtmgr
    tag: 0.9.7

submgr:
  image:
    registry: "docker.io/mdimado"
    name: ric-plt-submgr
    tag: cve-fix

vespamgr:
  image:
    registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
    name: ric-plt-vespamgr
    tag: 0.7.5

o1mediator:
  image:
    registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
    name: ric-plt-o1
    tag: 0.6.4

alarmmanager:
  image:
    registry: "nexus3.o-ran-sc.org:10002/o-ran-sc"
    name: ric-plt-alarmmanager
    tag: 0.5.17

influxdb:
  image:
    registry: "influxdb"
    name: influxdb
    tag: "2.2.0-alpine"
EOF

echo ">>> [1/5] Cloning and Preparing ric-dep repository..."
cd ~
if [ -d "ric-dep" ]; then
    echo "Existing ric-dep found. Backing up and re-cloning..."
    mv ric-dep "ric-dep_backup_$(date +%Y%m%d_%H%M%S)"
fi

git clone "$RIC_DEP_REPO"
cd ric-dep

# Create the custom recipe file
echo "$CUSTOM_RECIPE_CONTENT" > "$RECIPE_DIR/$RECIPE_FILE"
echo "Custom recipe created at $RECIPE_DIR/$RECIPE_FILE"

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

sed -i "s/ricip: .*/ricip: \"${MY_IP}\"/" "$RECIPE_DIR/$RECIPE_FILE"
sed -i "s/auxip: .*/auxip: \"${MY_IP}\"/" "$RECIPE_DIR/$RECIPE_FILE"

# Verify patching
grep -E "ricip|auxip" "$RECIPE_DIR/$RECIPE_FILE"

echo ">>> [4/5] Initiating Near-RT RIC Installation..."
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
