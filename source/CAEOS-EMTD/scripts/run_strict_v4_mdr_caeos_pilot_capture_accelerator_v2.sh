#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SERIAL_PID="${SERIAL_PID:?SERIAL_PID is required}"
WORKERS="${WORKERS:-4}"
PROTOCOL="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot_protocol_v2/protocol_manifest.json"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_mdr_caeos_pilot_v2"
ROOT="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot_acceleration_v2"
LOCK="$ROOT/coordinator.lock.d"
STATE="$ROOT/coordinator_state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "MDR pilot v2 capture coordinator already active" >&2
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
if [[ "$serial_command" != *"run_strict_v4_mdr_caeos_pilot_v2.py"* ]]; then
  echo "unexpected MDR pilot v2 runner command" >&2
  exit 1
fi
kill -STOP "$SERIAL_PID"
log_state "MDR pilot v2 runner stopped; waiting for active capture child"
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
  echo "MDR pilot v2 runner did not remain stopped" >&2
  exit 1
fi
run_id="capture_accel_v2_$(date -u +%Y%m%dT%H%M%SZ)"
log_state "launching v2 frozen-command capture workers"
"$PYTHON" accelerate_strict_v4_mdr_caeos_pilot_captures_v2.py \
  --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" \
  --project-root "$PROJECT_ROOT" \
  --serial-runner-pid "$SERIAL_PID" \
  --run-id "$run_id" \
  --workers "$WORKERS" \
  > "$ROOT/execution.log" 2>&1
log_state "all 42 v2 captures complete; resuming canonical MDR pilot v2 runner"
resume_serial
trap - EXIT INT TERM
