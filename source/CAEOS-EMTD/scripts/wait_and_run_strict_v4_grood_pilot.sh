#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
SELF_ALGORITHM_ROOT="${SELF_ALGORITHM_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
MAIN_PROJECT_ROOT="${MAIN_PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
SELF_ALGORITHM_COMPLETE="$SELF_ALGORITHM_ROOT/results/mal_tls_self_algorithm_selection/audit_complete"
VOS_COMPLETE="$MAIN_PROJECT_ROOT/results/strict_v4_vos_pilot_seed7/pilot_complete"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_grood_pilot_seed7"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "GROOD pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$SELF_ALGORITHM_COMPLETE" && -f "$VOS_COMPLETE" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_grood_pilot.sh \
  > "$RESULT_ROOT/execution.log" 2>&1
