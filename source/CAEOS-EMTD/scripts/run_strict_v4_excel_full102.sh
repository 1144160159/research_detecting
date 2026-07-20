#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUTPUT="$PROJECT_ROOT/results/strict_v4_excel_full102_seed7"
PROTOCOL="$OUTPUT/protocol_manifest.json"
EXISTING="$PROJECT_ROOT/results/strict_v4_mahalanobis_pp_full102_seed7/summary.json"
LOCK="$OUTPUT/launcher.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$OUTPUT"
if ! mkdir "$LOCK" 2>/dev/null; then
  printf '%s ExCeL full102 launcher already active\n' "$(date -Is)" >> "$OUTPUT/launcher.log"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

"$PYTHON" run_strict_v4_excel_full102.py \
  --protocol "$PROTOCOL" \
  --output-root "$OUTPUT" \
  --workers 1 \
  --device cpu > "$OUTPUT/training.log" 2>&1

"$PYTHON" summarize_strict_v4_excel_full102.py \
  --protocol "$PROTOCOL" \
  --result-root "$OUTPUT" \
  --existing-summary "$EXISTING" \
  --output-dir "$OUTPUT" > "$OUTPUT/summary.log" 2>&1

touch "$OUTPUT/screen_complete"
