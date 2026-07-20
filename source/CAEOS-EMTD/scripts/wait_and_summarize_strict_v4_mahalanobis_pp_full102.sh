#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_mahalanobis_pp_full102_seed7"
OUTPUT="$PROJECT_ROOT/results/strict_v4_mahalanobis_pp_full102_seed7"
MARKER="$RUN_ROOT/full102_complete"
LOCK="$OUTPUT/summary_watcher.lock.d"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

while [[ ! -f "$MARKER" ]]; do
  sleep 60
done
if [[ -f "$OUTPUT/comparator_decision_complete" ]]; then
  exit 0
fi
[[ "$(find "$RUN_ROOT" -name metrics.json | wc -l)" -eq 102 ]]
[[ "$(find "$RUN_ROOT" -name failure.json | wc -l)" -eq 0 ]]

cd "$PROJECT_ROOT"
"$PYTHON" summarize_strict_v4_mahalanobis_pp_full102.py \
  --protocol "$OUTPUT/protocol_manifest.json" \
  --result-root "$RUN_ROOT" \
  --existing-summary results/strict_v4_mandatory_scores_full102_seed7/summary.json \
  --output-dir "$OUTPUT" \
  > "$OUTPUT/summary.log" 2>&1
