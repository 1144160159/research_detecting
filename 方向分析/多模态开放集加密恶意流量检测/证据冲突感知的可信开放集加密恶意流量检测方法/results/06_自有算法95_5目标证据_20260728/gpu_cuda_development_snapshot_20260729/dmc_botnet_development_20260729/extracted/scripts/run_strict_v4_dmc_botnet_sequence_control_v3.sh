#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET="$PROJECT/caches/strict_v4_cicids2017_packet_sequences_statistics_v2.npz"
TASK_DIR="$PROJECT/runs/strict_v4_dual_metric_contrastive_botnet_sequence_control_v3"
RESULT_DIR="$PROJECT/results/strict_v4_dual_metric_contrastive_botnet_sequence_control_v3"
GPU_UUID=GPU-a186fd29-e5be-496b-d374-4baeada258ee

if [[ -e "$TASK_DIR" ]]; then
    echo "Refusing to overwrite existing task directory: $TASK_DIR" >&2
    exit 2
fi
mkdir -p "$RESULT_DIR"

"$PYTHON" "$PROJECT/train_strict_v4_dual_metric_contrastive_task_cuda.py" \
    --sequence-dataset "$DATASET" \
    --unknown-family Botnet \
    --seed 29 \
    --output-dir "$TASK_DIR" \
    --required-gpu-uuid "$GPU_UUID" \
    --epochs 80 \
    --batch-size 1024 \
    --statistic-modality-dropout-probability 1.0 \
    >"$RESULT_DIR/train.log" 2>&1

"$PYTHON" "$PROJECT/evaluate_strict_v4_dual_metric_contrastive_pilot.py" \
    --task-dir "$TASK_DIR" \
    --output "$RESULT_DIR/development.json" \
    >"$RESULT_DIR/evaluate.log" 2>&1

printf 'Corrected DMC Botnet sequence control completed at %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
