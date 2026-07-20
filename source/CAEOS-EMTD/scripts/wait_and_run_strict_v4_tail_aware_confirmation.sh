#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PILOT_COMPLETE="$PROJECT_ROOT/results/strict_v4_tail_aware_pilot/pilot_complete"
PILOT_ANALYSIS="$PROJECT_ROOT/results/strict_v4_tail_aware_pilot/analysis.json"
CONFIRMATION_COMPLETE="$PROJECT_ROOT/results/strict_v4_tail_aware_confirmation/confirmation_complete"

while [[ ! -f "$PILOT_COMPLETE" ]]; do
  sleep 60
done
if ! grep -q '"decision": "freeze_for_new_seed_confirmation"' "$PILOT_ANALYSIS"; then
  exit 0
fi
if [[ -f "$CONFIRMATION_COMPLETE" ]]; then
  exit 0
fi
exec bash "$PROJECT_ROOT/scripts/run_strict_v4_tail_aware_confirmation.sh"
