#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_pairwise_caeos_seed7"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_conflict_metrics_seed7"
LOCK_DIR="$RESULT_ROOT/launcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "conflict metric analysis launcher is already active" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
cd "$PROJECT_ROOT"

ionice -c3 nice -n 15 "$PYTHON" create_strict_v4_conflict_metric_protocol.py --project-root "$PROJECT_ROOT" --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/protocol.log" 2>&1

ionice -c3 nice -n 15 "$PYTHON" analyze_strict_v4_conflict_metrics.py --protocol "$RESULT_ROOT/protocol_manifest.json" --output-dir "$RESULT_ROOT" > "$RESULT_ROOT/analysis.log" 2>&1
