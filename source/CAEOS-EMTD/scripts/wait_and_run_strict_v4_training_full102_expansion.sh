#!/usr/bin/env bash
set -euo pipefail

GROUP="${1:?usage: wait_and_run_strict_v4_training_full102_expansion.sh complementary|aegis}"
PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
case "$GROUP" in
  complementary) PILOT_NAME="strict_v4_complementary_training_pilot_seed7" ;;
  aegis) PILOT_NAME="strict_v4_aegis_training_pilot_seed7" ;;
  *) echo "unsupported training full102 group: $GROUP" >&2; exit 2 ;;
esac

PILOT_RESULT_ROOT="$PROJECT_ROOT/results/$PILOT_NAME"
OUTPUT="$PROJECT_ROOT/results/strict_v4_${GROUP}_training_full102_seed7"
LOCK_DIR="$OUTPUT/launcher.lock.d"
mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "$GROUP training full102 launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$PILOT_RESULT_ROOT/pilot_complete" ]]; do
  sleep 60
done
if [[ ! -s "$PILOT_RESULT_ROOT/full102_expansion_required" ]]; then
  printf 'full102 expansion not required at %s\n' "$(date -u +%FT%TZ)" \
    > "$OUTPUT/not_required"
  exit 0
fi
if [[ -f "$PILOT_RESULT_ROOT/full102_expansion_complete" ]]; then
  exit 0
fi

cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_training_full102_expansion.sh "$GROUP"
