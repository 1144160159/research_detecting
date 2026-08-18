#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 CAPTURE_INTERFACE REPLAY_INTERFACE SOURCE_PCAP THRESHOLDS_JSON [DURATION_S] [af-packet-ts|af-packet|xdp|xdp-skb]" >&2
}

if [[ "$#" -lt 4 || "$#" -gt 6 ]]; then
  usage
  exit 2
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
GPU_ENDPOINT="${GPU_ENDPOINT:-listen://0.0.0.0:50052}"
GPU_TIMEOUT_MS="${GPU_TIMEOUT_MS:-150}"
BATCH_SIZE="${BATCH_SIZE:-128}"
FEATURE_FLUSH_US="${FEATURE_FLUSH_US:-1000}"
MINIMUM_PHYSICAL_SPEED_MBPS="${MINIMUM_PHYSICAL_SPEED_MBPS:-10000}"
CAPTURE_OFFLOAD_POLICY="${CAPTURE_OFFLOAD_POLICY:-externally_managed}"
CAPTURE_FALLBACK_DRIVER="${CAPTURE_FALLBACK_DRIVER:-}"
DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS="${DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS:-}"
XDP_RECEIVE_BATCH_SIZE="${XDP_RECEIVE_BATCH_SIZE:-64}"
COUNTER_MAP="${COUNTER_MAP:-${CODE_ROOT}/configs/live_counter_map_bnx2x_rc1.json}"
EVIDENCE_SCOPE="${EVIDENCE_SCOPE:-physical_nic_live_replay}"
CAPTURE_INTERFACE="$1"
REPLAY_INTERFACE="$2"
SOURCE_PCAP="$3"
THRESHOLDS_FILE="$4"
DURATION_OVERRIDE="${5:-}"
DRIVER="${6:-af-packet-ts}"

if [[ "${CAPTURE_INTERFACE}" == "${REPLAY_INTERFACE}" ]]; then
  echo "capture and replay interfaces must be distinct" >&2
  exit 3
fi
if [[ ! -f "${SOURCE_PCAP}" ]]; then
  echo "SOURCE_PCAP is not a file: ${SOURCE_PCAP}" >&2
  exit 3
fi
if [[ ! -f "${THRESHOLDS_FILE}" ]]; then
  echo "THRESHOLDS_JSON is not a file: ${THRESHOLDS_FILE}" >&2
  exit 3
fi
if [[ ! -f "${COUNTER_MAP}" ]]; then
  echo "COUNTER_MAP is not a file: ${COUNTER_MAP}" >&2
  exit 3
fi
case "${DRIVER}" in
  af-packet|af-packet-ts|xdp|xdp-skb) ;;
  *)
    echo "unsupported capture driver: ${DRIVER}" >&2
    exit 3
    ;;
esac
if [[ -n "${CAPTURE_FALLBACK_DRIVER}" \
   && "${CAPTURE_FALLBACK_DRIVER}" != "af-packet-ts" ]]; then
  echo "unsupported capture fallback driver: ${CAPTURE_FALLBACK_DRIVER}" >&2
  exit 3
fi
if [[ -n "${CAPTURE_FALLBACK_DRIVER}" && "${DRIVER}" != "xdp-skb" ]]; then
  echo "capture fallback is currently supported only for xdp-skb" >&2
  exit 3
fi
if ! [[ "${XDP_RECEIVE_BATCH_SIZE}" =~ ^[0-9]+$ ]] \
  || (( XDP_RECEIVE_BATCH_SIZE < 1 \
     || XDP_RECEIVE_BATCH_SIZE > 256 \
     || (XDP_RECEIVE_BATCH_SIZE & (XDP_RECEIVE_BATCH_SIZE - 1)) != 0 )); then
  echo "XDP_RECEIVE_BATCH_SIZE must be a power of two in 1..=256" >&2
  exit 3
fi
case "${EVIDENCE_SCOPE}" in
  physical_nic_live_replay|physical_link_live_diagnostic|virtual_link_live_diagnostic) ;;
  *)
    echo "unsupported EVIDENCE_SCOPE: ${EVIDENCE_SCOPE}" >&2
    exit 3
    ;;
esac

for command_name in cargo ethtool ip jq python3 sha256sum ss; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "required command is unavailable: ${command_name}" >&2
    exit 4
  fi
done
if [[ ! -x /usr/bin/time ]]; then
  echo "required command is unavailable: /usr/bin/time" >&2
  exit 4
fi

