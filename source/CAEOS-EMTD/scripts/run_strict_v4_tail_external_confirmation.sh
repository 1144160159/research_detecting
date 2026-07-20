#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_external_confirmation"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_tail_external_confirmation"
CANDIDATE_ROOT="$PROJECT_ROOT/runs/strict_v4_tail_external_confirmation"
COMPARATOR_ROOT="$PROJECT_ROOT/runs/strict_v4_tail_external_opendetect"
CACHE_ROOT="$PROJECT_ROOT/caches/strict_v4_tail_external_confirmation"
PROTOCOL="$PROTOCOL_ROOT/protocol_manifest.json"
OPTIMAL="$PROJECT_ROOT/results/strict_v4_optimal_self_algorithm/decision.json"

EDGE_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/Edge-IIoTset dataset/Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv"
NF_CSE_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/NF-CSE-CIC-IDS2018-v2.csv"
USTC_SOURCE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/ustc_tfc2016/ustc_tfc2016_nfstream.csv"
NF_UNSW_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/NF-UNSW-NB15-v2.csv"
CICIDS_SOURCE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v3/cicids2017/source/cicids2017_strict.csv"
TON_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
CICIOT_SOURCE="/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$PROTOCOL_ROOT" "$CANDIDATE_ROOT" "$COMPARATOR_ROOT" "$CACHE_ROOT"
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
read -r SELECTED < <(
  "$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["selected_algorithm"])' "$OPTIMAL"
)
[[ "$SELECTED" == "caeos_tail_aware_pairwise" ]]
mapfile -t VALUES < <(
  "$PYTHON" -c 'import json,sys; p=json.load(open(sys.argv[1])); c=p["candidate"]; print(",".join(map(str,p["seeds"]))); print(" ".join(map(str,p["seeds"]))); print(p["expected_candidate_runs"]); print(c["risk_policy"]); print(c["maximum_alpha"],c["runtime_minimum_fold_gain"],c["hard_pseudo_fraction"],c["boundary_interpolation"],c["boundary_max_per_task"])' "$PROTOCOL"
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
  test -s "$output" && test -s "$output.json"
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
  xargs -0 sha256sum > "$PROTOCOL_ROOT/cache_sha256.txt"
touch "$PROTOCOL_ROOT/caches_complete"

TAIL_COMMON=(
  --scenarios all --seeds "$SEEDS_COMMA" --workers 2 --model-jobs 8 --estimators 80
  --risk-selection nested_tail_aware_pairwise_pseudo_unknown_blend
  --pseudo-unknown-max-alpha "$MAX_ALPHA"
  --pseudo-unknown-min-fold-gain "$MIN_FOLD"
  --boundary-hard-pseudo-fraction "$HARD_FRACTION"
  --boundary-interpolation "$INTERPOLATION"
  --boundary-max-per-task "$MAX_TASK"
  --risk-policy-name "$POLICY" --output-root "$CANDIDATE_ROOT"
)
run_tail() {
  local suite="$1"; shift
  "$PYTHON" run_nested_gate_matrix.py --suite "$suite" "${TAIL_COMMON[@]}" "$@" \
    >> "$PROTOCOL_ROOT/candidate_training.log" 2>&1
}
run_tail edge_iiot --edge-iiot-cache-dir "$CACHE_ROOT/edge_iiot" --edge-iiot-max-per-class 1000
run_tail nf_cse --nf-cse-cache-dir "$CACHE_ROOT/nf_cse" --nf-cse-max-per-class 1000
run_tail ustc_tfc2016 --ustc-cache-dir "$CACHE_ROOT/ustc_tfc2016" --ustc-max-per-class 3000
run_tail nf_unsw --nf-unsw-cache-dir "$CACHE_ROOT/nf_unsw" --nf-unsw-max-per-class 5000
run_tail cicids2017 --cicids2017-cache-dir "$CACHE_ROOT/cicids2017" --cicids2017-max-per-class 5000
run_tail cic_ton_iot --cic-ton-iot-cache-dir "$CACHE_ROOT/cic_ton_iot" --cic-ton-iot-max-per-class 1000
run_tail cic_iot2023 --cic-iot2023-cache-dir "$CACHE_ROOT/cic_iot2023" --cic-iot2023-max-per-class 1000
[[ "$(find "$CANDIDATE_ROOT" -name metrics.json | wc -l)" -eq "$EXPECTED" ]]
[[ "$(find "$CANDIDATE_ROOT" -name failure.json | wc -l)" -eq 0 ]]

run_open() {
  local suite="$1"; shift
  "$PYTHON" run_neural_baseline_matrix.py \
    --suite "$suite" --scenarios all --models opendetect --seeds "$SEEDS_COMMA" \
    --workers 4 --epochs 0 --patience 10 --output-root "$COMPARATOR_ROOT" "$@" \
    >> "$PROTOCOL_ROOT/opendetect_training.log" 2>&1
}
run_open edge_iiot --edge-iiot-cache-dir "$CACHE_ROOT/edge_iiot" --edge-iiot-max-per-class 1000
run_open nf_cse --nf-cse-cache-dir "$CACHE_ROOT/nf_cse" --nf-cse-max-per-class 1000
run_open ustc_tfc2016 --ustc-cache-dir "$CACHE_ROOT/ustc_tfc2016" --ustc-max-per-class 3000
run_open nf_unsw --nf-unsw-cache-dir "$CACHE_ROOT/nf_unsw" --nf-unsw-max-per-class 5000
run_open cicids2017 --cicids2017-cache-dir "$CACHE_ROOT/cicids2017" --cicids2017-max-per-class 5000
run_open cic_ton_iot --cic-ton-iot-cache-dir "$CACHE_ROOT/cic_ton_iot" --cic-ton-iot-max-per-class 1000
run_open cic_iot2023 --cic-iot2023-cache-dir "$CACHE_ROOT/cic_iot2023" --cic-iot2023-max-per-class 1000
[[ "$(find "$COMPARATOR_ROOT" -name metrics.json | wc -l)" -eq "$EXPECTED" ]]
[[ "$(find "$COMPARATOR_ROOT" -name failure.json | wc -l)" -eq 0 ]]

"$PYTHON" confirm_strict_v4_tail_external.py \
  --protocol "$PROTOCOL" --optimal-decision "$OPTIMAL" \
  --candidate-root "$CANDIDATE_ROOT" --comparator-root "$COMPARATOR_ROOT" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/confirmation.log" 2>&1
touch "$RESULT_ROOT/confirmation_complete"
