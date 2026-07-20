#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v3-20260717}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
UPSTREAM_MARKER="${UPSTREAM_MARKER:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717/results/external_fusion_confirmation/confirmation.json}"
NF_CACHE="$PROJECT_ROOT/caches/strict_v3/nf_unsw/stratified"
CIC_CACHE="$PROJECT_ROOT/caches/strict_v3/cicids2017/stratified"
OUTPUT_DIR="$PROJECT_ROOT/results/strict_v3_pilot"
LOG="$OUTPUT_DIR/waiter.log"
LOCK_DIR="$OUTPUT_DIR/waiter.lock.d"
MANIFEST="$PROJECT_ROOT/selection/strict_v3_pilot_manifest.json"
EXPECTED_MANIFEST_SHA="438fb986d311f15b85551f1f55c2878c8f34f15790edfa91ea29c2bf49f0e71f"
SCENARIOS="exploits,fuzzers,reconnaissance,ddos,portscan,web_bruteforce"

mkdir -p "$OUTPUT_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf '%s another strict-v3 pilot waiter is active\n' "$(date -Is)" >> "$LOG"
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
verify_sha "1dffee81e52dd32bbe3d40e27ba64cdcbd1b976323f260222452d802f6c3f8bf" \
  run_nested_gate_matrix.py
verify_sha "70b707007667fda22f939d8d8413152e0051d096c3c692683ba39cda61bf9fc5" \
  run_neural_baseline_matrix.py
verify_sha "72f5ce41f66ff9e5271eb59d22ba393cc58209c1bd3001f4a33d40fb3335e1c2" \
  train_hybrid_open_set.py
verify_sha "1ba951a56f2f9caea2b6347697f7b1a921b33ae5daade32183dbb3437d9f5ca4" \
  "$NF_CACHE/seed7_max5000.csv"
verify_sha "bb5ced6383b461e0ba85d58de10828733eb35bedf6427d3fc836eef061286a62" \
  "$CIC_CACHE/seed7_max5000.csv"

while [[ ! -f "$UPSTREAM_MARKER" ]]; do
  printf '%s waiting for strict-v2 finalization and holdout training\n' \
    "$(date -Is)" >> "$LOG"
  sleep 300
done

printf '%s starting strict-v3 CAEOS pilot\n' "$(date -Is)" >> "$LOG"
"$CONDA" run -n py3.9 python run_nested_gate_matrix.py \
  --suite strict_v3 \
  --scenarios "$SCENARIOS" \
  --seeds 7 \
  --workers 1 \
  --model-jobs 8 \
  --estimators 80 \
  --risk-selection fixed_cauchy_modality_support_union \
  --risk-policy-name strict_v3_pilot_current_edge_policy \
  --nf-unsw-cache-dir "$NF_CACHE" \
  --nf-unsw-max-per-class 5000 \
  --cicids2017-cache-dir "$CIC_CACHE" \
  --cicids2017-max-per-class 5000 \
  --output-root runs/strict_v3_pilot_caeos >> "$LOG" 2>&1

printf '%s starting strict-v3 neural baseline pilot\n' "$(date -Is)" >> "$LOG"
"$CONDA" run -n py3.9 python run_neural_baseline_matrix.py \
  --suite strict_v3 \
  --scenarios "$SCENARIOS" \
  --models mlp,opendetect,ronetc \
  --seeds 7 \
  --workers 1 \
  --epochs 0 \
  --patience 10 \
  --nf-unsw-cache-dir "$NF_CACHE" \
  --nf-unsw-max-per-class 5000 \
  --cicids2017-cache-dir "$CIC_CACHE" \
  --cicids2017-max-per-class 5000 \
  --output-root runs/strict_v3_pilot_neural >> "$LOG" 2>&1

caeos_count="$(find runs/strict_v3_pilot_caeos -name metrics.json | wc -l)"
neural_count="$(find runs/strict_v3_pilot_neural -name metrics.json | wc -l)"
failures="$(find runs/strict_v3_pilot_caeos runs/strict_v3_pilot_neural -name failure.json | wc -l)"
printf '%s strict-v3 pilot complete caeos=%s/6 neural=%s/18 failures=%s\n' \
  "$(date -Is)" "$caeos_count" "$neural_count" "$failures" >> "$LOG"
[[ "$caeos_count" -eq 6 && "$neural_count" -eq 18 && "$failures" -eq 0 ]]
touch "$OUTPUT_DIR/training_complete"
