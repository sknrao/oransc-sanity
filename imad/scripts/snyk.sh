#!/bin/bash

# Configuration
GERRIT_BASE="https://gerrit.o-ran-sc.org/r"
WORK_DIR="./snyk-scan-workspace"
OUTPUT_DIR="./snyk-results"

# List of repositories to scan
REPOS=(
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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR_ABS="$SCRIPT_DIR/$WORK_DIR"
OUTPUT_DIR_ABS="$SCRIPT_DIR/$OUTPUT_DIR"

# Create directories
mkdir -p "$WORK_DIR_ABS"
mkdir -p "$OUTPUT_DIR_ABS"

# Summary file
SUMMARY_FILE="$OUTPUT_DIR_ABS/scan-summary.txt"
echo "Snyk Scan Summary - $(date)" > "$SUMMARY_FILE"
echo "================================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Function to install Python dependencies
install_python_deps() {
    # Check for requirements files
    if [ -f "requirements.txt" ]; then
        echo -e "${BLUE}Found Python project (requirements.txt), installing dependencies...${NC}"
        
        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        echo "Upgrading pip..."
        pip3 install --upgrade pip > /dev/null 2>&1
        
        echo "Installing dependencies from requirements.txt..."
        if pip3 install -r requirements.txt > /dev/null 2>&1; then
            echo -e "${GREEN}Python dependencies installed successfully${NC}"
            deactivate
            return 0
        else
            echo -e "${YELLOW}Some Python dependencies failed to install, but continuing...${NC}"
            deactivate
            return 1
        fi
    fi
    
    if [ -f "setup.py" ]; then
        echo -e "${BLUE}Found Python project (setup.py), installing package...${NC}"
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip3 install --upgrade pip > /dev/null 2>&1
        pip3 install -e . > /dev/null 2>&1
        deactivate
        return 0
    fi
    
    if [ -f "Pipfile" ]; then
        echo -e "${BLUE}Found Python project (Pipfile)${NC}"
        if command -v pipenv &> /dev/null; then
            echo "Installing with pipenv..."
            pipenv install > /dev/null 2>&1
        else
            echo -e "${YELLOW}pipenv not installed, skipping${NC}"
        fi
        return 0
    fi
    
    if [ -f "pyproject.toml" ]; then
        echo -e "${BLUE}Found Python project (pyproject.toml)${NC}"
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip3 install --upgrade pip > /dev/null 2>&1
        pip3 install . > /dev/null 2>&1
        deactivate
        return 0
    fi
    
    return 0
}

# Function to install Ruby dependencies
install_ruby_deps() {
    if [ -f "Gemfile" ]; then
        echo -e "${BLUE}Found Ruby project (Gemfile), installing dependencies...${NC}"
        if command -v bundle &> /dev/null; then
            if bundle install > /dev/null 2>&1; then
                echo -e "${GREEN}Ruby dependencies installed successfully${NC}"
            else
                echo -e "${RED}Failed to install Ruby dependencies (continuing anyway)${NC}"
            fi
        else
            echo -e "${YELLOW}bundler not installed, skipping Ruby dependencies${NC}"
        fi
        return 0
    fi
    return 0
}

# Function to install PHP dependencies
install_php_deps() {
    if [ -f "composer.json" ]; then
        echo -e "${BLUE}Found PHP project (composer.json), installing dependencies...${NC}"
        if command -v composer &> /dev/null; then
            if composer install --no-interaction > /dev/null 2>&1; then
                echo -e "${GREEN}PHP dependencies installed successfully${NC}"
            else
                echo -e "${RED}Failed to install PHP dependencies (continuing anyway)${NC}"
            fi
        else
            echo -e "${YELLOW}composer not installed, skipping PHP dependencies${NC}"
        fi
        return 0
    fi
    return 0
}

# Function to detect project type
detect_project_type() {
    local types=()
    
    # Check for different project types
    [ -f "package.json" ] && types+=("Node.js")
    [ -f "go.mod" ] && types+=("Go")
    [ -f "pom.xml" ] && types+=("Java/Maven")
    [ -f "build.gradle" ] && types+=("Java/Gradle")
    [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "Pipfile" ] && types+=("Python")
    [ -f "Gemfile" ] && types+=("Ruby")
    [ -f "composer.json" ] && types+=("PHP")
    [ -f "*.csproj" ] 2>/dev/null && types+=(".NET")
    [ -f "Cargo.toml" ] && types+=("Rust")
    
    if [ ${#types[@]} -eq 0 ]; then
        echo -e "${YELLOW}No recognized project type detected${NC}"
    else
        echo -e "${BLUE}Detected project type(s): ${types[*]}${NC}"
    fi
}

# Function to install dependencies based on project type
install_dependencies() {
    detect_project_type
    
    # Install dependencies for languages that need it
    install_python_deps
    install_ruby_deps
    install_php_deps
    
    # For other languages, Snyk doesn't need dependency installation
    if [ -f "package.json" ]; then
        echo -e "${GREEN}Node.js project detected - Snyk will analyze package.json directly${NC}"
    fi
    
    if [ -f "go.mod" ]; then
        echo -e "${GREEN}Go project detected - Snyk will analyze go.mod directly${NC}"
    fi
    
    if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        echo -e "${GREEN}Java project detected - Snyk will analyze build files directly${NC}"
    fi
}

# Function to normalize JSON (convert single object to array if needed)
normalize_json() {
    local json_file=$1
    local json_type=$(jq -r 'type' "$json_file" 2>/dev/null)
    
    if [ "$json_type" = "object" ]; then
        # Check if it's an error object
        local is_error=$(jq -r '.ok // "not_found"' "$json_file" 2>/dev/null)
        if [ "$is_error" = "false" ]; then
            # It's an error, don't normalize
            return 1
        fi
        
        # It's a single result, wrap it in an array
        echo "Normalizing single object to array..."
        jq '[.]' "$json_file" > "${json_file}.tmp" && mv "${json_file}.tmp" "$json_file"
    fi
    
    return 0
}

# Function to scan a single repository
scan_repo() {
    local repo=$1
    local repo_safe="${repo//\//_}"
    local json_file="$OUTPUT_DIR_ABS/${repo_safe}.json"
    local err_file="$OUTPUT_DIR_ABS/${repo_safe}.err"
    
    echo ""
    echo "========================================"
    echo -e "${YELLOW}Processing repository: $repo${NC}"
    echo "========================================"
    
    # Clone repository
    cd "$WORK_DIR_ABS" || exit 1
    if [ -d "$repo_safe" ]; then
        echo "Repository already exists, pulling latest changes..."
        cd "$repo_safe" || exit 1
        git pull
    else
        echo "Cloning repository..."
        if ! git clone "${GERRIT_BASE}/${repo}" "$repo_safe"; then
            echo -e "${RED}Failed to clone $repo${NC}"
            echo "FAILED: $repo (clone error)" >> "$SUMMARY_FILE"
            echo "" >> "$SUMMARY_FILE"
            cd "$SCRIPT_DIR" || exit 1
            return 1
        fi
        cd "$repo_safe" || exit 1
    fi
    
    # Install dependencies based on project type
    install_dependencies
    
    # Run Snyk scan
    echo ""
    echo "Running Snyk scan..."
    
    # If virtual environment exists, activate it for the scan
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    snyk test --json --all-projects > "$json_file" 2> "$err_file"
    
    # Deactivate virtual environment if it was activated
    if [ -d "venv" ]; then
        deactivate
    fi
    
    # Check if scan produced valid JSON
    if ! jq empty "$json_file" 2>/dev/null; then
        echo -e "${RED}Snyk scan produced invalid JSON for $repo${NC}"
        echo "Check error file: $err_file"
        echo "FAILED: $repo (invalid JSON output)" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        cd "$SCRIPT_DIR" || exit 1
        return 1
    fi
    
    # Check if it's an error response (object with ok:false)
    is_error=$(jq -r '.ok // "not_found"' "$json_file" 2>/dev/null)
    if [ "$is_error" = "false" ]; then
        error_msg=$(jq -r '.error // "Unknown error"' "$json_file" 2>/dev/null)
        echo -e "${RED}Snyk scan failed for $repo${NC}"
        echo -e "${RED}Error: $error_msg${NC}"
        
        echo "FAILED: $repo (dependency resolution error)" >> "$SUMMARY_FILE"
        echo "  Error: $error_msg" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        cd "$SCRIPT_DIR" || exit 1
        return 1
    fi
    
    # Normalize JSON (convert single object to array if needed)
    if ! normalize_json "$json_file"; then
        echo -e "${RED}Failed to process scan results for $repo${NC}"
        echo "FAILED: $repo (error in scan results)" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        cd "$SCRIPT_DIR" || exit 1
        return 1
    fi
    
    # Parse results (now guaranteed to be an array)
    critical=$(jq '[.[].vulnerabilities[]? | select(.severity=="critical")] | length' "$json_file" 2>/dev/null || echo 0)
    high=$(jq '[.[].vulnerabilities[]? | select(.severity=="high")] | length' "$json_file" 2>/dev/null || echo 0)
    medium=$(jq '[.[].vulnerabilities[]? | select(.severity=="medium")] | length' "$json_file" 2>/dev/null || echo 0)
    low=$(jq '[.[].vulnerabilities[]? | select(.severity=="low")] | length' "$json_file" 2>/dev/null || echo 0)
    total=$((critical + high + medium + low))
    
    # Print results
    echo ""
    echo -e "${GREEN}✓ Scan completed successfully for $repo${NC}"
    echo "  Critical: $critical | High: $high | Medium: $medium | Low: $low | Total: $total"
    
    # Package managers detected
    echo "  Package managers:"
    jq -r '.[].packageManager' "$json_file" 2>/dev/null | sort -u | sed 's/^/    - /' || echo "    - None detected"
    
    # Target files scanned
    echo "  Target files:"
    jq -r '.[].targetFile' "$json_file" 2>/dev/null | sed 's/^/    - /' || echo "    - None"
    
    # Add to summary
    echo "$repo:" >> "$SUMMARY_FILE"
    echo "  Critical: $critical | High: $high | Medium: $medium | Low: $low | Total: $total" >> "$SUMMARY_FILE"
    
    # List vulnerabilities if any exist
    if [ "$total" -gt 0 ]; then
        echo "  Vulnerabilities:" >> "$SUMMARY_FILE"
        jq -r '.[] | .packageManager as $pm | .vulnerabilities[]? | "    [\(.severity | ascii_upcase)] \($pm): \(.title)"' "$json_file" >> "$SUMMARY_FILE"
    fi
    echo "" >> "$SUMMARY_FILE"
    
    cd "$SCRIPT_DIR" || exit 1
    return 0
}

# Main execution
echo "========================================="
echo "  Snyk Multi-Repository Scanner"
echo "========================================="
echo "Work directory: $WORK_DIR_ABS"
echo "Output directory: $OUTPUT_DIR_ABS"
echo ""

successful=0
failed=0

for repo in "${REPOS[@]}"; do
    if scan_repo "$repo"; then
        ((successful++))
    else
        ((failed++))
    fi
done

# Final summary
echo ""
echo "========================================="
echo -e "${GREEN}Scan Complete!${NC}"
echo "========================================="
echo "Successful: $successful"
echo "Failed: $failed"
echo ""
echo "Results saved to: $OUTPUT_DIR_ABS"
echo "Summary file: $SUMMARY_FILE"

# Display summary
echo ""
echo "=== DETAILED SUMMARY ==="
cat "$SUMMARY_FILE"