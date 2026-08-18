#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 FROZEN_THRESHOLDS_JSON" >&2
  exit 2
fi
if [[ "${HFT_ALLOW_DISRUPTIVE_DPDK:-}" != "YES" ]]; then
  echo "set HFT_ALLOW_DISRUPTIVE_DPDK=YES only after approving dual-PF interruption" >&2
  exit 13
fi
if [[ -n "${HFT_DPDK_PREFLIGHT_ONLY:-}" \
  && "${HFT_DPDK_PREFLIGHT_ONLY}" != "YES" ]]; then
  echo "HFT_DPDK_PREFLIGHT_ONLY must be unset or YES" >&2
  exit 4
fi
if (( EUID != 0 )); then
  echo "DPDK dual-PF validation must run as root" >&2
  exit 13
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
DPDK_VERSION="${DPDK_VERSION:-25.11.2}"
DPDK_ROOT="${DPDK_ROOT:-${CODE_ROOT}/.deps/install/dpdk-${DPDK_VERSION}}"
THRESHOLDS_FILE="$1"
DPDK_BINARY="${CODE_ROOT}/rust/hft-dpdk/target/release/hft-dpdk"
HUGEPAGE_TARGET_NODE_PATH="/sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
HUGEPAGE_NODE_GLOB="/sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages"
HUGEPAGE_MOUNT="/dev/hugepages"
DPDK_RUNTIME_ROOT="/var/run/dpdk"
LOCK_FILE="/run/lock/hft-dpdk-bnx2x.lock"

for command_name in awk basename cat cp date diff ethtool find flock fuser grep \
  ip jq kill mkdir modprobe mountpoint mv pgrep python3 readlink setsid sha256sum \
  sleep sort rmdir sed stat sysctl tail tc timeout umount xargs; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "required command is unavailable: ${command_name}" >&2
    exit 4
  fi
done
exec 9> "${LOCK_FILE}"
if ! flock -n 9; then
  echo "another HFT DPDK validation owns ${LOCK_FILE}" >&2
  exit 13
fi
for path in "${THRESHOLDS_FILE}" "${DPDK_BINARY}" \
  "${DPDK_ROOT}/hft-build-manifest.txt" "${HUGEPAGE_TARGET_NODE_PATH}" \
  "${CODE_ROOT}/scripts/validate_dpdk_run.py" \
  "${CODE_ROOT}/scripts/compose_dpdk_run_acceptance.py" \
  "${CODE_ROOT}/scripts/preflight_dpdk_bnx2x.py" \
  "${CODE_ROOT}/scripts/preflight_dpdk_cpu_idle.py" /usr/bin/time; do
  if [[ ! -e "${path}" ]]; then
    echo "required path is missing: ${path}" >&2
    exit 4
  fi
done
if ! jq -e '
  .schema_version == 2
  and .qualification_mode == "release_gate_v2"
  and .frozen == true
  and .diagnostic_only == true
  and .final_pareto_ingestion_allowed == false
  and .max_pipeline_drop_rate == 0
  and .queue_count == 1
  and .expected_backend == "dpdk_bnx2x_single_queue"
  and (.binary_freeze_pending | type == "boolean")
  and (
    if .binary_freeze_pending then
      .expected_binary_sha256 == null
    else
      (.expected_binary_sha256 | type == "string"
        and test("^[0-9a-f]{64}$"))
    end
  )
  and (.expected_runner_sha256 | type == "string"
    and test("^[0-9a-f]{64}$"))
  and (.expected_validator_sha256 | type == "string"
    and test("^[0-9a-f]{64}$"))
  and (.expected_composer_sha256 | type == "string"
    and test("^[0-9a-f]{64}$"))
  and (.expected_cpu_preflight_sha256 | type == "string"
    and test("^[0-9a-f]{64}$"))
  and (.expected_dpdk_preflight_sha256 | type == "string"
    and test("^[0-9a-f]{64}$"))
  and (.expected_dpdk_build_manifest_sha256 | type == "string"
    and test("^[0-9a-f]{64}$"))
  and (.candidate_id | type == "string" and length > 0)
  and (.capture_interface | type == "string" and length > 0)
  and (.replay_interface | type == "string" and length > 0)
  and (.capture_pci | type == "string" and length > 0)
  and (.replay_pci | type == "string" and length > 0)
  and (.main_cpu | type == "number" and . >= 0 and . == floor)
  and (.rx_cpus | type == "array" and length == 1
    and all(.[]; type == "number" and . >= 0 and . == floor))
  and (.tx_cpus | type == "array" and length == 1
    and all(.[]; type == "number" and . >= 0 and . == floor))
  and (([.main_cpu] + .rx_cpus + .tx_cpus | unique | length) == 3)
  and (.realtime_priority | type == "number" and . >= 0 and . <= 20 and . == floor)
  and (.max_end_to_end_p99_us | type == "number" and . > 0)
  and (.max_end_to_end_p999_us | type == "number" and . > 0)
  and .rate_window_alignment == "shared_monotonic_epoch_fixed_1s_v1"
  and (.min_rate_full_windows | type == "number" and . > 0 and . == floor)
  and .min_rate_full_windows == (.min_run_duration_s | ceil)
  and .latency_sampling.stride_packets == 1024
  and (.latency_sampling.min_samples | type == "number" and . > 0 and . == floor)
  and .latency_sampling.timestamp_source == "dpdk_tsc_embedded_tx_rx_v1"
  and (.cpu_preflight.max_utilization | type == "number" and . >= 0 and . < 1)
  and (.cpu_preflight.sample_seconds | type == "number" and . > 0)
  and (.cpu_preflight.samples | type == "number" and . > 0 and . == floor)
  and .cpu_preflight.include_smt_siblings == true
  and (.hugepage_count | type == "number" and . > 0 and . == floor)
  and .hugepage_size_bytes == 2097152
  and .hugepage_target_node_path ==
    "/sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
  and .hugepage_node_glob ==
    "/sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages"
  and .interface_baseline.profile == "dedicated_bnx2x_kernel_default_v1"
  and .interface_baseline.admin_up == true
  and .interface_baseline.mtu == 1500
  and .interface_baseline.txqlen == 1000
  and all([
    .interface_baseline.features_sha256,
    .interface_baseline.coalesce_sha256,
    .interface_baseline.ring_sha256,
    .interface_baseline.channels_sha256,
    .interface_baseline.qdisc_sha256
  ][]; type == "string" and test("^[0-9a-f]{64}$"))
  and (.resource_max.process_cpu_cores_average | type == "number" and . > 0)
  and (.resource_max.process_rss_kib | type == "number" and . > 0)
  and (.resource_max.process_wall_overhead_s | type == "number" and . >= 0)
  and (.resource_max.hugepage_reserved_bytes | type == "number" and . > 0)
  and .resource_max.hugepage_reserved_bytes >=
    (.hugepage_count * .hugepage_size_bytes)
  and .resource_semantics == {
    "process_cpu_cores_average": "gnu_time_cpu_percent_div_100",
    "process_rss_kib": "gnu_time_max_rss_kib",
    "process_wall_overhead_s": "gnu_time_elapsed_minus_rust_duration",
    "hugepage_reserved_bytes": "sysfs_all_numa_nodes_reserved_count_during_run"
  }
' "${THRESHOLDS_FILE}" >/dev/null; then
  echo "thresholds do not satisfy release_gate_v2 schema" >&2
  exit 4
fi
candidate_id="$(jq -er '.candidate_id' "${THRESHOLDS_FILE}")"
thresholds_sha256="$(sha256sum "${THRESHOLDS_FILE}" | awk '{print $1}')"
binary_freeze_pending="$(jq -r '.binary_freeze_pending' "${THRESHOLDS_FILE}")"
expected_binary_sha256="$(jq -r '.expected_binary_sha256 // ""' "${THRESHOLDS_FILE}")"
expected_runner_sha256="$(jq -er '.expected_runner_sha256' "${THRESHOLDS_FILE}")"
expected_validator_sha256="$(jq -er '.expected_validator_sha256' "${THRESHOLDS_FILE}")"
expected_composer_sha256="$(jq -er '.expected_composer_sha256' "${THRESHOLDS_FILE}")"
expected_cpu_preflight_sha256="$(jq -er '.expected_cpu_preflight_sha256' \
  "${THRESHOLDS_FILE}")"
