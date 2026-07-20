#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUTPUT="$PROJECT_ROOT/results/strict_v4_mandatory_scores_full102_seed7"
LOCK_DIR="$OUTPUT/summary.lock.d"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "mandatory score summarizer already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$OUTPUT/mandatory_scores_complete" \
  && -f "$OUTPUT/protocol_manifest.json" \
  && -f "$OUTPUT/matrix_summary.json" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
"$PYTHON" summarize_strict_v4_mandatory_scores_full102.py \
  --full-root "$OUTPUT" \
  --source-root runs/strict_v4_full103_mlp_seed7 \
  --existing-summary results/strict_v4_sirc_msp_fixed_full102_seed7/summary.json \
  --output-dir "$OUTPUT" \
  > "$OUTPUT/summary.log" 2>&1
touch "$OUTPUT/summary_complete"
