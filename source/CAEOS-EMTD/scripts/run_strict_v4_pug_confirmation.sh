#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CICIOT_SOURCE="${CICIOT_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV}"
SEEDS_COMMA="283,293,307"
SEEDS_SPACE="283 293 307"
SCENARIOS="ddos_syn_flood,mirai_greeth_flood,dos_udp_flood,backdoor_malware,dns_spoofing,ddos_icmp_fragmentation"
MAX_PER_CLASS=1000
RUN_ID="${RUN_ID:-strict_v4_pug_confirmation_v1}"
RUN_ROOT="${RUN_ROOT:-$PROJECT_ROOT/runs/$RUN_ID}"
RESULT_ROOT="${RESULT_ROOT:-$PROJECT_ROOT/results/$RUN_ID}"
CANDIDATE_ROOT="$RUN_ROOT/candidate"
OPENDETECT_ROOT="$RUN_ROOT/opendetect"
RAW_ROOT="${RAW_ROOT:-$PROJECT_ROOT/caches/$RUN_ID/cic_iot2023/raw}"
CACHE_ROOT="${CACHE_ROOT:-$PROJECT_ROOT/caches/$RUN_ID/cic_iot2023/group_supported}"
PROTOCOL="${PROTOCOL:-$RESULT_ROOT/execution_protocol.json}"
RISK_POLICY_NAME="${RISK_POLICY_NAME:-$RUN_ID}"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$RAW_ROOT" "$CACHE_ROOT"

"$PYTHON" -c \
  'import json,sys; from pathlib import Path; from create_strict_v4_external_confirmation_protocol import canonical_hash,file_hash; p=json.load(open(sys.argv[1])); assert p["schema_version"]=="strict_v4_pug_execution_protocol_v1"; assert p["manifest_sha256"]==canonical_hash(p); assert all(Path(k).is_file() and file_hash(Path(k))==v for k,v in p["implementation_sha256"].items())' \
  "$PROTOCOL"

for seed in $SEEDS_SPACE; do
  raw="$RAW_ROOT/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$raw" ]]; then
    "$PYTHON" prepare_cic_iot2023_strict.py \
      --input-dir "$CICIOT_SOURCE" --output "$raw" --seed "$seed" \
      --max-per-class "$MAX_PER_CLASS" --group-rows 1000 \
      --expected-source-files 309
  fi
  cache="$CACHE_ROOT/seed${seed}_max${MAX_PER_CLASS}.csv"
  if [[ ! -s "$cache" ]]; then
    "$PYTHON" prepare_group_supported_cache.py \
      --input "$raw" --output "$cache" --label-column Attack \
      --group-column CaptureGroup --minimum-groups 3
  fi
done > "$RESULT_ROOT/cache_preparation.log" 2>&1

sha256sum "$RAW_ROOT"/*.csv "$CACHE_ROOT"/*.csv > "$RESULT_ROOT/cache_sha256.txt"

"$PYTHON" run_nested_gate_matrix.py \
  --suite cic_iot2023 --scenarios "$SCENARIOS" --seeds "$SEEDS_COMMA" \
  --workers 2 --model-jobs 8 --estimators 80 \
  --risk-selection nested_pug_continuous_outer_min_p \
  --pseudo-unknown-max-alpha 0.5 \
  --pseudo-unknown-min-fold-gain -0.05 \
  --boundary-hard-pseudo-fraction 0.5 \
  --boundary-interpolation 0.5 \
  --boundary-max-per-task 512 \
  --boundary-training-objective pairwise \
  --risk-policy-name "$RISK_POLICY_NAME" \
  --output-root "$CANDIDATE_ROOT" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CACHE_ROOT" \
  > "$RESULT_ROOT/candidate_training.log" 2>&1

"$PYTHON" run_neural_baseline_matrix.py \
  --suite cic_iot2023 --scenarios "$SCENARIOS" --models opendetect \
  --seeds "$SEEDS_COMMA" --workers 2 --epochs 0 --patience 10 \
  --output-root "$OPENDETECT_ROOT" \
  --cic-iot2023-max-per-class "$MAX_PER_CLASS" \
  --cic-iot2023-cache-dir "$CACHE_ROOT" \
  > "$RESULT_ROOT/opendetect_training.log" 2>&1

"$PYTHON" evaluate_strict_v4_pug_confirmation.py \
  --protocol "$PROTOCOL" --candidate-root "$CANDIDATE_ROOT" \
  --opendetect-root "$OPENDETECT_ROOT" \
  --output "$RESULT_ROOT/confirmation.json" \
  > "$RESULT_ROOT/evaluation.log" 2>&1

"$PYTHON" -c \
  'import json,sys; x=json.load(open(sys.argv[1])); assert x["task_count"]==18; assert isinstance(x["decision"]["passes"],bool)' \
  "$RESULT_ROOT/confirmation.json"
touch "$RESULT_ROOT/confirmation_complete"
