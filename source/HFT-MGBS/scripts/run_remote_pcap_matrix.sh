#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
DATASETS_ROOT="${DATASETS_ROOT:-/opt/data/private/wangwt/ParkAttackKE/datasets}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
MAX_PACKETS="${MAX_PACKETS:-500000}"
GPU_INDEX="${GPU_INDEX:-0}"
REPEATS="${REPEATS:-3}"
BATCH_SIZES="${BATCH_SIZES:-512 2048 4096}"
BUDGET_US_VALUES="${BUDGET_US_VALUES:-5000 10000 25000}"
MODES="${MODES:-normal fallback}"
RUN_TAG="${RUN_TAG:-}"
SAFETY_RATIO="${SAFETY_RATIO:-0.75}"

if ! [[ "${REPEATS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "REPEATS must be a positive integer" >&2
  exit 2
fi
if [[ -n "${RUN_TAG}" && ! "${RUN_TAG}" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "RUN_TAG may contain only letters, numbers, underscore, and hyphen" >&2
  exit 2
fi

read -r -a batch_sizes <<< "${BATCH_SIZES}"
read -r -a budget_us_values <<< "${BUDGET_US_VALUES}"
read -r -a modes <<< "${MODES}"
if (( ${#batch_sizes[@]} == 0 || ${#budget_us_values[@]} == 0 || ${#modes[@]} == 0 )); then
  echo "BATCH_SIZES, BUDGET_US_VALUES, and MODES must not be empty" >&2
  exit 2
fi
for mode in "${modes[@]}"; do
  if [[ "${mode}" != "normal" && "${mode}" != "fallback" ]]; then
    echo "Unsupported mode: ${mode}; use normal or fallback" >&2
    exit 2
  fi
done

if [[ -z "${PCAP_PATH:-}" ]]; then
  PCAP_PATH="$(find "${DATASETS_ROOT}" -type f \( -iname '*.pcap' -o -iname '*.cap' \) -print -quit)"
fi
if [[ -z "${PCAP_PATH}" || ! -f "${PCAP_PATH}" ]]; then
  echo "No classic PCAP found. Set PCAP_PATH to a readable server-side capture." >&2
  exit 3
fi

run_tag_segment=""
if [[ -n "${RUN_TAG}" ]]; then
  run_tag_segment="_${RUN_TAG}"
fi
RUN_ID="HFT_G3${run_tag_segment}_pcap_matrix_$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${PROJECT_ROOT}/runs/${RUN_ID}"
RESULT_DIR="${PROJECT_ROOT}/results/${RUN_ID}"
mkdir -p "${RUN_DIR}" "${RESULT_DIR}" "${PROJECT_ROOT}/manifests"

cd "${CODE_ROOT}"
"${CONDA}" run -n "${CONDA_ENV}" python scripts/check_local_policy.py
"${CONDA}" run -n "${CONDA_ENV}" python -m unittest discover -s tests -v \
  > "${RUN_DIR}/unit_tests.txt" 2>&1

{
  echo "run_id=${RUN_ID}"
  echo "pcap_path=${PCAP_PATH}"
  echo "pcap_sha256=$(sha256sum "${PCAP_PATH}" | awk '{print $1}')"
  echo "max_packets=${MAX_PACKETS}"
  echo "measured_repeats=${REPEATS}"
  echo "batch_sizes=${BATCH_SIZES}"
  echo "budget_us_values=${BUDGET_US_VALUES}"
  echo "execution_budget_safety_ratio=${SAFETY_RATIO}"
  echo "modes=${MODES}"
  echo "conda_env=${CONDA_ENV}"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -srmo)"
  echo "cpu=$(lscpu | tr '\n' ';')"
  echo "gpu=$(nvidia-smi -L | tr '\n' ';')"
} > "${RUN_DIR}/environment.txt"

for batch_size in "${batch_sizes[@]}"; do
  for budget_us in "${budget_us_values[@]}"; do
    for mode in "${modes[@]}"; do
      for repeat in $(seq 1 "${REPEATS}"); do
        output="${RESULT_DIR}/${mode}_batch${batch_size}_budget${budget_us}_repeat${repeat}.json"
        extra=()
        if [[ "${mode}" == "fallback" ]]; then
          extra+=(--disable-deep)
        fi
        PYTHONPATH=. "${CONDA}" run -n "${CONDA_ENV}" python scripts/benchmark_pcap.py \
          "${PCAP_PATH}" \
          --max-packets "${MAX_PACKETS}" \
          --batch-size "${batch_size}" \
          --budget-us "${budget_us}" \
          --execution-budget-safety-ratio "${SAFETY_RATIO}" \
          --key-flow-ratio 0.10 \
          --gpu-index "${GPU_INDEX}" \
          "${extra[@]}" > "${output}"
      done
    done
  done
done

find . -type f -not -path './__pycache__/*' -not -name '*.pyc' -print0 \
  | sort -z | xargs -0 sha256sum > "${PROJECT_ROOT}/manifests/HFT-MGBS_code_sha256.txt"
find "${RESULT_DIR}" -type f -print0 | sort -z | xargs -0 sha256sum \
  > "${RUN_DIR}/result_sha256.txt"

{
  echo "status=complete"
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "result_dir=${RESULT_DIR}"
  echo "result_count=$(find "${RESULT_DIR}" -type f -name '*.json' | wc -l)"
  echo "evidence_scope=offline_pcap_processing_only"
} > "${RUN_DIR}/manifest.txt"

echo "Completed ${RUN_ID}; results: ${RESULT_DIR}"
