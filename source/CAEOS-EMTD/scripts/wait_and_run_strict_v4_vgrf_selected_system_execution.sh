#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_selected_system_confirmation_v1"
DESIGN="$ROOT/design_protocol.json"
PREPARATION="$ROOT/preparation_protocol.json"
EXECUTION_REQUIRED="$ROOT/execution_required.json"
EXECUTION_PROTOCOL="$ROOT/execution_protocol.json"
SELECTION_ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_confirmation_seed311_313"
SELECTION="$SELECTION_ROOT/final_selection.json"
VGRF_PROTOCOL="$SELECTION_ROOT/protocol_manifest.json"
VGRF_SUMMARY="$SELECTION_ROOT/summary.json"
EXTERNAL_ROOT="$PROJECT_ROOT/results/strict_v4_selected_external_reconfirmation_seed311_313"
EXTERNAL_PROTOCOL="$EXTERNAL_ROOT/protocol_manifest.json"
EXTERNAL_SUMMARY="$EXTERNAL_ROOT/summary.json"
EXTERNAL_RUN="$PROJECT_ROOT/runs/strict_v4_selected_external_reconfirmation_seed311_313"
CORRUPTION_PROTOCOL="$PROJECT_ROOT/results/strict_v4_postselection_corruption_seed7/protocol_manifest.json"
SEED317_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_selected_system_seed317"
DEPLOYMENT_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_selected_system_deployments"
BENCHMARK_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_selected_system_benchmark"
TRAINING_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_selected_system_training_efficiency"
CORRUPTION_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_selected_system_corruption"
SEED317_STATE="$ROOT/seed317_state.json"
CAPTURE_STATE="$ROOT/capture_state.json"
BENCHMARK_STATE="$ROOT/benchmark_state.json"
TRAINING_STATE="$ROOT/training_efficiency_state.json"
CORRUPTION_STATE="$ROOT/corruption_state.json"
SUMMARY="$ROOT/summary.json"
LOCK="$ROOT/execution_watcher.lock.d"
STATE="$ROOT/execution_state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "VGRF selected-system execution watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

printf '%s waiting for final algorithm selection\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -f "$SELECTION_ROOT/branch_complete" && -s "$SELECTION" ]]; do
  sleep 60
done

selected="$("$PYTHON" - "$SELECTION" <<'PY'
import json
import sys

print(json.load(open(sys.argv[1], encoding="utf-8"))["selected_algorithm"])
PY
)"
if [[ "$selected" == "caeos_pairwise" ]]; then
  printf '%s Pairwise selected; VGRF system execution not required\n' \
    "$(date --iso-8601=seconds)" >> "$STATE"
  exit 0
fi
if [[ "$selected" != "caeos_validation_gated_class_conditional_reliability_fusion" ]]; then
  echo "unsupported selected algorithm: $selected" >&2
  exit 1
fi

