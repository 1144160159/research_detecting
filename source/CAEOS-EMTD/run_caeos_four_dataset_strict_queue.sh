#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
RUN_ROOT=/tmp/caeos-four-dataset-strict-queue-r14
BOT_PID=${BOT_PID:-92180}
MEMORY_START_LIMIT_BYTES=${MEMORY_START_LIMIT_BYTES:-182536110080}
MEMORY_START_LIMIT_MAX_BYTES=193273528320

if [[ ${MEMORY_START_LIMIT_BYTES} -gt ${MEMORY_START_LIMIT_MAX_BYTES} ]]; then
  echo "MEMORY_START_LIMIT_BYTES must not exceed 180 GiB" >&2
  exit 2
fi

mkdir -p "${RUN_ROOT}/logs" "${RUN_ROOT}/status"
exec </dev/null >> "${RUN_ROOT}/logs/stdout.log" 2>> "${RUN_ROOT}/logs/stderr.log"
echo "$$" > "${RUN_ROOT}/queue.pid"
printf 'cic_ton_iot\tqueued\ncicids2017\tqueued\ncicddos2019\tqueued\ndohbrw2020\tqueued\n' > "${RUN_ROOT}/queue.tsv"

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

record_memory_state() {
  local output=$1
  {
    echo "captured_at=$(date -u +%FT%TZ)"
    echo "memory_usage_bytes=$(memory_usage)"
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

while [[ $(memory_usage) -gt ${MEMORY_START_LIMIT_BYTES} ]]; do
  echo "waiting for reclaimable memory/cache headroom: $(memory_usage) bytes"
  sleep 60
done

run_stage() {
  local dataset_id=$1
  local runner=$2
  while [[ $(memory_usage) -gt ${MEMORY_START_LIMIT_BYTES} ]]; do
    echo "${dataset_id}: waiting for reclaimable memory/cache headroom: $(memory_usage) bytes"
    sleep 60
  done
  printf 'running\n' > "${RUN_ROOT}/status/${dataset_id}.status"
  date -u +%FT%TZ > "${RUN_ROOT}/status/${dataset_id}.started_at"
  record_memory_state "${RUN_ROOT}/status/${dataset_id}.memory_before.txt"
  bash "${WORKDIR}/${runner}" \
    > "/tmp/caeos-${dataset_id//_/-}-strict-runner.stdout.log" \
    2> "/tmp/caeos-${dataset_id//_/-}-strict-runner.stderr.log"
  local code=$?
  record_memory_state "${RUN_ROOT}/status/${dataset_id}.memory_after.txt"
  printf '%s\n' "${code}" > "${RUN_ROOT}/status/${dataset_id}.exit_code"
  date -u +%FT%TZ > "${RUN_ROOT}/status/${dataset_id}.finished_at"
  if [[ ${code} -eq 0 ]]; then
    printf 'complete\n' > "${RUN_ROOT}/status/${dataset_id}.status"
  else
    printf 'failed\n' > "${RUN_ROOT}/status/${dataset_id}.status"
  fi
}

run_stage cic_ton_iot run_caeos_ton_iot_full_label_alignment.sh
run_stage cicids2017 run_caeos_cicids2017_full_label_alignment.sh
run_stage cicddos2019 run_caeos_cicddos2019_full_label_alignment.sh
run_stage dohbrw2020 run_caeos_dohbrw2020_full_label_alignment.sh

date -u +%FT%TZ > "${RUN_ROOT}/queue.finished_at"
