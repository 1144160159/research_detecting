#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
MAX_DURATION_S="${MAX_DURATION_S:-15}"
REPEATS="${REPEATS:-3}"
CAMPAIGN_ID="${CAMPAIGN_ID:-hft_shadow_matrix_$(date -u +%Y%m%dT%H%M%SZ)}"
CAMPAIGN_ROOT="${REPLAY_ROOT}/${CAMPAIGN_ID}"
RUNNER="${CODE_ROOT}/scripts/run_temporary_shadow_capture.sh"
SUMMARIZER="${CODE_ROOT}/scripts/summarize_temporary_shadow_matrix.py"
CANDIDATES=(
  shadow_b128_f1000
  shadow_b64_f500
  shadow_b32_f250
)

if [[ "${REPEATS}" != "3" ]]; then
  echo "REPEATS must remain frozen at 3" >&2
  exit 2
fi
if [[ ! "${MAX_DURATION_S}" =~ ^[0-9]+$ ]] \
  || (( MAX_DURATION_S < 10 || MAX_DURATION_S > 60 )); then
  echo "MAX_DURATION_S must be between 10 and 60 seconds" >&2
  exit 2
fi
if [[ -e "${CAMPAIGN_ROOT}" ]]; then
  echo "campaign root already exists: ${CAMPAIGN_ROOT}" >&2
  exit 2
fi

mkdir -p "${CAMPAIGN_ROOT}"
cat > "${CAMPAIGN_ROOT}/matrix_scope.env" <<EOF
schema_version=1
scope=temporary_management_interface_runtime_matrix
candidate_count=3
repeat_count=${REPEATS}
total_run_count=9
max_duration_s=${MAX_DURATION_S}
capture_interface=ens9f0
traffic_generation_allowed=false
final_pareto_ingestion_allowed=false
production_10gbe_claim_allowed=false
EOF

for repeat in 1 2 3; do
  for candidate in "${CANDIDATES[@]}"; do
    run_id="${candidate}_r${repeat}"
    ACK_MANAGEMENT_INTERFACE=1 \
    MAX_DURATION_S="${MAX_DURATION_S}" \
    SHADOW_RUNTIME_CANDIDATE="${candidate}" \
    REPLAY_ROOT="${CAMPAIGN_ROOT}" \
    RUN_ID="${run_id}" \
      "${RUNNER}"
    sleep 2
  done
done

python3 "${SUMMARIZER}" \
  "${CAMPAIGN_ROOT}" \
  "${CAMPAIGN_ROOT}/summary.json"

(
  cd "${CAMPAIGN_ROOT}"
  sha256sum matrix_scope.env summary.json > campaign_sha256.txt
)

echo "campaign_root=${CAMPAIGN_ROOT}"
echo "summary=${CAMPAIGN_ROOT}/summary.json"
