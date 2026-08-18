#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET="$PROJECT/caches/strict_v4_cicids2017_packet_sequences_statistics_v2.npz"
RUN_ROOT="$PROJECT/runs/strict_v4_fhmm_stable_parallel_smoke_v1"
RESULT_ROOT="$PROJECT/results/strict_v4_fhmm_stable_parallel_smoke_v1"
GPU_UUID=GPU-a186fd29-e5be-496b-d374-4baeada258ee

if [[ -e "$RUN_ROOT" || -e "$RESULT_ROOT" ]]; then
    echo "Refusing to overwrite stable FHMM smoke outputs" >&2
    exit 2
fi
mkdir -p "$RUN_ROOT" "$RESULT_ROOT"

run_member() {
    local model_seed="$1"
    local identity="split53_model${model_seed}"
    OMP_NUM_THREADS=20 MKL_NUM_THREADS=20 \
        "$PYTHON" "$PROJECT/train_strict_v4_fhmm_stable_task_cuda.py" \
        --sequence-dataset "$DATASET" \
        --unknown-family Botnet \
        --split-seed 53 \
        --seed "$model_seed" \
        --output-dir "$RUN_ROOT/$identity" \
        --required-gpu-uuid "$GPU_UUID" \
        --epochs 5 \
        --batch-size 512 \
        --inference-batch-size 4096 \
        --learning-rate 0.002 \
        --weight-decay 0.0001 \
        --statistic-modality-dropout-probability 0.5 \
        --meta-heldout-loss-weight 0.5 \
        --meta-inner-learning-rate 0.02 \
        --meta-inner-gradient-clip-norm 1.0 \
        --gradient-clip-norm 5.0 \
        --meta-episode-rows-per-class 64 \
        >"$RESULT_ROOT/train_${identity}.log" 2>&1
}

pids=()
for model_seed in 201 203 207; do
    run_member "$model_seed" &
    pids+=("$!")
done

statuses=()
for pid in "${pids[@]}"; do
    status=0
    wait "$pid" || status=$?
    statuses+=("$status")
done
for status in "${statuses[@]}"; do
    if [[ "$status" -ne 0 ]]; then
        printf 'Stable FHMM smoke failed: %s\n' "${statuses[*]}" >&2
        exit 1
    fi
done

for model_seed in 201 203 207; do
    identity="split53_model${model_seed}"
    "$PYTHON" "$PROJECT/audit_strict_v4_gpu_execution_resource.py" \
        --gpu-execution "$RUN_ROOT/$identity/gpu_execution.json" \
        --output "$RESULT_ROOT/resource_audit_${identity}.json" \
        --minimum-mean-utilization 50 \
        --maximum-peak-memory-mib 45000 \
        >"$RESULT_ROOT/resource_audit_${identity}.log" 2>&1
done

printf 'Stable FHMM parallel smoke completed at %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
