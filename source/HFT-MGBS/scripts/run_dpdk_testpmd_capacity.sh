#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 FROZEN_CONTRACT_JSON" >&2
  exit 2
fi
if [[ "${HFT_ALLOW_DISRUPTIVE_DPDK:-}" != "YES" ]]; then
  echo "set HFT_ALLOW_DISRUPTIVE_DPDK=YES only after approving dual-PF interruption" >&2
  exit 13
fi
if (( EUID != 0 )); then
  echo "testpmd dual-PF capacity diagnostic must run as root" >&2
  exit 13
fi

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
DPDK_VERSION="${DPDK_VERSION:-25.11.2}"
DPDK_ROOT="${DPDK_ROOT:-${CODE_ROOT}/.deps/install/dpdk-${DPDK_VERSION}}"
TESTPMD="${TESTPMD:-${DPDK_ROOT}/bin/dpdk-testpmd}"
CONTRACT_FILE="$1"
SUMMARY_SCRIPT="${CODE_ROOT}/scripts/summarize_dpdk_testpmd_capacity.py"
HUGEPAGE_MOUNT="/dev/hugepages"
DPDK_RUNTIME_ROOT="/var/run/dpdk"
LOCK_FILE="/run/lock/hft-dpdk-bnx2x.lock"

for command_name in awk basename cat cp date diff ethtool find flock fuser grep \
  ip jq kill mkdir modprobe mountpoint pgrep python3 readlink setsid sha256sum \
  sleep sort rmdir sed stat tail tc timeout umount xargs mkfifo rm; do
  command -v "${command_name}" >/dev/null 2>&1 || {
    echo "required command is unavailable: ${command_name}" >&2
    exit 4
  }
done
for path in "${CONTRACT_FILE}" "${TESTPMD}" "${SUMMARY_SCRIPT}"; do
  [[ -e "${path}" ]] || { echo "required path is missing: ${path}" >&2; exit 4; }
done
exec 9> "${LOCK_FILE}"
flock -n 9 || { echo "another HFT DPDK validation owns ${LOCK_FILE}" >&2; exit 13; }

jq -e '
  .schema_version == 1
  and .scope == "dpdk_testpmd_dual_pf_capacity_only"
  and .frozen == true and .diagnostic_only == true
  and .final_pareto_ingestion_allowed == false
  and (.candidate_id | type == "string" and test("^[A-Za-z0-9_.-]+$"))
  and (.capture_interface | type == "string" and length > 0)
  and (.replay_interface | type == "string" and length > 0)
  and (.capture_pci | type == "string" and length > 0)
  and (.replay_pci | type == "string" and length > 0)
  and (.rx_main_cpu | type == "number" and . >= 0 and . == floor)
  and (.rx_queue_count as $queues
    | (.rx_worker_cpus | type == "array" and length == $queues
      and all(.[]; type == "number" and . >= 0 and . == floor)))
  and (.tx_main_cpu | type == "number" and . >= 0 and . == floor)
  and (.tx_queue_count as $queues
    | (.tx_worker_cpus | type == "array" and length == $queues
      and all(.[]; type == "number" and . >= 0 and . == floor)))
  and (([.rx_main_cpu, .tx_main_cpu] + .rx_worker_cpus + .tx_worker_cpus
    | unique | length) == (2 + .rx_queue_count + .tx_queue_count))
  and .numa_node == 1
  and .rx_queue_count == 1
  and .tx_queue_count == 1
  and .expected_backend == "dpdk_bnx2x_testpmd_q1_capacity"
  and .frame_size_bytes == 64
  and (.duration_seconds | type == "number" and . >= 15 and . == floor)
  and .stats_period_seconds == 1
  and .rx_lead_rate_windows == 2
  and (.warmup_rate_windows | type == "number" and . >= 0 and . == floor)
  and (.minimum_measured_rate_windows | type == "number" and . > 0 and . == floor)
  and .duration_seconds >= (.warmup_rate_windows + .minimum_measured_rate_windows)
  and (.target_capacity_mpps | type == "number" and . > 0)
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
' "${CONTRACT_FILE}" >/dev/null || {
  echo "capacity contract does not satisfy the frozen schema" >&2
  exit 4
}

