#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
MANIFEST="${MANIFEST:-${CODE_ROOT}/configs/ustc_tfc2016_binary_quality.json}"
REPEATS="${REPEATS:-3}"
MAX_PACKETS_PER_CAPTURE="${MAX_PACKETS_PER_CAPTURE:-20000}"
MAX_FLOWS_PER_CAPTURE="${MAX_FLOWS_PER_CAPTURE:-2000}"
ESTIMATORS="${ESTIMATORS:-200}"
N_JOBS="${N_JOBS:-8}"
BATCH_SIZE="${BATCH_SIZE:-512}"
BUDGET_US="${BUDGET_US:-5000}"
RUN_TAG="${RUN_TAG:-grouped_quality}"
seeds=(7 11 19)

if ! [[ "${REPEATS}" =~ ^[1-3]$ ]]; then
  echo "REPEATS must be 1, 2, or 3" >&2
  exit 2
fi
if [[ ! -f "${MANIFEST}" ]]; then
  echo "Quality manifest not found: ${MANIFEST}" >&2
  exit 3
fi

RUN_ID="HFT_G5_${RUN_TAG}_$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${PROJECT_ROOT}/runs/${RUN_ID}"
RESULT_DIR="${PROJECT_ROOT}/results/${RUN_ID}"
mkdir -p "${RUN_DIR}" "${RESULT_DIR}"

cd "${CODE_ROOT}"
"${CONDA}" run -n "${CONDA_ENV}" python scripts/check_local_policy.py
{
  echo "run_id=${RUN_ID}"
  echo "manifest=${MANIFEST}"
  echo "manifest_sha256=$(sha256sum "${MANIFEST}" | awk '{print $1}')"
  echo "repeats=${REPEATS}"
  echo "max_packets_per_capture=${MAX_PACKETS_PER_CAPTURE}"
  echo "max_flows_per_capture=${MAX_FLOWS_PER_CAPTURE}"
  echo "batch_size=${BATCH_SIZE}"
  echo "budget_us=${BUDGET_US}"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${RUN_DIR}/manifest.txt"

for mode in normal fallback; do
  extra=()
  if [[ "${mode}" == "fallback" ]]; then
    extra+=(--disable-deep)
  fi
  for repeat in $(seq 1 "${REPEATS}"); do
    seed="${seeds[$((repeat - 1))]}"
    PYTHONPATH=. "${CONDA}" run -n "${CONDA_ENV}" \
      python scripts/evaluate_grouped_quality.py "${MANIFEST}" \
      --batch-size "${BATCH_SIZE}" \
      --budget-us "${BUDGET_US}" \
      --max-packets-per-capture "${MAX_PACKETS_PER_CAPTURE}" \
      --max-flows-per-capture "${MAX_FLOWS_PER_CAPTURE}" \
      --estimators "${ESTIMATORS}" \
      --n-jobs "${N_JOBS}" \
      --seeds "${seed}" \
      "${extra[@]}" > "${RESULT_DIR}/${mode}_repeat${repeat}.json"
  done
done

find "${RESULT_DIR}" -type f -print0 | sort -z | xargs -0 sha256sum \
  > "${RUN_DIR}/result_sha256.txt"
{
  echo "status=complete"
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "result_dir=${RESULT_DIR}"
  echo "result_count=$(find "${RESULT_DIR}" -type f -name '*.json' | wc -l)"
} >> "${RUN_DIR}/manifest.txt"

echo "Completed ${RUN_ID}; results: ${RESULT_DIR}"
