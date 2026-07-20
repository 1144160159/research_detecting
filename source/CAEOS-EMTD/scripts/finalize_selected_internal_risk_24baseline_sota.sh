#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717}"
SELECTED_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
GATE="$SELECTED_ROOT/runs/final_selected_internal_risk_gate_5seed"
SELECTION="$SELECTED_ROOT/results/final_internal_risk_selection/selection.json"
STRONG="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/runs/strict_v2_strong_baselines_5seed"
MODERN="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_modern_baselines_5seed"
LEGACY="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_legacy_baselines_5seed"
CLASSICAL="$PROJECT_ROOT/runs/strict_v2_classical_ood_5seed"
MANIFEST="$PROJECT_ROOT/selection/strict_v2_classical_ood_manifest.json"
OUTPUT="$PROJECT_ROOT/results/final_selected_internal_risk_24baseline_sota"
POLICY="final_selected_internal_risk_composite_v1"

verify_sha() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

cd "$PROJECT_ROOT"
mkdir -p "$OUTPUT"
verify_sha "6c12df4c339130676f22589f5f73f9c4467613300d3e10cef61d1fd21473a80e" "$MANIFEST"
verify_sha "c0248468c8ef79878e069e9ca421ab55eff33317b8a8f391971a491d040bd64a" audit_classical_ood_reports.py
verify_sha "37c074b4ca2e03f118a936000b58ac8a34375d5c34b8c3c6d2896e6b2352e2c9" audit_strict_v2_sota.py
verify_sha "3fe53a0c211250b505f8a8db0e31a927607f51c7543146481842cbc28ec44bc7" summarize_neural_comparison_strict_v2.py
verify_sha "96b96f376001b4c7f7f55977ac43cf82030beb7934376452e041393c37d3fad2" summarize_sota_decision.py

"$PYTHON" audit_classical_ood_reports.py \
  --root "$CLASSICAL" \
  --expected-runs 190 \
  --output "$OUTPUT/classical_report_audit.json"
"$PYTHON" audit_strict_v2_sota.py \
  --gate-root "$GATE" \
  --baseline-root "strong=$STRONG" \
  --baseline-root "modern=$MODERN" \
  --baseline-root "legacy=$LEGACY" \
  --baseline-root "classical=$CLASSICAL" \
  --expected-models strong=opendetect,sieve \
  --expected-models modern=mlp,palm \
  --expected-models legacy=arpl,closr,cade,ronetc,foss \
  --expected-models classical=classical_ood \
  --seeds 7,11,19,23,37 \
  --output "$OUTPUT/audit.json"

comparison_args=(
  --gate-root "$GATE"
  --gate-policy-name "$POLICY"
  --neural-root "edge_iiot=$STRONG/edge_iiot"
  --neural-root "edge_iiot=$MODERN/edge_iiot"
  --neural-root "edge_iiot=$LEGACY/edge_iiot"
  --neural-root "edge_iiot=$CLASSICAL/edge_iiot"
  --neural-root "nf_cse=$STRONG/nf_cse"
  --neural-root "nf_cse=$MODERN/nf_cse"
  --neural-root "nf_cse=$LEGACY/nf_cse"
  --neural-root "nf_cse=$CLASSICAL/nf_cse"
  --neural-root "ustc_tfc2016=$STRONG/ustc_tfc2016"
  --neural-root "ustc_tfc2016=$MODERN/ustc_tfc2016"
  --neural-root "ustc_tfc2016=$LEGACY/ustc_tfc2016"
  --neural-root "ustc_tfc2016=$CLASSICAL/ustc_tfc2016"
  --output-dir "$OUTPUT"
  --bootstrap-repetitions 10000
  --bootstrap-seed 20260717
)
"$PYTHON" summarize_neural_comparison_strict_v2.py "${comparison_args[@]}"
"$PYTHON" summarize_sota_decision.py \
  --comparison "$OUTPUT/comparison_strict_v2.json" \
  --output "$OUTPUT/sota_decision.json" \
  --markdown-output "$OUTPUT/sota_decision.md"

"$PYTHON" -c \
  'import json,sys; from pathlib import Path; out=Path(sys.argv[1]); gate=json.load(open(sys.argv[2])); selection=json.load(open(sys.argv[3])); classical=json.load(open(out/"classical_report_audit.json")); audit=json.load(open(out/"audit.json")); comp=json.load(open(out/"comparison_strict_v2.json")); decision=json.load(open(out/"sota_decision.json")); required={"isolation_forest","one_class_svm","local_outlier_factor","pca_reconstruction"}; methods=set(comp["global"]["methods"]); assert gate["state"] == "complete"; assert gate["selected_edge_risk"] == selection["selected_internal_risk"]; assert classical["state"] == "complete"; assert classical["expected_method_evaluations"] == 760; assert audit["state"] == "complete"; assert comp["global"]["run_count"] == 190; assert comp["global"]["scenario_inference_units"] == 38; assert len(methods) == 24; assert required <= methods; assert comp["global"]["holm_hypotheses"] == 120; assert decision["global"]["baseline_method_count"] == 24; assert decision["claim_gate"]["suite_count"] == 3; assert isinstance(decision["claim_gate"]["full_sota_claim_allowed"], bool)' \
  "$OUTPUT" "$GATE/manifest.json" "$SELECTION"
touch "$OUTPUT/finalization_complete"
