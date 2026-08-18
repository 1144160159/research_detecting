#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 SOURCE_PCAP" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
SOURCE_PCAP="$1"
campaign_id="hft_xdp_receive_batch_exploration_$(date -u +%Y%m%dT%H%M%S%NZ)"
campaign_dir="${REPLAY_ROOT}/${campaign_id}"
mkdir -p "${campaign_dir}"
records="${campaign_dir}/runs.tsv"
printf 'candidate_id\treceive_batch_size\trunner_status\trun_dir\n' > "${records}"

profiles=(
  "XRB64:64:xdp_receive_batch_64_005mpps.json"
  "XRB128:128:xdp_receive_batch_128_005mpps.json"
  "XRB256:256:xdp_receive_batch_256_005mpps.json"
)
run_args=()

for record in "${profiles[@]}"; do
  IFS=: read -r candidate receive_batch profile <<< "${record}"
  set +e
  output="$(
    XDP_RECEIVE_BATCH_SIZE="${receive_batch}" \
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
    "${candidate}" "${receive_batch}" "${status}" "${run_dir}" >> "${records}"
  run_args+=(--run "${run_dir}")
done

set +e
python3 "${CODE_ROOT}/scripts/summarize_xdp_receive_batch_exploration.py" \
  "${run_args[@]}" \
  --output "${campaign_dir}/summary.json"
summary_status="$?"
set -e
sha256sum "${records}" "${campaign_dir}/summary.json" \
  > "${campaign_dir}/evidence_sha256.txt"
echo "${campaign_dir}"
exit "${summary_status}"
