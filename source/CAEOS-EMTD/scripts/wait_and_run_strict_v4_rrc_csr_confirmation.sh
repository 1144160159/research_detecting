#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PY="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PYTHONPATH_VALUE=".:/opt/data/private/wangwt/anaconda3/envs/py3.9/lib/python3.9/site-packages"
KRC="$ROOT/results/strict_v4_krc_csr_confirmation_v1"
INTEGRATED="$ROOT/results/strict_v4_krc_integrated_comprehensive_sota_v2"
DECISION="$INTEGRATED/downstream_decision.json"
RRC_DESIGN="$ROOT/results/strict_v4_rrc_csr_fallback_design_v1/design.json"
RRC_CORE="$ROOT/results/strict_v4_rrc_csr_core_protocol_v1/protocol.json"
RRC_IMPL="$ROOT/results/strict_v4_rrc_csr_execution_implementation_protocol_v1/protocol.json"
RRC_INPUT="$ROOT/results/strict_v4_rrc_csr_execution_input_protocol_v1"
RRC_RESULT="$ROOT/results/strict_v4_rrc_csr_confirmation_v1"
RRC_RUN="$ROOT/runs/strict_v4_rrc_csr_confirmation_v1"
STATE="$RRC_RESULT/state.log"
LOCK="$RRC_RESULT/watcher.lock.d"

mkdir -p "$RRC_RESULT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "RRC confirmation watcher is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

run_logged() {
  local log="$1"
  shift
  printf '%s running %s\n' "$(date --iso-8601=seconds)" "$*" >> "$STATE"
  (
    cd "$ROOT"
    PYTHONPATH="$PYTHONPATH_VALUE" "$@"
  ) > "$log" 2>&1
}

printf '%s waiting for canonical KRC v2 terminal decision\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$DECISION" ]]; do
  sleep 300
done

decision_action="$(
  cd "$ROOT"
  PYTHONPATH="$PYTHONPATH_VALUE" "$PY" \
    "$ROOT/classify_strict_v4_rrc_terminal_decision.py" \
    --decision "$DECISION"
)"
if [[ "$decision_action" == "rrc_not_required" ]]; then
  run_logged "$RRC_RESULT/not_required.log" \
    "$PY" - "$DECISION" "$RRC_RESULT/not_required.json" <<'PY'
import json
import sys
from create_strict_v4_external_confirmation_protocol import canonical_hash

decision = json.load(open(sys.argv[1], "r", encoding="utf-8"))
value = {
    "schema_version": "strict_v4_rrc_csr_not_required_v1",
    "state": "terminal_not_required_krc_selected",
    "krc_downstream_decision_manifest_sha256": decision["manifest_sha256"],
    "selected_algorithm": "krc_csr_caeos_v1",
    "rrc_execution_started": False,
}
value["manifest_sha256"] = canonical_hash(value)
open(sys.argv[2], "w", encoding="utf-8").write(
    json.dumps(value, indent=2, sort_keys=True) + "\n"
)
PY
  printf '%s KRC positive; RRC not required\n' \
    "$(date --iso-8601=seconds)" >> "$STATE"
  exit 0
fi
if [[ "$decision_action" != "run_rrc" ]]; then
  echo "unsupported RRC watcher decision action: $decision_action" >&2
  exit 3
fi

mkdir -p "$RRC_INPUT"
if [[ ! -s "$RRC_INPUT/protocol.json" ]]; then
  run_logged "$RRC_INPUT/protocol.log" \
    "$PY" "$ROOT/create_strict_v4_rrc_csr_execution_input_protocol.py" \
    --project-root "$ROOT" --rrc-design "$RRC_DESIGN" \
    --rrc-core-protocol "$RRC_CORE" \
    --integrated-protocol "$INTEGRATED/protocol.json" \
    --krc-protocol "$KRC/protocol.json" \
    --downstream-decision "$DECISION" \
    --output "$RRC_INPUT/protocol.json"
fi

run_logged "$RRC_RESULT/implementation_protocol.log" \
  "$PY" "$ROOT/create_strict_v4_rrc_csr_execution_implementation_protocol.py" \
  --project-root "$ROOT" --design "$RRC_DESIGN" \
  --core-protocol "$RRC_CORE" --output "$RRC_IMPL"

if [[ ! -s "$RRC_RESULT/protocol.json" ]]; then
  run_logged "$RRC_RESULT/protocol.log" \
    "$PY" "$ROOT/create_strict_v4_rrc_csr_execution_protocol.py" \
    --project-root "$ROOT" --rrc-design "$RRC_DESIGN" \
    --rrc-input-protocol "$RRC_INPUT/protocol.json" \
    --rrc-implementation-protocol "$RRC_IMPL" \
    --krc-protocol "$KRC/protocol.json" --run-root "$RRC_RUN" \
    --result-root "$RRC_RESULT" --output "$RRC_RESULT/protocol.json"
fi

if [[ ! -s "$RRC_RESULT/execution_complete.json" ]]; then
  run_logged "$RRC_RESULT/execution.log" \
    "$PY" "$ROOT/run_strict_v4_rrc_csr_confirmation.py" \
    --protocol "$RRC_RESULT/protocol.json" --project-root "$ROOT" \
    --run-root "$RRC_RUN" --result-root "$RRC_RESULT" --workers 4
fi
printf '%s RRC terminal execution complete\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
