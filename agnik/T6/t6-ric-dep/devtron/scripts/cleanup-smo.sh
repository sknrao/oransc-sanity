#!/bin/bash
# Clean up existing SMO deployment on Server 15
# Usage: bash cleanup-smo.sh

set -e

export KUBECONFIG=~/.kube/config

echo "=== Cleaning SMO Deployment ==="

# Check Kubernetes connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster."
    exit 1
fi

echo "1. Removing SMO namespaces..."
kubectl delete namespace smo nonrtric onap mariadb-operator strimzi-system --force --grace-period=0 2>&1 | head -10 || true
# Note: Keep openebs and devtroncd namespaces for Devtron GUI deployment

echo "2. Removing Helm releases (excluding Devtron and OpenEBS)..."
helm list -A | awk 'NR>1 {print $1 " " $2}' | while read release ns; do
    if [ -n "$release" ] && [ -n "$ns" ]; then
        # Skip Devtron and OpenEBS releases
        if [ "$release" != "devtron" ] && [ "$release" != "openebs" ] && [ "$ns" != "devtroncd" ] && [ "$ns" != "openebs" ]; then
            echo "  Uninstalling $release from $ns"
            helm uninstall "$release" -n "$ns" 2>&1 || true
        fi
    fi
done

echo "3. Removing CRDs..."
kubectl get crd | grep -E 'mariadb|strimzi|kafka|openebs' | awk '{print $1}' | xargs -r kubectl delete crd 2>&1 || true

echo "4. Removing Persistent Volumes..."
kubectl delete pv --all 2>&1 || true
kubectl delete pvc -A --all 2>&1 || true

echo "5. Removing Storage Classes..."
kubectl get storageclass | grep -E 'smo|openebs' | awk '{print $1}' | xargs -r kubectl delete storageclass 2>&1 || true

echo "6. Removing it-dep directory..."
sudo rm -rf ~/it-dep

echo ""
echo "=== Verification ==="
kubectl get namespaces | grep -E 'smo|nonrtric|onap|openebs|mariadb|strimzi' || echo "✓ No SMO namespaces found"
helm list -A | grep -v NAME || echo "✓ No Helm releases found"
kubectl get pods -A | grep -E 'smo|nonrtric|onap' || echo "✓ No SMO pods found"

echo ""
echo "✓ SMO cleanup completed"

