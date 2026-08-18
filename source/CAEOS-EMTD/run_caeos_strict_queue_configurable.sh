#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
RUN_ROOT=${RUN_ROOT:-/tmp/caeos-strict-queue-r14}
BOT_PID=${BOT_PID:-92180}
MEMORY_START_LIMIT_BYTES=${MEMORY_START_LIMIT_BYTES:-182536110080}
MEMORY_START_LIMIT_MAX_BYTES=193273528320

# Keep these arrays positional and update them only after every referenced runner exists.
STAGE_DATASETS=(
  cic_bot_iot
  cic_ton_iot
  cicids2017
  cicddos2019
  dohbrw2020
  ciciot2023
  ciciot2022
)
STAGE_RUNNERS=(
  run_caeos_bot_iot_full_label_alignment.sh
  run_caeos_ton_iot_full_label_alignment.sh
  run_caeos_cicids2017_full_label_alignment.sh
  run_caeos_cicddos2019_full_label_alignment.sh
  run_caeos_dohbrw2020_full_label_alignment.sh
  run_caeos_ciciot2023_all_pcaps_strict.sh
  run_caeos_ciciot2022_all_pcaps_strict.sh
)

if [[ ${#STAGE_DATASETS[@]} -ne ${#STAGE_RUNNERS[@]} ]]; then
  echo "STAGE_DATASETS and STAGE_RUNNERS length mismatch" >&2
  exit 2
fi
if [[ ${MEMORY_START_LIMIT_BYTES} -gt ${MEMORY_START_LIMIT_MAX_BYTES} ]]; then
  echo "MEMORY_START_LIMIT_BYTES must not exceed 180 GiB" >&2
  exit 2
fi
for runner in "${STAGE_RUNNERS[@]}"; do
  if [[ ! -r "${WORKDIR}/${runner}" ]]; then
    echo "configured runner is missing: ${WORKDIR}/${runner}" >&2
    exit 2
  fi
done

mkdir -p "${RUN_ROOT}/logs" "${RUN_ROOT}/status"
exec </dev/null >> "${RUN_ROOT}/logs/stdout.log" 2>> "${RUN_ROOT}/logs/stderr.log"
if [[ ! -e "${RUN_ROOT}/queue.stdout.log" ]]; then
  ln -s logs/stdout.log "${RUN_ROOT}/queue.stdout.log"
fi
if [[ ! -e "${RUN_ROOT}/queue.stderr.log" ]]; then
  ln -s logs/stderr.log "${RUN_ROOT}/queue.stderr.log"
fi
echo "$$" > "${RUN_ROOT}/queue.pid"

stage_status() {
  local dataset_id=$1
  local path="${RUN_ROOT}/status/${dataset_id}.status"
  if [[ -r "${path}" ]]; then
    cat "${path}"
  else
    echo queued
  fi
}

write_queue_status() {
  local temporary="${RUN_ROOT}/queue.tsv.tmp.$$"
  : > "${temporary}"
  local index
  for index in "${!STAGE_DATASETS[@]}"; do
    printf '%s\t%s\t%s\n' \
      "${STAGE_DATASETS[$index]}" \
      "$(stage_status "${STAGE_DATASETS[$index]}")" \
      "${STAGE_RUNNERS[$index]}" >> "${temporary}"
  done
  mv "${temporary}" "${RUN_ROOT}/queue.tsv"
}

set_stage_status() {
  local dataset_id=$1
  local status=$2
  printf '%s\n' "${status}" > "${RUN_ROOT}/status/${dataset_id}.status"
  write_queue_status
}

write_queue_status
printf 'waiting_for_bot\n' > "${RUN_ROOT}/queue.status"
if [[ -r "/proc/${BOT_PID}/cmdline" ]] && tr '\0' ' ' < "/proc/${BOT_PID}/cmdline" | grep -q 'audit_caeos_bot_iot_all_pcaps.py'; then
  echo "waiting for BoT-IoT strict audit PID ${BOT_PID}"
  while kill -0 "${BOT_PID}" 2>/dev/null; do sleep 60; done
fi

memory_usage() {
  if [[ -r /sys/fs/cgroup/memory/memory.usage_in_bytes ]]; then
    cat /sys/fs/cgroup/memory/memory.usage_in_bytes
  elif [[ -r /sys/fs/cgroup/memory.current ]]; then
    cat /sys/fs/cgroup/memory.current
  else
    echo 0
  fi
}

memory_inactive_file() {
  local stat_path=/sys/fs/cgroup/memory/memory.stat
  if [[ ! -r "${stat_path}" ]]; then
    echo 0
    return
  fi
  awk '
    $1 == "total_inactive_file" { total = $2 }
    $1 == "inactive_file" { local_value = $2 }
    END {
      if (total != "") print total
      else if (local_value != "") print local_value
      else print 0
    }
  ' "${stat_path}"
}

memory_stat_value() {
  local total_key=$1
  local local_key=$2
  local stat_path=/sys/fs/cgroup/memory/memory.stat
  if [[ ! -r "${stat_path}" ]]; then
    echo 0
    return
  fi
  awk -v total_key="${total_key}" -v local_key="${local_key}" '
    $1 == total_key { total = $2 }
    $1 == local_key { local_value = $2 }
    END {
      if (total != "") print total
      else if (local_value != "") print local_value
      else print 0
    }
  ' "${stat_path}"
}

memory_working_set() {
  local rss shmem dirty writeback unevictable
  rss=$(memory_stat_value total_rss rss)
  shmem=$(memory_stat_value total_shmem shmem)
  dirty=$(memory_stat_value total_dirty dirty)
  writeback=$(memory_stat_value total_writeback writeback)
  unevictable=$(memory_stat_value total_unevictable unevictable)
  echo $((rss + shmem + dirty + writeback + unevictable))
}

memory_under_oom() {
  local oom_path=/sys/fs/cgroup/memory/memory.oom_control
  if [[ -r "${oom_path}" ]]; then
    awk '$1 == "under_oom" { print $2; found = 1 } END { if (!found) print 0 }' "${oom_path}"
  else
    echo 0
  fi
}

record_memory_state() {
  local output=$1
  {
    echo "captured_at=$(date -u +%FT%TZ)"
    echo "memory_usage_bytes=$(memory_usage)"
    echo "memory_inactive_file_bytes=$(memory_inactive_file)"
    echo "memory_nonreclaimable_working_set_bytes=$(memory_working_set)"
    if [[ -r /sys/fs/cgroup/memory/memory.limit_in_bytes ]]; then
      echo "memory_limit_bytes=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)"
    fi
    if [[ -r /sys/fs/cgroup/memory/memory.failcnt ]]; then
      echo "memory_failcnt=$(cat /sys/fs/cgroup/memory/memory.failcnt)"
    fi
    if [[ -r /sys/fs/cgroup/memory/memory.oom_control ]]; then
      echo "memory_oom_control_begin"
      cat /sys/fs/cgroup/memory/memory.oom_control
      echo "memory_oom_control_end"
    fi
    if [[ -r /sys/fs/cgroup/memory.events ]]; then
      echo "memory_events_begin"
      cat /sys/fs/cgroup/memory.events
      echo "memory_events_end"
    fi
  } > "${output}"
}

run_stage() {
  local dataset_id=$1
  local runner=$2
  printf 'waiting_for_memory\n' > "${RUN_ROOT}/queue.status"
  while [[ $(memory_working_set) -gt ${MEMORY_START_LIMIT_BYTES} ]] || [[ $(memory_under_oom) -ne 0 ]]; do
    echo "${dataset_id}: waiting for memory working set: $(memory_working_set) bytes (total usage: $(memory_usage) bytes)"
    sleep 60
  done
  set_stage_status "${dataset_id}" running
  printf 'running:%s\n' "${dataset_id}" > "${RUN_ROOT}/queue.status"
  date -u +%FT%TZ > "${RUN_ROOT}/status/${dataset_id}.started_at"
  record_memory_state "${RUN_ROOT}/status/${dataset_id}.memory_before.txt"
  bash "${WORKDIR}/${runner}" \
    > "${RUN_ROOT}/logs/${dataset_id}.stdout.log" \
    2> "${RUN_ROOT}/logs/${dataset_id}.stderr.log"
  local code=$?
  record_memory_state "${RUN_ROOT}/status/${dataset_id}.memory_after.txt"
  printf '%s\n' "${code}" > "${RUN_ROOT}/status/${dataset_id}.exit_code"
  date -u +%FT%TZ > "${RUN_ROOT}/status/${dataset_id}.finished_at"
  if [[ ${code} -eq 0 ]]; then
    set_stage_status "${dataset_id}" complete
  else
    set_stage_status "${dataset_id}" failed
  fi
}

for index in "${!STAGE_DATASETS[@]}"; do
  if [[ $(stage_status "${STAGE_DATASETS[$index]}") == complete ]]; then
    echo "${STAGE_DATASETS[$index]}: verified complete; skipping"
    continue
  fi
  run_stage "${STAGE_DATASETS[$index]}" "${STAGE_RUNNERS[$index]}"
done

printf 'complete\n' > "${RUN_ROOT}/queue.status"
date -u +%FT%TZ > "${RUN_ROOT}/queue.finished_at"
