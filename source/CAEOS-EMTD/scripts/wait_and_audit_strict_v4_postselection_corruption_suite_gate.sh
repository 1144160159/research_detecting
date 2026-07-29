#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_postselection_corruption_seed7"
SUMMARY_ROOT="$PROJECT_ROOT/results/strict_v4_postselection_corruption_confirmation"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_postselection_corruption_seed7"
ROOT="$PROJECT_ROOT/results/strict_v4_postselection_corruption_suite_gate_seed7"
COVERAGE="$PROJECT_ROOT/results/strict_v4_full103_seed7/coverage_manifest_v2.json"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "post-selection corruption suite-gate watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

printf '%s waiting for authority corruption summary\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$ROOT/protocol_manifest.json" \
  && -f "$SUMMARY_ROOT/summary_complete" \
  && -s "$SUMMARY_ROOT/summary.json" \
  && -s "$ROOT/record_hash_compatibility.json" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
nice -n 19 ionice -c 3 "$PYTHON" \
  audit_strict_v4_postselection_corruption_suite_gate.py \
  --project-root "$PROJECT_ROOT" \
  --suite-protocol "$ROOT/protocol_manifest.json" \
  --base-protocol "$PROTOCOL_ROOT/protocol_manifest.json" \
  --coverage "$COVERAGE" \
  --authority-summary "$SUMMARY_ROOT/summary.json" \
  --record-hash-compatibility "$ROOT/record_hash_compatibility.json" \
  --run-root "$RUN_ROOT" \
  --output "$ROOT/audit.json" \
  > "$ROOT/audit.log" 2>&1
printf '%s suite-gate audit complete\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
