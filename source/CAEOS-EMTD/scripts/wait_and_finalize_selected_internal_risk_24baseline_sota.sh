#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717}"
SELECTED_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717"
GATE_MARKER="$SELECTED_ROOT/results/final_selected_internal_risk_20baseline_sota/materialization_complete"
BASELINE_MARKER="$PROJECT_ROOT/results/strict_v2_24baseline_extended/finalization_complete"
OUTPUT="$PROJECT_ROOT/results/final_selected_internal_risk_24baseline_sota"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
FINALIZER="$PROJECT_ROOT/scripts/finalize_selected_internal_risk_24baseline_sota.sh"
EXPECTED_FINALIZER_SHA="54c4de4e2eac8a957150b4e7d133e217c985edcaf260ff069b0822c7df867a66"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another selected-risk 24-baseline finalizer is active\n' \
    "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$GATE_MARKER" || ! -f "$BASELINE_MARKER" ]]; do
  gate_ready=0
  baseline_ready=0
  [[ -f "$GATE_MARKER" ]] && gate_ready=1
  [[ -f "$BASELINE_MARKER" ]] && baseline_ready=1
  printf '%s waiting selected_gate=%s baseline24=%s\n' \
    "$(date -Is)" "$gate_ready" "$baseline_ready" >> "$LOG"
  sleep 300
done

actual="$(sha256sum "$FINALIZER" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_FINALIZER_SHA" ]] || {
  printf 'finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_FINALIZER_SHA" "$actual" >&2
  exit 1
}
printf '%s starting selected-risk 24-baseline finalization\n' \
  "$(date -Is)" >> "$LOG"
bash "$FINALIZER" >> "$LOG" 2>&1
printf '%s selected-risk 24-baseline finalization complete\n' \
  "$(date -Is)" >> "$LOG"
