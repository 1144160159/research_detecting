#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_optimal_self_algorithm"
PAIRWISE_ROOT="$PROJECT_ROOT/runs/strict_v4_tail_aware_incumbent_pairwise"
TAIL_ROOT="$PROJECT_ROOT/runs/strict_v4_tail_aware_confirmation"
CACHE_ROOT="$PROJECT_ROOT/caches/strict_v4_tail_aware_confirmation"
PROTOCOL="$RESULT_ROOT/tournament_protocol.json"
TAIL_CONFIRMATION="$PROJECT_ROOT/results/strict_v4_tail_aware_confirmation/confirmation.json"
INCUMBENT="$PROJECT_ROOT/results/strict_v4_final_algorithm/decision.json"
ROUTER="$PROJECT_ROOT/results/strict_v4_domain_safe_router_development/candidate_manifest.json"
PAIRWISE_MANIFEST="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development/candidate_manifest.json"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$PAIRWISE_ROOT"
read -r TAIL_PASSES < <(
  "$PYTHON" -c 'import json,sys; print(str(json.load(open(sys.argv[1]))["decision"]["passes"]).lower())' "$TAIL_CONFIRMATION"
)
if [[ "$TAIL_PASSES" == "true" ]]; then
  mapfile -t VALUES < <(
    "$PYTHON" -c 'import json,sys; p=json.load(open(sys.argv[1])); h=p["head_to_head"]; print(",".join(map(str,h["seeds"]))); print(h["expected_pairwise_runs"]); print(h["pairwise_risk_policy"])' "$PROTOCOL"
  )
  SEEDS="${VALUES[0]}"
  EXPECTED="${VALUES[1]}"
  POLICY="${VALUES[2]}"
  read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK OBJECTIVE < <(
    "$PYTHON" -c 'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"],c["minimum_fold_gain"],c["hard_pseudo_fraction"],c["interpolation"],c["max_per_task"],c["training_objective"])' "$PAIRWISE_MANIFEST"
  )
  COMMON=(
    --scenarios all --seeds "$SEEDS" --workers 2 --model-jobs 8 --estimators 80
    --risk-selection nested_boundary_pairwise_pseudo_unknown_blend
    --pseudo-unknown-max-alpha "$MAX_ALPHA"
    --pseudo-unknown-min-fold-gain "$MIN_FOLD"
    --boundary-hard-pseudo-fraction "$HARD_FRACTION"
    --boundary-interpolation "$INTERPOLATION"
    --boundary-max-per-task "$MAX_TASK"
    --boundary-training-objective "$OBJECTIVE"
    --risk-policy-name "$POLICY" --output-root "$PAIRWISE_ROOT"
  )
  run_suite() {
    local suite="$1"; shift
    "$PYTHON" run_nested_gate_matrix.py --suite "$suite" "${COMMON[@]}" "$@" \
      >> "$RESULT_ROOT/pairwise_training.log" 2>&1
  }
  run_suite edge_iiot --edge-iiot-cache-dir "$CACHE_ROOT/edge_iiot" --edge-iiot-max-per-class 1000
  run_suite nf_cse --nf-cse-cache-dir "$CACHE_ROOT/nf_cse" --nf-cse-max-per-class 1000
  run_suite ustc_tfc2016 --ustc-cache-dir "$CACHE_ROOT/ustc_tfc2016" --ustc-max-per-class 3000
  run_suite nf_unsw --nf-unsw-cache-dir "$CACHE_ROOT/nf_unsw" --nf-unsw-max-per-class 5000
  run_suite cicids2017 --cicids2017-cache-dir "$CACHE_ROOT/cicids2017" --cicids2017-max-per-class 5000
  run_suite cic_ton_iot --cic-ton-iot-cache-dir "$CACHE_ROOT/cic_ton_iot" --cic-ton-iot-max-per-class 1000
  run_suite cic_iot2023 --cic-iot2023-cache-dir "$CACHE_ROOT/cic_iot2023" --cic-iot2023-max-per-class 1000
  [[ "$(find "$PAIRWISE_ROOT" -name metrics.json | wc -l)" -eq "$EXPECTED" ]]
  [[ "$(find "$PAIRWISE_ROOT" -name failure.json | wc -l)" -eq 0 ]]
  "$PYTHON" confirm_strict_v4_tail_vs_incumbent.py \
    --protocol "$PROTOCOL" --router-manifest "$ROUTER" \
    --incumbent-decision "$INCUMBENT" --tail-root "$TAIL_ROOT" \
    --pairwise-root "$PAIRWISE_ROOT" --output-dir "$RESULT_ROOT" \
    > "$RESULT_ROOT/head_to_head.log" 2>&1
  HEAD_ARGS=(--head-to-head "$RESULT_ROOT/head_to_head.json")
else
  HEAD_ARGS=()
fi

"$PYTHON" select_strict_v4_optimal_self_algorithm.py \
  --protocol "$PROTOCOL" --incumbent-decision "$INCUMBENT" \
  --tail-confirmation "$TAIL_CONFIRMATION" "${HEAD_ARGS[@]}" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/selection.log" 2>&1
touch "$RESULT_ROOT/decision_complete"
