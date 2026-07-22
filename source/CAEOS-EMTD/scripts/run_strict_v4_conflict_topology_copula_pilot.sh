#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_pilot_seed7"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_conflict_topology_copula_pilot_seed7"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"

cd "$PROJECT_ROOT"
"$PYTHON" run_strict_v4_conflict_topology_copula_matrix.py \
  --protocol "$PROTOCOL" --project-root "$PROJECT_ROOT" \
  --output-root "$RUN_ROOT" > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_conflict_topology_copula.py \
  --protocol "$PROTOCOL" --run-root "$RUN_ROOT" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1
