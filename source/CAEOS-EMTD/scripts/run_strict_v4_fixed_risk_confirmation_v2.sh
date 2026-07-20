#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
TON_SOURCE="${TON_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv}"
CICIOT_SOURCE="${CICIOT_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV}"
SEEDS_COMMA="23,37"
SEEDS_SPACE="23 37"
MAX_PER_CLASS=1000
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_fixed_risk_confirmation_v2"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_fixed_risk_confirmation_v2"
MANIFEST="$PROJECT_ROOT/results/strict_v4_risk_screening_v2/candidate_manifest.json"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4_confirmation_v2/cic_ton_iot/stratified"
CICIOT_RAW="$PROJECT_ROOT/caches/strict_v4_confirmation_v2/cic_iot2023/raw"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4_confirmation_v2/cic_iot2023/group_supported"
POLICY_NAME="strict_v4_confirmation_current_policy_v1"

verify_sha() {
  local expected="$1" path="$2" actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$TON_CACHE" "$CICIOT_RAW" "$CICIOT_CACHE"
verify_sha "483698a309206b570e11708e72fe1005922e3ff6961a6015ef3a44e6abb0f81d" train_hybrid_open_set.py
verify_sha "d3d85d6df41601a6ba1820ae763525b24f34c4d98e9fdba866609b6ec3df4155" run_nested_gate_matrix.py
verify_sha "1cbbcb89fca8b10984a42460f09232d43bdfc06489af9a4df52b3d6e098652e0" prepare_stratified_cache.py
verify_sha "1c57f250e9a24c0cad04c36c99ab0f0c75af19d9be56235b2e724dc38dfa77fd" prepare_cic_iot2023_strict.py
verify_sha "5d027b18ce591f89d9a2de405acdad7b2250bd75c9e5829566fd2a4293c94a07" prepare_group_supported_cache.py
verify_sha "9fdc13c759347a5e19e728b3ee64d271c415456ab6a9c9183ea76b3b58ba3bca" confirm_strict_v4_fixed_risk.py
verify_sha "8c1e9062f0e8e8447b849718c6dfb63f036ee2221295fddb5abef69ca54c3969" screen_strict_v4_risk_candidates_v2.py
verify_sha "d66c4445f9d961097113e1e27b40e7f4249871efcf0b45efa6a31d367c68fe8b" "$MANIFEST"

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

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_ton_iot \
  --scenarios injection,mitm,dos \
  --seeds "$SEEDS_COMMA" \
  --workers 1 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name "$POLICY_NAME" \
  --cic-ton-iot-max-per-class "$MAX_PER_CLASS" \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  --output-root "$RUN_ROOT" \
  > "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 \
  --scenarios backdoor_malware,ddos_http_flood,dictionary_bruteforce \
  --seeds "$SEEDS_COMMA" \
  --workers 1 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name "$POLICY_NAME" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  --output-root "$RUN_ROOT" \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" confirm_strict_v4_fixed_risk.py \
  --root "$RUN_ROOT" \
  --manifest "$MANIFEST" \
  --output-dir "$RESULT_ROOT" \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["validation"]["run_count"] == 12; assert p["validation"]["scenario_count"] == 6; assert p["validation"]["seeds"] == [23,37]; assert isinstance(p["decision"]["passes"], bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
