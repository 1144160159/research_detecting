#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
UPSTREAM="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717/results/strict_v2_classical_ood/matrix_complete"
OUTPUT="$PROJECT_ROOT/results/cross_suite_fixed_report_confirmation_v2"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"
RUNNER="$PROJECT_ROOT/scripts/run_cross_suite_risk_confirmation_v2.sh"
EXPECTED_RUNNER_SHA="1a4190459704c2992f7dc6d9ca8e4e41541182bdd601ce69632093d67f489323"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another cross-suite v2 confirmation is active\n' \
    "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while [[ ! -f "$UPSTREAM" ]]; do
  printf '%s waiting for classical matrix completion\n' "$(date -Is)" >> "$LOG"
  sleep 120
done

actual="$(sha256sum "$RUNNER" | awk '{print $1}')"
[[ "$actual" == "$EXPECTED_RUNNER_SHA" ]] || {
  printf 'runner SHA mismatch expected=%s actual=%s\n' \
    "$EXPECTED_RUNNER_SHA" "$actual" >&2
  exit 1
}
printf '%s starting cross-suite v2 held-out confirmation\n' \
  "$(date -Is)" >> "$LOG"
bash "$RUNNER" >> "$LOG" 2>&1
printf '%s cross-suite v2 held-out confirmation complete\n' \
  "$(date -Is)" >> "$LOG"
