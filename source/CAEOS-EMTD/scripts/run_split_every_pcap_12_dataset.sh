#!/usr/bin/env bash
set -euo pipefail

dataset="${1:?usage: $0 DATASET [RUN_ID]}"
run_id="${2:-split_every_pcap_12_20260815}"

case "${dataset}" in
    cicids2018|cic_bot_iot) ;;
    *)
        printf 'unsupported dataset: %s\n' "${dataset}" >&2
        exit 64
        ;;
esac

code_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14"
output_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5"
python_bin="/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
splitpcap_bin="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/splitpcap-fca18e270fe4-next-ex/bin/splitpcap"
control_root="${output_root}/_control/feature_extraction"
log_root="${control_root}/${run_id}"

mkdir -p "${log_root}"
cd "${code_root}"

exec "${python_bin}" -u prepare_caeos_splitpcap_class_csv.py \
    --catalog configs/unified_multimodal_v5_split_class.datasets.json \
    --schema configs/unified_multimodal_v4.schema.json \
    --source-manifest "${output_root}/_control/source_manifest.json" \
    --label-index-manifest "${output_root}/_control/label_index_manifest.json" \
    --pcap-repair-manifest "${output_root}/_control/pcap_repair_manifest.json" \
    --output-root "${output_root}" \
    --completion-path "${control_root}/completion.${run_id}.${dataset}.json" \
    --dataset "${dataset}" \
    --splitpcap-binary "${splitpcap_bin}" \
    --splitpcap-commit fca18e270fe4 \
    --target-piece-bytes 134217728 \
    --split-threshold-bytes 1 \
    --minimum-pieces-per-capture 12 \
    --maximum-pieces-per-capture 256 \
    --cpu-worker-cap 12 \
    --small-capture-concurrency 1 \
    --large-capture-concurrency 1 \
    --large-capture-worker-cap 12 \
    --dataset-worker-budget 12 \
    --memory-budget-gib 160 \
    --memory-reserve-gib 16 \
    --estimated-worker-gib 6 \
    --memory-safety-factor 2 \
    --maximum-active-flows 6000 \
    --packet-decoder tshark \
    --tshark-binary /usr/bin/tshark \
    --tshark-session-reset-packets 0
