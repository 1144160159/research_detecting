#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SEED=7
MAX_PER_CLASS=1000
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_boundary_pairwise_development"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"
POLICY_NAME="strict_v4_boundary_pairwise_development_v1"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

COMMON=(
  --seeds "$SEED"
  --workers 2
  --model-jobs 8
  --estimators 80
  --risk-selection nested_boundary_pairwise_pseudo_unknown_blend
  --pseudo-unknown-max-alpha 0.5
  --pseudo-unknown-min-fold-gain -1.0
  --boundary-hard-pseudo-fraction 0.5
  --boundary-interpolation 0.5
  --boundary-max-per-task 512
  --boundary-training-objective pairwise
  --risk-policy-name "$POLICY_NAME"
  --output-root "$RUN_ROOT"
)

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_ton_iot \
  --scenarios injection,password,scanning \
  "${COMMON[@]}" \
  --cic-ton-iot-max-per-class "$MAX_PER_CLASS" \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  > "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 \
  --scenarios browser_hijacking,ddos_http_flood,recon_host_discovery \
  "${COMMON[@]}" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  >> "$RESULT_ROOT/training.log" 2>&1

touch "$RESULT_ROOT/training_complete"
