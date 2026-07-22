#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_cadref_family_pilot_seed7"
FULL_ROOT="$PROJECT_ROOT/results/strict_v4_cadref_family_full102_seed7"
SOURCE_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_mlp_seed7"
OPENDETECT_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_independent_baselines_seed7"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
GATE="$RESULT_ROOT/expansion_gate.json"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
"$PYTHON" run_strict_v4_cadref_matrix.py \
  --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
  --output-root "$RESULT_ROOT" --mode pilot --workers 1 --device cpu \
  --protocol-only > "$RESULT_ROOT/protocol_freeze.log" 2>&1
if [[ ! -s "$GATE" ]]; then
  "$PYTHON" create_strict_v4_cadref_expansion_gate.py \
    --pilot-root "$RESULT_ROOT" --output "$GATE" \
    > "$RESULT_ROOT/gate_freeze.log" 2>&1
fi
"$PYTHON" run_strict_v4_cadref_matrix.py \
  --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
  --output-root "$RESULT_ROOT" --mode pilot --workers 1 --device cpu \
  > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_cadref_pilot.py \
  --pilot-root "$RESULT_ROOT" --source-root "$SOURCE_ROOT" \
  --opendetect-root "$OPENDETECT_ROOT" --gate "$GATE" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1

expand="$("$PYTHON" -c 'import json,sys; print(str(bool(json.load(open(sys.argv[1]))["decision"]["expand_methods_to_full102"])).lower())' "$RESULT_ROOT/analysis.json")"
if [[ "$expand" == "true" ]]; then
  mkdir -p "$FULL_ROOT"
  "$PYTHON" run_strict_v4_cadref_matrix.py \
    --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
    --output-root "$FULL_ROOT" --mode full --workers 1 --device cpu \
    --protocol-only > "$FULL_ROOT/protocol_freeze.log" 2>&1
  "$PYTHON" run_strict_v4_cadref_matrix.py \
    --source-root "$SOURCE_ROOT" --coverage "$COVERAGE" \
    --output-root "$FULL_ROOT" --mode full --workers 1 --device cpu \
    > "$FULL_ROOT/execution.log" 2>&1
  "$PYTHON" summarize_strict_v4_cadref_full.py \
    --full-root "$FULL_ROOT" --source-root "$SOURCE_ROOT" \
    --opendetect-root "$OPENDETECT_ROOT" \
    --pilot-analysis "$RESULT_ROOT/analysis.json" \
    --output-dir "$FULL_ROOT" > "$FULL_ROOT/summary.log" 2>&1
  touch "$RESULT_ROOT/full102_complete"
else
  "$PYTHON" -c \
    'import json,sys; from pathlib import Path; Path(sys.argv[1]).write_text(json.dumps({"status":"not_required","pilot_decision":False},indent=2)+"\n")' \
    "$RESULT_ROOT/full102_not_required.json"
fi
touch "$RESULT_ROOT/branch_complete"
