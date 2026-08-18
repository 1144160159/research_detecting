#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
RUN_ROOT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5/_control/audits/cicids2018_strict_r22_20260808
REGENERATED=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cse_cic_ids2018/derived/caeos_flow_identity_r20
MARKERS=/tmp/caeos-cicids2018-all-pcap-r20/audits/archives

mkdir -p "${RUN_ROOT}/per_day"
rm -f "${RUN_ROOT}/audit.done"
cd "${WORKDIR}"
if "${PYTHON}" -u audit_caeos_cicids2018_regenerated_flows.py \
  --schedule configs/cicids2018_official_attack_schedule.json \
  --generated-root "${REGENERATED}" \
  --archive-markers "${MARKERS}" \
  --per-day-dir "${RUN_ROOT}/per_day" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --workers 2 >"${RUN_ROOT}/audit.log" 2>&1; then
  printf '0\n' >"${RUN_ROOT}/audit.done"
else
  printf '1\n' >"${RUN_ROOT}/audit.done"
fi
