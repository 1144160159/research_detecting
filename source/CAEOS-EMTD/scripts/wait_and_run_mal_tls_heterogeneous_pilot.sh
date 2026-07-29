#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
LCB_COMPLETE="$PROJECT_ROOT/results/strict_v4_lcb_tail_aware_pilot_seed191/pilot_complete"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_heterogeneous_pilot_seed191"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Mal_TLS heterogeneous pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$LCB_COMPLETE" ]]; do
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
bash scripts/run_mal_tls_heterogeneous_pilot.sh > "$RESULT_ROOT/watcher.log" 2>&1
