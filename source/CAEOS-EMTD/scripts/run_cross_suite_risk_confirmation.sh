#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SEEDS="${SEEDS:-83,89,97,101}"
WORKERS="${WORKERS:-2}"
MODEL_JOBS="${MODEL_JOBS:-8}"
RUN_ROOT="$PROJECT_ROOT/runs/cross_suite_risk_confirmation"
RESULT_ROOT="$PROJECT_ROOT/results/cross_suite_risk_confirmation"
MANIFEST="$PROJECT_ROOT/results/cross_suite_fixed_risk_screen/candidate_manifest.json"
REFERENCE_POLICY='frozen_suite_conditional_density_v1[suites=edge_iiot;fallback=nested_hierarchical_joint_gate;weight=0.3;minimum_gain=0.02;minimum_known_classes=8]'
CANDIDATE_POLICY='cross_suite_fixed_risk_v1[manifest=68a990fa6e4d2238610d526de56d576717608b1aabb13cb2955aec35f01aa22a]'

bash "$PROJECT_ROOT/scripts/prepare_cross_suite_risk_confirmation_caches.sh"

run_arm() {
  local arm="$1" suite="$2" selection="$3" fixed="$4" policy="$5"
  shift 5
  local extra=()
  if [[ "$selection" == fixed_named ]]; then
    extra=(--fixed-risk-name "$fixed")
  fi
  "$PYTHON" "$PROJECT_ROOT/run_nested_gate_matrix.py" \
    --suite "$suite" --seeds "$SEEDS" --workers "$WORKERS" \
    --model-jobs "$MODEL_JOBS" --estimators 80 \
    --risk-selection "$selection" --risk-policy-name "$policy" \
    --joint-fallback-minimum-gain 0.055 \
    --output-root "$RUN_ROOT/$arm" "$@" "${extra[@]}"
}

NF_CACHE="$PROJECT_ROOT/caches/cross_suite_risk_confirmation/nf_cse/stratified"
USTC_CACHE="$PROJECT_ROOT/caches/cross_suite_risk_confirmation/ustc_tfc2016/stratified"
run_arm reference nf_cse nested_hierarchical_joint_gate '' "$REFERENCE_POLICY" --nf-cse-cache-dir "$NF_CACHE"
run_arm reference ustc_tfc2016 nested_hierarchical_joint_gate '' "$REFERENCE_POLICY" --ustc-cache-dir "$USTC_CACHE"
run_arm candidate nf_cse fixed_named disagreement_augmented "$CANDIDATE_POLICY" --nf-cse-cache-dir "$NF_CACHE"
run_arm candidate ustc_tfc2016 fixed_named cauchy_conflict "$CANDIDATE_POLICY" --ustc-cache-dir "$USTC_CACHE"

"$PYTHON" "$PROJECT_ROOT/confirm_cross_suite_fixed_risk.py" \
  --reference-root "$RUN_ROOT/reference" \
  --candidate-root "$RUN_ROOT/candidate" \
  --selection-manifest "$MANIFEST" \
  --candidate-risk-policy "$CANDIDATE_POLICY" \
  --reference-risk-policy "$REFERENCE_POLICY" \
  --expected-scenarios 24 \
  --output-dir "$RESULT_ROOT"
