#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PAIRWISE_MANIFEST="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development/candidate_manifest.json"
RUN_CAEOS="$PROJECT_ROOT/runs/strict_v4_full103_pairwise_caeos_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_full103_seed7"
CICIOT_DIR="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"
POLICY="strict_v4_full103_pairwise_coverage_v1"

cd "$PROJECT_ROOT"
read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK OBJECTIVE < <(
  "$PYTHON" -c \
    'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"], c["minimum_fold_gain"], c["hard_pseudo_fraction"], c["interpolation"], c["max_per_task"], c["training_objective"])' \
    "$PAIRWISE_MANIFEST"
)

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 --scenarios all --seeds 7 \
  --workers 4 --model-jobs 8 --estimators 80 \
  --risk-selection nested_boundary_pairwise_pseudo_unknown_blend \
  --pseudo-unknown-max-alpha "$MAX_ALPHA" \
  --pseudo-unknown-min-fold-gain "$MIN_FOLD" \
  --boundary-hard-pseudo-fraction "$HARD_FRACTION" \
  --boundary-interpolation "$INTERPOLATION" \
  --boundary-max-per-task "$MAX_TASK" \
  --boundary-training-objective "$OBJECTIVE" \
  --risk-policy-name "$POLICY" \
  --cic-iot2023-cache-dir "$CICIOT_DIR" \
  --cic-iot2023-max-per-class 1000 \
  --output-root "$RUN_CAEOS" \
  >> "$RESULT_ROOT/caeos_cic_iot2023.log" 2>&1

ciciot_count="$(find "$RUN_CAEOS/cic_iot2023" -name metrics.json | wc -l)"
total_count="$(find "$RUN_CAEOS" -name metrics.json | wc -l)"
failures="$(find "$RUN_CAEOS" -name failure.json | wc -l)"
[[ "$ciciot_count" -eq 32 && "$total_count" -eq 102 && "$failures" -eq 0 ]]
touch "$RESULT_ROOT/caeos_complete"

# Resume the corrected driver; all 102 feasible CAEOS tasks pass provenance and are skipped.
exec bash scripts/run_strict_v4_full103_seed7.sh
