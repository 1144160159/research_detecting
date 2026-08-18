#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET="$PROJECT/caches/strict_v4_cicids2017_packet_sequences_statistics_v2.npz"
RUN_ROOT="$PROJECT/runs/strict_v4_family_heldout_meta_botnet_pilot_v1"
RESULT_ROOT="$PROJECT/results/strict_v4_family_heldout_meta_botnet_pilot_v1"
GPU_UUID=GPU-a186fd29-e5be-496b-d374-4baeada258ee

mkdir -p "$RUN_ROOT" "$RESULT_ROOT"

run_task() {
    local seed="$1"
    local output_dir="$RUN_ROOT/unknown_botnet_seed${seed}"
    if [[ -e "$output_dir" ]]; then
        echo "Refusing to overwrite existing task directory: $output_dir" >&2
        return 2
    fi
    "$PYTHON" "$PROJECT/train_strict_v4_family_heldout_meta_task_cuda.py" \
        --sequence-dataset "$DATASET" \
        --unknown-family Botnet \
        --seed "$seed" \
        --output-dir "$output_dir" \
        --required-gpu-uuid "$GPU_UUID" \
        --epochs 120 \
        --batch-size 512 \
        --learning-rate 0.002 \
        --statistic-modality-dropout-probability 0.5 \
        --meta-heldout-loss-weight 1.0 \
        --meta-inner-learning-rate 0.05 \
        --meta-episode-rows-per-class 64 \
        >"$RESULT_ROOT/train_seed${seed}.log" 2>&1
}

run_task 29 &
pid_29=$!
run_task 31 &
pid_31=$!

status_29=0
status_31=0
wait "$pid_29" || status_29=$?
wait "$pid_31" || status_31=$?
if [[ "$status_29" -ne 0 || "$status_31" -ne 0 ]]; then
    printf 'Botnet pilot training failed: seed29=%s seed31=%s\n' \
        "$status_29" "$status_31" >&2
    exit 1
fi

for seed in 29 31; do
    "$PYTHON" "$PROJECT/audit_strict_v4_gpu_execution_resource.py" \
        --gpu-execution \
        "$RUN_ROOT/unknown_botnet_seed${seed}/gpu_execution.json" \
        --output "$RESULT_ROOT/resource_audit_seed${seed}.json" \
        --minimum-mean-utilization 50 \
        --maximum-peak-memory-mib 45000 \
        >"$RESULT_ROOT/resource_audit_seed${seed}.log" 2>&1
    "$PYTHON" "$PROJECT/evaluate_strict_v4_family_heldout_meta_pilot.py" \
        --task-dir "$RUN_ROOT/unknown_botnet_seed${seed}" \
        --output "$RESULT_ROOT/evaluation_seed${seed}.json" \
        >"$RESULT_ROOT/evaluation_seed${seed}.log" 2>&1
done

printf 'FHMM Botnet pilot completed at %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
