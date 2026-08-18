#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
QUEUE_ROOT=/tmp/caeos-eight-dataset-strict-queue-r17
DOH_RUN_ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/DoHBrw2020/derived/caeos_dohbrw2020_complete_flows_r16
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python

mkdir -p "${QUEUE_ROOT}/logs" "${QUEUE_ROOT}/status"

stage_status() {
  local dataset_id=$1
  local path="${QUEUE_ROOT}/status/${dataset_id}.status"
  if [[ -r "${path}" ]]; then
    cat "${path}"
  else
    printf 'queued\n'
  fi
}

write_queue_tsv() {
  local temporary="${QUEUE_ROOT}/queue.tsv.tmp.$$"
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

write_active_status() {
  local active=()
  local dataset_id pid_path pid
  for dataset_id in ciciot2023 ciciot2022 dohbrw2020; do
    pid_path="${QUEUE_ROOT}/status/${dataset_id}.pid"
    if [[ $(stage_status "${dataset_id}") == running ]] && [[ -r "${pid_path}" ]]; then
      pid=$(cat "${pid_path}")
      if [[ "${pid}" =~ ^[0-9]+$ ]] && kill -0 "${pid}" 2>/dev/null; then
        active+=("${dataset_id}")
      fi
    fi
  done
  if [[ ${#active[@]} -gt 0 ]]; then
    local joined
    joined=$(IFS=,; printf '%s' "${active[*]}")
    printf 'parallel:%s\n' "${joined}" > "${QUEUE_ROOT}/queue.status"
  else
    printf 'idle_no_active_worker_not_complete\n' > "${QUEUE_ROOT}/queue.status"
  fi
}

existing_pid=""
if [[ -r "${QUEUE_ROOT}/status/dohbrw2020.pid" ]]; then
  existing_pid=$(cat "${QUEUE_ROOT}/status/dohbrw2020.pid")
fi
if [[ "${existing_pid}" =~ ^[0-9]+$ ]] && kill -0 "${existing_pid}" 2>/dev/null; then
  echo "DoHBrw2020 worker already active: ${existing_pid}" >&2
  exit 3
fi

printf '%s\n' "$$" > "${QUEUE_ROOT}/status/dohbrw2020.pid"
printf 'running\n' > "${QUEUE_ROOT}/status/dohbrw2020.status"
date -u +%FT%TZ > "${QUEUE_ROOT}/status/dohbrw2020.resume_started_at"
write_queue_tsv
write_active_status

bash "${WORKDIR}/run_caeos_dohbrw2020_full_label_alignment.sh" \
  > "${QUEUE_ROOT}/logs/dohbrw2020.complete_flows_r16.stdout.log" \
  2> "${QUEUE_ROOT}/logs/dohbrw2020.complete_flows_r16.stderr.log"
code=$?

printf '%s\n' "${code}" > "${QUEUE_ROOT}/status/dohbrw2020.exit_code"
date -u +%FT%TZ > "${QUEUE_ROOT}/status/dohbrw2020.finished_at"
if [[ ${code} -eq 0 ]] && [[ -s "${DOH_RUN_ROOT}/summary.json" ]]; then
  if "${PYTHON}" -c 'import json,sys; d=json.load(open(sys.argv[1], encoding="utf-8")); raise SystemExit(0 if d.get("formal_label_gate_passed") is True and d.get("processed_source_count") == d.get("source_count") else 1)' "${DOH_RUN_ROOT}/summary.json"; then
    printf 'complete\n' > "${QUEUE_ROOT}/status/dohbrw2020.status"
  elif "${PYTHON}" -c 'import json,sys; d=json.load(open(sys.argv[1], encoding="utf-8")); raise SystemExit(0 if d.get("source_quality_adjusted_gate_passed") is True and d.get("processed_source_count") == d.get("source_count") else 1)' "${DOH_RUN_ROOT}/summary.json"; then
    printf 'usable_with_source_quality_exceptions\n' > "${QUEUE_ROOT}/status/dohbrw2020.status"
  else
    printf 'processed_gate_failed\n' > "${QUEUE_ROOT}/status/dohbrw2020.status"
  fi
else
  printf 'failed\n' > "${QUEUE_ROOT}/status/dohbrw2020.status"
fi
write_queue_tsv
write_active_status
exit "${code}"
