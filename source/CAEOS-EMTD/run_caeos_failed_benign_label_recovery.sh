#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
SOURCE_MANIFEST=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5/_control/source_manifest.json
TEMP_ROOT=/tmp/caeos-four-benign-dataset-temp-r18
ORIGINAL_QUEUE=/tmp/caeos-four-benign-dataset-strict-queue-r18
RECOVERY_ROOT=/tmp/caeos-benign-failed-recovery-r19
DATASETS=(iscx_vpn_nonvpn_2016 parrot2025)

mkdir -p "${RECOVERY_ROOT}/logs" "${RECOVERY_ROOT}/status" "${RECOVERY_ROOT}/pids"
exec 9>"${RECOVERY_ROOT}/recovery.lock"
flock -n 9 || exit 9

declare -A PIDS=()
write_status() {
  local temporary=${RECOVERY_ROOT}/status.tsv.tmp.$$
  : >"${temporary}"
  local dataset state
  for dataset in "${DATASETS[@]}"; do
    state=queued
    [[ -r "${RECOVERY_ROOT}/status/${dataset}" ]] && state=$(cat "${RECOVERY_ROOT}/status/${dataset}")
    printf '%s\t%s\t%s\n' "${dataset}" "${state}" "${PIDS[$dataset]:-}" >>"${temporary}"
  done
  mv "${temporary}" "${RECOVERY_ROOT}/status.tsv"
}

for dataset in "${DATASETS[@]}"; do
  run_root=/tmp/caeos-${dataset//_/-}-all-pcap-r18
  printf '%s\n' running >"${RECOVERY_ROOT}/status/${dataset}"
  date -u +%FT%TZ >"${RECOVERY_ROOT}/status/${dataset}.started_at"
  nice -n 15 ionice -c 3 "${PYTHON}" -u "${WORKDIR}/audit_caeos_benign_capture_dataset.py" \
    --dataset-id "${dataset}" \
    --source-manifest "${SOURCE_MANIFEST}" \
    --run-root "${run_root}" \
    --temp-root "${TEMP_ROOT}/${dataset}" \
    >"${RECOVERY_ROOT}/logs/${dataset}.stdout.log" \
    2>"${RECOVERY_ROOT}/logs/${dataset}.stderr.log" &
  PIDS[$dataset]=$!
  printf '%s\n' "${PIDS[$dataset]}" >"${RECOVERY_ROOT}/pids/${dataset}.pid"
done
write_status

remaining=${#DATASETS[@]}
while [[ ${remaining} -gt 0 ]]; do
  for dataset in "${DATASETS[@]}"; do
    state=$(cat "${RECOVERY_ROOT}/status/${dataset}")
    [[ "${state}" == running ]] || continue
    pid=${PIDS[$dataset]}
    process_state=$(ps -o stat= -p "${pid}" 2>/dev/null | tr -d ' ' || true)
    [[ -n "${process_state}" && "${process_state}" != Z* ]] && continue
    wait "${pid}" && code=0 || code=$?
    printf '%s\n' "${code}" >"${RECOVERY_ROOT}/status/${dataset}.exit_code"
    date -u +%FT%TZ >"${RECOVERY_ROOT}/status/${dataset}.finished_at"
    if [[ ${code} -eq 0 ]]; then
      printf '%s\n' complete >"${RECOVERY_ROOT}/status/${dataset}"
      printf '%s\n' complete >"${ORIGINAL_QUEUE}/status/${dataset}.status"
    else
      printf '%s\n' failed >"${RECOVERY_ROOT}/status/${dataset}"
    fi
    remaining=$((remaining - 1))
    write_status
  done
  [[ ${remaining} -gt 0 ]] && sleep 15
done

if grep -q $'\tfailed\t' "${RECOVERY_ROOT}/status.tsv"; then
  printf '%s\n' failed >"${RECOVERY_ROOT}/recovery.status"
  exit 1
fi
printf '%s\n' complete >"${RECOVERY_ROOT}/recovery.status"
