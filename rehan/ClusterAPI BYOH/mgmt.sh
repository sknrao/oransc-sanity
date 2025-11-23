#!/bin/bash
set -euo pipefail

LOG_FILE="$HOME/k8s-mgmt-setup.log"
echo "Logging setup to $LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

# =========================
# 1. Configuration Variables
# =========================
K8S_MINOR_SERIES=${K8S_MINOR_SERIES:-"v1.34"}
RETRY_MAX=5
RETRY_DELAY=5

# Network & IPs
INTERNAL_IP=$(hostname -I | awk '{print $1}')
POD_NETWORK_CIDR="10.244.0.0/16"
KUBE_APISERVER_ADVERTISE_ADDRESS=$INTERNAL_IP

# Versions & Images
BYOH_IMAGE="rehanfazal47/byoh-controller:controller-enhancced"
BYOH_NAMESPACE="byoh-system"
BYOH_DEPLOYMENT="byoh-controller-manager"

# Tools & Manifests
CLUSTERCTL_URL="https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.11.3/clusterctl-linux-amd64"
CERT_MANAGER_URL="https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml"
FLANNEL_URL="https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml"
LOCAL_PATH_URL="https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.24/deploy/local-path-storage.yaml"
ARGOCD_MANIFEST="https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
ARGOCD_NODEPORT=30007

# =========================
# 2. Helper Functions
# =========================
retry() {
    local n=0
    until "$@"; do
        n=$((n+1))
        if [ "$n" -lt "$RETRY_MAX" ]; then
            echo "Command '$*' failed. Retry $n/$RETRY_MAX in $RETRY_DELAY seconds..."
            sleep "$RETRY_DELAY"
        else
            echo "Command '$*' failed after $n attempts."
            return 1
        fi
    done
}

install_apt_pkg() {
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
}

# =========================
# 3. System Preparation
# =========================
prepare_system() {
    echo "=== [1/9] System Preparation (Swap, Modules, Sysctl) ==="
    
    sudo apt-get update -y
    install_apt_pkg apt-transport-https ca-certificates curl gpg iptables iproute2 wget lsb-release gnupg jq

    # Disable Swap
    sudo swapoff -a
    sudo sed -i '/\bswap\b/ s/^/#/' /etc/fstab

    # Load Modules
    cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
    sudo modprobe overlay
    sudo modprobe br_netfilter

    # Sysctl
    cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
    sudo sysctl --system
}

install_containerd() {
    echo "=== [2/9] Installing Containerd ==="
    install_apt_pkg containerd
    
    sudo mkdir -p /etc/containerd
    sudo containerd config default | sudo tee /etc/containerd/config.toml >/dev/null
    # Enforce SystemdCgroup
    sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
    
    sudo systemctl restart containerd
    sudo systemctl enable containerd
}

install_k8s_binaries() {
    echo "=== [3/9] Installing Kubernetes Binaries ($K8S_MINOR_SERIES) ==="
    
    sudo mkdir -p /etc/apt/keyrings
    sudo rm -f /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    curl -fsSL "https://pkgs.k8s.io/core:/stable:/${K8S_MINOR_SERIES}/deb/Release.key" \
        | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${K8S_MINOR_SERIES}/deb/ /" \
        | sudo tee /etc/apt/sources.list.d/kubernetes.list

    sudo apt-get update
    # Unhold if exists, update, then hold
    sudo apt-mark unhold kubelet kubeadm kubectl 2>/dev/null || true
    install_apt_pkg kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
    
    # Configure Kubelet Cgroup driver
    sudo mkdir -p /etc/systemd/system/kubelet.service.d
    echo '[Service]
Environment="KUBELET_EXTRA_ARGS=--cgroup-driver=systemd"' | sudo tee /etc/systemd/system/kubelet.service.d/20-extra-args.conf
    
    sudo systemctl daemon-reload
    sudo systemctl restart kubelet
}

# =========================
# 4. Ansible Setup
# =========================
setup_ansible_env() {
    echo "=== [4/9] Setting up Ansible & Kubernetes Collections ==="
    
    install_apt_pkg ansible python3-pip

    # OS Version Detection for Python Lib installation
    if [ -f /etc/os-release ]; then . /etc/os-release; fi
    MAJOR_VER="${VERSION_ID%%.*}"

    echo "Detected Ubuntu Version: $VERSION_ID"

    if [ "$MAJOR_VER" = "24" ]; then
        echo "Ubuntu 24.04 detected: Installing Python libs via APT"
        install_apt_pkg python3-kubernetes python3-jsonpatch python3-openshift
    else
        echo "Standard Ubuntu detected: Installing Python libs via PIP"
        sudo python3 -m pip install --upgrade pip || true
        retry sudo pip3 install kubernetes jsonpatch openshift
    fi

    # Install Ansible Kubernetes Collection (Required for your playbook)
    echo "Installing Ansible Galaxy Collection: kubernetes.core"
    ansible-galaxy collection install kubernetes.core
}

