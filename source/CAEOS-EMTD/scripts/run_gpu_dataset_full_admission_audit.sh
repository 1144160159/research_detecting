#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PARENT="$PROJECT_ROOT/results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json"
PROTOCOL_ROOT="$PROJECT_ROOT/results/gpu_dataset_admission_execution_protocol_v1"
OUTPUT="$PROJECT_ROOT/results/gpu_dataset_full_admission_audit_v1"
WORK="$PROJECT_ROOT/runs/gpu_dataset_full_admission_audit_v1"
EXECUTION_PROTOCOL="$PROTOCOL_ROOT/protocol.json"
RESULT="$OUTPUT/admission_audit.json"
LOCK_DIR="$OUTPUT/run.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$PROTOCOL_ROOT" "$OUTPUT" "$WORK"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "GPU dataset admission audit is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

if [[ ! -s "$EXECUTION_PROTOCOL" ]]; then
  "$PYTHON" create_gpu_dataset_admission_execution_protocol.py \
    --parent-protocol "$PARENT" \
    --scanner audit_gpu_dataset_admission.py \
    --lsnm-config configs/lsnm2024_external.json \
    --cic-config configs/cicids2017_strict.json \
    --runner scripts/run_gpu_dataset_full_admission_audit.sh \
    --result-path "$RESULT" \
    --output "$EXECUTION_PROTOCOL" \
    > "$PROTOCOL_ROOT/freeze.log" 2>&1
fi

"$PYTHON" - "$EXECUTION_PROTOCOL" <<'PY'
import json, sys
from create_gpu_dataset_admission_execution_protocol import verify_protocol

verify_protocol(json.load(open(sys.argv[1], encoding="utf-8")))
PY

if [[ -s "$RESULT" && -f "$OUTPUT/audit_complete" ]]; then
  echo "GPU dataset admission audit is already complete"
  exit 0
fi

ionice -c3 nice -n 15 "$PYTHON" audit_gpu_dataset_admission.py \
  --protocol "$PARENT" \
  --lsnm-config configs/lsnm2024_external.json \
  --cic-config configs/cicids2017_strict.json \
  --work-dir "$WORK" \
  --output-dir "$OUTPUT" \
  > "$OUTPUT/run.log" 2>&1
