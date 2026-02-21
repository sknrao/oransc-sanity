#!/bin/bash
# Install Devtron on Kubernetes Cluster
# Usage: bash install-devtron.sh

set -e

echo "=== Installing Devtron ==="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "Error: helm not found. Please install helm first."
    exit 1
fi

# Check Kubernetes connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster."
    exit 1
fi

echo "✓ Kubernetes cluster accessible"

# Add Devtron Helm repository
echo "Adding Devtron Helm repository..."
helm repo add devtron https://helm.devtron.ai
helm repo update

echo "✓ Devtron repository added"

# Create namespace
echo "Creating devtroncd namespace..."
kubectl create namespace devtroncd --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Namespace created"

# Install Devtron with storage configuration
echo "Installing Devtron..."
helm install devtron devtron/devtron-operator \
  --namespace devtroncd \
  --set installer.modules={cicd} \
  --set postgresql.auth.postgresPassword=devtron \
  --set postgresql.auth.password=devtron \
  --set postgresql.primary.persistence.enabled=true \
  --set postgresql.primary.persistence.size=20Gi \
  --set postgresql.primary.persistence.storageClass=smo-storage \
  --set postgresql.persistence.enabled=true \
  --set postgresql.persistence.size=20Gi \
  --set postgresql.persistence.storageClass=smo-storage \
  --set service.type=NodePort \
  --wait --timeout=15m

echo "✓ Devtron installation initiated"

# Wait for Devtron to be ready
echo "Waiting for Devtron to be ready (this may take 5-10 minutes)..."
kubectl wait --for=condition=ready pod -l app=devtron -n devtroncd --timeout=15m || true

echo ""
echo "=== Devtron Installation Complete ==="
echo ""
echo "To access Devtron:"
echo "1. Get service URL:"
echo "   kubectl get svc -n devtroncd devtron-service"
echo ""
echo "2. Port forward (if needed):"
echo "   kubectl port-forward -n devtroncd svc/devtron-service 8080:80"
echo ""
echo "3. Access: http://localhost:8080"
echo ""
echo "4. Get admin password:"
echo "   kubectl get secret devtron-secret -n devtroncd -o jsonpath='{.data.ACD_PASSWORD}' | base64 -d"
echo ""

