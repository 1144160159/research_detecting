#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717}"
MATRIX_MARKER="$PROJECT_ROOT/results/strict_v2_classical_ood/matrix_complete"
OUTPUT="$PROJECT_ROOT/results/strict_v2_24baseline_extended"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
FINALIZER="$PROJECT_ROOT/scripts/finalize_strict_v2_extended_sota.sh"
EXPECTED_FINALIZER_SHA="fe1676628fa895edf7d7c4e1e2f6dc57bbcba075449acc34d2b9a0ec2af2ab01"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another extended SOTA finalizer is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$MATRIX_MARKER" ]]; do
  metrics=0
  failures=0
  if [[ -d "$PROJECT_ROOT/runs/strict_v2_classical_ood_5seed" ]]; then
    metrics="$(find "$PROJECT_ROOT/runs/strict_v2_classical_ood_5seed" -name metrics.json | wc -l)"
    failures="$(find "$PROJECT_ROOT/runs/strict_v2_classical_ood_5seed" -name failure.json | wc -l)"
  fi
  printf '%s waiting for classical matrix metrics=%s/190 failures=%s\n' \
    "$(date -Is)" "$metrics" "$failures" >> "$LOG"
  [[ "$failures" -eq 0 ]] || exit 1
  sleep 300
done

actual="$(sha256sum "$FINALIZER" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_FINALIZER_SHA" ]] || {
  printf 'finalizer SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_FINALIZER_SHA" "$actual" >&2
  exit 1
}
printf '%s starting strict-v2 24-baseline extended finalization\n' \
  "$(date -Is)" >> "$LOG"
bash "$FINALIZER" >> "$LOG" 2>&1
printf '%s strict-v2 24-baseline extended finalization complete\n' \
  "$(date -Is)" >> "$LOG"
