#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
EXTERNAL_MARKER="$PROJECT_ROOT/results/strict_v4_external_confirmation/confirmation_complete"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_seed191_cache"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_protocol_v2"
PLAN_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_execution_plan_v2"
FORMAL_ROOT="$PROJECT_ROOT/runs/strict_v4_final_efficiency_v2"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "seed191 efficiency cache watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$EXTERNAL_MARKER" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
bash scripts/freeze_strict_v4_final_efficiency_protocol_v2.sh \
  > "$RESULT_ROOT/protocol_freeze.log" 2>&1
bash scripts/prepare_strict_v4_final_efficiency_seed191_caches.sh \
  > "$RESULT_ROOT/prepare.log" 2>&1

mkdir -p "$PLAN_ROOT"
"$PYTHON" \
  create_strict_v4_final_efficiency_execution_plan_v2.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --cache-readiness results/strict_v4_final_efficiency_cache_readiness/cache_readiness.json \
  --candidate-source-root runs/strict_v4_full103_pairwise_caeos_seed7 \
  --comparator-source-root runs/strict_v4_full103_independent_baselines_seed7 \
  --formal-output-root "$FORMAL_ROOT" \
  --output-dir "$PLAN_ROOT" \
  --python "$PYTHON" \
  > "$PLAN_ROOT/creation.log" 2>&1
touch "$PLAN_ROOT/plan_complete"

until ! nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null \
  | grep -q '[0-9]'; do
  sleep 60
done
"$PYTHON" \
  execute_strict_v4_final_efficiency_plan_v2.py \
  --plan "$PLAN_ROOT/execution_plan.json" --project-root "$PROJECT_ROOT" \
  > "$PLAN_ROOT/execution.log" 2>&1
"$PYTHON" \
  summarize_strict_v4_final_efficiency_v2.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --plan "$PLAN_ROOT/execution_plan.json" \
  --formal-root "$FORMAL_ROOT" \
  --output-dir "$PROJECT_ROOT/results/strict_v4_final_efficiency_v2" \
  > "$PLAN_ROOT/summary.log" 2>&1

CORRUPTION_PROTOCOL="$PROJECT_ROOT/results/strict_v4_postselection_corruption_seed7/protocol_manifest.json"
CORRUPTION_RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_postselection_corruption_seed7"
CORRUPTION_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_postselection_corruption_confirmation"
"$PYTHON" run_strict_v4_postselection_corruption.py \
  --protocol "$CORRUPTION_PROTOCOL" \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --pairwise-candidate results/strict_v4_boundary_pairwise_development/candidate_manifest.json \
  --clean-root runs/strict_v4_full103_pairwise_caeos_seed7 \
  --cache-root caches/strict_v4_domain_safe_router_confirmation \
  --output-root "$CORRUPTION_RUN_ROOT" \
  > "$CORRUPTION_RESULT_ROOT.execution.log" 2>&1
"$PYTHON" summarize_strict_v4_postselection_corruption.py \
  --protocol "$CORRUPTION_PROTOCOL" \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --run-root "$CORRUPTION_RUN_ROOT" \
  --output-dir "$CORRUPTION_RESULT_ROOT" \
  > "$CORRUPTION_RESULT_ROOT.summary.log" 2>&1

COMPARATIVE_PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_comparative_corruption_protocol"
COMPARATIVE_RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_comparative_corruption"
COMPARATIVE_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_comparative_corruption"
mkdir -p "$COMPARATIVE_PROTOCOL_ROOT" "$COMPARATIVE_RESULT_ROOT"
"$PYTHON" create_strict_v4_comparative_corruption_protocol.py \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --decision results/strict_v4_optimal_self_algorithm/decision.json \
  --external-confirmation results/strict_v4_external_confirmation/confirmation.json \
  --candidate-corruption-protocol "$CORRUPTION_PROTOCOL" \
  --candidate-corruption-summary "$CORRUPTION_RESULT_ROOT/summary.json" \
  --candidate-root runs/strict_v4_domain_safe_router_confirmation_caeos \
  --comparator-root runs/strict_v4_external_comparator_confirmation \
  --candidate-trainer train_hybrid_open_set.py \
  --candidate-runtime caeos/pairwise_runtime.py \
  --candidate-capture capture_pairwise_runtime.py \
  --comparator-runtime caeos/open_detect_runtime.py \
  --comparator-capture capture_opendetect_runtime.py \
  --evaluator evaluate_strict_v4_comparative_corruption.py \
  --runner run_strict_v4_comparative_corruption.py \
  --summarizer summarize_strict_v4_comparative_corruption.py \
  --run-root "$COMPARATIVE_RUN_ROOT" \
  --output-dir "$COMPARATIVE_PROTOCOL_ROOT" \
  > "$COMPARATIVE_PROTOCOL_ROOT/freeze.log" 2>&1
"$PYTHON" run_strict_v4_comparative_corruption.py \
  --protocol "$COMPARATIVE_PROTOCOL_ROOT/protocol_manifest.json" \
  --output-root "$COMPARATIVE_RUN_ROOT" \
  --project-root "$PROJECT_ROOT" \
  > "$COMPARATIVE_RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_comparative_corruption.py \
  --protocol "$COMPARATIVE_PROTOCOL_ROOT/protocol_manifest.json" \
  --run-root "$COMPARATIVE_RUN_ROOT" \
  --output-dir "$COMPARATIVE_RESULT_ROOT" \
  > "$COMPARATIVE_RESULT_ROOT/summary.log" 2>&1

until [[ -f "$PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit/audit_complete" ]]; do
  sleep 60
done
"$PYTHON" audit_strict_v4_final_paper_readiness.py \
  --accuracy-audit results/strict_v4_comprehensive_sota_audit/audit.json \
  --efficiency-summary results/strict_v4_final_efficiency_v2/summary.json \
  --corruption-summary "$CORRUPTION_RESULT_ROOT/summary.json" \
  --comparative-corruption-summary "$COMPARATIVE_RESULT_ROOT/summary.json" \
  --output-dir results/strict_v4_final_paper_readiness \
  > results/strict_v4_final_paper_readiness.log 2>&1
