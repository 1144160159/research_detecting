#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
CADREF_ROOT="$PROJECT_ROOT/results/strict_v4_cadref_family_pilot_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_fisher_rao_family_pilot_seed7"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Fisher-Rao pilot watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -s "$CADREF_ROOT/analysis.json" && -f "$CADREF_ROOT/branch_complete" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_fisher_rao_pilot.sh \
  > "$RESULT_ROOT/watcher_execution.log" 2>&1
