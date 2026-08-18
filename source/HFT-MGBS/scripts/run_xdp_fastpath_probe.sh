#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 SOURCE_PCAP FROZEN_THRESHOLDS_JSON" >&2
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
CAPTURE_INTERFACE="${CAPTURE_INTERFACE:-ens8f0}"
REPLAY_INTERFACE="${REPLAY_INTERFACE:-ens8f1}"
SHARDED_WORKER_CPUS="${SHARDED_WORKER_CPUS:-36,37,38,39,40,41,42,43}"
INJECTOR_WORKER_CPUS="${INJECTOR_WORKER_CPUS:-44,45,46,47,48,49,50,51}"
INJECTOR_BACKEND="${INJECTOR_BACKEND:-packet-tx-ring}"
REPLAY_TX_USECS="${REPLAY_TX_USECS:-}"
SOURCE_PCAP="$1"
THRESHOLDS_FILE="$2"

for path in "${SOURCE_PCAP}" "${THRESHOLDS_FILE}"; do
  if [[ ! -f "${path}" ]]; then
    echo "required input is not a file: ${path}" >&2
    exit 3
  fi
done
for command_name in cargo ethtool ip jq python3 sha256sum; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "required command is unavailable: ${command_name}" >&2
    exit 4
  fi
done
if [[ "${CAPTURE_INTERFACE}" == "${REPLAY_INTERFACE}" ]]; then
  echo "capture and replay interfaces must be distinct" >&2
  exit 3
fi
if [[ "${INJECTOR_BACKEND}" != "packet-tx-ring" \
  && "${INJECTOR_BACKEND}" != "af-xdp-skb" ]]; then
  echo "INJECTOR_BACKEND must be packet-tx-ring or af-xdp-skb" >&2
  exit 3
fi

target_mpps="$(jq -er 'select(.frozen == true) | .target_load_mpps | select(type == "number" and . > 0)' "${THRESHOLDS_FILE}")"
duration_s="$(jq -er '.min_run_duration_s | select(type == "number" and . > 0) | ceil' "${THRESHOLDS_FILE}")"
run_id="hft_r0_xdp_$(date -u +%Y%m%dT%H%M%S%NZ)"
run_dir="${REPLAY_ROOT}/${run_id}"
mkdir -p "${run_dir}"
cp --reflink=auto --preserve=timestamps "${THRESHOLDS_FILE}" "${run_dir}/frozen_thresholds.json"

feature_state() {
  ethtool -k "$1" | awk -F': ' -v feature="$2" \
    '$1 == feature {print $2; exit}' | awk '{print $1}'
}

snapshot_interface() {
  local interface="$1"
  local prefix="$2"
  ip -s -j link show dev "${interface}" > "${run_dir}/${prefix}_ip_link.json"
  ethtool "${interface}" > "${run_dir}/${prefix}_ethtool.txt"
  ethtool -k "${interface}" > "${run_dir}/${prefix}_ethtool_features.txt"
  ethtool -S "${interface}" > "${run_dir}/${prefix}_ethtool_stats.txt"
}

gro_before="$(feature_state "${CAPTURE_INTERFACE}" "generic-receive-offload")"
lro_before="$(feature_state "${CAPTURE_INTERFACE}" "large-receive-offload")"
replay_tx_usecs_before="$(ethtool -c "${REPLAY_INTERFACE}" \
  | awk -F': ' '$1 == "tx-usecs" {print $2; exit}' | awk '{print $1}')"
if [[ "${gro_before}" != "on" && "${gro_before}" != "off" ]]; then
  echo "unable to determine GRO state" >&2
  exit 3
fi
if [[ "${lro_before}" != "on" && "${lro_before}" != "off" ]]; then
  echo "unable to determine LRO state" >&2
  exit 3
fi
if [[ ! "${replay_tx_usecs_before}" =~ ^[0-9]+$ ]]; then
  echo "unable to determine replay TX coalesce usecs" >&2
  exit 3
fi
if [[ -n "${REPLAY_TX_USECS}" && ! "${REPLAY_TX_USECS}" =~ ^[0-9]+$ ]]; then
  echo "REPLAY_TX_USECS must be an unsigned integer when set" >&2
  exit 3
