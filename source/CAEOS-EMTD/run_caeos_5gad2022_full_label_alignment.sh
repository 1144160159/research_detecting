#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/5GAD-2022
RUN_ROOT=/tmp/caeos-5gad-2022-all-pcap-r19
INDEX=${RUN_ROOT}/label_indices/5gad_2022.sqlite
SELECTION=${RUN_ROOT}/selected_pcaps

mkdir -p "${RUN_ROOT}/label_indices" "${RUN_ROOT}/audits/per_source" \
  "${RUN_ROOT}/logs" "${RUN_ROOT}/temporary" "${SELECTION}"
cd "${WORKDIR}"

if [[ ! -s "${INDEX}" ]]; then
  "${PYTHON}" -u build_caeos_5gad2022_label_index.py \
    --dataset-root "${DATASET}" \
    --registry configs/unified_multimodal_v5.labels.json \
    --output-index "${INDEX}" \
    --audit-output "${RUN_ROOT}/audits/5gad_2022_label_index_r19.json"
fi

find "${SELECTION}" -type l -delete
while IFS= read -r -d '' source; do
  relative=${source#"${DATASET}/"}
  link=${relative//\//__}
  ln -s "${source}" "${SELECTION}/${link}"
done < <(
  find "${DATASET}/repository/Normal-2UE" -maxdepth 1 -type f -name '*.pcapng' -print0
  find "${DATASET}/repository/Attacks" -mindepth 2 -maxdepth 2 -type f -name 'Attacks_*.pcapng' -print0
)

INDEX_SHA256=$(sha256sum "${INDEX}" | cut -d' ' -f1)
"${PYTHON}" -u validate_caeos_label_index.py \
  --path "${INDEX}" --dataset-id 5gad_2022 --group-counts \
  --output "${RUN_ROOT}/audits/5gad_2022_label_index_validation_r19.json"

exec "${PYTHON}" -u audit_caeos_all_pcap_members.py \
  --dataset-id 5gad_2022 --dataset-root "${DATASET}" \
  --pcap-root "${SELECTION}" \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --inventory-output "${RUN_ROOT}/inventory.json" \
  --audit-dir "${RUN_ROOT}/audits/per_source" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --temporary-dir "${RUN_ROOT}/temporary" \
  --tolerance-ns 1000000 --idle-seconds 30 \
  --authority-granularity documented_single_class_capture \
  --conflict-policy reject
