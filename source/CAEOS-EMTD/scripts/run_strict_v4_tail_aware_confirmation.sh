#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_tail_aware_confirmation"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_tail_aware_confirmation"
CACHE_ROOT="$PROJECT_ROOT/caches/strict_v4_tail_aware_confirmation"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
PILOT_PROTOCOL="$PROJECT_ROOT/results/strict_v4_tail_aware_pilot/protocol_manifest.json"
PILOT_ANALYSIS="$PROJECT_ROOT/results/strict_v4_tail_aware_pilot/analysis.json"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"

EDGE_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/Edge-IIoTset dataset/Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv"
NF_CSE_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/NF-CSE-CIC-IDS2018-v2.csv"
USTC_SOURCE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/ustc_tfc2016/ustc_tfc2016_nfstream.csv"
NF_UNSW_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/NF-UNSW-NB15-v2.csv"
CICIDS_SOURCE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v3/cicids2017/source/cicids2017_strict.csv"
TON_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
CICIOT_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$RUN_ROOT" "$CACHE_ROOT"
test -s "$PROTOCOL"
"$PYTHON" - "$PROTOCOL" "$PROJECT_ROOT" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

path = Path(sys.argv[1])
root = Path(sys.argv[2])
payload = json.loads(path.read_text(encoding="utf-8"))
assert payload["manifest_sha256"] == canonical_hash(payload)
for name, expected in payload["implementation_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected
PY

mapfile -t VALUES < <(
  "$PYTHON" -c 'import json,sys; p=json.load(open(sys.argv[1])); c=p["candidate"]; q=p["confirmation"]; print(",".join(map(str,q["seeds"]))); print(" ".join(map(str,q["seeds"]))); print(q["expected_run_count"]); print(q["risk_policy"]); print(c["maximum_alpha"],c["runtime_minimum_fold_gain"],c["hard_pseudo_fraction"],c["boundary_interpolation"],c["boundary_max_per_task"])' "$PROTOCOL"
)
SEEDS_COMMA="${VALUES[0]}"
SEEDS_SPACE="${VALUES[1]}"
EXPECTED="${VALUES[2]}"
POLICY="${VALUES[3]}"
read -r MAX_ALPHA MIN_FOLD HARD_FRACTION INTERPOLATION MAX_TASK <<< "${VALUES[4]}"

prepare_one() {
  local suite="$1" source="$2" config="$3" maximum="$4" seed="$5"
  local output_dir="$CACHE_ROOT/$suite"
  local output="$output_dir/seed${seed}_max${maximum}.csv"
  mkdir -p "$output_dir"
  if [[ -s "$output" && -s "$output.json" ]]; then
    return
  fi
  ionice -c3 nice -n 19 "$PYTHON" prepare_stratified_cache.py \
    --csv "$source" --config "$config" --max-per-class "$maximum" \
    --chunksize 50000 --seed "$seed" --output "$output" \
    > "$output_dir/seed${seed}.log" 2>&1
  test -s "$output"
  test -s "$output.json"
}

for seed in $SEEDS_SPACE; do
  prepare_one edge_iiot "$EDGE_SOURCE" configs/edge_iiot.json 1000 "$seed"
  prepare_one nf_cse "$NF_CSE_SOURCE" configs/nf_cse_cic_ids2018_v2.json 1000 "$seed"
  prepare_one ustc_tfc2016 "$USTC_SOURCE" configs/ustc_tfc2016_nfstream.json 3000 "$seed"
  prepare_one nf_unsw "$NF_UNSW_SOURCE" configs/nf_unsw_nb15.json 5000 "$seed"
  prepare_one cicids2017 "$CICIDS_SOURCE" configs/cicids2017_strict.json 5000 "$seed"
  prepare_one cic_ton_iot "$TON_SOURCE" configs/cic_ton_iot_strict.json 1000 "$seed"

  raw="$CACHE_ROOT/cic_iot2023_raw/seed${seed}_max1000.csv"
  grouped="$CACHE_ROOT/cic_iot2023/seed${seed}_max1000.csv"
  mkdir -p "$(dirname "$raw")" "$(dirname "$grouped")"
  if [[ ! -s "$raw" || ! -s "$raw.json" ]]; then
    ionice -c3 nice -n 19 "$PYTHON" prepare_cic_iot2023_strict.py \
      --input-dir "$CICIOT_SOURCE" --output "$raw" --seed "$seed" \
      --max-per-class 1000 --group-rows 1000 --expected-source-files 309 \
      > "$CACHE_ROOT/cic_iot2023_raw/seed${seed}.log" 2>&1
  fi
  if [[ ! -s "$grouped" || ! -s "$grouped.json" ]]; then
    "$PYTHON" prepare_group_supported_cache.py \
      --input "$raw" --output "$grouped" --label-column Attack \
      --group-column CaptureGroup --minimum-groups 3 \
      > "$CACHE_ROOT/cic_iot2023/seed${seed}.log" 2>&1
  fi
done
find "$CACHE_ROOT" -name 'seed*_max*.csv' -type f -print0 | sort -z | \
  xargs -0 sha256sum > "$RESULT_ROOT/cache_sha256.txt"
touch "$RESULT_ROOT/caches_complete"

COMMON=(
  --scenarios all
  --seeds "$SEEDS_COMMA"
  --workers 2
  --model-jobs 8
  --estimators 80
  --risk-selection nested_tail_aware_pairwise_pseudo_unknown_blend
  --pseudo-unknown-max-alpha "$MAX_ALPHA"
  --pseudo-unknown-min-fold-gain "$MIN_FOLD"
  --boundary-hard-pseudo-fraction "$HARD_FRACTION"
  --boundary-interpolation "$INTERPOLATION"
  --boundary-max-per-task "$MAX_TASK"
  --risk-policy-name "$POLICY"
  --output-root "$RUN_ROOT"
)

run_suite() {
  local suite="$1"
  shift
  "$PYTHON" run_nested_gate_matrix.py --suite "$suite" "${COMMON[@]}" "$@" \
    >> "$RESULT_ROOT/training.log" 2>&1
}

run_suite edge_iiot --edge-iiot-cache-dir "$CACHE_ROOT/edge_iiot" --edge-iiot-max-per-class 1000
run_suite nf_cse --nf-cse-cache-dir "$CACHE_ROOT/nf_cse" --nf-cse-max-per-class 1000
run_suite ustc_tfc2016 --ustc-cache-dir "$CACHE_ROOT/ustc_tfc2016" --ustc-max-per-class 3000
run_suite nf_unsw --nf-unsw-cache-dir "$CACHE_ROOT/nf_unsw" --nf-unsw-max-per-class 5000
run_suite cicids2017 --cicids2017-cache-dir "$CACHE_ROOT/cicids2017" --cicids2017-max-per-class 5000
run_suite cic_ton_iot --cic-ton-iot-cache-dir "$CACHE_ROOT/cic_ton_iot" --cic-ton-iot-max-per-class 1000
run_suite cic_iot2023 --cic-iot2023-cache-dir "$CACHE_ROOT/cic_iot2023" --cic-iot2023-max-per-class 1000

metrics_count="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
printf 'tail-aware confirmation metrics=%s/%s failures=%s\n' "$metrics_count" "$EXPECTED" "$failures" \
  > "$RESULT_ROOT/coverage.log"
[[ "$metrics_count" -eq "$EXPECTED" && "$failures" -eq 0 ]]

"$PYTHON" confirm_strict_v4_tail_aware.py \
  --coverage "$COVERAGE" --pilot-protocol "$PILOT_PROTOCOL" \
  --pilot-analysis "$PILOT_ANALYSIS" --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/confirmation.log" 2>&1
touch "$RESULT_ROOT/confirmation_complete"
