#!/usr/bin/env bash
set -euo pipefail

code_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14"
output_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5"
control_root="${output_root}/_control/feature_extraction"
launcher="${code_root}/scripts/run_caeos_unified_feature_extraction_v5_additional_lane.sh"
formal_log="${control_root}/formal_v5_schema_v4_edge_final_fix_20260807.log"
supervisor_log="${control_root}/four_lane_supervisor_20260807.log"
legacy_pid_file="${control_root}/legacy_main.pid"
label_index_manifest="${output_root}/_control/label_index_manifest.json"
source_manifest="${output_root}/_control/source_manifest.json"
catalog="${code_root}/configs/unified_multimodal_v5_split_class.datasets.json"
queue=(cic_bot_iot cicddos2019 cicids2017 cicids2018 unsw_nb15 5gad_2022 cic_ton_iot dohbrw2020 ciciot2023)
target_dataset_concurrency=5
lanes=(lane1 lane2 lane3 lane4 lane5)
declare -A retry_after=()

mkdir -p "${control_root}"
exec 9>"/tmp/caeos_unified_feature_extraction_v5_five_lane_supervisor.lock"
if ! flock -n 9; then
    echo '{"event":"launch_rejected","reason":"feature_supervisor_already_running"}' >&2
    exit 73
fi

log_event() {
    printf '%s %s\n' "$(date --iso-8601=seconds)" "$1" >> "${supervisor_log}"
}

root_dataset_processes() {
    ps -eo pid=,ppid=,comm=,args= |
        awk '$3 ~ /^python/ && $0 ~ /prepare_caeos_splitpcap_class_csv(_legacy_cicddos)?[.]py/ {
                 active[$1] = 1; parent[$1] = $2; line[$1] = $0
             }
             END {
                 for (pid in active) if (!(parent[pid] in active)) print pid "\t" line[pid]
             }'
}

dataset_is_complete() {
    local dataset_id="$1"
    local manifest="${output_root}/${dataset_id}/dataset.manifest.json"
    [[ -f "${manifest}" ]] &&
        /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python -c \
            'import json,sys; raise SystemExit(0 if json.load(open(sys.argv[1], encoding="utf-8")).get("complete") else 1)' \
            "${manifest}"
}

dataset_is_admitted() {
    local dataset_id="$1"
    /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python -c '
import json, sys

dataset_id, label_path, source_path, catalog_path = sys.argv[1:]
labels = json.load(open(label_path, encoding="utf-8"))
sources = json.load(open(source_path, encoding="utf-8"))
catalog = json.load(open(catalog_path, encoding="utf-8"))
label_ready = any(
    item.get("id") == dataset_id and item.get("status") == "ready"
    for item in labels.get("datasets", [])
)
source_ready = any(item.get("id") == dataset_id for item in sources.get("datasets", []))
catalog_ready = any(item.get("id") == dataset_id for item in catalog.get("datasets", []))
raise SystemExit(0 if label_ready and source_ready and catalog_ready else 1)
' "${dataset_id}" "${label_index_manifest}" "${source_manifest}" "${catalog}"
}

legacy_main_finished_cicddos() {
    local legacy_pid
    [[ -f "${legacy_pid_file}" ]] || return 1
    legacy_pid="$(cat "${legacy_pid_file}")"
    kill -0 "${legacy_pid}" 2>/dev/null || return 1
    grep -q '"dataset_id": "cicddos2019".*"event": "dataset_complete"' "${formal_log}"
}

stop_legacy_main_after_cicddos() {
    local legacy_pid
    legacy_pid="$(cat "${legacy_pid_file}")"
    kill -TERM "${legacy_pid}"
    log_event "{\"event\":\"legacy_main_stop_requested\",\"pid\":${legacy_pid},\"after_dataset\":\"cicddos2019\"}"
}

