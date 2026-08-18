#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 || "$#" -gt 2 ]]; then
  echo "usage: $0 SOURCE_PCAP [MAX_PACKETS]" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
GPU_ENDPOINT="${GPU_ENDPOINT:-listen://0.0.0.0:50052}"
GPU_TIMEOUT_MS="${GPU_TIMEOUT_MS:-150}"
BATCH_SIZE="${BATCH_SIZE:-128}"
FEATURE_FLUSH_US="${FEATURE_FLUSH_US:-1000}"
SOURCE_PCAP="$1"
MAX_PACKETS="${2:-0}"

if [[ ! -f "${SOURCE_PCAP}" ]]; then
  echo "SOURCE_PCAP is not a file: ${SOURCE_PCAP}" >&2
  exit 3
fi

input_sha="$(sha256sum "${SOURCE_PCAP}" | awk '{print $1}')"
run_id="hft_replay_$(date -u +%Y%m%dT%H%M%SZ)"
run_dir="${REPLAY_ROOT}/${run_id}"
input_dir="${REPLAY_ROOT}/inputs"
mkdir -p "${run_dir}" "${input_dir}"
input_copy="${input_dir}/${input_sha}_$(basename "${SOURCE_PCAP}")"
if [[ ! -f "${input_copy}" ]]; then
  cp --reflink=auto --preserve=timestamps "${SOURCE_PCAP}" "${input_copy}"
fi
copied_sha="$(sha256sum "${input_copy}" | awk '{print $1}')"
if [[ "${copied_sha}" != "${input_sha}" ]]; then
  echo "replay input hash mismatch" >&2
  exit 4
fi

manifest="${run_dir}/manifest.txt"
{
  echo "run_id=${run_id}"
  echo "source=${SOURCE_PCAP}"
  echo "replay_input=${input_copy}"
  echo "input_sha256=${input_sha}"
  echo "gpu_endpoint=${GPU_ENDPOINT}"
  echo "gpu_timeout_ms=${GPU_TIMEOUT_MS}"
  echo "batch_size=${BATCH_SIZE}"
  echo "feature_flush_us=${FEATURE_FLUSH_US}"
  echo "candidate_id=A09"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${manifest}"

cargo build --release \
  --manifest-path "${CODE_ROOT}/rust/hft-capture/Cargo.toml"
binary="${CODE_ROOT}/rust/hft-capture/target/release/hft-capture"
evidence_binary="${run_dir}/hft-capture.bin"
cp --reflink=auto --preserve=timestamps "${binary}" "${evidence_binary}"
binary_sha="$(sha256sum "${evidence_binary}" | awk '{print $1}')"
{
  echo "binary=${evidence_binary}"
  echo "binary_sha256=${binary_sha}"
} >> "${manifest}"
args=(
  --pcap "${input_copy}"
  --gpu-endpoint "${GPU_ENDPOINT}"
  --gpu-startup-wait-ms 10000
  --gpu-timeout-ms "${GPU_TIMEOUT_MS}"
  --metrics "${run_dir}/metrics.json"
  --batch-size "${BATCH_SIZE}"
  --feature-flush-us "${FEATURE_FLUSH_US}"
  --budget-us 5000
  --execution-budget-safety-ratio 0.50
)
if [[ "${MAX_PACKETS}" -gt 0 ]]; then
  args+=(--max-packets "${MAX_PACKETS}")
fi
/usr/bin/time -v -o "${run_dir}/physical_process_time.txt" \
  "${evidence_binary}" "${args[@]}" \
  > "${run_dir}/stdout.json" 2> "${run_dir}/stderr.log"
{
  echo "status=complete"
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "metrics=${run_dir}/metrics.json"
} >> "${manifest}"
sha256sum "${manifest}" "${run_dir}/metrics.json" "${run_dir}/stdout.json" \
  "${run_dir}/physical_process_time.txt" "${evidence_binary}" \
  > "${run_dir}/evidence_sha256.txt"
echo "${run_dir}"
