#!/usr/bin/env bash
set -euo pipefail

RIC_NAME="${RIC_NAME:-hpe16-ric}"
RIC_BASE_URL="${RIC_BASE_URL:-http://hpe16.anuket.iol.unh.edu:30803/A1-P/v2}"
CONTROLLER_NAME="${CONTROLLER_NAME:-controller1}"
A1_NODEPORT="${A1_NODEPORT:-30094}"

log() { echo "[INFO] $*"; }
err() { echo "[ERROR] $*"; exit 1; }

for bin in curl jq; do
  command -v "$bin" >/dev/null 2>&1 || err "Required command '$bin' not found in PATH"
done

A1_BASE="http://localhost:${A1_NODEPORT}/a1-policy-management/v1"
log "Using A1PMS base URL: $A1_BASE"

TMP_ORIG="/tmp/a1pms_config_orig.json"
TMP_NEW="/tmp/a1pms_config_new.json"

log "Fetching current A1PMS configuration (GET /configuration)..."
HTTP_CODE=$(curl -s -o "$TMP_ORIG" -w '%{http_code}' "${A1_BASE}/configuration" || echo 000)

if [ "$HTTP_CODE" != "200" ]; then
  err "getConfiguration failed with HTTP $HTTP_CODE"
fi

log "Adding/updating RIC '$RIC_NAME' -> '$RIC_BASE_URL'..."

jq \
  --arg name "$RIC_NAME" \
  --arg url  "$RIC_BASE_URL" \
  --arg ctrl "$CONTROLLER_NAME" \
  '
  # Ensure config structure
  .config.ric //= [] |
  .config.controller //= [] |

  # Ensure controller exists
  .config.controller |= (
    if (length > 0 and (.[] | select(.name == $ctrl)) != null) then .
    else . + [{
      name: $ctrl,
      baseUrl: "http://sdnc.onap:8282",
      userName: "admin",
      password: "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"
    }] end
  ) |

  # Update RIC: remove existing with same name, add new
  .config.ric = (
    (.config.ric | map(select(.name != $name))) + [{
      name: $name,
      baseUrl: $url,
      controller: $ctrl,
      managedElementIds: []
    }]
  )
  ' "$TMP_ORIG" > "$TMP_NEW" || err "Failed to build new configuration JSON with jq"

log "Pushing updated configuration (PUT /configuration)..."
PUT_CODE=$(curl -s -o /dev/null -w '%{http_code}' \
  -X PUT "${A1_BASE}/configuration" \
  -H 'Content-Type: application/json' \
  --data-binary "@${TMP_NEW}" || echo 000)

if [ "$PUT_CODE" != "200" ]; then
  err "putConfiguration failed with HTTP $PUT_CODE"
fi

log "✅ Configuration updated successfully (HTTP 200)."

log "Verifying configuration now contains '$RIC_NAME'..."
curl -s "${A1_BASE}/configuration" | jq '.config.ric[] | select(.name == "'"$RIC_NAME"'")' \
  || err "RIC '$RIC_NAME' NOT found in configuration after update"

log "Checking RIC repository (GET /rics)..."
curl -s "${A1_BASE}/rics" | jq '.' || log "Warning: failed to pretty-print RIC list"

log "Checking single RIC entry (GET /rics/$RIC_NAME)..."
RIC_JSON=$(curl -s -w '\n%{http_code}' "${A1_BASE}/rics/${RIC_NAME}")
RIC_BODY="$(echo "$RIC_JSON" | sed '$d')"
RIC_CODE="$(echo "$RIC_JSON" | tail -n1)"

if [ "$RIC_CODE" != "200" ]; then
  err "getRic /rics/${RIC_NAME} failed with HTTP $RIC_CODE"
fi

echo "$RIC_BODY" | jq '.' || true

log "✅ Integration complete: RIC '$RIC_NAME' is registered in A1PMS."

