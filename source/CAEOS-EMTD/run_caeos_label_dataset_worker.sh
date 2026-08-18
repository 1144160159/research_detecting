#!/usr/bin/env bash
set -uo pipefail

[[ $# -eq 3 ]] || { echo "usage: $0 DATASET RUNNER SUCCESS_STATE" >&2; exit 2; }
DATASET=$1
RUNNER=$2
SUCCESS_STATE=$3
WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
RUN_ROOT=/tmp/caeos-four-new-label-datasets-r20

mkdir -p "${RUN_ROOT}/logs" "${RUN_ROOT}/status" "${RUN_ROOT}/pids"
exec 9>"${RUN_ROOT}/${DATASET}.lock"
flock -n 9 || exit 9

refresh_status() {
  exec 8>"${RUN_ROOT}/status.lock"
  flock 8
  local temporary=${RUN_ROOT}/status.tsv.tmp.${BASHPID}
  : >"${temporary}"
  local dataset runner state
  while read -r dataset runner; do
    state=queued
    [[ -r "${RUN_ROOT}/status/${dataset}" ]] && state=$(cat "${RUN_ROOT}/status/${dataset}")
    printf '%s\t%s\t%s\n' "${dataset}" "${state}" "${runner}" >>"${temporary}"
  done <<'EOF'
5gad_2022 run_caeos_5gad2022_full_label_alignment.sh
unsw_nb15 run_caeos_unsw_nb15_full_label_alignment.sh
cicids2018 run_caeos_cicids2018_exact_flow_regeneration.sh
cert_insider_threat run_caeos_cert_insider_full_label_join.sh
EOF
  mv "${temporary}" "${RUN_ROOT}/status.tsv"
  flock -u 8
}

printf '%s\n' running >"${RUN_ROOT}/status/${DATASET}"
date -u +%FT%TZ >"${RUN_ROOT}/status/${DATASET}.started_at"
refresh_status
nice -n 15 ionice -c 3 bash "${WORKDIR}/${RUNNER}" \
  >"${RUN_ROOT}/logs/${DATASET}.stdout.log" \
  2>"${RUN_ROOT}/logs/${DATASET}.stderr.log"
code=$?
printf '%s\n' "${code}" >"${RUN_ROOT}/status/${DATASET}.exit_code"
date -u +%FT%TZ >"${RUN_ROOT}/status/${DATASET}.finished_at"
if [[ ${code} -eq 0 ]]; then
  printf '%s\n' "${SUCCESS_STATE}" >"${RUN_ROOT}/status/${DATASET}"
else
  printf '%s\n' failed >"${RUN_ROOT}/status/${DATASET}"
fi
refresh_status
exit "${code}"
