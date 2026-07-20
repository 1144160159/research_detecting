#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PRIMARY_ROOT="$PROJECT_ROOT/results/strict_v4_external_training_pilot_seed7"
OUTPUT="$PROJECT_ROOT/results/strict_v4_complementary_training_pilot_seed7"
LOCK_DIR="$OUTPUT/launcher.lock.d"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "complementary training pilot launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$PRIMARY_ROOT/pilot_complete" ]]; do
  sleep 60
done

while [[ -f "$PRIMARY_ROOT/full102_expansion_required" \
  && ! -f "$PRIMARY_ROOT/full102_expansion_complete" ]]; do
  printf 'waiting for primary full102 expansion at %s\n' "$(date -u +%FT%TZ)" \
    >> "$OUTPUT/watcher.log"
  sleep 300
done

cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_complementary_training_pilot.sh