fi

probe_pid=""
cleanup() {
  if [[ -n "${probe_pid}" ]] && kill -0 "${probe_pid}" 2>/dev/null; then
    kill -TERM "${probe_pid}" 2>/dev/null || true
    wait "${probe_pid}" 2>/dev/null || true
  fi
  ethtool -K "${CAPTURE_INTERFACE}" gro "${gro_before}" >/dev/null 2>&1 || true
  if [[ "${lro_before}" == "on" ]]; then
    ethtool -K "${CAPTURE_INTERFACE}" lro on >/dev/null 2>&1 || true
  fi
  ethtool -C "${REPLAY_INTERFACE}" tx-usecs "${replay_tx_usecs_before}" \
    >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

if [[ "${gro_before}" == "on" ]]; then
  ethtool -K "${CAPTURE_INTERFACE}" gro off
fi
if [[ "${lro_before}" == "on" ]]; then
  ethtool -K "${CAPTURE_INTERFACE}" lro off
fi
if [[ -n "${REPLAY_TX_USECS}" ]]; then
  ethtool -C "${REPLAY_INTERFACE}" tx-usecs "${REPLAY_TX_USECS}"
fi

preflight_failed=0
python3 "${CODE_ROOT}/scripts/preflight_live_host.py" \
  --interface "${CAPTURE_INTERFACE}" \
  --capture-driver xdp-skb \
  --thresholds-file "${run_dir}/frozen_thresholds.json" \
  --minimum-speed-mbps 10000 \
  --require-unmanaged \
  --output "${run_dir}/capture_preflight.json" \
  > "${run_dir}/capture_preflight.stdout" || preflight_failed=1
python3 "${CODE_ROOT}/scripts/preflight_live_host.py" \
  --interface "${REPLAY_INTERFACE}" \
  --capture-driver replay-tx \
  --thresholds-file "${run_dir}/frozen_thresholds.json" \
  --minimum-speed-mbps 10000 \
  --require-unmanaged \
  --output "${run_dir}/replay_preflight.json" \
  > "${run_dir}/replay_preflight.stdout" || preflight_failed=1
if (( preflight_failed != 0 )); then
  echo "${run_dir}"
  exit 6
fi

cargo build --release --manifest-path "${CODE_ROOT}/rust/hft-capture/Cargo.toml"
"${CODE_ROOT}/scripts/build_hft_xdp_ebpf.sh" > "${run_dir}/xdp_ebpf_build_sha256.txt"
probe="${CODE_ROOT}/rust/hft-capture/target/release/xdp_sharded_fastpath_probe"
if [[ "${INJECTOR_BACKEND}" == "af-xdp-skb" ]]; then
  injector="${CODE_ROOT}/rust/hft-capture/target/release/synthetic_xdp_injector"
else
  injector="${CODE_ROOT}/rust/hft-capture/target/release/synthetic_packet_injector"
fi
ebpf="${CODE_ROOT}/rust/hft-capture/target/hft_xdp_redirect.o"
cp --reflink=auto --preserve=timestamps "${probe}" "${run_dir}/xdp-fastpath-probe.bin"
cp --reflink=auto --preserve=timestamps "${injector}" "${run_dir}/traffic-injector.bin"
cp --reflink=auto --preserve=timestamps "${ebpf}" "${run_dir}/hft_xdp_redirect.o"
cp --reflink=auto --preserve=timestamps \
  "${CODE_ROOT}/rust/hft-capture/ebpf/hft_xdp_redirect.c" \
  "${run_dir}/hft_xdp_redirect.c"

{
  echo "run_id=${run_id}"
  echo "scope=r0_borrowed_umem_capture_only"
  echo "capture_interface=${CAPTURE_INTERFACE}"
  echo "replay_interface=${REPLAY_INTERFACE}"
  echo "traffic_profile=synthetic_ethernet_ipv4_udp_64b_rss_sharded"
  echo "source_pcap_provenance_only=${SOURCE_PCAP}"
  echo "target_mpps=${target_mpps}"
  echo "duration_s=${duration_s}"
  echo "receive_batch_size=256"
  echo "architecture=one_thread_per_xsk_rx_queue"
  echo "worker_cpus=${SHARDED_WORKER_CPUS}"
  echo "injector_worker_cpus=${INJECTOR_WORKER_CPUS}"
  echo "injector_backend=${INJECTOR_BACKEND}"
  echo "injector_batch_size=256"
  echo "frame_size_bytes=64"
  echo "replay_tx_usecs_before=${replay_tx_usecs_before}"
  echo "replay_tx_usecs_candidate=${REPLAY_TX_USECS:-unchanged}"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${run_dir}/manifest.txt"

snapshot_interface "${CAPTURE_INTERFACE}" capture_before
snapshot_interface "${REPLAY_INTERFACE}" replay_before
probe_duration_s=$((duration_s + 2))
/usr/bin/time -v -o "${run_dir}/probe_process_time.txt" \
  "${run_dir}/xdp-fastpath-probe.bin" \
  --interface "${CAPTURE_INTERFACE}" \
  --receive-batch-size 256 \
  --ebpf-object "${run_dir}/hft_xdp_redirect.o" \
  --worker-cpus "${SHARDED_WORKER_CPUS}" \
  --duration-s "${probe_duration_s}" \
  --output "${run_dir}/probe_metrics.json" \
  > "${run_dir}/probe_stdout.json" 2> "${run_dir}/probe_stderr.log" &
probe_pid="$!"
sleep 1

set +e
/usr/bin/time -v -o "${run_dir}/injector_process_time.txt" \
  "${run_dir}/traffic-injector.bin" \
  --interface "${REPLAY_INTERFACE}" \
  --duration-s "${duration_s}" \
  --target-mpps "${target_mpps}" \
  --worker-cpus "${INJECTOR_WORKER_CPUS}" \
  --batch-size 256 \
  --frame-size 64 \
  --output "${run_dir}/injector_metrics.json" \
  > "${run_dir}/injector_stdout.json" 2> "${run_dir}/injector_stderr.log"
injector_status="$?"
wait "${probe_pid}"
probe_status="$?"
set -e
probe_pid=""

snapshot_interface "${CAPTURE_INTERFACE}" capture_after
snapshot_interface "${REPLAY_INTERFACE}" replay_after
if ip -details link show dev "${CAPTURE_INTERFACE}" | grep -q 'prog/xdp'; then
  echo "residual XDP program after probe" >&2
  exit 9
fi

if (( injector_status != 0 || probe_status != 0 )) \
  || [[ ! -f "${run_dir}/probe_metrics.json" ]] \
  || [[ ! -f "${run_dir}/injector_metrics.json" ]]; then
  {
    echo "injector_exit_status=${injector_status}"
    echo "probe_exit_status=${probe_status}"
    echo "summary_exit_status=not_run"
    echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${run_dir}/manifest.txt"
  sha256sum "${run_dir}/manifest.txt" "${run_dir}/frozen_thresholds.json" \
    "${run_dir}/xdp-fastpath-probe.bin" "${run_dir}/traffic-injector.bin" \
    "${run_dir}/hft_xdp_redirect.o" "${run_dir}/hft_xdp_redirect.c" \
    > "${run_dir}/evidence_sha256.txt"
  echo "${run_dir}"
  exit 8
fi

set +e
python3 "${CODE_ROOT}/scripts/summarize_xdp_fastpath_probe.py" \
  --run-dir "${run_dir}" > "${run_dir}/summary.stdout.json"
summary_status="$?"
set -e
{
  echo "injector_exit_status=${injector_status}"
  echo "probe_exit_status=${probe_status}"
  echo "summary_exit_status=${summary_status}"
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "${run_dir}/manifest.txt"
sha256sum "${run_dir}/manifest.txt" "${run_dir}/frozen_thresholds.json" \
  "${run_dir}/probe_metrics.json" "${run_dir}/injector_metrics.json" \
  "${run_dir}/summary.json" "${run_dir}/xdp-fastpath-probe.bin" \
  "${run_dir}/traffic-injector.bin" \
  "${run_dir}/hft_xdp_redirect.o" "${run_dir}/hft_xdp_redirect.c" \
  > "${run_dir}/evidence_sha256.txt"
echo "${run_dir}"
exit "${summary_status}"
