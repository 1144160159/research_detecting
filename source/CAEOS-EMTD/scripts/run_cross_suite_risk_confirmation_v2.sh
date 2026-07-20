#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SEEDS_COMMA="103,107,109,113"
SEEDS_SPACE="103 107 109 113"
RUN_ROOT="$PROJECT_ROOT/runs/cross_suite_risk_confirmation_v2/reference"
RESULT_ROOT="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation_v2"
MANIFEST="$PROJECT_ROOT/results/cross_suite_fixed_risk_screen_v2/candidate_manifest.json"
REFERENCE_POLICY='frozen_suite_conditional_density_v1[suites=edge_iiot;fallback=nested_hierarchical_joint_gate;weight=0.3;minimum_gain=0.02;minimum_known_classes=8]'

verify_sha() {
  local expected="$1" path="$2" actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
verify_sha "d3d85d6df41601a6ba1820ae763525b24f34c4d98e9fdba866609b6ec3df4155" run_nested_gate_matrix.py
verify_sha "483698a309206b570e11708e72fe1005922e3ff6961a6015ef3a44e6abb0f81d" train_hybrid_open_set.py
verify_sha "01545b3bf850b656a7473f9f5ec1e3d9433b23f44d44a47eef9cc79888fece9c" confirm_cross_suite_fixed_reports.py
verify_sha "92dd1c3e6d0c7ceaf0c9e633d7ce59600d07b24461d2052a53504c24583c0c7a" confirm_cross_suite_fixed_risk.py
verify_sha "3294b3dd90e9a1afb4a9e1c0f026b2657802370a4069b4ada56e1cae5bc4e4b3" scripts/prepare_cross_suite_risk_confirmation_caches.sh
verify_sha "1cbbcb89fca8b10984a42460f09232d43bdfc06489af9a4df52b3d6e098652e0" prepare_stratified_cache.py

SEEDS="$SEEDS_SPACE" bash scripts/prepare_cross_suite_risk_confirmation_caches.sh \
  > "$RESULT_ROOT/cache_preparation.log" 2>&1

NF_CACHE="$PROJECT_ROOT/caches/cross_suite_risk_confirmation/nf_cse/stratified"
USTC_CACHE="$PROJECT_ROOT/caches/cross_suite_risk_confirmation/ustc_tfc2016/stratified"
"$PYTHON" run_nested_gate_matrix.py \
  --suite nf_cse --seeds "$SEEDS_COMMA" --workers 2 --model-jobs 8 \
  --estimators 80 --risk-selection nested_hierarchical_joint_gate \
  --risk-policy-name "$REFERENCE_POLICY" --joint-fallback-minimum-gain 0.055 \
  --nf-cse-cache-dir "$NF_CACHE" --output-root "$RUN_ROOT" \
  > "$RESULT_ROOT/reference.log" 2>&1
"$PYTHON" run_nested_gate_matrix.py \
  --suite ustc_tfc2016 --seeds "$SEEDS_COMMA" --workers 2 --model-jobs 8 \
  --estimators 80 --risk-selection nested_hierarchical_joint_gate \
  --risk-policy-name "$REFERENCE_POLICY" --joint-fallback-minimum-gain 0.055 \
  --ustc-cache-dir "$USTC_CACHE" --output-root "$RUN_ROOT" \
  >> "$RESULT_ROOT/reference.log" 2>&1

"$PYTHON" confirm_cross_suite_fixed_reports.py \
  --root "$RUN_ROOT" \
  --selection-manifest "$MANIFEST" \
  --reference-risk-policy "$REFERENCE_POLICY" \
  --expected-scenarios 24 \
  --output-dir "$RESULT_ROOT" >> "$RESULT_ROOT/reference.log" 2>&1
"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["validation"]["paired_tasks"] == 96; assert p["validation"]["expected_seeds"] == [103,107,109,113]; assert isinstance(p["frozen_confirmation_decision"]["passes"], bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
