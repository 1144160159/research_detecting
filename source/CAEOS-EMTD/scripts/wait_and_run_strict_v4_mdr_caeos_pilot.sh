#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PROTOCOL="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot_protocol/protocol_manifest.json"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_mdr_caeos_pilot"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot"
COMPARATIVE_ROOT="$PROJECT_ROOT/results/strict_v4_comparative_corruption"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"
STATE_LOG="$RESULT_ROOT/watcher_state.log"
IDLE_LOG="$RESULT_ROOT/idle_observations.log"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "MDR-CAEOS pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE_LOG"
}

cd "$PROJECT_ROOT"
: > "$STATE_LOG"
log_state "waiting for comparative corruption summary"
until [[ -s "$COMPARATIVE_ROOT/summary.json" \
  && -f "$COMPARATIVE_ROOT/summary_complete" ]]; do
  sleep 60
done

"$PYTHON" - "$PROTOCOL" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

path = Path(sys.argv[1])
value = json.loads(path.read_text(encoding="utf-8"))
if value.get("schema_version") != "strict_v4_mdr_caeos_pilot_execution_protocol_v1":
    raise SystemExit("wrong MDR pilot protocol schema")
if value.get("manifest_sha256") != canonical_hash(value):
    raise SystemExit("MDR pilot protocol canonical hash mismatch")
if value.get("execution_admitted") is not True:
    raise SystemExit("MDR pilot execution not admitted")
PY

BLOCKER_PATTERN='run_strict_v4_comparative_corruption|run_strict_v4_vgrf|run_strict_v4_mdr_caeos|train_hybrid_open_set|train_mdr_caeos|capture_mdr_caeos'
: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(
    pgrep -af "$BLOCKER_PATTERN" 2>/dev/null \
      | grep -v 'wait_and_run_strict_v4_mdr_caeos_pilot.sh' \
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

log_state "running resumable MDR-CAEOS pilot"
ionice -c 3 nice -n 19 "$PYTHON" run_strict_v4_mdr_caeos_pilot.py \
  --protocol "$PROTOCOL" \
  --run-root "$RUN_ROOT" \
  --result-root "$RESULT_ROOT" \
  --project-root "$PROJECT_ROOT" \
  > "$RESULT_ROOT/execution.log" 2>&1

DESIGN="$PROJECT_ROOT/results/strict_v4_mdr_caeos_design/design_v2.json"
log_state "summarizing MDR-CAEOS pilot"
"$PYTHON" summarize_mdr_caeos_pilot.py \
  --design "$DESIGN" \
  --selection "$RESULT_ROOT/weight_selection.json" \
  --evaluation-root "$RUN_ROOT/evaluations" \
  --output "$RESULT_ROOT/summary.json" \
  > "$RESULT_ROOT/summary.log" 2>&1

log_state "independently auditing MDR-CAEOS pilot"
"$PYTHON" audit_mdr_caeos_pilot.py \
  --protocol "$PROTOCOL" \
  --design "$DESIGN" \
  --selection "$RESULT_ROOT/weight_selection.json" \
  --summary "$RESULT_ROOT/summary.json" \
  --evaluation-root "$RUN_ROOT/evaluations" \
  --project-root "$PROJECT_ROOT" \
  --output "$RESULT_ROOT/audit.json" \
  > "$RESULT_ROOT/audit.log" 2>&1

"$PYTHON" - "$RESULT_ROOT/summary.json" "$RESULT_ROOT/audit.json" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
audit = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if summary.get("manifest_sha256") != canonical_hash(summary):
    raise SystemExit("MDR pilot summary canonical hash mismatch")
if audit.get("manifest_sha256") != canonical_hash(audit):
    raise SystemExit("MDR pilot audit canonical hash mismatch")
if audit.get("passes") is not True:
    raise SystemExit("MDR pilot independent audit failed")
if summary["decision"]["expand_to_full102_confirmation"]:
    marker = "full_confirmation_design_required"
else:
    marker = "full_confirmation_not_admitted"
Path(sys.argv[1]).parent.joinpath(marker).write_text(
    summary["manifest_sha256"] + "\n", encoding="utf-8"
)
Path(sys.argv[1]).parent.joinpath("pilot_complete").write_text(
    audit["manifest_sha256"] + "\n", encoding="utf-8"
)
PY
log_state "MDR-CAEOS pilot complete; full confirmation remains conditional"
