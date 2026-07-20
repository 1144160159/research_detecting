#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-classical-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
UPSTREAM_MARKER="${UPSTREAM_MARKER:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717/results/strict_v3_pilot/training_complete}"
EDGE_CACHE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot"
NF_CACHE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse"
USTC_CACHE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016"
MANIFEST="$PROJECT_ROOT/selection/strict_v2_classical_ood_manifest.json"
EXPECTED_MANIFEST_SHA="6c12df4c339130676f22589f5f73f9c4467613300d3e10cef61d1fd21473a80e"
OUTPUT_DIR="$PROJECT_ROOT/results/strict_v2_classical_ood"
RUN_ROOT="$PROJECT_ROOT/runs/strict_v2_classical_ood_5seed"
LOG="$OUTPUT_DIR/waiter.log"
LOCK_DIR="$OUTPUT_DIR/waiter.lock.d"

mkdir -p "$OUTPUT_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another classical OOD waiter is active\n' "$(date -Is)" >> "$LOG"
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

cd "$PROJECT_ROOT"
verify_sha "$EXPECTED_MANIFEST_SHA" "$MANIFEST"
verify_sha "3314a9f013ac9170d89a4005d7558f71f39c13ee0356c1ae54fd22914b1de995" \
  train_classical_ood.py
verify_sha "c3da514f52aeb8d8103a84926a168cf5731e0da7c5518542f601c5e35e945eee" \
  run_neural_baseline_matrix.py
verify_sha "1dffee81e52dd32bbe3d40e27ba64cdcbd1b976323f260222452d802f6c3f8bf" \
  run_nested_gate_matrix.py
for seed in 7 11 19 23 37; do
  test -s "$EDGE_CACHE/seed${seed}_max1000.csv"
  test -s "$NF_CACHE/seed${seed}_max1000.csv"
  test -s "$USTC_CACHE/seed${seed}_max3000.csv"
done

while [[ ! -f "$UPSTREAM_MARKER" ]]; do
  printf '%s waiting for strict-v3 pilot training\n' "$(date -Is)" >> "$LOG"
  sleep 300
done

# Recheck the frozen protocol after the potentially long queue wait.
verify_sha "$EXPECTED_MANIFEST_SHA" "$MANIFEST"
verify_sha "3314a9f013ac9170d89a4005d7558f71f39c13ee0356c1ae54fd22914b1de995" \
  train_classical_ood.py
verify_sha "c3da514f52aeb8d8103a84926a168cf5731e0da7c5518542f601c5e35e945eee" \
  run_neural_baseline_matrix.py
verify_sha "1dffee81e52dd32bbe3d40e27ba64cdcbd1b976323f260222452d802f6c3f8bf" \
  run_nested_gate_matrix.py

printf '%s starting real classical OOD smoke\n' "$(date -Is)" >> "$LOG"
"$CONDA" run -n py3.9 python run_neural_baseline_matrix.py \
  --suite edge_iiot \
  --scenarios fingerprinting \
  --models classical_ood \
  --seeds 7 \
  --workers 1 \
  --epochs 0 \
  --edge-iiot-cache-dir "$EDGE_CACHE" \
  --edge-iiot-max-per-class 1000 \
  --output-root runs/strict_v2_classical_ood_5seed >> "$LOG" 2>&1

"$CONDA" run -n py3.9 python - <<'PY' >> "$LOG" 2>&1
import json
from pathlib import Path

path = Path("runs/strict_v2_classical_ood_5seed/edge_iiot/fingerprinting_seed7_classical_ood/metrics.json")
payload = json.loads(path.read_text(encoding="utf-8"))
expected = {
    "isolation_forest",
    "one_class_svm",
    "local_outlier_factor",
    "pca_reconstruction",
}
if set(payload.get("reports", {})) != expected:
    raise SystemExit("classical smoke report set mismatch")
selection = payload.get("selection_evidence", {})
if selection.get("unknown_or_test_labels_used_for_training") is not False:
    raise SystemExit("classical smoke training leakage guard failed")
if selection.get("unknown_or_test_labels_used_for_thresholds") is not False:
    raise SystemExit("classical smoke threshold leakage guard failed")
print("classical smoke audit PASS")
PY

printf '%s classical OOD smoke passed; starting 190-run matrix\n' \
  "$(date -Is)" >> "$LOG"
"$CONDA" run -n py3.9 python run_neural_baseline_matrix.py \
  --suite extended \
  --scenarios all \
  --models classical_ood \
  --seeds 7,11,19,23,37 \
  --workers 1 \
  --epochs 0 \
  --edge-iiot-cache-dir "$EDGE_CACHE" \
  --edge-iiot-max-per-class 1000 \
  --nf-cse-cache-dir "$NF_CACHE" \
  --nf-cse-max-per-class 1000 \
  --ustc-cache-dir "$USTC_CACHE" \
  --ustc-max-per-class 3000 \
  --output-root runs/strict_v2_classical_ood_5seed >> "$LOG" 2>&1

metrics_count="$(find "$RUN_ROOT" -name metrics.json | wc -l)"
failures="$(find "$RUN_ROOT" -name failure.json | wc -l)"
printf '%s classical OOD matrix complete metrics=%s/190 failures=%s\n' \
  "$(date -Is)" "$metrics_count" "$failures" >> "$LOG"
[[ "$metrics_count" -eq 190 && "$failures" -eq 0 ]]
touch "$OUTPUT_DIR/matrix_complete"