candidate_id="$(jq -er '.candidate_id' "${CONTRACT_FILE}")"
CAPTURE_INTERFACE="$(jq -er '.capture_interface' "${CONTRACT_FILE}")"
REPLAY_INTERFACE="$(jq -er '.replay_interface' "${CONTRACT_FILE}")"
CAPTURE_PCI="$(jq -er '.capture_pci' "${CONTRACT_FILE}")"
REPLAY_PCI="$(jq -er '.replay_pci' "${CONTRACT_FILE}")"
RX_MAIN_CPU="$(jq -er '.rx_main_cpu' "${CONTRACT_FILE}")"
RX_CPUS="$(jq -er '.rx_worker_cpus | map(tostring) | join(",")' "${CONTRACT_FILE}")"
TX_MAIN_CPU="$(jq -er '.tx_main_cpu' "${CONTRACT_FILE}")"
TX_CPUS="$(jq -er '.tx_worker_cpus | map(tostring) | join(",")' "${CONTRACT_FILE}")"
NUMA_NODE="$(jq -er '.numa_node' "${CONTRACT_FILE}")"
RX_QUEUE_COUNT="$(jq -er '.rx_queue_count' "${CONTRACT_FILE}")"
TX_QUEUE_COUNT="$(jq -er '.tx_queue_count' "${CONTRACT_FILE}")"
DURATION="$(jq -er '.duration_seconds' "${CONTRACT_FILE}")"
STATS_PERIOD="$(jq -er '.stats_period_seconds' "${CONTRACT_FILE}")"
HUGEPAGES="$(jq -er '.hugepage_count' "${CONTRACT_FILE}")"
HUGEPAGE_TARGET_NODE_PATH="$(jq -er '.hugepage_target_node_path' "${CONTRACT_FILE}")"
HUGEPAGE_NODE_GLOB="$(jq -er '.hugepage_node_glob' "${CONTRACT_FILE}")"
baseline_mtu="$(jq -er '.interface_baseline.mtu' "${CONTRACT_FILE}")"
baseline_txqlen="$(jq -er '.interface_baseline.txqlen' "${CONTRACT_FILE}")"
baseline_features_sha256="$(jq -er '.interface_baseline.features_sha256' "${CONTRACT_FILE}")"
baseline_coalesce_sha256="$(jq -er '.interface_baseline.coalesce_sha256' "${CONTRACT_FILE}")"
baseline_ring_sha256="$(jq -er '.interface_baseline.ring_sha256' "${CONTRACT_FILE}")"
baseline_channels_sha256="$(jq -er '.interface_baseline.channels_sha256' "${CONTRACT_FILE}")"
baseline_qdisc_sha256="$(jq -er '.interface_baseline.qdisc_sha256' "${CONTRACT_FILE}")"

IFS=, read -r -a CAPACITY_CPUS <<< \
  "${RX_MAIN_CPU},${RX_CPUS},${TX_MAIN_CPU},${TX_CPUS}"
for cpu in "${CAPACITY_CPUS[@]}"; do
  [[ "${cpu}" =~ ^[0-9]+$ \
    && -e "/sys/devices/system/cpu/cpu${cpu}/node${NUMA_NODE}" ]] || {
    echo "CPU ${cpu} is not online on frozen NUMA node ${NUMA_NODE}" >&2
    exit 5
  }
done

driver_for_pci() {
  [[ -L "/sys/bus/pci/devices/$1/driver" ]] \
    && basename "$(readlink "/sys/bus/pci/devices/$1/driver")" || echo none
}
interface_pci() {
  [[ -L "/sys/class/net/$1/device" ]] || return 1
  basename "$(readlink -f "/sys/class/net/$1/device")"
}
current_combined() {
  ethtool -l "$1" | awk '$0 == "Current hardware settings:" {c=1; next} c && $1 == "Combined:" {print $2; exit}'
}
current_ring() {
  ethtool -g "$1" | awk -v field="$2" '$0 == "Current hardware settings:" {c=1; next} c && $1 == field ":" {print $2; exit}'
}
current_coalesce() {
  ethtool -c "$1" | awk -F': ' -v field="$2" '$1 == field {print $2; exit}' | awk '{print $1}'
}
current_feature() {
  ethtool -k "$1" | awk -F': ' -v field="$2" '$1 == field {print $2; exit}' | awk '{print $1}'
}
normalized_ethtool_sha256() {
  ethtool "$1" "$2" | tail -n +2 | sha256sum | awk '{print $1}'
}
qdisc_sha256() { tc -j qdisc show dev "$1" | jq -S . | sha256sum | awk '{print $1}'; }

