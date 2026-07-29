#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot"
DESIGN="$PROJECT_ROOT/results/strict_v4_mdr_caeos_design/design_v2.json"
PILOT_PROTOCOL="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot_protocol/protocol_manifest.json"
COMPARATIVE_PROTOCOL="$PROJECT_ROOT/results/strict_v4_comparative_corruption_protocol/protocol_manifest_v2.json"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_mdr_caeos_confirmation"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_mdr_caeos_confirmation"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"
STATE_LOG="$RESULT_ROOT/watcher_state.log"
IDLE_LOG="$RESULT_ROOT/idle_observations.log"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "MDR-CAEOS confirmation watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE_LOG"
}

cd "$PROJECT_ROOT"
: > "$STATE_LOG"
log_state "waiting for MDR-CAEOS pilot completion"
until [[ -f "$PILOT_ROOT/pilot_complete" \
  && -s "$PILOT_ROOT/summary.json" \
  && -s "$PILOT_ROOT/audit.json" ]]; do
  sleep 60
done

pilot_positive="$("$PYTHON" - \
  "$PILOT_ROOT/summary.json" "$PILOT_ROOT/audit.json" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
audit = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
valid = (
    summary.get("manifest_sha256") == canonical_hash(summary)
    and audit.get("manifest_sha256") == canonical_hash(audit)
    and audit.get("passes") is True
    and audit.get("summary_manifest_sha256") == summary["manifest_sha256"]
)
if not valid:
    raise SystemExit("invalid MDR pilot completion artifacts")
print(
    "true"
    if summary["decision"]["expand_to_full102_confirmation"] is True
    else "false"
)
PY
)"

if [[ "$pilot_positive" != "true" ]]; then
  log_state "pilot gate negative; writing canonical not-required branch"
  "$PYTHON" - \
    "$PILOT_ROOT/summary.json" "$PILOT_ROOT/audit.json" \
    "$RESULT_ROOT/not_required.json" \
    "$RESULT_ROOT/final_selection.json" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

