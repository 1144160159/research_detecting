#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
CONFIRMATION="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation_v2/confirmation.json"
OUTPUT="$PROJECT_ROOT/results/final_composite_risk_v2_20baseline_sota"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
FINALIZER="$PROJECT_ROOT/scripts/finalize_composite_risk_v2_20baseline_sota.sh"
EXPECTED_FINALIZER_SHA="677079ca3d632b277b15367f3379e84e915a4e27dd7475fb16470b2a960b17b3"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another composite v2 20-baseline finalizer is active\n' \
    "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$CONFIRMATION" ]]; do
  printf '%s waiting for cross-suite v2 confirmation\n' \
    "$(date -Is)" >> "$LOG"
  sleep 300
done
actual="$(sha256sum "$FINALIZER" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_FINALIZER_SHA" ]] || {
  printf 'finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_FINALIZER_SHA" "$actual" >&2
  exit 1
}
printf '%s starting composite v2 20-baseline finalization\n' \
  "$(date -Is)" >> "$LOG"
bash "$FINALIZER" >> "$LOG" 2>&1
printf '%s composite v2 20-baseline finalization complete\n' \
  "$(date -Is)" >> "$LOG"