mapfile -t HUGEPAGE_NODE_PATHS < <(compgen -G "${HUGEPAGE_NODE_GLOB}" | sort)
(( ${#HUGEPAGE_NODE_PATHS[@]} > 0 )) || { echo "no hugepage counters matched" >&2; exit 4; }
hugepage_nodes_json() {
  local path count
  for path in "${HUGEPAGE_NODE_PATHS[@]}"; do
    count="$(cat "${path}")" || return
    [[ "${count}" =~ ^[0-9]+$ ]] || return 1
    jq -cn --arg path "${path}" --argjson count "${count}" '{path:$path,count:$count}'
  done | jq -s 'sort_by(.path)'
}
hugepage_global_count() { jq -er '[.[].count] | add // 0'; }

[[ "$(interface_pci "${CAPTURE_INTERFACE}")" == "${CAPTURE_PCI}" \
  && "$(interface_pci "${REPLAY_INTERFACE}")" == "${REPLAY_PCI}" ]] || {
  echo "interface-to-PCI mapping does not match the frozen contract" >&2; exit 13;
}
[[ "${CAPTURE_PCI%.*}" == "${REPLAY_PCI%.*}" ]] || {
  echo "authorized PFs must belong to the same PCI adapter" >&2; exit 13;
}
[[ "$(driver_for_pci "${CAPTURE_PCI}")" == bnx2x \
  && "$(driver_for_pci "${REPLAY_PCI}")" == bnx2x ]] || {
  echo "both PFs must start on bnx2x" >&2; exit 13;
}
for process_dir in /proc/[0-9]*; do
  process_pid="${process_dir#/proc/}"
  [[ "${process_pid}" == "$$" ]] && continue
  process_exe="$(readlink "${process_dir}/exe" 2>/dev/null || true)"
  process_name="$(cat "${process_dir}/comm" 2>/dev/null || true)"
  case "${process_name}" in
    hft-dpdk|dpdk-testpmd|dpdk-testpmd.bin|dpdk-test|dpdk-proc)
      echo "an existing DPDK process is active: pid=${process_pid} name=${process_name}" >&2
      exit 13
      ;;
  esac
  case "$(basename "${process_exe:-none}")" in
    hft-dpdk|dpdk-testpmd|dpdk-testpmd.bin|dpdk-test|dpdk-proc)
      echo "an existing DPDK executable is active: pid=${process_pid} exe=${process_exe}" >&2
      exit 13
      ;;
  esac
done
for runtime_path in "${DPDK_RUNTIME_ROOT}"/*/config "${DPDK_RUNTIME_ROOT}"/*/mp_socket; do
  [[ -e "${runtime_path}" || -S "${runtime_path}" ]] || continue
  fuser "${runtime_path}" >/dev/null 2>&1 && {
    echo "an active DPDK runtime owns ${runtime_path}" >&2; exit 13;
  }
done
if mountpoint -q "${HUGEPAGE_MOUNT}" \
  && find "${HUGEPAGE_MOUNT}" -maxdepth 1 -type f -print -quit | grep -q .; then
  echo "the hugepage mount already contains files" >&2; exit 13
fi

for interface in "${CAPTURE_INTERFACE}" "${REPLAY_INTERFACE}"; do
  link_json="$(ip -j link show dev "${interface}")"
  [[ "$(jq -er '.[0].mtu' <<< "${link_json}")" == "${baseline_mtu}" \
    && "$(jq -er '.[0].txqlen' <<< "${link_json}")" == "${baseline_txqlen}" \
    && "$(jq -er '.[0].flags | index("UP") != null' <<< "${link_json}")" == true \
    && "$(normalized_ethtool_sha256 -k "${interface}")" == "${baseline_features_sha256}" \
    && "$(normalized_ethtool_sha256 -c "${interface}")" == "${baseline_coalesce_sha256}" \
    && "$(normalized_ethtool_sha256 -g "${interface}")" == "${baseline_ring_sha256}" \
    && "$(normalized_ethtool_sha256 -l "${interface}")" == "${baseline_channels_sha256}" \
    && "$(qdisc_sha256 "${interface}")" == "${baseline_qdisc_sha256}" ]] || {
    echo "${interface} does not match the frozen baseline" >&2; exit 13;
  }
  [[ ! -L "/sys/class/net/${interface}/master" ]] \
    && ! compgen -G "/sys/class/net/${interface}/upper_*" >/dev/null || {
      echo "${interface} belongs to a master or upper device" >&2; exit 13;
    }
  ip -j -4 address show dev "${interface}" | jq -e '.[0].addr_info | length == 0' >/dev/null \
    || { echo "${interface} has IPv4 addresses" >&2; exit 13; }
  ip -j -6 address show dev "${interface}" | jq -e '[.[0].addr_info[]? | select(.scope != "link")] | length == 0' >/dev/null \
    || { echo "${interface} has non-link-local IPv6 addresses" >&2; exit 13; }
  ip -j -4 route show table all dev "${interface}" | jq -e 'length == 0' >/dev/null \
    || { echo "${interface} has IPv4 routes" >&2; exit 13; }
  ip -j -6 route show table all dev "${interface}" | jq -e '[.[] | select((.protocol == "kernel" and .scope == "link" or .protocol == "kernel" and .type == "multicast" and .dst == "ff00::/8" and .table == "local") | not)] | length == 0' >/dev/null \
    || { echo "${interface} has non-link-local IPv6 routes" >&2; exit 13; }
  for family in -4 -6; do
    ip -j "${family}" rule show | jq -e --arg interface "${interface}" '[.[] | select(.iif == $interface or .oif == $interface or .iifname == $interface or .oifname == $interface)] | length == 0' >/dev/null \
      || { echo "${interface} is referenced by a policy route" >&2; exit 13; }
  done
  ip -details link show dev "${interface}" | grep -q 'prog/xdp' \
    && { echo "${interface} has an attached XDP program" >&2; exit 13; }
done

snapshot_interface() {
  local interface="$1" prefix="$2" status=0
  ip -s -j link show dev "${interface}" > "${run_dir}/${prefix}_ip_link.json" || status=1
  ethtool "${interface}" > "${run_dir}/${prefix}_ethtool.txt" || status=1
  ethtool -k "${interface}" > "${run_dir}/${prefix}_features.txt" || status=1
  ethtool -c "${interface}" > "${run_dir}/${prefix}_coalesce.txt" || status=1
  ethtool -g "${interface}" > "${run_dir}/${prefix}_ring.txt" || status=1
  ethtool -l "${interface}" > "${run_dir}/${prefix}_channels.txt" || status=1
  ethtool -S "${interface}" > "${run_dir}/${prefix}_stats.txt" || status=1
  ip -j -4 address show dev "${interface}" | jq -S . > "${run_dir}/${prefix}_ipv4_addresses.json" || status=1
  ip -j -6 address show dev "${interface}" | jq -S . > "${run_dir}/${prefix}_ipv6_addresses.json" || status=1
  ip -j -4 route show table all dev "${interface}" | jq -S . > "${run_dir}/${prefix}_ipv4_routes.json" || status=1
  ip -j -6 route show table all dev "${interface}" | jq -S . > "${run_dir}/${prefix}_ipv6_routes.json" || status=1
  tc -j qdisc show dev "${interface}" | jq -S . > "${run_dir}/${prefix}_tc_qdisc.json" || status=1
  return "${status}"
}

capture_combined_before="$(current_combined "${CAPTURE_INTERFACE}")"
replay_combined_before="$(current_combined "${REPLAY_INTERFACE}")"
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
[[ "${hugepages_global_before}" == 0 && "${hugepages_target_before}" == 0 ]] || {
  echo "pre-existing reserved hugepages have ambiguous ownership" >&2; exit 13;
}
uio_pci_loaded_before=0; uio_loaded_before=0; hugetlb_mounted_before=0
[[ -d /sys/module/uio_pci_generic ]] && uio_pci_loaded_before=1
[[ -d /sys/module/uio ]] && uio_loaded_before=1
mountpoint -q "${HUGEPAGE_MOUNT}" && hugetlb_mounted_before=1

run_id="hft_dpdk_testpmd_capacity_$(date -u +%Y%m%dT%H%M%S%NZ)"
run_dir="${REPLAY_ROOT}/${run_id}"
mkdir -p "${run_dir}"
cp --reflink=auto --preserve=timestamps "${CONTRACT_FILE}" "${run_dir}/frozen_contract.json"
cp --reflink=auto --preserve=timestamps "$0" "${run_dir}/run_dpdk_testpmd_capacity.sh"
cp --reflink=auto --preserve=timestamps "${SUMMARY_SCRIPT}" "${run_dir}/summarize_dpdk_testpmd_capacity.py"
cp --reflink=auto --preserve=timestamps "${TESTPMD}" "${run_dir}/dpdk-testpmd.bin"
snapshot_interface "${CAPTURE_INTERFACE}" capture_before
snapshot_interface "${REPLAY_INTERFACE}" replay_before

# A shared-host capacity result is useful only when all EAL/forwarding cores and
# their SMT siblings were idle before either PF was detached.
python3 "${CODE_ROOT}/scripts/preflight_dpdk_cpu_idle.py" \
  --cpus "${RX_MAIN_CPU},${RX_CPUS},${TX_MAIN_CPU},${TX_CPUS}" \
  --max-utilization 0.05 --sample-seconds 1 --samples 5 --include-smt-siblings \
  --output "${run_dir}/cpu_preflight.json" \
  > "${run_dir}/cpu_preflight.stdout.json" \
  2> "${run_dir}/cpu_preflight.stderr.log" || {
    echo "DPDK capacity CPUs or SMT siblings are not idle; no PF was mutated" >&2
    exit 5
  }

if [[ "${HFT_PREFLIGHT_ONLY:-}" == "YES" ]]; then
  jq -n --arg run_dir "${run_dir}" \
    '{schema_version:1,preflight_only:true,mutation_started:false,run_dir:$run_dir}' \
    > "${run_dir}/preflight_only.json"
  echo "${run_dir}"
  exit 0
fi

mutation_started=0; restore_attempted=0; restore_status=0; restoration_verified=false
rx_pid=""; tx_pid=""; rx_command_pid=""; tx_command_pid=""
termination_signal=""; original_status=99
restore_steps="${run_dir}/restoration_steps.tsv"; : > "${restore_steps}"
record_restore_step() { printf '%s\t%s\n' "$1" "$2" >> "${restore_steps}"; (( $2 == 0 )) || restore_status=1; }
run_restore_step() { local name="$1"; shift; "$@"; local status=$?; record_restore_step "${name}" "${status}"; return "${status}"; }
write_sysfs_value() { printf '%s\n' "$1" > "$2"; }
restore_driver_override() {
  if [[ -z "$2" || "$2" == "(null)" ]]; then printf '\n' > "/sys/bus/pci/devices/$1/driver_override";
  else printf '%s\n' "$2" > "/sys/bus/pci/devices/$1/driver_override"; fi
}
bind_bnx2x() {
  local pci="$1" original="$2" driver="$(driver_for_pci "$1")"
  [[ "${driver}" != uio_pci_generic ]] || write_sysfs_value "${pci}" /sys/bus/pci/drivers/uio_pci_generic/unbind || return
  [[ "$(driver_for_pci "${pci}")" == bnx2x ]] || {
    write_sysfs_value bnx2x "/sys/bus/pci/devices/${pci}/driver_override" || return
    write_sysfs_value "${pci}" /sys/bus/pci/drivers_probe || return
  }
  restore_driver_override "${pci}" "${original}" || return
  [[ "$(driver_for_pci "${pci}")" == bnx2x ]]
}
wait_for_netdevs() {
  for _ in {1..50}; do
    [[ -e "/sys/class/net/${CAPTURE_INTERFACE}" && -e "/sys/class/net/${REPLAY_INTERFACE}" ]] && return 0
    sleep 0.1
  done
  return 1
}
restore_interface_settings() {
  local interface="$1" combined="$2" rx_ring="$3" tx_ring="$4" rx_usecs="$5" tx_usecs="$6" gro="$7" lro="$8"
  ethtool -L "${interface}" combined "${combined}" || return
  ethtool -G "${interface}" rx "${rx_ring}" tx "${tx_ring}" || return
  ethtool -C "${interface}" rx-usecs "${rx_usecs}" tx-usecs "${tx_usecs}" || return
  ethtool -K "${interface}" gro "${gro}" lro "${lro}" || return
  ip link set dev "${interface}" mtu "${baseline_mtu}" txqueuelen "${baseline_txqlen}" up
}
stop_children() {
  local status=0 pid
  for pid in "${rx_pid}" "${tx_pid}" "${rx_command_pid}" "${tx_command_pid}"; do
    [[ -n "${pid}" ]] || continue
    kill -TERM -- "-${pid}" 2>/dev/null || true
    kill -TERM "${pid}" 2>/dev/null || true
  done
  for _ in {1..50}; do
    local live=0
    for pid in "${rx_pid}" "${tx_pid}" "${rx_command_pid}" "${tx_command_pid}"; do [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null && live=1; done
    (( live == 0 )) && break
    sleep 0.1
  done
  for pid in "${rx_pid}" "${tx_pid}" "${rx_command_pid}" "${tx_command_pid}"; do
    [[ -n "${pid}" ]] || continue
    kill -0 "${pid}" 2>/dev/null && kill -KILL -- "-${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  done
  pgrep -af '[d]pdk-testpmd\.bin' | grep -F "${run_id}" >/dev/null && status=1
  rx_pid=""; tx_pid=""; rx_command_pid=""; tx_command_pid=""
  return "${status}"
}
remove_runtime_prefixes() {
  local role path
  for role in rx tx; do
    path="${DPDK_RUNTIME_ROOT}/${run_id}_${role}"
    [[ "${path}" == /var/run/dpdk/hft_dpdk_testpmd_capacity_*_rx \
      || "${path}" == /var/run/dpdk/hft_dpdk_testpmd_capacity_*_tx ]] || return 1
    [[ ! -d "${path}" ]] || { find "${path}" -mindepth 1 -delete || return; rmdir "${path}" || return; }
  done
}
remove_command_fifos() {
  [[ -n "${rx_input:-}" || -n "${tx_input:-}" ]] || return 0
  [[ "${rx_input:-}" == "${run_dir}/rx.commands" \
    && "${tx_input:-}" == "${run_dir}/tx.commands" ]] || return 1
  rm -f -- "${rx_input}" "${tx_input}"
}
restore_host() {
  (( restore_attempted == 0 )) || return "${restore_status}"
  restore_attempted=1
  (( mutation_started == 1 )) || { record_restore_step no_mutation 0; return 0; }
  set +e
  run_restore_step children_stopped stop_children
  run_restore_step command_fifos_removed remove_command_fifos
  run_restore_step "bind_${CAPTURE_PCI}_bnx2x" bind_bnx2x "${CAPTURE_PCI}" "${capture_driver_override_before}"
  run_restore_step "bind_${REPLAY_PCI}_bnx2x" bind_bnx2x "${REPLAY_PCI}" "${replay_driver_override_before}"
  run_restore_step netdevs_reappeared wait_for_netdevs
  run_restore_step "restore_${CAPTURE_INTERFACE}" restore_interface_settings "${CAPTURE_INTERFACE}" "${capture_combined_before}" "${capture_rx_ring_before}" "${capture_tx_ring_before}" "${capture_rx_usecs_before}" "${capture_tx_usecs_before}" "${capture_gro_before}" "${capture_lro_before}"
  run_restore_step "restore_${REPLAY_INTERFACE}" restore_interface_settings "${REPLAY_INTERFACE}" "${replay_combined_before}" "${replay_rx_ring_before}" "${replay_tx_ring_before}" "${replay_rx_usecs_before}" "${replay_tx_usecs_before}" "${replay_gro_before}" "${replay_lro_before}"
  run_restore_step runtime_prefixes_removed remove_runtime_prefixes
  run_restore_step hugepage_count_restored write_sysfs_value "${hugepages_target_before}" "${HUGEPAGE_TARGET_NODE_PATH}"
  if (( hugetlb_mounted_before == 0 )); then run_restore_step hugetlb_unmounted umount "${HUGEPAGE_MOUNT}"; else record_restore_step hugetlb_mount_preserved 0; fi
  if (( uio_pci_loaded_before == 0 )); then run_restore_step uio_pci_generic_unloaded modprobe -r uio_pci_generic; else record_restore_step uio_pci_generic_preserved 0; fi
  if (( uio_loaded_before == 0 )); then run_restore_step uio_unloaded modprobe -r uio; else record_restore_step uio_preserved 0; fi
  return "${restore_status}"
}
on_signal() { termination_signal="$1"; exit "$2"; }
trap 'on_signal HUP 129' HUP
trap 'on_signal INT 130' INT
trap 'on_signal TERM 143' TERM

verify_host_restoration() {
  [[ "$(driver_for_pci "${CAPTURE_PCI}")" == bnx2x && "$(driver_for_pci "${REPLAY_PCI}")" == bnx2x ]] || return 1
  [[ "$(cat "/sys/bus/pci/devices/${CAPTURE_PCI}/driver_override")" == "${capture_driver_override_before}" \
    && "$(cat "/sys/bus/pci/devices/${REPLAY_PCI}/driver_override")" == "${replay_driver_override_before}" ]] || return 1
  [[ "$(interface_pci "${CAPTURE_INTERFACE}")" == "${CAPTURE_PCI}" && "$(interface_pci "${REPLAY_INTERFACE}")" == "${REPLAY_PCI}" ]] || return 1
  [[ "$(cat "/sys/class/net/${CAPTURE_INTERFACE}/carrier")" == 1 && "$(cat "/sys/class/net/${REPLAY_INTERFACE}/carrier")" == 1 ]] || return 1
  [[ "$(hugepage_nodes_json)" == "${hugepage_nodes_before_json}" ]] || return 1
  if (( hugetlb_mounted_before == 1 )); then mountpoint -q "${HUGEPAGE_MOUNT}" || return 1
  else ! mountpoint -q "${HUGEPAGE_MOUNT}" || return 1; fi
  if (( uio_pci_loaded_before == 1 )); then [[ -d /sys/module/uio_pci_generic ]] || return 1
  else [[ ! -d /sys/module/uio_pci_generic ]] || return 1; fi
  if (( uio_loaded_before == 1 )); then [[ -d /sys/module/uio ]] || return 1
  else [[ ! -d /sys/module/uio ]] || return 1; fi
  local interface link_json family
  for interface in "${CAPTURE_INTERFACE}" "${REPLAY_INTERFACE}"; do
    link_json="$(ip -j link show dev "${interface}")" || return 1
    [[ "$(jq -er '.[0].mtu' <<< "${link_json}")" == "${baseline_mtu}" \
      && "$(jq -er '.[0].txqlen' <<< "${link_json}")" == "${baseline_txqlen}" \
      && "$(jq -er '.[0].flags | index("UP") != null' <<< "${link_json}")" == true ]] || return 1
    [[ ! -L "/sys/class/net/${interface}/master" ]] || return 1
    ! compgen -G "/sys/class/net/${interface}/upper_*" >/dev/null || return 1
    ip -j -4 address show dev "${interface}" | jq -e '.[0].addr_info | length == 0' >/dev/null || return 1
    ip -j -6 address show dev "${interface}" | jq -e '[.[0].addr_info[]? | select(.scope != "link")] | length == 0' >/dev/null || return 1
    ip -j -4 route show table all dev "${interface}" | jq -e 'length == 0' >/dev/null || return 1
    ip -j -6 route show table all dev "${interface}" | jq -e '[.[] | select((.protocol == "kernel" and .scope == "link" or .protocol == "kernel" and .type == "multicast" and .dst == "ff00::/8" and .table == "local") | not)] | length == 0' >/dev/null || return 1
    for family in -4 -6; do
      ip -j "${family}" rule show | jq -e --arg interface "${interface}" '[.[] | select(.iif == $interface or .oif == $interface or .iifname == $interface or .oifname == $interface)] | length == 0' >/dev/null || return 1
    done
    ip -details link show dev "${interface}" | grep -q 'prog/xdp' && return 1
  done
  [[ "$(qdisc_sha256 "${CAPTURE_INTERFACE}")" == "${baseline_qdisc_sha256}" && "$(qdisc_sha256 "${REPLAY_INTERFACE}")" == "${baseline_qdisc_sha256}" ]] || return 1
  [[ "$(normalized_ethtool_sha256 -k "${CAPTURE_INTERFACE}")" == "${baseline_features_sha256}" && "$(normalized_ethtool_sha256 -k "${REPLAY_INTERFACE}")" == "${baseline_features_sha256}" ]] || return 1
  [[ "$(normalized_ethtool_sha256 -c "${CAPTURE_INTERFACE}")" == "${baseline_coalesce_sha256}" && "$(normalized_ethtool_sha256 -c "${REPLAY_INTERFACE}")" == "${baseline_coalesce_sha256}" ]] || return 1
  [[ "$(normalized_ethtool_sha256 -g "${CAPTURE_INTERFACE}")" == "${baseline_ring_sha256}" && "$(normalized_ethtool_sha256 -g "${REPLAY_INTERFACE}")" == "${baseline_ring_sha256}" ]] || return 1
  [[ "$(normalized_ethtool_sha256 -l "${CAPTURE_INTERFACE}")" == "${baseline_channels_sha256}" && "$(normalized_ethtool_sha256 -l "${REPLAY_INTERFACE}")" == "${baseline_channels_sha256}" ]] || return 1
  ! pgrep -af '[d]pdk-testpmd\.bin' | grep -F "${run_id}" >/dev/null
}

finalize() {
  local status=$? summary_status=99 verify_status=1 evidence_status=0 final_status
  trap 'trap - EXIT; exit 99' EXIT
  trap '' HUP INT TERM
  set +e
  restore_host
  snapshot_interface "${CAPTURE_INTERFACE}" capture_restored
  snapshot_interface "${REPLAY_INTERFACE}" replay_restored
  verify_host_restoration; verify_status=$?
  record_restore_step final_state_verification "${verify_status}"
  (( restore_status == 0 && verify_status == 0 )) && restoration_verified=true || restoration_verified=false
  jq -Rn '[inputs | split("\t") | {step:.[0],status:(.[1]|tonumber),ok:((.[1]|tonumber)==0)}]' < "${restore_steps}" > "${run_dir}/restoration_ledger.json"
  python3 "${run_dir}/summarize_dpdk_testpmd_capacity.py" \
    --contract "${run_dir}/frozen_contract.json" --rx-stdout "${run_dir}/rx.stdout.log" \
    --tx-stdout "${run_dir}/tx.stdout.log" --output "${run_dir}/capacity_result.json" \
    > "${run_dir}/summary.stdout.json" 2>> "${run_dir}/runner.stderr.log"
  summary_status=$?
  local capacity_qualified=false
  (( status == 0 && restore_status == 0 && verify_status == 0 \
    && summary_status == 0 )) && capacity_qualified=true
  jq -n --argjson status "${status}" --arg signal "${termination_signal:-none}" \
    --argjson restore_status "${restore_status}" --argjson summary_status "${summary_status}" \
    --argjson restoration_verified "${restoration_verified}" \
    --argjson capacity_qualified "${capacity_qualified}" \
    '{schema_version:1,original_exit_status:$status,termination_signal:$signal,restore_status:$restore_status,summary_status:$summary_status,restoration_verified:$restoration_verified,capacity_qualified:$capacity_qualified,diagnostic_only:true,r0_capture_only_qualified:false,full_pipeline_qualified:false,final_pareto_ingestion_allowed:false}' \
    > "${run_dir}/acceptance.json"
  (
    cd "${run_dir}" || exit
    find . -maxdepth 1 -type f ! -name 'evidence_sha256*' -printf '%P\0' | sort -z | xargs -0 sha256sum > evidence_sha256_complete.txt
    sha256sum -c evidence_sha256_complete.txt > evidence_sha256_complete_check.txt
  ) || evidence_status=1
  if (( restore_status != 0 || verify_status != 0 )); then final_status=15
  elif (( evidence_status != 0 )); then final_status=16
  elif (( summary_status != 0 )); then final_status=10
  else final_status="${status}"; fi
  echo "${run_dir}"
  trap - EXIT
  exit "${final_status}"
}
trap finalize EXIT

: > "${run_dir}/rx.stdout.log"; : > "${run_dir}/rx.stderr.log"
: > "${run_dir}/tx.stdout.log"; : > "${run_dir}/tx.stderr.log"
: > "${run_dir}/runner.stderr.log"
mutation_started=1
modprobe uio_pci_generic
mkdir -p "${HUGEPAGE_MOUNT}"
mountpoint -q "${HUGEPAGE_MOUNT}" || mount -t hugetlbfs nodev "${HUGEPAGE_MOUNT}"
write_sysfs_value "${HUGEPAGES}" "${HUGEPAGE_TARGET_NODE_PATH}"
[[ "$(hugepage_global_count <<< "$(hugepage_nodes_json)")" == "${HUGEPAGES}" ]] || {
  echo "requested hugepages were not reserved exactly" >&2; exit 14;
}
ip link set dev "${CAPTURE_INTERFACE}" down
ip link set dev "${REPLAY_INTERFACE}" down
for pci in "${CAPTURE_PCI}" "${REPLAY_PCI}"; do
  write_sysfs_value uio_pci_generic "/sys/bus/pci/devices/${pci}/driver_override"
  write_sysfs_value "${pci}" /sys/bus/pci/drivers/bnx2x/unbind
  write_sysfs_value "${pci}" /sys/bus/pci/drivers_probe
  [[ "$(driver_for_pci "${pci}")" == uio_pci_generic ]] || exit 14
done

rx_input="${run_dir}/rx.commands"
tx_input="${run_dir}/tx.commands"
mkfifo "${rx_input}" "${tx_input}"
# The delayed command streams ensure RX is forwarding before TX begins, keep RX
# draining after TX stops, and explicitly seal both final stats and xstats.
run_timeout=$((DURATION + 30))
setsid timeout --signal=TERM --kill-after=5s "${run_timeout}s" \
  "${run_dir}/dpdk-testpmd.bin" -l "${RX_MAIN_CPU},${RX_CPUS}" -n 4 \
  --main-lcore "${RX_MAIN_CPU}" --file-prefix "${run_id}_rx" --huge-unlink=always \
  --iova-mode=pa --socket-mem 0,256 -a "${CAPTURE_PCI}" -- \
  --rxq="${RX_QUEUE_COUNT}" --txq=1 --rxd=1024 --txd=1024 --forward-mode=rxonly \
  --nb-cores="${RX_QUEUE_COUNT}" \
  --burst=256 --mbcache=512 --total-num-mbufs=32768 --record-burst-stats \
  --no-flush-rx -i \
  < "${rx_input}" > "${run_dir}/rx.stdout.log" 2> "${run_dir}/rx.stderr.log" &
rx_pid=$!
setsid timeout --signal=TERM --kill-after=5s "${run_timeout}s" \
  "${run_dir}/dpdk-testpmd.bin" -l "${TX_MAIN_CPU},${TX_CPUS}" -n 4 \
  --main-lcore "${TX_MAIN_CPU}" --file-prefix "${run_id}_tx" --huge-unlink=always \
  --iova-mode=pa --socket-mem 0,256 -a "${REPLAY_PCI}" -- \
  --rxq=1 --txq="${TX_QUEUE_COUNT}" --rxd=1024 --txd=1024 --forward-mode=txonly \
  --nb-cores="${TX_QUEUE_COUNT}" \
  --burst=256 --mbcache=512 --total-num-mbufs=32768 \
  --record-burst-stats \
  --txpkts=64 -i \
  < "${tx_input}" > "${run_dir}/tx.stdout.log" 2> "${run_dir}/tx.stderr.log" &
tx_pid=$!
# Open FIFO writers only after both readers exist.  Each writer waits for its
# interactive prompt. TX additionally waits for RX's start marker and then two
# seconds, so its 15 measured seconds are bracketed by RX warm-up/drain.
rx_ready="${run_dir}/rx_ready.marker"
tx_ready="${run_dir}/tx_ready.marker"
rx_started="${run_dir}/rx_started.marker"
setsid bash -c '
  log="$1"; ready="$2"; peer_ready="$3"; started="$4"; duration="$5"; period="$6"
  for _ in {1..100}; do grep -q "testpmd>" "${log}" && break; sleep 0.1; done
  grep -q "testpmd>" "${log}" || exit 90
  : > "${ready}"
  for _ in {1..100}; do [[ -f "${peer_ready}" ]] && break; sleep 0.1; done
  [[ -f "${peer_ready}" ]] || exit 91
  printf "start\n"; : > "${started}"
  for ((i=0; i<duration+4; i+=period)); do
    sleep "${period}"; printf "show port stats all\n"
  done
  printf "stop\nshow port stats all\nshow port xstats all\nquit\n"
' _ "${run_dir}/rx.stdout.log" "${rx_ready}" "${tx_ready}" "${rx_started}" "${DURATION}" "${STATS_PERIOD}" \
  > "${rx_input}" & rx_command_pid=$!
setsid bash -c '
  log="$1"; ready="$2"; rx_started="$3"; duration="$4"; period="$5"
  for _ in {1..100}; do grep -q "testpmd>" "${log}" && break; sleep 0.1; done
  grep -q "testpmd>" "${log}" || exit 90
  : > "${ready}"
  for _ in {1..100}; do [[ -f "${rx_started}" ]] && break; sleep 0.1; done
  [[ -f "${rx_started}" ]] || exit 91
  sleep 2; printf "start\n"
  for ((i=0; i<duration; i+=period)); do
    sleep "${period}"; printf "show port stats all\n"
  done
  printf "stop\nshow port stats all\nshow port xstats all\nquit\n"
' _ "${run_dir}/tx.stdout.log" "${tx_ready}" "${rx_started}" "${DURATION}" "${STATS_PERIOD}" \
  > "${tx_input}" & tx_command_pid=$!
set +e
wait "${tx_command_pid}"; tx_command_status=$?; tx_command_pid=""
wait "${rx_command_pid}"; rx_command_status=$?; rx_command_pid=""
wait "${tx_pid}"; tx_status=$?; tx_pid=""
wait "${rx_pid}"; rx_status=$?; rx_pid=""
set -e
(( tx_command_status == 0 && rx_command_status == 0 \
  && tx_status == 0 && rx_status == 0 )) || exit 10
exit 0
