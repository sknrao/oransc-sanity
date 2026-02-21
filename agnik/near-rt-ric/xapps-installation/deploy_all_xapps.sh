#!/bin/bash
# ==================================================================================
# O-RAN SC xApp Automated Deployment Script (Definitive Version)
# Target: Generic K8s Cluster (Near-RT RIC installed)
# ==================================================================================
set -e

NAMESPACE="ricxapp"
PLATFORM_NAMESPACE="ricplt"

echo ">>> [1/6] Preparing environment..."
sudo kubectl create namespace ${NAMESPACE} 2>/dev/null || true

# Dynamic Service Discovery
echo ">>> Discovering RIC Platform Services..."
E2TERM_RMR_SVC=$(sudo kubectl get svc -n "${PLATFORM_NAMESPACE}" --no-headers | grep "e2term-rmr" | awk '{print $1}' | head -n 1)
E2MGR_RMR_SVC=$(sudo kubectl get svc -n "${PLATFORM_NAMESPACE}" --no-headers | grep "e2mgr-rmr" | awk '{print $1}' | head -n 1)
A1MED_RMR_SVC=$(sudo kubectl get svc -n "${PLATFORM_NAMESPACE}" --no-headers | grep "a1mediator-rmr" | awk '{print $1}' | head -n 1)
RTMGR_RMR_SVC=$(sudo kubectl get svc -n "${PLATFORM_NAMESPACE}" --no-headers | grep "rtmgr-rmr" | awk '{print $1}' | head -n 1)

if [ -z "$E2TERM_RMR_SVC" ] || [ -z "$E2MGR_RMR_SVC" ] || [ -z "$A1MED_RMR_SVC" ]; then
    echo "ERROR: Could not discover all required RIC platform services in namespace ${PLATFORM_NAMESPACE}"
    exit 1
fi

echo "Found Services: E2Term($E2TERM_RMR_SVC), E2Mgr($E2MGR_RMR_SVC), A1Med($A1MED_RMR_SVC), RtMgr($RTMGR_RMR_SVC)"

# Function to deploy an xApp
# Arguments: label_name, descriptor_name, image, config_json_content, [working_dir]
deploy_xapp() {
    local LABEL=$1
    local DESC_NAME=$2
    local IMAGE=$3
    local CONFIG_JSON=$4
    local WDIR=$5

    echo ">>> Deploying xApp: ${DESC_NAME} (label: ${LABEL})..."

    # Create temporary files for ConfigMap
    echo "${CONFIG_JSON}" > "/tmp/${LABEL}-config.json"
    
    cat <<EOF > "/tmp/${LABEL}-local.rt"
newrt|start
rte|10090|${E2TERM_RMR_SVC}.${PLATFORM_NAMESPACE}:38000
rte|10091|${E2TERM_RMR_SVC}.${PLATFORM_NAMESPACE}:38000
rte|12010|${E2MGR_RMR_SVC}.${PLATFORM_NAMESPACE}:3801
rte|12011|${E2MGR_RMR_SVC}.${PLATFORM_NAMESPACE}:3801
rte|12012|${E2MGR_RMR_SVC}.${PLATFORM_NAMESPACE}:3801
rte|20011|${A1MED_RMR_SVC}.${PLATFORM_NAMESPACE}:4562
rte|20012|${A1MED_RMR_SVC}.${PLATFORM_NAMESPACE}:4562
# Self entry
rte|4560|service-${NAMESPACE}-${LABEL}-rmr.${NAMESPACE}:4560
newrt|end
EOF

    sudo kubectl create configmap configmap-${NAMESPACE}-${LABEL} -n ${NAMESPACE} \
      --from-file=config-file.json="/tmp/${LABEL}-config.json" \
      --from-file=local.rt="/tmp/${LABEL}-local.rt" \
      --dry-run=client -o yaml | sudo kubectl apply -f -

    # Prepare workingDir snippet
    local WDIR_SNIPPET=""
    if [ ! -z "$WDIR" ]; then
        WDIR_SNIPPET="workingDir: ${WDIR}"
    fi

    # Create Deployment
    cat <<EOF | sudo kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment-${NAMESPACE}-${LABEL}
  namespace: ${NAMESPACE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${NAMESPACE}-${LABEL}
  template:
    metadata:
      labels:
        app: ${NAMESPACE}-${LABEL}
    spec:
      containers:
      - name: container-${NAMESPACE}-${LABEL}
        image: ${IMAGE}
        imagePullPolicy: IfNotPresent
        ${WDIR_SNIPPET}
        env:
        - name: RMR_SEED_RT
          value: "/opt/route/local.rt"
        - name: RMR_RTG_SVC
          value: "${RTMGR_RMR_SVC}.${PLATFORM_NAMESPACE}:4561"
        - name: RMR_SRC_ID
          value: "service-${NAMESPACE}-${LABEL}-rmr.${NAMESPACE}"
        - name: DBAAS_SERVICE_HOST
          value: "service-ricplt-dbaas-tcp.${PLATFORM_NAMESPACE}"
        - name: CONFIG_FILE
          value: "/opt/ric/config/config-file.json"
        - name: PLT_NAMESPACE
          value: "${PLATFORM_NAMESPACE}"
        ports:
        - name: rmr-data
          containerPort: 4560
        - name: rmr-route
          containerPort: 4561
        - name: http
          containerPort: 8080
        volumeMounts:
        - name: config-volume
          mountPath: /opt/ric/config/config-file.json
          subPath: config-file.json
        - name: config-volume
          mountPath: /playpen/config-file.json
          subPath: config-file.json
        - name: config-volume
          mountPath: /config-file.json
          subPath: config-file.json
        - name: route-volume
          mountPath: /opt/route/local.rt
          subPath: local.rt
      volumes:
      - name: config-volume
        configMap:
          name: configmap-${NAMESPACE}-${LABEL}
      - name: route-volume
        configMap:
          name: configmap-${NAMESPACE}-${LABEL}
EOF

    # Create Service
    cat <<EOF | sudo kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: service-${NAMESPACE}-${LABEL}-rmr
  namespace: ${NAMESPACE}
spec:
  selector:
    app: ${NAMESPACE}-${LABEL}
  ports:
  - name: rmr-data
    port: 4560
    targetPort: 4560
  - name: rmr-route
    port: 4561
    targetPort: 4561
---
apiVersion: v1
kind: Service
metadata:
  name: service-${NAMESPACE}-${LABEL}-http
  namespace: ${NAMESPACE}
spec:
  selector:
    app: ${NAMESPACE}-${LABEL}
  ports:
  - name: http
    port: 8080
    targetPort: 8080
EOF
}

# 1. KPIMON-GO
KPIMON_CONFIG='{
  "xapp_name": "kpimon-go",
  "version": "2.0.2-alpha",
  "containers": [ { "name": "kpimon-go", "image": { "registry": "nexus3.o-ran-sc.org:10004", "name": "o-ran-sc/ric-app-kpimon-go", "tag": "1.0.1" } } ],
  "rmr": { "protPort": "tcp:4560", "maxSize": 2072, "numWorkers": 1, "rxMessages": ["RIC_SUB_RESP", "RIC_INDICATION"], "txMessages": ["RIC_SUB_REQ"], "policies": [] }
}'
deploy_xapp "kpimon-go" "kpimon-go" "nexus3.o-ran-sc.org:10004/o-ran-sc/ric-app-kpimon-go:1.0.1" "${KPIMON_CONFIG}" ""

