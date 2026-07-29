#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
UPSTREAM_ROOT="${UPSTREAM_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
GEOMETRY_BRANCH="$UPSTREAM_ROOT/results/mal_tls_geometry_adapter_confirmation_branch"
COUNTERFACTUAL_BRANCH="$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_confirmation_branch"
PROTOCOL_ROOT="$PROJECT_ROOT/results/mal_tls_self_algorithm_selection_protocol_v2"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_self_algorithm_selection"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "self-algorithm selection watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$GEOMETRY_BRANCH/branch_complete" \
  && -f "$COUNTERFACTUAL_BRANCH/branch_complete" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
"$PYTHON" audit_mal_tls_self_algorithm_selection.py \
  --protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --geometry-pilot-analysis "$UPSTREAM_ROOT/results/mal_tls_geometry_preserving_adapter_seed195/analysis.json" \
  --geometry-branch-root "$GEOMETRY_BRANCH" \
  --geometry-confirmation-protocol "$UPSTREAM_ROOT/results/mal_tls_geometry_adapter_confirmation/protocol_manifest.json" \
  --geometry-confirmation-analysis "$UPSTREAM_ROOT/results/mal_tls_geometry_adapter_confirmation/analysis.json" \
  --counterfactual-pilot-analysis "$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_seed201/analysis.json" \
  --counterfactual-branch-root "$COUNTERFACTUAL_BRANCH" \
  --counterfactual-confirmation-protocol "$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_confirmation/protocol_manifest.json" \
  --counterfactual-confirmation-analysis "$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_confirmation/analysis.json" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/audit.log" 2>&1
