#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-counterfactual-gate-20260721}"
UPSTREAM_ROOT="${UPSTREAM_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PREREQUISITE="$UPSTREAM_ROOT/results/mal_tls_geometry_adapter_confirmation_branch/branch_complete"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_counterfactual_conflict_gate_seed201"
RUN_ROOT="$PROJECT_ROOT/runs/mal_tls_counterfactual_conflict_gate_seed201"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "counterfactual conflict-gate watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
if [[ ! -s "$PROTOCOL" ]]; then
  "$PYTHON" create_mal_tls_counterfactual_conflict_gate_protocol.py \
    --dataset /opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/data/malicious_TLS.csv \
    --project-root "$PROJECT_ROOT" --run-root "$RUN_ROOT" --output "$PROTOCOL" \
    > "$RESULT_ROOT/protocol_freeze.log" 2>&1
fi

until [[ -f "$PREREQUISITE" ]]; do sleep 60; done
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  observed="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  if [[ -n "$observed" ]]; then
    idle_samples=0
  else
    idle_samples=$((idle_samples + 1))
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done
bash scripts/run_mal_tls_counterfactual_conflict_gate.sh \
  > "$RESULT_ROOT/execution.log" 2>&1
