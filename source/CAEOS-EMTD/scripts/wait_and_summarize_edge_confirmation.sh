#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-dev-20260716}"
CANDIDATE_ROOT="$PROJECT_ROOT/runs/cauchy_modality_union_confirmation_new_seeds_edge_v1"
REFERENCE_ROOT="$PROJECT_ROOT/runs/frozen_density_confirmation_new_seeds_edge_v1"
OUTPUT_DIR="$PROJECT_ROOT/results/cauchy_modality_union_confirmation_new_seeds_edge_v1"
PID_FILE="$PROJECT_ROOT/results/confirmation_logs/edge_reference_confirmation.pid"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"

cd "$PROJECT_ROOT"
printf '%s\n' "$$" > results/confirmation_logs/edge_confirmation_summarizer.pid

while true; do
  metrics=$(find "$REFERENCE_ROOT" -name metrics.json 2>/dev/null | wc -l)
  failures=$(find "$REFERENCE_ROOT" -name failure.json 2>/dev/null | wc -l)
  if (( failures > 0 )); then
    printf 'reference confirmation has %d failures\n' "$failures" >&2
    exit 1
  fi
  if (( metrics == 56 )); then
    break
  fi
  if (( metrics > 56 )); then
    printf 'reference confirmation has unexpected metric count %d\n' "$metrics" >&2
    exit 1
  fi
  reference_pid=$(cat "$PID_FILE" 2>/dev/null || true)
  if [[ -z "$reference_pid" ]] || ! kill -0 "$reference_pid" 2>/dev/null; then
    printf 'reference process stopped at %d/56 without a failure marker\n' "$metrics" >&2
    exit 1
  fi
  sleep 60
done

candidate_metrics=$(find "$CANDIDATE_ROOT" -name metrics.json 2>/dev/null | wc -l)
candidate_failures=$(find "$CANDIDATE_ROOT" -name failure.json 2>/dev/null | wc -l)
if (( candidate_metrics != 56 || candidate_failures != 0 )); then
  printf 'candidate coverage invalid: metrics=%d failures=%d\n' \
    "$candidate_metrics" "$candidate_failures" >&2
  exit 1
fi

"$CONDA" run -n py3.9 python summarize_paired_confirmation.py \
  --reference-root "$REFERENCE_ROOT" \
  --candidate-root "$CANDIDATE_ROOT" \
  --output-dir "$OUTPUT_DIR" \
  --seeds 29,31,41,43 \
  --expected-scenarios 14 \
  --candidate-risk-policy frozen_cauchy_modality_union_v1_edge_devseed7 \
  --reference-risk-policy frozen_suite_conditional_density_v1_edge \
  --bootstrap-repetitions 10000 \
  --bootstrap-seed 20260716
