#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_ustc_deployment_packages_v1"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_ustc_deployment_packages_v1"
DESIGN="$RESULT_ROOT/design_protocol.json"
PROTOCOL="$RESULT_ROOT/execution_protocol.json"
SUMMARY="$RESULT_ROOT/summary.json"
SELECTION_ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_confirmation_seed311_313"
SELECTION="$SELECTION_ROOT/final_selection.json"
VGRF_PROTOCOL="$SELECTION_ROOT/protocol_manifest.json"
VGRF_SUMMARY="$SELECTION_ROOT/summary.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"
STATE_LOG="$RESULT_ROOT/state.log"
IDLE_LOG="$RESULT_ROOT/gpu_idle_observations.log"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "USTC deployment package watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE_LOG"
}

: > "$STATE_LOG"
log_state "waiting for frozen design and final VGRF-or-Pairwise selection"
until [[ -s "$DESIGN" && -s "$SELECTION" \
  && -f "$SELECTION_ROOT/branch_complete" ]]; do
  sleep 300
done

BLOCKER_PATTERN='train_|run_strict|execute_strict|corruption|tensorized|gpu_external|parrot2025_full'
: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(pgrep -af "$BLOCKER_PATTERN" 2>/dev/null \
    | grep -v -E 'wait_and_|pgrep -af' || true)"
  printf '%s sample=%d gpu=%q experiments=%q\n' \
    "$(date --iso-8601=seconds)" "$idle_samples" \
    "$gpu_processes" "$experiment_processes" >> "$IDLE_LOG"
  if [[ -z "$gpu_processes" && -z "$experiment_processes" ]]; then
    idle_samples=$((idle_samples + 1))
  else
    idle_samples=0
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done
log_state "five consecutive idle samples passed"

cd "$PROJECT_ROOT"
if [[ ! -s "$PROTOCOL" ]]; then
  observed=0
  if [[ -d "$RESULT_ROOT/packages" ]]; then
    observed="$(find "$RESULT_ROOT/packages" -name package_record.json \
      -type f | wc -l)"
  fi
  if [[ "$observed" -ne 0 ]]; then
    log_state "refusing to freeze execution protocol after package records exist"
    exit 1
  fi
  log_state "freezing selected-algorithm execution protocol"
  "$PYTHON" create_strict_v4_ustc_deployment_package_protocol.py \
    --design "$DESIGN" \
    --selection "$SELECTION" \
    --project-root "$PROJECT_ROOT" \
    --vgrf-confirmation-protocol "$VGRF_PROTOCOL" \
    --vgrf-confirmation-summary "$VGRF_SUMMARY" \
    --output "$PROTOCOL" \
    > "$RESULT_ROOT/protocol_freeze.log" 2>&1
fi

log_state "running resumable twenty-package deployment matrix"
ionice -c3 nice -n19 "$PYTHON" \
  run_strict_v4_ustc_deployment_packages.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --python "$PYTHON" \
  > "$RESULT_ROOT/execution.log" 2>&1

log_state "summarizing twenty deployment packages"
"$PYTHON" summarize_strict_v4_ustc_deployment_packages.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --output "$SUMMARY" \
  > "$RESULT_ROOT/summary.log" 2>&1
log_state "USTC deployment package chain complete"
