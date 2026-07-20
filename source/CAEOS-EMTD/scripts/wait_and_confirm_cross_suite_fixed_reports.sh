#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
ROOT="$PROJECT_ROOT/runs/cross_suite_risk_confirmation/reference"
MANIFEST="$PROJECT_ROOT/results/cross_suite_fixed_risk_screen/candidate_manifest.json"
OUTPUT="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
REFERENCE_POLICY='frozen_suite_conditional_density_v1[suites=edge_iiot;fallback=nested_hierarchical_joint_gate;weight=0.3;minimum_gain=0.02;minimum_known_classes=8]'

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another fixed-report confirmation waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while true; do
  count="$(find "$ROOT" -name metrics.json 2>/dev/null | wc -l)"
  failures="$(find "$ROOT" -name failure.json 2>/dev/null | wc -l)"
  printf '%s reference=%s/96 failures=%s\n' \
    "$(date -Is)" "$count" "$failures" >> "$LOG"
  [[ "$failures" -eq 0 ]] || exit 1
  [[ "$count" -eq 96 ]] && break
  sleep 120
done

cd "$PROJECT_ROOT"
"$PYTHON" confirm_cross_suite_fixed_reports.py \
  --root "$ROOT" \
  --selection-manifest "$MANIFEST" \
  --reference-risk-policy "$REFERENCE_POLICY" \
  --expected-scenarios 24 \
  --output-dir "$OUTPUT" >> "$LOG" 2>&1
printf '%s fixed-report confirmation complete\n' "$(date -Is)" >> "$LOG"
