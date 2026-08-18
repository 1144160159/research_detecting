#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
RUN_ROOT=/tmp/caeos-four-new-label-datasets-r20
mkdir -p "${RUN_ROOT}/logs" "${RUN_ROOT}/status" "${RUN_ROOT}/pids"

RUNNERS=(
  run_caeos_5gad2022_full_label_alignment.sh
  run_caeos_unsw_nb15_full_label_alignment.sh
  run_caeos_cicids2018_exact_flow_regeneration.sh
  run_caeos_cert_insider_full_label_join.sh
)
for runner in "${RUNNERS[@]}" run_caeos_label_dataset_worker.sh; do
  [[ -r "${WORKDIR}/${runner}" ]] || { echo "missing runner: ${runner}" >&2; exit 2; }
done

bash "${WORKDIR}/run_caeos_label_dataset_worker.sh" 5gad_2022 "${RUNNERS[0]}" complete &
printf '%s\n' "$!" >"${RUN_ROOT}/pids/5gad_2022.pid"
bash "${WORKDIR}/run_caeos_label_dataset_worker.sh" unsw_nb15 "${RUNNERS[1]}" complete &
printf '%s\n' "$!" >"${RUN_ROOT}/pids/unsw_nb15.pid"
bash "${WORKDIR}/run_caeos_label_dataset_worker.sh" cicids2018 "${RUNNERS[2]}" waiting_for_exact_official_label_join &
printf '%s\n' "$!" >"${RUN_ROOT}/pids/cicids2018.pid"
bash "${WORKDIR}/run_caeos_label_dataset_worker.sh" cert_insider_threat "${RUNNERS[3]}" complete &
printf '%s\n' "$!" >"${RUN_ROOT}/pids/cert_insider_threat.pid"

set +e
wait
code=$?
set -e
if [[ ${code} -eq 0 ]]; then
  printf '%s\n' complete >"${RUN_ROOT}/launcher.status"
else
  printf '%s\n' failed >"${RUN_ROOT}/launcher.status"
fi
exit "${code}"
