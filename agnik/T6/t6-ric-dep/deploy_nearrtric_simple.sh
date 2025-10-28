#!/bin/bash

# =============================================================================
# O-RAN Near-RT RIC Deployment Script - Simplified Version
# Based on actual deployment used for Server 16
# =============================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# =============================================================================
# INSTALL PREREQUISITES
# =============================================================================

install_prerequisites() {
    log "Installing prerequisites..."
    
    # Update system
    sudo apt update
    
    # Install basic tools
    sudo apt install -y curl wget git
    
    # Install Kubernetes repository
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
    
    # Update package list
    sudo apt update
    
    # Install Kubernetes components
    sudo apt install -y kubelet kubeadm kubectl
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    # Install containerd
    sudo apt install -y containerd
    
    # Configure containerd for Kubernetes
    sudo mkdir -p /etc/containerd
    sudo containerd config default | sudo tee /etc/containerd/config.toml
    sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
    sudo systemctl restart containerd
    sudo systemctl enable containerd
    
    # Disable swap
    sudo swapoff -a
    sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
    
    log "Prerequisites installed successfully"
}

# =============================================================================
# INITIALIZE KUBERNETES CLUSTER
# =============================================================================

init_kubernetes() {
    log "Initializing Kubernetes cluster..."
    
    # Initialize cluster
    sudo kubeadm init --pod-network-cidr=10.244.0.0/16
    
    # Setup kubectl
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    
    # Install pod network (Flannel)
    kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/v0.18.1/Documentation/kube-flannel.yml
    
    # Remove taint from control plane node
    kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule-
    
    # Wait for cluster to be ready
    log "Waiting for cluster to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=300s
    
    log "Kubernetes cluster initialized successfully"
}

# =============================================================================
# INSTALL HELM
# =============================================================================

install_helm() {
    log "Installing Helm..."
    
    # Download and install Helm
    curl https://get.helm.sh/helm-v3.14.4-linux-amd64.tar.gz -o helm-v3.14.4-linux-amd64.tar.gz
    tar -xzf helm-v3.14.4-linux-amd64.tar.gz
    sudo mv linux-amd64/helm /usr/local/bin/helm
    rm -rf linux-amd64 helm-v3.14.4-linux-amd64.tar.gz
    
    # Verify Helm installation
    helm version
    
    log "Helm installation completed"
}

# =============================================================================
# CLONE RIC-DEP REPOSITORY
# =============================================================================

clone_ric_dep() {
    log "Cloning ric-dep repository..."
    
    # Remove existing ric-dep directory
    if [ -d "ric-dep" ]; then
        warn "Removing existing ric-dep directory..."
        rm -rf ric-dep
    fi
    
    # Clone repository
    git clone "https://gerrit.o-ran-sc.org/r/ric-plt/ric-dep"
    
    # Verify clone
    if [ ! -d "ric-dep/bin" ]; then
        error "Failed to clone ric-dep repository"
    fi
    
    log "ric-dep repository cloned successfully"
}

# =============================================================================
# SETUP RIC-COMMON REPOSITORY
# =============================================================================

setup_ric_common_repo() {
    log "Setting up ric-common repository..."
    
    # Package ric-common
    helm package ric-dep/ric-common/Common-Template/helm/ric-common
    
    # Create local repository
    mkdir -p /tmp/local-repo
    cp ric-common-*.tgz /tmp/local-repo/
    cd /tmp/local-repo && helm repo index .
    cd $OLDPWD  # Return to previous directory
    
    # Kill any existing HTTP server on port 8879
    sudo pkill -f "python3 -m http.server 8879" || true
    sleep 2
    
    # Start HTTP server
    python3 -m http.server 8879 --directory /tmp/local-repo &
    
    # Wait for server to start
    sleep 5
    
    # Add local repository
    helm repo add local http://127.0.0.1:8879
    
    # Verify repository
    helm search repo local/ric-common
    
    log "ric-common repository setup completed"
}

# =============================================================================
# MODIFY DEPLOYMENT RECIPE
# =============================================================================

