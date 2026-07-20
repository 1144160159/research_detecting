#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
MARKER="$PROJECT_ROOT/results/strict_v4_pilot/training_complete"
OUTPUT="$PROJECT_ROOT/results/strict_v4_pilot"
LOG="$OUTPUT/summary_waiter.log"
LOCK_DIR="$OUTPUT/summary_waiter.lock.d"
MANIFEST="$PROJECT_ROOT/results/gpu_candidate_dataset_inventory_20260717/strict_v4_candidate_manifest.json"
GROUP_SIDECAR="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported/seed7_max1000.csv.json"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another strict-v4 summary waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

actual="$(sha256sum "$PROJECT_ROOT/summarize_strict_v4_pilot.py" | awk '{print $1}')"
[[ "$actual" == "a9ed896a14aef5a9ee27244aa5b9beb7f0f5f9e294c2ff3513181e0634bd67c0" ]]

while [[ ! -f "$MARKER" ]]; do
  neural="$(find "$PROJECT_ROOT/runs/strict_v4_pilot_neural" -name metrics.json 2>/dev/null | wc -l)"
  printf '%s waiting strict-v4 neural=%s/18\n' "$(date -Is)" "$neural" >> "$LOG"
  sleep 120
done

cd "$PROJECT_ROOT"
"$PYTHON" summarize_strict_v4_pilot.py \
  --caeos-root runs/strict_v4_pilot_caeos \
  --neural-root runs/strict_v4_pilot_neural \
  --manifest "$MANIFEST" \
  --expected-manifest-sha256 39f8c4801420aa7c9501f1065710ec07c10560117f12bb5bcec8541d2b6cc945 \
  --group-cache-sidecar "$GROUP_SIDECAR" \
  --output-dir "$OUTPUT" >> "$LOG" 2>&1
touch "$OUTPUT/summary_complete"
printf '%s strict-v4 summary complete\n' "$(date -Is)" >> "$LOG"
