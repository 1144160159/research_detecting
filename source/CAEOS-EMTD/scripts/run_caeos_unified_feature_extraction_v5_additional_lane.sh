#!/usr/bin/env bash
set -euo pipefail

if (( $# != 2 )); then
    echo "usage: $0 <lane1|lane2|lane3|lane4|lane5> <dataset_id>" >&2
    exit 64
fi

lane_id="$1"
dataset_id="$2"
case "${lane_id}" in
    lane1|lane2|lane3|lane4|lane5) ;;
    *) echo "unsupported lane: ${lane_id}" >&2; exit 64 ;;
esac
case "${dataset_id}" in
    ciciot2022|cic_bot_iot|cicddos2019|cic_ton_iot|cicids2017|cicids2018|unsw_nb15|5gad_2022|dohbrw2020|ciciot2023) ;;
    *) echo "unsupported additional-lane dataset: ${dataset_id}" >&2; exit 64 ;;
esac

code_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14"
output_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5"
python_bin="/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
splitpcap_bin="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/splitpcap-fca18e270fe4-next-ex/bin/splitpcap"
control_root="${output_root}/_control/feature_extraction"

mkdir -p "${control_root}"
exec 9>"/tmp/caeos_unified_feature_extraction_v5_${lane_id}.lock"
if ! flock -n 9; then
    printf '{"event":"launch_rejected","reason":"lane_already_running","lane":"%s"}\n' \
        "${lane_id}" >&2
    exit 73
fi

active_dataset_processes="$(
    ps -eo pid=,ppid=,comm=,args= |
        awk '$3 ~ /^python/ && $0 ~ /prepare_caeos_splitpcap_class_csv(_legacy_cicddos)?[.]py/ {
                 active[$1] = 1; parent[$1] = $2
             }
             END {
                 for (pid in active) if (!(parent[pid] in active)) count++
                 print count + 0
             }'
)"
if (( active_dataset_processes >= 5 )); then
    printf '{"event":"launch_rejected","reason":"dataset_concurrency_limit","active":%s,"limit":5}\n' \
        "${active_dataset_processes}" >&2
    exit 74
fi

printf '%s\n' "$$" > "${control_root}/${lane_id}.pid"
printf '%s\n' "$(date --iso-8601=seconds)" > "${control_root}/${lane_id}.started_at"
printf '%s\n' "${dataset_id}" > "${control_root}/${lane_id}.dataset"
cd "${code_root}"

case "${dataset_id}" in
    cicids2017|cic_ton_iot|dohbrw2020)
        export CAEOS_PREPROCESSOR_VARIANT=frozen_7caf
        ;;
    ciciot2023)
        export CAEOS_PREPROCESSOR_VARIANT=frozen_87f_tcp_ns_fix
        ;;
    cic_bot_iot)
        export CAEOS_PREPROCESSOR_VARIANT=frozen_87f_tcp_ns_fix
        ;;
    *)
        export CAEOS_PREPROCESSOR_VARIANT=current
        ;;
esac

target_piece_bytes=134217728
split_threshold_bytes=268435456
cpu_worker_cap=6
estimated_worker_gib=6
if [[ "${dataset_id}" == ciciot2023 ]]; then
    target_piece_bytes=67108864
    split_threshold_bytes=134217728
    cpu_worker_cap=28
    estimated_worker_gib=1
fi

exec "${python_bin}" -u prepare_caeos_splitpcap_class_csv.py \
    --catalog configs/unified_multimodal_v5_split_class.datasets.json \
    --schema configs/unified_multimodal_v4.schema.json \
    --source-manifest "${output_root}/_control/source_manifest.json" \
    --label-index-manifest "${output_root}/_control/label_index_manifest.json" \
    --pcap-repair-manifest "${output_root}/_control/pcap_repair_manifest.json" \
    --output-root "${output_root}" \
    --completion-path "${control_root}/completion.${lane_id}.${dataset_id}.json" \
    --dataset "${dataset_id}" \
    --splitpcap-binary "${splitpcap_bin}" \
    --splitpcap-commit fca18e270fe4 \
    --target-piece-bytes "${target_piece_bytes}" \
    --split-threshold-bytes "${split_threshold_bytes}" \
    --maximum-pieces-per-capture 256 \
    --cpu-worker-cap "${cpu_worker_cap}" \
    --memory-budget-gib 88 \
    --memory-reserve-gib 16 \
    --estimated-worker-gib "${estimated_worker_gib}" \
    --memory-safety-factor 2 \
    --maximum-active-flows 6000 \
    --packet-decoder tshark \
    --tshark-binary /usr/bin/tshark \
    --tshark-session-reset-packets 0 \
    --finalize-workers 2 \
    --finalize-row-workers 8 \
    --finalize-batch-rows 2048
