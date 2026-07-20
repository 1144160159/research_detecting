#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
OUTPUT_DIR="$PROJECT_ROOT/results/strict_v3_pilot"
LOG="$OUTPUT_DIR/summary_waiter.log"
LOCK_DIR="$OUTPUT_DIR/summary_waiter.lock.d"
MANIFEST="$PROJECT_ROOT/selection/strict_v3_pilot_manifest.json"
EXPECTED_MANIFEST_SHA="438fb986d311f15b85551f1f55c2878c8f34f15790edfa91ea29c2bf49f0e71f"

mkdir -p "$OUTPUT_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another strict-v3 summary waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$OUTPUT_DIR/training_complete" ]]; do
  printf '%s waiting for strict-v3 pilot training\n' "$(date -Is)" >> "$LOG"
  sleep 300
done

printf '%s starting strict-v3 pilot audit and summary\n' "$(date -Is)" >> "$LOG"
cd "$PROJECT_ROOT"
"$CONDA" run -n py3.9 python summarize_strict_v3_pilot.py \
  --caeos-root runs/strict_v3_pilot_caeos \
  --neural-root runs/strict_v3_pilot_neural \
  --manifest "$MANIFEST" \
  --expected-manifest-sha256 "$EXPECTED_MANIFEST_SHA" \
  --output-dir results/strict_v3_pilot \
  --seed 7 \
  --known-acceptance 0.95 >> "$LOG" 2>&1
printf '%s strict-v3 pilot audit and summary complete\n' "$(date -Is)" >> "$LOG"
