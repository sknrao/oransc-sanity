# Demo Script: Management & Workload Cluster Creation (BYOH)this is going to be cool55

This document outlines the end-to-end process for deploying a Cluster API (CAPI) management cluster and provisioning a new workload cluster using the BYOH (Bring Your Own Host) infrastructure provider, all managed via GitOps.

Phase 1: Management Cluster (BMC) Setup

The first phase involves preparing our central management cluster.

1.1. Run Initial Setup Script

We begin by running the mgmt_cluster.sh script on the designated management node.

# On the Management Cluster Node
./mgmt_cluster.sh


This script automates the following setup:

Installs Kubernetes: A single-node k8s cluster.

Installs Tooling: Helm, ArgoCD, ArgoCD CLI, and clusterctl.

Initializes CAPI: Runs clusterctl init --infrastructure byoh.

Patches Controller: Updates the BYOH controller image to rehanfazal47/cluster-api-byoh-controller:v0.5.0 to include necessary fixes or features.

Configures GitOps: Sets up ArgoCD to monitor a specified git repository.

1.2. Generate Bootstrap Kubeconfig

For workload nodes (hosts) to join, they need a way to communicate with the management cluster's API server. We generate a special, limited bootstrap kubeconfig for this.

# On the Management Cluster Node

echo "Fetching APIServer and CA data..."
APISERVER=$(kubectl config view -ojsonpath='{.clusters[0].cluster.server}')
CA_CERT=$(kubectl config view --flatten -ojsonpath='{.clusters[0].cluster.certificate-authority-data}')

echo "Applying BootstrapKubeconfig CR..."
cat <<EOF | kubectl apply -f -
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: BootstrapKubeconfig
metadata:
  name: bootstrap-kubeconfig
  namespace: default
spec:
  apiserver: "$APISERVER"
  certificate-authority-data: "$CA_CERT"
EOF

echo "Waiting for controller to generate kubeconfig (waiting 10s)..."
sleep 10

echo "Extracting bootstrap kubeconfig from CR status..."
kubectl get bootstrapkubeconfig bootstrap-kubeconfig -n default -o=jsonpath='{.status.bootstrapKubeconfigData}' > ~/bootstrap-kubeconfig.conf

echo "Bootstrap kubeconfig saved to ~/bootstrap-kubeconfig.conf"


Phase 2: Workload Host (BWC Node) Preparation

Next, we prepare the bare-metal machine or VM that will become our workload cluster.

2.1. Copy Bootstrap Kubeconfig

The file we just created must be securely copied to the target workload node.

# On the Management Cluster Node
scp ~/bootstrap-kubeconfig.conf user@<WORKLOAD_NODE_IP>:~/bootstrap-kubeconfig.conf


2.2. Run Prerequisite Script

On the target workload node, we run prerequsite_workload.sh.

# On the Target Workload Node
# (Ensure ~/bootstrap-kubeconfig.conf exists)
./prerequsite_workload.sh


This script:

Installs all necessary prerequisites (e.g., containerd, kubelet, kubeadm).

Uses the bootstrap-kubeconfig.conf to register itself with the management cluster.

2.3. Verify Host Registration

Back on the management cluster, we can now see the new host registered as a ByoHost object.

# On the Management Cluster Node
kubectl get byohosts

# NAME        OSNAME   OSIMAGE              ARCH
# workload5   linux    Ubuntu 22.04.5 LTS   amd64


We note the name of the host (e.g., workload5 or workload-node-hostname) for later steps.

Phase 3: Workload Cluster (BWC) Generation

With the host available, we can now define and create the workload cluster.

3.1. Generate Cluster YAML

We use clusterctl to generate the cluster manifests.

# On the Management Cluster Node
# Set this IP to the FQDN or IP of the workload node
export CONTROL_PLANE_ENDPOINT_IP=10.105.247.117 

