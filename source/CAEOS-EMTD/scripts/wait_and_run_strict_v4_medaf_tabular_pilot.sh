#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PROTOCOL="$PROJECT_ROOT/results/strict_v4_medaf_tabular_pilot_protocol/protocol_manifest.json"
DESIGN="$PROJECT_ROOT/results/strict_v4_medaf_tabular_design/design.json"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_medaf_tabular_pilot"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_medaf_tabular_pilot"
COMPARATIVE_ROOT="$PROJECT_ROOT/results/strict_v4_comparative_corruption"
MDR_ROOT="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"
STATE_LOG="$RESULT_ROOT/watcher_state.log"
IDLE_LOG="$RESULT_ROOT/idle_observations.log"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "MEDAF-Tabular pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE_LOG"
}

cd "$PROJECT_ROOT"
: > "$STATE_LOG"
log_state "waiting for comparative corruption and MDR pilot completion"
until [[ -s "$COMPARATIVE_ROOT/summary.json" \
  && -f "$COMPARATIVE_ROOT/summary_complete" \
  && -s "$MDR_ROOT/summary.json" \
  && -s "$MDR_ROOT/audit.json" \
  && -f "$MDR_ROOT/pilot_complete" ]]; do
  sleep 60
done

"$PYTHON" - "$PROTOCOL" "$MDR_ROOT/audit.json" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

protocol = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
audit = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if protocol.get("schema_version") != "strict_v4_medaf_tabular_pilot_protocol_v1":
    raise SystemExit("wrong MEDAF pilot protocol schema")
if protocol.get("manifest_sha256") != canonical_hash(protocol):
    raise SystemExit("MEDAF pilot protocol canonical hash mismatch")
if protocol.get("execution_admitted") is not True:
    raise SystemExit("MEDAF pilot execution not admitted")
if audit.get("manifest_sha256") != canonical_hash(audit):
    raise SystemExit("MDR audit canonical hash mismatch")
if audit.get("passes") is not True:
    raise SystemExit("MDR pilot audit failed")
PY

BLOCKER_PATTERN='run_strict_v4_comparative_corruption|run_strict_v4_mdr_caeos|run_strict_v4_medaf_tabular|train_hybrid_open_set|train_mdr_caeos|train_medaf_tabular|train_neural_open_set'
: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(
    pgrep -af "$BLOCKER_PATTERN" 2>/dev/null \
      | grep -v 'wait_and_run_strict_v4_medaf_tabular_pilot.sh' \
      | grep -v 'pgrep -af' \
      || true
  )"
  printf '%s sample=%d gpu=%q experiments=%q\n' \
    "$(date --iso-8601=seconds)" "$idle_samples" \
    "$gpu_processes" "$experiment_processes" >> "$IDLE_LOG"
  if [[ -n "$gpu_processes" || -n "$experiment_processes" ]]; then
    idle_samples=0
  else
    idle_samples=$((idle_samples + 1))
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done
log_state "five consecutive idle samples passed"

log_state "running resumable MEDAF-Tabular pilot"
ionice -c 3 nice -n 19 "$PYTHON" run_strict_v4_medaf_tabular_pilot.py \
  --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" \
  --project-root "$PROJECT_ROOT" \
  > "$RESULT_ROOT/execution.log" 2>&1

log_state "summarizing MEDAF-Tabular pilot"
"$PYTHON" summarize_strict_v4_medaf_tabular_pilot.py \
  --design "$DESIGN" \
  --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" \
  --output "$RESULT_ROOT/summary.json" \
  > "$RESULT_ROOT/summary.log" 2>&1

log_state "independently auditing MEDAF-Tabular pilot"
"$PYTHON" audit_strict_v4_medaf_tabular_pilot.py \
  --protocol "$PROTOCOL" \
  --design "$DESIGN" \
  --summary "$RESULT_ROOT/summary.json" \
  --run-root "$RUN_ROOT" \
  --project-root "$PROJECT_ROOT" \
  --output "$RESULT_ROOT/audit.json" \
  > "$RESULT_ROOT/audit.log" 2>&1

"$PYTHON" - "$RESULT_ROOT/summary.json" "$RESULT_ROOT/audit.json" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

summary_path = Path(sys.argv[1])
summary = json.loads(summary_path.read_text(encoding="utf-8"))
audit = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if summary.get("manifest_sha256") != canonical_hash(summary):
    raise SystemExit("MEDAF summary canonical hash mismatch")
if audit.get("manifest_sha256") != canonical_hash(audit):
    raise SystemExit("MEDAF audit canonical hash mismatch")
if audit.get("passes") is not True:
    raise SystemExit("MEDAF independent audit failed")
if summary["decision"]["expand_to_full102_confirmation"]:
    marker = "full102_design_required"
else:
    marker = "full102_not_admitted"
summary_path.parent.joinpath(marker).write_text(
    summary["manifest_sha256"] + "\n", encoding="utf-8"
)
summary_path.parent.joinpath("pilot_complete").write_text(
    audit["manifest_sha256"] + "\n", encoding="utf-8"
)
PY
log_state "MEDAF-Tabular pilot complete; full102 remains conditional"
