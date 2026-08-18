#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 CAMPAIGN_ID" >&2
  exit 2
fi

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
RUN_ROOT="${PROJECT_ROOT}/runs/split_deployment"
RUNTIME_MANIFEST="${RUN_ROOT}/runtime_manifest.json"
RELEASE_CONFIG="${CODE_ROOT}/configs/release_candidate_rc1.json"
CAMPAIGN_ID="$1"
OUTPUT_ROOT="${OUTPUT_ROOT:-${PROJECT_ROOT}/runs/resource_confirmation/${CAMPAIGN_ID}}"

[[ ! -e "${OUTPUT_ROOT}" ]] || {
  echo "resource campaign already exists: ${OUTPUT_ROOT}" >&2
  exit 2
}
mkdir -p "${OUTPUT_ROOT}"

for repeat in 1 2 3; do
  PYTHONPATH="${CODE_ROOT}" "${CONDA}" run --no-capture-output \
    -n "${CONDA_ENV}" \
    python "${CODE_ROOT}/scripts/sample_inference_node_resources.py" \
    --runtime-manifest "${RUNTIME_MANIFEST}" \
    --release-config "${RELEASE_CONFIG}" \
    --duration-s 40 \
    --interval-s 0.1 \
    --gpu-interval-s 0.5 \
    --gpu-index 0 \
    --output "${OUTPUT_ROOT}/resource_run${repeat}.json"
done

PYTHONPATH="${CODE_ROOT}" "${CONDA}" run --no-capture-output \
  -n "${CONDA_ENV}" \
  python "${CODE_ROOT}/scripts/aggregate_inference_node_resources.py" \
  "${OUTPUT_ROOT}/resource_run1.json" \
  "${OUTPUT_ROOT}/resource_run2.json" \
  "${OUTPUT_ROOT}/resource_run3.json" \
  --minimum-runs 3 \
  --output "${OUTPUT_ROOT}/summary.json"

(
  cd "${OUTPUT_ROOT}"
  sha256sum \
    resource_run1.json \
    resource_run2.json \
    resource_run3.json \
    summary.json \
    > evidence_sha256.txt
)
