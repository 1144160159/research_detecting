#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
MAIN_PROJECT_ROOT="${MAIN_PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CACHE_ROOT="${CACHE_ROOT:-$MAIN_PROJECT_ROOT/caches/strict_v4_final_efficiency_seed191}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_lcb_tail_aware_pilot_seed191"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_lcb_tail_aware_pilot_seed191"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
POLICY="strict_v4_lcb_tail_aware_pilot_seed191_v1"

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
  --seeds 191
  --workers 2
  --model-jobs 8
  --estimators 80
  --risk-selection nested_lcb_tail_aware_pairwise_pseudo_unknown_blend
  --pseudo-unknown-max-alpha 0.5
  --pseudo-unknown-min-fold-gain -0.05
  --boundary-hard-pseudo-fraction 0.5
  --boundary-interpolation 0.5
  --boundary-max-per-task 512
  --tail-aware-confidence-z 1.645
  --tail-aware-min-metric-lcb-gain 0.0
  --tail-aware-min-aupr-lcb-gain 0.0
  --tail-aware-min-aupr-fold-gain -0.05
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
    "${COMMON[@]}" "$@" >> "$RESULT_ROOT/training.log" 2>&1
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
printf 'LCB tail-aware pilot metrics=%s/14 failures=%s\n' "$metrics_count" "$failures" > "$RESULT_ROOT/coverage.log"
[[ "$metrics_count" -eq 14 && "$failures" -eq 0 ]]

"$PYTHON" analyze_strict_v4_lcb_tail_aware_pilot.py \
  --protocol "$PROTOCOL" --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/analysis.log" 2>&1
touch "$RESULT_ROOT/pilot_complete"
