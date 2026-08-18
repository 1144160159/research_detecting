#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/DoHBrw2020
RUN_ROOT=${DATASET}/derived/caeos_dohbrw2020_complete_flows_r16
INDEX=${DATASET}/derived/caeos_dohbrw2020_r14/label_processing/label_indices/dohbrw2020.sqlite
EXPECTED_INDEX_SHA256=7e619a5679038c38e571dc9a4f112ff3ee490c19f9edee68563121c618d1e278
SOURCE_QUALITY_POLICY=${WORKDIR}/configs/dohbrw2020_complete_flow_policy_r16.json

mkdir -p "${RUN_ROOT}/audits/per_source" "${RUN_ROOT}/logs" "${RUN_ROOT}/temporary"
cd "${WORKDIR}"
[[ -s "${INDEX}" ]]
[[ -s "${SOURCE_QUALITY_POLICY}" ]]
INDEX_SHA256=$(sha256sum "${INDEX}" | cut -d' ' -f1)
[[ "${INDEX_SHA256}" == "${EXPECTED_INDEX_SHA256}" ]]
"${PYTHON}" -u validate_caeos_label_index.py \
  --path "${INDEX}" --dataset-id dohbrw2020 --group-counts \
  --output "${RUN_ROOT}/audits/dohbrw2020_label_index_validation_complete_flows_r16.json"

exec "${PYTHON}" -u audit_caeos_all_pcap_members.py \
  --dataset-id dohbrw2020 --dataset-root "${DATASET}" \
  --archive-root "${DATASET}/PCAPs" --archive-member-mode pcap_suffix \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --inventory-output "${RUN_ROOT}/inventory.json" \
  --audit-dir "${RUN_ROOT}/audits/per_source" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --temporary-dir "${RUN_ROOT}/temporary" \
  --source-quality-policy "${SOURCE_QUALITY_POLICY}" \
  --tolerance-ns 1000000 --idle-seconds 30 \
  --summarize-existing-only
