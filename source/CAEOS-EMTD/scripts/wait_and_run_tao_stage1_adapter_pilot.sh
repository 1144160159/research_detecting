#!/usr/bin/env bash
set -euo pipefail

BASE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716
ROOT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-tao-adapter-code-20260717
PY=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
OUT="$ROOT/results/tao_stage1_adapter_pilot"
LOG="$ROOT/results/tao_stage1_adapter_pilot_waiter.log"
MANIFEST="$ROOT/selection/tao_stage1_adapter_pilot_manifest.json"

verify_sha() {
  local expected="$1"
  local path="$2"
  local actual
  actual=$(sha256sum "$path" | awk '{print $1}')
  [[ "$actual" == "$expected" ]] || {
    printf 'SHA mismatch path=%s expected=%s actual=%s\n' \
      "$path" "$expected" "$actual" >&2
    exit 1
  }
}

verify_protocol() {
  verify_sha 64a681fb317175e5df87fb2afa7377cbf114561f71b640c7b5fbb92586a07421 "$MANIFEST"
  verify_sha 7a045526613258d9a8ca3b486419084f252a183d0c1dce3c37118f81c4e47f19 "$ROOT/caeos/tao_stage1.py"
  verify_sha fc766120f19d5345034ec78c1027bb8ad5fd659fc018ddaa843c61688a587fe9 "$ROOT/train_neural_open_set.py"
  verify_sha 518f51484e40d3011bd595a20e054d8240a923fed281d9977596b664228050cb "$ROOT/run_neural_baseline_matrix.py"
  verify_sha 0d7bfb13df998752d80261b6d38b291e2166fd3e3fed7331295ba48959f66410 "$ROOT/run_nested_gate_matrix.py"
  verify_sha 148fe920ab95a4a3a49d5fa163f41c0849ee8d6fed32f65abeb852ee6821f22c "$ROOT/summarize_tao_stage1_adapter_pilot.py"
}

mkdir -p "$OUT"
verify_protocol
while true; do
  count=$(find "$BASE/runs/strict_v2_modern_baselines_5seed" -name metrics.json 2>/dev/null | wc -l)
  if [[ "$count" -ge 380 ]]; then
    break
  fi
  printf '%s waiting modern metrics=%s/380\n' "$(date -Iseconds)" "$count" >>"$LOG"
  sleep 120
done

cd "$ROOT"
verify_protocol
COMMON=(
  --models mlp --seeds 7 --workers 1 --epochs 35 --patience 10
  --tao-stage1-adapter --tao-blood-estimators 50
  --edge-iiot-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/edge_iiot
  --edge-iiot-max-per-class 1000
  --nf-cse-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/nf_cse
  --nf-cse-max-per-class 1000
  --ustc-cache-dir /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/strict_v2/ustc_tfc2016
  --ustc-max-per-class 3000
  --output-root "$OUT"
)

"$PY" run_neural_baseline_matrix.py --suite edge_iiot --scenarios fingerprinting "${COMMON[@]}" >>"$LOG" 2>&1
"$PY" run_neural_baseline_matrix.py --suite nf_cse --scenarios bot "${COMMON[@]}" >>"$LOG" 2>&1
"$PY" run_neural_baseline_matrix.py --suite ustc_tfc2016 --scenarios geodo "${COMMON[@]}" >>"$LOG" 2>&1
"$PY" summarize_tao_stage1_adapter_pilot.py \
  --input-root "$OUT" \
  --output "$OUT/summary.json" >>"$LOG" 2>&1
printf '%s pilot_complete\n' "$(date -Iseconds)" >>"$LOG"
