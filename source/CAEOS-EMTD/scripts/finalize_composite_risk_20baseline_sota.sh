#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
EDGE_ROOT="${EDGE_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
SOURCE_GATE="${SOURCE_GATE:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-formal-20260716/runs/strict_v2_caeos_confirmed_policy_5seed}"
STRONG="${STRONG:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/runs/strict_v2_strong_baselines_5seed}"
MODERN="${MODERN:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_modern_baselines_5seed}"
LEGACY="${LEGACY:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_legacy_baselines_5seed}"
EDGE_SELECTION="${EDGE_SELECTION:-$EDGE_ROOT/results/final_internal_risk_selection/selection.json}"
CROSS_CONFIRMATION="${CROSS_CONFIRMATION:-$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation/confirmation.json}"
CROSS_MANIFEST="${CROSS_MANIFEST:-$PROJECT_ROOT/results/cross_suite_fixed_risk_screen/candidate_manifest.json}"
SELECTION="${SELECTION:-$PROJECT_ROOT/results/final_composite_risk_selection/selection.json}"
GATE="${GATE:-$PROJECT_ROOT/runs/final_composite_risk_gate_5seed}"
OUTPUT="${OUTPUT:-$PROJECT_ROOT/results/final_composite_risk_20baseline_sota}"
POLICY="${POLICY:-final_composite_risk_v1}"

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
mkdir -p "$OUTPUT" "$(dirname "$SELECTION")"
verify_sha "30f87349d854ace4f4151ac415109e622247ec2db40a87e968fad26a2b6187e9" select_final_composite_risk.py
verify_sha "6bc3a6e0835f9ce67b60f7959f74139f5468eb4195046f40951daf01d07ac038" materialize_final_composite_gate.py
verify_sha "37c074b4ca2e03f118a936000b58ac8a34375d5c34b8c3c6d2896e6b2352e2c9" audit_strict_v2_sota.py
verify_sha "3fe53a0c211250b505f8a8db0e31a927607f51c7543146481842cbc28ec44bc7" summarize_neural_comparison_strict_v2.py
verify_sha "96b96f376001b4c7f7f55977ac43cf82030beb7934376452e041393c37d3fad2" summarize_sota_decision.py

"$PYTHON" select_final_composite_risk.py \
  --edge-selection "$EDGE_SELECTION" \
  --cross-suite-confirmation "$CROSS_CONFIRMATION" \
  --cross-suite-manifest "$CROSS_MANIFEST" \
  --output "$SELECTION" \
  --markdown-output "${SELECTION%.json}.md" \
  > "$OUTPUT/selection.log" 2>&1

"$PYTHON" materialize_final_composite_gate.py \
  --source-root "$SOURCE_GATE" \
  --selection "$SELECTION" \
  --output-root "$GATE" \
  --known-acceptance 0.95 \
  > "$OUTPUT/materialization.log" 2>&1
touch "$OUTPUT/materialization_complete"

"$PYTHON" audit_strict_v2_sota.py \
  --gate-root "$GATE" \
  --baseline-root "strong=$STRONG" \
  --baseline-root "modern=$MODERN" \
  --baseline-root "legacy=$LEGACY" \
  --expected-models strong=opendetect,sieve \
  --expected-models modern=mlp,palm \
  --expected-models legacy=arpl,closr,cade,ronetc,foss \
  --seeds 7,11,19,23,37 \
  --output "$OUTPUT/audit.json"

comparison_args=(
  --gate-root "$GATE"
  --gate-policy-name "$POLICY"
  --neural-root "edge_iiot=$STRONG/edge_iiot"
  --neural-root "edge_iiot=$MODERN/edge_iiot"
  --neural-root "edge_iiot=$LEGACY/edge_iiot"
  --neural-root "nf_cse=$STRONG/nf_cse"
  --neural-root "nf_cse=$MODERN/nf_cse"
  --neural-root "nf_cse=$LEGACY/nf_cse"
  --neural-root "ustc_tfc2016=$STRONG/ustc_tfc2016"
  --neural-root "ustc_tfc2016=$MODERN/ustc_tfc2016"
  --neural-root "ustc_tfc2016=$LEGACY/ustc_tfc2016"
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
  'import json,sys; from pathlib import Path; out=Path(sys.argv[1]); gate=json.load(open(sys.argv[2])); selection=json.load(open(sys.argv[3])); audit=json.load(open(out/"audit.json")); comp=json.load(open(out/"comparison_strict_v2.json")); decision=json.load(open(out/"sota_decision.json")); assert gate["state"] == "complete"; assert gate["number_of_experiments"] == 190; assert gate["suite_risks"] == selection["suite_risks"]; assert audit["state"] == "complete"; assert comp["global"]["run_count"] == 190; assert comp["global"]["scenario_inference_units"] == 38; assert len(comp["global"]["methods"]) == 20; assert comp["global"]["holm_hypotheses"] == 100; assert decision["global"]["baseline_method_count"] == 20; assert decision["claim_gate"]["suite_count"] == 3; assert isinstance(decision["claim_gate"]["full_sota_claim_allowed"], bool)' \
  "$OUTPUT" "$GATE/manifest.json" "$SELECTION"
touch "$OUTPUT/finalization_complete"