printf '%s VGRF selected; waiting for source-producing branches\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
until [[ -s "$DESIGN" \
  && -s "$PREPARATION" \
  && -s "$EXECUTION_REQUIRED" \
  && -s "$VGRF_PROTOCOL" \
  && -s "$VGRF_SUMMARY" \
  && -f "$EXTERNAL_ROOT/branch_complete" \
  && -s "$EXTERNAL_PROTOCOL" \
  && -s "$EXTERNAL_SUMMARY" \
  && -s "$CORRUPTION_PROTOCOL" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
if [[ ! -s "$EXECUTION_PROTOCOL" ]]; then
  "$PYTHON" create_strict_v4_vgrf_selected_system_execution_protocol.py \
    --project-root "$PROJECT_ROOT" \
    --design "$DESIGN" \
    --preparation "$PREPARATION" \
    --final-selection "$SELECTION" \
    --vgrf-protocol "$VGRF_PROTOCOL" \
    --vgrf-summary "$VGRF_SUMMARY" \
    --selected-external-protocol "$EXTERNAL_PROTOCOL" \
    --selected-external-summary "$EXTERNAL_SUMMARY" \
    --corruption-protocol "$CORRUPTION_PROTOCOL" \
    --comparator-root "$EXTERNAL_RUN" \
    --seed317-run-root "$SEED317_ROOT" \
    --deployment-root "$DEPLOYMENT_ROOT" \
    --benchmark-root "$BENCHMARK_ROOT" \
    --corruption-root "$CORRUPTION_ROOT" \
    --result-root "$ROOT" \
    --implementation run_strict_v4_vgrf_selected_system_seed317.py \
    --implementation run_strict_v4_vgrf_selected_system_capture.py \
    --implementation benchmark_strict_v4_vgrf_selected_system.py \
    --implementation run_strict_v4_vgrf_selected_system_training_efficiency.py \
    --implementation evaluate_strict_v4_vgrf_selected_system_corruption.py \
    --implementation run_strict_v4_vgrf_selected_system_corruption.py \
    --implementation summarize_strict_v4_vgrf_selected_system.py \
    --implementation capture_pairwise_deployment_bundle.py \
    --implementation audit_pairwise_deployment_bundle.py \
    --implementation build_vgrf_deployment_bundle.py \
    --implementation audit_vgrf_deployment_bundle.py \
    --implementation capture_opendetect_deployment_bundle.py \
    --implementation audit_opendetect_deployment_bundle.py \
    --implementation capture_opendetect_training_runtime.py \
    --implementation train_hybrid_open_set.py \
    --implementation train_neural_open_set.py \
    --implementation caeos/pairwise_deployment.py \
    --implementation caeos/vgrf_deployment.py \
    --implementation caeos/opendetect_deployment.py \
    --implementation caeos/class_conditional_reliability_fusion.py \
    --implementation caeos/validation_gated_reliability_fusion.py \
    --implementation caeos/open_detect.py \
    --output "$EXECUTION_PROTOCOL" \
    > "$ROOT/execution_protocol_freeze.log" 2>&1
fi

idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(pgrep -af 'train_|run_strict|execute_strict|corruption|gpu_external' \
    | grep -v -E 'wait_and_|pgrep -af|vgrf_selected_system_execution' || true)"
  if [[ -z "$gpu_processes" && -z "$experiment_processes" ]]; then
    idle_samples=$((idle_samples + 1))
  else
    idle_samples=0
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done

run_low_priority() {
  local log="$1"
  shift
  nice -n 15 ionice -c 3 "$@" >> "$log" 2>&1
}

printf '%s running 102 seed317 source triples\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
run_low_priority "$ROOT/seed317_execution.log" \
  "$PYTHON" run_strict_v4_vgrf_selected_system_seed317.py \
  --protocol "$EXECUTION_PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --state "$SEED317_STATE"

printf '%s capturing and auditing 306 deployment triples\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
run_low_priority "$ROOT/deployment_capture.log" \
  "$PYTHON" run_strict_v4_vgrf_selected_system_capture.py \
  --protocol "$EXECUTION_PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --state "$CAPTURE_STATE"

printf '%s running 42 clean-process training efficiency blocks\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
run_low_priority "$ROOT/training_efficiency.log" \
  "$PYTHON" run_strict_v4_vgrf_selected_system_training_efficiency.py \
  --protocol "$EXECUTION_PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --output-root "$TRAINING_ROOT" \
  --state "$TRAINING_STATE"

printf '%s running 204 same-hardware runtime blocks\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
run_low_priority "$ROOT/runtime_benchmark.log" \
  "$PYTHON" benchmark_strict_v4_vgrf_selected_system.py \
  --protocol "$EXECUTION_PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --output-root "$BENCHMARK_ROOT" \
  --state "$BENCHMARK_STATE"

printf '%s running 1530 paired corruption conditions\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
run_low_priority "$ROOT/corruption_execution.log" \
  "$PYTHON" run_strict_v4_vgrf_selected_system_corruption.py \
  --protocol "$EXECUTION_PROTOCOL" \
  --output-root "$CORRUPTION_ROOT" \
  --state "$CORRUPTION_STATE"

printf '%s summarizing VGRF selected-system evidence\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
"$PYTHON" summarize_strict_v4_vgrf_selected_system.py \
  --protocol "$EXECUTION_PROTOCOL" \
  --capture-state "$CAPTURE_STATE" \
  --training-state "$TRAINING_STATE" \
  --benchmark-state "$BENCHMARK_STATE" \
  --corruption-state "$CORRUPTION_STATE" \
  --output-dir "$ROOT" \
  > "$ROOT/summary.log" 2>&1
printf '%s VGRF selected-system execution complete\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
