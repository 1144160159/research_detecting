#!/usr/bin/env bash
set -uo pipefail

QUEUE_ROOT=${QUEUE_ROOT:-/tmp/caeos-eight-dataset-strict-queue-r17}
POLL_SECONDS=${POLL_SECONDS:-30}

mkdir -p "${QUEUE_ROOT}/status"

stage_status() {
  local dataset_id=$1
  local path="${QUEUE_ROOT}/status/${dataset_id}.status"
  if [[ -r "${path}" ]]; then
    cat "${path}"
  else
    printf 'queued\n'
  fi
}

stage_active() {
  local dataset_id=$1
  local pid_path="${QUEUE_ROOT}/status/${dataset_id}.pid"
  local pid
  [[ $(stage_status "${dataset_id}") == running ]] || return 1
  [[ -r "${pid_path}" ]] || return 1
  pid=$(cat "${pid_path}")
  [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
  kill -0 "${pid}" 2>/dev/null
}

write_queue_tsv() {
  local temporary="${QUEUE_ROOT}/queue.tsv.tmp.monitor.$$"
  : > "${temporary}"
  printf 'cic_bot_iot\t%s\trun_caeos_bot_iot_full_label_alignment.sh\n' "$(stage_status cic_bot_iot)" >> "${temporary}"
  printf 'cic_ton_iot\t%s\trun_caeos_ton_iot_full_label_alignment.sh\n' "$(stage_status cic_ton_iot)" >> "${temporary}"
  printf 'cicids2017\t%s\trun_caeos_cicids2017_full_label_alignment.sh\n' "$(stage_status cicids2017)" >> "${temporary}"
  printf 'cicddos2019\t%s\trun_caeos_cicddos2019_full_label_alignment.sh\n' "$(stage_status cicddos2019)" >> "${temporary}"
  printf 'dohbrw2020\t%s\trun_caeos_dohbrw2020_full_label_alignment.sh\n' "$(stage_status dohbrw2020)" >> "${temporary}"
  printf 'ciciot2023\t%s\trun_caeos_ciciot2023_all_pcaps_strict.sh\n' "$(stage_status ciciot2023)" >> "${temporary}"
  printf 'ciciot2022\t%s\trun_caeos_ciciot2022_all_pcaps_strict.sh\n' "$(stage_status ciciot2022)" >> "${temporary}"
  printf 'edge_iiotset\t%s\trun_caeos_edge_iiotset_full_label_alignment.sh\n' "$(stage_status edge_iiotset)" >> "${temporary}"
  mv "${temporary}" "${QUEUE_ROOT}/queue.tsv"
}

printf '%s\n' "$$" > "${QUEUE_ROOT}/queue.monitor.pid"
date -u +%FT%TZ > "${QUEUE_ROOT}/queue.monitor.started_at"
while true; do
  active=()
  stale=()
  for dataset_id in ciciot2023 ciciot2022 dohbrw2020; do
    if stage_active "${dataset_id}"; then
      active+=("${dataset_id}")
    elif [[ $(stage_status "${dataset_id}") == running ]]; then
      stale+=("${dataset_id}")
    fi
  done
  write_queue_tsv
  if [[ ${#active[@]} -gt 0 ]]; then
    joined=$(IFS=,; printf '%s' "${active[*]}")
    printf 'parallel:%s\n' "${joined}" > "${QUEUE_ROOT}/queue.status"
  elif [[ ${#stale[@]} -gt 0 ]]; then
    joined=$(IFS=,; printf '%s' "${stale[*]}")
    printf 'stale_running_status_without_live_pid:%s\n' "${joined}" > "${QUEUE_ROOT}/queue.status"
  else
    printf 'idle_no_active_worker_not_global_completion\n' > "${QUEUE_ROOT}/queue.status"
    date -u +%FT%TZ > "${QUEUE_ROOT}/queue.monitor.finished_at"
    exit 0
  fi
  sleep "${POLL_SECONDS}"
done
