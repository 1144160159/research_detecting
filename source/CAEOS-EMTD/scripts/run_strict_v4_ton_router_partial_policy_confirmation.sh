#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
TON_SOURCE="${TON_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv}"
SEEDS_COMMA="67,71"
SEEDS_SPACE="67 71"
MAX_PER_CLASS=1000
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_ton_router_partial_policy_confirmation"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_ton_router_partial_policy_confirmation"
MANIFEST="$PROJECT_ROOT/results/strict_v4_ton_router_partial_policy_development/candidate_manifest.json"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4_ton_router_partial_policy_confirmation/cic_ton_iot/stratified"
POLICY_NAME="strict_v4_confirmation_current_policy_v1"

verify_sha() {
  local expected="$1" path="$2" actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' "$path" "$expected" "$actual" >&2
    exit 1
  }
}

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$TON_CACHE"
verify_sha "483698a309206b570e11708e72fe1005922e3ff6961a6015ef3a44e6abb0f81d" train_hybrid_open_set.py
verify_sha "d3d85d6df41601a6ba1820ae763525b24f34c4d98e9fdba866609b6ec3df4155" run_nested_gate_matrix.py
verify_sha "1cbbcb89fca8b10984a42460f09232d43bdfc06489af9a4df52b3d6e098652e0" prepare_stratified_cache.py
verify_sha "d9c424f30a70da77f3bc2fb5018eb945da357496a3719a498381d27a90935cb4" analyze_strict_v4_validation_router_v2.py
verify_sha "3aab0f35b6dc7e6a4c889e73d8f4bf8d08c2729129a48800537b43c3dccd2cc7" confirm_strict_v4_ton_router_policy.py
verify_sha "c4bee48d53cebcabffa54d87d2f4c014783b363bd613b45fa80122e7207ffe4e" "$MANIFEST"

for seed in $SEEDS_SPACE; do
  output="$TON_CACHE/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$output" ]]; then
    "$PYTHON" prepare_stratified_cache.py --csv "$TON_SOURCE" \
      --config configs/cic_ton_iot_strict.json --max-per-class "$MAX_PER_CLASS" \
      --chunksize 50000 --seed "$seed" --output "$output"
  fi
done > "$RESULT_ROOT/cache_preparation.log" 2>&1

"$PYTHON" run_nested_gate_matrix.py --suite cic_ton_iot \
  --scenarios backdoor,ddos,dos,injection,mitm,password,ransomware,scanning,xss \
  --seeds "$SEEDS_COMMA" --workers 1 --model-jobs 8 --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union --risk-policy-name "$POLICY_NAME" \
  --cic-ton-iot-max-per-class "$MAX_PER_CLASS" --cic-ton-iot-cache-dir "$TON_CACHE" \
  --output-root "$RUN_ROOT" > "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" confirm_strict_v4_ton_router_policy.py --root "$RUN_ROOT" \
  --manifest "$MANIFEST" --router-implementation analyze_strict_v4_validation_router_v2.py \
  --output-dir "$RESULT_ROOT" >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["validation"]["run_count"] == 18; assert p["validation"]["scenario_count"] == 9; assert p["validation"]["seeds"] == [67,71]; assert isinstance(p["decision"]["passes"], bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
