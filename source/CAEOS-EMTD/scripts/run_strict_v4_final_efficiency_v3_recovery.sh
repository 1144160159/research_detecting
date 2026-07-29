#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_protocol_v3"
PLAN_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_execution_plan_v3"
FORMAL_ROOT="$PROJECT_ROOT/runs/strict_v4_final_efficiency_v3"
SUMMARY_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_v3"
DIAGNOSTIC="$PROJECT_ROOT/results/strict_v4_final_efficiency_repeatability_diagnostic/browser_hijacking_v3.json"
LOCK_DIR="$PLAN_ROOT/recovery.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$PROTOCOL_ROOT" "$PLAN_ROOT" "$SUMMARY_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "efficiency v3 recovery already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

"$PYTHON" - "$DIAGNOSTIC" <<'PY'
import json, sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["prediction_array_equal"] is True
assert report["risk_max_absolute_difference"] <= 1e-12
assert report["component_max_absolute_difference"] <= 1e-12
PY

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

until ! nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null \
  | grep -q '[0-9]'; do
  sleep 60
done
"$PYTHON" execute_strict_v4_final_efficiency_plan_v2.py \
  --plan "$PLAN_ROOT/execution_plan.json" --project-root "$PROJECT_ROOT" \
  > "$PLAN_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_final_efficiency_v2.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --plan "$PLAN_ROOT/execution_plan.json" --formal-root "$FORMAL_ROOT" \
  --output-dir "$SUMMARY_ROOT" > "$PLAN_ROOT/summary.log" 2>&1
touch "$SUMMARY_ROOT/recovery_complete"
