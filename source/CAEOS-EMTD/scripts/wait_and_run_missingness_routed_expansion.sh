#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-robust-route-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
UPSTREAM_MARKER="${UPSTREAM_MARKER:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-robustness-20260717/results/strict_v2_open_set_corruption_pilot/pilot_complete}"
CACHE_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
MANIFEST="$PROJECT_ROOT/selection/missingness_routed_expansion_manifest.json"
RUN_ROOT="$PROJECT_ROOT/runs/missingness_routed_expansion"
EVALUATION_ROOT="$PROJECT_ROOT/results/missingness_routed_expansion/evaluations"
OUTPUT="$PROJECT_ROOT/results/missingness_routed_expansion"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"

EXPECTED_MANIFEST_FILE_SHA="292e7e832754c4ee1d13f482e4bc7ac03bb2a07ef4d66bc158e85e7add5d1d39"
EXPECTED_TRAIN_SHA="3aebd7d4faffe3d0579c5e5338c525e5da9fafe3fd04a5dd3cddc78bfd565620"
EXPECTED_DROPOUT_SHA="59ac433fb29420a228ce3eb484c4da3601e4201bcc4826abc3aef8162bf5cd37"
EXPECTED_WRAPPER_SHA="e88f26a2b01f88d5c5467ad732a1e166197d62a345005ad036f037d36782c4f9"
EXPECTED_EVALUATOR_SHA="ee72d4dee9d0994d96b35617d656ff4aedad426377034917a62142c6b5ecef4b"
EXPECTED_SUMMARY_SHA="14677044cce03af39bcb77b090fb563dbd468ad0a35b82e6cc6045235e3eaae2"

mkdir -p "$OUTPUT" "$EVALUATION_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another routed-expansion waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

verify_sha() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' "$path" "$expected" "$actual" >&2
    exit 1
  }
}

verify_protocol() {
  verify_sha "$EXPECTED_MANIFEST_FILE_SHA" "$MANIFEST"
  verify_sha "$EXPECTED_TRAIN_SHA" "$PROJECT_ROOT/train_hybrid_open_set.py"
  verify_sha "$EXPECTED_DROPOUT_SHA" "$PROJECT_ROOT/caeos/modality_dropout.py"
  verify_sha "$EXPECTED_WRAPPER_SHA" "$PROJECT_ROOT/train_modality_dropout_open_set.py"
  verify_sha "$EXPECTED_EVALUATOR_SHA" "$PROJECT_ROOT/evaluate_dual_path_robustness.py"
  verify_sha "$EXPECTED_SUMMARY_SHA" "$PROJECT_ROOT/summarize_missingness_routed_expansion.py"
  "$PYTHON" -c \
    'import sys; from pathlib import Path; from summarize_missingness_routed_expansion import validate_manifest; validate_manifest(Path(sys.argv[1]))' \
    "$MANIFEST"
}

cd "$PROJECT_ROOT"
verify_protocol
for seed in 7 11 19; do
  test -s "$CACHE_ROOT/seed${seed}_max1000.csv"
done

while [[ ! -f "$UPSTREAM_MARKER" ]]; do
  pilot_metrics=0
  if [[ -d /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-robustness-20260717/runs/strict_v2_open_set_corruption_pilot ]]; then
    pilot_metrics="$(find /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-robustness-20260717/runs/strict_v2_open_set_corruption_pilot -name metrics.json | wc -l)"
  fi
  printf '%s waiting for base corruption pilot metrics=%s/39\n' \
    "$(date -Is)" "$pilot_metrics" >> "$LOG"
  sleep 300
done

verify_protocol
printf '%s starting 27-pair routed robustness expansion\n' "$(date -Is)" >> "$LOG"

for pair in ddos_udp:DDoS_UDP mitm:MITM xss:XSS; do
  scenario="${pair%%:*}"
  unknown="${pair##*:}"
  for seed in 7 11 19; do
    cache="$CACHE_ROOT/seed${seed}_max1000.csv"
    for modality in 0 1 2; do
      run_id="${scenario}_seed${seed}_m${modality}"
      detector="$RUN_ROOT/detector/edge_iiot/$run_id"
      classifier="$RUN_ROOT/classifier/edge_iiot/$run_id"
      mkdir -p "$detector" "$classifier"
      "$PYTHON" train_hybrid_open_set.py \
        --csv "$cache" --config configs/edge_iiot.json \
        --unknown-classes "$unknown" --benign-class Normal \
        --max-per-class 1000 --estimators 80 --jobs 4 \
        --split-strategy fingerprint_grouped \
        --risk-selection fixed_cauchy_modality_support_union \
        --risk-policy-name missingness_routed_expansion_detector_v1 \
        --seed "$seed" --output-dir "$detector" \
        --test-corruption-kind field_missing \
        --test-corruption-modality "$modality" \
        --test-corruption-severity 0.5 \
        --test-corruption-seed 20260717 \
        --train-label-noise 0.0 > "$detector/run.log" 2>&1 &
      detector_pid="$!"
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
        --risk-policy-name missingness_routed_expansion_classifier_v1 \
        --seed "$seed" --output-dir "$classifier" \
        --test-corruption-kind field_missing \
        --test-corruption-modality "$modality" \
        --test-corruption-severity 0.5 \
        --test-corruption-seed 20260717 \
        --train-label-noise 0.0 > "$classifier/run.log" 2>&1 &
      classifier_pid="$!"
      wait "$detector_pid"
      wait "$classifier_pid"
      "$PYTHON" evaluate_dual_path_robustness.py \
        --detector-run "$detector" \
        --classifier-run "$classifier" \
        --prediction-routing missingness \
        --output "$EVALUATION_ROOT/$run_id.json" >> "$LOG" 2>&1
      printf '%s completed %s\n' "$(date -Is)" "$run_id" >> "$LOG"
    done
  done
done

verify_protocol
"$PYTHON" summarize_missingness_routed_expansion.py \
  --root "$EVALUATION_ROOT" \
  --manifest "$MANIFEST" \
  --output "$OUTPUT/summary.json" \
  --markdown-output "$OUTPUT/summary.md" >> "$LOG" 2>&1

evaluations="$(find "$EVALUATION_ROOT" -name '*.json' | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
[[ "$evaluations" -eq 27 && "$failures" -eq 0 ]]
touch "$OUTPUT/expansion_complete"
printf '%s routed expansion complete pairs=%s/27 failures=%s\n' \
  "$(date -Is)" "$evaluations" "$failures" >> "$LOG"
