#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
RUN_ROOT=/tmp/caeos-four-new-label-datasets-r19
MEMORY_START_LIMIT_BYTES=${MEMORY_START_LIMIT_BYTES:-182536110080}

DATASETS=(cicids2018 cert_insider_threat 5gad_2022 unsw_nb15)
RUNNERS=(
  run_caeos_cicids2018_label_regeneration_intake.sh
  run_caeos_cert_insider_label_intake.sh
  run_caeos_5gad2022_full_label_alignment.sh
  run_caeos_unsw_nb15_full_label_alignment.sh
)

mkdir -p "${RUN_ROOT}/logs" "${RUN_ROOT}/status"
exec </dev/null >>"${RUN_ROOT}/logs/queue.stdout.log" 2>>"${RUN_ROOT}/logs/queue.stderr.log"
echo "$$" >"${RUN_ROOT}/queue.pid"

stage_status() {
  local dataset=$1
  local file="${RUN_ROOT}/status/${dataset}.status"
  [[ -r "${file}" ]] && cat "${file}" || echo queued
}

write_status() {
  local temporary="${RUN_ROOT}/status.tsv.tmp.$$"
  : >"${temporary}"
  local index
  for index in "${!DATASETS[@]}"; do
    printf '%s\t%s\t%s\n' "${DATASETS[$index]}" \
      "$(stage_status "${DATASETS[$index]}")" "${RUNNERS[$index]}" >>"${temporary}"
  done
  mv "${temporary}" "${RUN_ROOT}/status.tsv"
}

set_status() {
  printf '%s\n' "$2" >"${RUN_ROOT}/status/$1.status"
  write_status
}

memory_usage() {
  if [[ -r /sys/fs/cgroup/memory/memory.usage_in_bytes ]]; then
    cat /sys/fs/cgroup/memory/memory.usage_in_bytes
  else
    cat /sys/fs/cgroup/memory.current 2>/dev/null || echo 0
  fi
}

heavy_label_processes_running() {
  pgrep -f 'audit_caeos_(ciciot|benign_capture_dataset)' >/dev/null 2>&1
}

run_stage() {
  local dataset=$1 runner=$2 heavy=$3 success_status=${4:-complete}
  local current
  current=$(stage_status "${dataset}")
  if [[ "${current}" == complete ]] || [[ "${current}" == waiting_for_exact_flow_regeneration ]] \
    || [[ "${current}" == waiting_for_release_log_join ]]; then
    return
  fi
  if [[ "${heavy}" == true ]]; then
    set_status "${dataset}" waiting_for_resources
    while heavy_label_processes_running || [[ $(memory_usage) -gt ${MEMORY_START_LIMIT_BYTES} ]]; do
      sleep 60
    done
  fi
  set_status "${dataset}" running
  date -u +%FT%TZ >"${RUN_ROOT}/status/${dataset}.started_at"
  bash "${WORKDIR}/${runner}" \
    >"${RUN_ROOT}/logs/${dataset}.stdout.log" \
    2>"${RUN_ROOT}/logs/${dataset}.stderr.log"
  code=$?
  printf '%s\n' "${code}" >"${RUN_ROOT}/status/${dataset}.exit_code"
  date -u +%FT%TZ >"${RUN_ROOT}/status/${dataset}.finished_at"
  if [[ ${code} -eq 0 ]]; then
    set_status "${dataset}" "${success_status}"
  else
    set_status "${dataset}" failed
  fi
}

for runner in "${RUNNERS[@]}"; do
  [[ -r "${WORKDIR}/${runner}" ]] || { echo "missing runner: ${runner}"; exit 2; }
done

write_status
run_stage cicids2018 run_caeos_cicids2018_label_regeneration_intake.sh false waiting_for_exact_flow_regeneration
run_stage cert_insider_threat run_caeos_cert_insider_label_intake.sh false waiting_for_release_log_join
run_stage 5gad_2022 run_caeos_5gad2022_full_label_alignment.sh true
run_stage unsw_nb15 run_caeos_unsw_nb15_full_label_alignment.sh true

printf 'complete\n' >"${RUN_ROOT}/queue.status"
date -u +%FT%TZ >"${RUN_ROOT}/queue.finished_at"
