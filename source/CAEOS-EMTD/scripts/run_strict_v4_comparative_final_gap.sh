#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SERIAL_PID="${SERIAL_PID:-261602}"
WORKERS="${WORKERS:-4}"
PROTOCOL="$PROJECT_ROOT/results/strict_v4_comparative_corruption_protocol/protocol_manifest_v2.json"
OUTPUT_ROOT="$PROJECT_ROOT/runs/strict_v4_comparative_corruption"
ROOT="$PROJECT_ROOT/results/strict_v4_comparative_final_gap_v1"
LOCK="$ROOT/coordinator.lock.d"
STATE="$ROOT/coordinator_state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "final-gap coordinator already active" >&2
  exit 0
fi
resumed=0
resume_serial() {
  if [[ "$resumed" -eq 0 ]] && kill -0 "$SERIAL_PID" 2>/dev/null; then
    kill -CONT "$SERIAL_PID" 2>/dev/null || true
    resumed=1
  fi
  rmdir "$LOCK" 2>/dev/null || true
}
trap resume_serial EXIT INT TERM

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE"
}

cd "$PROJECT_ROOT"
: > "$STATE"
serial_command="$(tr '\0' ' ' < "/proc/$SERIAL_PID/cmdline")"
if [[ "$serial_command" != *"run_strict_v4_comparative_corruption.py"* ]]; then
  echo "unexpected serial runner command" >&2
  exit 1
fi

kill -STOP "$SERIAL_PID"
log_state "serial runner stopped; waiting for its active child to become zombie"
while true; do
  active_children="$(
    ps -eo ppid=,stat= 2>/dev/null \
      | awk -v parent="$SERIAL_PID" \
        '$1 == parent && substr($2,1,1) != "Z" {print}'
  )"
  [[ -z "$active_children" ]] && break
  sleep 10
done

state="$(awk '{print $3}' "/proc/$SERIAL_PID/stat")"
if [[ "$state" != "T" && "$state" != "t" ]]; then
  echo "serial runner did not remain stopped" >&2
  exit 1
fi
frontier="$(
  "$PYTHON" - "$PROTOCOL" "$OUTPUT_ROOT" <<'PY'
import json, sys
from pathlib import Path
from accelerate_strict_v4_comparative_corruption import contiguous_completed
protocol = json.load(open(sys.argv[1], encoding="utf-8"))
print(contiguous_completed(protocol, Path(sys.argv[2])))
PY
)"
minimum_source_index=$((frontier + 1))
run_id="final_gap_$(date -u +%Y%m%dT%H%M%SZ)"
log_state "launching final-gap workers frontier=$frontier minimum=$minimum_source_index"

"$PYTHON" accelerate_strict_v4_comparative_final_gap.py \
  --protocol "$PROTOCOL" \
  --output-root "$OUTPUT_ROOT" \
  --project-root "$PROJECT_ROOT" \
  --run-id "$run_id" \
  --workers "$WORKERS" \
  --minimum-source-index "$minimum_source_index" \
  --serial-runner-pid "$SERIAL_PID" \
  > "$ROOT/execution.log" 2>&1

log_state "final-gap workers complete; resuming canonical serial runner"
resume_serial
trap - EXIT INT TERM