expected_dpdk_preflight_sha256="$(jq -er '.expected_dpdk_preflight_sha256' \
  "${THRESHOLDS_FILE}")"
expected_dpdk_manifest_sha256="$(jq -er \
  '.expected_dpdk_build_manifest_sha256' "${THRESHOLDS_FILE}")"
CAPTURE_INTERFACE="$(jq -er '.capture_interface' "${THRESHOLDS_FILE}")"
REPLAY_INTERFACE="$(jq -er '.replay_interface' "${THRESHOLDS_FILE}")"
CAPTURE_PCI="$(jq -er '.capture_pci' "${THRESHOLDS_FILE}")"
REPLAY_PCI="$(jq -er '.replay_pci' "${THRESHOLDS_FILE}")"
MAIN_CPU="$(jq -er '.main_cpu' "${THRESHOLDS_FILE}")"
HUGEPAGES="$(jq -er '.hugepage_count' "${THRESHOLDS_FILE}")"
HUGEPAGE_TARGET_NODE_PATH="$(jq -er '.hugepage_target_node_path' \
  "${THRESHOLDS_FILE}")"
HUGEPAGE_NODE_GLOB="$(jq -er '.hugepage_node_glob' "${THRESHOLDS_FILE}")"
baseline_mtu="$(jq -er '.interface_baseline.mtu' "${THRESHOLDS_FILE}")"
baseline_txqlen="$(jq -er '.interface_baseline.txqlen' "${THRESHOLDS_FILE}")"
baseline_features_sha256="$(jq -er '.interface_baseline.features_sha256' \
  "${THRESHOLDS_FILE}")"
baseline_coalesce_sha256="$(jq -er '.interface_baseline.coalesce_sha256' \
  "${THRESHOLDS_FILE}")"
baseline_ring_sha256="$(jq -er '.interface_baseline.ring_sha256' "${THRESHOLDS_FILE}")"
baseline_channels_sha256="$(jq -er '.interface_baseline.channels_sha256' \
  "${THRESHOLDS_FILE}")"
baseline_qdisc_sha256="$(jq -er '.interface_baseline.qdisc_sha256' \
  "${THRESHOLDS_FILE}")"
