#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_full103_baselines_seed7"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_independent_baselines_seed7"
COVERAGE_MANIFEST="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
UPSTREAM_MARKER="$PROJECT_ROOT/results/strict_v4_full103_seed7/full103_complete"
MANIFEST="$RESULT_ROOT/baseline_manifest_v2.json"

EDGE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
NF_CSE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse"
USTC_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016"
NF_UNSW_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/nf_unsw/stratified"
CICIDS_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/cicids2017/stratified"
TON_DIR="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
CICIOT_DIR="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
if [[ ! -f "$UPSTREAM_MARKER" ]]; then
  echo "full103 candidate coverage is incomplete: $UPSTREAM_MARKER" >&2
  exit 1
fi
if [[ ! -s "$MANIFEST" ]]; then
  "$PYTHON" create_strict_v4_full103_baseline_manifest.py \
    --project-root "$PROJECT_ROOT" \
    --coverage-manifest "$COVERAGE_MANIFEST" \
    --output "$MANIFEST" > "$RESULT_ROOT/manifest.log"
fi

run_suite() {
  local suite="$1"
  shift
  "$PYTHON" run_neural_baseline_matrix.py \
    --suite "$suite" --scenarios all \
    --models opendetect,classical_ood --seeds 7 \
    --workers 2 --epochs 0 --patience 10 \
    --output-root "$RUN_ROOT" "$@" \
    >> "$RESULT_ROOT/${suite}.log" 2>&1
}

run_suite edge_iiot --edge-iiot-cache-dir "$EDGE_DIR" --edge-iiot-max-per-class 1000
run_suite nf_cse --nf-cse-cache-dir "$NF_CSE_DIR" --nf-cse-max-per-class 1000
run_suite ustc_tfc2016 --ustc-cache-dir "$USTC_DIR" --ustc-max-per-class 3000
run_suite nf_unsw --nf-unsw-cache-dir "$NF_UNSW_DIR" --nf-unsw-max-per-class 5000
run_suite cicids2017 --cicids2017-cache-dir "$CICIDS_DIR" --cicids2017-max-per-class 5000
run_suite cic_ton_iot --cic-ton-iot-cache-dir "$TON_DIR" --cic-ton-iot-max-per-class 1000
run_suite cic_iot2023 --cic-iot2023-cache-dir "$CICIOT_DIR" --cic-iot2023-max-per-class 1000

metrics_count="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
printf 'baseline run directories=%s/204 failures=%s\n' "$metrics_count" "$failures" \
  > "$RESULT_ROOT/coverage.log"
[[ "$metrics_count" -eq 204 && "$failures" -eq 0 ]]
touch "$RESULT_ROOT/full103_baselines_complete"
