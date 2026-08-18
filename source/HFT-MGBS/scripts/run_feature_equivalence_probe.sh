#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 4 ]]; then
  echo "usage: $0 OLD_BINARY NEW_BINARY PCAP OUTPUT_DIR" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
EQUIVALENCE_BATCH_SIZE="${HFT_EQUIVALENCE_BATCH_SIZE:-128}"
EQUIVALENCE_FEATURE_FLUSH_US="${HFT_EQUIVALENCE_FEATURE_FLUSH_US:-60000000}"
OLD_BINARY="$1"
NEW_BINARY="$2"
PCAP="$3"
OUTPUT_DIR="$4"

[[ -x "${OLD_BINARY}" ]] || {
  echo "old binary is unavailable: ${OLD_BINARY}" >&2
  exit 2
}
[[ -x "${NEW_BINARY}" ]] || {
  echo "new binary is unavailable: ${NEW_BINARY}" >&2
  exit 2
}
[[ -f "${PCAP}" ]] || {
  echo "PCAP is unavailable: ${PCAP}" >&2
  exit 2
}
[[ ! -e "${OUTPUT_DIR}" ]] || {
  echo "output directory already exists: ${OUTPUT_DIR}" >&2
  exit 2
}

mkdir -p "${OUTPUT_DIR}"

run_probe() {
  local label="$1"
  local binary="$2"
  local port="$3"
  PYTHONPATH="${CODE_ROOT}" python3 \
    "${CODE_ROOT}/scripts/capture_feature_requests.py" \
    --port "${port}" \
    --output "${OUTPUT_DIR}/${label}_features.json" \
    > "${OUTPUT_DIR}/${label}_collector.stdout.log" \
    2> "${OUTPUT_DIR}/${label}_collector.stderr.log" &
  local collector_pid="$!"
  sleep 0.5
  "${binary}" \
    --pcap "${PCAP}" \
    --gpu-endpoint "127.0.0.1:${port}" \
    --gpu-startup-wait-ms 1000 \
    --gpu-timeout-ms 1000 \
    --metrics "${OUTPUT_DIR}/${label}_metrics.json" \
    --batch-size "${EQUIVALENCE_BATCH_SIZE}" \
    --feature-flush-us "${EQUIVALENCE_FEATURE_FLUSH_US}" \
    --budget-us 5000 \
    --execution-budget-safety-ratio 0.50 \
    > "${OUTPUT_DIR}/${label}_capture.stdout.log" \
    2> "${OUTPUT_DIR}/${label}_capture.stderr.log"
  wait "${collector_pid}"
}

run_probe old "${OLD_BINARY}" 50160
run_probe new_a "${NEW_BINARY}" 50161
run_probe new_b "${NEW_BINARY}" 50162

PYTHONPATH="${CODE_ROOT}" python3 \
  "${CODE_ROOT}/scripts/compare_feature_requests.py" \
  "${OUTPUT_DIR}/old_features.json" \
  "${OUTPUT_DIR}/new_a_features.json" \
  "${OUTPUT_DIR}/base_mapping_comparison.json" \
  --require base

PYTHONPATH="${CODE_ROOT}" python3 \
  "${CODE_ROOT}/scripts/compare_feature_requests.py" \
  "${OUTPUT_DIR}/new_a_features.json" \
  "${OUTPUT_DIR}/new_b_features.json" \
  "${OUTPUT_DIR}/determinism_comparison.json" \
  --require full

(
  cd "${OUTPUT_DIR}"
  sha256sum \
    old_features.json \
    new_a_features.json \
    new_b_features.json \
    old_metrics.json \
    new_a_metrics.json \
    new_b_metrics.json \
    base_mapping_comparison.json \
    determinism_comparison.json \
    > evidence_sha256.txt
)

sha256sum "${OLD_BINARY}" "${NEW_BINARY}" "${PCAP}" \
  > "${OUTPUT_DIR}/input_sha256.txt"
cat "${OUTPUT_DIR}/base_mapping_comparison.json"
cat "${OUTPUT_DIR}/determinism_comparison.json"
