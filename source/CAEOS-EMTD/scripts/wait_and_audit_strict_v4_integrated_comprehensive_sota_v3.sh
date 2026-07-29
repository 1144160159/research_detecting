#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
V2_ROOT="$PROJECT_ROOT/results/strict_v4_integrated_comprehensive_sota_v2"
SUITE_ROOT="$PROJECT_ROOT/results/strict_v4_postselection_corruption_suite_gate_seed7"
ROOT="$PROJECT_ROOT/results/strict_v4_integrated_comprehensive_sota_v3"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "integrated comprehensive SOTA v3 watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

printf '%s waiting for integrated v2 and suite-gate audits\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$ROOT/design_protocol.json" \
  && -f "$V2_ROOT/audit_complete" \
  && -s "$V2_ROOT/audit.json" \
  && -f "$SUITE_ROOT/audit_complete" \
  && -s "$SUITE_ROOT/audit.json" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
nice -n 19 ionice -c 3 "$PYTHON" \
  audit_strict_v4_integrated_comprehensive_sota_v3.py \
  --design "$ROOT/design_protocol.json" \
  --v2-design "$V2_ROOT/design_protocol.json" \
  --suite-gate-protocol "$SUITE_ROOT/protocol_manifest.json" \
  --v2-audit "$V2_ROOT/audit.json" \
  --suite-gate-audit "$SUITE_ROOT/audit.json" \
  --output "$ROOT/audit.json" \
  > "$ROOT/audit.log" 2>&1
printf '%s integrated v3 audit complete\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
