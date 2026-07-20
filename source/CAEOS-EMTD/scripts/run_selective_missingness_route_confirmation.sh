#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-robust-route-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CACHE_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
MANIFEST="$PROJECT_ROOT/selection/selective_missingness_route_confirmation_manifest.json"
RUN_ROOT="$PROJECT_ROOT/runs/selective_missingness_route_confirmation"
EVALUATION_ROOT="$PROJECT_ROOT/results/selective_missingness_route_confirmation/evaluations"
OUTPUT="$PROJECT_ROOT/results/selective_missingness_route_confirmation"
LOG="$OUTPUT/run.log"
LOCK_DIR="$OUTPUT/run.lock.d"

mkdir -p "$OUTPUT" "$EVALUATION_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another selective confirmation is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

verify_sha() {
  local expected="$1" path="$2" actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

verify_protocol() {
  verify_sha bf0d45bdb79da86d9bcfbcc62b7cfc9aedcdaa727c1a3e939b5928d3c8b2e276 "$MANIFEST"
  verify_sha 3aebd7d4faffe3d0579c5e5338c525e5da9fafe3fd04a5dd3cddc78bfd565620 "$PROJECT_ROOT/train_hybrid_open_set.py"
  verify_sha e88f26a2b01f88d5c5467ad732a1e166197d62a345005ad036f037d36782c4f9 "$PROJECT_ROOT/train_modality_dropout_open_set.py"
  verify_sha 59ac433fb29420a228ce3eb484c4da3601e4201bcc4826abc3aef8162bf5cd37 "$PROJECT_ROOT/caeos/modality_dropout.py"
  verify_sha 6d7ed707a7243419f012868ca27c3cdc47e542353a051acf3bad694de0ea9bb3 "$PROJECT_ROOT/evaluate_dual_path_robustness.py"
  verify_sha 9f4c936f8eaf76ea876ddb5efb3e7d6ec5f8bcf60859c62acbe4992cd4b26076 "$PROJECT_ROOT/reevaluate_selective_missingness_route.py"
  verify_sha e1b5b4d69b1c8294b45b1b49850952ee0522a704aee49106e8bda4ec6e35d300 "$PROJECT_ROOT/summarize_selective_missingness_route.py"
  verify_sha d166ce9b0111cdcaab92c09672fd94314158cbd3e1eb2284b18b1625fc5a2fb8 "$PROJECT_ROOT/summarize_selective_missingness_route_confirmation.py"
  "$PYTHON" -c \
    'import sys; from pathlib import Path; from summarize_missingness_routed_expansion import validate_manifest; validate_manifest(Path(sys.argv[1]))' \
    "$MANIFEST"
}

cd "$PROJECT_ROOT"
verify_protocol
for seed in 23 37; do
  test -s "$CACHE_ROOT/seed${seed}_max1000.csv"
done

printf '%s starting frozen 18-pair selective confirmation\n' "$(date -Is)" >> "$LOG"
for pair in ddos_tcp:DDoS_TCP port_scanning:Port_Scanning uploading:Uploading; do
  scenario="${pair%%:*}"
  unknown="${pair##*:}"
  for seed in 23 37; do
    cache="$CACHE_ROOT/seed${seed}_max1000.csv"
    for modality in 0 1 2; do
      run_id="${scenario}_seed${seed}_m${modality}"
      detector="$RUN_ROOT/detector/edge_iiot/$run_id"
      classifier="$RUN_ROOT/classifier/edge_iiot/$run_id"
      mkdir -p "$detector" "$classifier"
      if [[ ! -s "$detector/scores.npz" ]]; then
        "$PYTHON" train_hybrid_open_set.py \
          --csv "$cache" --config configs/edge_iiot.json \
          --unknown-classes "$unknown" --benign-class Normal \
          --max-per-class 1000 --estimators 80 --jobs 4 \
          --split-strategy fingerprint_grouped \
          --risk-selection fixed_cauchy_modality_support_union \
          --risk-policy-name selective_missingness_confirmation_detector_v1 \
          --seed "$seed" --output-dir "$detector" \
          --test-corruption-kind field_missing \
          --test-corruption-modality "$modality" \
          --test-corruption-severity 0.5 \
          --test-corruption-seed 20260717 \
          --train-label-noise 0.0 > "$detector/run.log" 2>&1 &
        detector_pid="$!"
      else
        detector_pid=""
      fi
      if [[ ! -s "$classifier/scores.npz" ]]; then
        "$PYTHON" train_modality_dropout_open_set.py \
          --train-modality-dropout-copies 0 \
          --train-modality-dropout-weight 0.25 \
          --train-field-dropout-severities 0.25,0.5,0.75 \
          --train-dropout-seed 20260717 \
          --csv "$cache" --config configs/edge_iiot.json \
          --unknown-classes "$unknown" --benign-class Normal \
          --max-per-class 1000 --estimators 80 --jobs 4 \
          --split-strategy fingerprint_grouped \
          --risk-selection fixed_cauchy_modality_support_union \
          --risk-policy-name selective_missingness_confirmation_classifier_v1 \
          --seed "$seed" --output-dir "$classifier" \
          --test-corruption-kind field_missing \
          --test-corruption-modality "$modality" \
          --test-corruption-severity 0.5 \
          --test-corruption-seed 20260717 \
          --train-label-noise 0.0 > "$classifier/run.log" 2>&1 &
        classifier_pid="$!"
      else
        classifier_pid=""
      fi
      [[ -z "$detector_pid" ]] || wait "$detector_pid"
      [[ -z "$classifier_pid" ]] || wait "$classifier_pid"
      printf '%s trained %s\n' "$(date -Is)" "$run_id" >> "$LOG"
    done
  done
done

verify_protocol
"$PYTHON" reevaluate_selective_missingness_route.py \
  --detector-root "$RUN_ROOT/detector/edge_iiot" \
  --classifier-root "$RUN_ROOT/classifier/edge_iiot" \
  --manifest "$MANIFEST" \
  --output-root "$EVALUATION_ROOT" >> "$LOG" 2>&1
"$PYTHON" summarize_selective_missingness_route_confirmation.py \
  --root "$EVALUATION_ROOT" \
  --manifest "$MANIFEST" \
  --output "$OUTPUT/summary.json" \
  --markdown-output "$OUTPUT/summary.md" >> "$LOG" 2>&1

detectors="$(find "$RUN_ROOT/detector" -name scores.npz | wc -l)"
classifiers="$(find "$RUN_ROOT/classifier" -name scores.npz | wc -l)"
evaluations="$(find "$EVALUATION_ROOT" -name '*.json' | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
[[ "$detectors" -eq 18 && "$classifiers" -eq 18 && "$evaluations" -eq 18 && "$failures" -eq 0 ]]
touch "$OUTPUT/confirmation_complete"
printf '%s selective confirmation complete training=%s/%s pairs=%s/18 failures=%s\n' \
  "$(date -Is)" "$detectors" "$classifiers" "$evaluations" "$failures" >> "$LOG"
