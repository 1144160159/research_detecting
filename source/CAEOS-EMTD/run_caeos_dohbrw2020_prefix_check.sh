#!/usr/bin/env bash
set -uo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
RUN_ROOT=/tmp/caeos-dohbrw2020

mkdir -p "${RUN_ROOT}/label_indices" "${RUN_ROOT}/audits" "${RUN_ROOT}/logs"
exec </dev/null > "${RUN_ROOT}/logs/runner.stdout.log" 2> "${RUN_ROOT}/logs/runner.stderr.log"
echo "$$" > "${RUN_ROOT}/builder.pid"
rm -f "${RUN_ROOT}/build_exit_code"

cd "${WORKDIR}"
set +e
"${PYTHON}" -u build_caeos_dohbrw2020_label_index.py \
  --total-dir /opt/data/private/wangwt/ParkAttackKE/datasets/cic/DoHBrw2020/CSVs/Total_CSVs \
  --tool-csv-root /opt/data/private/wangwt/ParkAttackKE/datasets/cic/DoHBrw2020/CSVs/CSVs \
  --registry configs/unified_multimodal_v5.labels.json \
  --output-index "${RUN_ROOT}/label_indices/dohbrw2020.sqlite" \
  --audit-output "${RUN_ROOT}/audits/dohbrw2020_label_index_r14.json" \
  --resolver-tolerance-ns 1000000 \
  >> "${RUN_ROOT}/logs/build.stdout.json" \
  2>> "${RUN_ROOT}/logs/build.stderr.log"
code=$?
set -e
echo "${code}" > "${RUN_ROOT}/build_exit_code"
exit "${code}"
