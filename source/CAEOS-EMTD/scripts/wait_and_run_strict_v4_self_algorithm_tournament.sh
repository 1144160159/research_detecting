#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_optimal_self_algorithm"
until [[ -f "$PROJECT_ROOT/results/strict_v4_domain_safe_router_confirmation/confirmation_complete" \
  && -f "$PROJECT_ROOT/results/strict_v4_tail_aware_confirmation/confirmation_complete" ]]; do
  sleep 60
done
if [[ -f "$RESULT_ROOT/decision_complete" ]]; then
  exit 0
fi
exec bash "$PROJECT_ROOT/scripts/run_strict_v4_self_algorithm_tournament.sh"
