#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
ROOT="$PROJECT_ROOT/results/strict_v4_mdr_parrot_safety_v1"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_mdr_parrot_safety_v1"
DESIGN="$ROOT/design_protocol.json"
MDR="$PROJECT_ROOT/results/strict_v4_mdr_caeos_confirmation"
SELECTION="$MDR/final_selection.json"
FEATURE="$PROJECT_ROOT/results/parrot2025_full_no_decryption_features_v1"
EXTERNAL="$PROJECT_ROOT/results/strict_v4_mdr_external_malicious_v1"
SYSTEM="$PROJECT_ROOT/results/strict_v4_mdr_selected_system_v1"
COMPARATIVE_PROTOCOL="$PROJECT_ROOT/results/strict_v4_comparative_corruption_protocol/protocol_manifest_v2.json"
COMPARATIVE_RUN="$PROJECT_ROOT/runs/strict_v4_comparative_corruption"
PROTOCOL="$ROOT/protocol_manifest.json"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/watcher_state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "MDR PARROT safety watcher already active" >&2
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
    "schema_version": "strict_v4_mdr_parrot_safety_not_required_v1",
    "status": "not_required",
    "reason": "final_reserved_confirmation_did_not_select_mdr",
    "selected_algorithm": selection.get("selected_algorithm"),
    "design_manifest_sha256": design["manifest_sha256"],
    "selection_manifest_sha256": selection["manifest_sha256"],
    "input_file_sha256": {
        "design": hashlib.sha256(design_path.read_bytes()).hexdigest(),
        "selection": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
    },
    "benign_domain_shift_safety_gate_passes": False,
    "malicious_detection_claim_supported": False,
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

log_state "MDR selected; waiting for features, malicious external, and system evidence"
until [[ -s "$MDR/protocol_manifest.json" \
  && -s "$MDR/summary.json" \
  && -s "$MDR/audit.json" \
  && -f "$FEATURE/full_feature_extraction_complete" \
  && -s "$FEATURE/feature_shard_manifest.json" \
  && -f "$EXTERNAL/branch_complete" \
  && -f "$SYSTEM/branch_complete" ]]; do
  sleep 300
done

idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(
    nvidia-smi --query-compute-apps=pid --format=csv,noheader \
      2>/dev/null || true
  )"
  experiment_processes="$(
    pgrep -af 'train_|capture_|benchmark_|run_strict|execute_strict|corruption' \
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
  "$PYTHON" create_strict_v4_mdr_parrot_safety_protocol.py \
    --project-root "$PROJECT_ROOT" \
    --run-root "$RUN_ROOT" \
    --comparative-run-root "$COMPARATIVE_RUN" \
    --design "$DESIGN" \
    --selection "$SELECTION" \
    --confirmation-protocol "$MDR/protocol_manifest.json" \
    --confirmation-summary "$MDR/summary.json" \
    --confirmation-audit "$MDR/audit.json" \
    --feature-protocol "$FEATURE/protocol.json" \
    --feature-summary "$FEATURE/feature_shard_manifest.json" \
    --comparative-protocol "$COMPARATIVE_PROTOCOL" \
    --output "$PROTOCOL" \
    > "$ROOT/protocol_freeze.log" 2>&1
fi

log_state "running fresh MDR deployments and 320-capture benign safety replay"
nice -n 10 ionice -c 3 "$PYTHON" \
  run_strict_v4_mdr_parrot_safety.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --run-root "$RUN_ROOT" \
  --workers 3 \
  > "$ROOT/execution.log" 2>&1

log_state "summarizing capture-block benign false-alert evidence"
"$PYTHON" summarize_strict_v4_mdr_parrot_safety.py \
  --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" \
  --output "$ROOT/summary.json" \
  > "$ROOT/summary.log" 2>&1

log_state "independently auditing MDR PARROT safety evidence"
"$PYTHON" audit_strict_v4_mdr_parrot_safety.py \
  --protocol "$PROTOCOL" \
  --summary "$ROOT/summary.json" \
  --project-root "$PROJECT_ROOT" \
  --run-root "$RUN_ROOT" \
  --output "$ROOT/audit.json" \
  > "$ROOT/audit.log" 2>&1

"$PYTHON" - "$ROOT/audit.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
if value.get("passes") is not True:
    raise SystemExit("MDR PARROT integrity audit failed")
PY
touch "$ROOT/branch_complete"
log_state "MDR PARROT safety branch complete"
