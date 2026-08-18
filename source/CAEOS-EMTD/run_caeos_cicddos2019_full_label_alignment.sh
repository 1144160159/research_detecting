#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CICDDoS2019
RUN_ROOT=/tmp/caeos-cicddos2019-all-pcap-r14
INDEX=/tmp/caeos-cicddos2019/label_indices/cicddos2019.sqlite

mkdir -p "${RUN_ROOT}/audits/per_source" "${RUN_ROOT}/logs" "${RUN_ROOT}/temporary"
cd "${WORKDIR}"
[[ -s "${INDEX}" ]]
INDEX_SHA256=$(sha256sum "${INDEX}" | cut -d' ' -f1)
"${PYTHON}" -u validate_caeos_label_index.py \
  --path "${INDEX}" --dataset-id cicddos2019 --group-counts \
  --require-protocol-distribution \
  --output "${RUN_ROOT}/audits/cicddos2019_label_index_validation_r14.json"

exec "${PYTHON}" -u audit_caeos_all_pcap_members.py \
  --dataset-id cicddos2019 --dataset-root "${DATASET}" \
  --archive-root "${DATASET}/PCAPs" --archive-member-mode all_files \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --inventory-output "${RUN_ROOT}/inventory.json" \
  --audit-dir "${RUN_ROOT}/audits/per_source" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --temporary-dir "${RUN_ROOT}/temporary" \
  --tolerance-ns 2000000 --idle-seconds 30 \
  --official-boundary-split
