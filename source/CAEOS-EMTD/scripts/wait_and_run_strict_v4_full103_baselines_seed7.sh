#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_full103_baselines_seed7"
UPSTREAM_MARKER="$PROJECT_ROOT/results/strict_v4_full103_seed7/full103_complete"

mkdir -p "$RESULT_ROOT"
LOCK_DIR="$RESULT_ROOT/launcher.lock.d"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "baseline launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$UPSTREAM_MARKER" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
exec bash scripts/run_strict_v4_full103_baselines_seed7.sh
