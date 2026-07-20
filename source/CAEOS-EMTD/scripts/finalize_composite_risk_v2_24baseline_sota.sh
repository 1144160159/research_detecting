#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717}"
COMPOSITE_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717"
BASE="$PROJECT_ROOT/scripts/finalize_composite_risk_24baseline_sota.sh"
EXPECTED_BASE_SHA="7d3510825158f344673c56672b4667633709b9ff67b8003862f0c12491e4d432"
actual="$(sha256sum "$BASE" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_BASE_SHA" ]] || {
  printf 'base finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_BASE_SHA" "$actual" >&2
  exit 1
}

GATE="$COMPOSITE_ROOT/runs/final_composite_risk_gate_v2_5seed" \
SELECTION="$COMPOSITE_ROOT/results/final_composite_risk_selection_v2/selection.json" \
OUTPUT="$PROJECT_ROOT/results/final_composite_risk_v2_24baseline_sota" \
bash "$BASE"
