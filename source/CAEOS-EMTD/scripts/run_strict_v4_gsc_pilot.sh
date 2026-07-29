#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_gsc_pilot_seed7"
SOURCE_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_mlp_seed7"
OPENDETECT_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_independent_baselines_seed7"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
GATE="$RESULT_ROOT/expansion_gate.json"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
"$PYTHON" run_strict_v4_gsc_matrix.py \
  --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
  --output-root "$RESULT_ROOT" --mode pilot --workers 1 --device cpu \
  --protocol-only > "$RESULT_ROOT/protocol_freeze.log" 2>&1
if [[ ! -s "$GATE" ]]; then
  "$PYTHON" create_strict_v4_gsc_expansion_gate.py \
    --pilot-root "$RESULT_ROOT" --output "$GATE" \
    > "$RESULT_ROOT/gate_freeze.log" 2>&1
fi
"$PYTHON" run_strict_v4_gsc_matrix.py \
  --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
  --output-root "$RESULT_ROOT" --mode pilot --workers 1 --device cpu \
  > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_gsc_pilot.py \
  --pilot-root "$RESULT_ROOT" --source-root "$SOURCE_ROOT" \
  --opendetect-root "$OPENDETECT_ROOT" --gate "$GATE" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1
touch "$RESULT_ROOT/pilot_complete"
