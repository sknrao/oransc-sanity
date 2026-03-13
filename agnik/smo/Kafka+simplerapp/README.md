# Simple Energy Saving rApp (Continuous)

A simple rApp that monitors O-RAN PM data from Kafka, applies a threshold-based energy-saving decision, and controls cell power via SDNR (O1 interface).

## Core Logic
```text
Kafka (pmreports) → Threshold (PRB < 20%?) → SDNR RESTCONF (LOCK/UNLOCK cell)
```

## Deployment & Verification (Step-by-Step)

Follow these exact commands on the server to deploy the latest version to the `smo` namespace.

### Step 1: SSH into the server
```bash
sshpass -p 1234 ssh agnikmisra@hpe15.anuket.iol.unh.edu
```

### Step 2: Delete existing artifacts
```bash
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl delete deployment simple-es-rapp -n smo --ignore-not-found
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl delete configmap simple-rapp-code -n smo --ignore-not-found
```

### Step 3: Copy updated code (Run locally)
From your local machine, copy the latest script and manifest:
```bash
sshpass -p 1234 scp simple_rapp.py agnikmisra@hpe15.anuket.iol.unh.edu:/tmp/
sshpass -p 1234 scp rapp-job.yaml agnikmisra@hpe15.anuket.iol.unh.edu:/tmp/
```

### Step 4: Create ConfigMap & Deploy (Back in SSH)
```bash
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl create configmap simple-rapp-code --from-file=/tmp/simple_rapp.py -n smo
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl apply -f /tmp/rapp-job.yaml
```

### Step 5: Watch the Pod status
```bash
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl get pods -n smo | grep simple
```

### Step 6: Stream live logs
```bash
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl logs -n smo deployment/simple-es-rapp -f
```

## Expected Output
When running correctly, the logs will show dynamic authentication and data processing:
```text
[AUTH] OAuth token fetched successfully from Keycloak
[KAFKA] Using OAUTHBEARER authentication (dynamic token)
[DATA] Message #1 | partition=5 offset=554
[DECISION] 1: PRB=0.6% -> LOCKED
[DECISION] 1: PRB=56.3% -> UNLOCKED
--- Cycle complete. Sleeping 60s ---
```

---

## 🛠 Troubleshooting: Restart PM Data Flow
If the rApp logs show `Waiting for data...` or `0 messages`, the data pipeline (simulators → VES → Kafka) might have stalled. Run these commands to kickstart the flow:

### 1. Restart Simulators
```bash
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl rollout restart deployment o-du-pynts-1122 o-du-pynts-1123 -n network
```

### 2. Restart VES Collector
```bash
sudo KUBECONFIG=/etc/kubernetes/admin.conf kubectl rollout restart deployment onap-dcae-ves-collector -n onap
```
Wait 2-3 minutes for the data to begin flowing into the `pmreports` topic again.
