#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 || "$#" -gt 3 ]]; then
  echo "usage: $0 SOURCE_PCAP [DURATION_S] [af-packet-ts|af-packet|xdp|xdp-skb]" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
CAPTURE_INTERFACE="${CAPTURE_INTERFACE:-ens8f0}"
REPLAY_INTERFACE="${REPLAY_INTERFACE:-ens8f1}"
SOURCE_PCAP="$1"
DURATION_S="${2:-15}"
DRIVER="${3:-af-packet-ts}"
THRESHOLDS_FILE="${PHYSICAL_DIAGNOSTIC_THRESHOLDS:-${CODE_ROOT}/configs/live_thresholds_physical_diagnostic.json}"

if [[ ! -f "${THRESHOLDS_FILE}" ]]; then
  echo "physical diagnostic thresholds do not exist: ${THRESHOLDS_FILE}" >&2
  exit 3
fi

feature_state() {
  ethtool -k "$1" | awk -F': ' -v feature="$2" \
    '$1 == feature {print $2; exit}' | awk '{print $1}'
}

gro_before="$(feature_state "${CAPTURE_INTERFACE}" "generic-receive-offload")"
lro_before="$(feature_state "${CAPTURE_INTERFACE}" "large-receive-offload")"
if [[ "${gro_before}" != "on" && "${gro_before}" != "off" ]]; then
  echo "unable to determine GRO state for ${CAPTURE_INTERFACE}" >&2
  exit 3
fi
if [[ "${lro_before}" != "on" && "${lro_before}" != "off" ]]; then
  echo "unable to determine LRO state for ${CAPTURE_INTERFACE}" >&2
  exit 3
fi

restore_capture_offloads() {
  ethtool -K "${CAPTURE_INTERFACE}" gro "${gro_before}" >/dev/null 2>&1 || true
  if [[ "${lro_before}" == "on" ]]; then
    ethtool -K "${CAPTURE_INTERFACE}" lro on >/dev/null 2>&1 || true
  fi
}
trap restore_capture_offloads EXIT INT TERM

if [[ "${gro_before}" == "on" ]]; then
  ethtool -K "${CAPTURE_INTERFACE}" gro off
fi
if [[ "${lro_before}" == "on" ]]; then
  ethtool -K "${CAPTURE_INTERFACE}" lro off
fi

EVIDENCE_SCOPE=physical_link_live_diagnostic \
CAPTURE_OFFLOAD_POLICY="temporary_gro_lro_off_restore_on_exit" \
COUNTER_MAP="${CODE_ROOT}/configs/live_counter_map_bnx2x_rc1.json" \
"${CODE_ROOT}/scripts/run_live_acceptance.sh" \
  "${CAPTURE_INTERFACE}" \
  "${REPLAY_INTERFACE}" \
  "${SOURCE_PCAP}" \
  "${THRESHOLDS_FILE}" \
  "${DURATION_S}" \
  "${DRIVER}"
