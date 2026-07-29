#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CICIOT_SOURCE="${CICIOT_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV}"
SEEDS_COMMA="139,149,163"
SEEDS_SPACE="139 149 163"
SCENARIOS="recon_os_scan,ddos_udp_flood,ddos_synonymous_ip_flood,ddos_rstfin_flood,ddos_http_flood,ddos_slowloris"
MAX_PER_CLASS=1000
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_comp_confirmation_v1"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_comp_confirmation_v1"
PAIRWISE_ROOT="$RUN_ROOT/pairwise"
OPENDETECT_ROOT="$RUN_ROOT/opendetect"
PAIRWISE_MANIFEST="$PROJECT_ROOT/results/strict_v4_boundary_pairwise_development/candidate_manifest.json"
CICIOT_RAW="$PROJECT_ROOT/caches/strict_v4_comp_confirmation_v1/cic_iot2023/raw"
CICIOT_CACHE="$PROJECT_ROOT/caches/strict_v4_comp_confirmation_v1/cic_iot2023/group_supported"
POLICY_NAME="strict_v4_comp_confirmation_pairwise_v1"
PROTOCOL="$RESULT_ROOT/protocol.json"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$CICIOT_RAW" "$CICIOT_CACHE"

"$PYTHON" -c \
  'import json,sys; from pathlib import Path; from create_strict_v4_external_confirmation_protocol import canonical_hash,file_hash; p=json.load(open(sys.argv[1])); assert p["schema_version"] == "strict_v4_comp_confirmation_protocol_v1"; assert p["manifest_sha256"] == canonical_hash(p); assert all(Path(k).is_file() and file_hash(Path(k)) == v for k,v in p["implementation_sha256"].items())' \
  "$PROTOCOL"

read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK OBJECTIVE < <(
  "$PYTHON" -c \
    'import json,sys; c=json.load(open(sys.argv[1]))["candidate"]; print(c["maximum_alpha"], c["minimum_fold_gain"], c["hard_pseudo_fraction"], c["interpolation"], c["max_per_task"], c["training_objective"])' \
    "$PAIRWISE_MANIFEST"
)

for seed in $SEEDS_SPACE; do
  raw="$CICIOT_RAW/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$raw" ]]; then
    "$PYTHON" prepare_cic_iot2023_strict.py \
      --input-dir "$CICIOT_SOURCE" \
      --output "$raw" \
      --seed "$seed" \
      --max-per-class "$MAX_PER_CLASS" \
      --group-rows 1000 \
      --expected-source-files 309
  fi
  cache="$CICIOT_CACHE/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$cache" ]]; then
    "$PYTHON" prepare_group_supported_cache.py \
      --input "$raw" \
      --output "$cache" \
      --label-column Attack \
      --group-column CaptureGroup \
      --minimum-groups 3
  fi
done > "$RESULT_ROOT/cache_preparation.log" 2>&1

sha256sum "$CICIOT_RAW"/*.csv "$CICIOT_CACHE"/*.csv \
  > "$RESULT_ROOT/cache_sha256.txt"

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 \
  --scenarios "$SCENARIOS" \
  --seeds "$SEEDS_COMMA" \
  --workers 2 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection nested_boundary_pairwise_pseudo_unknown_blend \
  --pseudo-unknown-max-alpha "$MAX_ALPHA" \
  --pseudo-unknown-min-fold-gain "$MIN_FOLD" \
  --boundary-hard-pseudo-fraction "$HARD_FRACTION" \
  --boundary-interpolation "$INTERPOLATION" \
  --boundary-max-per-task "$MAX_TASK" \
  --boundary-training-objective "$OBJECTIVE" \
  --risk-policy-name "$POLICY_NAME" \
  --output-root "$PAIRWISE_ROOT" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  > "$RESULT_ROOT/pairwise_training.log" 2>&1

"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_iot2023 \
  --scenarios "$SCENARIOS" \
  --models opendetect \
  --seeds "$SEEDS_COMMA" \
  --workers 2 \
  --epochs 0 \
  --patience 10 \
  --output-root "$OPENDETECT_ROOT" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CICIOT_CACHE" \
  > "$RESULT_ROOT/opendetect_training.log" 2>&1

"$PYTHON" evaluate_strict_v4_comp_confirmation.py \
  --protocol "$PROTOCOL" \
  --pairwise-root "$PAIRWISE_ROOT" \
  --opendetect-root "$OPENDETECT_ROOT" \
  --output "$RESULT_ROOT/confirmation.json" \
  > "$RESULT_ROOT/evaluation.log" 2>&1

"$PYTHON" -c \
  'import json,sys; x=json.load(open(sys.argv[1])); assert x["validation"]["paired_task_count"] == 18; assert x["validation"]["seeds"] == [139,149,163]; assert isinstance(x["decision"]["passes"], bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
