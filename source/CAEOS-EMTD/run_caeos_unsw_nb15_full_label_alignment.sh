#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/UNSW-NB15
RUN_ROOT=/tmp/caeos-unsw-nb15-all-pcap-r19
INDEX=${RUN_ROOT}/label_indices/unsw_nb15.sqlite

mkdir -p "${RUN_ROOT}/label_indices" "${RUN_ROOT}/audits/per_source" \
  "${RUN_ROOT}/logs" "${RUN_ROOT}/temporary"
cd "${WORKDIR}"

if [[ ! -s "${INDEX}" ]]; then
  "${PYTHON}" -u build_caeos_unsw_nb15_label_index.py \
    --csv-dir "${DATASET}/CSVs/CSV Files" \
    --registry configs/unified_multimodal_v5.labels.json \
    --output-index "${INDEX}" \
    --audit-output "${RUN_ROOT}/audits/unsw_nb15_label_index_r19.json"
fi

INDEX_SHA256=$(sha256sum "${INDEX}" | cut -d' ' -f1)
"${PYTHON}" -u validate_caeos_label_index.py \
  --path "${INDEX}" --dataset-id unsw_nb15 --group-counts \
  --require-protocol-distribution \
  --output "${RUN_ROOT}/audits/unsw_nb15_label_index_validation_r19.json"

exec "${PYTHON}" -u audit_caeos_all_pcap_members.py \
  --dataset-id unsw_nb15 --dataset-root "${DATASET}" \
  --pcap-root "${DATASET}/PCAPs" \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --inventory-output "${RUN_ROOT}/inventory.json" \
  --audit-dir "${RUN_ROOT}/audits/per_source" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --temporary-dir "${RUN_ROOT}/temporary" \
  --tolerance-ns 1000000000 --idle-seconds 30 \
  --conflict-policy malicious_over_benign_bidirectional \
  --conflict-exclusion-policy binary_malicious_consensus_multiclass_ambiguous \
  --conflict-exclusion-evidence \
  /tmp/caeos-unsw-nb15-conflict-recovery-r21/audits/unsw_nb15_conflict_inventory_manifest.json
