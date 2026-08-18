#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 || "$#" -gt 3 ]]; then
  echo "usage: $0 SOURCE_PCAP [DURATION_S] [FAIL_AFTER_PACKETS]" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
CAPTURE_INTERFACE="${CAPTURE_INTERFACE:-ens8f0}"
SOURCE_PCAP="$1"
DURATION_S="${2:-15}"
FAIL_AFTER_PACKETS="${3:-50000}"
MAXIMUM_RECOVERY_MS="${MAXIMUM_RECOVERY_MS:-300}"

set +e
run_output="$(
  CAPTURE_FALLBACK_DRIVER=af-packet-ts \
  DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS="${FAIL_AFTER_PACKETS}" \
    "${CODE_ROOT}/scripts/run_physical_link_diagnostic.sh" \
      "${SOURCE_PCAP}" "${DURATION_S}" xdp-skb
)"
runner_status="$?"
set -e
printf '%s\n' "${run_output}"
run_dir="$(printf '%s\n' "${run_output}" | tail -n 1)"
if [[ ! -d "${run_dir}" ]]; then
  echo "fallback diagnostic did not return an evidence directory" >&2
  exit 3
fi
if [[ "${runner_status}" != "0" && "${runner_status}" != "10" ]]; then
  echo "fallback diagnostic runner failed with status ${runner_status}" >&2
  exit "${runner_status}"
fi

ip -details -j link show dev "${CAPTURE_INTERFACE}" \
  > "${run_dir}/fallback_post_ip_link.json"
bpftool net show dev "${CAPTURE_INTERFACE}" \
  > "${run_dir}/fallback_post_bpftool.txt"
ethtool -k "${CAPTURE_INTERFACE}" \
  > "${run_dir}/fallback_post_ethtool_features.txt"

PYTHONPATH="${CODE_ROOT}" python3 \
  "${CODE_ROOT}/scripts/summarize_capture_fallback.py" \
  "${run_dir}" \
  --maximum-recovery-ms "${MAXIMUM_RECOVERY_MS}" \
  --output "${run_dir}/capture_fallback_evidence.json"
sha256sum \
  "${run_dir}/fallback_post_ip_link.json" \
  "${run_dir}/fallback_post_bpftool.txt" \
  "${run_dir}/fallback_post_ethtool_features.txt" \
  "${run_dir}/capture_fallback_evidence.json" \
  >> "${run_dir}/evidence_sha256.txt"
echo "${run_dir}"
