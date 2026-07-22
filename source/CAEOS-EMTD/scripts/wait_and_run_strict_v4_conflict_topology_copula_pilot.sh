#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
SELF_ALGORITHM_ROOT="${SELF_ALGORITHM_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SELF_ALGORITHM_COMPLETE="$SELF_ALGORITHM_ROOT/results/mal_tls_self_algorithm_selection/audit_complete"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_pilot_seed7"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_conflict_topology_copula_pilot_seed7"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "conflict-topology copula watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
if [[ ! -s "$PROTOCOL" ]]; then
  "$PYTHON" create_strict_v4_conflict_topology_copula_protocol.py \
    --project-root "$PROJECT_ROOT" \
    --source-root runs/strict_v4_full103_pairwise_caeos_seed7 \
    --run-root "$RUN_ROOT" --output "$PROTOCOL" \
    > "$RESULT_ROOT/protocol_freeze.log" 2>&1
fi
until [[ -f "$SELF_ALGORITHM_COMPLETE" ]]; do
  sleep 60
done
bash scripts/run_strict_v4_conflict_topology_copula_pilot.sh
