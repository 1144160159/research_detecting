#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
SELECTION_MARKER="$PROJECT_ROOT/results/final_internal_risk_selection/selection_complete"
BASELINE_MARKER="$PROJECT_ROOT/results/strict_v2_20baseline_final/sota_decision.json"
OUTPUT="$PROJECT_ROOT/results/final_selected_internal_risk_20baseline_sota"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
FINALIZER="$PROJECT_ROOT/scripts/finalize_selected_internal_risk_20baseline_sota.sh"
EXPECTED_FINALIZER_SHA="3e67fbff4006c1cfebdc25c111eff8f61e2cccd9800a5d2ef578b32c311c4245"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another selected-risk SOTA finalizer is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$SELECTION_MARKER" || ! -f "$BASELINE_MARKER" ]]; do
  selection_ready=0
  baseline_ready=0
  [[ -f "$SELECTION_MARKER" ]] && selection_ready=1
  [[ -f "$BASELINE_MARKER" ]] && baseline_ready=1
  printf '%s waiting selection=%s baseline20=%s\n' \
    "$(date -Is)" "$selection_ready" "$baseline_ready" >> "$LOG"
  sleep 300
done

actual="$(sha256sum "$FINALIZER" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_FINALIZER_SHA" ]] || {
  printf 'finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_FINALIZER_SHA" "$actual" >&2
  exit 1
}
printf '%s starting selected-risk gate replay and 20-baseline finalization\n' \
  "$(date -Is)" >> "$LOG"
bash "$FINALIZER" >> "$LOG" 2>&1
printf '%s selected-risk 20-baseline finalization complete\n' \
  "$(date -Is)" >> "$LOG"
