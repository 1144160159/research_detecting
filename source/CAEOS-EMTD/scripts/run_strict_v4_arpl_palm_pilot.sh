#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_arpl_palm_pilot"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_arpl_palm_pilot"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_ton_iot \
  --scenarios xss,scanning,ransomware \
  --models arpl,palm \
  --seeds 7 \
  --workers 2 \
  --epochs 0 \
  --patience 10 \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  --cic-ton-iot-max-per-class 1000 \
  --output-root "$RUN_ROOT" \
  > "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_iot2023 \
  --scenarios ddos_icmp_flood,mirai_udpplain,command_injection \
  --models arpl,palm \
  --seeds 7 \
  --workers 2 \
  --epochs 0 \
  --patience 10 \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  --cic-iot2023-max-per-class 1000 \
  --output-root "$RUN_ROOT" \
  >> "$RESULT_ROOT/training.log" 2>&1

count="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
printf 'complete metrics=%s failures=%s\n' "$count" "$failures" \
  >> "$RESULT_ROOT/training.log"
[[ "$count" -eq 12 && "$failures" -eq 0 ]]
touch "$RESULT_ROOT/training_complete"
