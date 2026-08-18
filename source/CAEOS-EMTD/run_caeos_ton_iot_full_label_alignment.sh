#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT
RUN_ROOT=/tmp/caeos-ton-iot-all-pcap-r15
INDEX=${RUN_ROOT}/label_indices/ton_iot.sqlite

mkdir -p "${RUN_ROOT}/label_indices" "${RUN_ROOT}/audits/per_source" "${RUN_ROOT}/logs" "${RUN_ROOT}/temporary"
cd "${WORKDIR}"

if [[ ! -s "${INDEX}" ]]; then
  "${PYTHON}" -u build_caeos_ton_iot_label_index.py \
    --processed-dir "${DATASET}/Processed_datasets/Processed_Network_dataset" \
    --ground-truth-dir "${DATASET}/SecuityEvents_GroundTruth_datasets/SecurityEvents_Network_datasets" \
    --registry configs/unified_multimodal_v5.labels.json \
    --output-index "${INDEX}" \
    --audit-output "${RUN_ROOT}/audits/ton_iot_label_index_r15.json" \
    --resolver-tolerance-ns 1000000000
fi
INDEX_SHA256=$(sha256sum "${INDEX}" | cut -d' ' -f1)
"${PYTHON}" -u validate_caeos_label_index.py \
  --path "${INDEX}" --dataset-id cic_ton_iot --group-counts \
  --output "${RUN_ROOT}/audits/ton_iot_label_index_validation_r15.json"
"${PYTHON}" -u audit_caeos_ton_iot_official_event_coverage.py \
  --ground-truth-dir "${DATASET}/SecuityEvents_GroundTruth_datasets/SecurityEvents_Network_datasets" \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --output "${RUN_ROOT}/audits/ton_iot_official_event_coverage_r15.json"
"${PYTHON}" - "${RUN_ROOT}/audits/ton_iot_official_event_coverage_r15.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report.get("coverage_fraction") != 1.0:
    raise SystemExit("ToN-IoT official malicious event coverage is not exact")
if report.get("ground_truth_counters", {}).get("invalid_ground_truth_rows", 0) != 0:
    raise SystemExit("ToN-IoT official ground truth contains invalid rows")
PY

exec "${PYTHON}" -u audit_caeos_all_pcap_members.py \
  --dataset-id cic_ton_iot --dataset-root "${DATASET}" \
  --pcap-root "${DATASET}/Raw_datasets/network_data/Network_dataset_pcaps" \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --inventory-output "${RUN_ROOT}/inventory.json" \
  --audit-dir "${RUN_ROOT}/audits/per_source" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --temporary-dir "${RUN_ROOT}/temporary" \
  --tolerance-ns 1000000000 --idle-seconds 30
