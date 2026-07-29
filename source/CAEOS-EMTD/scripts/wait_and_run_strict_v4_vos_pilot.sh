#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PREREQUISITE="${PREREQUISITE:-$PROJECT_ROOT/results/doh_temporal_external/execution_complete}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_vos_pilot_seed7"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_vos_pilot_seed7"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
GATE="$RESULT_ROOT/expansion_gate.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "VOS pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
"$PYTHON" create_strict_v4_vos_pilot_protocol.py \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --project-root "$PROJECT_ROOT" \
  --mlp-root runs/strict_v4_full103_mlp_seed7 \
  --comparator-root runs/strict_v4_full103_independent_baselines_seed7 \
  --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/protocol_freeze.log" 2>&1

until [[ -f "$PREREQUISITE" ]]; do
  sleep 60
done
until [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d')" ]]; do
  sleep 60
done
"$PYTHON" run_strict_v4_vos_matrix.py \
  --protocol "$PROTOCOL" --output-root "$RUN_ROOT" --project-root "$PROJECT_ROOT" \
  > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_vos_pilot.py \
  --protocol "$PROTOCOL" --gate "$GATE" --run-root "$RUN_ROOT" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1
