#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PY="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PYTHONPATH_VALUE=".:/opt/data/private/wangwt/anaconda3/envs/py3.9/lib/python3.9/site-packages"
KRC_RESULT="$ROOT/results/strict_v4_krc_csr_confirmation_v1"
INTEGRATED="$ROOT/results/strict_v4_krc_integrated_comprehensive_sota_v2"
STATE="$INTEGRATED/state.log"
LOCK="$INTEGRATED/orchestrator.lock.d"

mkdir -p "$INTEGRATED"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "KRC downstream orchestrator is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

run_logged() {
  local log="$1"
  shift
  printf '%s running %s\n' "$(date --iso-8601=seconds)" "$*" >> "$STATE"
  PYTHONPATH="$PYTHONPATH_VALUE" "$@" > "$log" 2>&1
}

printf '%s waiting for canonical KRC final summary and audit\n' "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$KRC_RESULT/summary.json" && -s "$KRC_RESULT/audit.json" ]]; do
  sleep 300
done

DECISION="$INTEGRATED/downstream_decision.json"
if [[ ! -s "$DECISION" ]]; then
  run_logged "$INTEGRATED/downstream_decision.log" \
    "$PY" "$ROOT/finalize_strict_v4_krc_downstream_decision_v2.py" \
    --integrated-protocol "$INTEGRATED/protocol.json" \
    --confirmation-protocol "$KRC_RESULT/protocol.json" \
    --confirmation-summary "$KRC_RESULT/summary.json" \
    --confirmation-audit "$KRC_RESULT/audit.json" \
    --output "$DECISION"
fi

HANDOFF="$INTEGRATED/terminal_handoff.json"
run_logged "$INTEGRATED/terminal_handoff.log" \
  "$PY" "$ROOT/write_strict_v4_krc_terminal_handoff.py" \
  --decision "$DECISION" --output "$HANDOFF"
printf '%s KRC terminal decision handed off; algorithm-specific downstream deferred\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
