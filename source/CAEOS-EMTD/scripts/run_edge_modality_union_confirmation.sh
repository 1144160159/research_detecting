#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-dev-20260716}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CACHE_DIR="${CACHE_DIR:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot}"

cd "$PROJECT_ROOT"
mkdir -p results/confirmation_logs
printf '%s\n' "$$" > results/confirmation_logs/edge_modality_union_confirmation.pid

COMMON_ARGS=(
  --suite edge_iiot
  --seeds 29,31,41,43
  --scenarios all
  --workers 1
  --model-jobs 8
  --estimators 80
  --density-gate-minimum-gain 0.02
  --density-gate-minimum-known-classes 8
  --density-gate-blend-weight 0.3
  --edge-iiot-cache-dir "$CACHE_DIR"
)

"$CONDA" run -n py3.9 python run_nested_gate_matrix.py \
  "${COMMON_ARGS[@]}" \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name frozen_cauchy_modality_union_v1_edge_devseed7 \
  --output-root runs/cauchy_modality_union_confirmation_new_seeds_edge_v1

"$CONDA" run -n py3.9 python run_nested_gate_matrix.py \
  "${COMMON_ARGS[@]}" \
  --risk-selection nested_density_reliability_gate \
  --density-gate-supported-suites edge_iiot \
  --density-gate-fallback-risk-selection nested_hierarchical_joint_gate \
  --risk-policy-name frozen_suite_conditional_density_v1_edge \
  --output-root runs/frozen_density_confirmation_new_seeds_edge_v1
