#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
DATA_ROOT="${DATA_ROOT:-/opt/data/private/wangwt/ParkAttackKE/datasets/caeos_external_open_set_v1}"
ROOT="$PROJECT_ROOT/results/strict_v4_mdr_external_malicious_v1"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_mdr_external_malicious_v1"
DESIGN="$ROOT/design_protocol.json"
POSTSELECTION="$PROJECT_ROOT/results/strict_v4_mdr_postselection_evidence_v1/design_protocol.json"
EXTERNAL_V1="$PROJECT_ROOT/results/gpu_external_dataset_evaluation_v1/design_protocol.json"
MDR="$PROJECT_ROOT/results/strict_v4_mdr_caeos_confirmation"
SELECTION="$MDR/final_selection.json"
PREPARATION="$PROJECT_ROOT/results/gpu_external_dataset_preparation_v1"
PROTOCOL="$ROOT/protocol_manifest.json"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/watcher_state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "MDR external malicious watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE"
}

cd "$PROJECT_ROOT"
: > "$STATE"
log_state "waiting for canonical MDR branch completion"
until [[ -f "$MDR/branch_complete" && -s "$SELECTION" ]]; do
  sleep 60
done

selected="$("$PYTHON" - "$SELECTION" <<'PY'
import json, sys
from create_strict_v4_external_confirmation_protocol import canonical_hash
value = json.load(open(sys.argv[1], encoding="utf-8"))
if value.get("schema_version") != "strict_v4_final_self_algorithm_selection_v2":
    raise SystemExit("wrong final selection schema")
if value.get("manifest_sha256") != canonical_hash(value):
    raise SystemExit("final selection canonical SHA mismatch")
print(value.get("selected_algorithm", ""))
PY
)"

if [[ "$selected" != "mdr_caeos_v1" ]]; then
  "$PYTHON" - "$DESIGN" "$SELECTION" "$ROOT/not_required.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash
design_path, selection_path, output = map(Path, sys.argv[1:])
design = json.loads(design_path.read_text(encoding="utf-8"))
selection = json.loads(selection_path.read_text(encoding="utf-8"))
value = {
    "schema_version": "strict_v4_mdr_external_malicious_not_required_v1",
    "status": "not_required",
    "reason": "final_reserved_confirmation_did_not_select_mdr",
    "selected_algorithm": selection.get("selected_algorithm"),
    "design_manifest_sha256": design["manifest_sha256"],
    "selection_manifest_sha256": selection["manifest_sha256"],
    "input_file_sha256": {
        "design": hashlib.sha256(design_path.read_bytes()).hexdigest(),
        "selection": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
    },
    "external_effect_gate_passes": False,
    "comprehensive_sota_confirmed": False,
}
value["manifest_sha256"] = canonical_hash(value)
output.write_text(
    json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY
  touch "$ROOT/branch_complete"
  log_state "MDR not selected; canonical not-required record written"
  exit 0
fi

log_state "MDR selected; waiting for full confirmation and external preparation"
until [[ -s "$MDR/protocol_manifest.json" \
  && -s "$MDR/summary.json" \
  && -s "$MDR/audit.json" \
  && -f "$PREPARATION/preparation_complete" \
  && -s "$PREPARATION/summary.json" ]]; do
  sleep 300
done

idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(
    nvidia-smi --query-compute-apps=pid --format=csv,noheader \
      2>/dev/null || true
  )"
  experiment_processes="$(
    pgrep -af 'train_|capture_|run_strict|execute_strict|corruption' \
      | grep -v -E 'wait_and_|pgrep -af' || true
  )"
  if [[ -z "$gpu_processes" && -z "$experiment_processes" ]]; then
    idle_samples=$((idle_samples + 1))
  else
    idle_samples=0
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done
log_state "five consecutive idle samples passed"

if [[ ! -s "$PROTOCOL" ]]; then
  "$PYTHON" create_strict_v4_mdr_external_malicious_protocol.py \
    --project-root "$PROJECT_ROOT" \
    --data-root "$DATA_ROOT" \
    --run-root "$RUN_ROOT" \
    --design "$DESIGN" \
    --postselection-design "$POSTSELECTION" \
    --external-v1-design "$EXTERNAL_V1" \
    --selection "$SELECTION" \
    --confirmation-protocol "$MDR/protocol_manifest.json" \
    --confirmation-summary "$MDR/summary.json" \
    --confirmation-audit "$MDR/audit.json" \
    --preparation-summary "$PREPARATION/summary.json" \
    --output "$PROTOCOL" \
    > "$ROOT/protocol_freeze.log" 2>&1
fi

log_state "running fresh MDR and OpenDetect external matrix"
ionice -c 3 nice -n 19 "$PYTHON" \
  run_strict_v4_mdr_external_malicious.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --output-root "$RUN_ROOT" \
  --python "$PYTHON" \
  > "$ROOT/execution.log" 2>&1

log_state "summarizing frozen MDR external evidence"
"$PYTHON" summarize_strict_v4_mdr_external_malicious.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --run-root "$RUN_ROOT" \
  --output "$ROOT/summary.json" \
  > "$ROOT/summary.log" 2>&1

log_state "independently auditing MDR external evidence"
"$PYTHON" audit_strict_v4_mdr_external_malicious.py \
  --protocol "$PROTOCOL" \
  --summary "$ROOT/summary.json" \
  --project-root "$PROJECT_ROOT" \
  --run-root "$RUN_ROOT" \
  --output "$ROOT/audit.json" \
  > "$ROOT/audit.log" 2>&1

touch "$ROOT/branch_complete"
log_state "MDR external malicious branch complete"
