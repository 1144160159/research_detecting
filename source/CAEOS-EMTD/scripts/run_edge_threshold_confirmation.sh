#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-threshold-confirm-20260716}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CACHE_DIR="${CACHE_DIR:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot}"

cd "$PROJECT_ROOT"
mkdir -p results/threshold_confirmation_logs
printf '%s\n' "$$" > results/threshold_confirmation_logs/edge_threshold_confirmation.pid

"$CONDA" run -n py3.9 python run_nested_gate_matrix.py \
  --suite edge_iiot \
  --seeds 47,53,59,61 \
  --scenarios all \
  --workers 2 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name threshold_confirmation_cauchy_modality_union_v1_target0975 \
  --density-gate-minimum-gain 0.02 \
  --density-gate-minimum-known-classes 8 \
  --density-gate-blend-weight 0.3 \
  --edge-iiot-cache-dir "$CACHE_DIR" \
  --output-root runs/cauchy_modality_union_threshold_confirmation_new_seeds
