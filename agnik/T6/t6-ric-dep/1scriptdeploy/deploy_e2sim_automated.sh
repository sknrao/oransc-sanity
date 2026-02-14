#!/bin/bash
# ==================================================================================
# E2 Simulator Automated Deployment Script
# Target: Generic K8s Cluster (Near-RT RIC installed)
# ==================================================================================
set -e

# Configuration
E2SIM_REPO="https://gerrit.o-ran-sc.org/r/sim/e2-interface"
IMAGE_NAME="e2simul"
IMAGE_TAG="0.0.4"
NAMESPACE="ricplt"
BUILD_DIR="$HOME/e2sim_automated_build"

# Function to ensure build tooling is present
ensure_build_tooling() {
    if command -v docker >/dev/null 2>&1; then
        echo ">>> Found docker. Proceeding with Docker build."
        return 0
    fi

    if command -v nerdctl >/dev/null 2>&1 && systemctl is-active --quiet buildkit; then
        echo ">>> Found nerdctl and buildkit. Proceeding."
        return 0
    fi

    echo ">>> Docker missing. Ensuring nerdctl and buildkit are installed..."
    
    # 1. Install nerdctl
    if ! command -v nerdctl >/dev/null 2>&1; then
        echo ">>> Installing nerdctl..."
        curl -L https://github.com/containerd/nerdctl/releases/download/v1.7.6/nerdctl-1.7.6-linux-amd64.tar.gz -o /tmp/nerdctl.tar.gz
        sudo tar Cxzvf /usr/local/bin /tmp/nerdctl.tar.gz
        rm /tmp/nerdctl.tar.gz
    fi

    # 2. Install buildkit
    if ! command -v buildkitd >/dev/null 2>&1; then
        echo ">>> Installing buildkit..."
        curl -L https://github.com/moby/buildkit/releases/download/v0.13.1/buildkit-v0.13.1.linux-amd64.tar.gz -o /tmp/buildkit.tar.gz
        sudo tar Cxzvf /usr/local /tmp/buildkit.tar.gz
        rm /tmp/buildkit.tar.gz
    fi

    # 3. Setup buildkit service
    if ! systemctl is-active --quiet buildkit; then
        echo ">>> Setting up buildkit service..."
        sudo tee /etc/systemd/system/buildkit.service <<EOF
[Unit]
Description=BuildKit
Documentation=https://github.com/moby/buildkit

[Service]
ExecStart=/usr/local/bin/buildkitd --containerd-worker=true

[Install]
WantedBy=multi-user.target
EOF
        sudo systemctl daemon-reload
        sudo systemctl enable --now buildkit
    fi
    
    echo ">>> Build tooling setup complete."
}

echo ">>> [1/6] Preparing workspace: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo ">>> [2/6] Creating robust Dockerfile..."
cat <<EOF > Dockerfile
FROM ubuntu:22.04 as build-env
ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \\
    build-essential git cmake libsctp-dev autoconf automake libtool bison flex \\
    libboost-all-dev wget pkg-config

# Install nlohmann/json
RUN mkdir -p /usr/local/include/nlohmann && \\
    wget https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp \\
    -O /usr/local/include/nlohmann/json.hpp

WORKDIR /playpen

# Clone repo
RUN git clone "${E2SIM_REPO}" .

# Build Core E2Sim Library
WORKDIR /playpen/e2sim
RUN mkdir build && cd build && cmake .. && make && make install

