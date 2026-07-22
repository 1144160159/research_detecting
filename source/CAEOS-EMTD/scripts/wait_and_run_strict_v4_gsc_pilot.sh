#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
EXPLORATION_ROOT="${EXPLORATION_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
GROOD_ANALYSIS="$EXPLORATION_ROOT/results/strict_v4_grood_pilot_seed7/analysis.json"
GROOD_COMPLETE="$EXPLORATION_ROOT/results/strict_v4_grood_pilot_seed7/pilot_complete"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_gsc_pilot_seed7"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "GSC pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -s "$GROOD_ANALYSIS" && -f "$GROOD_COMPLETE" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_gsc_pilot.sh \
  > "$RESULT_ROOT/watcher_execution.log" 2>&1
