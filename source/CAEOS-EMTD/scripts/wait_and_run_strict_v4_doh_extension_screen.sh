#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
UPSTREAM="$PROJECT_ROOT/results/strict_v4_domain_safe_router_confirmation/confirmation_complete"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_doh_extension_screen"
LOCK_DIR="$RESULT_ROOT/launcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "DoH extension launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
until [[ -f "$UPSTREAM" ]]; do
  sleep 60
done
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_doh_extension_screen.sh \
  > "$RESULT_ROOT/launcher.log" 2>&1
