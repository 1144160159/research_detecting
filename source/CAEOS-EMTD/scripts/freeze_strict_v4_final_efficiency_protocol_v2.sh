#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUTPUT="$PROJECT_ROOT/results/strict_v4_final_efficiency_protocol_v2"
EXTERNAL_ROOT="$PROJECT_ROOT/results/strict_v4_external_confirmation"
EXTERNAL_MARKER="$EXTERNAL_ROOT/confirmation_complete"
LOCK_DIR="$OUTPUT/freeze.lock.d"

test -f "$EXTERNAL_MARKER" || {
  echo "external comparator confirmation is incomplete" >&2
  exit 3
}
mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "efficiency v2 protocol freeze already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
if [[ -s "$OUTPUT/protocol_manifest.json" ]]; then
  "$PYTHON" -c \
    'import json,sys; from create_strict_v4_external_confirmation_protocol import canonical_hash; p=json.load(open(sys.argv[1])); assert p["schema_version"]=="strict_v4_final_efficiency_protocol_v2"; assert p["manifest_sha256"]==canonical_hash(p); assert p["efficiency_metrics_observed_at_freeze"]==0' \
    "$OUTPUT/protocol_manifest.json"
else
  "$PYTHON" create_strict_v4_final_efficiency_protocol_v2.py \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --v1-protocol results/strict_v4_final_efficiency_protocol/protocol_manifest.json \
    --readiness results/strict_v4_final_efficiency_readiness_seed7/readiness.json \
    --decision results/strict_v4_optimal_self_algorithm/decision.json \
    --external-confirmation "$EXTERNAL_ROOT/confirmation.json" \
    --candidate-implementation train_hybrid_open_set.py \
    --comparator-implementation train_neural_open_set.py \
    --candidate-runtime caeos/pairwise_runtime.py \
    --candidate-capture capture_pairwise_runtime.py \
    --candidate-benchmark benchmark_pairwise_runtime.py \
    --comparator-runtime caeos/open_detect_runtime.py \
    --comparator-capture capture_opendetect_runtime.py \
    --comparator-training-capture capture_opendetect_training_runtime.py \
    --comparator-benchmark benchmark_opendetect_runtime.py \
    --paired-runner run_strict_v4_final_efficiency_v2.py \
    --execution-plan-creator create_strict_v4_final_efficiency_execution_plan_v2.py \
    --execution-plan-executor execute_strict_v4_final_efficiency_plan_v2.py \
    --efficiency-summarizer summarize_strict_v4_final_efficiency_v2.py \
    --output-dir "$OUTPUT" > "$OUTPUT/freeze.log" 2>&1
fi
test -s "$OUTPUT/protocol_manifest.json"
touch "$OUTPUT/protocol_complete"
