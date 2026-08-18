#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET="$PROJECT/caches/strict_v4_cicids2017_packet_sequences_statistics_v2.npz"
RUN_ROOT="$PROJECT/runs/strict_v4_fhmm_stable_confirmation_v1"
RESULT_ROOT="$PROJECT/results/strict_v4_fhmm_stable_confirmation_v1"
PROTOCOL="$RESULT_ROOT/protocol.json"
GPU_UUID=GPU-a186fd29-e5be-496b-d374-4baeada258ee

if [[ ! -f "$PROTOCOL" ]]; then
    echo "Frozen confirmation protocol is missing" >&2
    exit 2
fi
if find "$RUN_ROOT" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
    echo "Refusing to use non-empty confirmation run root" >&2
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
    OMP_NUM_THREADS=20 MKL_NUM_THREADS=20 \
        "$PYTHON" "$PROJECT/train_strict_v4_fhmm_stable_task_cuda.py" \
        --sequence-dataset "$DATASET" \
        --unknown-family Botnet \
        --split-seed "$split_seed" \
        --seed "$model_seed" \
        --output-dir "$RUN_ROOT/$identity" \
        --required-gpu-uuid "$GPU_UUID" \
        --epochs 120 \
        --batch-size 512 \
        --inference-batch-size 4096 \
        --learning-rate 0.002 \
        --weight-decay 0.0001 \
        --attack-loss-weight 1.0 \
        --knownness-loss-weight 0.2 \
        --family-contrastive-loss-weight 0.10 \
        --attack-contrastive-loss-weight 0.30 \
        --pseudo-mix-loss-weight 0.25 \
        --episodic-margin-loss-weight 0.15 \
        --statistic-modality-dropout-probability 0.5 \
        --meta-heldout-loss-weight 0.5 \
        --meta-inner-learning-rate 0.02 \
        --meta-inner-gradient-clip-norm 1.0 \
        --gradient-clip-norm 5.0 \
        --meta-episode-rows-per-class 64 \
        --contrastive-temperature 0.12 \
        --pseudo-mix-lambda 0.5 \
        --cosine-scale 16.0 \
        --known-similarity-margin 0.35 \
        --pseudo-unknown-similarity-margin 0.15 \
        --early-stopping-patience 24 \
        --minimum-improvement 0.0001 \
        --gpu-sample-interval-seconds 0.2 \
        >"$RESULT_ROOT/train_${identity}.log" 2>&1
}

run_split() {
    local split_seed="$1"
    shift
    local model_seeds=("$@")
    local pids=()
    local model_seed
    for model_seed in "${model_seeds[@]}"; do
        run_member "$split_seed" "$model_seed" &
        pids+=("$!")
    done
    local statuses=()
    local pid
    for pid in "${pids[@]}"; do
        local status=0
        wait "$pid" || status=$?
        statuses+=("$status")
    done
    for status in "${statuses[@]}"; do
        if [[ "$status" -ne 0 ]]; then
            printf 'FHMM-S split %s failed: %s\n' \
                "$split_seed" "${statuses[*]}" >&2
            exit 1
        fi
    done
}

run_split 43 131 137 139
run_split 47 149 151 157

for identity in \
    split43_model131 split43_model137 split43_model139 \
    split47_model149 split47_model151 split47_model157; do
    "$PYTHON" "$PROJECT/audit_strict_v4_gpu_execution_resource.py" \
        --gpu-execution "$RUN_ROOT/$identity/gpu_execution.json" \
        --output "$RESULT_ROOT/resource_audit_${identity}.json" \
        --minimum-mean-utilization 50 \
        --maximum-peak-memory-mib 45000 \
        >"$RESULT_ROOT/resource_audit_${identity}.log" 2>&1
done

"$PYTHON" "$PROJECT/evaluate_strict_v4_fhmm_stable_confirmation.py" \
    --protocol "$PROTOCOL" \
    --repeat 43 \
    "$RUN_ROOT/split43_model131" \
    "$RUN_ROOT/split43_model137" \
    "$RUN_ROOT/split43_model139" \
    --repeat 47 \
    "$RUN_ROOT/split47_model149" \
    "$RUN_ROOT/split47_model151" \
    "$RUN_ROOT/split47_model157" \
    --output "$RESULT_ROOT/evaluation.json" \
    >"$RESULT_ROOT/evaluation.log" 2>&1

"$PYTHON" "$PROJECT/complete_strict_v4_fhmm_stable_confirmation.py" \
    --protocol "$PROTOCOL" \
    --run-root "$RUN_ROOT" \
    --result-root "$RESULT_ROOT" \
    --output "$RESULT_ROOT/completion.json" \
    >"$RESULT_ROOT/completion.log" 2>&1

printf 'FHMM-S confirmation completed at %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
