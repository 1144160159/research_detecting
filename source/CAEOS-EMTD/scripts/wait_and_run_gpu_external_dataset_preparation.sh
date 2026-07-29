#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
AUDIT_ROOT="$PROJECT_ROOT/results/gpu_dataset_full_admission_audit_v1"
RESULT_ROOT="$PROJECT_ROOT/results/gpu_external_dataset_preparation_v1"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "GPU external dataset preparation watcher is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$AUDIT_ROOT/audit_complete" ]]; do
  sleep 300
done
if [[ ! -f "$AUDIT_ROOT/admission_passed" ]]; then
  touch "$RESULT_ROOT/blocked_by_admission_failure"
  exit 0
fi
bash scripts/run_gpu_external_dataset_preparation.sh
