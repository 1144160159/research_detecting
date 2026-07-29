#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_validation_gated_reliability_fusion_seed307"
REFERENCE_ROOT="$PROJECT_ROOT/runs/strict_v4_validation_gated_reliability_fusion_reference_seed307"
CANDIDATE_ROOT="$PROJECT_ROOT/runs/strict_v4_validation_gated_reliability_fusion_seed307"

cd "$PROJECT_ROOT"
"$PYTHON" run_strict_v4_validation_gated_reliability_fusion_matrix.py \
  --protocol "$RESULT_ROOT/protocol_manifest.json" --project-root "$PROJECT_ROOT" \
  --reference-root "$REFERENCE_ROOT" --candidate-root "$CANDIDATE_ROOT" \
  > "$RESULT_ROOT/execution.log" 2>&1
"$PYTHON" summarize_strict_v4_validation_gated_reliability_fusion.py \
  --protocol "$RESULT_ROOT/protocol_manifest.json" --run-root "$CANDIDATE_ROOT" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1
