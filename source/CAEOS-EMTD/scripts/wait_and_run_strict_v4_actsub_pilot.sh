#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PRO_ROOT="$PROJECT_ROOT/results/strict_v4_pro_msp_fixed_pilot_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_actsub_scale_fixed_pilot_seed7"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "ActSub pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -s "$PRO_ROOT/analysis.json" && -f "$PRO_ROOT/branch_complete" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_actsub_pilot.sh \
  > "$RESULT_ROOT/watcher_execution.log" 2>&1
