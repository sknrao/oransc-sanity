#!/bin/bash
set -e

# --- Configuration ---
CLUSTER_NAME="hpe16-cluster"
BMH_NAME="hpe16-bmh"
TARGET_IP="10.200.105.XXX"  # Replace with the actual IP address
SSH_USER="rehanfazal"
# --- FIX: Use your local private key file directly ---
SSH_KEY_PATH="/home/rehanfazal/.ssh/id_rsa"
# ---

echo "--- 🚀 Starting cluster bootstrap for ${CLUSTER_NAME} ---"

# 1. Wait for BMH Association
echo "1. Waiting for BMH association..."
MACHINE_NAME=""
while [ -z "$MACHINE_NAME" ]; do
  MACHINE_NAME=$(kubectl get bmh "$BMH_NAME" -n default -o jsonpath='{.spec.consumerRef.name}' 2>/dev/null || true)
  [ -z "$MACHINE_NAME" ] && sleep 5 && printf "."
done
echo -e "\n✅ BMH associated: ${MACHINE_NAME}"

# 2. Wait for Bootstrap Secret
echo "2. Waiting for bootstrap secret..."
BOOTSTRAP_READY=""
while [ "$BOOTSTRAP_READY" != "true" ]; do
  BOOTSTRAP_READY=$(kubectl get machine "$MACHINE_NAME" -n default -o jsonpath='{.status.bootstrapReady}' 2>/dev/null || true)
  [ "$BOOTSTRAP_READY" != "true" ] && sleep 5 && printf "."
done
echo -e "\n✅ Bootstrap secret ready"

# 3. Create kubeadm config
echo "3. Creating kubeadm config..."
cat > "/tmp/${CLUSTER_NAME}-kubeadm.yaml" <<EOF
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
clusterName: ${CLUSTER_NAME}
controlPlaneEndpoint: ${TARGET_IP}:6443
kubernetesVersion: v1.29.0
networking:
  podSubnet: 192.168.0.0/16
  serviceSubnet: 10.96.0.0/16
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
nodeRegistration:
  imagePullPolicy: IfNotPresent
  kubeletExtraArgs: {}
EOF

# 4. Bootstrap cluster
echo "4. Bootstrapping Kubernetes cluster..."
# 4a. Upload the kubeadm.yaml file
echo "  Uploading kubeadm.yaml to hpe16..."
cat "/tmp/${CLUSTER_NAME}-kubeadm.yaml" | ssh -i "$SSH_KEY_PATH" -o "StrictHostKeyChecking=no" "${SSH_USER}@${TARGET_IP}" "sudo tee /tmp/kubeadm.yaml > /dev/null"

# 4b. Define all remote commands
BOOTSTRAP_CMDS=$(cat <<EOF
set -e
echo "  [hpe16] Pre-pulling K8s images..."
sudo kubeadm config images pull --cri-socket=unix:///var/run/containerd/containerd.sock

echo "  [hpe16] Running kubeadm init..."
sudo kubeadm init --config /tmp/kubeadm.yaml --ignore-preflight-errors=all

echo "  [hpe16] Setting up kubeconfig..."
mkdir -p \$HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf \$HOME/.kube/config
sudo chown \$(id -u):\$(id -g) \$HOME/.kube/config

echo "  [hpe16] Installing Calico CNI..."
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/calico.yaml

# --- FIX: REMOVE THE TAINT ---
NODE_NAME=\$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
echo "  [hpe16] Removing control-plane taint from node: \$NODE_NAME"
kubectl taint nodes \$NODE_NAME node-role.kubernetes.io/control-plane:NoSchedule-

echo "  [hpe16] Waiting for node readiness..."
kubectl wait --for=condition=Ready node/\$NODE_NAME --timeout=300s
echo -e "\n  [hpe16] Node \$NODE_NAME is Ready"

echo "  [hpe16] Patching providerID..."
kubectl patch node \$NODE_NAME -p '{"spec":{"providerID":"metal3://default/${BMH_NAME}"}}'

echo "  [hpe16] ✅ Cluster bootstrap complete!"
EOF
)

# 4c. Execute the remote commands
echo "  Running remote bootstrap commands..."
ssh -i "$SSH_KEY_PATH" -o "StrictHostKeyChecking=no" "${SSH_USER}@${TARGET_IP}" "$BOOTSTRAP_CMDS"

# 5. Cleanup
rm "/tmp/${CLUSTER_NAME}-kubeadm.yaml"

echo "---
🎉 Bootstrap complete! Check 'kubectl get machine -n default' on nephio.
The machine phase should now change to 'Running'."