diagnostic_only=false
if [[ "${EVIDENCE_SCOPE}" == "virtual_link_live_diagnostic" ]]; then
  run_prefix="hft_vdiag"
  diagnostic_only=true
  preflight_scope_args=(--allow-virtual-diagnostic)
  composition_name="live_evidence.diagnostic.json"
elif [[ "${EVIDENCE_SCOPE}" == "physical_link_live_diagnostic" ]]; then
  run_prefix="hft_pdiag"
  diagnostic_only=true
  preflight_scope_args=(
    --minimum-speed-mbps "${MINIMUM_PHYSICAL_SPEED_MBPS}"
    --require-unmanaged
  )
  composition_name="live_evidence.diagnostic.json"
else
  run_prefix="hft_live"
  preflight_scope_args=(
    --minimum-speed-mbps "${MINIMUM_PHYSICAL_SPEED_MBPS}"
    --require-unmanaged
  )
  composition_name="live_evidence.incomplete.json"
fi
if [[ -n "${DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS}" ]]; then
  if [[ "${diagnostic_only}" != "true" || "${DRIVER}" != "xdp-skb" ]]; then
    echo "XDP fault injection is restricted to xdp-skb diagnostic scope" >&2
    exit 3
  fi
  if ! [[ "${DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS}" =~ ^[1-9][0-9]*$ ]]; then
    echo "DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS must be positive" >&2
    exit 3
  fi
  if [[ "${CAPTURE_FALLBACK_DRIVER}" != "af-packet-ts" ]]; then
    echo "XDP fault injection requires af-packet-ts fallback" >&2
    exit 3
  fi
fi
run_id="${run_prefix}_$(date -u +%Y%m%dT%H%M%S%NZ)"
run_dir="${REPLAY_ROOT}/${run_id}"
input_dir="${REPLAY_ROOT}/inputs"
mkdir -p "${run_dir}" "${input_dir}"
manifest="${run_dir}/manifest.txt"

input_sha="$(sha256sum "${SOURCE_PCAP}" | awk '{print $1}')"
thresholds_sha="$(sha256sum "${THRESHOLDS_FILE}" | awk '{print $1}')"
input_copy="${input_dir}/${input_sha}_$(basename "${SOURCE_PCAP}")"
if [[ ! -f "${input_copy}" ]]; then
  cp --reflink=auto --preserve=timestamps "${SOURCE_PCAP}" "${input_copy}"
fi
if [[ "$(sha256sum "${input_copy}" | awk '{print $1}')" != "${input_sha}" ]]; then
  echo "replay input hash mismatch" >&2
  exit 5
fi
cp "${THRESHOLDS_FILE}" "${run_dir}/frozen_thresholds.json"
cp "${COUNTER_MAP}" "${run_dir}/frozen_counter_map.json"
counter_map_sha="$(sha256sum "${run_dir}/frozen_counter_map.json" | awk '{print $1}')"

