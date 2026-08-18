#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
RUN_ROOT=/tmp/caeos-bot-iot-all-pcap-r15

mkdir -p "${RUN_ROOT}/audits" "${RUN_ROOT}/logs"
exec </dev/null > "${RUN_ROOT}/logs/runner.stdout.log" 2> "${RUN_ROOT}/logs/runner.stderr.log"
echo "$$" > "${RUN_ROOT}/runner.pid"
rm -f "${RUN_ROOT}/exit_code"

cd "${WORKDIR}"
set +e
"${PYTHON}" -u audit_caeos_bot_iot_all_pcaps.py \
  --pcap-root /opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-BoT-IoT/PCAPs \
  --dataset-root /opt/data/private/wangwt/ParkAttackKE/datasets \
  --label-index /tmp/caeos-label-index-p_7_v3j3/labels.sqlite \
  --label-index-sha256 82033309ca0450e5a5c0f6ed4cf76d2098ee3bcbbcf9afb0a5c78f3e14df355e \
  --audit-dir "${RUN_ROOT}/audits" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --tolerance-ns 1000000 \
  --idle-seconds 30 \
  --maximum-unmatched-samples 100 \
  >> "${RUN_ROOT}/logs/stdout.jsonl" \
  2>> "${RUN_ROOT}/logs/stderr.log"
code=$?
set -e
echo "${code}" > "${RUN_ROOT}/exit_code"
exit "${code}"
