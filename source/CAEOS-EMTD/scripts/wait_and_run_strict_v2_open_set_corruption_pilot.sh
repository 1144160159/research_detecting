#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-robustness-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
UPSTREAM_MARKER="${UPSTREAM_MARKER:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717/results/strict_v2_24baseline_extended/finalization_complete}"
EDGE_CACHE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
MANIFEST="$PROJECT_ROOT/selection/strict_v2_open_set_corruption_pilot_manifest.json"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v2_open_set_corruption_pilot"
OUTPUT="$PROJECT_ROOT/results/strict_v2_open_set_corruption_pilot"
LOG="$OUTPUT/waiter.log"
LOCK_DIR="$OUTPUT/waiter.lock.d"

EXPECTED_MANIFEST_FILE_SHA="8bd03f37b759452508c9f24b9ded4cca44821807a0dc7d0e7a0731911067042d"
EXPECTED_TRAIN_SHA="9a1b83df0a4a80b8181a345d0263032ade79784611ea0f87c5dbaf7744430c04"
EXPECTED_MATRIX_SHA="0d7bfb13df998752d80261b6d38b291e2166fd3e3fed7331295ba48959f66410"
EXPECTED_SUMMARY_SHA="b1a63f8d8716b37d8636ce684266438a55f0d96af72aeae9412620658522a803"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another corruption-pilot waiter is active\n' "$(date -Is)" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

verify_sha() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

verify_frozen_protocol() {
  verify_sha "$EXPECTED_MANIFEST_FILE_SHA" "$MANIFEST"
  verify_sha "$EXPECTED_TRAIN_SHA" "$PROJECT_ROOT/train_hybrid_open_set.py"
  verify_sha "$EXPECTED_MATRIX_SHA" "$PROJECT_ROOT/run_nested_gate_matrix.py"
  verify_sha "$EXPECTED_SUMMARY_SHA" "$PROJECT_ROOT/summarize_open_set_corruption_pilot.py"
  "$PYTHON" -c \
    'import sys; from pathlib import Path; from summarize_open_set_corruption_pilot import validate_manifest; validate_manifest(Path(sys.argv[1]))' \
    "$MANIFEST"
}

cd "$PROJECT_ROOT"
verify_frozen_protocol
test -s "$EDGE_CACHE/seed7_max1000.csv"

while [[ ! -f "$UPSTREAM_MARKER" ]]; do
  modern="$(find /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_modern_baselines_5seed -name metrics.json 2>/dev/null | wc -l)"
  printf '%s waiting for 24-baseline finalization modern=%s/380\n' \
    "$(date -Is)" "$modern" >> "$LOG"
  sleep 300
done

verify_frozen_protocol
printf '%s starting 39-run open-set corruption pilot\n' "$(date -Is)" >> "$LOG"

while IFS=$'\t' read -r condition kind modality severity label_noise corruption_seed; do
  printf '%s starting condition=%s kind=%s modality=%s severity=%s label_noise=%s\n' \
    "$(date -Is)" "$condition" "$kind" "$modality" "$severity" "$label_noise" >> "$LOG"
  "$PYTHON" run_nested_gate_matrix.py \
    --suite edge_iiot \
    --scenarios fingerprinting,ddos_http,ransomware \
    --seeds 7 \
    --workers 1 \
    --model-jobs 20 \
    --estimators 80 \
    --risk-selection fixed_cauchy_modality_support_union \
    --risk-policy-name strict_v2_open_set_corruption_pilot_v1 \
    --edge-iiot-cache-dir "$EDGE_CACHE" \
    --edge-iiot-max-per-class 1000 \
    --test-corruption-kind "$kind" \
    --test-corruption-modality "$modality" \
    --test-corruption-severity "$severity" \
    --test-corruption-seed "$corruption_seed" \
    --train-label-noise "$label_noise" \
    --output-root "$RUN_ROOT/$condition" >> "$LOG" 2>&1
done < <(
  "$PYTHON" -c \
    'import json,sys; p=json.load(open(sys.argv[1])); [print(c["id"],c["test_corruption_kind"],c["test_corruption_modality"],c["test_corruption_severity"],c["train_label_noise"],c["test_corruption_seed"],sep="\t") for c in p["conditions"]]' \
    "$MANIFEST"
)

verify_frozen_protocol
"$PYTHON" summarize_open_set_corruption_pilot.py \
  --root "$RUN_ROOT" \
  --manifest "$MANIFEST" \
  --output "$OUTPUT/summary.json" \
  --markdown-output "$OUTPUT/summary.md" >> "$LOG" 2>&1

metrics_count="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
[[ "$metrics_count" -eq 39 && "$failures" -eq 0 ]]
touch "$OUTPUT/pilot_complete"
printf '%s corruption pilot complete metrics=%s/39 failures=%s\n' \
  "$(date -Is)" "$metrics_count" "$failures" >> "$LOG"
