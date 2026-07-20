#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUTPUT_ROOT="$PROJECT_ROOT/runs/efc_strict_v2_pilot"
RESULT_ROOT="$PROJECT_ROOT/results/efc_strict_v2_pilot"
LOG="$RESULT_ROOT/pilot.log"

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

mkdir -p "$OUTPUT_ROOT" "$RESULT_ROOT"
cd "$PROJECT_ROOT"
verify_sha "20fa086decfedd369d134d8f5b7c1ad55ff2014763893d6f720a936c0c101527" train_efc_open_set.py
verify_sha "f75c67109f75755e549e2cfcf7407c3496c8b56280a3abb181baea4d128175ec" run_neural_baseline_matrix.py
verify_sha "afe62f211a467716d52986fa95095031c7b19ef3f2d1d065a7c9088d6fe8dfec" selection/efc_strict_v2_pilot_manifest.json
verify_sha "1100919c47f121ce405896ac118a0c8d6bcc9c41735911e8354308a5478def2e" /opt/data/private/wangwt/ParkAttackKE/third_party/EFC-package-2b935be.tar.gz
verify_sha "26dcfa8039d910c2897eaebc70218ed75909c1d337664bc2c27c52d2c179dec0" /opt/data/private/wangwt/ParkAttackKE/third_party/wheels/efc-0.1.0-cp39-cp39-linux_x86_64.whl
"$PYTHON" -c 'import efc; assert efc.__version__ == "0.1.0"'

"$PYTHON" run_neural_baseline_matrix.py \
  --suite extended \
  --scenarios fingerprinting,bot,geodo \
  --models efc \
  --seeds 7 \
  --workers 1 \
  --efc-jobs 8 \
  --edge-iiot-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot \
  --nf-cse-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse \
  --ustc-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016 \
  --output-root "$OUTPUT_ROOT" > "$LOG" 2>&1

metrics="$(find "$OUTPUT_ROOT" -name metrics.json -type f | wc -l)"
scores="$(find "$OUTPUT_ROOT" -name scores.npz -type f | wc -l)"
failures="$(find "$OUTPUT_ROOT" -name failure.json -type f | wc -l)"
"$PYTHON" -c \
  'import json,sys; p=json.load(open(sys.argv[1])); assert p["state"] == "complete"; assert p["completed"] + p["skipped"] == 3; assert p["failed"] == 0' \
  "$OUTPUT_ROOT/manifest.json"
[[ "$metrics" -eq 3 && "$scores" -eq 3 && "$failures" -eq 0 ]]
touch "$RESULT_ROOT/pilot_complete"
printf 'EFC strict-v2 pilot complete metrics=%s/3 scores=%s/3 failures=%s\n' \
  "$metrics" "$scores" "$failures" >> "$LOG"
