#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET="$PROJECT/caches/strict_v4_cicids2017_packet_sequences_statistics_v2.npz"
RUN_ROOT="$PROJECT/runs/strict_v4_dual_metric_contrastive_botnet_dropout_pilot_v2"
RESULT_ROOT="$PROJECT/results/strict_v4_dual_metric_contrastive_botnet_dropout_pilot_v2"
GPU_UUID=GPU-a186fd29-e5be-496b-d374-4baeada258ee

mkdir -p "$RUN_ROOT" "$RESULT_ROOT"

run_branch() {
    local name="$1"
    local dropout_probability="$2"
    local output_dir="$RUN_ROOT/$name"
    if [[ -e "$output_dir" ]]; then
        echo "Refusing to overwrite existing task directory: $output_dir" >&2
        return 2
    fi
    "$PYTHON" "$PROJECT/train_strict_v4_dual_metric_contrastive_task_cuda.py" \
        --sequence-dataset "$DATASET" \
        --unknown-family Botnet \
        --seed 29 \
        --output-dir "$output_dir" \
        --required-gpu-uuid "$GPU_UUID" \
        --epochs 80 \
        --batch-size 1024 \
        --statistic-modality-dropout-probability "$dropout_probability" \
        >"$RESULT_ROOT/train_${name}.log" 2>&1
}

run_branch dropout_0p5 0.5 &
pid_half=$!
run_branch dropout_1p0 1.0 &
pid_full=$!

status_half=0
status_full=0
wait "$pid_half" || status_half=$?
wait "$pid_full" || status_full=$?
if [[ "$status_half" -ne 0 || "$status_full" -ne 0 ]]; then
    printf 'Training failed: dropout_0p5=%s dropout_1p0=%s\n' \
        "$status_half" "$status_full" >&2
    exit 1
fi

for name in dropout_0p5 dropout_1p0; do
    "$PYTHON" "$PROJECT/evaluate_strict_v4_dual_metric_contrastive_pilot.py" \
        --task-dir "$RUN_ROOT/$name" \
        --output "$RESULT_ROOT/${name}.json" \
        >"$RESULT_ROOT/evaluate_${name}.log" 2>&1
done

printf 'DMC Botnet dropout pilot completed at %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
