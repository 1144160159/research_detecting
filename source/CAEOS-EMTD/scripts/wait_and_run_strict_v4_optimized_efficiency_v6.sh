#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
V5_COMPLETE="$PROJECT_ROOT/results/strict_v4_final_efficiency_v5/recovery_complete"
CTC_COMPLETE="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_confirmation_branch/branch_complete"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_optimized_efficiency_protocol_v1"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_optimized_efficiency_v6"
SUMMARY_ROOT="$PROJECT_ROOT/results/strict_v4_optimized_efficiency_v6"
LOCK_DIR="$SUMMARY_ROOT/watcher.lock.d"
IDLE_LOG="$SUMMARY_ROOT/gpu_idle_observations.log"

cd "$PROJECT_ROOT"
mkdir -p "$PROTOCOL_ROOT" "$RUN_ROOT" "$SUMMARY_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "optimized efficiency v6 watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

if [[ ! -s "$PROTOCOL_ROOT/protocol_manifest.json" ]]; then
  "$PYTHON" create_strict_v4_optimized_efficiency_protocol.py \
    --v5-protocol results/strict_v4_final_efficiency_protocol_v5/protocol_manifest.json \
    --v5-plan results/strict_v4_final_efficiency_execution_plan_v5/execution_plan.json \
    --v5-formal-root runs/strict_v4_final_efficiency_v5 \
    --v5-summary-root results/strict_v4_final_efficiency_v5 \
    --optimized-result-root "$RUN_ROOT" \
    --pairwise-runtime caeos/pairwise_runtime.py \
    --optimized-runtime caeos/pairwise_runtime_optimized.py \
    --open-detect-runtime caeos/open_detect_runtime.py \
    --block-runner run_strict_v4_optimized_efficiency_block.py \
    --matrix-runner run_strict_v4_optimized_efficiency_matrix.py \
    --summarizer summarize_strict_v4_optimized_efficiency.py \
    --output-dir "$PROTOCOL_ROOT" > "$PROTOCOL_ROOT/freeze.log" 2>&1
fi

until [[ -f "$V5_COMPLETE" && -f "$CTC_COMPLETE" ]]; do
  sleep 60
done

: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(pgrep -af 'run_strict_v4_optimized_efficiency|execute_strict_v4_final_efficiency|mal_tls_geometry|counterfactual_conflict|conflict_topology' 2>/dev/null || true)"
  printf '%s sample=%d gpu=%q experiments=%q\n' \
    "$(date --iso-8601=seconds)" "$idle_samples" \
    "$gpu_processes" "$experiment_processes" >> "$IDLE_LOG"
  if [[ -n "$gpu_processes" || -n "$experiment_processes" ]]; then
    idle_samples=0
  else
    idle_samples=$((idle_samples + 1))
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done

"$PYTHON" run_strict_v4_optimized_efficiency_matrix.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --v5-root runs/strict_v4_final_efficiency_v5 \
  --output-root "$RUN_ROOT" \
  --block-runner run_strict_v4_optimized_efficiency_block.py \
  > "$SUMMARY_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_optimized_efficiency.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --result-root "$RUN_ROOT" --output-dir "$SUMMARY_ROOT" \
  > "$SUMMARY_ROOT/summary.log" 2>&1
touch "$SUMMARY_ROOT/branch_complete"
