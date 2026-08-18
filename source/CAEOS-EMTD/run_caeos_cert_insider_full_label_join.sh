#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
ARCHIVE=/opt/data/private/wangwt/ParkAttackKE/datasets/cert/cert_insider_threat/raw/12841247.zip
RUN_ROOT=/tmp/caeos-cert-insider-threat-r20
OUTPUT_ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/cert/cert_insider_threat/derived/caeos_labels_r20

mkdir -p "${RUN_ROOT}/audits" "${RUN_ROOT}/logs" "${OUTPUT_ROOT}"
cd "${WORKDIR}"

"${PYTHON}" -u build_caeos_cert_insider_label_manifest.py \
  --archive "${ARCHIVE}" \
  --output "${RUN_ROOT}/audits/label_manifest.json" >/dev/null

exec "${PYTHON}" -u label_caeos_cert_insider_events.py \
  --archive "${ARCHIVE}" \
  --label-manifest "${RUN_ROOT}/audits/label_manifest.json" \
  --output-root "${OUTPUT_ROOT}" \
  --checkpoint "${RUN_ROOT}/audits/event_join_checkpoint.json"
