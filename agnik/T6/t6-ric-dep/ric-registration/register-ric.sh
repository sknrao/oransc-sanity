#!/usr/bin/env bash
set -euo pipefail

############################################
# Load configuration
############################################

CONFIG_FILE="${1:-config.env}"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "[ERROR] Config file '$CONFIG_FILE' not found"
  exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG_FILE"

############################################
# Validation
############################################

log() { echo "[INFO] $*"; }
err() { echo "[ERROR] $*"; exit 1; }

for bin in curl jq; do
  command -v "$bin" >/dev/null 2>&1 || err "Required command '$bin' not found"
done

: "${RIC_NAME:?Missing RIC_NAME}"
: "${RIC_BASE_URL:?Missing RIC_BASE_URL}"
: "${A1_NODEPORT:?Missing A1_NODEPORT}"
: "${ENABLE_CONTROLLER:?Missing ENABLE_CONTROLLER}"

############################################
# A1PMS base URL
############################################

# UPDATED: Correct API Path for A1PMS
A1_BASE="http://localhost:${A1_NODEPORT}/a1-policy/v2"
log "Using A1PMS base URL: $A1_BASE"

TMP_ORIG="/tmp/a1pms_config_orig.json"
TMP_NEW="/tmp/a1pms_config_new.json"

log "Fetching current A1PMS configuration..."
HTTP_CODE=$(curl -s -o "$TMP_ORIG" -w '%{http_code}' "${A1_BASE}/configuration" || echo 000)

# UPDATED: Handle 404/204 (No config exists yet)
if [ "$HTTP_CODE" = "404" ] || [ "$HTTP_CODE" = "204" ]; then
    log "No existing configuration found (HTTP $HTTP_CODE). Starting with empty list."
    echo '{"config": {"ric": []}}' > "$TMP_ORIG"
elif [ "$HTTP_CODE" != "200" ]; then
     err "GET /configuration failed (HTTP $HTTP_CODE)"
else 
     # If content is empty or invalid JSON, reset it
     if ! jq '.' "$TMP_ORIG" >/dev/null 2>&1; then
        log "Existing configuration was invalid/empty. Resetting."
        echo '{"config": {"ric": []}}' > "$TMP_ORIG"
     fi
fi

log "Updating RIC '$RIC_NAME' (controller enabled: $ENABLE_CONTROLLER)"

jq \
  --arg name "$RIC_NAME" \
  --arg url "$RIC_BASE_URL" \
  --arg ctrl "${CONTROLLER_NAME:-}" \
  --arg enable_ctrl "$ENABLE_CONTROLLER" \
  --arg ctrl_url "${CONTROLLER_BASE_URL:-}" \
  --arg ctrl_user "${CONTROLLER_USERNAME:-}" \
  --arg ctrl_pass "${CONTROLLER_PASSWORD:-}" \
  '
  .config.ric //= [] |
  .config.controller //= [] |
  
  (if $enable_ctrl == "true" then
    .config.controller |= (
      if (.[] | select(.name == $ctrl)) then .
      else . + [{
        name: $ctrl,
        baseUrl: $ctrl_url,
        userName: $ctrl_user,
        password: $ctrl_pass
      }] end
    )
  else . end) |

  .config.ric = (
    (.config.ric | map(select(.name != $name))) + [
      ({
        name: $name,
        baseUrl: $url,
        managedElementIds: [],
        customAdapterClass: "org.onap.ccsdk.oran.a1policymanagementservice.clients.StdA1ClientVersion2"
      } + (if $enable_ctrl == "true" then {controller: $ctrl} else {} end))
    ]
  )
  ' "$TMP_ORIG" > "$TMP_NEW"

log "Pushing updated configuration..."
PUT_CODE=$(curl -s -o /dev/null -w '%{http_code}' \
  -X PUT "${A1_BASE}/configuration" \
  -H 'Content-Type: application/json' \
  --data-binary "@${TMP_NEW}" || echo 000)

[ "$PUT_CODE" = "200" ] || [ "$PUT_CODE" = "201" ] || err "PUT /configuration failed (HTTP $PUT_CODE)"

log "Verifying RIC registration request..."
curl -s "${A1_BASE}/rics?ric_id=${RIC_NAME}" | jq '.' || log "RIC not fully registered/active yet (might take a moment)"

log "✅ RIC '$RIC_NAME' registration updated."
