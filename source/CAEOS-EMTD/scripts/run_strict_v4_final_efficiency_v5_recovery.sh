#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OLD_PROTOCOL="$PROJECT_ROOT/results/strict_v4_final_efficiency_protocol_v4/protocol_manifest.json"
OLD_PLAN="$PROJECT_ROOT/results/strict_v4_final_efficiency_execution_plan_v4/execution_plan.json"
OLD_FORMAL="$PROJECT_ROOT/runs/strict_v4_final_efficiency_v4"
FAILURE_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_v4_failure_20260721T2235Z"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_protocol_v5"
PLAN_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_execution_plan_v5"
FORMAL_ROOT="$PROJECT_ROOT/runs/strict_v4_final_efficiency_v5"
SUMMARY_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_v5"
REUSE_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_v5_reuse_audit"
IDLE_LOG="$PLAN_ROOT/gpu_idle_observations.log"
LOCK_DIR="$PLAN_ROOT/recovery.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$PROTOCOL_ROOT" "$PLAN_ROOT" "$SUMMARY_ROOT" "$REUSE_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "efficiency v5 recovery already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

if [[ ! -s "$PROTOCOL_ROOT/protocol_manifest.json" ]]; then
  "$PYTHON" create_strict_v4_final_efficiency_protocol_v2.py \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --v1-protocol results/strict_v4_final_efficiency_protocol/protocol_manifest.json \
    --readiness results/strict_v4_final_efficiency_readiness_seed7/readiness.json \
    --decision results/strict_v4_optimal_self_algorithm/decision.json \
    --external-confirmation results/strict_v4_external_confirmation/confirmation.json \
    --candidate-implementation train_hybrid_open_set.py \
    --comparator-implementation train_neural_open_set.py \
    --candidate-runtime caeos/pairwise_runtime.py \
    --candidate-capture capture_pairwise_runtime.py \
    --candidate-benchmark benchmark_pairwise_runtime.py \
    --comparator-runtime caeos/open_detect_runtime.py \
    --comparator-capture capture_opendetect_runtime.py \
    --comparator-training-capture capture_opendetect_training_runtime.py \
    --comparator-benchmark benchmark_opendetect_runtime.py \
    --paired-runner run_strict_v4_final_efficiency_v2.py \
    --execution-plan-creator create_strict_v4_final_efficiency_execution_plan_v2.py \
    --execution-plan-executor execute_strict_v4_final_efficiency_plan_v2.py \
    --efficiency-summarizer summarize_strict_v4_final_efficiency_v2.py \
    --output-dir "$PROTOCOL_ROOT" > "$PROTOCOL_ROOT/freeze.log" 2>&1
fi

if [[ ! -s "$PLAN_ROOT/execution_plan.json" ]]; then
  "$PYTHON" create_strict_v4_final_efficiency_execution_plan_v2.py \
    --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --cache-readiness results/strict_v4_final_efficiency_cache_readiness/cache_readiness.json \
    --candidate-source-root runs/strict_v4_full103_pairwise_caeos_seed7 \
    --comparator-source-root runs/strict_v4_full103_independent_baselines_seed7 \
    --formal-output-root "$FORMAL_ROOT" \
    --output-dir "$PLAN_ROOT" --python "$PYTHON" \
    > "$PLAN_ROOT/creation.log" 2>&1
fi

if [[ ! -f "$REUSE_ROOT/reuse_complete" ]]; then
  "$PYTHON" prepare_strict_v4_final_efficiency_v5_reuse.py \
    --old-protocol "$OLD_PROTOCOL" --new-protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
    --old-plan "$OLD_PLAN" --new-plan "$PLAN_ROOT/execution_plan.json" \
    --old-root "$OLD_FORMAL" --new-root "$FORMAL_ROOT" \
    --failure "$FAILURE_ROOT/failure.json" \
    --archived-old-runtime "$FAILURE_ROOT/pairwise_runtime_v4.py" \
    --active-new-runtime caeos/pairwise_runtime.py \
    --output-dir "$REUSE_ROOT" > "$REUSE_ROOT/execution.log" 2>&1
fi

: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  observed="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  printf '%s sample=%d processes=%q\n' \
    "$(date --iso-8601=seconds)" "$idle_samples" "$observed" >> "$IDLE_LOG"
  if [[ -n "$observed" ]]; then
    idle_samples=0
  else
    idle_samples=$((idle_samples + 1))
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done

"$PYTHON" execute_strict_v4_final_efficiency_plan_v2.py \
  --plan "$PLAN_ROOT/execution_plan.json" --project-root "$PROJECT_ROOT" \
  > "$PLAN_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_final_efficiency_v2.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --plan "$PLAN_ROOT/execution_plan.json" --formal-root "$FORMAL_ROOT" \
  --output-dir "$SUMMARY_ROOT" > "$PLAN_ROOT/summary.log" 2>&1
touch "$SUMMARY_ROOT/recovery_complete"
