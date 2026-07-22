#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
MAIN_PROJECT_ROOT="${MAIN_PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
EFFICIENCY_COMPLETE="${EFFICIENCY_COMPLETE:-$MAIN_PROJECT_ROOT/results/strict_v4_final_efficiency_v5/recovery_complete}"
PREREQUISITE="${PREREQUISITE:-$EFFICIENCY_COMPLETE}"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_geometry_preserving_adapter_seed195"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "geometry-preserving adapter watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
if [[ ! -s "$RESULT_ROOT/protocol_manifest.json" ]]; then
  /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python \
    create_mal_tls_geometry_preserving_adapter_protocol.py \
    --dataset /opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/data/malicious_TLS.csv \
    --project-root "$PROJECT_ROOT" \
    --run-root "$PROJECT_ROOT/runs/mal_tls_geometry_preserving_adapter_seed195" \
    --output "$RESULT_ROOT/protocol_manifest.json" \
    > "$RESULT_ROOT/protocol_freeze.log" 2>&1
fi
until [[ -f "$PREREQUISITE" ]]; do sleep 60; done
until [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d')" ]]; do
  sleep 60
done
bash scripts/run_mal_tls_geometry_preserving_adapter.sh \
  > "$RESULT_ROOT/execution.log" 2>&1