# 2. AD
AD_CONFIG='{
  "name": "ad", "version": "1.0.2",
  "containers": [ { "name": "ad", "image": { "registry": "nexus3.o-ran-sc.org:10002", "name": "o-ran-sc/ric-app-ad", "tag": "1.0.0" } } ],
  "rmr": { "protPort": "tcp:4560", "maxSize": 2072, "numWorkers": 1, "rxMessages": ["TS_ANOMALY_ACK"], "txMessages": ["TS_ANOMALY_UPDATE"], "policies": [] }
}'
deploy_xapp "ad" "ad" "nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-ad:1.0.0" "${AD_CONFIG}" ""

# 3. QP
QP_CONFIG='{
  "xapp_name": "qp", "version": "0.0.6",
  "containers": [ { "name": "qp", "image": { "registry": "nexus3.o-ran-sc.org:10002", "name": "o-ran-sc/ric-app-qp", "tag": "0.0.5" } } ],
  "rmr": { "protPort": "tcp:4560", "maxSize": 2072, "numWorkers": 1, "rxMessages": ["TS_UE_LIST"], "txMessages": ["TS_QOE_PREDICTION"], "policies": [] }
}'
deploy_xapp "qp" "qp" "nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-qp:0.0.5" "${QP_CONFIG}" ""

# 4. TS (Traffic Steering)
TS_CONFIG='{
    "xapp_name": "trafficxapp", "version": "1.2.5",
    "containers": [ { "name": "trafficxapp", "image": { "registry": "nexus3.o-ran-sc.org:10002", "name": "o-ran-sc/ric-app-ts", "tag": "1.2.5" } } ],
    "messaging": {
        "ports": [
            {
                "name": "rmr-data",
                "container": "trafficxapp",
                "port": 4560,
                "rxMessages": [ "TS_QOE_PREDICTION", "A1_POLICY_REQ", "TS_ANOMALY_UPDATE" ],
                "txMessages": [ "TS_UE_LIST", "TS_ANOMALY_ACK" ],
                "policies": [20008],
                "description": "rmr receive data port for trafficxapp"
            }
        ]
    },
    "rmr": { "protPort": "tcp:4560", "maxSize": 2072, "numWorkers": 1, "txMessages": [ "TS_UE_LIST", "TS_ANOMALY_ACK" ], "rxMessages": [ "TS_QOE_PREDICTION", "A1_POLICY_REQ", "TS_ANOMALY_UPDATE" ], "policies": [20008] },
    "controls": { "ts_control_api": "rest", "ts_control_ep": "http://127.0.0.1:5000/api/echo" }
}'
deploy_xapp "ts" "trafficxapp" "nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-ts:1.2.5" "${TS_CONFIG}" "/playpen"

# 5. RC
RC_CONFIG='{
  "name": "rc", "version": "1.0.1",
  "containers": [ { "name": "rc", "image": { "registry": "nexus3.o-ran-sc.org:10002", "name": "o-ran-sc/ric-app-rc", "tag": "1.0.1" } } ],
  "rmr": { "protPort": "tcp:4560", "maxSize": 2072, "numWorkers": 1, "rxMessages": ["RIC_CONTROL_ACK", "RIC_CONTROL_FAILURE", "RIC_ERROR_INDICATION"], "txMessages": ["RIC_CONTROL_REQ"], "policies": [] },
  "controls": { "ricHOControlgRpcServerPort" : "7777", "logLevel": 4 }
}'
deploy_xapp "rc" "rc" "nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-rc:1.0.1" "${RC_CONFIG}" ""

echo ">>> [DONE] All 5 xApps deployed. Verifying status..."
sudo kubectl get pods -n ${NAMESPACE}
