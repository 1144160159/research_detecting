#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_doh_extension_screen"
RUN_CAEOS="$PROJECT_ROOT/runs/strict_v4_doh_extension_caeos"
RUN_MLP="$PROJECT_ROOT/runs/strict_v4_doh_extension_mlp"
RUN_BASELINE="$PROJECT_ROOT/runs/strict_v4_doh_extension_baselines"
PROTOCOL="$PROJECT_ROOT/results/strict_v4_domain_safe_router_confirmation/protocol_manifest.json"
PAIRWISE_MANIFEST="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development/candidate_manifest.json"
AUDIT="$PROJECT_ROOT/results/strict_v4_extension_dataset_audit.json"
DOH_CSV="/opt/data/private/wangwt/ParkAttackKE/datasets/DoHBrw2020/caeos_multiclass_balanced_seed7.csv"
POLICY="strict_v4_doh_extension_pairwise_screen_v1"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
read -r SEEDS_COMMA EXPECTED < <(
  "$PYTHON" -c \
    'import json,sys; p=json.load(open(sys.argv[1])); s=p["confirmation_seeds"]; print(",".join(map(str,s)), 3*len(s))' \
    "$PROTOCOL"
)
"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); d=p["datasets"]["dohbrw2020"]; assert d["strict_group_generalization_eligible"] is True; assert d["source_csv"] == sys.argv[2]' \
  "$AUDIT" "$DOH_CSV"

read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK OBJECTIVE < <(
  "$PYTHON" -c \
    'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"], c["minimum_fold_gain"], c["hard_pseudo_fraction"], c["interpolation"], c["max_per_task"], c["training_objective"])' \
    "$PAIRWISE_MANIFEST"
)

"$PYTHON" run_nested_gate_matrix.py \
  --suite doh --scenarios all --seeds "$SEEDS_COMMA" \
  --workers 2 --model-jobs 8 --estimators 80 \
  --risk-selection nested_boundary_pairwise_pseudo_unknown_blend \
  --pseudo-unknown-max-alpha "$MAX_ALPHA" \
  --pseudo-unknown-min-fold-gain "$MIN_FOLD" \
  --boundary-hard-pseudo-fraction "$HARD_FRACTION" \
  --boundary-interpolation "$INTERPOLATION" \
  --boundary-max-per-task "$MAX_TASK" \
  --boundary-training-objective "$OBJECTIVE" \
  --risk-policy-name "$POLICY" --doh-csv "$DOH_CSV" \
  --doh-max-per-class 4000 --output-root "$RUN_CAEOS" \
  > "$RESULT_ROOT/caeos.log" 2>&1
[[ "$(find "$RUN_CAEOS" -name metrics.json | wc -l)" -eq "$EXPECTED" ]]
[[ "$(find "$RUN_CAEOS" -name failure.json | wc -l)" -eq 0 ]]
touch "$RESULT_ROOT/caeos_complete"

"$PYTHON" run_neural_baseline_matrix.py \
  --suite doh --scenarios all --models mlp --seeds "$SEEDS_COMMA" \
  --workers 2 --epochs 0 --patience 10 --doh-csv "$DOH_CSV" \
  --doh-max-per-class 4000 --output-root "$RUN_MLP" \
  > "$RESULT_ROOT/mlp.log" 2>&1
[[ "$(find "$RUN_MLP" -name metrics.json | wc -l)" -eq "$EXPECTED" ]]
[[ "$(find "$RUN_MLP" -name failure.json | wc -l)" -eq 0 ]]
touch "$RESULT_ROOT/mlp_complete"

"$PYTHON" run_neural_baseline_matrix.py \
  --suite doh --scenarios all --models opendetect,classical_ood \
  --seeds "$SEEDS_COMMA" --workers 2 --epochs 0 --patience 10 \
  --doh-csv "$DOH_CSV" --doh-max-per-class 4000 \
  --output-root "$RUN_BASELINE" > "$RESULT_ROOT/baselines.log" 2>&1
[[ "$(find "$RUN_BASELINE" -name metrics.json | wc -l)" -eq $((2 * EXPECTED)) ]]
[[ "$(find "$RUN_BASELINE" -name failure.json | wc -l)" -eq 0 ]]
touch "$RESULT_ROOT/baselines_complete"

"$PYTHON" analyze_caeos_closr_fusion.py \
  --gate-root "$RUN_CAEOS" --expert-root "$RUN_MLP" \
  --expert-name openmax --expert-model mlp --seeds "$SEEDS_COMMA" \
  --output "$RESULT_ROOT/raw_fusion.json" > "$RESULT_ROOT/fusion.log" 2>&1
"$PYTHON" summarize_strict_v4_doh_extension.py \
  --raw-fusion "$RESULT_ROOT/raw_fusion.json" \
  --gate-root "$RUN_CAEOS" --mlp-root "$RUN_MLP" \
  --baseline-root "$RUN_BASELINE" --protocol-manifest "$PROTOCOL" \
  --extension-audit "$AUDIT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/summary.log" 2>&1
touch "$RESULT_ROOT/screen_complete"
