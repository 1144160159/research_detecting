#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
UPSTREAM="$PROJECT_ROOT/results/strict_v4_postefficiency_claim_chain_v2/chain_complete"
OUTPUT="$PROJECT_ROOT/results/gpu_dataset_full_admission_audit_v1"
LOCK_DIR="$OUTPUT/watcher.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "GPU dataset admission watcher is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$UPSTREAM" ]]; do
  sleep 300
done

idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(pgrep -af 'train_|capture_|benchmark_|run_strict|execute_strict|corruption' | grep -v -E 'wait_and_|pgrep -af' || true)"
  if [[ -z "$gpu_processes" && -z "$experiment_processes" ]]; then
    idle_samples=$((idle_samples + 1))
  else
    idle_samples=0
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done

bash scripts/run_gpu_dataset_full_admission_audit.sh
