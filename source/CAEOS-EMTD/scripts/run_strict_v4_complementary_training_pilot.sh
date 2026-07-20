#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_complementary_training_pilot_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_complementary_training_pilot_seed7"
MODELS="arpl,palm,ronetc,foss"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

"$PYTHON" create_strict_v4_complementary_training_pilot_protocol.py \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --project-root "$PROJECT_ROOT" \
  --pilot-root "$RUN_ROOT" \
  > "$RESULT_ROOT/protocol.log" 2>&1
cp "$RUN_ROOT/protocol_manifest.json" "$RESULT_ROOT/protocol_manifest.json"
cp "$RUN_ROOT/expansion_gate.json" "$RESULT_ROOT/expansion_gate.json"

run_suite() {
  local suite="$1"
  local scenarios="$2"
  shift 2
  nice -n 10 "$PYTHON" run_neural_baseline_matrix.py \
    --suite "$suite" --scenarios "$scenarios" --models "$MODELS" \
    --seeds 7 --workers 4 --epochs 0 --patience 10 \
    --output-root "$RUN_ROOT" "$@" \
    >> "$RESULT_ROOT/training.log" 2>&1
}

run_suite cic_iot2023 ddos_icmp_fragmentation,ddos_rstfin_flood \
  --cic-iot2023-cache-dir "$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported" \
  --cic-iot2023-max-per-class 1000
run_suite cic_ton_iot ddos,mitm \
  --cic-ton-iot-cache-dir "$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified" \
  --cic-ton-iot-max-per-class 1000
run_suite cicids2017 dos_hulk,heartbleed \
  --cicids2017-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/cicids2017/stratified \
  --cicids2017-max-per-class 5000
run_suite edge_iiot ddos_icmp,sql_injection \
  --edge-iiot-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot \
  --edge-iiot-max-per-class 1000
run_suite nf_cse dos_slowhttptest,ssh_bruteforce \
  --nf-cse-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse \
  --nf-cse-max-per-class 1000
run_suite nf_unsw generic,shellcode \
  --nf-unsw-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/nf_unsw/stratified \
  --nf-unsw-max-per-class 5000
run_suite ustc_tfc2016 htbot,tinba \
  --ustc-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016 \
  --ustc-max-per-class 3000

count="$(find "$RUN_ROOT" -mindepth 3 -maxdepth 3 -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -mindepth 3 -maxdepth 3 -name failure.json | wc -l)"
[[ "$count" -eq 56 && "$failures" -eq 0 ]]

"$PYTHON" summarize_strict_v4_complementary_training_pilot.py \
  --pilot-root "$RUN_ROOT" \
  --source-root runs/strict_v4_full103_mlp_seed7 \
  --opendetect-root runs/strict_v4_full103_independent_baselines_seed7 \
  --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/summary.log" 2>&1
