#!/bin/bash
set -e # Exit immediately on error

# --- Configuration ---
K8S_VERSION="1.29.0"
NEPHIO_PUBLIC_KEY="key-contents-go-here"  # Replace with the actual public key
# ---

K8S_MAJOR_MINOR=$(echo "${K8S_VERSION}" | cut -d. -f1,2)

echo "🚀 Starting prerequisite installation for Kubernetes v${K8S_VERSION}..."

echo "  Disabling swap..."
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

echo "📦 Installing containerd..."
sudo apt-get update
sudo apt-get install -y containerd

echo "🔧 Configuring containerd..."
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml >/dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

echo "🔄 Restarting and enabling containerd..."
sudo systemctl restart containerd
sudo systemctl enable containerd

echo "📦 Installing Kubernetes components (kubelet, kubeadm, kubectl)..."
sudo apt-get install -y apt-transport-https ca-certificates curl gpg

K8S_KEYRING="/etc/apt/keyrings/kubernetes-apt-keyring.gpg"
K8S_KEY_URL="https://pkgs.k8s.io/core:/stable:/v${K8S_MAJOR_MINOR}/deb/Release.key"
K8S_REPO_FILE="/etc/apt/sources.list.d/kubernetes.list"

echo "  Adding Kubernetes apt repository key..."
sudo rm -f "${K8S_KEYRING}"
curl -fsSL "${K8S_KEY_URL}" | sudo gpg --dearmor -o "${K8S_KEYRING}"

echo "  Adding Kubernetes apt repository..."
echo "deb [signed-by=${K8S_KEYRING}] https://pkgs.k8s.io/core:/stable:/v${K8S_MAJOR_MINOR}/deb/ /" | sudo tee "${K8S_REPO_FILE}"

sudo apt-get update
KUBE_PKG_VERSION=$(apt-cache madison kubeadm | grep "${K8S_VERSION}" | head -1 | awk '{print $3}')
if [ -z "$KUBE_PKG_VERSION" ]; then
  echo "❌ Error: Could not find K8s package version ${K8S_VERSION}."
  exit 1
fi

echo "  Found package version: ${KUBE_PKG_VERSION}. Installing..."
sudo apt-get install -y \
    kubelet="${KUBE_PKG_VERSION}" \
    kubeadm="${KUBE_PKG_VERSION}" \
    kubectl="${KUBE_PKG_VERSION}"

echo "🔒 Holding Kubernetes packages..."
sudo apt-mark hold kubelet kubeadm kubectl

echo "🔑 Ensuring SSH key for 'rehanfazal' is authorized..."
# This assumes the script is run by the 'rehanfazal' user
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"

# Add the public key if it's not already there
if ! grep -q "$NEPHIO_PUBLIC_KEY" "$HOME/.ssh/authorized_keys"; then
    echo "Adding Nephio public key to authorized_keys..."
    echo "$NEPHIO_PUBLIC_KEY" >> "$HOME/.ssh/authorized_keys"
else
    echo "Nephio public key already present in authorized_keys."
fi

echo "✅ Prerequisites  installed."
