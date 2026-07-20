#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SEEDS="${SEEDS:-83 89 97 101}"
NF_SOURCE="${NF_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/NF-CSE-CIC-IDS2018-v2.csv}"
USTC_SOURCE="${USTC_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/ustc_tfc2016/ustc_tfc2016_nfstream.csv}"

prepare_one() {
  local suite="$1" source="$2" config="$3" seed="$4" maximum="$5"
  local output_dir="$PROJECT_ROOT/caches/cross_suite_risk_confirmation/$suite/stratified"
  local output="$output_dir/seed${seed}_max${maximum}.csv"
  mkdir -p "$output_dir"
  if [[ -s "$output" && -s "${output}.json" ]]; then
    printf '%s skip %s seed=%s\n' "$(date -Is)" "$suite" "$seed"
    return
  fi
  printf '%s prepare %s seed=%s\n' "$(date -Is)" "$suite" "$seed"
  ionice -c3 nice -n 19 "$PYTHON" "$PROJECT_ROOT/prepare_stratified_cache.py" \
    --csv "$source" --config "$PROJECT_ROOT/$config" --max-per-class "$maximum" \
    --chunksize 50000 --seed "$seed" --output "$output" \
    > "$output_dir/seed${seed}.log" 2>&1
  test -s "$output"
  test -s "${output}.json"
}

for seed in $SEEDS; do
  prepare_one nf_cse "$NF_SOURCE" configs/nf_cse_cic_ids2018_v2.json "$seed" 1000
  prepare_one ustc_tfc2016 "$USTC_SOURCE" configs/ustc_tfc2016_nfstream.json "$seed" 3000
done
