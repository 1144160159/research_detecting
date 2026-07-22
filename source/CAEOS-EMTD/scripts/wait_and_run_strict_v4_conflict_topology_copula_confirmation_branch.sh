#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_pilot_seed7"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_conflict_topology_copula_confirmation"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_confirmation"
BRANCH_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_confirmation_branch"
LOCK_DIR="$BRANCH_ROOT/watcher.lock.d"

mkdir -p "$BRANCH_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "CTC confirmation branch watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$PILOT_ROOT/pilot_complete" && -s "$PILOT_ROOT/analysis.json" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
decision="$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["decision"])' "$PILOT_ROOT/analysis.json")"
if [[ "$decision" == "freeze_for_reserved_seed_confirmation" ]]; then
  mkdir -p "$RESULT_ROOT"
  if [[ ! -s "$RESULT_ROOT/protocol_manifest.json" ]]; then
    "$PYTHON" create_strict_v4_conflict_topology_copula_confirmation_protocol.py \
      --pilot-protocol "$PILOT_ROOT/protocol_manifest.json" \
      --pilot-analysis "$PILOT_ROOT/analysis.json" \
      --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
      --pairwise-manifest results/strict_v4_boundary_pairwise_development/candidate_manifest.json \
      --project-root "$PROJECT_ROOT" --run-root "$RUN_ROOT" \
      --output "$RESULT_ROOT/protocol_manifest.json" \
      > "$RESULT_ROOT/protocol_freeze.log" 2>&1
  fi
  bash scripts/run_strict_v4_conflict_topology_copula_confirmation.sh \
    > "$RESULT_ROOT/execution.log" 2>&1
else
  "$PYTHON" -c \
    'import json,sys; from pathlib import Path; Path(sys.argv[1]).write_text(json.dumps({"status":"not_required","pilot_decision":sys.argv[2]},indent=2)+"\n")' \
    "$BRANCH_ROOT/not_required.json" "$decision"
fi
touch "$BRANCH_ROOT/branch_complete"
