#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PILOT_ROOT="$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_seed201"
RUN_ROOT="$PROJECT_ROOT/runs/mal_tls_counterfactual_conflict_gate_confirmation"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_confirmation"
BRANCH_ROOT="$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_confirmation_branch"
LOCK_DIR="$BRANCH_ROOT/watcher.lock.d"

mkdir -p "$BRANCH_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "counterfactual confirmation branch watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$PILOT_ROOT/pilot_complete" && -s "$PILOT_ROOT/analysis.json" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
decision="$("$PYTHON" -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["decision"])' \
  "$PILOT_ROOT/analysis.json")"
if [[ "$decision" == "freeze_for_reserved_seed_confirmation" ]]; then
  mkdir -p "$RESULT_ROOT"
  if [[ ! -s "$RESULT_ROOT/protocol_manifest.json" ]]; then
    "$PYTHON" create_mal_tls_counterfactual_conflict_gate_confirmation_protocol.py \
      --pilot-protocol "$PILOT_ROOT/protocol_manifest.json" \
      --pilot-analysis "$PILOT_ROOT/analysis.json" \
      --project-root "$PROJECT_ROOT" --run-root "$RUN_ROOT" \
      --output "$RESULT_ROOT/protocol_manifest.json" \
      > "$RESULT_ROOT/protocol_freeze.log" 2>&1
  fi
  idle_samples=0
  while [[ "$idle_samples" -lt 5 ]]; do
    observed="$(nvidia-smi --query-compute-apps=pid,process_name \
      --format=csv,noheader 2>/dev/null || true)"
    if [[ -n "$observed" ]]; then idle_samples=0; else idle_samples=$((idle_samples + 1)); fi
    [[ "$idle_samples" -ge 5 ]] || sleep 30
  done
  bash scripts/run_mal_tls_counterfactual_conflict_gate_confirmation.sh \
    > "$RESULT_ROOT/execution.log" 2>&1
else
  "$PYTHON" -c \
    'import json,sys; from pathlib import Path; Path(sys.argv[1]).write_text(json.dumps({"status":"not_required","pilot_decision":sys.argv[2]},indent=2)+"\n")' \
    "$BRANCH_ROOT/not_required.json" "$decision"
fi
touch "$BRANCH_ROOT/branch_complete"