# =========================
# 5. Cluster Bootstrap
# =========================
bootstrap_cluster() {
    echo "=== [5/9] Bootstrapping Management Cluster ==="
    
    # Init Kubeadm
    retry sudo kubeadm init --apiserver-advertise-address="$KUBE_APISERVER_ADVERTISE_ADDRESS" --pod-network-cidr="$POD_NETWORK_CIDR"
    
    # Setup Kubeconfig
    mkdir -p "$HOME/.kube"
    sudo cp -f /etc/kubernetes/admin.conf "$HOME/.kube/config"
    sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"

    # Untaint Master (since it's a single node mgmt cluster)
    kubectl taint nodes --all node-role.kubernetes.io/control-plane- || true

    # Install CNI (Flannel)
    retry kubectl apply -f "$FLANNEL_URL"
    
    echo "Waiting for node to be Ready..."
    kubectl wait --for=condition=Ready node --all --timeout=120s
}

install_storage_and_cert_manager() {
    echo "=== [6/9] Installing Storage & Cert Manager ==="
    
    # Local Path Storage (Fixed: Added this back from your original script)
    retry kubectl apply -f "$LOCAL_PATH_URL"
    # Patch it as default class
    kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}' || true
    
    # Cert Manager
    retry kubectl apply -f "$CERT_MANAGER_URL"
    echo "Waiting for cert-manager pods..."
    kubectl wait --for=condition=Ready --timeout=300s pods -n cert-manager --all || true
}

install_tools_and_argocd() {
    echo "=== [7/9] Installing Tools (Helm, Clusterctl, ArgoCD) ==="
    
    # Helm
    if ! command -v helm &> /dev/null; then
        curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi

    # Clusterctl
    if ! command -v clusterctl &> /dev/null; then
        curl -L "$CLUSTERCTL_URL" -o clusterctl
        sudo install -o root -g root -m 0755 clusterctl /usr/local/bin/clusterctl
        rm clusterctl
    fi

    # ArgoCD
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    retry kubectl apply -n argocd -f "$ARGOCD_MANIFEST"
    
    # Patch ArgoCD Service to NodePort
    echo "Patching ArgoCD to NodePort $ARGOCD_NODEPORT..."
    kubectl -n argocd patch svc argocd-server --type='merge' -p "{\"spec\": {\"type\": \"NodePort\", \"ports\": [{\"port\": 443, \"targetPort\": 8080, \"nodePort\": $ARGOCD_NODEPORT}]}}"
}

# =========================
# 6. CAPI & BYOH Setup
# =========================
setup_capi_byoh() {
    echo "=== [8/9] Initializing CAPI with BYOH Provider ==="

    # Initialize CAPI
    export CLUSTER_TOPOLOGY=true
    retry clusterctl init --infrastructure byoh

    echo "Waiting for BYOH Deployment..."
    kubectl -n "$BYOH_NAMESPACE" rollout status deployment/"$BYOH_DEPLOYMENT" --timeout=180s || true

    echo "Patching BYOH Controller Image to: $BYOH_IMAGE"
    kubectl -n "$BYOH_NAMESPACE" set image deployment/"$BYOH_DEPLOYMENT" manager="$BYOH_IMAGE"
    kubectl -n "$BYOH_NAMESPACE" rollout status deployment/"$BYOH_DEPLOYMENT" --timeout=180s

    echo "Patching RBAC for Agent Permissions..."
    # This fixes the 'forbidden' error for patching byomachines
    PATCH_JSON='[
      {"op": "add", "path": "/rules/-", "value": {"apiGroups": ["infrastructure.cluster.x-k8s.io"], "resources": ["byomachines"], "verbs": ["get","list","patch","update","watch"]}},
      {"op": "add", "path": "/rules/-", "value": {"apiGroups": ["infrastructure.cluster.x-k8s.io"], "resources": ["byomachines/status"], "verbs": ["get","patch","update"]}}
    ]'
    kubectl patch clusterrole byoh-byohost-editor-role --type='json' -p "$PATCH_JSON" || true
}

final_report() {
    echo "=== [9/9] Installation Complete ==="
    echo "-----------------------------------"
    echo "Mgmt Node IP: $INTERNAL_IP"
    echo "K8s Version:  $(kubectl version --short 2>/dev/null || kubectl version | grep Server)"
    echo "Ansible:      $(ansible --version | head -n 1)"
    echo "ArgoCD URL:   https://$INTERNAL_IP:$ARGOCD_NODEPORT"
    echo "BYOH Image:   $BYOH_IMAGE"
    echo "-----------------------------------"
    echo "Run this to get kubectl auto completion"
    echo "source <(kubectl completion bash) >> ~/.bashrc"
    echo "kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null"
    echo "=== Mgmt cluster installed successfully ==="
}

# =========================
# Main Execution
# =========================
main() {
    prepare_system
    install_containerd
    install_k8s_binaries
    setup_ansible_env
    bootstrap_cluster
    install_storage_and_cert_manager
    install_tools_and_argocd
    setup_capi_byoh
    final_report
}

main