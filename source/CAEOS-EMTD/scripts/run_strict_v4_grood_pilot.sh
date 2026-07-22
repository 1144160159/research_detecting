#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
MAIN_ROOT="${MAIN_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_grood_pilot_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_grood_pilot_seed7"
SOURCE_ROOT="$MAIN_ROOT/runs/strict_v4_full103_mlp_seed7"
OPENDETECT_ROOT="$MAIN_ROOT/runs/strict_v4_full103_independent_baselines_seed7"
COVERAGE="$MAIN_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"

cd "$PROJECT_ROOT"
mkdir -p "$RUN_ROOT" "$RESULT_ROOT"
if [[ ! -s "$RUN_ROOT/protocol_manifest.json" ]]; then
  "$PYTHON" run_strict_v4_grood_matrix.py \
    --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
    --output-root "$RUN_ROOT" --mode pilot --workers 1 --device cpu \
    --protocol-only
fi
if [[ ! -s "$RUN_ROOT/expansion_gate.json" ]]; then
  "$PYTHON" create_strict_v4_grood_expansion_gate.py \
    --pilot-root "$RUN_ROOT" --output "$RUN_ROOT/expansion_gate.json"
fi
cp "$RUN_ROOT/protocol_manifest.json" "$RESULT_ROOT/protocol_manifest.json"
cp "$RUN_ROOT/expansion_gate.json" "$RESULT_ROOT/expansion_gate.json"

"$PYTHON" run_strict_v4_grood_matrix.py \
  --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
  --output-root "$RUN_ROOT" --mode pilot --workers 1 --device cpu
"$PYTHON" summarize_strict_v4_grood_pilot.py \
  --pilot-root "$RUN_ROOT" --source-root "$SOURCE_ROOT" \
  --opendetect-root "$OPENDETECT_ROOT" --gate "$RUN_ROOT/expansion_gate.json" \
  --output-dir "$RESULT_ROOT"
touch "$RESULT_ROOT/pilot_complete"
