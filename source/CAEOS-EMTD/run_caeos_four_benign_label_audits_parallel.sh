#!/usr/bin/env bash
set -uo pipefail

WORKDIR=${WORKDIR:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14}
PYTHON=${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}
SOURCE_MANIFEST=${SOURCE_MANIFEST:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5/_control/source_manifest.json}
QUEUE_ROOT=${QUEUE_ROOT:-/tmp/caeos-four-benign-dataset-strict-queue-r18}
TEMP_ROOT=${TEMP_ROOT:-/tmp/caeos-four-benign-dataset-temp-r18}

DATASETS=(
  iscx_tor_nontor_2017
  iscx_vpn_nonvpn_2016
  parrot2025
  crossplatform_android_ios
)

declare -A PIDS=()
declare -A OWNED=()
mkdir -p "${QUEUE_ROOT}/logs" "${QUEUE_ROOT}/status" "${TEMP_ROOT}"
echo "$$" > "${QUEUE_ROOT}/queue.pid"

write_status() {
  local temporary="${QUEUE_ROOT}/status.tsv.tmp.$$"
  : > "${temporary}"
  local dataset status
  for dataset in "${DATASETS[@]}"; do
    status=queued
    [[ -r "${QUEUE_ROOT}/status/${dataset}.status" ]] && status=$(<"${QUEUE_ROOT}/status/${dataset}.status")
    printf '%s\t%s\t%s\n' "${dataset}" "${status}" "${PIDS[${dataset}]:-}" >> "${temporary}"
  done
  mv "${temporary}" "${QUEUE_ROOT}/status.tsv"
  cp "${QUEUE_ROOT}/status.tsv" "${QUEUE_ROOT}/queue.tsv"
}

for dataset in "${DATASETS[@]}"; do
  existing_pid=""
  [[ -r "${QUEUE_ROOT}/status/${dataset}.pid" ]] && existing_pid=$(<"${QUEUE_ROOT}/status/${dataset}.pid")
  if [[ -n "${existing_pid}" ]] \
    && [[ -r "/proc/${existing_pid}/cmdline" ]] \
    && tr '\0' ' ' < "/proc/${existing_pid}/cmdline" | grep -q "audit_caeos_benign_capture_dataset.py --dataset-id ${dataset}"; then
    PIDS[${dataset}]=${existing_pid}
    OWNED[${dataset}]=0
    printf 'running\n' > "${QUEUE_ROOT}/status/${dataset}.status"
    continue
  fi
  printf 'running\n' > "${QUEUE_ROOT}/status/${dataset}.status"
  date -u +%FT%TZ > "${QUEUE_ROOT}/status/${dataset}.started_at"
  run_root="/tmp/caeos-${dataset//_/-}-all-pcap-r18"
  mkdir -p "${run_root}" "${TEMP_ROOT}/${dataset}"
  nice -n 10 ionice -c 2 -n 7 "${PYTHON}" "${WORKDIR}/audit_caeos_benign_capture_dataset.py" \
    --dataset-id "${dataset}" \
    --source-manifest "${SOURCE_MANIFEST}" \
    --run-root "${run_root}" \
    --temp-root "${TEMP_ROOT}/${dataset}" \
    > "${QUEUE_ROOT}/logs/${dataset}.stdout.log" \
    2> "${QUEUE_ROOT}/logs/${dataset}.stderr.log" &
  PIDS[${dataset}]=$!
  OWNED[${dataset}]=1
  printf '%s\n' "${PIDS[${dataset}]}" > "${QUEUE_ROOT}/status/${dataset}.pid"
done

write_status
printf 'parallel_running\n' > "${QUEUE_ROOT}/queue.status"

while :; do
  running=0
  for dataset in "${DATASETS[@]}"; do
    status=$(<"${QUEUE_ROOT}/status/${dataset}.status")
    [[ "${status}" == complete || "${status}" == failed ]] && continue
    pid=${PIDS[${dataset}]}
    state=$(ps -o stat= -p "${pid}" 2>/dev/null | tr -d ' ' || true)
    if [[ -n "${state}" && "${state}" != Z* ]]; then
      running=$((running + 1))
      continue
    fi
    code=2
    if [[ ${OWNED[${dataset}]} -eq 1 ]]; then
      wait "${pid}" && code=0 || code=$?
    elif "${PYTHON}" -c 'import json,sys; d=json.load(open(sys.argv[1],encoding="utf-8")); raise SystemExit(0 if d.get("formal_dataset_gate_passed") is True else 2)' "/tmp/caeos-${dataset//_/-}-all-pcap-r18/summary.json"; then
      code=0
    fi
    printf '%s\n' "${code}" > "${QUEUE_ROOT}/status/${dataset}.exit_code"
    date -u +%FT%TZ > "${QUEUE_ROOT}/status/${dataset}.finished_at"
    if [[ ${code} -eq 0 ]]; then
      printf 'complete\n' > "${QUEUE_ROOT}/status/${dataset}.status"
    else
      printf 'failed\n' > "${QUEUE_ROOT}/status/${dataset}.status"
    fi
    write_status
  done
  [[ ${running} -eq 0 ]] && break
  sleep 15
done

printf 'parallel_finished\n' > "${QUEUE_ROOT}/queue.status"
date -u +%FT%TZ > "${QUEUE_ROOT}/queue.finished_at"
