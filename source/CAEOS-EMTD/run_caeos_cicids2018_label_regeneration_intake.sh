#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
RUN_ROOT=/tmp/caeos-four-new-label-datasets-r19
DATASET_RUN_ROOT=/tmp/caeos-cicids2018-all-pcap-r19
FLOWMETER=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/CICFlowMeter/target/CICFlowMeterV3-0.0.4-SNAPSHOT.jar

mkdir -p "${DATASET_RUN_ROOT}/audits" "${DATASET_RUN_ROOT}/logs"
cd "${WORKDIR}"
exec "${PYTHON}" -u create_caeos_cicids2018_label_regeneration_protocol.py \
  --intake "${RUN_ROOT}/intake.json" \
  --flowmeter-jar "${FLOWMETER}" \
  --output "${DATASET_RUN_ROOT}/audits/regeneration_protocol.json"
