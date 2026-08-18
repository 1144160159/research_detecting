#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
CAPTURE_INTERFACE="${CAPTURE_INTERFACE:-hftdiagc}"
REPLAY_INTERFACE="${REPLAY_INTERFACE:-hftdiagr}"
SOURCE_PCAP="${1:-${REPLAY_ROOT}/inputs/16f2fd56abfe05d2048fad5c18377e8990ca928b00e9e2c05ffdc420a42c8660_FTP-EXP1.pcap}"
DURATION_S="${2:-5}"
THRESHOLDS="${CODE_ROOT}/configs/live_thresholds_veth_diagnostic.json"
COUNTER_MAP="${CODE_ROOT}/configs/live_counter_map_veth_diagnostic.json"

if ip link show "${CAPTURE_INTERFACE}" >/dev/null 2>&1 \
  || ip link show "${REPLAY_INTERFACE}" >/dev/null 2>&1; then
  echo "diagnostic interface name is already in use" >&2
  exit 3
fi

cleanup() {
  if ip link show "${CAPTURE_INTERFACE}" >/dev/null 2>&1; then
    ip link del "${CAPTURE_INTERFACE}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

ip link add "${CAPTURE_INTERFACE}" type veth peer name "${REPLAY_INTERFACE}"
sysctl -q -w "net.ipv6.conf.${CAPTURE_INTERFACE}.disable_ipv6=1" >/dev/null
sysctl -q -w "net.ipv6.conf.${REPLAY_INTERFACE}.disable_ipv6=1" >/dev/null
ip link set "${CAPTURE_INTERFACE}" up
ip link set "${REPLAY_INTERFACE}" up
sleep 1

EVIDENCE_SCOPE=virtual_link_live_diagnostic \
COUNTER_MAP="${COUNTER_MAP}" \
  "${CODE_ROOT}/scripts/run_live_acceptance.sh" \
  "${CAPTURE_INTERFACE}" \
  "${REPLAY_INTERFACE}" \
  "${SOURCE_PCAP}" \
  "${THRESHOLDS}" \
  "${DURATION_S}" \
  af-packet-ts
