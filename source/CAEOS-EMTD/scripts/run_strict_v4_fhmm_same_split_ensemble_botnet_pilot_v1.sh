#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET="$PROJECT/caches/strict_v4_cicids2017_packet_sequences_statistics_v2.npz"
RUN_ROOT="$PROJECT/runs/strict_v4_fhmm_same_split_ensemble_botnet_pilot_v1"
RESULT_ROOT="$PROJECT/results/strict_v4_fhmm_same_split_ensemble_botnet_pilot_v1"
PROTOCOL="$RESULT_ROOT/protocol.json"
GPU_UUID=GPU-a186fd29-e5be-496b-d374-4baeada258ee

if [[ ! -f "$PROTOCOL" ]]; then
    echo "Frozen protocol is missing: $PROTOCOL" >&2
    exit 2
fi
if find "$RUN_ROOT" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
    echo "Refusing to use non-empty run root: $RUN_ROOT" >&2
    exit 2
fi
if find "$RESULT_ROOT" -mindepth 1 \
    ! -name protocol.json ! -name protocol_creation.log \
    -print -quit 2>/dev/null | grep -q .; then
    echo "Refusing to use result root containing post-protocol artifacts" >&2
    exit 2
fi
mkdir -p "$RUN_ROOT"

run_member() {
    local split_seed="$1"
    local model_seed="$2"
    local identity="split${split_seed}_model${model_seed}"
    local output_dir="$RUN_ROOT/$identity"
    OMP_NUM_THREADS=20 MKL_NUM_THREADS=20 \
        "$PYTHON" "$PROJECT/train_strict_v4_fhmm_same_split_member_cuda.py" \
        --split-seed "$split_seed" \
        --sequence-dataset "$DATASET" \
        --unknown-family Botnet \
        --seed "$model_seed" \
        --output-dir "$output_dir" \
        --required-gpu-uuid "$GPU_UUID" \
        --epochs 120 \
        --batch-size 512 \
        --inference-batch-size 4096 \
        --learning-rate 0.002 \
        --weight-decay 0.0001 \
        --statistic-modality-dropout-probability 0.5 \
        --meta-heldout-loss-weight 1.0 \
        --meta-inner-learning-rate 0.05 \
        --meta-episode-rows-per-class 64 \
        >"$RESULT_ROOT/train_${identity}.log" 2>&1
}

audit_member() {
    local split_seed="$1"
    local model_seed="$2"
    local identity="split${split_seed}_model${model_seed}"
    "$PYTHON" "$PROJECT/audit_strict_v4_gpu_execution_resource.py" \
        --gpu-execution "$RUN_ROOT/$identity/gpu_execution.json" \
        --output "$RESULT_ROOT/resource_audit_${identity}.json" \
        --minimum-mean-utilization 50 \
        --maximum-peak-memory-mib 45000 \
        >"$RESULT_ROOT/resource_audit_${identity}.log" 2>&1
}

run_split() {
    local split_seed="$1"
    shift
    local model_seeds=("$@")
    local pids=()
    local statuses=()
    local model_seed
    for model_seed in "${model_seeds[@]}"; do
        run_member "$split_seed" "$model_seed" &
        pids+=("$!")
    done
    local index
    for index in "${!pids[@]}"; do
        local status=0
        wait "${pids[$index]}" || status=$?
        statuses+=("$status")
    done
    for status in "${statuses[@]}"; do
        if [[ "$status" -ne 0 ]]; then
            printf 'FHMM split %s member training failed: %s\n' \
                "$split_seed" "${statuses[*]}" >&2
            exit 1
        fi
    done
    for model_seed in "${model_seeds[@]}"; do
        audit_member "$split_seed" "$model_seed"
    done
    "$PYTHON" "$PROJECT/evaluate_strict_v4_fhmm_same_split_ensemble.py" \
        --member-dir "$RUN_ROOT/split${split_seed}_model${model_seeds[0]}" \
        --member-dir "$RUN_ROOT/split${split_seed}_model${model_seeds[1]}" \
        --member-dir "$RUN_ROOT/split${split_seed}_model${model_seeds[2]}" \
        --output "$RESULT_ROOT/evaluation_split${split_seed}.json" \
        >"$RESULT_ROOT/evaluation_split${split_seed}.log" 2>&1
}

run_split 37 101 103 107
run_split 41 109 113 127

"$PYTHON" \
    "$PROJECT/complete_strict_v4_fhmm_same_split_ensemble_botnet_pilot.py" \
    --protocol "$PROTOCOL" \
    --run-root "$RUN_ROOT" \
    --result-root "$RESULT_ROOT" \
    --output "$RESULT_ROOT/completion.json" \
    >"$RESULT_ROOT/completion.log" 2>&1

printf 'FHMM same-split Botnet pilot completed at %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
