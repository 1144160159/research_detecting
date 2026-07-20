#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-formal-20260716}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CACHE_DIR="${CACHE_DIR:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot}"
OUTPUT_ROOT="${OUTPUT_ROOT:-runs/strict_v2_caeos_modality_union_edge_5seed}"

cd "$PROJECT_ROOT"
mkdir -p results/formal_logs
printf '%s\n' "$$" > results/formal_logs/edge_modality_union_formal_5seed.pid

"$CONDA" run -n py3.9 python run_nested_gate_matrix.py \
  --suite edge_iiot \
  --seeds 7,11,19,23,37 \
  --scenarios all \
  --workers 2 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name confirmed_cauchy_modality_union_v1_edge \
  --density-gate-minimum-gain 0.02 \
  --density-gate-minimum-known-classes 8 \
  --density-gate-blend-weight 0.3 \
  --edge-iiot-cache-dir "$CACHE_DIR" \
  --output-root "$OUTPUT_ROOT"
