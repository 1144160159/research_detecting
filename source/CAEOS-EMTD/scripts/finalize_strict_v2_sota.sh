#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
GATE_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-formal-20260716/runs/strict_v2_caeos_confirmed_policy_5seed"
STRONG="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/runs/strict_v2_strong_baselines_5seed"
MODERN="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_modern_baselines_5seed"
LEGACY="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_legacy_baselines_5seed"
OUTPUT="$PROJECT_ROOT/results/strict_v2_20baseline_final"
POLICY="confirmed_composite_caeos_strict_v2_20260717"

cd "$PROJECT_ROOT"
mkdir -p "$OUTPUT"

"$CONDA" run -n py3.9 python audit_strict_v2_sota.py \
  --gate-root "$GATE_ROOT" \
  --baseline-root "strong=$STRONG" \
  --baseline-root "modern=$MODERN" \
  --baseline-root "legacy=$LEGACY" \
  --expected-models strong=opendetect,sieve \
  --expected-models modern=mlp,palm \
  --expected-models legacy=arpl,closr,cade,ronetc,foss \
  --seeds 7,11,19,23,37 \
  --output "$OUTPUT/audit.json"

comparison_args=(
  --gate-root "$GATE_ROOT"
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
"$CONDA" run -n py3.9 python summarize_neural_comparison_strict_v2.py \
  "${comparison_args[@]}"

"$CONDA" run -n py3.9 python summarize_sota_decision.py \
  --comparison "$OUTPUT/comparison_strict_v2.json" \
  --output "$OUTPUT/sota_decision.json" \
  --markdown-output "$OUTPUT/sota_decision.md"

"$CONDA" run -n py3.9 python -c \
  'import json,sys; from pathlib import Path; out=Path(sys.argv[1]); audit=json.load(open(out/"audit.json")); comp=json.load(open(out/"comparison_strict_v2.json")); decision=json.load(open(out/"sota_decision.json")); assert audit["state"] == "complete"; assert comp["global"]["run_count"] == 190; assert comp["global"]["scenario_inference_units"] == 38; assert len(comp["global"]["methods"]) == 20; assert decision["global"]["baseline_method_count"] == 20; assert decision["claim_gate"]["suite_count"] == 3; assert isinstance(decision["claim_gate"]["full_sota_claim_allowed"], bool); assert decision["claim_gate"]["highest_supported_claim"]' \
  "$OUTPUT"
