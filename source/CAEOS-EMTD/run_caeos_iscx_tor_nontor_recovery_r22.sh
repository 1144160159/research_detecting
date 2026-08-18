#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
SOURCE_MANIFEST=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5/_control/source_manifest.json
RUN_ROOT=/tmp/caeos-iscx-tor-nontor-2017-all-pcap-r18
RECOVERY_ROOT=/tmp/caeos-iscx-tor-nontor-recovery-r22
GROUP_STATUS=/tmp/caeos-four-benign-dataset-strict-queue-r18/status.tsv

mkdir -p "${RECOVERY_ROOT}/logs" "${RECOVERY_ROOT}/temporary"

set_status() {
  local state=$1
  local pid=$2
  printf 'iscx_tor_nontor_2017\t%s\t%s\n' "${state}" "${pid}" \
    > "${RECOVERY_ROOT}/status.tsv.tmp"
  mv "${RECOVERY_ROOT}/status.tsv.tmp" "${RECOVERY_ROOT}/status.tsv"
  "${PYTHON}" - "${GROUP_STATUS}" "${state}" "${pid}" <<'PY'
from pathlib import Path
import os
import sys

path = Path(sys.argv[1])
state = sys.argv[2]
pid = sys.argv[3]
rows = []
if path.is_file():
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
replacement = f"iscx_tor_nontor_2017\t{state}\t{pid}"
rows = [
    replacement if row.split("\t", 1)[0] == "iscx_tor_nontor_2017" else row
    for row in rows
]
if not any(row.split("\t", 1)[0] == "iscx_tor_nontor_2017" for row in rows):
    rows.append(replacement)
temporary = path.with_suffix(path.suffix + ".r22.tmp")
temporary.write_text("\n".join(rows) + "\n", encoding="utf-8")
os.replace(temporary, path)
PY
}

finish() {
  local rc=$?
  trap - EXIT
  if [[ ${rc} -eq 0 ]] && "${PYTHON}" - "${RUN_ROOT}/summary.json" <<'PY'
import json
import sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
raise SystemExit(0 if value.get("formal_dataset_gate_passed") is True else 1)
PY
  then
    set_status complete "$$"
    exit 0
  fi
  set_status failed "$$"
  exit "${rc:-1}"
}
trap finish EXIT

set_status running "$$"
cd "${WORKDIR}"
"${PYTHON}" -u audit_caeos_benign_capture_dataset.py \
  --dataset-id iscx_tor_nontor_2017 \
  --source-manifest "${SOURCE_MANIFEST}" \
  --run-root "${RUN_ROOT}" \
  --temp-root "${RECOVERY_ROOT}/temporary" \
  --summary-interval 1
