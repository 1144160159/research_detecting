#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-formal-20260716}"
REFERENCE_ROOT="${REFERENCE_ROOT:-$PROJECT_ROOT/references/frozen_policy_edge_5seed}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"

cd "$PROJECT_ROOT"
"$CONDA" run -n py3.9 python summarize_paired_confirmation.py \
  --reference-root "$REFERENCE_ROOT" \
  --candidate-root runs/strict_v2_caeos_modality_union_edge_5seed \
  --output-dir results/strict_v2_caeos_modality_union_edge_5seed_vs_frozen \
  --seeds 7,11,19,23,37 \
  --expected-scenarios 14 \
  --candidate-risk-policy confirmed_cauchy_modality_union_v1_edge \
  --reference-risk-policy 'frozen_suite_conditional_density_v1[suites=edge_iiot;fallback=nested_hierarchical_joint_gate;weight=0.3;minimum_gain=0.02;minimum_known_classes=8]' \
  --bootstrap-repetitions 10000 \
  --bootstrap-seed 20260716
