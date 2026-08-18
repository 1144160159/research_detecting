#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
ARCHIVE=/opt/data/private/wangwt/ParkAttackKE/datasets/cert/cert_insider_threat/raw/12841247.zip
RUN_ROOT=/tmp/caeos-cert-insider-threat-r19

mkdir -p "${RUN_ROOT}/audits" "${RUN_ROOT}/logs"
cd "${WORKDIR}"
exec "${PYTHON}" -u build_caeos_cert_insider_label_manifest.py \
  --archive "${ARCHIVE}" \
  --output "${RUN_ROOT}/audits/label_manifest.json"
