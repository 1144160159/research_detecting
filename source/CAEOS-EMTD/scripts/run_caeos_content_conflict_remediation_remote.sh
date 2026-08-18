#!/usr/bin/env bash
set -euo pipefail

PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
CODE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/paper_protocols/caeos_paper_closure_v3
DATA=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5
CONTROL="$DATA/_control/paper_protocol_v1/content_conflict_remediation"
SCRATCH=/tmp/caeos_content_conflict_remediation_v1
CICIOT_SCRATCH=/tmp/caeos_ciciot2023_duplicate_audit_v2
CICIOT_TRANSACTION="$DATA/_control/sample_id_repairs/ciciot2023/sample_id_v2_20260814T104500Z"
TEMPLATE="$DATA/_control/feature_extraction/completion.lane3.ciciot2022.json"
PID_FILE="$CONTROL/queue.pid"
LOG_FILE="$CONTROL/queue.log"

mkdir -p "$CONTROL" "$SCRATCH"
if [[ -s "$PID_FILE" ]]; then
    old_pid=$(cat "$PID_FILE")
    if kill -0 "$old_pid" 2>/dev/null; then
        echo "content conflict remediation already running: $old_pid" >&2
        exit 2
    fi
fi

nohup setsid "$PYTHON" -u "$CODE/run_caeos_content_conflict_remediation.py" \
    --output-root "$DATA" \
    --code-root "$CODE" \
    --scratch-root "$SCRATCH" \
    --ciciot-audit-scratch "$CICIOT_SCRATCH" \
    --ciciot-transaction "$CICIOT_TRANSACTION" \
    --completion-template "$TEMPLATE" \
    --workers 16 \
    --buckets 256 \
    >>"$LOG_FILE" 2>&1 </dev/null &
pid=$!
printf '%s\n' "$pid" >"$PID_FILE"
echo "started content conflict remediation pid=$pid workers=16"
