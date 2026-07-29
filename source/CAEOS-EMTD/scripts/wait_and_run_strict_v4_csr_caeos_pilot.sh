#!/usr/bin/env bash
set -euo pipefail

ROOT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
PROTOCOL="$ROOT/results/strict_v4_csr_caeos_pilot_protocol_v1/protocol.json"
RUN_ROOT="$ROOT/runs/strict_v4_csr_caeos_pilot_v1"
RESULT_ROOT="$ROOT/results/strict_v4_csr_caeos_pilot_v1"
STATE="$RESULT_ROOT/watcher_state.log"
LOCK="$RESULT_ROOT/watcher_lock"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  printf 'CSR watcher lock already exists: %s\n' "$LOCK" >&2
  exit 1
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

if [[ -f "$RESULT_ROOT/pilot_complete" ]]; then
  printf 'pilot_complete already exists\n' >>"$STATE"
  exit 0
fi

cpu_count=$(getconf _NPROCESSORS_ONLN)
idle_limit=$((cpu_count * 3 / 4))
idle_count=0
while (( idle_count < 5 )); do
  load_one=$(awk '{print $1}' /proc/loadavg)
  load_integer=${load_one%.*}
  if (( load_integer <= idle_limit )); then
    idle_count=$((idle_count + 1))
  else
    idle_count=0
  fi
  printf '%s load1=%s limit=%s idle_count=%s\n' \
    "$(date -u +%FT%TZ)" "$load_one" "$idle_limit" "$idle_count" >>"$STATE"
  if (( idle_count < 5 )); then
    sleep 30
  fi
done

cd "$ROOT"
nice -n 19 ionice -c 3 "$PYTHON" \
  run_strict_v4_csr_caeos_pilot.py \
  --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" \
  --result-root "$RESULT_ROOT" \
  --project-root "$ROOT"
