#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CROSS_MARKER="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation_v2/confirmation.json"
STRICT_V3_MARKER="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/results/strict_v3_pilot/summary.json"
MANIFEST="$PROJECT_ROOT/results/gpu_candidate_dataset_inventory_20260717/strict_v4_candidate_manifest.json"
OUTPUT="$PROJECT_ROOT/results/strict_v4_pilot"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
TON_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
TON_CACHE_DIR="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
TON_CACHE="$TON_CACHE_DIR/seed7_max1000.csv"
CIC_SOURCE_CACHE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717/caches/strict_v4/cic_iot2023/stratified"
CIC_SOURCE_CACHE="$CIC_SOURCE_CACHE_DIR/seed7_max1000.csv"
CIC_CACHE_DIR="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"
CIC_CACHE="$CIC_CACHE_DIR/seed7_max1000.csv"
POLICY="strict_v4_pilot_fixed_cauchy_modality_union_v1"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another strict-v4 pilot waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

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
verify_sha 39f8c4801420aa7c9501f1065710ec07c10560117f12bb5bcec8541d2b6cc945 "$MANIFEST"
verify_sha 1cbbcb89fca8b10984a42460f09232d43bdfc06489af9a4df52b3d6e098652e0 prepare_stratified_cache.py
verify_sha 3a607c09a30644bdd622858ec32e599e7ae6589fecee4d0a45bbd0e850a30e38 audit_tabular_config_schema.py
verify_sha 5d027b18ce591f89d9a2de405acdad7b2250bd75c9e5829566fd2a4293c94a07 prepare_group_supported_cache.py
verify_sha d3d85d6df41601a6ba1820ae763525b24f34c4d98e9fdba866609b6ec3df4155 run_nested_gate_matrix.py
verify_sha f75c67109f75755e549e2cfcf7407c3496c8b56280a3abb181baea4d128175ec run_neural_baseline_matrix.py
verify_sha 483698a309206b570e11708e72fe1005922e3ff6961a6015ef3a44e6abb0f81d train_hybrid_open_set.py
verify_sha 93818c76867cff89750c5cb59f0760177d3243b450618411af273259772f821d configs/cic_ton_iot_strict.json
verify_sha 2c7e8dbd4f1d6c399c913b884b0ae7f4743fc7521e011df4b9ae27e8c3441cdb configs/cic_iot2023_strict.json

while [[ ! -f "$CROSS_MARKER" || ! -f "$STRICT_V3_MARKER" ]]; do
  cross=0
  strict_v3=0
  [[ -f "$CROSS_MARKER" ]] && cross=1
  [[ -f "$STRICT_V3_MARKER" ]] && strict_v3=1
  printf '%s waiting cross_suite=%s strict_v3=%s\n' \
    "$(date -Is)" "$cross" "$strict_v3" >> "$LOG"
  sleep 300
done

printf '%s building strict ToN-IoT cache\n' "$(date -Is)" >> "$LOG"
mkdir -p "$TON_CACHE_DIR"
if [[ ! -s "$TON_CACHE" || ! -s "${TON_CACHE}.json" ]]; then
  ionice -c3 nice -n 19 "$PYTHON" prepare_stratified_cache.py \
    --csv "$TON_SOURCE" \
    --config configs/cic_ton_iot_strict.json \
    --max-per-class 1000 \
    --chunksize 50000 \
    --seed 7 \
    --output "$TON_CACHE" \
    > "$TON_CACHE_DIR/seed7.log" 2>&1
fi
test -s "$TON_CACHE"
test -s "${TON_CACHE}.json"
test -s "$CIC_SOURCE_CACHE"
test -s "${CIC_SOURCE_CACHE}.json"
printf '%s deriving group-supported CICIoT2023 cache\n' "$(date -Is)" >> "$LOG"
mkdir -p "$CIC_CACHE_DIR"
if [[ ! -s "$CIC_CACHE" || ! -s "${CIC_CACHE}.json" ]]; then
  "$PYTHON" prepare_group_supported_cache.py \
    --input "$CIC_SOURCE_CACHE" \
    --output "$CIC_CACHE" \
    --label-column Attack \
    --group-column CaptureGroup \
    --minimum-groups 3 \
    > "$CIC_CACHE_DIR/seed7.log" 2>&1
fi
test -s "$CIC_CACHE"
test -s "${CIC_CACHE}.json"

printf '%s starting strict-v4 CAEOS pilot\n' "$(date -Is)" >> "$LOG"
"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_ton_iot --scenarios xss,scanning,ransomware --seeds 7 \
  --workers 1 --model-jobs 8 --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name "$POLICY" \
  --cic-ton-iot-cache-dir "$TON_CACHE_DIR" --cic-ton-iot-max-per-class 1000 \
  --output-root runs/strict_v4_pilot_caeos >> "$LOG" 2>&1
"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 \
  --scenarios ddos_icmp_flood,mirai_udpplain,command_injection --seeds 7 \
  --workers 1 --model-jobs 8 --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name "$POLICY" \
  --cic-iot2023-cache-dir "$CIC_CACHE_DIR" --cic-iot2023-max-per-class 1000 \
  --output-root runs/strict_v4_pilot_caeos >> "$LOG" 2>&1

printf '%s starting strict-v4 neural pilot\n' "$(date -Is)" >> "$LOG"
"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_ton_iot --scenarios xss,scanning,ransomware \
  --models mlp,opendetect,ronetc --seeds 7 --workers 1 \
  --epochs 0 --patience 10 \
  --cic-ton-iot-cache-dir "$TON_CACHE_DIR" --cic-ton-iot-max-per-class 1000 \
  --output-root runs/strict_v4_pilot_neural >> "$LOG" 2>&1
"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_iot2023 \
  --scenarios ddos_icmp_flood,mirai_udpplain,command_injection \
  --models mlp,opendetect,ronetc --seeds 7 --workers 1 \
  --epochs 0 --patience 10 \
  --cic-iot2023-cache-dir "$CIC_CACHE_DIR" --cic-iot2023-max-per-class 1000 \
  --output-root runs/strict_v4_pilot_neural >> "$LOG" 2>&1

caeos_count="$(find runs/strict_v4_pilot_caeos -name metrics.json | wc -l)"
neural_count="$(find runs/strict_v4_pilot_neural -name metrics.json | wc -l)"
failures="$(find runs/strict_v4_pilot_caeos runs/strict_v4_pilot_neural -name failure.json | wc -l)"
printf '%s strict-v4 pilot complete caeos=%s/6 neural=%s/18 failures=%s\n' \
  "$(date -Is)" "$caeos_count" "$neural_count" "$failures" >> "$LOG"
[[ "$caeos_count" -eq 6 && "$neural_count" -eq 18 && "$failures" -eq 0 ]]
touch "$OUTPUT/training_complete"
