#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_tail_aware_pilot"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_tail_aware_pilot"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
POLICY="strict_v4_tail_aware_pairwise_pilot_v1"

EDGE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
NF_CSE_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse"
USTC_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016"
NF_UNSW_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/nf_unsw/stratified"
CICIDS_DIR="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/caches/strict_v3/cicids2017/stratified"
TON_DIR="$PROJECT_ROOT/caches/strict_v4/cic_ton_iot/stratified"
CICIOT_DIR="$PROJECT_ROOT/caches/strict_v4/cic_iot2023/group_supported"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

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

COMMON=(
  --seeds 7
  --workers 2
  --model-jobs 8
  --estimators 80
  --risk-selection nested_tail_aware_pairwise_pseudo_unknown_blend
  --pseudo-unknown-max-alpha 0.5
  --pseudo-unknown-min-fold-gain -0.05
  --boundary-hard-pseudo-fraction 0.5
  --boundary-interpolation 0.5
  --boundary-max-per-task 512
  --risk-policy-name "$POLICY"
  --output-root "$RUN_ROOT"
)

run_suite() {
  local suite="$1"
  shift
  local scenarios
  scenarios="$("$PYTHON" -c 'import json,sys; p=json.load(open(sys.argv[1])); print(",".join(p["pilot"]["scenarios"][sys.argv[2]]))' "$PROTOCOL" "$suite")"
  "$PYTHON" run_nested_gate_matrix.py \
    --suite "$suite" --scenarios "$scenarios" \
    "${COMMON[@]}" "$@" \
    >> "$RESULT_ROOT/training.log" 2>&1
}

run_suite edge_iiot --edge-iiot-cache-dir "$EDGE_DIR" --edge-iiot-max-per-class 1000
run_suite nf_cse --nf-cse-cache-dir "$NF_CSE_DIR" --nf-cse-max-per-class 1000
run_suite ustc_tfc2016 --ustc-cache-dir "$USTC_DIR" --ustc-max-per-class 3000
run_suite nf_unsw --nf-unsw-cache-dir "$NF_UNSW_DIR" --nf-unsw-max-per-class 5000
run_suite cicids2017 --cicids2017-cache-dir "$CICIDS_DIR" --cicids2017-max-per-class 5000
run_suite cic_ton_iot --cic-ton-iot-cache-dir "$TON_DIR" --cic-ton-iot-max-per-class 1000
run_suite cic_iot2023 --cic-iot2023-cache-dir "$CICIOT_DIR" --cic-iot2023-max-per-class 1000

metrics_count="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
printf 'tail-aware pilot metrics=%s/14 failures=%s\n' "$metrics_count" "$failures" \
  > "$RESULT_ROOT/coverage.log"
[[ "$metrics_count" -eq 14 && "$failures" -eq 0 ]]

"$PYTHON" analyze_strict_v4_tail_aware_pilot.py \
  --protocol "$PROTOCOL" --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/analysis.log" 2>&1
touch "$RESULT_ROOT/pilot_complete"
