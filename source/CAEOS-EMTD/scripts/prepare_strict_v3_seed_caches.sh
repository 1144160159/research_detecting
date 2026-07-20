#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SEEDS="${SEEDS:-7 11 19 23 37}"
MAX_PER_CLASS="${MAX_PER_CLASS:-5000}"

NF_UNSW_SOURCE="${NF_UNSW_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/NF-UNSW-NB15-v2.csv}"
CICIDS_SOURCE="${CICIDS_SOURCE:-$PROJECT_ROOT/caches/strict_v3/cicids2017/source/cicids2017_strict.csv}"

prepare_one() {
  local suite="$1"
  local source="$2"
  local config="$3"
  local seed="$4"
  local output_dir="$PROJECT_ROOT/caches/strict_v3/$suite/stratified"
  local output="$output_dir/seed${seed}_max${MAX_PER_CLASS}.csv"
  local sidecar="${output}.json"
  local log="$output_dir/seed${seed}.log"
  mkdir -p "$output_dir"
  if [[ -s "$output" && -s "$sidecar" ]]; then
    printf '%s skip %s seed=%s existing cache and sidecar\n' \
      "$(date -Is)" "$suite" "$seed"
    return
  fi
  printf '%s prepare %s seed=%s\n' "$(date -Is)" "$suite" "$seed"
  ionice -c3 nice -n 19 "$PYTHON" "$PROJECT_ROOT/prepare_stratified_cache.py" \
    --csv "$source" \
    --config "$PROJECT_ROOT/$config" \
    --max-per-class "$MAX_PER_CLASS" \
    --chunksize 50000 \
    --seed "$seed" \
    --output "$output" \
    > "$log" 2>&1
  test -s "$output"
  test -s "$sidecar"
}

for seed in $SEEDS; do
  prepare_one "nf_unsw" "$NF_UNSW_SOURCE" "configs/nf_unsw_nb15.json" "$seed"
done

for seed in $SEEDS; do
  prepare_one "cicids2017" "$CICIDS_SOURCE" "configs/cicids2017_strict.json" "$seed"
done

printf '%s strict-v3 caches complete\n' "$(date -Is)"
