#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_validation_gated_reliability_fusion_seed307"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "validation-gated reliability watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

while [[ ! -f "$PROJECT_ROOT/results/strict_v4_postefficiency_claim_chain_v2/chain_complete" ]]; do
  sleep 300
done
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_validation_gated_reliability_fusion_pilot.sh \
  > "$RESULT_ROOT/watcher_execution.log" 2>&1