summary_path, audit_path, output_path, selection_path = map(Path, sys.argv[1:])
summary = json.loads(summary_path.read_text(encoding="utf-8"))
audit = json.loads(audit_path.read_text(encoding="utf-8"))
not_required = {
    "schema_version": "strict_v4_mdr_caeos_confirmation_not_required_v1",
    "state": "complete",
    "reason": "frozen_mdr_pilot_gate_failed",
    "pilot_summary_manifest_sha256": summary["manifest_sha256"],
    "pilot_audit_manifest_sha256": audit["manifest_sha256"],
    "confirmation_metrics_generated": 0,
}
not_required["manifest_sha256"] = canonical_hash(not_required)
selection = {
    "schema_version": "strict_v4_final_self_algorithm_selection_v2",
    "state": "complete_after_negative_mdr_pilot",
    "selected_algorithm": "caeos_pairwise",
    "previous_incumbent": "caeos_pairwise",
    "mdr_confirmation_passes": False,
    "mdr_confirmation_not_required_manifest_sha256": not_required[
        "manifest_sha256"
    ],
    "selection_rule": (
        "negative MDR pilot makes reserved confirmation not required and "
        "retains Pairwise"
    ),
    "no_component_or_metric_wise_splicing": True,
    "comprehensive_sota_confirmed": False,
}
selection["manifest_sha256"] = canonical_hash(selection)
output_path.write_text(
    json.dumps(not_required, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
selection_path.write_text(
    json.dumps(selection, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
  printf '%s\n' "not_required" > "$RESULT_ROOT/confirmation_complete"
  touch "$RESULT_ROOT/branch_complete"
  log_state "negative MDR confirmation branch complete"
  exit 0
fi

BLOCKER_PATTERN='run_strict_v4_comparative_corruption|run_strict_v4_vgrf|run_strict_v4_mdr_caeos|run_strict_v4_medaf|train_hybrid_open_set|train_mdr_caeos|capture_mdr_caeos'
: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(
    pgrep -af "$BLOCKER_PATTERN" 2>/dev/null \
      | grep -v -E 'wait_and_|pgrep -af' \
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

log_state "freezing MDR reserved-confirmation protocol"
"$PYTHON" create_strict_v4_mdr_caeos_confirmation_protocol.py \
  --design "$DESIGN" \
  --pilot-protocol "$PILOT_PROTOCOL" \
  --pilot-selection "$PILOT_ROOT/weight_selection.json" \
  --pilot-summary "$PILOT_ROOT/summary.json" \
  --pilot-audit "$PILOT_ROOT/audit.json" \
  --comparative-protocol "$COMPARATIVE_PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --run-root "$RUN_ROOT" \
  --result-root "$RESULT_ROOT" \
  --implementation protocol_creator=create_strict_v4_mdr_caeos_confirmation_protocol.py \
  --implementation pilot_protocol_helper=create_strict_v4_mdr_caeos_pilot_execution_protocol.py \
  --implementation capture=capture_mdr_caeos_runtime.py \
  --implementation clean_trainer=train_hybrid_open_set.py \
  --implementation robust_trainer=train_mdr_caeos_open_set.py \
  --implementation structured_module=caeos/structured_robust.py \
  --implementation fusion_module=caeos/mdr_fusion.py \
  --implementation runtime=caeos/mdr_runtime.py \
  --implementation pilot_evaluator=evaluate_mdr_caeos_runtime.py \
  --implementation confirmation_evaluator=evaluate_mdr_caeos_confirmation_runtime.py \
  --implementation runner=run_strict_v4_mdr_caeos_confirmation.py \
  --implementation pilot_summarizer=summarize_mdr_caeos_pilot.py \
  --implementation summarizer=summarize_mdr_caeos_confirmation.py \
  --implementation auditor=audit_mdr_caeos_confirmation.py \
  --implementation watcher=scripts/wait_and_run_strict_v4_mdr_caeos_confirmation.sh \
  --output "$PROTOCOL" > "$RESULT_ROOT/protocol.log" 2>&1

log_state "running 306-capture / 1836-evaluation MDR confirmation"
ionice -c 3 nice -n 15 "$PYTHON" \
  run_strict_v4_mdr_caeos_confirmation.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --run-root "$RUN_ROOT" \
  --workers 4 > "$RESULT_ROOT/execution.log" 2>&1

log_state "summarizing MDR reserved confirmation"
"$PYTHON" summarize_mdr_caeos_confirmation.py \
  --protocol "$PROTOCOL" \
  --evaluation-root "$RUN_ROOT/evaluations" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/summary.log" 2>&1

log_state "independently auditing MDR reserved confirmation"
"$PYTHON" audit_mdr_caeos_confirmation.py \
  --protocol "$PROTOCOL" \
  --summary "$RESULT_ROOT/summary.json" \
  --selection "$RESULT_ROOT/final_selection.json" \
  --evaluation-root "$RUN_ROOT/evaluations" \
  --project-root "$PROJECT_ROOT" \
  --output "$RESULT_ROOT/audit.json" > "$RESULT_ROOT/audit.log" 2>&1

"$PYTHON" - "$RESULT_ROOT/audit.json" "$RESULT_ROOT" <<'PY'
import json
import sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

audit = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if (
    audit.get("manifest_sha256") != canonical_hash(audit)
    or audit.get("passes") is not True
):
    raise SystemExit("MDR confirmation audit failed")
root = Path(sys.argv[2])
root.joinpath("confirmation_complete").write_text(
    audit["manifest_sha256"] + "\n", encoding="utf-8"
)
root.joinpath("branch_complete").write_text(
    audit["manifest_sha256"] + "\n", encoding="utf-8"
)
PY
log_state "MDR reserved-confirmation branch complete"
