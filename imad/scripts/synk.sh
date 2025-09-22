#!/bin/bash

#NOTE: THIS ISNT WORKING, NEEDS TO BE FIXED

repos=(
    "oam"
    "aiml-fw/awmf/tm"
    "it/dep"
    "ci-management"
    "smo/teiv"
    "aiml-fw/aimlfw-dep"
    "ric-app/ad-cell"
    "aiml-fw/awmf/modelmgmtservice"
    "nonrtric/plt/rappmanager"
    "it/test"
    "pti/rtp"
    "oam/oam-controller"
    "portal/aiml-dashboard"
    "nonrtric"
    "pti/o2"
    "smo/o2"
    "nonrtric/plt/a1policymanagementservice"
    "aiml-fw/athp/pipeline-components"
    "o-du/l2"
    "nonrtric/plt/sme"
    "aiml-fw/athp/sdk/model-storage"
    "nonrtric/plt/ranpm"
    "aiml-fw/athp/tps/kubeflow-adapter"
    "sim/a1-interface"
    "aiml-fw/athp/data-extraction"
    "aiml-fw/athp/sdk/feature-store"
    "doc"
    "it/tifg"
    "nonrtric/plt/informationcoordinatorservice"
    "sim/o1-ofhmp-interfaces"
    "ric-plt/conflictmgr"
    "aiml-fw/apm/monitoring-agent"
    "aiml-fw/apm/analysis-module"
    "aiml-fw/apm/influx-wrapper"
    "aiml-fw/apm/monitoring-server"
    "o-du/phy"
    ".github"
    "nonrtric/plt/dmaapadapter"
    "nonrtric/plt/rappcatalogue"
    "nonrtric/rapp/orufhrecovery"
    "ric-plt/ric-dep"
    "ric-plt/xapp-frame-rust"
    "sim/ns3-o-ran-e2"
    "aiml-fw/aihp/ips/kserve-adapter"
    "aiml-fw/aihp/tps/kserve-adapter"
    "nonrtric/plt/dmaapmediatorproducer"
    "nonrtric/plt/helmmanager"
    "nonrtric/rapp/healthcheck"
    "nonrtric/rapp/ransliceassurance"
    "portal/nonrtric-controlpanel"
)

# Base URL - change this to your Git server
BASE_URL="https://github.com/o-ran-sc"

# Create results directory
mkdir -p snyk_results
cd snyk_results

echo "Starting Snyk scans..."

for repo in "${repos[@]}"; do
    echo "Processing: $repo"
    
    # Clone repo
    git clone "$BASE_URL/$repo.git" 2>/dev/null || echo "Failed to clone $repo"
    
    if [ -d "$(basename $repo)" ]; then
        cd "$(basename $repo)"
        
        # Run Snyk scans
        echo "  Running dependency scan..."
        snyk test --json > "../${repo//\//_}_deps.json" 2>/dev/null || echo "  Dependency scan failed"
        
        echo "  Running code scan..."
        snyk code test --json > "../${repo//\//_}_code.json" 2>/dev/null || echo "  Code scan failed"
        
        cd ..
    fi
    echo "---"
done

echo "Done! Results in snyk_results/"