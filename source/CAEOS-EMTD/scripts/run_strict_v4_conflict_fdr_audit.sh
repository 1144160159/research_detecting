#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_metrics_seed7"
LOCK_DIR="$RESULT_ROOT/fdr_audit.lock.d"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "conflict FDR audit launcher is already active" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
cd "$PROJECT_ROOT"

"$PYTHON" create_strict_v4_conflict_fdr_audit_protocol.py --project-root "$PROJECT_ROOT" --parent-protocol "$RESULT_ROOT/protocol_manifest.json" --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/fdr_protocol.log" 2>&1
test -f "$RESULT_ROOT/analysis_complete"
"$PYTHON" audit_strict_v4_conflict_metric_fdr.py --protocol "$RESULT_ROOT/fdr_protocol_manifest.json" --parent-protocol "$RESULT_ROOT/protocol_manifest.json" --analysis "$RESULT_ROOT/analysis.json" --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/fdr_audit.log" 2>&1
