#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 SOURCE_PCAP" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
SOURCE_PCAP="$1"
campaign_id="hft_xdp_load_boundary_$(date -u +%Y%m%dT%H%M%S%NZ)"
campaign_dir="${REPLAY_ROOT}/${campaign_id}"
mkdir -p "${campaign_dir}"
records="${campaign_dir}/runs.tsv"
printf 'candidate_id\ttarget_mpps\trunner_status\trun_dir\n' > "${records}"

profiles=(
  "LB02_0.02mpps:0.02:load_boundary_xdp_002mpps.json"
  "LB03_0.03mpps:0.03:load_boundary_xdp_003mpps.json"
  "LB04_0.04mpps:0.04:load_boundary_xdp_004mpps.json"
)
run_args=()

for record in "${profiles[@]}"; do
  IFS=: read -r candidate target profile <<< "${record}"
  set +e
  output="$(
    XDP_RECEIVE_BATCH_SIZE=64 \
    PHYSICAL_DIAGNOSTIC_THRESHOLDS="${CODE_ROOT}/configs/${profile}" \
      "${CODE_ROOT}/scripts/run_physical_link_diagnostic.sh" \
        "${SOURCE_PCAP}" 15 xdp-skb
  )"
  status="$?"
  set -e
  printf '%s\n' "${output}"
  run_dir="$(printf '%s\n' "${output}" | tail -n 1)"
  if [[ ! -d "${run_dir}" ]]; then
    echo "candidate ${candidate} did not return an evidence directory" >&2
    exit 8
  fi
  printf '%s\t%s\t%s\t%s\n' \
    "${candidate}" "${target}" "${status}" "${run_dir}" >> "${records}"
  run_args+=(--run "${run_dir}")
done

set +e
python3 "${CODE_ROOT}/scripts/summarize_xdp_load_exploration.py" \
  "${run_args[@]}" \
  --output "${campaign_dir}/summary.json"
summary_status="$?"
set -e
sha256sum "${records}" "${campaign_dir}/summary.json" \
  > "${campaign_dir}/evidence_sha256.txt"
echo "${campaign_dir}"
exit "${summary_status}"