mapfile -t HUGEPAGE_NODE_PATHS < <(compgen -G "${HUGEPAGE_NODE_GLOB}" | sort)
if (( ${#HUGEPAGE_NODE_PATHS[@]} == 0 )); then
  echo "no NUMA hugepage counters matched the frozen node glob" >&2
  exit 4
fi
target_node_seen=0
for path in "${HUGEPAGE_NODE_PATHS[@]}"; do
  if [[ ! -f "${path}" || ! -r "${path}" \
    || ! "$(cat "${path}")" =~ ^[0-9]+$ ]]; then
    echo "invalid NUMA hugepage counter: ${path}" >&2
    exit 4
  fi
  [[ "${path}" == "${HUGEPAGE_TARGET_NODE_PATH}" ]] && target_node_seen=1
done
if (( target_node_seen != 1 )); then
  echo "target NUMA hugepage counter is not covered by the frozen node glob" >&2
  exit 4
fi
if [[ ! "${candidate_id}" =~ ^[A-Za-z0-9_.-]+$ ]]; then
  echo "candidate ID contains unsupported characters" >&2
  exit 4
fi
runner_sha256="$(sha256sum "${CODE_ROOT}/scripts/run_dpdk_bnx2x_validation.sh" \
  | awk '{print $1}')"
validator_sha256="$(sha256sum "${CODE_ROOT}/scripts/validate_dpdk_run.py" \
  | awk '{print $1}')"
composer_sha256="$(sha256sum "${CODE_ROOT}/scripts/compose_dpdk_run_acceptance.py" \
  | awk '{print $1}')"
cpu_preflight_sha256="$(sha256sum "${CODE_ROOT}/scripts/preflight_dpdk_cpu_idle.py" \
  | awk '{print $1}')"
dpdk_preflight_sha256="$(sha256sum "${CODE_ROOT}/scripts/preflight_dpdk_bnx2x.py" \
  | awk '{print $1}')"
dpdk_manifest_sha256="$(sha256sum "${DPDK_ROOT}/hft-build-manifest.txt" \
  | awk '{print $1}')"
binary_sha256="$(sha256sum "${DPDK_BINARY}" | awk '{print $1}')"
if [[ "${runner_sha256}" != "${expected_runner_sha256}" \
  || "${validator_sha256}" != "${expected_validator_sha256}" \
  || "${composer_sha256}" != "${expected_composer_sha256}" \
  || "${cpu_preflight_sha256}" != "${expected_cpu_preflight_sha256}" \
  || "${dpdk_preflight_sha256}" != "${expected_dpdk_preflight_sha256}" \
  || "${dpdk_manifest_sha256}" != "${expected_dpdk_manifest_sha256}" ]]; then
  echo "release scripts or DPDK build manifest do not match the frozen candidate" >&2
  exit 4
fi
if [[ "${HFT_DPDK_PREFLIGHT_ONLY:-}" != "YES" ]]; then
  if [[ "${binary_freeze_pending}" != "false" \
    || "${binary_sha256}" != "${expected_binary_sha256}" ]]; then
    echo "release binary hash is not frozen; build and freeze it before PF mutation" >&2
    exit 4
  fi
fi
target_mpps="$(jq -er \
  'select(.frozen == true) | .target_load_mpps | select(type == "number" and . > 0)' \
  "${THRESHOLDS_FILE}")"
duration_s="$(jq -er \
  '.min_run_duration_s | select(type == "number" and . > 0) | ceil' \
  "${THRESHOLDS_FILE}")"
burst_size="$(jq -er '.burst_size | select(. == 64 or . == 128 or . == 256)' \
  "${THRESHOLDS_FILE}")"
frame_size="$(jq -er '.frame_size_bytes | select(type == "number" and . >= 64 and . <= 1500)' \
  "${THRESHOLDS_FILE}")"
queue_count="$(jq -er '(.queue_count // 1) | select(type == "number" and . >= 1 and . <= 16) | floor' \
  "${THRESHOLDS_FILE}")"
rx_cpus="$(jq -er '(.rx_cpus // [36]) | map(tostring) | join(",")' \
  "${THRESHOLDS_FILE}")"
tx_cpus="$(jq -er '(.tx_cpus // [44]) | map(tostring) | join(",")' \
  "${THRESHOLDS_FILE}")"
realtime_priority="$(jq -er \
  '(.realtime_priority // 0) | select(type == "number" and . >= 0 and . <= 20 and . == floor)' \
  "${THRESHOLDS_FILE}")"
max_p99_us="$(jq -er '.max_end_to_end_p99_us' "${THRESHOLDS_FILE}")"
max_p999_us="$(jq -er '.max_end_to_end_p999_us' "${THRESHOLDS_FILE}")"
cpu_preflight_max_utilization="$(jq -er \
  '.cpu_preflight.max_utilization' "${THRESHOLDS_FILE}")"
cpu_preflight_sample_seconds="$(jq -er \
  '.cpu_preflight.sample_seconds' "${THRESHOLDS_FILE}")"
cpu_preflight_samples="$(jq -er '.cpu_preflight.samples' "${THRESHOLDS_FILE}")"
if [[ "${CAPTURE_INTERFACE}" == "${REPLAY_INTERFACE}" \
  || "${CAPTURE_PCI}" == "${REPLAY_PCI}" \
  || ! "${CAPTURE_PCI}" =~ ^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$ \
  || ! "${REPLAY_PCI}" =~ ^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$ ]]; then
  echo "capture/replay identity in thresholds is invalid" >&2
  exit 4
fi
if [[ "${CAPTURE_PCI%.*}" != "${REPLAY_PCI%.*}" ]]; then
  echo "authorized PFs must belong to the same PCI adapter" >&2
  exit 13
fi
if (( realtime_priority > 0 )); then
  if ! command -v chrt >/dev/null 2>&1; then
    echo "realtime_priority requires chrt for a non-disruptive capability preflight" >&2
    exit 5
  fi
  realtime_limit="$(ulimit -r)"
  if [[ "${realtime_limit}" != "unlimited" ]] &&
    (( realtime_limit < realtime_priority )); then
    echo "realtime_priority=${realtime_priority} exceeds RLIMIT_RTPRIO=${realtime_limit}" >&2
    exit 5
  fi
  if ! chrt -f "${realtime_priority}" true >/dev/null 2>&1; then
    echo "SCHED_FIFO priority ${realtime_priority} is unavailable; refusing PF disruption" >&2
    exit 5
  fi
fi

driver_for_pci() {
  local pci="$1"
  if [[ -L "/sys/bus/pci/devices/${pci}/driver" ]]; then
    basename "$(readlink "/sys/bus/pci/devices/${pci}/driver")"
  else
    echo "none"
  fi
}

current_combined() {
  ethtool -l "$1" | awk \
    '$0 == "Current hardware settings:" {current=1; next}
     current && $1 == "Combined:" {print $2; exit}'
}

current_ring() {
  ethtool -g "$1" | awk -v field="$2" \
    '$0 == "Current hardware settings:" {current=1; next}
     current && $1 == field ":" {print $2; exit}'
}

current_coalesce() {
  ethtool -c "$1" | awk -F': ' -v field="$2" \
    '$1 == field {print $2; exit}' | awk '{print $1}'
}

current_feature() {
  ethtool -k "$1" | awk -F': ' -v field="$2" \
     '$1 == field {print $2; exit}' | awk '{print $1}'
}

normalized_ethtool_sha256() {
  local option="$1"
  local interface="$2"
  ethtool "${option}" "${interface}" | tail -n +2 | sha256sum | awk '{print $1}'
}

qdisc_sha256() {
  tc -j qdisc show dev "$1" | jq -S . | sha256sum | awk '{print $1}'
}

hugepage_nodes_json() {
  local path count
  for path in "${HUGEPAGE_NODE_PATHS[@]}"; do
    count="$(cat "${path}")" || return
    [[ "${count}" =~ ^[0-9]+$ ]] || return 1
    jq -cn --arg path "${path}" --argjson count "${count}" \
      '{path: $path, count: $count}'
  done | jq -s 'sort_by(.path)'
}

hugepage_global_count() {
  jq -er '[.[].count] | add // 0'
}

interface_pci() {
  local interface="$1"
  if [[ ! -L "/sys/class/net/${interface}/device" ]]; then
    return 1
  fi
  basename "$(readlink -f "/sys/class/net/${interface}/device")"
}

if [[ "$(interface_pci "${CAPTURE_INTERFACE}")" != "${CAPTURE_PCI}" \
  || "$(interface_pci "${REPLAY_INTERFACE}")" != "${REPLAY_PCI}" ]]; then
  echo "interface-to-PCI mapping does not match the frozen candidate" >&2
  exit 13
fi

adapter_pf_count=0
adapter_pf_match_count=0
for device_path in "/sys/bus/pci/devices/${CAPTURE_PCI%.*}".*; do
  [[ -e "${device_path}" ]] || continue
  device_class="$(cat "${device_path}/class" 2>/dev/null || true)"
  [[ "${device_class}" == 0x02* ]] || continue
  adapter_pf_count=$((adapter_pf_count + 1))
  device_bdf="$(basename "${device_path}")"
  if [[ "${device_bdf}" == "${CAPTURE_PCI}" || "${device_bdf}" == "${REPLAY_PCI}" ]]; then
    adapter_pf_match_count=$((adapter_pf_match_count + 1))
  fi
done
if (( adapter_pf_count != 2 || adapter_pf_match_count != 2 )); then
  echo "the approved pair does not cover every Ethernet PF on the adapter" >&2
  exit 13
fi

for interface in "${CAPTURE_INTERFACE}" "${REPLAY_INTERFACE}"; do
  link_json="$(ip -j link show dev "${interface}")"
  if [[ "$(jq -er '.[0].mtu' <<< "${link_json}")" != "${baseline_mtu}" \
    || "$(jq -er '.[0].txqlen' <<< "${link_json}")" != "${baseline_txqlen}" \
    || "$(jq -er '.[0].flags | index("UP") != null' <<< "${link_json}")" != true \
    || "$(normalized_ethtool_sha256 -k "${interface}")" != "${baseline_features_sha256}" \
    || "$(normalized_ethtool_sha256 -c "${interface}")" != "${baseline_coalesce_sha256}" \
    || "$(normalized_ethtool_sha256 -g "${interface}")" != "${baseline_ring_sha256}" \
    || "$(normalized_ethtool_sha256 -l "${interface}")" != "${baseline_channels_sha256}" \
    || "$(qdisc_sha256 "${interface}")" != "${baseline_qdisc_sha256}" ]]; then
    echo "${interface} does not match the frozen dedicated-interface baseline" >&2
    exit 13
  fi
  if [[ -L "/sys/class/net/${interface}/master" ]] \
    || compgen -G "/sys/class/net/${interface}/upper_*" >/dev/null; then
    echo "${interface} belongs to a master or upper device" >&2
    exit 13
  fi
  ip -j -4 address show dev "${interface}" | jq -e '.[0].addr_info | length == 0' \
    >/dev/null || {
      echo "${interface} has configured addresses; refusing disruptive validation" >&2
      exit 13
    }
  ip -j -6 address show dev "${interface}" | jq -e \
    '[.[0].addr_info[]? | select(.scope != "link")] | length == 0' >/dev/null || {
      echo "${interface} has configured non-link-local IPv6 addresses" >&2
      exit 13
    }
  ip -j -4 route show table all dev "${interface}" | jq -e 'length == 0' >/dev/null || {
      echo "${interface} has active routes; refusing disruptive validation" >&2
      exit 13
    }
  ip -j -6 route show table all dev "${interface}" | jq -e \
    '[.[] | select(
      (.protocol == "kernel" and .scope == "link"
        or .protocol == "kernel" and .type == "multicast"
          and .dst == "ff00::/8" and .table == "local") | not
    )] | length == 0' \
    >/dev/null || {
      echo "${interface} has active non-link-local IPv6 routes" >&2
      exit 13
    }
  for family in -4 -6; do
    ip -j "${family}" rule show | jq -e --arg interface "${interface}" \
      '[.[] | select(
        .iif == $interface or .oif == $interface
        or .iifname == $interface or .oifname == $interface
      )] | length == 0' \
      >/dev/null || {
        echo "${interface} is referenced by a policy-routing rule" >&2
        exit 13
      }
  done
  if ip -details link show dev "${interface}" | grep -q 'prog/xdp'; then
    echo "${interface} has an attached XDP program" >&2
    exit 13
  fi
done
if [[ "$(driver_for_pci "${CAPTURE_PCI}")" != "bnx2x" \
  || "$(driver_for_pci "${REPLAY_PCI}")" != "bnx2x" ]]; then
  echo "both PFs must start on bnx2x" >&2
  exit 13
fi
if pgrep -af '[h]ft-dpdk|[t]estpmd|[d]pdk-test|[d]pdk-proc' >/dev/null; then
  echo "an existing DPDK process is active; refusing shared-host mutation" >&2
  exit 13
