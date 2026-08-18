#!/usr/bin/env bash
set -euo pipefail

code_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14"
output_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5"
python_bin="/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"

cd "${code_root}"
exec "${python_bin}" -u prepare_caeos_splitpcap_class_csv_legacy_cicddos.py \
    --catalog configs/unified_multimodal_v5_split_class.datasets.json \
    --schema configs/unified_multimodal_v4.schema.json \
    --source-manifest "${output_root}/_control/source_manifest.json" \
    --label-index-manifest "${output_root}/_control/label_index_manifest.json" \
    --pcap-repair-manifest "${output_root}/_control/pcap_repair_manifest.json" \
    --label-boundary-repair-manifest configs/cicddos2019_label_boundary_repairs.v1.json \
    --output-root "${output_root}" \
    --completion-path "${output_root}/_control/feature_extraction/completion.legacy_cicddos2019.json" \
    --dataset cicddos2019 \
    --splitpcap-binary /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/splitpcap-fca18e270fe4/bin/splitpcap \
    --splitpcap-commit fca18e270fe4 \
    --target-piece-bytes 134217728 \
    --split-threshold-bytes 268435456 \
    --maximum-pieces-per-capture 256 \
    --cpu-worker-cap 6 \
    --memory-budget-gib 88 \
    --memory-reserve-gib 16 \
    --estimated-worker-gib 6 \
    --memory-safety-factor 2 \
    --maximum-active-flows 6000 \
    --packet-decoder tshark \
    --tshark-binary /usr/bin/tshark \
    --tshark-session-reset-packets 0
