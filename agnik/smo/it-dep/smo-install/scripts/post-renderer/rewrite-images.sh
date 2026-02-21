#!/usr/bin/env bash
set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_MAP="$SCRIPT_DIR/image-map.yaml"
STRICT_MODE="${STRICT_MODE:-false}"
DEBUG="${DEBUG:-true}"

log() {
  [[ "$DEBUG" == "true" ]] && echo "[DEBUG] $*" >&2
}

fail() {
  echo "[ERROR] $*" >&2
  exit 1
}

[[ -f "$IMAGE_MAP" ]] || fail "image map not found: $IMAGE_MAP"

declare -A MAP

while IFS=$'\t' read -r key value; do
  MAP["$key"]="$value"
done < <(
  yq eval '
    to_entries
    | .[]
    | [.key, .value]
    | @tsv
  ' "$IMAGE_MAP"
)

#for k in "${!MAP[@]}"; do
# echo "  KEY=[$k] VALUE=[${MAP[$k]}]"
#done >&2


# Read rendered YAML
INPUT="$(cat)"

# Extract image lines only (string images)
IMAGES=$(echo "$INPUT" | yq eval '.. | select(has("image")) | .image' - 2>/dev/null | grep -v '^-' || true)
log "Found images: ${IMAGES}"

OUTPUT="$INPUT"

for img in $IMAGES; do
  name="$(echo "$img" | awk -F/ '{print $NF}' | awk -F: '{print $1}')"
  log "Processing image: $img (name: $name)"
  if [[ -n "${MAP[$name]:-}" ]]; then
    log "✓ Rewriting $img -> ${MAP[$name]}"
    escaped_img=$(printf '%s\n' "$img" | sed 's/[.[\*^$(){}+?|]/\\&/g')
    OUTPUT="$(echo "$OUTPUT" | sed -E \
      "s|(image:[[:space:]]*)[\"']?$escaped_img[\"']?|\1\"${MAP[$name]}\"|g"
    )"
  else
    log "○ No mapping for: $img"
    if [[ "$STRICT_MODE" == "true" ]]; then
      fail "Image not found in image-map.yaml: $img"
    fi
  fi
done

log "Post-rendering complete"

echo "$OUTPUT"

