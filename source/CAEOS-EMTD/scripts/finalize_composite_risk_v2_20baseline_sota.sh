#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
BASE="$PROJECT_ROOT/scripts/finalize_composite_risk_20baseline_sota.sh"
EXPECTED_BASE_SHA="53dda8fad96da7df12dfc5734af205584e500c5b51a3353c6a46626326f4de06"
actual="$(sha256sum "$BASE" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_BASE_SHA" ]] || {
  printf 'base finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_BASE_SHA" "$actual" >&2
  exit 1
}

CROSS_CONFIRMATION="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation_v2/confirmation.json" \
CROSS_MANIFEST="$PROJECT_ROOT/results/cross_suite_fixed_risk_screen_v2/candidate_manifest.json" \
SELECTION="$PROJECT_ROOT/results/final_composite_risk_selection_v2/selection.json" \
GATE="$PROJECT_ROOT/runs/final_composite_risk_gate_v2_5seed" \
OUTPUT="$PROJECT_ROOT/results/final_composite_risk_v2_20baseline_sota" \
bash "$BASE"
