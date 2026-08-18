#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
PROFILE="${PROFILE:-${CODE_ROOT}/configs/temporary_interface_ens9f0_shadow.json}"
CAPTURE_INTERFACE="${CAPTURE_INTERFACE:-ens9f0}"
CAPTURE_DRIVER="${CAPTURE_DRIVER:-af-packet-ts}"
MAX_DURATION_S="${MAX_DURATION_S:-15}"
SHADOW_RUNTIME_CANDIDATE="${SHADOW_RUNTIME_CANDIDATE:-shadow_b128_f1000}"
GPU_ENDPOINT="${GPU_ENDPOINT:-listen://0.0.0.0:50052}"
ACK_MANAGEMENT_INTERFACE="${ACK_MANAGEMENT_INTERFACE:-0}"
BINARY="${BINARY:-${CODE_ROOT}/rust/hft-capture/target/release/hft-capture}"
RUN_ID="${RUN_ID:-hft_shadow_ens9f0_$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="${REPLAY_ROOT}/${RUN_ID}"

fail() {
  echo "temporary shadow capture refused: $*" >&2
  exit 2
}

[[ "${ACK_MANAGEMENT_INTERFACE}" == "1" ]] || fail \
  "set ACK_MANAGEMENT_INTERFACE=1 after confirming passive capture on the management uplink"
[[ "${CAPTURE_INTERFACE}" == "ens9f0" ]] || fail \
  "the frozen temporary profile only permits ens9f0"
[[ "${CAPTURE_DRIVER}" == "af-packet-ts" ]] || fail \
  "the frozen temporary profile only permits af-packet-ts"
[[ "${MAX_DURATION_S}" =~ ^[0-9]+$ ]] || fail \
  "MAX_DURATION_S must be an integer"
(( MAX_DURATION_S >= 1 && MAX_DURATION_S <= 60 )) || fail \
  "MAX_DURATION_S must be between 1 and 60 seconds"

case "${SHADOW_RUNTIME_CANDIDATE}" in
  shadow_b128_f1000)
    BATCH_SIZE=128
    FEATURE_FLUSH_US=1000
    ;;
  shadow_b64_f500)
    BATCH_SIZE=64
    FEATURE_FLUSH_US=500
    ;;
  shadow_b32_f250)
    BATCH_SIZE=32
    FEATURE_FLUSH_US=250
    ;;
  *)
    fail "runtime candidate is not in the frozen three-candidate set"
    ;;
esac

[[ -x "${BINARY}" ]] || fail "capture binary is unavailable: ${BINARY}"
[[ -f "${PROFILE}" ]] || fail "profile is unavailable: ${PROFILE}"
[[ ! -e "${RUN_DIR}" ]] || fail "run directory already exists: ${RUN_DIR}"

carrier="$(cat "/sys/class/net/${CAPTURE_INTERFACE}/carrier")"
operstate="$(cat "/sys/class/net/${CAPTURE_INTERFACE}/operstate")"
speed="$(cat "/sys/class/net/${CAPTURE_INTERFACE}/speed")"
master="$(basename "$(readlink "/sys/class/net/${CAPTURE_INTERFACE}/master")")"
[[ "${carrier}" == "1" ]] || fail "carrier is not present"
[[ "${operstate}" == "up" ]] || fail "operstate is not up"
[[ "${speed}" == "1000" ]] || fail "observed speed is not the frozen 1GbE diagnostic speed"
[[ "${master}" == "br0" ]] || fail "ens9f0 is not attached to the expected br0 management bridge"

mkdir -p "${RUN_DIR}"
cp "${PROFILE}" "${RUN_DIR}/interface_profile.json"
ip -details link show dev "${CAPTURE_INTERFACE}" \
  > "${RUN_DIR}/interface_before.txt"
ethtool "${CAPTURE_INTERFACE}" > "${RUN_DIR}/ethtool_before.txt"
ethtool -i "${CAPTURE_INTERFACE}" > "${RUN_DIR}/driver_before.txt"
for counter in rx_packets rx_bytes rx_dropped rx_errors tx_packets tx_bytes tx_dropped tx_errors; do
  printf '%s=%s\n' "${counter}" \
    "$(cat "/sys/class/net/${CAPTURE_INTERFACE}/statistics/${counter}")"
done > "${RUN_DIR}/nic_counters_before.env"

set +e
"${BINARY}" \
  --interface "${CAPTURE_INTERFACE}" \
  --driver "${CAPTURE_DRIVER}" \
  --gpu-endpoint "${GPU_ENDPOINT}" \
  --gpu-startup-wait-ms 10000 \
  --gpu-timeout-ms 150 \
  --metrics "${RUN_DIR}/metrics.json" \
  --batch-size "${BATCH_SIZE}" \
  --feature-flush-us "${FEATURE_FLUSH_US}" \
  --budget-us 5000 \
  --execution-budget-safety-ratio 0.50 \
  --max-duration-s "${MAX_DURATION_S}" \
  > "${RUN_DIR}/capture.stdout.log" \
  2> "${RUN_DIR}/capture.stderr.log"
capture_exit="$?"
set -e

ip -details link show dev "${CAPTURE_INTERFACE}" \
  > "${RUN_DIR}/interface_after.txt"
ethtool "${CAPTURE_INTERFACE}" > "${RUN_DIR}/ethtool_after.txt"
for counter in rx_packets rx_bytes rx_dropped rx_errors tx_packets tx_bytes tx_dropped tx_errors; do
  printf '%s=%s\n' "${counter}" \
    "$(cat "/sys/class/net/${CAPTURE_INTERFACE}/statistics/${counter}")"
done > "${RUN_DIR}/nic_counters_after.env"

cat > "${RUN_DIR}/scope.env" <<EOF
schema_version=1
scope=temporary_management_interface_passive_shadow
profile_id=temporary-ens9f0-passive-shadow-v1
capture_interface=${CAPTURE_INTERFACE}
capture_driver=${CAPTURE_DRIVER}
observed_speed_mbps=${speed}
network_master=${master}
max_duration_s=${MAX_DURATION_S}
runtime_candidate=${SHADOW_RUNTIME_CANDIDATE}
batch_size=${BATCH_SIZE}
feature_flush_us=${FEATURE_FLUSH_US}
capture_exit=${capture_exit}
pcap_injection_allowed=false
traffic_generation_allowed=false
final_pareto_ingestion_allowed=false
production_10gbe_claim_allowed=false
EOF

(
  cd "${RUN_DIR}"
  sha256sum \
    interface_profile.json \
    interface_before.txt \
    ethtool_before.txt \
    driver_before.txt \
    nic_counters_before.env \
    metrics.json \
    capture.stdout.log \
    capture.stderr.log \
    interface_after.txt \
    ethtool_after.txt \
    nic_counters_after.env \
    scope.env \
    > evidence_sha256.txt
)

echo "run_dir=${RUN_DIR}"
echo "runtime_candidate=${SHADOW_RUNTIME_CANDIDATE}"
echo "capture_exit=${capture_exit}"
echo "diagnostic_only=true"
exit "${capture_exit}"
