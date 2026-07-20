#!/usr/bin/env bash
set -euo pipefail

GROUP="${1:?usage: run_strict_v4_training_full102_expansion.sh complementary|aegis}"
PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"

case "$GROUP" in
  complementary)
    PILOT_NAME="strict_v4_complementary_training_pilot_seed7"
    EXPANSION_NAME="strict_v4_complementary_training_full102_seed7"
    RUNNER="run_neural_baseline_matrix.py"
    WORKERS=4
    ;;
  aegis)
    PILOT_NAME="strict_v4_aegis_training_pilot_seed7"
    EXPANSION_NAME="strict_v4_aegis_training_full102_seed7"
    RUNNER="run_aegis_baseline_matrix.py"
    WORKERS=1
    ;;
  *)
    echo "unsupported training full102 group: $GROUP" >&2
    exit 2
    ;;
esac

PILOT_RESULT_ROOT="$PROJECT_ROOT/results/$PILOT_NAME"
RUN_ROOT="$PROJECT_ROOT/runs/$EXPANSION_NAME"
RESULT_ROOT="$PROJECT_ROOT/results/$EXPANSION_NAME"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"

[[ -f "$PILOT_RESULT_ROOT/pilot_complete" ]]
[[ -s "$PILOT_RESULT_ROOT/full102_expansion_required" ]]
mkdir -p "$RESULT_ROOT"
cd "$PROJECT_ROOT"

"$PYTHON" create_strict_v4_training_full102_expansion_protocol.py \
  --group "$GROUP" \
  --coverage "$COVERAGE" \
  --pilot-protocol "$PILOT_RESULT_ROOT/protocol_manifest.json" \
  --pilot-analysis "$PILOT_RESULT_ROOT/analysis.json" \
  --project-root "$PROJECT_ROOT" \
  --expansion-root "$RUN_ROOT" \
  > "$RESULT_ROOT/protocol.log" 2>&1
cp "$RUN_ROOT/protocol_manifest.json" "$RESULT_ROOT/protocol_manifest.json"

METHODS="$($PYTHON -c 'import json,sys; print(",".join(json.load(open(sys.argv[1]))["methods"]))' "$RUN_ROOT/protocol_manifest.json")"
EXPECTED="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_runs"])' "$RUN_ROOT/protocol_manifest.json")"

run_suite() {
  local suite="$1"
  shift
  nice -n 10 "$PYTHON" "$RUNNER" \
    --suite "$suite" --scenarios all --models "$METHODS" \
    --seeds 7 --workers "$WORKERS" --epochs 0 --patience 10 \
    --output-root "$RUN_ROOT" "$@" \
    >> "$RESULT_ROOT/training.log" 2>&1
}

run_suite cic_iot2023 \
  --cic-iot2023-cache-dir "$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported" \
  --cic-iot2023-max-per-class 1000
run_suite cic_ton_iot \
  --cic-ton-iot-cache-dir "$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified" \
  --cic-ton-iot-max-per-class 1000
run_suite cicids2017 \
  --cicids2017-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/cicids2017/stratified \
  --cicids2017-max-per-class 5000
run_suite edge_iiot \
  --edge-iiot-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot \
  --edge-iiot-max-per-class 1000
run_suite nf_cse \
  --nf-cse-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse \
  --nf-cse-max-per-class 1000
run_suite nf_unsw \
  --nf-unsw-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/nf_unsw/stratified \
  --nf-unsw-max-per-class 5000
run_suite ustc_tfc2016 \
  --ustc-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016 \
  --ustc-max-per-class 3000

COUNT="$(find "$RUN_ROOT" -mindepth 3 -maxdepth 3 -name metrics.json | wc -l)"
FAILURES="$(find "$RUN_ROOT" -mindepth 3 -maxdepth 3 -name failure.json | wc -l)"
[[ "$COUNT" -eq "$EXPECTED" && "$FAILURES" -eq 0 ]]

"$PYTHON" summarize_strict_v4_training_full102_expansion.py \
  --expansion-root "$RUN_ROOT" \
  --source-root runs/strict_v4_full103_mlp_seed7 \
  --opendetect-root runs/strict_v4_full103_independent_baselines_seed7 \
  --output-dir "$RESULT_ROOT" \
  --pilot-result-root "$PILOT_RESULT_ROOT" \
  > "$RESULT_ROOT/summary.log" 2>&1
