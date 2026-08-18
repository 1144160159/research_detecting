#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 SOURCE_PCAP" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
SOURCE_PCAP="$1"
campaign_id="hft_xdp_load_exploration_$(date -u +%Y%m%dT%H%M%S%NZ)"
campaign_dir="${REPLAY_ROOT}/${campaign_id}"
mkdir -p "${campaign_dir}"
records="${campaign_dir}/runs.tsv"
printf 'candidate_id\ttarget_mpps\trunner_status\trun_dir\n' > "${records}"

profiles=(
  "L01_0.05mpps:0.05:load_exploration_xdp_005mpps.json"
  "L02_0.10mpps:0.10:load_exploration_xdp_010mpps.json"
  "L03_0.25mpps:0.25:load_exploration_xdp_025mpps.json"
  "L04_0.50mpps:0.50:load_exploration_xdp_050mpps.json"
)

for record in "${profiles[@]}"; do
  IFS=: read -r candidate target profile <<< "${record}"
  set +e
  output="$(
    PHYSICAL_DIAGNOSTIC_THRESHOLDS="${CODE_ROOT}/configs/${profile}" \
      "${CODE_ROOT}/scripts/run_physical_link_diagnostic.sh" \
        "${SOURCE_PCAP}" 15 xdp-skb
  )"
  status="$?"
  set -e
  printf '%s\n' "${output}"
  run_dir="$(printf '%s\n' "${output}" | tail -n 1)"
  if [[ ! -d "${run_dir}" ]]; then
    run_dir="missing"
  fi
  printf '%s\t%s\t%s\t%s\n' \
    "${candidate}" "${target}" "${status}" "${run_dir}" >> "${records}"
done

sha256sum "${records}" > "${campaign_dir}/evidence_sha256.txt"
echo "${campaign_dir}"
