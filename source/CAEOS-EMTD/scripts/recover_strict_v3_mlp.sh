#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v3_pilot_neural"
ARCHIVE_ROOT="$PROJECT_ROOT/runs/strict_v3_pilot_neural_failed_scale_args_20260717"
OUTPUT="$PROJECT_ROOT/results/strict_v3_pilot"
LOG="$OUTPUT/mlp_recovery.log"
SCENARIOS="exploits,fuzzers,reconnaissance,ddos,portscan,web_bruteforce"
FAILED_RELATIVE=(
  cicids2017/ddos_seed7_mlp
  cicids2017/portscan_seed7_mlp
  cicids2017/web_bruteforce_seed7_mlp
  nf_unsw/exploits_seed7_mlp
  nf_unsw/fuzzers_seed7_mlp
  nf_unsw/reconnaissance_seed7_mlp
)

mkdir -p "$OUTPUT"
cd "$PROJECT_ROOT"
if [[ ! -e "$ARCHIVE_ROOT" ]]; then
  for relative in "${FAILED_RELATIVE[@]}"; do
    directory="$RUN_ROOT/$relative"
    [[ -d "$directory" ]]
    [[ ! -e "$directory/metrics.json" ]]
    grep -q -- '--scale-percentile 85 --scale-temperature 1' "$directory/run.log"
  done

  mkdir -p "$ARCHIVE_ROOT/cicids2017" "$ARCHIVE_ROOT/nf_unsw"
  cp "$RUN_ROOT/manifest.json" "$ARCHIVE_ROOT/original_18_task_manifest.json"
  for relative in "${FAILED_RELATIVE[@]}"; do
    mv "$RUN_ROOT/$relative" "$ARCHIVE_ROOT/$relative"
  done
else
  [[ -s "$ARCHIVE_ROOT/original_18_task_manifest.json" ]]
  for relative in "${FAILED_RELATIVE[@]}"; do
    [[ -d "$ARCHIVE_ROOT/$relative" ]]
    [[ ! -e "$RUN_ROOT/$relative" ]]
  done
fi

printf '%s starting six-task MLP recovery\n' "$(date -Is)" >> "$LOG"
"$PYTHON" run_neural_baseline_matrix.py \
  --suite strict_v3 \
  --scenarios "$SCENARIOS" \
  --models mlp \
  --seeds 7 \
  --workers 1 \
  --epochs 0 \
  --patience 10 \
  --nf-unsw-cache-dir "$PROJECT_ROOT/caches/strict_v3/nf_unsw/stratified" \
  --nf-unsw-max-per-class 5000 \
  --cicids2017-cache-dir "$PROJECT_ROOT/caches/strict_v3/cicids2017/stratified" \
  --cicids2017-max-per-class 5000 \
  --output-root runs/strict_v3_pilot_neural >> "$LOG" 2>&1

mv "$RUN_ROOT/manifest.json" "$ARCHIVE_ROOT/recovery_6_task_manifest.json"
cp "$ARCHIVE_ROOT/original_18_task_manifest.json" "$RUN_ROOT/manifest.json"
caeos_count="$(find runs/strict_v3_pilot_caeos -name metrics.json | wc -l)"
neural_count="$(find runs/strict_v3_pilot_neural -name metrics.json | wc -l)"
failures="$(find runs/strict_v3_pilot_caeos runs/strict_v3_pilot_neural -name failure.json | wc -l)"
printf '%s recovery complete caeos=%s/6 neural=%s/18 failures=%s\n' \
  "$(date -Is)" "$caeos_count" "$neural_count" "$failures" >> "$LOG"
[[ "$caeos_count" -eq 6 && "$neural_count" -eq 18 && "$failures" -eq 0 ]]
touch "$OUTPUT/training_complete"
