```
~/argo-parent-app.yaml

export KUBECONFIG=~/.kube/config; kubectl apply -f ~/argo-parent-app.yaml

export KUBECONFIG=~/.kube/config; kubectl get app onap-gitops-hpe16 -n argocd

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   Unknown       Healthy



kubectl get app onap-gitops-hpe16 -n argocd -o jsonpath='{.status.conditions}'

[{"lastTransitionTime":"2026-01-23T18:07:46Z","message":"Failed to load target state: failed to generate manifest for source 1 of 1: rpc error: code = Unknown desc = 1Algooverride: app path does not exist","type":"ComparisonError"}]

kubectl delete app onap-gitops-hpe16 -n argocd && sleep 2 && kubectl apply -f ~/argo-parent-app.yaml

application.argoproj.io "onap-gitops-hpe16" deleted
application.argoproj.io/onap-gitops-hpe16 created

kubectl get app onap-gitops-hpe16 -n argocd

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   OutOfSync     Progressing

sleep 20 && kubectl get app onap-gitops-hpe16 -n argocd

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   OutOfSync     Degraded

.export KUBECONFIG=~/.kube/config; kubectl get pods -n onap"

NAME                                            READY   STATUS    RESTARTS   AGE
onap-policy-postgres-primary-f76cb64c-szt2r     0/1     Pending   0          57s
onap-policy-postgres-replica-6887f9856f-nmk8v   0/1     Pending   0          57s
onap-postgres-primary-66c8dff577-nltcr          0/1     Pending   0          57s
onap-postgres-replica-86b64c8455-pbvd9          0/1     Pending   0          57s

 kubectl describe pod onap-postgres-primary-66c8dff577-nltcr -n onap | grep -A 5 Events

Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  2m2s  default-scheduler  0/1 nodes are available: persistentvolumeclaim "onap-postgres-primary" not found. preemption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling..
  Warning  FailedScheduling  2m    default-scheduler  0/1 nodes are available: persistentvolumeclaim "onap-postgres-primary" not found. pree

kubectl get app onap-gitops-hpe16 -n argocd

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   OutOfSync     Degraded

kubectl get pods -n onap

NAME                                            READY   STATUS    RESTARTS   AGE
onap-policy-postgres-primary-f76cb64c-szt2r     0/1     Pending   0          20m
onap-policy-postgres-replica-6887f9856f-nmk8v   0/1     Pending   0          20m
onap-postgres-primary-66c8dff577-nltcr          0/1     Pending   0          20m
onap-postgres-replica-86b64c8455-pbvd9          0/1     Pending   0          20m

kubectl get pvc -n onap

NAME                       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
storage-mariadb-galera-0   Pending                                      smo-storage    20m

kubectl get events -n onap --sort-by='.lastTimestamp' | tail -n 15

20m         Normal    ScalingReplicaSet    deployment/onap-policy-api                               Scaled up replica set onap-policy-api-85d85ccf84 to 1
9m22s       Warning   FailedCreate         statefulset/mariadb-galera                               create Pod mariadb-galera-0 in StatefulSet mariadb-galera failed error: pods "mariadb-galera-0" is forbidden: error looking up service account onap/mariadb-galera: serviceaccount "mariadb-galera" not found
9m18s       Warning   FailedCreate         replicaset/onap-policy-pap-668b55cfd                     Error creating: pods "onap-policy-pap-668b55cfd-" is forbidden: error looking up service account onap/onap-policy-pap-read: serviceaccount "onap-policy-pap-read" not found
9m18s       Warning   FailedCreate         replicaset/onap-policy-clamp-runtime-acm-78c6d8588c      Error creating: pods "onap-policy-clamp-runtime-acm-78c6d8588c-" is forbidden: error looking up service account onap/onap-policy-clamp-runtime-acm-read: serviceaccount "onap-policy-clamp-runtime-acm-read" not found
9m18s       Warning   FailedCreate         replicaset/onap-policy-clamp-ac-kserve-ppnt-77f55f9c75   Error creating: pods "onap-policy-clamp-ac-kserve-ppnt-77f55f9c75-" is forbidden: error looking up service account onap/onap-policy-clamp-ac-kserve-ppnt-create: serviceaccount "onap-policy-clamp-ac-kserve-ppnt-create" not found
9m18s       Warning   FailedCreate         replicaset/onap-strimzi-kafka-bridge-857dff6bdd          Error creating: pods "onap-strimzi-kafka-bridge-857dff6bdd-" is forbidden: error looking up service account onap/onap-strimzi-kafka-bridge: serviceaccount "onap-strimzi-kafka-bridge" not found
9m18s       Warning   FailedCreate         replicaset/onap-dcae-ves-collector-546c98c765            Error creating: pods "onap-dcae-ves-collector-546c98c765-" is forbidden: error looking up service account onap/onap-dcae-ves-collector-read: serviceaccount "onap-dcae-ves-collector-read" not found
9m17s       Warning   FailedCreate         replicaset/onap-policy-clamp-ac-http-ppnt-5d46545bfb     Error creating: pods "onap-policy-clamp-ac-http-ppnt-5d46545bfb-" is forbidden: error looking up service account onap/onap-policy-clamp-ac-http-ppnt-read: serviceaccount "onap-policy-clamp-ac-http-ppnt-read" not found
9m17s       Warning   FailedCreate         replicaset/onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7    Error creating: pods "onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7-" is forbidden: error looking up service account onap/onap-policy-clamp-ac-a1pms-ppnt-create: serviceaccount "onap-policy-clamp-ac-a1pms-ppnt-create" not found
9m17s       Warning   FailedCreate         replicaset/onap-policy-apex-pdp-d458bbcbb                Error creating: pods "onap-policy-apex-pdp-d458bbcbb-" is forbidden: error looking up service account onap/onap-policy-apex-pdp-read: serviceaccount "onap-policy-apex-pdp-read" not found
9m16s       Warning   FailedCreate         replicaset/onap-policy-clamp-ac-pf-ppnt-757fdb4687       Error creating: pods "onap-policy-clamp-ac-pf-ppnt-757fdb4687-" is forbidden: error looking up service account onap/onap-policy-clamp-ac-pf-ppnt-read: serviceaccount "onap-policy-clamp-ac-pf-ppnt-read" not found
9m16s       Warning   FailedCreate         replicaset/onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c      Error creating: pods "onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c-" is forbidden: error looking up service account onap/onap-policy-clamp-ac-k8s-ppnt-create: serviceaccount "onap-policy-clamp-ac-k8s-ppnt-create" not found
9m16s       Warning   FailedCreate         replicaset/onap-policy-api-85d85ccf84                    Error creating: pods "onap-policy-api-85d85ccf84-" is forbidden: error looking up service account onap/onap-policy-api-read: serviceaccount "onap-policy-api-read" not found
9m16s       Warning   FailedCreate         replicaset/onap-strimzi-entity-operator-587b94dc9        Error creating: pods "onap-strimzi-entity-operator-587b94dc9-" is forbidden: error looking up service account onap/onap-strimzi-entity-operator: serviceaccount "onap-strimzi-entity-operator" not found
17s         Warning   ProvisioningFailed   persistentvolumeclaim/storage-mariadb-galera-0           storageclass.storage.k8s.io "smo-storage" not found


kubectl get storageclass smo-storage -o yaml

allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"allowVolumeExpansion":true,"apiVersion":"storage.k8s.io/v1","kind":"StorageClass","metadata":{"annotations":{},"name":"smo-storage"},"provisioner":"cluster.local/nfs-server-provisioner","reclaimPolicy":"Delete","volumeBindingMode":"Immediate"}
  creationTimestamp: "2026-01-22T17:19:51Z"
  name: smo-storage
  resourceVersion: "961891"
  uid: 89ece48d-22b1-45c9-a0ed-c93a5647d4e6
provisioner: cluster.local/nfs-server-provisioner
reclaimPolicy: Delete
volumeBindingMode: Immediate

 kubectl get storageclass"

NAME   PROVISIONER                            RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
nfs    cluster.local/nfs-server-provisioner   Delete          Immediate           true                   3d7h

~/…/deployoran $ ls -lh /home/agnik/Desktop/deployoran/1Algooverride/all_serviceaccounts.yaml

-rw-rw-r-- 1 agnik agnik 8.1K Jan 24 00:03 /home/agnik/Desktop/deployoran/1Algooverride/all_serviceaccounts.yaml


~/…/deployoran $ cat /home/agnik/Desktop/deployoran/smo-storageclass.yaml | sshpass -p 1234 ssh -o StrictHostKeyChecking=no agnikmisra@hpe16.anuket.iol.unh.edu "export KUBECONFIG=~/.kube/config; kubectl apply -f -"

storageclass.storage.k8s.io/smo-storage created


 kubectl get storageclass smo-storage"

NAME          PROVISIONER                            RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
smo-storage   cluster.local/nfs-server-provisioner   Delete          Immediate           true                   0s

 kubectl get pvc -n onap"

NAME                       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
storage-mariadb-galera-0   Pending                                      smo-storage    24m

1Algooverride $ git commit -m "Add ServiceAccounts to fix deployment blockers"

[master (root-commit) 73888c0] Add ServiceAccounts to fix deployment blockers
 12 files changed, 8883 insertions(+)
 create mode 100644 README_AND_COMPARISON.md
 create mode 100644 all_serviceaccounts.yaml
 create mode 100644 apply_values_override.py
 create mode 100644 dcae_full.yaml
 create mode 100644 onap-read-bindings.yaml
 create mode 100644 onap-read-role.yaml
 create mode 100644 policy_full.yaml
 create mode 100644 postgres_full.yaml
 create mode 100644 sdnc-serviceaccounts.yaml
 create mode 100644 sdnc_manual_fix.yaml
 create mode 100644 strimzi_full.yaml
 create mode 100644 user_desired_values.yaml


 git remote add origin https://github.com/Jitmisra/argoover.git

 git branch -M main

 1Algooverride $ git push -u origin main --force

Enumerating objects: 14, done.
Counting objects: 100% (14/14), done.
Delta compression using up to 8 threads
Compressing objects: 100% (14/14), done.
Writing objects: 100% (14/14), 67.37 KiB | 2.17 MiB/s, done.
Total 14 (delta 1), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (1/1), done.
To https://github.com/Jitmisra/argoover.git
 + 1357a1d...73888c0 main -> main (forced update)
branch 'main' set up to track 'origin/main'.

~/…/deployoran $ sleep 15 && sshpass -p 1234 ssh -o StrictHostKeyChecking=no agnikmisra@hpe16.anuket.iol.unh.edu "export KUBECONFIG=~/.kube/config; kubectl get app onap-gitops-hpe16 -n argocd"

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   OutOfSync     Degraded

 kubectl get sa -n onap | head -n 20"

NAME      SECRETS   AGE
default   0         58m

 kubectl get pods -n onap"

NAME                                            READY   STATUS    RESTARTS   AGE
onap-policy-postgres-primary-f76cb64c-szt2r     0/1     Pending   0          37m
onap-policy-postgres-replica-6887f9856f-nmk8v   0/1     Pending   0          37m
onap-postgres-primary-66c8dff577-nltcr          0/1     Pending   0          37m
onap-postgres-replica-86b64c8455-pbvd9          0/1     Pending   0          37m

 kubectl patch app onap-gitops-hpe16 -n argocd --type merge -p '{\"metadata\":{\"annotations\":{\"argocd.argoproj.io/refresh\":\"hard\"}}}'"

application.argoproj.io/onap-gitops-hpe16 patched

 kubectl get sa -n onap

NAME                                      SECRETS   AGE
default                                   0         59m
mariadb-galera                            0         44s
onap-dcae-ves-collector-read              0         44s
onap-policy-apex-pdp-read                 0         44s
onap-policy-api-read                      0         44s
onap-policy-clamp-ac-a1pms-ppnt-create    0         44s
onap-policy-clamp-ac-http-ppnt-read       0         44s
onap-policy-clamp-ac-k8s-ppnt-create      0         44s
onap-policy-clamp-ac-kserve-ppnt-create   0         44s
onap-policy-clamp-ac-pf-ppnt-read         0         44s
onap-policy-clamp-runtime-acm-read        0         44s
onap-policy-pap-read                      0         44s
onap-policy-read                          0         44s
onap-strimzi-entity-operator              0         44s
onap-strimzi-kafka                        0         44s
onap-strimzi-kafka-bridge                 0         44s
onap-strimzi-kafka-read                   0         44s

 kubectl get pods -n onap | head -n 15"

NAME                                                READY   STATUS              RESTARTS   AGE
mariadb-galera-0                                    0/1     Running             0          11s
onap-dcae-ves-collector-546c98c765-jp2g8            0/2     Init:0/1            0          8s
onap-policy-apex-pdp-d458bbcbb-n86ms                0/1     Init:0/1            0          6s
onap-policy-api-85d85ccf84-xjvw5                    0/1     Init:0/4            0          6s
onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7-zql6r    0/1     Init:0/1            0          6s
onap-policy-clamp-ac-http-ppnt-5d46545bfb-5vgn6     0/1     Init:0/1            0          6s
onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c-wpndr      0/1     Init:0/1            0          6s
onap-policy-clamp-ac-kserve-ppnt-77f55f9c75-hrcq7   0/1     Init:0/1            0          7s
onap-policy-clamp-ac-pf-ppnt-757fdb4687-q64cq       0/1     Init:0/1            0          6s
onap-policy-clamp-runtime-acm-78c6d8588c-5sz6s      0/1     Init:0/2            0          8s
onap-policy-pap-668b55cfd-6qk89                     0/1     Init:0/2            0          7s
onap-policy-postgres-primary-f76cb64c-szt2r         0/1     Pending             0          38m
onap-policy-postgres-replica-6887f9856f-nmk8v       0/1     Pending             0          38m
onap-postgres-primary-66c8dff577-nltcr              0/1     Pending             0          38m



 kubectl get app onap-gitops-hpe16 -n argocd"

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   OutOfSync     Degraded

 kubectl get app onap-gitops-hpe16 -n argocd"

NAME                SYNC STATUS   HEALTH STATUS
onap-gitops-hpe16   OutOfSync     Degraded


 kubectl get pods -n onap"

NAME                                                READY   STATUS             RESTARTS        AGE
mariadb-galera-0                                    1/1     Running            0               25m
onap-dcae-ves-collector-546c98c765-jp2g8            2/2     Running            0               25m
onap-policy-apex-pdp-d458bbcbb-n86ms                1/1     Running            0               25m
onap-policy-api-85d85ccf84-xjvw5                    0/1     Init:0/4           2 (4m20s ago)   25m
onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7-zql6r    1/1     Running            0               25m
onap-policy-clamp-ac-http-ppnt-5d46545bfb-5vgn6     1/1     Running            0               25m
onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c-wpndr      1/1     Running            0               25m
onap-policy-clamp-ac-kserve-ppnt-77f55f9c75-hrcq7   1/1     Running            0               25m
onap-policy-clamp-ac-pf-ppnt-757fdb4687-q64cq       1/1     Running            0               25m
onap-policy-clamp-runtime-acm-78c6d8588c-5sz6s      0/1     Init:0/2           2 (4m54s ago)   25m
onap-policy-pap-668b55cfd-6qk89                     0/1     Init:0/2           2 (4m24s ago)   25m
onap-policy-postgres-primary-f76cb64c-szt2r         0/1     Pending            0               63m
onap-policy-postgres-replica-6887f9856f-nmk8v       0/1     Pending            0               63m
onap-postgres-primary-66c8dff577-nltcr              0/1     Pending            0               63m
onap-postgres-replica-86b64c8455-pbvd9              0/1     Pending            0               63m
onap-strimzi-entity-operator-587b94dc9-z75sp        0/2     CrashLoopBackOff   18 (61s ago)    25m
onap-strimzi-kafka-bridge-857dff6bdd-mbvj7          1/1     Running            0               25m

 kubectl get pvc -n onap"

NAME                       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
storage-mariadb-galera-0   Bound    pvc-8a4cfa4c-3ac6-4d4c-b5c4-88cc3b0b9030   3Gi        RWO            smo-storage    63m

 kubectl describe kafka onap-strimzi -n onap | head -n 50"

Name:         onap-strimzi
Namespace:    onap
Labels:       app.kubernetes.io/instance=onap-gitops-hpe16
Annotations:  strimzi.io/kraft: enabled
              strimzi.io/node-pools: enabled
API Version:  kafka.strimzi.io/v1beta2
Kind:         Kafka
Metadata:
  Creation Timestamp:  2026-01-23T18:11:08Z
  Generation:          1
  Resource Version:    842503
  UID:                 9ff44fbb-5976-4551-a8bd-e59616378bff
Spec:
  Entity Operator:
    Template:
      Pod:
        Image Pull Secrets:
        Security Context:
          Seccomp Profile:
            Type:  RuntimeDefault
      Topic Operator Container:
        Security Context:
          Allow Privilege Escalation:  false
          Capabilities:
            Drop:
              ALL
              CAP_NET_RAW
          Read Only Root Filesystem:  true
          Run As Group:               1001
          Run As Non Root:            true
          Run As User:                1001
      User Operator Container:
        Security Context:
          Allow Privilege Escalation:  false
          Capabilities:
            Drop:
              ALL
              CAP_NET_RAW
          Read Only Root Filesystem:  true
          Run As Group:               1001
          Run As Non Root:            true
          Run As User:                1001
    Topic Operator:
      Resources:
        Limits:
          Cpu:     2
          Memory:  2Gi
        Requests:
          Cpu:     100m
          Memory:  1Gi

 kubectl get pods -n onap | grep -i kafka"

onap-strimzi-kafka-bridge-857dff6bdd-mbvj7          1/1     Running            0               33m

 kubectl get pods -n onap --field-selector=status.phase=Running"

NAME                                                READY   STATUS             RESTARTS        AGE
mariadb-galera-0                                    1/1     Running            0               34m
onap-dcae-ves-collector-546c98c765-jp2g8            2/2     Running            0               33m
onap-policy-apex-pdp-d458bbcbb-n86ms                1/1     Running            0               33m
onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7-zql6r    1/1     Running            0               33m
onap-policy-clamp-ac-http-ppnt-5d46545bfb-5vgn6     1/1     Running            0               33m
onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c-wpndr      1/1     Running            0               33m
onap-policy-clamp-ac-kserve-ppnt-77f55f9c75-hrcq7   1/1     Running            0               33m
onap-policy-clamp-ac-pf-ppnt-757fdb4687-q64cq       1/1     Running            0               33m
onap-strimzi-entity-operator-587b94dc9-z75sp        0/2     CrashLoopBackOff   21 (114s ago)   33m
onap-strimzi-kafka-bridge-857dff6bdd-mbvj7          1/1     Running            0               33m

 kubectl get pods -n onap"

NAME                                                READY   STATUS             RESTARTS         AGE
mariadb-galera-0                                    1/1     Running            0                41m
onap-dcae-ves-collector-546c98c765-jp2g8            2/2     Running            0                41m
onap-policy-apex-pdp-d458bbcbb-n86ms                1/1     Running            0                41m
onap-policy-api-85d85ccf84-xjvw5                    0/1     Init:0/4           4 (46s ago)      41m
onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7-zql6r    1/1     Running            0                41m
onap-policy-clamp-ac-http-ppnt-5d46545bfb-5vgn6     1/1     Running            0                41m
onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c-wpndr      1/1     Running            0                41m
onap-policy-clamp-ac-kserve-ppnt-77f55f9c75-hrcq7   1/1     Running            0                41m
onap-policy-clamp-ac-pf-ppnt-757fdb4687-q64cq       1/1     Running            0                41m
onap-policy-clamp-runtime-acm-78c6d8588c-5sz6s      0/1     Init:0/2           4 (80s ago)      41m
onap-policy-pap-668b55cfd-6qk89                     0/1     Init:0/2           4 (50s ago)      41m
onap-policy-postgres-primary-f76cb64c-h95d6         0/1     Pending            0                8m39s
onap-policy-postgres-replica-6887f9856f-sl2k7       0/1     Pending            0                8m39s
onap-postgres-primary-66c8dff577-7bs9q              0/1     Pending            0                8m39s
onap-postgres-replica-86b64c8455-7r9n8              0/1     Pending            0                8m39s
onap-strimzi-entity-operator-587b94dc9-z75sp        0/2     CrashLoopBackOff   24 (4m18s ago)   41m
onap-strimzi-kafka-bridge-857dff6bdd-mbvj7          1/1     Running            0                41m

~/…/deployoran $ cd /home/agnik/Desktop/deployoran && python3 snapshot_resources.py

Fetching policy...
Saved 54 resources to /home/agnik/Desktop/deployoran/1Algooverride/policy_full.yaml
Fetching dcae...
Saved 7 resources to /home/agnik/Desktop/deployoran/1Algooverride/dcae_full.yaml
Fetching strimzi...
Saved 27 resources to /home/agnik/Desktop/deployoran/1Algooverride/strimzi_full.yaml
Fetching postgres...
Saved 24 resources to /home/agnik/Desktop/deployoran/1Algooverride/postgres_full.yaml

~/…/deployoran $ sshpass -p 1234 ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu "export KUBECONFIG=~/.kube/config; kubectl get deployment -n strimzi-system"

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
strimzi-cluster-operator   1/1     1            1           21h


~/…/deployoran $ cat <<'EOF' > /home/agnik/Desktop/deployoran/capture_strimzi_operator.py
import subprocess
import yaml
import os

SSH_CMD = "sshpass -p 1234 ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu"
KUBECTL = "export KUBECONFIG=~/.kube/config; kubectl"
DEST_FILE = "/home/agnik/Desktop/deployoran/1Algooverride/strimzi_operator.yaml"

def clean_metadata(doc):
    if not doc: return None
    if 'metadata' in doc:
        for field in ['uid', 'resourceVersion', 'generation', 'creationTimestamp', 'status', 'managedFields', 'ownerReferences', 'selfLink']:
            if field in doc['metadata']:
                del doc['metadata'][field]
        # Clean annotations
        if 'annotations' in doc['metadata']:
            if 'kubectl.kubernetes.io/last-applied-configuration' in doc['metadata']['annotations']:
                del doc['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']
            if 'deployment.kubernetes.io/revision' in doc['metadata']['annotations']:
                del doc['metadata']['annotations']['deployment.kubernetes.io/revision']
            if not doc['metadata']['annotations']:
                del doc['metadata']['annotations']
    
    if 'status' in doc:
        del doc['status']
        
    return doc

print("Capturing Strimzi operator from strimzi-system namespace...")
cmd = f"{SSH_CMD} '{KUBECTL} get deployment,clusterrole,clusterrolebinding,serviceaccount,configmap -n strimzi-system -l app.kubernetes.io/name=strimzi -o yaml'"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error: {result.stderr}")
    exit(1)

data = yaml.safe_load_all(result.stdout)
docs = list(data)

if 'items' in docs[0]:
    items = docs[0]['items']
else:
    items = docs

cleaned_items = []
for item in items:
    clean = clean_metadata(item)
    if clean:
        cleaned_items.append(clean)

print(f"Captured {len(cleaned_items)} resources")

with open(DEST_FILE, 'w') as f:
    yaml.dump_all(cleaned_items, f, default_flow_style=False, sort_keys=False)

print(f"Saved to {DEST_FILE}")
EOF
python3 /home/agnik/Desktop/deployoran/capture_strimzi_operator.py


~/…/deployoran $ python3 /home/agnik/Desktop/deployoran/capture_strimzi_operator.py

Capturing Strimzi operator from strimzi-system namespace...

~/…/deployoran $ ls -lah /home/agnik/Desktop/deployoran/1Algooverride/*.yaml | grep -E "(strimzi|policy|dcae|postgres)"

-rw-rw-r-- 1 agnik agnik  16K Jan 24 10:50 /home/agnik/Desktop/deployoran/1Algooverride/dcae_full.yaml
-rw-rw-r-- 1 agnik agnik 176K Jan 24 10:50 /home/agnik/Desktop/deployoran/1Algooverride/policy_full.yaml
-rw-rw-r-- 1 agnik agnik  54K Jan 24 10:52 /home/agnik/Desktop/deployoran/1Algooverride/postgres_full.yaml
-rw-rw-r-- 1 agnik agnik  90K Jan 24 10:51 /home/agnik/Desktop/deployoran/1Algooverride/strimzi_full.yaml
-rw-rw-r-- 1 agnik agnik    0 Jan 24 10:54 /home/agnik/Desktop/deployoran/1Algooverride/strimzi_operator.yaml


~/…/deployoran $ timeout 30 sshpass -p 1234 ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu "export KUBECONFIG=~/.kube/config; kubectl get deployment,serviceaccount -n strimzi-system -l app.kubernetes.io/name=strimzi -o yaml" > /tmp/strimzi_operator_raw.yaml 2>&1 && python3 -c "
import yaml
with open('/tmp/strimzi_operator_raw.yaml') as f:
    data = yaml.safe_load_all(f)
    docs = list(data)
    if docs and 'items' in docs[0]:
        items = docs[0]['items']
    else:
        items = docs
    
    cleaned = []
    for item in items:
        if 'metadata' in item:
            for field in ['uid', 'resourceVersion', 'generation', 'creationTimestamp', 'status', 'managedFields', 'ownerReferences', 'selfLink']:
                item['metadata'].pop(field, None)
            if 'annotations' in item['metadata']:
                item['metadata']['annotations'].pop('kubectl.kubernetes.io/last-applied-configuration', None)
                item['metadata']['annotations'].pop('deployment.kubernetes.io/revision', None)
                if not item['metadata']['annotations']:
                    del item['metadata']['annotations']
        item.pop('status', None)
        cleaned.append(item)
    
    with open('/home/agnik/Desktop/deployoran/1Algooverride/strimzi_operator.yaml', 'w') as out:
        yaml.dump_all(cleaned, out, default_flow_style=False, sort_keys=False)
    
    print(f'Saved {len(cleaned)} Strimzi operator resources')
"

Saved 0 Strimzi operator resources



~/…/deployoran $ sleep 30 && sshpass -p 1234 ssh -o StrictHostKeyChecking=no agnikmisra@hpe16.anuket.iol.unh.edu "export KUBECONFIG=~/.kube/config; kubectl get pods -n onap -o wide | sort -k1"

NAME                                                READY   STATUS     RESTARTS       AGE     IP            NODE        NOMINATED NODE   READINESS GATES
mariadb-galera-0                                    1/1     Running    0              6m33s   10.244.0.35   nearrtric   <none>           <none>
onap-dcae-ves-collector-546c98c765-tgmgh            2/2     Running    0              6m33s   10.244.0.31   nearrtric   <none>           <none>
onap-policy-apex-pdp-d458bbcbb-br89q                1/1     Running    0              6m33s   10.244.0.29   nearrtric   <none>           <none>
onap-policy-api-85d85ccf84-jwjxk                    0/1     Init:0/4   0              6m31s   10.244.0.34   nearrtric   <none>           <none>
onap-policy-clamp-ac-a1pms-ppnt-6b7896f5b7-47bz8    1/1     Running    0              6m33s   10.244.0.30   nearrtric   <none>           <none>
onap-policy-clamp-ac-http-ppnt-5d46545bfb-j8crw     1/1     Running    0              6m33s   10.244.0.24   nearrtric   <none>           <none>
onap-policy-clamp-ac-k8s-ppnt-5df98fdc6c-nkrhj      1/1     Running    0              6m33s   10.244.0.27   nearrtric   <none>           <none>
onap-policy-clamp-ac-kserve-ppnt-77f55f9c75-6bzzr   1/1     Running    0              6m33s   10.244.0.23   nearrtric   <none>           <none>
onap-policy-clamp-ac-pf-ppnt-757fdb4687-7bz8p       1/1     Running    0              6m33s   10.244.0.25   nearrtric   <none>           <none>
onap-policy-clamp-runtime-acm-78c6d8588c-rxf4g      0/1     Init:0/2   0              6m32s   10.244.0.32   nearrtric   <none>           <none>
onap-policy-pap-668b55cfd-zq9tm                     0/1     Init:0/2   0              6m33s   10.244.0.26   nearrtric   <none>           <none>
onap-policy-postgres-primary-f76cb64c-z76dw         0/1     Pending    0              6m33s   <none>        <none>      <none>           <none>
onap-policy-postgres-replica-6887f9856f-gcgb5       0/1     Pending    0              6m31s   <none>        <none>      <none>           <none>
onap-postgres-primary-66c8dff577-5r69z              0/1     Pending    0              6m33s   <none>        <none>      <none>           <none>
onap-postgres-replica-86b64c8455-9jfhg              0/1     Pending    0              6m32s   <none>        <none>      <none>           <none>
onap-strimzi-entity-operator-587b94dc9-lggd2        1/2     Running    11 (12s ago)   6m33s   10.244.0.28   nearrtric   <none>           <none>
onap-strimzi-kafka-bridge-857dff6bdd-sht84          1/1     Running    0              6m31s   10.244.0.33   nearrtric   <none>           <none>
onap-strimzi-onap-strimzi-broker-0                  1/1     Running    0              76s     10.244.0.36   nearrtric   <none>           <none>
onap-strimzi-onap-strimzi-controller-1              1/1     Running    0              76s     10.244.0.37   nearrtric   <none>           <none>
```