active_single_datasets() {
    local row args dataset_count dataset_id
    while IFS=$'\t' read -r _pid row; do
        [[ -n "${row:-}" ]] || continue
        args=" ${row} "
        dataset_count="$(grep -o -- ' --dataset ' <<< "${args}" | wc -l)"
        if (( dataset_count == 1 )); then
            dataset_id="$(sed -n 's/.* --dataset \([^ ]*\).*/\1/p' <<< "${args}")"
            [[ -n "${dataset_id}" ]] && printf '%s\n' "${dataset_id}"
        elif [[ -f "${legacy_pid_file}" ]] && [[ "${_pid}" == "$(cat "${legacy_pid_file}")" ]]; then
            printf '%s\n' cicddos2019
        fi
    done < <(root_dataset_processes)
}

lane_is_free() {
    local lane="$1"
    local pid_file="${control_root}/${lane}.pid"
    local pid
    [[ -f "${pid_file}" ]] || return 0
    pid="$(cat "${pid_file}")"
    ! kill -0 "${pid}" 2>/dev/null
}

choose_next_dataset() {
    local active_list="$1"
    local dataset_id now
    now="$(date +%s)"
    for dataset_id in "${queue[@]}"; do
        dataset_is_complete "${dataset_id}" && continue
        dataset_is_admitted "${dataset_id}" || continue
        grep -qxF "${dataset_id}" <<< "${active_list}" && continue
        if (( now < ${retry_after[${dataset_id}]:-0} )); then
            continue
        fi
        printf '%s\n' "${dataset_id}"
        return 0
    done
    return 1
}

log_event "{\"event\":\"supervisor_started\",\"target_dataset_concurrency\":${target_dataset_concurrency}}"
while true; do
    if legacy_main_finished_cicddos; then
        stop_legacy_main_after_cicddos
        sleep 2
    fi

    mapfile -t roots < <(root_dataset_processes)
    active_count="${#roots[@]}"
    active_list="$(active_single_datasets || true)"

    if (( active_count < target_dataset_concurrency )); then
        for lane in "${lanes[@]}"; do
            (( active_count < target_dataset_concurrency )) || break
            lane_is_free "${lane}" || continue
            if ! dataset_id="$(choose_next_dataset "${active_list}")"; then
                continue
            fi
            run_log="${control_root}/${lane}_${dataset_id}_supervised_$(date +%Y%m%dT%H%M%S).log"
            if [[ "${dataset_id}" == cicddos2019 ]]; then
                setsid -f bash "${code_root}/scripts/run_caeos_cicddos2019_legacy_resume.sh" 9>&- > "${run_log}" 2>&1
            else
                setsid -f bash "${launcher}" "${lane}" "${dataset_id}" 9>&- > "${run_log}" 2>&1
            fi
            sleep 5
            refreshed_active_list="$(active_single_datasets || true)"
            if grep -qxF "${dataset_id}" <<< "${refreshed_active_list}"; then
                log_event "{\"event\":\"dataset_launched\",\"lane\":\"${lane}\",\"dataset_id\":\"${dataset_id}\",\"log\":\"${run_log}\"}"
                retry_after["${dataset_id}"]="$(( $(date +%s) + 300 ))"
                active_list="${active_list}"$'\n'"${dataset_id}"
                ((active_count += 1))
            else
                retry_after["${dataset_id}"]="$(( $(date +%s) + 900 ))"
                log_event "{\"event\":\"dataset_launch_failed\",\"lane\":\"${lane}\",\"dataset_id\":\"${dataset_id}\",\"retry_after_seconds\":900,\"log\":\"${run_log}\"}"
            fi
        done
    fi

    all_queued_complete=true
    for dataset_id in "${queue[@]}"; do
        if ! dataset_is_complete "${dataset_id}"; then
            all_queued_complete=false
            break
        fi
    done
    if [[ "${all_queued_complete}" == true ]]; then
        log_event '{"event":"supervisor_complete","reason":"queued_datasets_complete"}'
        exit 0
    fi
    sleep 15
done
