#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
DATASET_ROOT="${DATASET_ROOT:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/DoHBrw2020}"
PREREQUISITE="${PREREQUISITE:-$PROJECT_ROOT/runs/strict_v4_wdiscood_pilot_seed7/pilot_complete}"
RESULT_ROOT="$PROJECT_ROOT/results/doh_temporal_external"
RUN_ROOT="$PROJECT_ROOT/runs/doh_temporal_external"
CACHE_ROOT="$PROJECT_ROOT/caches/doh_temporal_external"
CSV="$CACHE_ROOT/doh_all_timed.csv"
METADATA="$CACHE_ROOT/preparation.json"
PROTOCOL="$RESULT_ROOT/protocol.json"

while [[ ! -f "$PREREQUISITE" ]]; do sleep 300; done
cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$RUN_ROOT" "$CACHE_ROOT"

if [[ ! -f "$PROTOCOL" ]]; then
  "$PYTHON" create_doh_temporal_external_protocol.py \
    --project-root "$PROJECT_ROOT" --dataset-root "$DATASET_ROOT" --output "$PROTOCOL"
fi
if [[ ! -s "$CSV" ]]; then
  "$PYTHON" prepare_dohbrw2020.py \
    --root "$DATASET_ROOT" --output "$CSV" --metadata "$METADATA" \
    --selection all --require-capture-time --rows-per-capture 200 --seed 7
fi

for seed in 223 227 229; do
  pairwise="$RUN_ROOT/seed${seed}_pairwise"
  if [[ ! -f "$pairwise/metrics.json" ]]; then
    "$PYTHON" train_hybrid_open_set.py \
      --csv "$CSV" --config configs/dohbrw2020_temporal_multiclass.json \
      --unknown-classes dns2tcp --benign-class benign \
      --split-strategy temporal_capture_grouped --max-per-class 4000 \
      --estimators 80 --jobs 8 --known-acceptance 0.95 --seed "$seed" \
      --risk-selection nested_boundary_pairwise_pseudo_unknown_blend \
      --pseudo-unknown-max-alpha 0.5 --pseudo-unknown-min-fold-gain -0.05 \
      --boundary-hard-pseudo-fraction 0.5 --boundary-interpolation 0.5 \
      --boundary-max-per-task 512 --boundary-training-objective pairwise \
      --risk-policy-name doh_temporal_external_pairwise_v1 --output-dir "$pairwise"
  fi
  comparator="$RUN_ROOT/seed${seed}_opendetect"
  if [[ ! -f "$comparator/metrics.json" ]]; then
    "$PYTHON" train_neural_open_set.py \
      --dataset tabular --csv "$CSV" \
      --config configs/dohbrw2020_temporal_multiclass.json \
      --unknown-classes dns2tcp --benign-class benign \
      --split-strategy temporal_capture_grouped --max-per-class 4000 \
      --model opendetect --epochs 100 --patience 100 --hidden-dim 128 \
      --embedding-dim 64 --known-acceptance 0.95 --seed "$seed" \
      --device auto --output-dir "$comparator"
  fi
done > "$RESULT_ROOT/execution.log" 2>&1

"$PYTHON" summarize_doh_temporal_external.py \
  --protocol "$PROTOCOL" --run-root "$RUN_ROOT" --output "$RESULT_ROOT/summary.json" \
  > "$RESULT_ROOT/summary.log" 2>&1
touch "$RESULT_ROOT/execution_complete"
