#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PAIRWISE_MANIFEST="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development/candidate_manifest.json"
EXTERNAL_MANIFEST="$PROJECT_ROOT/results/strict_v4_external_risk_diagnostic/candidate_manifest.json"
RUN_CAEOS="$PROJECT_ROOT/runs/strict_v4_full103_pairwise_caeos_seed7"
RUN_MLP="$PROJECT_ROOT/runs/strict_v4_full103_mlp_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_full103_seed7"
MANIFEST="$RESULT_ROOT/coverage_manifest_v2.json"
POLICY="strict_v4_full103_pairwise_coverage_v1"

EDGE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
EDGE_CACHE="$EDGE_DIR/seed7_max1000.csv"
NF_CSE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse"
NF_CSE_CACHE="$NF_CSE_DIR/seed7_max1000.csv"
USTC_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016"
USTC_CACHE="$USTC_DIR/seed7_max3000.csv"
NF_UNSW_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/nf_unsw/stratified"
NF_UNSW_CACHE="$NF_UNSW_DIR/seed7_max5000.csv"
CICIDS_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/cicids2017/stratified"
CICIDS_CACHE="$CICIDS_DIR/seed7_max5000.csv"
TON_DIR="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
TON_CACHE="$TON_DIR/seed7_max1000.csv"
CICIOT_DIR="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"
CICIOT_CACHE="$CICIOT_DIR/seed7_max1000.csv"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

if [[ ! -s "$MANIFEST" ]]; then
  "$PYTHON" create_strict_v4_full103_manifest.py \
    --project-root "$PROJECT_ROOT" \
    --pairwise-manifest "$PAIRWISE_MANIFEST" \
    --external-manifest "$EXTERNAL_MANIFEST" \
    --cache "edge_iiot=$EDGE_CACHE" \
    --cache "nf_cse=$NF_CSE_CACHE" \
    --cache "ustc_tfc2016=$USTC_CACHE" \
    --cache "nf_unsw=$NF_UNSW_CACHE" \
    --cache "cicids2017=$CICIDS_CACHE" \
    --cache "cic_ton_iot=$TON_CACHE" \
    --cache "cic_iot2023=$CICIOT_CACHE" \
    --output "$MANIFEST" > "$RESULT_ROOT/manifest.log"
fi

read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK OBJECTIVE < <(
  "$PYTHON" -c \
    'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"], c["minimum_fold_gain"], c["hard_pseudo_fraction"], c["interpolation"], c["max_per_task"], c["training_objective"])' \
    "$PAIRWISE_MANIFEST"
)

run_caeos_suite() {
  local suite="$1"
  shift
  "$PYTHON" run_nested_gate_matrix.py \
    --suite "$suite" --scenarios all --seeds 7 \
    --workers 2 --model-jobs 8 --estimators 80 \
    --risk-selection nested_boundary_pairwise_pseudo_unknown_blend \
    --pseudo-unknown-max-alpha "$MAX_ALPHA" \
    --pseudo-unknown-min-fold-gain "$MIN_FOLD" \
    --boundary-hard-pseudo-fraction "$HARD_FRACTION" \
    --boundary-interpolation "$INTERPOLATION" \
    --boundary-max-per-task "$MAX_TASK" \
    --boundary-training-objective "$OBJECTIVE" \
    --risk-policy-name "$POLICY" \
    --output-root "$RUN_CAEOS" "$@" \
    >> "$RESULT_ROOT/caeos_${suite}.log" 2>&1
}

run_mlp_suite() {
  local suite="$1"
  shift
  "$PYTHON" run_neural_baseline_matrix.py \
    --suite "$suite" --scenarios all --models mlp --seeds 7 \
    --workers 2 --epochs 0 --patience 10 \
    --output-root "$RUN_MLP" "$@" \
    >> "$RESULT_ROOT/mlp_${suite}.log" 2>&1
}

run_caeos_suite edge_iiot --edge-iiot-cache-dir "$EDGE_DIR" --edge-iiot-max-per-class 1000
run_caeos_suite nf_cse --nf-cse-cache-dir "$NF_CSE_DIR" --nf-cse-max-per-class 1000
run_caeos_suite ustc_tfc2016 --ustc-cache-dir "$USTC_DIR" --ustc-max-per-class 3000
run_caeos_suite nf_unsw --nf-unsw-cache-dir "$NF_UNSW_DIR" --nf-unsw-max-per-class 5000
run_caeos_suite cicids2017 --cicids2017-cache-dir "$CICIDS_DIR" --cicids2017-max-per-class 5000
run_caeos_suite cic_ton_iot --cic-ton-iot-cache-dir "$TON_DIR" --cic-ton-iot-max-per-class 1000
run_caeos_suite cic_iot2023 --cic-iot2023-cache-dir "$CICIOT_DIR" --cic-iot2023-max-per-class 1000

caeos_count="$(find "$RUN_CAEOS" -name metrics.json | wc -l)"
caeos_failures="$(find "$RUN_CAEOS" -name failure.json | wc -l)"
printf 'pairwise CAEOS metrics=%s failures=%s\n' "$caeos_count" "$caeos_failures" \
  > "$RESULT_ROOT/coverage.log"
[[ "$caeos_count" -eq 102 && "$caeos_failures" -eq 0 ]]
touch "$RESULT_ROOT/caeos_complete"

run_mlp_suite edge_iiot --edge-iiot-cache-dir "$EDGE_DIR" --edge-iiot-max-per-class 1000
run_mlp_suite nf_cse --nf-cse-cache-dir "$NF_CSE_DIR" --nf-cse-max-per-class 1000
run_mlp_suite ustc_tfc2016 --ustc-cache-dir "$USTC_DIR" --ustc-max-per-class 3000
run_mlp_suite nf_unsw --nf-unsw-cache-dir "$NF_UNSW_DIR" --nf-unsw-max-per-class 5000
run_mlp_suite cicids2017 --cicids2017-cache-dir "$CICIDS_DIR" --cicids2017-max-per-class 5000
run_mlp_suite cic_ton_iot --cic-ton-iot-cache-dir "$TON_DIR" --cic-ton-iot-max-per-class 1000
run_mlp_suite cic_iot2023 --cic-iot2023-cache-dir "$CICIOT_DIR" --cic-iot2023-max-per-class 1000

mlp_count="$(find "$RUN_MLP" -name metrics.json | wc -l)"
mlp_failures="$(find "$RUN_MLP" -name failure.json | wc -l)"
printf 'MLP metrics=%s failures=%s\n' "$mlp_count" "$mlp_failures" \
  >> "$RESULT_ROOT/coverage.log"
[[ "$mlp_count" -eq 102 && "$mlp_failures" -eq 0 ]]
touch "$RESULT_ROOT/mlp_complete"

"$PYTHON" analyze_caeos_closr_fusion.py \
  --gate-root "$RUN_CAEOS" \
  --expert-root "$RUN_MLP" \
  --expert-name openmax --expert-model mlp --seeds 7 \
  --output "$RESULT_ROOT/raw_fusion.json" \
  > "$RESULT_ROOT/fusion.log" 2>&1

"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert len(p["runs"]) == 102; assert p["overall"]["number_of_runs"] == 102; assert all(r["audit"]["split_fingerprints_identical"] for r in p["runs"])' \
  "$RESULT_ROOT/raw_fusion.json"
touch "$RESULT_ROOT/full103_complete"
