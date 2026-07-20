#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_pairwise_pilot_caeos"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_pairwise_pilot"
TON_CACHE="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"
NEURAL_ROOT="$PROJECT_ROOT/runs/strict_v4_pilot_neural"
HCRP_ROOT="$PROJECT_ROOT/runs/strict_v4_hcrp_osd_pilot"
DATASET_MANIFEST="$PROJECT_ROOT/results/gpu_candidate_dataset_inventory_20260717/strict_v4_candidate_manifest.json"
DATASET_MANIFEST_SHA="39f8c4801420aa7c9501f1065710ec07c10560117f12bb5bcec8541d2b6cc945"
GROUP_SIDECAR="$CICIOT_CACHE/seed7_max1000.csv.json"
POLICY="strict_v4_pairwise_pilot_v1"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

COMMON=(
  --seeds 7
  --workers 2
  --model-jobs 8
  --estimators 80
  --risk-selection nested_boundary_pairwise_pseudo_unknown_blend
  --pseudo-unknown-max-alpha 0.5
  --pseudo-unknown-min-fold-gain -0.05
  --boundary-hard-pseudo-fraction 0.5
  --boundary-interpolation 0.5
  --boundary-max-per-task 512
  --boundary-training-objective pairwise
  --risk-policy-name "$POLICY"
  --output-root "$RUN_ROOT"
)

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_ton_iot \
  --scenarios xss,scanning,ransomware \
  "${COMMON[@]}" \
  --cic-ton-iot-cache-dir "$TON_CACHE" \
  --cic-ton-iot-max-per-class 1000 \
  > "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 \
  --scenarios ddos_icmp_flood,mirai_udpplain,command_injection \
  "${COMMON[@]}" \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  --cic-iot2023-max-per-class 1000 \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" summarize_strict_v4_pairwise_pilot.py \
  --caeos-root "$RUN_ROOT" \
  --neural-root "$NEURAL_ROOT" \
  --manifest "$DATASET_MANIFEST" \
  --expected-manifest-sha256 "$DATASET_MANIFEST_SHA" \
  --group-cache-sidecar "$GROUP_SIDECAR" \
  --output-dir "$RESULT_ROOT/base_15_method" \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" summarize_hcrp_osd_strict_v4_pilot.py \
  --hcrp-root "$HCRP_ROOT" \
  --caeos-root "$RUN_ROOT" \
  --existing-summary "$RESULT_ROOT/base_15_method/summary.json" \
  --output-dir "$RESULT_ROOT" \
  >> "$RESULT_ROOT/training.log" 2>&1

"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["scenario_count"] == 6; assert len(p["overall"]) == 16' \
  "$RESULT_ROOT/summary.json"
touch "$RESULT_ROOT/training_complete"
