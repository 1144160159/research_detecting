#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUTPUT="$PROJECT_ROOT/results/strict_v4_running_confirmation_health"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-300}"
LOCK_DIR="$OUTPUT/watcher.lock.d"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "running confirmation health watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
while true; do
  if ! "$PYTHON" audit_strict_v4_running_confirmations.py \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --router-caeos-root runs/strict_v4_domain_safe_router_confirmation_caeos \
    --router-mlp-root runs/strict_v4_domain_safe_router_confirmation_mlp \
    --tail-root runs/strict_v4_tail_aware_confirmation \
    --router-protocol results/strict_v4_domain_safe_router_confirmation/protocol_manifest.json \
    --tail-protocol results/strict_v4_tail_aware_confirmation/protocol_manifest.json \
    --output-dir "$OUTPUT" \
    > "$OUTPUT/latest.log" 2>&1; then
    printf '%s audit_failed_retrying\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      >> "$OUTPUT/watcher_errors.log"
    sleep "$INTERVAL_SECONDS"
    continue
  fi

  if "$PYTHON" - "$OUTPUT/health.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report.get("schema_version") != "strict_v4_running_confirmation_health_audit_v2":
    raise SystemExit(2)
matrices = report.get("matrices", {})
required = ("router_caeos", "router_mlp_openmax", "tail_aware")
complete = all(
    matrices.get(name, {}).get("validation", {}).get("completed_runs")
    == matrices.get(name, {}).get("validation", {}).get("expected_runs")
    for name in required
)
healthy = report.get("overall_health_passes") is True
raise SystemExit(0 if complete and healthy else 1)
PY
  then
    touch "$OUTPUT/monitoring_complete"
    exit 0
  fi
  sleep "$INTERVAL_SECONDS"
done
