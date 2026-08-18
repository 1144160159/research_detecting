#!/usr/bin/env bash
set -uo pipefail

root=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD
data_root="${root}/datasets/caeos_unified_multimodal_v5"
code_root="${root}/paper_protocols/caeos_paper_closure_v3"
control_root="${data_root}/_control/paper_protocol_v1/duplicate_audits"
scratch_root=/tmp/caeos_parallel_duplicate_audit_v2
python=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python

mkdir -p "${control_root}/logs" "${scratch_root}"
printf '%s\n' "$$" > "${control_root}/queue.pid"
rm -f "${control_root}/queue.exit"

ionice -c2 -n7 nice -n 10 "${python}" \
  "${code_root}/run_caeos_parallel_duplicate_audits.py" \
  --output-root "${data_root}" \
  --audit-script "${code_root}/audit_caeos_flow_duplicates.py" \
  --scratch-root "${scratch_root}" \
  --dataset-parallelism 2 \
  --class-parallelism 2 \
  --shards-per-class 8 \
  --buckets 256 \
  --dataset-attempts 4 \
  --retry-delay-seconds 60 \
  --status "${control_root}/queue.status.json" \
  --readiness-watcher "${code_root}/watch_caeos_paper_readiness_v1.sh" \
  >> "${control_root}/queue.log" 2>&1
rc=$?
printf '%s\n' "${rc}" > "${control_root}/queue.exit"
exit "${rc}"
