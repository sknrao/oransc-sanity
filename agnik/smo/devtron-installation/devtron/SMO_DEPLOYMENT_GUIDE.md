# SMO Deployment via Devtron GUI - Step by Step Guide

## Prerequisites

- ✅ Kubernetes cluster running on server 15
- ✅ Helm installed
- ✅ Devtron installed (run `install-devtron.sh`)
- ✅ Clean SMO deployment (run `scripts/cleanup-smo.sh`)

---

## Step 1: Access Devtron GUI

### Get Devtron URL:
```bash
kubectl get svc -n devtroncd devtron-service
```

### Port Forward (if needed):
```bash
kubectl port-forward -n devtroncd svc/devtron-service 8080:80
```

### Access:
- URL: http://localhost:8080 (or server-ip:NodePort)
- Username: `admin`
- Password: Get with:
  ```bash
  kubectl get secret devtron-secret -n devtroncd -o jsonpath='{.data.ACD_PASSWORD}' | base64 -d
  ```

---

## Step 2: Configure Helm Repositories

1. **Login to Devtron**
2. **Navigate to:** Global Configurations → Helm Repositories
3. **Add each repository** (from `configs/smo-repositories.yaml`):

   | Name | URL |
   |------|-----|
   | oran-snapshot | https://nexus3.o-ran-sc.org/repository/helm.snapshot/ |
   | oran-release | https://nexus3.o-ran-sc.org/repository/helm.release/ |
   | strimzi | https://strimzi.io/charts/ |
   | openebs | https://openebs.github.io/openebs |
   | mariadb-operator | https://helm.mariadb.com/mariadb-operator |

4. **Click "Save"** for each repository
5. **Verify:** Go to Charts → Browse Charts, you should see charts from these repos

---

## Step 3: Deploy Infrastructure Components

### 3.1 Deploy OpenEBS

1. **Go to:** Charts → Browse Charts
2. **Search:** `openebs`
3. **Select:** `openebs/openebs` chart
4. **Click:** "Deploy"
5. **Configure:**
   - Release Name: `openebs`
   - Namespace: `openebs` (create new)
   - Chart Version: Latest
   - Values: Use defaults or customize
6. **Click:** "Deploy"
7. **Wait:** Until deployment completes (check status)

### 3.2 Deploy MariaDB Operator

1. **Search:** `mariadb-operator`
2. **Select:** `mariadb-operator/mariadb-operator`
3. **Configure:**
   - Release Name: `mariadb-operator`
   - Namespace: `mariadb-operator` (create new)
4. **Deploy** and wait for completion

### 3.3 Deploy Strimzi Kafka Operator

1. **Search:** `strimzi`
2. **Select:** `strimzi/strimzi-kafka-operator`
3. **Configure:**
   - Release Name: `strimzi-kafka-operator`
   - Namespace: `strimzi-system` (create new)
4. **Deploy** and wait for completion

---

## Step 4: Deploy ONAP

⚠️ **Note:** ONAP uses custom `helm deploy` plugin. Devtron may not support this directly.

### Option A: Use Devtron Custom Script

1. **Go to:** Applications → Custom Scripts
2. **Create new script:**
   ```bash
   #!/bin/bash
   cd ~/it-dep/smo-install/scripts/layer-2
   bash 2-install-oran.sh default release
   ```
3. **Run script** via Devtron

### Option B: Deploy ONAP Sub-charts Individually

1. **Search:** `onap` in Charts
2. **Deploy components individually:**
   - onap-strimzi
   - onap-mariadb-galera
   - onap-postgres
   - onap-repository-wrapper
   - onap-roles-wrapper
   - onap (main chart)

### Option C: Use Devtron's Helm Install (if supported)

1. **Search:** `onap`
2. **Select:** `oran-release/onap` or `oran-snapshot/onap`
3. **Configure:**
   - Release Name: `onap`
   - Namespace: `onap` (create new)
4. **Deploy**

---

## Step 5: Deploy Non-RT-RIC

1. **Search:** `nonrtric`
2. **Select:** `oran-release/nonrtric` or `oran-snapshot/nonrtric`
3. **Configure:**
   - Release Name: `oran-nonrtric`
   - Namespace: `nonrtric` (create new)
   - **Important:** May need to copy Kafka secrets from `onap` namespace
4. **Deploy** and wait

---

## Step 6: Deploy SMO

1. **Search:** `smo`
2. **Select:** `oran-release/smo` or `oran-snapshot/smo`
3. **Configure:**
   - Release Name: `oran-smo`
   - Namespace: `smo` (create new)
   - **Important:** May need to copy Kafka secrets from `onap` namespace
4. **Deploy** and wait

---

## Step 7: Verify Deployment

### In Devtron GUI:

1. **Go to:** Applications → Deployed Applications
2. **Check status** of all deployments:
   - openebs: ✅ Deployed
   - mariadb-operator: ✅ Deployed
   - strimzi-kafka-operator: ✅ Deployed
   - onap: ✅ Deployed
   - oran-nonrtric: ✅ Deployed
   - oran-smo: ✅ Deployed

3. **Check Pods:**
   - Go to each application
   - View Pods tab
   - Verify all pods are Running

### Via Command Line:

```bash
# Check namespaces
kubectl get namespaces | grep -E 'smo|nonrtric|onap|openebs|mariadb|strimzi'

# Check Helm releases
helm list -A

# Check pods
kubectl get pods -A | grep -E 'smo|nonrtric|onap'
```

---

## Troubleshooting

### Issue: Helm Deploy Plugin Not Supported
**Solution:** Use Custom Script feature in Devtron or deploy sub-charts individually

### Issue: Kafka Secrets Not Found
**Solution:** Manually copy secrets:
```bash
kubectl get secrets -n onap | grep kafka
kubectl get secret <kafka-secret-name> -n onap -o yaml | sed 's/namespace: onap/namespace: nonrtric/' | kubectl apply -f -
```

### Issue: Charts Not Found
**Solution:** 
- Verify repositories are added correctly
- Update repositories: `helm repo update`
- Check repository URLs in Devtron

### Issue: Pods Stuck in Pending
**Solution:**
- Check resource constraints: `kubectl describe pod <pod-name> -n <namespace>`
- Check storage: `kubectl get pvc -A`
- Check events: `kubectl get events -A --sort-by='.lastTimestamp'`

---



