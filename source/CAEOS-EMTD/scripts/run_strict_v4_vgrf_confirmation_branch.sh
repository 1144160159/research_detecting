#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_confirmation_seed311_313"
REFERENCE_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_confirmation_reference_seed311_313"
CANDIDATE_ROOT="$PROJECT_ROOT/runs/strict_v4_vgrf_confirmation_seed311_313"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
if [[ ! -f "$RESULT_ROOT/protocol_manifest.json" ]]; then
  "$PYTHON" create_strict_v4_vgrf_confirmation_protocol.py \
    --project-root "$PROJECT_ROOT" --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --pilot-protocol results/strict_v4_validation_gated_reliability_fusion_seed307/protocol_manifest.json \
    --pilot-analysis results/strict_v4_validation_gated_reliability_fusion_seed307/analysis.json \
    --pilot-run-root "$PROJECT_ROOT/runs/strict_v4_validation_gated_reliability_fusion_seed307" \
    --reference-root "$REFERENCE_ROOT" --candidate-root "$CANDIDATE_ROOT" \
    --output "$RESULT_ROOT/protocol_manifest.json"
fi
"$PYTHON" run_strict_v4_vgrf_confirmation_matrix.py \
  --protocol "$RESULT_ROOT/protocol_manifest.json" --project-root "$PROJECT_ROOT" \
  --reference-root "$REFERENCE_ROOT" --candidate-root "$CANDIDATE_ROOT" > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_vgrf_confirmation.py \
  --protocol "$RESULT_ROOT/protocol_manifest.json" --run-root "$CANDIDATE_ROOT" \
  --reference-root "$REFERENCE_ROOT" \
  --project-root "$PROJECT_ROOT" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1
