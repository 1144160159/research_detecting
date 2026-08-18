#!/usr/bin/env bash
set -euo pipefail

code_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14"
output_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5"
python_bin="/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
splitpcap_bin="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/splitpcap-fca18e270fe4/bin/splitpcap"
control_root="${output_root}/_control/feature_extraction"

mkdir -p "${control_root}"
exec 9>"/tmp/caeos_unified_feature_extraction_v5.lock"
if ! flock -n 9; then
    echo '{"event":"launch_rejected","reason":"feature_extraction_already_running"}' >&2
    exit 73
fi

printf '%s\n' "$$" > "${control_root}/pid"
printf '%s\n' "$(date --iso-8601=seconds)" > "${control_root}/started_at"
cd "${code_root}"

exec "${python_bin}" -u prepare_caeos_splitpcap_class_csv.py \
    --catalog configs/unified_multimodal_v5_split_class.datasets.json \
    --schema configs/unified_multimodal_v4.schema.json \
    --source-manifest "${output_root}/_control/source_manifest.json" \
    --label-index-manifest "${output_root}/_control/label_index_manifest.json" \
    --pcap-repair-manifest "${output_root}/_control/pcap_repair_manifest.json" \
    --output-root "${output_root}" \
    --dataset edge_iiotset \
    --dataset cicddos2019 \
    --dataset cic_ton_iot \
    --dataset cicids2017 \
    --dataset ciciot2022 \
    --dataset cic_bot_iot \
    --dataset dohbrw2020 \
    --dataset ciciot2023 \
    --splitpcap-binary "${splitpcap_bin}" \
    --splitpcap-commit fca18e270fe4 \
    --target-piece-bytes 134217728 \
    --split-threshold-bytes 268435456 \
    --maximum-pieces-per-capture 256 \
    --cpu-worker-cap 24 \
    --memory-budget-gib 190 \
    --memory-reserve-gib 46 \
    --estimated-worker-gib 6 \
    --memory-safety-factor 2 \
    --maximum-active-flows 6000 \
    --packet-decoder tshark \
    --tshark-binary /usr/bin/tshark \
    --tshark-session-reset-packets 0