{
  echo "run_id=${run_id}"
  echo "status=preflight_pending"
  echo "candidate_id=A09"
  echo "evidence_scope=${EVIDENCE_SCOPE}"
  echo "diagnostic_only=${diagnostic_only}"
  echo "capture_interface=${CAPTURE_INTERFACE}"
  echo "replay_interface=${REPLAY_INTERFACE}"
  echo "capture_driver=${DRIVER}"
  echo "source=${SOURCE_PCAP}"
  echo "replay_input=${input_copy}"
  echo "input_sha256=${input_sha}"
  echo "thresholds_sha256=${thresholds_sha}"
  echo "counter_map_sha256=${counter_map_sha}"
  echo "gpu_endpoint=${GPU_ENDPOINT}"
  echo "gpu_timeout_ms=${GPU_TIMEOUT_MS}"
  echo "batch_size=${BATCH_SIZE}"
  echo "feature_flush_us=${FEATURE_FLUSH_US}"
  echo "capture_offload_policy=${CAPTURE_OFFLOAD_POLICY}"
  echo "capture_fallback_driver=${CAPTURE_FALLBACK_DRIVER:-none}"
  echo "diagnostic_xdp_fail_after_packets=${DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS:-none}"
  echo "xdp_receive_batch_size=${XDP_RECEIVE_BATCH_SIZE}"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${manifest}"

preflight_failed=0
python3 "${CODE_ROOT}/scripts/preflight_live_host.py" \
  --interface "${CAPTURE_INTERFACE}" \
  --capture-driver "${DRIVER}" \
  --thresholds-file "${run_dir}/frozen_thresholds.json" \
  "${preflight_scope_args[@]}" \
  --output "${run_dir}/capture_preflight.json" \
  > "${run_dir}/capture_preflight.stdout" || preflight_failed=1
python3 "${CODE_ROOT}/scripts/preflight_live_host.py" \
  --interface "${REPLAY_INTERFACE}" \
  --capture-driver "replay-tx" \
  --thresholds-file "${run_dir}/frozen_thresholds.json" \
  "${preflight_scope_args[@]}" \
  --output "${run_dir}/replay_preflight.json" \
  > "${run_dir}/replay_preflight.stdout" || preflight_failed=1
if (( preflight_failed != 0 )); then
  {
    echo "status=preflight_failed"
    echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${manifest}"
  sha256sum "${manifest}" "${run_dir}/frozen_thresholds.json" \
    "${run_dir}/frozen_counter_map.json" \
    "${run_dir}/capture_preflight.json" "${run_dir}/replay_preflight.json" \
    > "${run_dir}/evidence_sha256.txt"
  echo "${run_dir}"
  exit 6
fi

threshold_duration="$(
  jq -er '
    if .frozen == true
       and (.min_run_duration_s | type) == "number"
       and .min_run_duration_s > 0
    then .min_run_duration_s | ceil
    else error("thresholds are not frozen or min_run_duration_s is invalid")
    end
  ' "${run_dir}/frozen_thresholds.json"
)"
duration_s="${DURATION_OVERRIDE:-${threshold_duration}}"
if ! [[ "${duration_s}" =~ ^[1-9][0-9]*$ ]]; then
  echo "DURATION_S must be a positive integer" >&2
  exit 3
fi
if (( duration_s < threshold_duration )); then
  echo "DURATION_S ${duration_s} is below frozen min_run_duration_s ${threshold_duration}" >&2
  exit 3
fi

target_kind="$(
  jq -er '
    if (.target_load_mpps | type) == "number" and .target_load_mpps > 0
    then "mpps"
    elif (.target_load_gbps | type) == "number" and .target_load_gbps > 0
    then "gbps"
    else error("a positive target load is required")
    end
  ' "${run_dir}/frozen_thresholds.json"
)"
target_value="$(
  jq -er \
    "if \"${target_kind}\" == \"mpps\" then .target_load_mpps else .target_load_gbps end" \
    "${run_dir}/frozen_thresholds.json"
)"
{
  echo "duration_s=${duration_s}"
  echo "target_load_${target_kind}=${target_value}"
} >> "${manifest}"

