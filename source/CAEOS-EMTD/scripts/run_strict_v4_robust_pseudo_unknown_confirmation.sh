#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
TON_SOURCE="${TON_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv}"
CICIOT_SOURCE="${CICIOT_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV}"
SEEDS_COMMA="83,89"
SEEDS_SPACE="83 89"
MAX_PER_CLASS=1000
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_robust_pseudo_unknown_confirmation"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_robust_pseudo_unknown_confirmation"
MANIFEST="$PROJECT_ROOT/results/strict_v4_robust_pseudo_unknown_development/candidate_manifest.json"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4_robust_pseudo_unknown_confirmation/cic_ton_iot/stratified"
CICIOT_RAW="$PROJECT_ROOT/caches/strict_v4_robust_pseudo_unknown_confirmation/cic_iot2023/raw"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4_robust_pseudo_unknown_confirmation/cic_iot2023/group_supported"
POLICY_NAME="strict_v4_robust_pseudo_unknown_confirmation_v1"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$TON_CACHE" "$CICIOT_RAW" "$CICIOT_CACHE"
read -r MAX_ALPHA MIN_FOLD_GAIN < <(
  "$PYTHON" -c \
    'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"], c["minimum_fold_gain"])' \
    "$MANIFEST"
)

for seed in $SEEDS_SPACE; do
  ton_output="$TON_CACHE/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$ton_output" ]]; then
    "$PYTHON" prepare_stratified_cache.py \
      --csv "$TON_SOURCE" \
      --config configs/cic_ton_iot_strict.json \
      --max-per-class "$MAX_PER_CLASS" \
      --chunksize 50000 \
      --seed "$seed" \
      --output "$ton_output"
  fi

  ciciot_raw="$CICIOT_RAW/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$ciciot_raw" ]]; then
    "$PYTHON" prepare_cic_iot2023_strict.py \
      --input-dir "$CICIOT_SOURCE" \
      --output "$ciciot_raw" \
      --seed "$seed" \
      --max-per-class "$MAX_PER_CLASS" \
      --group-rows 1000 \
      --expected-source-files 309
  fi

  ciciot_output="$CICIOT_CACHE/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$ciciot_output" ]]; then
    "$PYTHON" prepare_group_supported_cache.py \
      --input "$ciciot_raw" \
      --output "$ciciot_output" \
      --label-column Attack \
      --group-column CaptureGroup \
      --minimum-groups 3
  fi
done > "$RESULT_ROOT/cache_preparation.log" 2>&1

sha256sum "$TON_CACHE"/*.csv "$CICIOT_RAW"/*.csv "$CICIOT_CACHE"/*.csv \
  > "$RESULT_ROOT/cache_sha256.txt"

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_ton_iot \
  --scenarios mitm,ransomware,xss \
  --seeds "$SEEDS_COMMA" \
  --workers 2 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection nested_robust_pseudo_unknown_blend \
  --pseudo-unknown-max-alpha "$MAX_ALPHA" \
  --pseudo-unknown-min-fold-gain "$MIN_FOLD_GAIN" \
  --risk-policy-name "$POLICY_NAME" \
  --cic-ton-iot-max-per-class "$MAX_PER_CLASS" \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  --output-root "$RUN_ROOT" \
  > "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 \
  --scenarios ddos_syn_flood,dns_spoofing,recon_port_scan \
  --seeds "$SEEDS_COMMA" \
  --workers 2 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection nested_robust_pseudo_unknown_blend \
  --pseudo-unknown-max-alpha "$MAX_ALPHA" \
  --pseudo-unknown-min-fold-gain "$MIN_FOLD_GAIN" \
  --risk-policy-name "$POLICY_NAME" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  --output-root "$RUN_ROOT" \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" confirm_strict_v4_robust_pseudo_unknown.py \
  --root "$RUN_ROOT" \
  --manifest "$MANIFEST" \
  --project-root "$PROJECT_ROOT" \
  --output-dir "$RESULT_ROOT" \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["validation"]["run_count"] == 12; assert p["validation"]["scenario_count"] == 6; assert p["validation"]["seeds"] == [83,89]; assert isinstance(p["decision"]["passes"], bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
