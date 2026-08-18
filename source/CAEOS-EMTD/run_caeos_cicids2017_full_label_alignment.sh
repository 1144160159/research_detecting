#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cicids2017
RUN_ROOT=/tmp/caeos-cicids2017-all-pcap-r14
INDEX=${RUN_ROOT}/label_indices/cicids2017.sqlite

mkdir -p "${RUN_ROOT}/label_indices" "${RUN_ROOT}/audits/per_source" "${RUN_ROOT}/logs" "${RUN_ROOT}/temporary"
cd "${WORKDIR}"

if [[ ! -s "${INDEX}" ]]; then
  "${PYTHON}" -u build_caeos_cicids2017_label_index.py \
    --labels-dir "${DATASET}/derived/GeneratedLabelledFlows" \
    --pcap-dir "${DATASET}/raw/PCAPs" \
    --source-root "${DATASET}" \
    --registry configs/unified_multimodal_v5.labels.json \
    --output-index "${INDEX}" \
    --audit-output "${RUN_ROOT}/audits/cicids2017_label_index_r14.json" \
    --tolerance-us 2000000 --offset-probe-packets 5000000
fi
INDEX_SHA256=$(sha256sum "${INDEX}" | cut -d' ' -f1)
"${PYTHON}" -u validate_caeos_label_index.py \
  --path "${INDEX}" --dataset-id cicids2017 --group-counts \
  --require-protocol-distribution \
  --output "${RUN_ROOT}/audits/cicids2017_label_index_validation_r14.json"
"${PYTHON}" - "${RUN_ROOT}/audits/cicids2017_label_index_r14.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report.get("ready_for_coverage_dry_run") is not True:
    raise SystemExit("CICIDS2017 label index is not ready for full PCAP coverage")
if int(report.get("flow_record_count", 0)) <= 0:
    raise SystemExit("CICIDS2017 label index contains no official flow records")
PY

exec "${PYTHON}" -u audit_caeos_all_pcap_members.py \
  --dataset-id cicids2017 --dataset-root "${DATASET}" \
  --pcap-root "${DATASET}/raw/PCAPs" \
  --label-index "${INDEX}" --label-index-sha256 "${INDEX_SHA256}" \
  --inventory-output "${RUN_ROOT}/inventory.json" \
  --audit-dir "${RUN_ROOT}/audits/per_source" \
  --summary-output "${RUN_ROOT}/summary.json" \
  --temporary-dir "${RUN_ROOT}/temporary" \
  --tolerance-ns 2000000000 --idle-seconds 30 \
  --conflict-policy malicious_over_benign_bidirectional
