#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
CONFIRMATION="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation/confirmation.json"
OUTPUT="$PROJECT_ROOT/results/final_composite_risk_20baseline_sota"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
FINALIZER="$PROJECT_ROOT/scripts/finalize_composite_risk_20baseline_sota.sh"
EXPECTED_FINALIZER_SHA="ce35a6451a3d4bde59aa5cb270ce34792ae2e5200311fe979f3aa99fcbc4e071"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another composite 20-baseline finalizer is active\n' \
    "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$CONFIRMATION" ]]; do
  printf '%s waiting for same-run cross-suite confirmation\n' \
    "$(date -Is)" >> "$LOG"
  sleep 300
done

actual="$(sha256sum "$FINALIZER" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_FINALIZER_SHA" ]] || {
  printf 'finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_FINALIZER_SHA" "$actual" >&2
  exit 1
}
printf '%s starting final composite 20-baseline finalization\n' \
  "$(date -Is)" >> "$LOG"
bash "$FINALIZER" >> "$LOG" 2>&1
printf '%s final composite 20-baseline finalization complete\n' \
  "$(date -Is)" >> "$LOG"
