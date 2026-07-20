#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
RUN_ROOT="${RUN_ROOT:-$PROJECT_ROOT/runs/external_fusion_confirmation_caeos}"
MANIFEST="${MANIFEST:-$PROJECT_ROOT/selection/entropy_cauchy_fusion_manifest.json}"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/results/entropy_cauchy_fusion_confirmation}"
EXTERNAL_MARKER="${EXTERNAL_MARKER:-$PROJECT_ROOT/results/external_fusion_confirmation/confirmation.json}"
LOG="$OUTPUT_DIR/waiter.log"
LOCK_DIR="$OUTPUT_DIR/waiter.lock.d"

mkdir -p "$OUTPUT_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another fusion confirmation waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

while true; do
  completed=0
  failures=0
  if [[ -d "$RUN_ROOT" ]]; then
    completed="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
    failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
  fi
  marker=0
  [[ -f "$EXTERNAL_MARKER" ]] && marker=1
  printf '%s caeos_holdout=%s/56 failures=%s external_marker=%s\n' \
    "$(date -Is)" "$completed" "$failures" "$marker" >> "$LOG"
  [[ "$failures" -eq 0 ]] || exit 1
  if [[ "$completed" -eq 56 && "$marker" -eq 1 ]]; then
    break
  fi
  sleep 300
done

printf '%s starting frozen entropy-Cauchy fusion confirmation\n' \
  "$(date -Is)" >> "$LOG"
cd "$PROJECT_ROOT"
"$CONDA" run -n py3.9 python confirm_entropy_cauchy_fusion.py \
  --root runs/external_fusion_confirmation_caeos \
  --selection-manifest "$MANIFEST" \
  --output-dir results/entropy_cauchy_fusion_confirmation \
  --expected-scenarios 14 \
  --known-acceptance 0.95 \
  --expected-selected-risk cauchy_modality_support_union \
  --expected-risk-policy confirmed_cauchy_modality_union_v1_edge_external_fusion_holdout \
  --bootstrap-repetitions 10000 \
  --bootstrap-seed 20260717 >> "$LOG" 2>&1
printf '%s entropy-Cauchy fusion confirmation complete\n' "$(date -Is)" >> "$LOG"