fi
for runtime_path in "${DPDK_RUNTIME_ROOT}"/*/config "${DPDK_RUNTIME_ROOT}"/*/mp_socket; do
  [[ -e "${runtime_path}" || -S "${runtime_path}" ]] || continue
  if fuser "${runtime_path}" >/dev/null 2>&1; then
    echo "an active DPDK runtime owns ${runtime_path}" >&2
    exit 13
  fi
done
if mountpoint -q "${HUGEPAGE_MOUNT}" \
  && find "${HUGEPAGE_MOUNT}" -maxdepth 1 -type f -print -quit | grep -q .; then
  echo "the hugepage mount already contains files; ownership is ambiguous" >&2
  exit 13
fi

capture_combined_before="$(current_combined "${CAPTURE_INTERFACE}")"
replay_combined_before="$(current_combined "${REPLAY_INTERFACE}")"
capture_mtu_before="$(ip -j link show dev "${CAPTURE_INTERFACE}" | jq -er '.[0].mtu')"
replay_mtu_before="$(ip -j link show dev "${REPLAY_INTERFACE}" | jq -er '.[0].mtu')"
capture_txqlen_before="$(ip -j link show dev "${CAPTURE_INTERFACE}" | jq -er '.[0].txqlen')"
replay_txqlen_before="$(ip -j link show dev "${REPLAY_INTERFACE}" | jq -er '.[0].txqlen')"
capture_admin_up_before="$(ip -j link show dev "${CAPTURE_INTERFACE}" \
  | jq -er '.[0].flags | index("UP") != null')"
replay_admin_up_before="$(ip -j link show dev "${REPLAY_INTERFACE}" \
  | jq -er '.[0].flags | index("UP") != null')"
capture_rx_ring_before="$(current_ring "${CAPTURE_INTERFACE}" RX)"
capture_tx_ring_before="$(current_ring "${CAPTURE_INTERFACE}" TX)"
replay_rx_ring_before="$(current_ring "${REPLAY_INTERFACE}" RX)"
replay_tx_ring_before="$(current_ring "${REPLAY_INTERFACE}" TX)"
capture_rx_usecs_before="$(current_coalesce "${CAPTURE_INTERFACE}" rx-usecs)"
capture_tx_usecs_before="$(current_coalesce "${CAPTURE_INTERFACE}" tx-usecs)"
replay_rx_usecs_before="$(current_coalesce "${REPLAY_INTERFACE}" rx-usecs)"
replay_tx_usecs_before="$(current_coalesce "${REPLAY_INTERFACE}" tx-usecs)"
capture_gro_before="$(current_feature "${CAPTURE_INTERFACE}" generic-receive-offload)"
capture_lro_before="$(current_feature "${CAPTURE_INTERFACE}" large-receive-offload)"
replay_gro_before="$(current_feature "${REPLAY_INTERFACE}" generic-receive-offload)"
replay_lro_before="$(current_feature "${REPLAY_INTERFACE}" large-receive-offload)"
capture_driver_override_before="$(cat "/sys/bus/pci/devices/${CAPTURE_PCI}/driver_override")"
replay_driver_override_before="$(cat "/sys/bus/pci/devices/${REPLAY_PCI}/driver_override")"
hugepage_nodes_before_json="$(hugepage_nodes_json)"
hugepages_global_before="$(hugepage_global_count <<< "${hugepage_nodes_before_json}")"
hugepages_target_before="$(cat "${HUGEPAGE_TARGET_NODE_PATH}")"
if [[ "${hugepages_global_before}" != "0" \
  || "${hugepages_target_before}" != "0" ]]; then
  echo "pre-existing reserved hugepages have ambiguous ownership" >&2
  exit 13
fi
uio_pci_loaded_before=0
uio_loaded_before=0
[[ -d /sys/module/uio_pci_generic ]] && uio_pci_loaded_before=1
[[ -d /sys/module/uio ]] && uio_loaded_before=1
hugetlb_mounted_before=0
mountpoint -q "${HUGEPAGE_MOUNT}" && hugetlb_mounted_before=1

if [[ "${HFT_DPDK_PREFLIGHT_ONLY:-}" == "YES" ]]; then
  run_id="hft_dpdk_release_preflight_$(date -u +%Y%m%dT%H%M%S%NZ)"
else
  run_id="hft_r0_dpdk_$(date -u +%Y%m%dT%H%M%S%NZ)"
fi
run_dir="${REPLAY_ROOT}/${run_id}"
mkdir -p "${run_dir}"
cp --reflink=auto --preserve=timestamps "${THRESHOLDS_FILE}" \
  "${run_dir}/frozen_thresholds.json"
cp --reflink=auto --preserve=timestamps "${DPDK_BINARY}" "${run_dir}/hft-dpdk.bin"
cp --reflink=auto --preserve=timestamps \
  "${CODE_ROOT}/rust/hft-dpdk/Cargo.toml" \
  "${CODE_ROOT}/rust/hft-dpdk/build.rs" \
  "${CODE_ROOT}/rust/hft-dpdk/csrc/hft_dpdk_shim.h" \
  "${CODE_ROOT}/rust/hft-dpdk/csrc/hft_dpdk_shim.c" \
  "${CODE_ROOT}/rust/hft-dpdk/src/main.rs" \
  "${CODE_ROOT}/scripts/run_dpdk_bnx2x_validation.sh" \
  "${CODE_ROOT}/scripts/validate_dpdk_run.py" \
  "${CODE_ROOT}/scripts/compose_dpdk_run_acceptance.py" \
  "${CODE_ROOT}/scripts/preflight_dpdk_cpu_idle.py" \
  "${CODE_ROOT}/scripts/preflight_dpdk_bnx2x.py" "${run_dir}/"
cp --reflink=auto --preserve=timestamps \
  "${DPDK_ROOT}/hft-build-manifest.txt" "${run_dir}/dpdk-build-manifest.txt"

set +e
python3 "${run_dir}/preflight_dpdk_cpu_idle.py" \
  --cpus "${MAIN_CPU},${rx_cpus},${tx_cpus}" \
  --max-utilization "${cpu_preflight_max_utilization}" \
  --sample-seconds "${cpu_preflight_sample_seconds}" \
  --samples "${cpu_preflight_samples}" \
  --include-smt-siblings \
  --output "${run_dir}/cpu_preflight.json" \
  > "${run_dir}/cpu_preflight.stdout.json" \
  2> "${run_dir}/cpu_preflight.stderr.log"
