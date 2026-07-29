#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
SELF_ROOT="${SELF_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_unified_self_algorithm_selection"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
MAL_AUDIT="$SELF_ROOT/results/mal_tls_self_algorithm_selection/audit.json"
MAL_COMPLETE="$SELF_ROOT/results/mal_tls_self_algorithm_selection/audit_complete"
CTC_PILOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_pilot_seed7/analysis.json"
CTC_BRANCH="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_confirmation_branch"
CTC_CONFIRM_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_topology_copula_confirmation"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "unified self-algorithm selector already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -s "$PROTOCOL" && -f "$MAL_COMPLETE" && -s "$MAL_AUDIT" \
  && -s "$CTC_PILOT" && -f "$CTC_BRANCH/branch_complete" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
"$PYTHON" select_strict_v4_unified_self_algorithm.py \
  --protocol "$PROTOCOL" \
  --pairwise-manifest results/strict_v4_boundary_pairwise_development/candidate_manifest.json \
  --mal-tls-audit "$MAL_AUDIT" \
  --ctc-pilot-analysis "$CTC_PILOT" \
  --ctc-branch-root "$CTC_BRANCH" \
  --ctc-confirmation-protocol "$CTC_CONFIRM_ROOT/protocol_manifest.json" \
  --ctc-confirmation-analysis "$CTC_CONFIRM_ROOT/confirmation.json" \
  --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/selection.log" 2>&1