gpu_listen_port="${GPU_ENDPOINT##*:}"
if ss -H -ltn "sport = :${gpu_listen_port}" | grep -q .; then
  {
    echo "status=gpu_listener_conflict"
    echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${manifest}"
  sha256sum "${manifest}" "${run_dir}/frozen_thresholds.json" \
    "${run_dir}/frozen_counter_map.json" \
    "${run_dir}/capture_preflight.json" "${run_dir}/replay_preflight.json" \
    > "${run_dir}/evidence_sha256.txt"
  echo "GPU reverse-listener port is already in use: ${gpu_listen_port}" >&2
  echo "${run_dir}"
  exit 7
fi

snapshot_interface() {
  local interface="$1"
  local prefix="$2"
  ip -s -j link show dev "${interface}" > "${run_dir}/${prefix}_ip_link.json"
  ethtool "${interface}" > "${run_dir}/${prefix}_ethtool.txt"
  ethtool -k "${interface}" > "${run_dir}/${prefix}_ethtool_features.txt"
  ethtool -S "${interface}" > "${run_dir}/${prefix}_ethtool_stats.txt"
  (
    cd "/sys/class/net/${interface}/statistics"
    for counter in *; do
      printf "%s=%s\n" "${counter}" "$(<"${counter}")"
    done
  ) > "${run_dir}/${prefix}_sysfs_counters.txt"
}

cargo build --release \
  --manifest-path "${CODE_ROOT}/rust/hft-capture/Cargo.toml"
binary="${CODE_ROOT}/rust/hft-capture/target/release/hft-capture"
injector="${CODE_ROOT}/rust/hft-capture/target/release/pcap_injector"
evidence_binary="${run_dir}/hft-capture.bin"
evidence_injector="${run_dir}/pcap-injector.bin"
cp --reflink=auto --preserve=timestamps "${binary}" "${evidence_binary}"
cp --reflink=auto --preserve=timestamps "${injector}" "${evidence_injector}"
binary_sha="$(sha256sum "${evidence_binary}" | awk '{print $1}')"
injector_sha="$(sha256sum "${evidence_injector}" | awk '{print $1}')"
echo "binary=${evidence_binary}" >> "${manifest}"
echo "injector_binary=${evidence_injector}" >> "${manifest}"
echo "binary_sha256=${binary_sha}" >> "${manifest}"
echo "injector_sha256=${injector_sha}" >> "${manifest}"
xdp_capture_args=()
fallback_capture_args=()
evidence_xdp_ebpf=""
evidence_xdp_source=""
if [[ "${DRIVER}" == "xdp" || "${DRIVER}" == "xdp-skb" ]]; then
  "${CODE_ROOT}/scripts/build_hft_xdp_ebpf.sh" \
    > "${run_dir}/xdp_ebpf_build_sha256.txt"
  built_xdp_ebpf="${CODE_ROOT}/rust/hft-capture/target/hft_xdp_redirect.o"
  evidence_xdp_ebpf="${run_dir}/hft_xdp_redirect.o"
  evidence_xdp_source="${run_dir}/hft_xdp_redirect.c"
  cp --reflink=auto --preserve=timestamps \
    "${built_xdp_ebpf}" "${evidence_xdp_ebpf}"
  cp --reflink=auto --preserve=timestamps \
    "${CODE_ROOT}/rust/hft-capture/ebpf/hft_xdp_redirect.c" \
    "${evidence_xdp_source}"
  xdp_ebpf_sha="$(sha256sum "${evidence_xdp_ebpf}" | awk '{print $1}')"
  xdp_source_sha="$(sha256sum "${evidence_xdp_source}" | awk '{print $1}')"
  echo "xdp_ebpf_object=${evidence_xdp_ebpf}" >> "${manifest}"
  echo "xdp_ebpf_sha256=${xdp_ebpf_sha}" >> "${manifest}"
  echo "xdp_ebpf_source=${evidence_xdp_source}" >> "${manifest}"
  echo "xdp_ebpf_source_sha256=${xdp_source_sha}" >> "${manifest}"
  xdp_capture_args=(
    --xdp-ebpf-object "${evidence_xdp_ebpf}"
    --xdp-receive-batch-size "${XDP_RECEIVE_BATCH_SIZE}"
  )
fi
if [[ -n "${CAPTURE_FALLBACK_DRIVER}" ]]; then
  fallback_capture_args=(
    --capture-fallback-driver "${CAPTURE_FALLBACK_DRIVER}"
  )
fi
if [[ -n "${DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS}" ]]; then
  fallback_capture_args+=(
    --diagnostic-xdp-fail-after-packets \
      "${DIAGNOSTIC_XDP_FAIL_AFTER_PACKETS}"
    --allow-diagnostic-fault-injection
  )
fi

snapshot_interface "${CAPTURE_INTERFACE}" "capture_before"
snapshot_interface "${REPLAY_INTERFACE}" "replay_before"

capture_pid=""
cleanup() {
  if [[ -n "${capture_pid}" ]] && kill -0 "${capture_pid}" 2>/dev/null; then
    kill -TERM "${capture_pid}" 2>/dev/null || true
    wait "${capture_pid}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

capture_duration_s=$((duration_s + 3))
/usr/bin/time -v -o "${run_dir}/physical_process_time.txt" \
  "${evidence_binary}" \
  --interface "${CAPTURE_INTERFACE}" \
  --driver "${DRIVER}" \
  "${xdp_capture_args[@]}" \
  "${fallback_capture_args[@]}" \
  --gpu-endpoint "${GPU_ENDPOINT}" \
  --gpu-startup-wait-ms 10000 \
  --gpu-timeout-ms "${GPU_TIMEOUT_MS}" \
  --metrics "${run_dir}/metrics.json" \
  --batch-size "${BATCH_SIZE}" \
  --feature-flush-us "${FEATURE_FLUSH_US}" \
  --budget-us 5000 \
  --execution-budget-safety-ratio 0.50 \
  --max-duration-s "${capture_duration_s}" \
  > "${run_dir}/capture_stdout.json" 2> "${run_dir}/capture_stderr.log" &
capture_pid="$!"

listener_ready=0
for _ in $(seq 1 120); do
  if ! kill -0 "${capture_pid}" 2>/dev/null; then
    break
  fi
  if ss -H -ltn "sport = :${gpu_listen_port}" | grep -q .; then
    listener_ready=1
    break
  fi
  sleep 0.1
done
if (( listener_ready == 0 )); then
  wait "${capture_pid}" || true
  capture_pid=""
  echo "Rust capture did not expose the reverse GPU listener" >&2
  exit 8
fi

sleep 1
injector_rate=(--target-"${target_kind}" "${target_value}")
set +e
/usr/bin/time -v -o "${run_dir}/injector_process_time.txt" \
  "${evidence_injector}" \
  --interface "${REPLAY_INTERFACE}" \
  --pcap "${input_copy}" \
  --duration-s "${duration_s}" \
  --evidence-scope "${EVIDENCE_SCOPE}" \
  "${injector_rate[@]}" \
  --output "${run_dir}/injector_metrics.json" \
  > "${run_dir}/injector_stdout.json" 2> "${run_dir}/injector_stderr.log"
injector_status="$?"
wait "${capture_pid}"
capture_status="$?"
set -e
capture_pid=""
trap - EXIT INT TERM

snapshot_interface "${CAPTURE_INTERFACE}" "capture_after"
snapshot_interface "${REPLAY_INTERFACE}" "replay_after"
if (( injector_status == 0 && capture_status == 0 )); then
  execution_status="raw_evidence_complete"
else
  execution_status="execution_failed"
fi
{
  echo "status=${execution_status}"
  echo "injector_exit_status=${injector_status}"
  echo "capture_exit_status=${capture_status}"
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "note=raw evidence requires strict live-evidence composition and three-repeat audit before Pareto admission"
} >> "${manifest}"
composition_status="not_run"
if [[ "${execution_status}" == "raw_evidence_complete" ]]; then
  set +e
  PYTHONPATH="${CODE_ROOT}" python3 \
    "${CODE_ROOT}/scripts/compose_live_evidence.py" \
    "${run_dir}" \
    "${CODE_ROOT}/configs/release_candidate_rc1.json" \
    "${run_dir}/frozen_counter_map.json" \
    --output "${run_dir}/${composition_name}" \
    > "${run_dir}/live_composition_stdout.json" \
    2> "${run_dir}/live_composition_stderr.log"
  composition_status="$?"
  set -e
fi
echo "live_composition_exit_status=${composition_status}" >> "${manifest}"
artifacts=(
  "${manifest}"
  "${run_dir}/frozen_thresholds.json"
  "${run_dir}/frozen_counter_map.json"
  "${run_dir}/capture_preflight.json"
  "${run_dir}/replay_preflight.json"
  "${run_dir}/metrics.json"
  "${run_dir}/physical_process_time.txt"
  "${run_dir}/capture_stdout.json"
  "${run_dir}/capture_stderr.log"
  "${evidence_binary}"
  "${evidence_injector}"
  "${evidence_xdp_ebpf}"
  "${evidence_xdp_source}"
  "${run_dir}/xdp_ebpf_build_sha256.txt"
  "${run_dir}/injector_metrics.json"
  "${run_dir}/injector_process_time.txt"
  "${run_dir}/injector_stdout.json"
  "${run_dir}/injector_stderr.log"
  "${run_dir}/${composition_name}"
  "${run_dir}/live_composition_stdout.json"
  "${run_dir}/live_composition_stderr.log"
  "${run_dir}/capture_before_ip_link.json"
  "${run_dir}/capture_after_ip_link.json"
  "${run_dir}/capture_before_ethtool_stats.txt"
  "${run_dir}/capture_after_ethtool_stats.txt"
  "${run_dir}/capture_before_ethtool_features.txt"
  "${run_dir}/capture_after_ethtool_features.txt"
  "${run_dir}/replay_before_ip_link.json"
  "${run_dir}/replay_after_ip_link.json"
  "${run_dir}/replay_before_ethtool_stats.txt"
  "${run_dir}/replay_after_ethtool_stats.txt"
  "${run_dir}/replay_before_ethtool_features.txt"
  "${run_dir}/replay_after_ethtool_features.txt"
)
for artifact in "${artifacts[@]}"; do
  if [[ -f "${artifact}" ]]; then
    sha256sum "${artifact}"
  fi
done > "${run_dir}/evidence_sha256.txt"
echo "${run_dir}"
if [[ "${execution_status}" != "raw_evidence_complete" ]]; then
  exit 9
fi
if [[ "${composition_status}" != "0" ]]; then
  exit 10
fi
