#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PILOT_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_npos_pilot_seed7"
PILOT_RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_npos_pilot_seed7"
FULL_PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_npos_full102_protocol"
FULL_RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_npos_full102_seed7"
FULL_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_npos_full102_seed7"
LOCK_DIR="$PILOT_RESULT_ROOT/watcher.lock.d"

mkdir -p "$PILOT_RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "NPOS extension watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$PROJECT_ROOT/results/strict_v4_final_paper_readiness/audit_complete" ]]; do
  sleep 60
done
until ! nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null \
  | grep -q '[0-9]'; do
  sleep 60
done
if [[ ! -f "$PILOT_RESULT_ROOT/protocol_complete" ]]; then
  echo "frozen NPOS pilot protocol is missing" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
"$PYTHON" run_strict_v4_npos_matrix.py \
  --protocol "$PILOT_RESULT_ROOT/protocol_manifest.json" \
  --output-root "$PILOT_RUN_ROOT" \
  --project-root "$PROJECT_ROOT" \
  > "$PILOT_RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_npos_pilot.py \
  --protocol "$PILOT_RESULT_ROOT/protocol_manifest.json" \
  --gate "$PILOT_RESULT_ROOT/expansion_gate.json" \
  --run-root "$PILOT_RUN_ROOT" \
  --output-dir "$PILOT_RESULT_ROOT" \
  > "$PILOT_RESULT_ROOT/summary.log" 2>&1

if "$PYTHON" -c 'import json,sys; x=json.load(open("results/strict_v4_npos_pilot_seed7/analysis.json")); sys.exit(0 if x["decision"]["expand_to_full102"] else 1)'; then
  mkdir -p "$FULL_PROTOCOL_ROOT" "$FULL_RESULT_ROOT"
  "$PYTHON" create_strict_v4_npos_full102_protocol.py \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --pilot-protocol "$PILOT_RESULT_ROOT/protocol_manifest.json" \
    --pilot-analysis "$PILOT_RESULT_ROOT/analysis.json" \
    --project-root "$PROJECT_ROOT" \
    --mlp-root runs/strict_v4_full103_mlp_seed7 \
    --comparator-root runs/strict_v4_full103_independent_baselines_seed7 \
    --run-root "$FULL_RUN_ROOT" \
    --output-dir "$FULL_PROTOCOL_ROOT" \
    > "$FULL_PROTOCOL_ROOT/freeze.log" 2>&1
  "$PYTHON" run_strict_v4_npos_matrix.py \
    --protocol "$FULL_PROTOCOL_ROOT/protocol_manifest.json" \
    --output-root "$FULL_RUN_ROOT" \
    --project-root "$PROJECT_ROOT" \
    > "$FULL_RESULT_ROOT/execution.log" 2>&1
  "$PYTHON" summarize_strict_v4_npos_full102.py \
    --protocol "$FULL_PROTOCOL_ROOT/protocol_manifest.json" \
    --run-root "$FULL_RUN_ROOT" \
    --existing-summary results/strict_v4_excel_full102_seed7/summary.json \
    --output-dir "$FULL_RESULT_ROOT" \
    > "$FULL_RESULT_ROOT/summary.log" 2>&1
else
  touch "$PILOT_RESULT_ROOT/pilot_negative_complete"
fi
touch "$PILOT_RESULT_ROOT/extension_chain_complete"