clusterctl generate cluster byoh-cluster6 \
  --infrastructure byoh \
  --kubernetes-version v1.29.3 \
  --control-plane-machine-count 1 \
  --worker-machine-count 0 > work6-cluster.yaml

echo "Generated work6-cluster.yaml"


3.2. Modify Cluster YAML

We must edit work6-cluster.yaml to inject critical postKubeadmCommands. These commands run inside the new workload cluster node after kubeadm init completes.

We find the KubeadmConfigTemplate and add the postKubeadmCommands section:

# ... inside work6-cluster.yaml ...
---
apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
kind: KubeadmConfigTemplate
metadata:
  name: byoh-cluster6-control-plane
spec:
  template:
    spec:
      kubeadmConfigSpec:
        # ... other kubeadm settings ...

        # ADD THIS SECTION
        postKubeadmCommands:
          # Install Calico CNI
          - curl -L [https://raw.githubusercontent.com/projectcalico/calico/v3.27.2/manifests/calico.yaml](https://raw.githubusercontent.com/projectcalico/calico/v3.27.2/manifests/calico.yaml) -o /root/calico.yaml
          - kubectl --kubeconfig=/etc/kubernetes/admin.conf apply -f /root/calico.yaml || true
          # Allow pods to run on the control-plane node
          - kubectl --kubeconfig=/etc/kubernetes/admin.conf taint nodes --all node-role.kubernetes.io/control-plane- || true
          # Critically, set the node's ProviderID. This is vital for CAPI.
          - kubectl --kubeconfig=/etc/kubernetes/admin.conf patch node $(hostname) --patch '{"spec":{"providerID":"byoh://'$(hostname)'"}}'


Phase 4: GitOps Deployment & Manual Patching

4.1. Push to GitOps Repo

We commit the modified work6-cluster.yaml to our git repository.

# On our local machine (with the git repo cloned)
git add work6-cluster.yaml
git commit -m "Add byoh-cluster6 workload cluster"
git push origin main


ArgoCD will detect the change and apply the manifest, starting the CAPI provisioning process.

4.2. Monitor Cluster Creation

We can watch the CAPI objects being created on the management cluster:

# On the Management Cluster Node
watch kubectl get cluster,machine,byomachine,kubeadmcontrolplane


4.3. Run Manual Patch Script

In this BYOH flow, the ByoMachine object often gets stuck, as it doesn't automatically detect that the node is ready. We must run a patch script to manually set the providerID (on the management cluster's ByoMachine CR) and mark it as ready.

Save this as patch-byoh.sh

# On the Management Cluster Node
chmod +x patch-byoh.sh

# Run with cluster name and the workload node's *hostname*
./patch-byoh.sh byoh-cluster6 <WORKLOAD_NODE_HOSTNAME>


Phase 5: Final Verification

5.1. Check CAPI Objects

After patching, the CAPI objects should all transition to a Ready or Provisioned state.

# On the Management Cluster Node
kubectl get cluster,machine,byomachine


5.2. Get Workload Cluster Kubeconfig

Finally, we retrieve the kubeconfig for our new, running workload cluster.

# On the Management Cluster Node
clusterctl get kubeconfig byoh-cluster6 > ./byoh-cluster6.kubeconfig

echo "Workload cluster kubeconfig saved to ./byoh-cluster6.kubeconfig"

# Test the new cluster

# kubectl get cluster,machine
# NAME            CLUSTERCLASS   AVAILABLE   CP DESIRED   CP AVAILABLE   CP UP-TO-DATE   W DESIRED   W AVAILABLE   W UP-TO-DATE   PHASE         AGE   VERSION
# byoh-cluster5                  True        1            1              1               0           0             0              Provisioned   11h  
# NAME                                CLUSTER         NODE NAME   READY   AVAILABLE   UP-TO-DATE   PHASE          AGE   VERSION
# byoh-cluster5-control-plane-vsqqd   byoh-cluster5   workload5   True    True        True         Running        11h   v1.29.3




This final output confirms our workload cluster is successfully created and operational.
