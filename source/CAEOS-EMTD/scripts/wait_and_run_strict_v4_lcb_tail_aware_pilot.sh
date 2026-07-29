#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
MAIN_PROJECT_ROOT="${MAIN_PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_lcb_tail_aware_pilot_seed191"
UPSTREAM="$MAIN_PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit/audit_complete"
CACHES="$MAIN_PROJECT_ROOT/results/strict_v4_final_efficiency_seed191_cache/caches_complete"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "LCB tail-aware watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$UPSTREAM" && -f "$CACHES" ]]; do
  sleep 60
done

idle_checks=0
while (( idle_checks < 3 )); do
  active="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)"
  if [[ "$active" -eq 0 ]]; then
    idle_checks=$((idle_checks + 1))
  else
    idle_checks=0
  fi
  sleep 30
done

cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_lcb_tail_aware_pilot.sh > "$RESULT_ROOT/watcher.log" 2>&1