cpu_preflight_status="$?"
set -e
if (( cpu_preflight_status != 0 )); then
  blocked_id="hft_dpdk_preflight_blocked_$(date -u +%Y%m%dT%H%M%S%NZ)"
  blocked_dir="${REPLAY_ROOT}/${blocked_id}"
  mv "${run_dir}" "${blocked_dir}"
  run_id="${blocked_id}"
  run_dir="${blocked_dir}"
  {
    echo "run_id=${run_id}"
    echo "scope=dpdk_release_gate_cpu_preflight_blocked"
    echo "candidate_id=${candidate_id}"
    echo "frozen_thresholds_sha256=${thresholds_sha256}"
    echo "cpu_preflight_exit_status=${cpu_preflight_status}"
    echo "mutations_performed=false"
    echo "completed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "${run_dir}/manifest.txt"
  (
    cd "${run_dir}"
    find . -maxdepth 1 -type f ! -name 'evidence_sha256*' -printf '%P\0' \
      | sort -z | xargs -0 sha256sum > evidence_sha256_complete.txt
    sha256sum -c evidence_sha256_complete.txt \
      > evidence_sha256_complete_check.txt
  )
  echo "${run_dir}"
  exit 5
fi

snapshot_interface() {
  local interface="$1"
  local prefix="$2"
  local status=0
  ip -s -j link show dev "${interface}" \
    > "${run_dir}/${prefix}_ip_link.json" || status=1
  ethtool "${interface}" > "${run_dir}/${prefix}_ethtool.txt" || status=1
  ethtool -k "${interface}" > "${run_dir}/${prefix}_features.txt" || status=1
  ethtool -c "${interface}" > "${run_dir}/${prefix}_coalesce.txt" || status=1
  ethtool -g "${interface}" > "${run_dir}/${prefix}_ring.txt" || status=1
  ethtool -l "${interface}" > "${run_dir}/${prefix}_channels.txt" || status=1
  ethtool -S "${interface}" > "${run_dir}/${prefix}_stats.txt" || status=1
  ip -j -4 address show dev "${interface}" | jq -S . \
    > "${run_dir}/${prefix}_ipv4_addresses.json" || status=1
  ip -j -6 address show dev "${interface}" | jq -S . \
    > "${run_dir}/${prefix}_ipv6_addresses.json" || status=1
  ip -j -4 route show table all dev "${interface}" | jq -S . \
    > "${run_dir}/${prefix}_ipv4_routes.json" || status=1
  ip -j -6 route show table all dev "${interface}" | jq -S . \
    > "${run_dir}/${prefix}_ipv6_routes.json" || status=1
  tc -j qdisc show dev "${interface}" | jq -S . \
    > "${run_dir}/${prefix}_tc_qdisc.json" || status=1
  return "${status}"
}

snapshot_interface "${CAPTURE_INTERFACE}" capture_before
snapshot_interface "${REPLAY_INTERFACE}" replay_before
  python3 "${run_dir}/preflight_dpdk_bnx2x.py" \
  --interfaces "${CAPTURE_INTERFACE}" "${REPLAY_INTERFACE}" \
  --dpdk-root "${DPDK_ROOT}" --output "${run_dir}/preflight.json" \
  > "${run_dir}/preflight.stdout.json"
jq -e \
  --arg capture_interface "${CAPTURE_INTERFACE}" \
  --arg replay_interface "${REPLAY_INTERFACE}" \
  --arg capture_pci "${CAPTURE_PCI}" \
  --arg replay_pci "${REPLAY_PCI}" \
  '.ready_for_disruptive_validation == true
  and .explicit_approval_required == true
  and .mutations_performed == false
  and ([.ports[] | select(
    .interface == $capture_interface
    and .pci_address == $capture_pci
    and .driver == "bnx2x"
    and .carrier == 1
    and .speed_mbps == 10000
  )] | length == 1)
  and ([.ports[] | select(
    .interface == $replay_interface
    and .pci_address == $replay_pci
    and .driver == "bnx2x"
    and .carrier == 1
    and .speed_mbps == 10000
  )] | length == 1)' \
  "${run_dir}/preflight.json" >/dev/null
if [[ "${HFT_DPDK_PREFLIGHT_ONLY:-}" == "YES" ]]; then
  {
    echo "run_id=${run_id}"
    echo "scope=dpdk_release_gate_non_mutating_preflight"
    echo "candidate_id=${candidate_id}"
    echo "frozen_thresholds_sha256=${thresholds_sha256}"
    echo "binary_freeze_pending=${binary_freeze_pending}"
    echo "current_binary_sha256=${binary_sha256}"
    echo "mutations_performed=false"
    echo "completed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "${run_dir}/manifest.txt"
  (
    cd "${run_dir}"
    find . -maxdepth 1 -type f ! -name 'evidence_sha256*' -printf '%P\0' \
      | sort -z | xargs -0 sha256sum > evidence_sha256_preflight.txt
    sha256sum -c evidence_sha256_preflight.txt \
      > evidence_sha256_preflight_check.txt
  )
  echo "${run_dir}"
  exit 0
fi

mutation_started=0
restore_attempted=0
restore_status=0
restoration_verified=false
child_pid=""
child_pgid=""
termination_signal=""
hugepages_global_during=0
validator_status=99
acceptance_status=99
evidence_status=0
restore_steps="${run_dir}/restoration_steps.tsv"
: > "${restore_steps}"

record_restore_step() {
  local name="$1"
  local status="$2"
  printf '%s\t%s\n' "${name}" "${status}" >> "${restore_steps}"
  if (( status != 0 )); then
    restore_status=1
  fi
}

run_restore_step() {
  local name="$1"
  shift
  "$@"
  local status="$?"
  record_restore_step "${name}" "${status}"
  return "${status}"
}

write_sysfs_value() {
  local value="$1"
  local path="$2"
  printf '%s\n' "${value}" > "${path}"
}

restore_driver_override() {
  local pci="$1"
  local original="$2"
  if [[ -z "${original}" || "${original}" == "(null)" ]]; then
    printf '\n' > "/sys/bus/pci/devices/${pci}/driver_override"
  else
    printf '%s\n' "${original}" > "/sys/bus/pci/devices/${pci}/driver_override"
  fi
}

bind_bnx2x() {
  local pci="$1"
  local original_override="$2"
  local driver
  driver="$(driver_for_pci "${pci}")"
  if [[ "${driver}" == "uio_pci_generic" ]]; then
    write_sysfs_value "${pci}" /sys/bus/pci/drivers/uio_pci_generic/unbind || return
  elif [[ "${driver}" != "none" && "${driver}" != "bnx2x" ]]; then
    return 1
  fi
  if [[ "$(driver_for_pci "${pci}")" != "bnx2x" ]]; then
    write_sysfs_value bnx2x "/sys/bus/pci/devices/${pci}/driver_override" || return
    write_sysfs_value "${pci}" /sys/bus/pci/drivers_probe || return
  fi
  restore_driver_override "${pci}" "${original_override}" || return
  [[ "$(driver_for_pci "${pci}")" == "bnx2x" ]]
}

wait_for_netdevs() {
  local attempt
  for attempt in {1..50}; do
    if [[ -e "/sys/class/net/${CAPTURE_INTERFACE}" \
      && -e "/sys/class/net/${REPLAY_INTERFACE}" ]]; then
      return 0
    fi
    sleep 0.1
  done
  return 1
}

restore_interface_settings() {
  local interface="$1"
  local combined="$2"
  local rx_ring="$3"
  local tx_ring="$4"
  local rx_usecs="$5"
  local tx_usecs="$6"
  local gro="$7"
  local lro="$8"
  local mtu="$9"
  local txqlen="${10}"
  local admin_up="${11}"
  ethtool -L "${interface}" combined "${combined}" || return
  ethtool -G "${interface}" rx "${rx_ring}" tx "${tx_ring}" || return
  ethtool -C "${interface}" rx-usecs "${rx_usecs}" tx-usecs "${tx_usecs}" || return
  ethtool -K "${interface}" gro "${gro}" lro "${lro}" || return
  ip link set dev "${interface}" mtu "${mtu}" txqueuelen "${txqlen}" || return
  if [[ "${admin_up}" == true ]]; then
    ip link set dev "${interface}" up
  else
    ip link set dev "${interface}" down
  fi
}

remove_runtime_prefix() {
  local runtime_dir="${DPDK_RUNTIME_ROOT}/${run_id}"
  if pgrep -af '[h]ft-dpdk\.bin' | grep -F -- "--file-prefix ${run_id}" >/dev/null; then
    return 1
  fi
  if [[ ! "${run_id}" =~ ^hft_r0_dpdk_[0-9]{8}T[0-9]{6}[0-9]+Z$ \
    || "${runtime_dir}" != /var/run/dpdk/hft_r0_dpdk_* ]]; then
    return 1
  fi
  if [[ -d "${runtime_dir}" ]]; then
    find "${runtime_dir}" -mindepth 1 -delete || return
    rmdir "${runtime_dir}" || return
  fi
  [[ ! -e "${runtime_dir}" ]]
}

stop_child() {
  local status=0
  if [[ -n "${child_pid}" ]] && kill -0 "${child_pid}" 2>/dev/null; then
    kill -TERM -- "-${child_pgid}" 2>/dev/null || true
    for _ in {1..50}; do
      kill -0 "${child_pid}" 2>/dev/null || break
      sleep 0.1
    done
    if kill -0 "${child_pid}" 2>/dev/null; then
      kill -KILL -- "-${child_pgid}" 2>/dev/null || true
    fi
    wait "${child_pid}" 2>/dev/null || true
  fi
  if pgrep -af '[h]ft-dpdk\.bin' \
    | grep -F -- "--file-prefix ${run_id}" >/dev/null; then
    status=1
  fi
  child_pid=""
  child_pgid=""
  return "${status}"
}

restore_host() {
  if (( restore_attempted == 1 )); then
    return "${restore_status}"
  fi
  restore_attempted=1
  if (( mutation_started == 0 )); then
    record_restore_step no_mutation 0
    return 0
  fi
  set +e
  if ! run_restore_step child_stopped stop_child; then
    return "${restore_status}"
  fi
  run_restore_step "bind_${CAPTURE_PCI}_bnx2x" \
    bind_bnx2x "${CAPTURE_PCI}" "${capture_driver_override_before}"
  run_restore_step "bind_${REPLAY_PCI}_bnx2x" \
    bind_bnx2x "${REPLAY_PCI}" "${replay_driver_override_before}"
  run_restore_step netdevs_reappeared wait_for_netdevs
  run_restore_step "restore_${CAPTURE_INTERFACE}" restore_interface_settings \
    "${CAPTURE_INTERFACE}" "${capture_combined_before}" \
    "${capture_rx_ring_before}" "${capture_tx_ring_before}" \
    "${capture_rx_usecs_before}" "${capture_tx_usecs_before}" \
    "${capture_gro_before}" "${capture_lro_before}" \
    "${capture_mtu_before}" "${capture_txqlen_before}" \
    "${capture_admin_up_before}"
  run_restore_step "restore_${REPLAY_INTERFACE}" restore_interface_settings \
    "${REPLAY_INTERFACE}" "${replay_combined_before}" \
    "${replay_rx_ring_before}" "${replay_tx_ring_before}" \
    "${replay_rx_usecs_before}" "${replay_tx_usecs_before}" \
    "${replay_gro_before}" "${replay_lro_before}" \
    "${replay_mtu_before}" "${replay_txqlen_before}" \
    "${replay_admin_up_before}"
  run_restore_step runtime_prefix_removed remove_runtime_prefix
  run_restore_step hugepage_count_restored \
    write_sysfs_value "${hugepages_target_before}" "${HUGEPAGE_TARGET_NODE_PATH}"
  if (( hugetlb_mounted_before == 0 )); then
    run_restore_step hugetlb_unmounted umount "${HUGEPAGE_MOUNT}"
  else
    record_restore_step hugetlb_mount_preserved 0
  fi
  if (( uio_pci_loaded_before == 0 )); then
    run_restore_step uio_pci_generic_unloaded modprobe -r uio_pci_generic
  else
    record_restore_step uio_pci_generic_preserved 0
  fi
  if (( uio_loaded_before == 0 )); then
    run_restore_step uio_unloaded modprobe -r uio
  else
    record_restore_step uio_preserved 0
  fi
  return "${restore_status}"
}

on_signal() {
  termination_signal="$1"
  exit "$2"
}

trap 'on_signal HUP 129' HUP
trap 'on_signal INT 130' INT
trap 'on_signal TERM 143' TERM

verify_host_restoration() {
  local capture_speed replay_speed capture_carrier replay_carrier current_mount_status
  local attempt
  for attempt in {1..50}; do
    capture_speed="$(ethtool "${CAPTURE_INTERFACE}" 2>/dev/null \
      | awk '/Speed:/ {gsub(/Mb.s/, "", $2); print $2; exit}')"
    replay_speed="$(ethtool "${REPLAY_INTERFACE}" 2>/dev/null \
      | awk '/Speed:/ {gsub(/Mb.s/, "", $2); print $2; exit}')"
    capture_carrier="$(cat "/sys/class/net/${CAPTURE_INTERFACE}/carrier" 2>/dev/null || echo 0)"
    replay_carrier="$(cat "/sys/class/net/${REPLAY_INTERFACE}/carrier" 2>/dev/null || echo 0)"
    if [[ "${capture_speed}" == "10000" && "${replay_speed}" == "10000" \
      && "${capture_carrier}" == "1" && "${replay_carrier}" == "1" ]]; then
      break
    fi
    sleep 0.1
  done
  mountpoint -q "${HUGEPAGE_MOUNT}"
  current_mount_status="$?"
  [[ "$(driver_for_pci "${CAPTURE_PCI}")" == "bnx2x" ]] || return 1
  [[ "$(driver_for_pci "${REPLAY_PCI}")" == "bnx2x" ]] || return 1
  [[ "$(interface_pci "${CAPTURE_INTERFACE}")" == "${CAPTURE_PCI}" ]] || return 1
  [[ "$(interface_pci "${REPLAY_INTERFACE}")" == "${REPLAY_PCI}" ]] || return 1
  [[ "${capture_speed}" == "10000" && "${replay_speed}" == "10000" ]] || return 1
  [[ "${capture_carrier}" == "1" && "${replay_carrier}" == "1" ]] || return 1
  [[ "$(current_combined "${CAPTURE_INTERFACE}")" == "${capture_combined_before}" ]] || return 1
  [[ "$(current_combined "${REPLAY_INTERFACE}")" == "${replay_combined_before}" ]] || return 1
  [[ "$(current_ring "${CAPTURE_INTERFACE}" RX)" == "${capture_rx_ring_before}" ]] || return 1
  [[ "$(current_ring "${CAPTURE_INTERFACE}" TX)" == "${capture_tx_ring_before}" ]] || return 1
  [[ "$(current_ring "${REPLAY_INTERFACE}" RX)" == "${replay_rx_ring_before}" ]] || return 1
  [[ "$(current_ring "${REPLAY_INTERFACE}" TX)" == "${replay_tx_ring_before}" ]] || return 1
  [[ "$(current_coalesce "${CAPTURE_INTERFACE}" rx-usecs)" == "${capture_rx_usecs_before}" ]] || return 1
  [[ "$(current_coalesce "${CAPTURE_INTERFACE}" tx-usecs)" == "${capture_tx_usecs_before}" ]] || return 1
  [[ "$(current_coalesce "${REPLAY_INTERFACE}" rx-usecs)" == "${replay_rx_usecs_before}" ]] || return 1
  [[ "$(current_coalesce "${REPLAY_INTERFACE}" tx-usecs)" == "${replay_tx_usecs_before}" ]] || return 1
  [[ "$(current_feature "${CAPTURE_INTERFACE}" generic-receive-offload)" == "${capture_gro_before}" ]] || return 1
  [[ "$(current_feature "${CAPTURE_INTERFACE}" large-receive-offload)" == "${capture_lro_before}" ]] || return 1
  [[ "$(current_feature "${REPLAY_INTERFACE}" generic-receive-offload)" == "${replay_gro_before}" ]] || return 1
  [[ "$(current_feature "${REPLAY_INTERFACE}" large-receive-offload)" == "${replay_lro_before}" ]] || return 1
  [[ "$(ip -j link show dev "${CAPTURE_INTERFACE}" | jq -er '.[0].mtu')" == "${capture_mtu_before}" ]] || return 1
  [[ "$(ip -j link show dev "${REPLAY_INTERFACE}" | jq -er '.[0].mtu')" == "${replay_mtu_before}" ]] || return 1
  [[ "$(ip -j link show dev "${CAPTURE_INTERFACE}" | jq -er '.[0].txqlen')" == "${capture_txqlen_before}" ]] || return 1
  [[ "$(ip -j link show dev "${REPLAY_INTERFACE}" | jq -er '.[0].txqlen')" == "${replay_txqlen_before}" ]] || return 1
  [[ "$(ip -j link show dev "${CAPTURE_INTERFACE}" | jq -er '.[0].flags | index("UP") != null')" == "${capture_admin_up_before}" ]] || return 1
  [[ "$(ip -j link show dev "${REPLAY_INTERFACE}" | jq -er '.[0].flags | index("UP") != null')" == "${replay_admin_up_before}" ]] || return 1
  [[ "$(hugepage_nodes_json)" == "${hugepage_nodes_before_json}" ]] || return 1
  [[ ! -e "${DPDK_RUNTIME_ROOT}/${run_id}" ]] || return 1
  [[ "${current_mount_status}" == "$((1 - hugetlb_mounted_before))" ]] || return 1
  [[ "$(cat "/sys/bus/pci/devices/${CAPTURE_PCI}/driver_override")" \
    == "${capture_driver_override_before}" ]] || return 1
  [[ "$(cat "/sys/bus/pci/devices/${REPLAY_PCI}/driver_override")" \
    == "${replay_driver_override_before}" ]] || return 1
  (( uio_pci_loaded_before == 1 )) || [[ ! -d /sys/module/uio_pci_generic ]] || return 1
  (( uio_loaded_before == 1 )) || [[ ! -d /sys/module/uio ]] || return 1
  find "${HUGEPAGE_MOUNT}" -maxdepth 1 -type f -print -quit 2>/dev/null \
    | grep -q . && return 1
  diff -q "${run_dir}/capture_before_tc_qdisc.json" \
    "${run_dir}/capture_restored_tc_qdisc.json" >/dev/null || return 1
  diff -q "${run_dir}/replay_before_tc_qdisc.json" \
    "${run_dir}/replay_restored_tc_qdisc.json" >/dev/null || return 1
  for suffix in ethtool.txt features.txt coalesce.txt ring.txt channels.txt \
    ipv4_addresses.json ipv6_addresses.json ipv4_routes.json ipv6_routes.json; do
    diff -q "${run_dir}/capture_before_${suffix}" \
      "${run_dir}/capture_restored_${suffix}" >/dev/null || return 1
    diff -q "${run_dir}/replay_before_${suffix}" \
      "${run_dir}/replay_restored_${suffix}" >/dev/null || return 1
  done
  return 0
}

build_evidence() {
  local original_status="$1"
  local snapshot_status=0
  local verify_status=0
  local required_json present_json missing_json empty_json
  local base_status complete_status
  # Bash nounset treats a declared-but-never-assigned empty array as unset.
  # Initialize every evidence array so a fully complete run can seal evidence.
  local -a required_files=() present_files=() missing_files=() empty_files=()
  local -a snapshot_suffixes=()
  set +e
  if [[ -e "/sys/class/net/${CAPTURE_INTERFACE}" \
    && -e "/sys/class/net/${REPLAY_INTERFACE}" ]]; then
    snapshot_interface "${CAPTURE_INTERFACE}" capture_restored || snapshot_status=1
    snapshot_interface "${REPLAY_INTERFACE}" replay_restored || snapshot_status=1
  else
    snapshot_status=1
  fi
  verify_host_restoration
  verify_status="$?"
  record_restore_step final_state_verification "${verify_status}"
  if (( restore_status == 0 && snapshot_status == 0 && verify_status == 0 )); then
    restoration_verified=true
  else
    restoration_verified=false
  fi
  jq -Rn '
    [inputs | split("\t") |
      {step: .[0], status: (.[1] | tonumber), ok: ((.[1] | tonumber) == 0)}]
  ' < "${restore_steps}" > "${run_dir}/restoration_ledger.json"
  python3 "${run_dir}/validate_dpdk_run.py" \
    --thresholds "${run_dir}/frozen_thresholds.json" \
    --result "${run_dir}/result.json" \
    --process-time "${run_dir}/process_time.txt" \
    --hugepage-snapshot "${run_dir}/hugepages_during.json" \
    --runner "${run_dir}/run_dpdk_bnx2x_validation.sh" \
    --binary "${run_dir}/hft-dpdk.bin" \
    --dpdk-build-manifest "${run_dir}/dpdk-build-manifest.txt" \
    --cpu-preflight "${run_dir}/cpu_preflight.json" \
    --output "${run_dir}/data_resource_acceptance.json" \
    > "${run_dir}/validation.stdout.json" 2>> "${run_dir}/stderr.log"
  validator_status="$?"
  {
    echo "original_exit_status=${original_status}"
    echo "termination_signal=${termination_signal:-none}"
    echo "validator_exit_status=${validator_status}"
    echo "restore_status=${restore_status}"
    echo "restoration_verified=${restoration_verified}"
    echo "dpdk_runtime_prefix_removed=$([[ ! -e "${DPDK_RUNTIME_ROOT}/${run_id}" ]] && echo true || echo false)"
    echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${run_dir}/manifest.txt"

  required_files=(
    manifest.txt frozen_thresholds.json preflight.json preflight.stdout.json
    hft-dpdk.bin Cargo.toml build.rs hft_dpdk_shim.h hft_dpdk_shim.c
    main.rs run_dpdk_bnx2x_validation.sh validate_dpdk_run.py
    compose_dpdk_run_acceptance.py preflight_dpdk_bnx2x.py
    preflight_dpdk_cpu_idle.py cpu_preflight.json cpu_preflight.stdout.json
    cpu_preflight.stderr.log
    dpdk-build-manifest.txt result.json process_time.txt stdout.log stderr.log
    hugepages_during.json
    data_resource_acceptance.json validation.stdout.json restoration_steps.tsv
    restoration_ledger.json
  )
  snapshot_suffixes=(
    ip_link.json ethtool.txt features.txt coalesce.txt ring.txt channels.txt
    stats.txt ipv4_addresses.json ipv6_addresses.json ipv4_routes.json
    ipv6_routes.json tc_qdisc.json
  )
  for prefix in capture_before replay_before capture_restored replay_restored; do
    for suffix in "${snapshot_suffixes[@]}"; do
      required_files+=("${prefix}_${suffix}")
    done
  done
  for file in "${required_files[@]}"; do
    if [[ -f "${run_dir}/${file}" ]]; then
      present_files+=("${file}")
    else
      missing_files+=("${file}")
    fi
  done
  for file in "${required_files[@]}"; do
    if [[ "${file}" != "stdout.log" && "${file}" != "stderr.log" \
      && "${file}" != "cpu_preflight.stderr.log" \
      && -f "${run_dir}/${file}" && ! -s "${run_dir}/${file}" ]]; then
      empty_files+=("${file}")
    fi
  done
  required_json="$(printf '%s\n' "${required_files[@]}" | jq -R . | jq -s .)"
  present_json="$(printf '%s\n' "${present_files[@]:-}" | sed '/^$/d' | jq -R . | jq -s .)"
  missing_json="$(printf '%s\n' "${missing_files[@]:-}" | sed '/^$/d' | jq -R . | jq -s .)"
  empty_json="$(printf '%s\n' "${empty_files[@]:-}" | sed '/^$/d' | jq -R . | jq -s .)"
  jq -n \
    --argjson required "${required_json}" \
    --argjson present "${present_json}" \
    --argjson missing "${missing_json}" \
    --argjson empty "${empty_json}" \
    --argjson restoration_verified "${restoration_verified}" \
    '{
      schema_version: 1,
      required: $required,
      present: $present,
      missing: $missing,
      empty_required: $empty,
      restoration_verified: $restoration_verified,
      evidence_complete_before_hash:
        (($missing | length) == 0 and ($empty | length) == 0)
    }' > "${run_dir}/evidence_inventory.json"
  if (( ${#missing_files[@]} != 0 || ${#empty_files[@]} != 0 )); then
    evidence_status=1
  fi
  (
    cd "${run_dir}" || exit
    printf '%s\0' "${present_files[@]}" evidence_inventory.json \
      | sort -z | xargs -0 sha256sum > evidence_sha256_base.txt
    sha256sum -c evidence_sha256_base.txt > evidence_sha256_base_check.txt
  )
  base_status="$?"
  (( base_status == 0 )) || evidence_status=1
  (
    cd "${run_dir}" || exit
    find . -maxdepth 1 -type f ! -name 'evidence_sha256*' \
      ! -name 'acceptance.json' -printf '%P\0' \
      | sort -z | xargs -0 sha256sum > evidence_sha256_complete.txt
    sha256sum -c evidence_sha256_complete.txt > evidence_sha256_complete_check.txt
  )
  complete_status="$?"
  (( complete_status == 0 )) || evidence_status=1
  (( snapshot_status == 0 )) || evidence_status=1
  python3 "${run_dir}/compose_dpdk_run_acceptance.py" \
    --data-resource-acceptance "${run_dir}/data_resource_acceptance.json" \
    --evidence-inventory "${run_dir}/evidence_inventory.json" \
    --original-exit-status "${original_status}" \
    --validator-exit-status "${validator_status}" \
    --restore-status "${restore_status}" \
    --restoration-verified "${restoration_verified}" \
    --evidence-status "${evidence_status}" \
    --base-hash-check-status "${base_status}" \
    --complete-hash-check-status "${complete_status}" \
    --termination-signal "${termination_signal:-none}" \
    --base-hash-evidence "${run_dir}/evidence_sha256_base_check.txt" \
    --complete-hash-evidence "${run_dir}/evidence_sha256_complete_check.txt" \
    --output "${run_dir}/acceptance.json" \
    > "${run_dir}/acceptance.stdout.json" 2>> "${run_dir}/stderr.log"
  acceptance_status="$?"
  return 0
}

finalize() {
  local original_status="$?"
  local final_status=99
  local build_status=99
  # Replace the normal EXIT handler with a non-recursive emergency guard.
  # Any unexpected fatal error during cleanup must be visible to the caller.
  trap 'trap - EXIT; exit 99' EXIT
  # A second signal during the restoration window must not terminate the shell
  # before both PFs and hugepages are restored.  The first signal is already
  # recorded by on_signal() and represented by original_status.
  trap '' HUP INT TERM
  set +e
  restore_host
  build_evidence "${original_status}"
  build_status="$?"
  if (( build_status != 0 )); then
    final_status=17
  elif (( restore_status != 0 )) || [[ "${restoration_verified}" != true ]]; then
    final_status=15
  elif (( evidence_status != 0 )); then
    final_status=16
  elif (( acceptance_status != 0 )); then
    final_status=10
  else
    final_status="${original_status}"
  fi
  echo "${run_dir}"
  trap - EXIT
  exit "${final_status}"
}

trap finalize EXIT

{
  echo "run_id=${run_id}"
  echo "scope=r0_dpdk_bnx2x_capture_only"
  echo "candidate_id=${candidate_id}"
  echo "frozen_thresholds_sha256=${thresholds_sha256}"
  echo "capture_interface=${CAPTURE_INTERFACE}"
  echo "replay_interface=${REPLAY_INTERFACE}"
  echo "capture_pci=${CAPTURE_PCI}"
  echo "replay_pci=${REPLAY_PCI}"
  echo "target_mpps=${target_mpps}"
  echo "duration_s=${duration_s}"
  echo "burst_size=${burst_size}"
  echo "frame_size_bytes=${frame_size}"
  echo "queue_count=${queue_count}"
  echo "rx_cpus=${rx_cpus}"
  echo "tx_cpus=${tx_cpus}"
  echo "realtime_priority=${realtime_priority}"
  echo "main_cpu=${MAIN_CPU}"
  echo "max_end_to_end_p99_us=${max_p99_us}"
  echo "max_end_to_end_p999_us=${max_p999_us}"
  echo "hugepages_global_before=${hugepages_global_before}"
  echo "hugepages_target_before=${hugepages_target_before}"
  echo "hugepages_candidate=${HUGEPAGES}"
  echo "hugetlb_mounted_before=${hugetlb_mounted_before}"
  echo "explicit_disruptive_approval=YES"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${run_dir}/manifest.txt"

mutation_started=1
modprobe uio_pci_generic
mkdir -p "${HUGEPAGE_MOUNT}"
if ! mountpoint -q "${HUGEPAGE_MOUNT}"; then
  mount -t hugetlbfs nodev "${HUGEPAGE_MOUNT}"
fi
write_sysfs_value "${HUGEPAGES}" "${HUGEPAGE_TARGET_NODE_PATH}"
hugepage_nodes_during_json="$(hugepage_nodes_json)"
hugepages_global_during="$(hugepage_global_count <<< "${hugepage_nodes_during_json}")"
hugepages_target_during="$(cat "${HUGEPAGE_TARGET_NODE_PATH}")"
if [[ "${hugepages_global_during}" != "${HUGEPAGES}" \
  || "${hugepages_target_during}" != "${HUGEPAGES}" ]]; then
  echo "requested hugepages were not reserved exactly" >&2
  exit 14
fi
jq -n \
  --arg node_glob "${HUGEPAGE_NODE_GLOB}" \
  --arg target_node_path "${HUGEPAGE_TARGET_NODE_PATH}" \
  --arg sampled_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson nodes_before "${hugepage_nodes_before_json}" \
  --argjson nodes_during "${hugepage_nodes_during_json}" \
  --argjson global_count_before "${hugepages_global_before}" \
  --argjson global_count_during "${hugepages_global_during}" \
  '{
    schema_version: 2,
    source: "sysfs_all_numa_nodes_reserved_hugepages",
    node_glob: $node_glob,
    target_node_path: $target_node_path,
    sampled_at: $sampled_at,
    nodes_before: $nodes_before,
    nodes_during: $nodes_during,
    global_count_before: $global_count_before,
    global_count_during: $global_count_during,
    page_size_bytes: 2097152
  }' > "${run_dir}/hugepages_during.json"
ip link set dev "${CAPTURE_INTERFACE}" down
ip link set dev "${REPLAY_INTERFACE}" down
for pci in "${CAPTURE_PCI}" "${REPLAY_PCI}"; do
  write_sysfs_value uio_pci_generic "/sys/bus/pci/devices/${pci}/driver_override"
  write_sysfs_value "${pci}" /sys/bus/pci/drivers/bnx2x/unbind
  write_sysfs_value "${pci}" /sys/bus/pci/drivers_probe
  if [[ "$(driver_for_pci "${pci}")" != "uio_pci_generic" ]]; then
    echo "failed to bind ${pci} to uio_pci_generic" >&2
    exit 14
  fi
done

: > "${run_dir}/stdout.log"
: > "${run_dir}/stderr.log"
: > "${run_dir}/process_time.txt"
set +e
run_timeout_s="$((duration_s + 35))"
setsid timeout --signal=TERM --kill-after=5s "${run_timeout_s}s" \
  /usr/bin/time -v -o "${run_dir}/process_time.txt" \
  "${run_dir}/hft-dpdk.bin" \
  --candidate-id "${candidate_id}" \
  --frozen-thresholds-sha256 "${thresholds_sha256}" \
  --capture-pci "${CAPTURE_PCI}" \
  --replay-pci "${REPLAY_PCI}" \
  --file-prefix "${run_id}" \
  --rx-cpus "${rx_cpus}" \
  --tx-cpus "${tx_cpus}" \
  --queue-count "${queue_count}" \
  --realtime-priority "${realtime_priority}" \
  --main-cpu "${MAIN_CPU}" \
  --duration-s "${duration_s}" \
  --target-mpps "${target_mpps}" \
  --burst-size "${burst_size}" \
  --frame-size "${frame_size}" \
  --max-end-to-end-p99-us "${max_p99_us}" \
  --max-end-to-end-p999-us "${max_p999_us}" \
  --output "${run_dir}/result.json" \
  > "${run_dir}/stdout.log" 2> "${run_dir}/stderr.log" &
child_pid="$!"
child_pgid="${child_pid}"
wait "${child_pid}"
dpdk_status="$?"
child_pid=""
child_pgid=""
set -e
exit "${dpdk_status}"