modify_recipe() {
    log "Modifying deployment recipe..."
    
    # Get host IP address
    local host_ip=$(hostname -I | awk '{print $1}')
    log "Host IP address: $host_ip"
    
    # Copy recipe file
    cp ric-dep/RECIPE_EXAMPLE/example_recipe_latest_stable.yaml ric-dep/RECIPE_EXAMPLE/my_recipe.yaml
    
    # Update IP addresses in recipe
    sed -i "s/ricip: \".*\"/ricip: \"$host_ip\"/g" ric-dep/RECIPE_EXAMPLE/my_recipe.yaml
    sed -i "s/auxip: \".*\"/auxip: \"$host_ip\"/g" ric-dep/RECIPE_EXAMPLE/my_recipe.yaml
    
    log "Deployment recipe modified successfully"
}

# =============================================================================
# CREATE REQUIRED NAMESPACES
# =============================================================================

create_namespaces() {
    log "Creating required namespaces..."
    
    # Create namespaces
    kubectl create namespace ricinfra || true
    kubectl create namespace ricxapp || true
    kubectl create namespace ricaux || true
    
    log "Namespaces created successfully"
}

# =============================================================================
# INSTALL RIC
# =============================================================================

install_ric() {
    log "Installing Near-RT RIC..."
    
    # Create namespaces first
    create_namespaces
    
    # Change to ric-dep/bin directory
    cd ric-dep/bin
    
    # Install RIC using the modified recipe
    ./install -f ../RECIPE_EXAMPLE/my_recipe.yaml
    
    # Return to original directory
    cd $OLDPWD
    
    log "Near-RT RIC installation completed"
}

# =============================================================================
# VERIFY DEPLOYMENT
# =============================================================================

verify_deployment() {
    log "Verifying Near-RT RIC deployment..."
    
    # Wait for deployment to stabilize
    log "Waiting for deployment to stabilize..."
    sleep 60
    
    # Check Helm releases
    log "Checking Helm releases..."
    helm list --all-namespaces
    
    # Check pods in ricplt namespace
    log "Checking pods in ricplt namespace..."
    kubectl get pods -n ricplt
    
    # Check pods in ricinfra namespace
    log "Checking pods in ricinfra namespace..."
    kubectl get pods -n ricinfra
    
    # Check services
    log "Checking services..."
    kubectl get svc --all-namespaces | grep -E "(ricplt|ricinfra)"
    
    # Check Kong proxy
    log "Checking Kong proxy..."
    kubectl get svc -n ricplt | grep kong
    
    # Test Kong proxy health
    local kong_service=$(kubectl get svc -n ricplt | grep kong | awk '{print $1}')
    if [ ! -z "$kong_service" ]; then
        log "Kong service: $kong_service"
        # Get NodePort for Kong
        local kong_port=$(kubectl get svc -n ricplt $kong_service -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')
        if [ ! -z "$kong_port" ]; then
            log "Kong proxy accessible on port: $kong_port"
            log "Health check: http://$(hostname -I | awk '{print $1}'):$kong_port/health"
        fi
    fi
    
    log "Deployment verification completed"
}

# =============================================================================
# MAIN FUNCTION
# =============================================================================

main() {
    log "Starting O-RAN Near-RT RIC Deployment (Simplified Version)"
    
    # Install prerequisites
    install_prerequisites
    
    # Initialize Kubernetes
    init_kubernetes
    
    # Install Helm
    install_helm
    
    # Clone repository
    clone_ric_dep
    
    # Setup ric-common repository
    setup_ric_common_repo
    
    # Modify recipe
    modify_recipe
    
    # Install RIC
    install_ric
    
    # Verify deployment
    verify_deployment
    
    # Display access information
    local host_ip=$(hostname -I | awk '{print $1}')
    log "🎉 Near-RT RIC deployment completed successfully!"
    echo ""
    log "Access Information:"
    log "  Host IP: $host_ip"
    log "  Kong Proxy: Check kubectl get svc -n ricplt for NodePort"
    log "  Kong Health: http://$host_ip:NODEPORT/health"
    echo ""
    log "Useful commands:"
    log "  kubectl get pods -n ricplt"
    log "  kubectl get pods -n ricinfra"
    log "  kubectl get svc --all-namespaces"
    log "  helm list --all-namespaces"
}

# Run main function
main "$@"
