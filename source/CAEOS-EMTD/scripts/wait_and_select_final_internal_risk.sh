#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
ENTROPY="$PROJECT_ROOT/results/entropy_confirmation/confirmation.json"
FUSION="$PROJECT_ROOT/results/entropy_cauchy_fusion_confirmation/confirmation.json"
MANIFEST="$PROJECT_ROOT/selection/final_internal_risk_decision_manifest.json"
OUTPUT_DIR="$PROJECT_ROOT/results/final_internal_risk_selection"
LOG="$OUTPUT_DIR/waiter.log"
LOCK_DIR="$OUTPUT_DIR/waiter.lock.d"

mkdir -p "$OUTPUT_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another final internal-risk selector is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$ENTROPY" || ! -f "$FUSION" ]]; do
  entropy_ready=0
  fusion_ready=0
  [[ -f "$ENTROPY" ]] && entropy_ready=1
  [[ -f "$FUSION" ]] && fusion_ready=1
  printf '%s waiting for held-out confirmations entropy=%s fusion=%s\n' \
    "$(date -Is)" "$entropy_ready" "$fusion_ready" >> "$LOG"
  sleep 300
done

verify_sha() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

cd "$PROJECT_ROOT"
verify_sha "0850bc060c832e9169791ab28fd1b73a71e6a273e0b0d47d007fb1be29ed1272" \
  select_final_internal_risk.py
verify_sha "f152a99ba6c82b48799084bd9dcdbbf18e9a43405fded9c1f7b744f61cbb224d" \
  "$MANIFEST"
printf '%s selecting final internal CAEOS risk with frozen decision tree\n' \
  "$(date -Is)" >> "$LOG"
"$CONDA" run -n py3.9 python select_final_internal_risk.py \
  --entropy-confirmation "$ENTROPY" \
  --fusion-confirmation "$FUSION" \
  --decision-manifest "$MANIFEST" \
  --output "$OUTPUT_DIR/selection.json" \
  --markdown-output "$OUTPUT_DIR/selection.md" \
  --bootstrap-repetitions 10000 \
  --bootstrap-seed 20260717 >> "$LOG" 2>&1
touch "$OUTPUT_DIR/selection_complete"
printf '%s final internal CAEOS risk selection complete\n' "$(date -Is)" >> "$LOG"
