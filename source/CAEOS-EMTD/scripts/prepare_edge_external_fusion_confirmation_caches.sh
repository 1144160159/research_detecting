#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CACHE_DIR="${CACHE_DIR:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot}"
SOURCE_CSV="${SOURCE_CSV:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/Edge-IIoTset dataset/Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv}"

cd "$PROJECT_ROOT"
for seed in 67 71 73 79; do
  output="$CACHE_DIR/seed${seed}_max1000.csv"
  metadata="$output.json"
  if [[ -e "$output" || -e "$metadata" ]]; then
    printf 'using existing external-fusion confirmation cache for seed %d\n' "$seed"
    [[ -s "$output" && -s "$metadata" ]]
    continue
  fi
  "$CONDA" run -n py3.9 python prepare_stratified_cache.py \
    --csv "$SOURCE_CSV" \
    --config configs/edge_iiot.json \
    --max-per-class 1000 \
    --chunksize 100000 \
    --seed "$seed" \
    --output "$output"
done
