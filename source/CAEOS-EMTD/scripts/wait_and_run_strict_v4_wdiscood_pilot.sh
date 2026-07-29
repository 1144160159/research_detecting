#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
EXPLORATION_ROOT="${EXPLORATION_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
SELF_ALGORITHM_ROOT="${SELF_ALGORITHM_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
EFFICIENCY_COMPLETE="$PROJECT_ROOT/results/strict_v4_final_efficiency_v5/recovery_complete"
SELF_ALGORITHM_COMPLETE="$SELF_ALGORITHM_ROOT/results/mal_tls_self_algorithm_selection/audit_complete"
CONFLICT_TOPOLOGY_COMPLETE="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_confirmation_branch/branch_complete"
UNIFIED_SELF_COMPLETE="$PROJECT_ROOT/results/strict_v4_unified_self_algorithm_selection/accuracy_decision_complete"
OPTIMIZED_EFFICIENCY_COMPLETE="$PROJECT_ROOT/results/strict_v4_optimized_efficiency_v6/branch_complete"
HETEROGENEOUS_COMPLETE="$EXPLORATION_ROOT/results/mal_tls_heterogeneous_pilot_seed191/pilot_complete"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_wdiscood_pilot_seed7"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_wdiscood_pilot_seed7"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "WDiscOOD pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$EFFICIENCY_COMPLETE" && -f "$SELF_ALGORITHM_COMPLETE" \
  && -f "$CONFLICT_TOPOLOGY_COMPLETE" \
  && -f "$UNIFIED_SELF_COMPLETE" \
  && -f "$OPTIMIZED_EFFICIENCY_COMPLETE" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
"$PYTHON" create_strict_v4_wdiscood_pilot_protocol.py \
  --coverage-manifest results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --mlp-root runs/strict_v4_full103_mlp_seed7 \
  --opendetect-root runs/strict_v4_full103_independent_baselines_seed7 \
  --output "$PROTOCOL" > "$RESULT_ROOT/protocol_freeze.log" 2>&1

until [[ -f "$HETEROGENEOUS_COMPLETE" ]]; do
  sleep 60
done
"$PYTHON" run_strict_v4_wdiscood_pilot.py \
  --protocol "$PROTOCOL" --output-root "$RUN_ROOT" --device cpu --workers 1 \
  > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_wdiscood_pilot.py \
  --protocol "$PROTOCOL" --pilot-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/summary.log" 2>&1
