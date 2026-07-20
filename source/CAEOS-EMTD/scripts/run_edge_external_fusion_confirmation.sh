#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CACHE_DIR="${CACHE_DIR:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot}"
SELECTION="${SELECTION:-selection/external_fusion_selection_manifest.json}"
EXPECTED_SELECTION_SHA="69f219a86cce6b4eb74fb842aa283deff1e48d66dc78645782f0d4fdcf98cf7d"

cd "$PROJECT_ROOT"
actual_sha="$(sha256sum "$SELECTION" | awk '{print $1}')"
[[ "$actual_sha" == "$EXPECTED_SELECTION_SHA" ]] || {
  printf 'selection manifest SHA mismatch: expected=%s actual=%s\n' \
    "$EXPECTED_SELECTION_SHA" "$actual_sha" >&2
  exit 1
}

bash scripts/prepare_edge_external_fusion_confirmation_caches.sh

"$CONDA" run -n py3.9 python run_nested_gate_matrix.py \
  --suite edge_iiot \
  --seeds 67,71,73,79 \
  --scenarios all \
  --workers 1 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name confirmed_cauchy_modality_union_v1_edge_external_fusion_holdout \
  --density-gate-minimum-gain 0.02 \
  --density-gate-minimum-known-classes 8 \
  --density-gate-blend-weight 0.3 \
  --edge-iiot-cache-dir "$CACHE_DIR" \
  --output-root runs/external_fusion_confirmation_caeos

"$CONDA" run -n py3.9 python run_neural_baseline_matrix.py \
  --suite edge_iiot \
  --scenarios all \
  --models mlp \
  --seeds 67,71,73,79 \
  --workers 1 \
  --epochs 0 \
  --patience 10 \
  --edge-iiot-cache-dir "$CACHE_DIR" \
  --edge-iiot-max-per-class 1000 \
  --output-root runs/external_fusion_confirmation_mlp

mkdir -p results/external_fusion_confirmation
"$CONDA" run -n py3.9 python analyze_caeos_closr_fusion.py \
  --gate-root runs/external_fusion_confirmation_caeos \
  --expert-root runs/external_fusion_confirmation_mlp \
  --expert-name relative_mahalanobis \
  --expert-model mlp \
  --seeds 67,71,73,79 \
  --suites edge_iiot \
  --output results/external_fusion_confirmation/raw_confirmation.json

"$CONDA" run -n py3.9 python confirm_external_fusion_candidate.py \
  --selection-manifest "$SELECTION" \
  --raw-confirmation results/external_fusion_confirmation/raw_confirmation.json \
  --output results/external_fusion_confirmation/confirmation.json \
  --bootstrap-repetitions 10000 \
  --bootstrap-seed 20260717