# FIX: Manually copy headers (make install is incomplete)
RUN cp -f src/base/*.hpp /usr/local/include/ 2>/dev/null || true
RUN cp -f src/SCTP/*.hpp src/SCTP/*.h /usr/local/include/ 2>/dev/null || true
RUN cp -f src/DEF/*.hpp src/DEF/*.h /usr/local/include/ 2>/dev/null || true
RUN cp -f src/messagerouting/*.hpp /usr/local/include/ 2>/dev/null || true
RUN cp -f src/encoding/*.hpp /usr/local/include/ 2>/dev/null || true
RUN cp -f src/asn1c/*.h /usr/local/include/ 2>/dev/null || true

# FIX: Manually copy library and link
RUN cp -f build/libe2sim_shared.so /usr/local/lib/libe2sim_shared.so 2>/dev/null || \\
    cp -f build/src/base/libe2sim_shared.so /usr/local/lib/libe2sim_shared.so 2>/dev/null || true
RUN ln -sf /usr/local/lib/libe2sim_shared.so /usr/local/lib/libe2sim.so
RUN ldconfig

# Build KPM Simulator
WORKDIR /playpen/e2sim/e2sm_examples/kpm_e2sm
RUN cp -r ../../asn1c .
RUN mkdir build && cd build && cmake .. && make

# Runtime Stage
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y libsctp1 && rm -rf /var/lib/apt/lists/*

# Fix: Copy binary and shared library
COPY --from=build-env /playpen/e2sim/e2sm_examples/kpm_e2sm/build/src/kpm/kpm_sim /usr/local/bin/kpm_sim
COPY --from=build-env /usr/local/lib/libe2sim_shared.so /usr/local/lib/libe2sim_shared.so
RUN ln -sf /usr/local/lib/libe2sim_shared.so /usr/local/lib/libe2sim.so && ldconfig
ENV LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH

ENTRYPOINT ["kpm_sim"]
EOF

echo ">>> [3/6] Building image (using docker or nerdctl)..."
ensure_build_tooling
if command -v docker >/dev/null 2>&1; then
    sudo docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    echo ">>> [4/6] Importing image into K8s (containerd namespace: k8s.io)"
    sudo docker save -o e2simul_img.tar "${IMAGE_NAME}:${IMAGE_TAG}"
    if command -v ctr >/dev/null 2>&1; then
        sudo ctr -n=k8s.io images import e2simul_img.tar 2>/dev/null || true
    fi
    rm -f e2simul_img.tar
elif command -v nerdctl >/dev/null 2>&1; then
    # nerdctl builds directly into containerd
    sudo nerdctl -n k8s.io build --no-cache -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    echo ">>> Image built and imported directly into containerd via nerdctl."
else
    echo "ERROR: Neither docker nor nerdctl found. Please install one to continue."
    exit 1
fi

echo ">>> [5/6] Patching and deploying Helm chart..."
cd "$HOME"
if [ ! -d "e2-interface" ]; then
    git clone "${E2SIM_REPO}"
fi
cd e2-interface/e2sim/e2sm_examples/kpm_e2sm/helm

# Reset chart to clean state
git reset --hard HEAD 2>/dev/null || true

# Patch: Fix hardcoded image in chart and use dynamic E2Term IP Detection
sed -i 's|image: e2simul:0.0.2|image: {{ .Values.image.repository }}:{{ .Values.image.tag }}|' templates/deployment.yaml

E2TERM_SVC=$(sudo kubectl get svc -n "${NAMESPACE}" --no-headers | grep "e2term-sctp" | awk '{print $1}' | head -n 1)

if [ -z "$E2TERM_SVC" ]; then
    echo "ERROR: Could not find e2term SCTP service in namespace ${NAMESPACE}"
    exit 1
fi

E2TERM_IP=$(sudo kubectl get svc -n "${NAMESPACE}" "${E2TERM_SVC}" -o jsonpath='{.spec.clusterIP}')
echo ">>> Detected E2Term ($E2TERM_SVC) ClusterIP: $E2TERM_IP"

sed -i '/restartPolicy: Never/d' templates/deployment.yaml
sed -i "s|imagePullPolicy: IfNotPresent|imagePullPolicy: IfNotPresent\n          args: [\"$E2TERM_IP\", \"36422\"]|" templates/deployment.yaml

# Uninstall old release
sudo helm uninstall e2sim -n "${NAMESPACE}" 2>/dev/null || true
sleep 5

# Install new release
sudo helm install e2sim . -n "${NAMESPACE}" \
  --set image.repository="${IMAGE_NAME}" \
  --set image.tag="${IMAGE_TAG}" \
  --set image.pullPolicy=IfNotPresent

echo ">>> [6/6] Verifying connection..."
# Wait for pod to start
echo "Waiting for pod to start..."
sleep 20
POD_NAME=$(sudo kubectl get pods -n "${NAMESPACE}" -l app=e2simulator -o jsonpath='{.items[0].metadata.name}')
echo ">>> Checking logs for $POD_NAME..."

# Poll logs for success message
for i in {1..15}; do
    if sudo kubectl logs -n "${NAMESPACE}" "${POD_NAME}" | grep -q "Received SETUP-RESPONSE-SUCCESS"; then
        echo ">>> SUCCESS: E2 Simulator connected to RIC Platform!"
        exit 0
    fi
    echo "Wait for E2 Setup Response... ($i/15)"
    sleep 10
done

echo ">>> WARNING: E2 Setup Response not detected yet. Check logs manually:"
echo "kubectl logs -n ${NAMESPACE} -l app=e2simulator"
