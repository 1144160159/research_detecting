#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
SEEDS_COMMA="127,131"
MAX_PER_CLASS=1000
CAEOS_ROOT="$PROJECT_ROOT/runs/strict_v4_boundary_pairwise_confirmation"
MLP_ROOT="$PROJECT_ROOT/runs/strict_v4_external_risk_confirmation_mlp"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_external_risk_confirmation"
MANIFEST="$PROJECT_ROOT/results/strict_v4_external_risk_diagnostic/candidate_manifest.json"
PAIRWISE_MANIFEST="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development/candidate_manifest.json"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4_boundary_pairwise_confirmation/cic_ton_iot/stratified"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4_boundary_pairwise_confirmation/cic_iot2023/group_supported"
POLICY_NAME="strict_v4_boundary_pairwise_confirmation_v1"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK OBJECTIVE < <(
  "$PYTHON" -c \
    'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"], c["minimum_fold_gain"], c["hard_pseudo_fraction"], c["interpolation"], c["max_per_task"], c["training_objective"])' \
    "$PAIRWISE_MANIFEST"
)

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_ton_iot \
  --scenarios injection,password \
  --seeds "$SEEDS_COMMA" \
  --workers 2 --model-jobs 8 --estimators 80 \
  --risk-selection nested_boundary_pairwise_pseudo_unknown_blend \
  --pseudo-unknown-max-alpha "$MAX_ALPHA" \
  --pseudo-unknown-min-fold-gain "$MIN_FOLD" \
  --boundary-hard-pseudo-fraction "$HARD_FRACTION" \
  --boundary-interpolation "$INTERPOLATION" \
  --boundary-max-per-task "$MAX_TASK" \
  --boundary-training-objective "$OBJECTIVE" \
  --risk-policy-name "$POLICY_NAME" \
  --cic-ton-iot-max-per-class "$MAX_PER_CLASS" \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  --output-root "$CAEOS_ROOT" \
  > "$RESULT_ROOT/caeos_training.log" 2>&1

"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_ton_iot \
  --scenarios injection,password,mitm \
  --models mlp --seeds "$SEEDS_COMMA" --workers 2 --epochs 0 --patience 10 \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  --cic-ton-iot-max-per-class "$MAX_PER_CLASS" \
  --output-root "$MLP_ROOT" \
  > "$RESULT_ROOT/mlp_training.log" 2>&1

"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_iot2023 \
  --scenarios ddos_ack_fragmentation,dictionary_bruteforce,recon_ping_sweep \
  --models mlp --seeds "$SEEDS_COMMA" --workers 2 --epochs 0 --patience 10 \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --output-root "$MLP_ROOT" \
  >> "$RESULT_ROOT/mlp_training.log" 2>&1

"$PYTHON" analyze_caeos_closr_fusion.py \
  --gate-root "$CAEOS_ROOT" \
  --expert-root "$MLP_ROOT" \
  --expert-name openmax --expert-model mlp \
  --seeds "$SEEDS_COMMA" \
  --output "$RESULT_ROOT/raw_confirmation.json" \
  > "$RESULT_ROOT/analysis.log" 2>&1

"$PYTHON" confirm_strict_v4_external_risk.py \
  --raw-analysis "$RESULT_ROOT/raw_confirmation.json" \
  --manifest "$MANIFEST" \
  --project-root "$PROJECT_ROOT" \
  --output-dir "$RESULT_ROOT" \
  >> "$RESULT_ROOT/analysis.log" 2>&1

"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["validation"]["run_count"] == 12; assert isinstance(p["decision"]["passes"], bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
