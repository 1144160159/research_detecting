#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_external_confirmation"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_external_comparator_confirmation"
CACHE_ROOT="$PROJECT_ROOT/caches/strict_v4_domain_safe_router_confirmation"
MLP_ROOT="$PROJECT_ROOT/runs/strict_v4_domain_safe_router_confirmation_mlp"
ROUTER_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_domain_safe_router_confirmation"
FINAL_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_final_algorithm"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
ROUTER_PROTOCOL="$ROUTER_RESULT_ROOT/protocol_manifest.json"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
ROUTER="$PROJECT_ROOT/results/strict_v4_domain_safe_router_development/candidate_manifest.json"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$RUN_ROOT"
read -r COMPARATOR SOURCE SEEDS EXPECTED < <(
  "$PYTHON" -c \
    'import json,sys; p=json.load(open(sys.argv[1])); print(p["selected_comparator"], p["selected_comparator_run_source"], ",".join(map(str,p["confirmation_seeds"])), p["expected_comparator_runs"])' \
    "$PROTOCOL"
)
WORKERS=2

run_suite() {
  local model="$1" suite="$2"
  shift 2
  "$PYTHON" run_neural_baseline_matrix.py \
    --suite "$suite" --scenarios all --models "$model" --seeds "$SEEDS" \
    --workers "$WORKERS" --epochs 0 --patience 10 --output-root "$RUN_ROOT" "$@" \
    >> "$RESULT_ROOT/${suite}_${model}.log" 2>&1
}

if [[ "$SOURCE" == "new_opendetect_confirmation_runs" ]]; then
  MODEL="opendetect"
  WORKERS=4
elif [[ "$SOURCE" == "new_shared_classical_confirmation_runs" ]]; then
  MODEL="classical_ood"
else
  MODEL=""
fi

"$PYTHON" - "$PROTOCOL" "$RESULT_ROOT/scheduler_plan.json" "$MODEL" "$WORKERS" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

protocol = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
record = {
    "schema_version": "strict_v4_external_confirmation_scheduler_plan_v1",
    "protocol_manifest_sha256": protocol["manifest_sha256"],
    "model": sys.argv[3] or "reuse_existing_mlp_reports",
    "outer_scenario_workers": int(sys.argv[4]),
    "algorithm_or_hyperparameter_changed": False,
    "seed_or_split_changed": False,
    "reason": (
        "OpenDetect seed7 observation: two workers used about 741 MiB of 49 GiB "
        "and about 54 percent GPU; four workers reduce wall time without changing "
        "per-scenario commands"
        if sys.argv[3] == "opendetect"
        else "conservative default for non-OpenDetect or reused reports"
    ),
}
core = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
record["record_sha256"] = hashlib.sha256(core).hexdigest()
Path(sys.argv[2]).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
PY

if [[ -n "$MODEL" ]]; then
  run_suite "$MODEL" edge_iiot --edge-iiot-cache-dir "$CACHE_ROOT/edge_iiot" --edge-iiot-max-per-class 1000
  run_suite "$MODEL" nf_cse --nf-cse-cache-dir "$CACHE_ROOT/nf_cse" --nf-cse-max-per-class 1000
  run_suite "$MODEL" ustc_tfc2016 --ustc-cache-dir "$CACHE_ROOT/ustc_tfc2016" --ustc-max-per-class 3000
  run_suite "$MODEL" nf_unsw --nf-unsw-cache-dir "$CACHE_ROOT/nf_unsw" --nf-unsw-max-per-class 5000
  run_suite "$MODEL" cicids2017 --cicids2017-cache-dir "$CACHE_ROOT/cicids2017" --cicids2017-max-per-class 5000
  run_suite "$MODEL" cic_ton_iot --cic-ton-iot-cache-dir "$CACHE_ROOT/cic_ton_iot" --cic-ton-iot-max-per-class 1000
  run_suite "$MODEL" cic_iot2023 --cic-iot2023-cache-dir "$CACHE_ROOT/cic_iot2023" --cic-iot2023-max-per-class 1000
  [[ "$(find "$RUN_ROOT" -name metrics.json | wc -l)" -eq "$EXPECTED" ]]
  [[ "$(find "$RUN_ROOT" -name failure.json | wc -l)" -eq 0 ]]
fi

"$PYTHON" confirm_strict_v4_external_comparator.py \
  --external-protocol "$PROTOCOL" --router-protocol "$ROUTER_PROTOCOL" \
  --coverage-manifest "$COVERAGE" --router-manifest "$ROUTER" \
  --raw-fusion "$ROUTER_RESULT_ROOT/raw_fusion.json" \
  --final-decision "$FINAL_RESULT_ROOT/decision.json" \
  --mlp-root "$MLP_ROOT" --external-root "$RUN_ROOT" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/confirmation.log" 2>&1
touch "$RESULT_ROOT/confirmation_complete"
