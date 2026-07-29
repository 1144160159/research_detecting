#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CACHE_ROOT="$PROJECT_ROOT/caches/strict_v4_final_efficiency_seed191"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_seed191_cache"
READINESS_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_cache_readiness"
EXTERNAL_MARKER="$PROJECT_ROOT/results/strict_v4_external_confirmation/confirmation_complete"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
LOCK_DIR="$RESULT_ROOT/prepare.lock.d"
SEED=191

EDGE_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/Edge-IIoTset dataset/Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv"
NF_CSE_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/NF-CSE-CIC-IDS2018-v2.csv"
USTC_SOURCE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/ustc_tfc2016/ustc_tfc2016_nfstream.csv"
NF_UNSW_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/NF-UNSW-NB15-v2.csv"
CICIDS_SOURCE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v3/cicids2017/source/cicids2017_strict.csv"
TON_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
CICIOT_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV"

test -f "$EXTERNAL_MARKER" || {
  echo "external comparator confirmation is incomplete" >&2
  exit 3
}
test -s "$COVERAGE"
mkdir -p "$RESULT_ROOT" "$CACHE_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "seed191 cache preparation already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

prepare_one() {
  local suite="$1" source="$2" config="$3" maximum="$4"
  local output_dir="$CACHE_ROOT/$suite"
  local output="$output_dir/seed${SEED}_max${maximum}.csv"
  mkdir -p "$output_dir"
  if [[ -s "$output" && -s "$output.json" ]]; then
    return
  fi
  ionice -c3 nice -n 19 "$PYTHON" prepare_stratified_cache.py \
    --csv "$source" --config "$config" --max-per-class "$maximum" \
    --chunksize 50000 --seed "$SEED" --output "$output" \
    > "$output_dir/seed${SEED}.log" 2>&1
  test -s "$output"
  test -s "$output.json"
}

cd "$PROJECT_ROOT"
prepare_one edge_iiot "$EDGE_SOURCE" configs/edge_iiot.json 1000
prepare_one nf_cse "$NF_CSE_SOURCE" configs/nf_cse_cic_ids2018_v2.json 1000
prepare_one ustc_tfc2016 "$USTC_SOURCE" configs/ustc_tfc2016_nfstream.json 3000
prepare_one nf_unsw "$NF_UNSW_SOURCE" configs/nf_unsw_nb15.json 5000
prepare_one cicids2017 "$CICIDS_SOURCE" configs/cicids2017_strict.json 5000
prepare_one cic_ton_iot "$TON_SOURCE" configs/cic_ton_iot_strict.json 1000

raw="$CACHE_ROOT/cic_iot2023_raw/seed${SEED}_max1000.csv"
grouped="$CACHE_ROOT/cic_iot2023/seed${SEED}_max1000.csv"
mkdir -p "$(dirname "$raw")" "$(dirname "$grouped")"
if [[ ! -s "$raw" || ! -s "$raw.json" ]]; then
  ionice -c3 nice -n 19 "$PYTHON" prepare_cic_iot2023_strict.py \
    --input-dir "$CICIOT_SOURCE" --output "$raw" --seed "$SEED" \
    --max-per-class 1000 --group-rows 1000 --expected-source-files 309 \
    > "$CACHE_ROOT/cic_iot2023_raw/seed${SEED}.log" 2>&1
fi
if [[ ! -s "$grouped" || ! -s "$grouped.json" ]]; then
  "$PYTHON" prepare_group_supported_cache.py \
    --input "$raw" --output "$grouped" --label-column Attack \
    --group-column CaptureGroup --minimum-groups 3 \
    > "$CACHE_ROOT/cic_iot2023/seed${SEED}.log" 2>&1
fi
test -s "$grouped"
test -s "$grouped.json"

find "$CACHE_ROOT" \( -name 'seed191_max*.csv' -o -name 'seed191_max*.csv.json' \) \
  -type f -print0 | sort -z | xargs -0 sha256sum > "$RESULT_ROOT/cache_sha256.txt"
"$PYTHON" audit_strict_v4_final_efficiency_cache_readiness.py \
  --coverage "$COVERAGE" --search-root "$CACHE_ROOT" \
  --output-dir "$READINESS_ROOT" > "$RESULT_ROOT/readiness.log" 2>&1
"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["gates"]["formal_timing_allowed"] is True' \
  "$READINESS_ROOT/cache_readiness.json"
touch "$RESULT_ROOT/caches_complete"
