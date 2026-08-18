#!/usr/bin/env bash
# One authorized, fail-closed TPACKET_V3 full-pipeline diagnostic on the
# current BCM57810 host. This script never declares production qualification.
set -Eeuo pipefail
umask 077

readonly evidence_root=/home/wangwt/task/datasets/replay
readonly default_config=/home/wangwt/phase_2/code/HFT-MGBS/configs/current_hardware_2_79_tpacket_fixed64_rxusecs12_diagnostic.json
readonly default_binary=/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture/target/release/tpacket_v3_full_pipeline_fixed64
readonly capture_nic=ens8f0
readonly replay_nic=ens8f1
readonly reverse_port=50052
readonly capture_irq_first_cpu=28
readonly replay_irq_first_cpu=28
readonly pktgen_cpus=(44 45 46 47 48 49 50 52)
readonly scheduler_cpu=53
readonly generator_control_cpu=54
readonly formal_binary_sha=6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca
readonly runner_source="$(readlink -f -- "${BASH_SOURCE[0]}")"
readonly config_source="$(readlink -f -- "${HFT_CURRENT_279_CONFIG:-${default_config}}")"
readonly pipeline_binary="$(readlink -f -- "${HFT_CURRENT_279_BINARY:-${default_binary}}")"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 NEW_EVIDENCE_DIRECTORY" >&2
  exit 2
fi

mutation_authorization="${HFT_CURRENT_279_MUTATION_AUTHORIZATION:-}"
restoration_authorization="${HFT_CURRENT_279_RESTORATION_AUTHORIZATION:-}"
irqbalance_service_authorization="${HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION:-}"
change_ticket="${HFT_CURRENT_279_CHANGE_TICKET:-}"
trusted_runner_sha="${HFT_CURRENT_279_RUNNER_SHA256:-}"
trusted_config_sha="${HFT_CURRENT_279_CONFIG_SHA256:-}"
trusted_binary_sha="${HFT_CURRENT_279_BINARY_SHA256:-}"

[[ "${mutation_authorization}" == I_AUTHORIZE_CURRENT_279_TPACKET_MUTATION ]] || {
  echo "exact current-2.79 mutation authorization is required" >&2; exit 74; }
[[ "${restoration_authorization}" == I_AUTHORIZE_CURRENT_279_TPACKET_RESTORATION ]] || {
  echo "exact current-2.79 restoration authorization is required" >&2; exit 74; }
[[ "${irqbalance_service_authorization}" == I_AUTHORIZE_IRQBALANCE_STOP_START_FOR_CURRENT_279 ]] || {
  echo "exact irqbalance stop/start authorization is required" >&2; exit 74; }
[[ "${change_ticket}" =~ ^[A-Za-z0-9._:-]{4,128}$ ]] || {
  echo "a bounded change ticket is required" >&2; exit 74; }

is_sha256() { [[ "$1" =~ ^[0-9a-f]{64}$ ]]; }
sha_file() { sha256sum -- "$1" | awk '{print $1}'; }
for trusted in "${trusted_runner_sha}" "${trusted_config_sha}" "${trusted_binary_sha}"; do
  is_sha256 "${trusted}" || { echo "all three external SHA-256 trust roots are required" >&2; exit 75; }
done
[[ "${trusted_binary_sha}" == "${formal_binary_sha}" ]] || {
  echo "binary trust root differs from the fixed formal binary SHA-256" >&2; exit 75; }
[[ -f "${runner_source}" && ! -L "${runner_source}" && "$(sha_file "${runner_source}")" == "${trusted_runner_sha}" ]] || {
  echo "runner failed external hash gate" >&2; exit 75; }
[[ -f "${config_source}" && ! -L "${config_source}" && "$(sha_file "${config_source}")" == "${trusted_config_sha}" ]] || {
  echo "config failed external hash gate" >&2; exit 75; }
[[ -f "${pipeline_binary}" && ! -L "${pipeline_binary}" && -x "${pipeline_binary}" \
  && "$(sha_file "${pipeline_binary}")" == "${trusted_binary_sha}" ]] || {
  echo "pipeline binary failed external hash gate" >&2; exit 75; }

# The runner intentionally validates the fixed contract without importing shell
# values from JSON. This rejects a validly hashed but semantically different file.
python3 - "${config_source}" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
def pairs(items):
    out = {}
    for key, value in items:
        if key in out: raise ValueError("duplicate JSON key")
        out[key] = value
    return out
def nonfinite(value): raise ValueError("non-finite JSON value")
value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                   parse_constant=nonfinite)
expected = {
    ("schema_version",): 1,
    ("scope",): "current_hardware_2_79_tpacket_single_run_diagnostic",
    ("candidate_id",): "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC",
    ("interfaces", "capture"): "ens8f0",
    ("interfaces", "replay"): "ens8f1",
    ("interfaces", "required_driver"): "bnx2x",
    ("interfaces", "required_numa_node"): 1,
    ("interfaces", "hardware_queues"): 8,
    ("traffic", "packet_size_l2_bytes"): 64,
    ("traffic", "generator_queues"): 8,
    ("traffic", "profile_id"): "deterministic_multiflow_v2",
    ("traffic", "flows_per_queue"): 144,
    ("traffic", "flowlen_packets"): 36,
    ("traffic", "flow_sequence_flag"): "FLOW_SEQ",
    ("traffic", "unique_destination_addresses_per_queue"): 144,
    ("traffic", "udp_destination_port"): 53,
    ("traffic", "clone_skb"): 64,
    ("traffic", "burst"): 8,
    ("traffic", "rx_usecs"): 12,
    ("traffic", "rx_ring"): 4078,
    ("traffic", "generator_duration_seconds"): 19,
    ("pipeline", "binary_sha256"): "6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca",
    ("pipeline", "fanout_mode"): "qm",
    ("pipeline", "allow_qm_override"): True,
    ("pipeline", "require_runtime_flow_affinity_evidence"): True,
    ("pipeline", "flow_affinity_hash_algorithm"): "dual_fnv1a64_v1",
    ("pipeline", "flow_affinity_max_distinct_per_worker"): 65536,
    ("pipeline", "flow_affinity_cross_worker_collision_max"): 0,
    ("pipeline", "capture_worker_cpus"): list(range(36, 44)),
    ("pipeline", "capture_irq_cpus"): list(range(28, 36)),
    ("pipeline", "dual_port_same_queue_irq_mapping"): True,
    ("pipeline", "pktgen_cpus"): [44,45,46,47,48,49,50,52],
    ("pipeline", "scheduler_cpu"): 53,
    ("pipeline", "generator_control_cpu"): 54,
    ("pipeline", "capture_duration_seconds"): 21,
    ("pipeline", "start_delay_ms"): 13000,
    ("pipeline", "minimum_required_full_windows"): 15,
    ("pipeline", "active_timeout_seconds"): 1,
    ("pipeline", "batch_size"): 8,
    ("pipeline", "gpu_endpoint"): "listen://0.0.0.0:50052",
    ("preflight", "reserved_cpu_average_busy_fraction_max"): 0.85,
    ("preflight", "reserved_cpu_single_sample_busy_fraction_block"): 0.98,
    ("preflight", "cpu_sample_count"): 5,
    ("preflight", "include_smt_siblings"): True,
    ("preflight", "require_complete_cpu_evidence"): True,
    ("preflight", "irqbalance_active_mode"): "explicitly_authorized_stop_then_fixed_irq_then_restore_service",
    ("preflight", "irqbalance_inactive_mode"): "fixed_irq_fail_closed",
    ("preflight", "irqbalance_service_stop_start_authorization_required"): True,
    ("preflight", "irqbalance_service_stop_timeout_seconds"): 15,
    ("preflight", "irqbalance_service_start_timeout_seconds"): 15,
    ("preflight", "irqbalance_minimum_stability_wait_seconds"): 11,
    ("runtime_hard_gates", "capture_nic_rx_discards_delta_max"): 0,
    ("runtime_hard_gates", "aggregate_closed_flows_per_full_window_min"): 1000,
    ("runtime_hard_gates", "aggregate_gate_is_not_per_window_qualification"): True,
    ("qualification", "raw_diagnostic_only"): True,
    ("qualification", "runtime_identity_verified"): False,
    ("qualification", "full_pipeline_qualified"): False,
    ("qualification", "final_pareto_ingestion_allowed"): False,
}
for keys, wanted in expected.items():
    got = value
    for key in keys: got = got[key]
    if got != wanted or type(got) is not type(wanted):
        raise SystemExit("fixed contract mismatch at " + ".".join(keys))
PY

for command_name in awk basename cat chmod comm cmp cp date ethtool find flock grep id ip \
  lsmod mkdir modprobe mv paste pgrep ps python3 readlink rmmod seq setsid sha256sum sleep sort \
  ss stat sync systemctl taskset tc timeout tr wc; do
  command -v "${command_name}" >/dev/null || { echo "missing command: ${command_name}" >&2; exit 76; }
done
[[ "$(id -u)" -eq 0 ]] || { echo "root is required" >&2; exit 76; }

requested_evidence_dir="$(readlink -m -- "$1")"
case "${requested_evidence_dir}" in
  "${evidence_root}"/hft_current_279_tpacket_*) ;;
  *) echo "evidence directory must be a new hft_current_279_tpacket_* child of ${evidence_root}" >&2; exit 77 ;;
esac
[[ ! -e "${requested_evidence_dir}" && ! -L "${requested_evidence_dir}" ]] || {
  echo "evidence directory must not already exist" >&2; exit 77; }
mkdir -m 0700 -- "${requested_evidence_dir}"
readonly evidence_dir="${requested_evidence_dir}"
exec 9>"${evidence_root}/.hft_current_279_tpacket.lock"
flock -n 9 || { echo "another current-2.79 TPACKET diagnostic owns the lock" >&2; exit 73; }

mkdir -m 0700 -- "${evidence_dir}/frozen"
cp --no-preserve=mode,ownership,timestamps -- "${runner_source}" "${evidence_dir}/frozen/runner.sh"
cp --no-preserve=mode,ownership,timestamps -- "${config_source}" "${evidence_dir}/frozen/config.json"
cp --no-preserve=mode,ownership,timestamps -- "${pipeline_binary}" "${evidence_dir}/frozen/tpacket_v3_full_pipeline"
chmod 0400 "${evidence_dir}/frozen/runner.sh" "${evidence_dir}/frozen/config.json"
chmod 0500 "${evidence_dir}/frozen/tpacket_v3_full_pipeline"
readonly frozen_runner="${evidence_dir}/frozen/runner.sh"
readonly frozen_config="${evidence_dir}/frozen/config.json"
readonly frozen_binary="${evidence_dir}/frozen/tpacket_v3_full_pipeline"

verify_frozen() {
  [[ "$(sha_file "${frozen_runner}")" == "${trusted_runner_sha}" \
    && "$(sha_file "${frozen_config}")" == "${trusted_config_sha}" \
    && "$(sha_file "${frozen_binary}")" == "${trusted_binary_sha}" ]]
}
verify_frozen || { echo "frozen artifact copy failed hash gate" >&2; exit 75; }
printf '%s  %s\n%s  %s\n%s  %s\n' \
  "${trusted_runner_sha}" frozen/runner.sh \
  "${trusted_config_sha}" frozen/config.json \
  "${trusted_binary_sha}" frozen/tpacket_v3_full_pipeline \
  >"${evidence_dir}/trusted_artifacts.sha256"

capture_pid=
generator_start_pid=
timer_pid=
monitor_pid=
resource_monitor_pid=
capture_pgid=
capture_identity_verified=false
cleanup_started=false
mutations_started=false
irq_affinity_managed=false
irqbalance_initial_active=false
irqbalance_stop_attempted=false
irqbalance_stopped=false
irq_affinity_restoration_daemon_managed=false
irqbalance_pid=
irqbalance_start_ticks=
irqbalance_cmdline=
irqbalance_exe=
original_rx_ring=
original_rx_usecs=
restoration_failed=false
readonly ledger="${evidence_dir}/restoration_ledger.tsv"
printf 'domain\taction\tattempted\tstatus\texpected\tobserved\n' >"${ledger}"
readonly events="${evidence_dir}/execution_events.tsv"
printf 'utc\tevent\n' >"${events}"
event() { printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)" "$1" >>"${events}"; }

ledger_row() {
  local domain="$1" action="$2" attempted="$3" status="$4" expected="$5" observed="$6"
  expected="${expected//$'\t'/ }"; observed="${observed//$'\t'/ }"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$domain" "$action" "$attempted" "$status" "$expected" "$observed" >>"${ledger}"
}
set_restoration_failure() { restoration_failed=true; }

find_competing_pipeline() {
  local proc exe command_line
  for proc in /proc/[0-9]*; do
    [[ "${proc##*/}" != "$$" ]] || continue
    exe="$(readlink -f -- "${proc}/exe" 2>/dev/null || true)"
    [[ "$(basename -- "${exe}")" == tpacket_v3_full_pipeline* ]] || continue
    command_line="$(tr '\0' ' ' <"${proc}/cmdline" 2>/dev/null || true)"
    [[ -n "${command_line}" ]] || continue
    printf '%s\t%s\t%s\n' "${proc##*/}" "${exe}" "${command_line}"
  done
}

bounded_stop_pid() {
  local label="$1" pid="$2" deadline
  [[ -n "${pid}" ]] || { ledger_row "child:${label}" stop false absent none none; return 0; }
  if ! kill -0 "${pid}" 2>/dev/null; then
    wait "${pid}" 2>/dev/null || true
    ledger_row "child:${label}" stop false already_exited exited exited
    return 0
  fi
  kill -TERM "${pid}" 2>/dev/null || true
  deadline=$((SECONDS + 5))
  while kill -0 "${pid}" 2>/dev/null && ((SECONDS < deadline)); do sleep 0.1; done
  if kill -0 "${pid}" 2>/dev/null; then kill -KILL "${pid}" 2>/dev/null || true; fi
  deadline=$((SECONDS + 2))
  while kill -0 "${pid}" 2>/dev/null && ((SECONDS < deadline)); do sleep 0.1; done
  if kill -0 "${pid}" 2>/dev/null; then
    ledger_row "child:${label}" stop true failed exited "pid=${pid}_still_alive"
    set_restoration_failure
  else
    ledger_row "child:${label}" stop true stopped exited exited
  fi
  wait "${pid}" 2>/dev/null || true
}

bounded_stop_capture_group() {
  local deadline
  [[ -n "${capture_pid}" ]] || { ledger_row child:capture stop false absent none none; return 0; }
  if ! kill -0 "${capture_pid}" 2>/dev/null; then
    wait "${capture_pid}" 2>/dev/null || true
    ledger_row child:capture stop false already_exited exited exited
    return 0
  fi
  if [[ "${capture_identity_verified}" != true || -z "${capture_pgid}" ]]; then
    ledger_row child:capture stop false identity_unverified safe_refusal "pid=${capture_pid}"
    set_restoration_failure
    return 0
  fi
  kill -TERM -- "-${capture_pgid}" 2>/dev/null || true
  deadline=$((SECONDS + 5))
  while kill -0 "${capture_pid}" 2>/dev/null && ((SECONDS < deadline)); do sleep 0.1; done
  if kill -0 "${capture_pid}" 2>/dev/null; then kill -KILL -- "-${capture_pgid}" 2>/dev/null || true; fi
  deadline=$((SECONDS + 2))
  while kill -0 "${capture_pid}" 2>/dev/null && ((SECONDS < deadline)); do sleep 0.1; done
  if kill -0 "${capture_pid}" 2>/dev/null; then
    ledger_row child:capture stop true failed exited "pgid=${capture_pgid}_still_alive"
    set_restoration_failure
  else
    ledger_row child:capture stop true stopped exited exited
  fi
  wait "${capture_pid}" 2>/dev/null || true
}

irq_rows() {
  local nic="$1"
  awk -v nic="$nic" '$NF ~ ("^" nic "-fp-[0-9]+$") {
    irq=$1; sub(":", "", irq); print irq "\t" $NF
  }' /proc/interrupts | sort -V
}
record_irq_affinity() {
  local output="$1" nic irq label
  : >"${output}"
  for nic in "${capture_nic}" "${replay_nic}"; do
    while IFS=$'\t' read -r irq label; do
      [[ -n "${irq}" ]] || continue
      printf '%s\t%s\t%s\n' "${irq}" "${label}" "$(<"/proc/irq/${irq}/smp_affinity_list")" >>"${output}"
    done < <(irq_rows "${nic}")
  done
}
verify_target_irq_affinity() {
  local index irq _label actual expected
  for index in "${!capture_irqs[@]}"; do
    IFS=$'\t' read -r irq _label <<<"${capture_irqs[$index]}"
    expected="$((capture_irq_first_cpu + index))"
    actual="$(<"/proc/irq/${irq}/smp_affinity_list")"
    [[ "${actual}" == "${expected}" ]] || {
      printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)" "${irq}" "${expected}" "${actual}"
      return 1
    }
  done
  for index in "${!replay_irqs[@]}"; do
    IFS=$'\t' read -r irq _label <<<"${replay_irqs[$index]}"
    expected="$((replay_irq_first_cpu + index))"
    actual="$(<"/proc/irq/${irq}/smp_affinity_list")"
    [[ "${actual}" == "${expected}" ]] || {
      printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)" "${irq}" "${expected}" "${actual}"
      return 1
    }
  done
}

monitor_target_irq_affinity() {
  local drift_file="${evidence_dir}/irq_affinity_drift.tsv"
  local topology="${evidence_dir}/irq_affinity_fixed_monitor.tsv" sequence=0
  printf 'utc\tsequence\tirq\tlabel\taffinity\n' >"${topology}"
  while true; do
    if [[ "${irqbalance_stopped}" == true && $((sequence % 10)) -eq 0 ]] \
      && ! verify_irqbalance_inactive; then
      printf '%s\tirqbalance_unexpectedly_active\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)" \
        >"${evidence_dir}/irqbalance_runtime_failure.tsv"
      sync "${evidence_dir}/irqbalance_runtime_failure.tsv"
      [[ -w /proc/net/pktgen/pgctrl ]] && echo stop >/proc/net/pktgen/pgctrl 2>/dev/null || true
      if [[ "${capture_identity_verified}" == true && -n "${capture_pgid}" ]]; then
        kill -TERM -- "-${capture_pgid}" 2>/dev/null || true
      fi
      return 43
    fi
    if ! verify_target_irq_affinity >"${drift_file}.tmp"; then
      mv "${drift_file}.tmp" "${drift_file}"
      sync "${drift_file}"
      [[ -w /proc/net/pktgen/pgctrl ]] && echo stop >/proc/net/pktgen/pgctrl 2>/dev/null || true
      if [[ "${capture_identity_verified}" == true && -n "${capture_pgid}" ]]; then
        kill -TERM -- "-${capture_pgid}" 2>/dev/null || true
      fi
      return 42
    fi
    rm -f "${drift_file}.tmp"
    sequence=$((sequence + 1))
    while IFS=$'\t' read -r irq label affinity; do
      printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)" \
        "${sequence}" "${irq}" "${label}" "${affinity}" >>"${topology}"
    done < <(record_irq_affinity /dev/stdout)
    sleep 0.1
  done
}

verify_irqbalance_identity() {
  local active current_pid current_ticks
  active="$(systemctl is-active irqbalance 2>/dev/null || true)"
  current_pid="$(systemctl show irqbalance -p MainPID --value 2>/dev/null || true)"
  [[ "${active}" == active && "${current_pid}" == "${irqbalance_pid}" \
    && -r "/proc/${current_pid}/stat" ]] || return 1
  current_ticks="$(awk '{print $22}' "/proc/${current_pid}/stat")"
  [[ "${current_ticks}" == "${irqbalance_start_ticks}" ]]
}

verify_irqbalance_inactive() {
  local active current_pid
  active="$(systemctl is-active irqbalance 2>/dev/null || true)"
  current_pid="$(systemctl show irqbalance -p MainPID --value 2>/dev/null || true)"
  [[ "${active}" == inactive && "${current_pid}" == 0 \
    && ( -z "${irqbalance_pid}" || ! -e "/proc/${irqbalance_pid}" ) ]]
}
current_rx_ring() {
  ethtool -g "${capture_nic}" | awk '/Current hardware settings:/{active=1;next} active && /^RX:/{print $2;exit}'
}
current_rx_usecs() { ethtool -c "${capture_nic}" | awk '/^rx-usecs:/{print $2;exit}'; }

snapshot_state() {
  local phase="$1" nic rc=0
  for nic in "${capture_nic}" "${replay_nic}"; do
    ip -details -oneline link show dev "${nic}" >"${evidence_dir}/${phase}_${nic}_interface.txt" || rc=1
    ip -o addr show dev "${nic}" >"${evidence_dir}/${phase}_${nic}_addresses.txt" || rc=1
    ethtool -i "${nic}" >"${evidence_dir}/${phase}_${nic}_driver.txt" || rc=1
    ethtool "${nic}" >"${evidence_dir}/${phase}_${nic}_link.txt" || rc=1
    ethtool -g "${nic}" >"${evidence_dir}/${phase}_${nic}_ring.txt" || rc=1
    ethtool -c "${nic}" >"${evidence_dir}/${phase}_${nic}_coalesce.txt" || rc=1
    ethtool -k "${nic}" >"${evidence_dir}/${phase}_${nic}_features.txt" || rc=1
    ethtool -l "${nic}" >"${evidence_dir}/${phase}_${nic}_channels.txt" || rc=1
    ethtool -S "${nic}" >"${evidence_dir}/${phase}_${nic}_statistics.txt" || rc=1
    ip -details link show dev "${nic}" >"${evidence_dir}/${phase}_${nic}_xdp.txt" || rc=1
    tc qdisc show dev "${nic}" >"${evidence_dir}/${phase}_${nic}_qdisc.txt" || rc=1
    tc -s qdisc show dev "${nic}" >"${evidence_dir}/${phase}_${nic}_qdisc_statistics.txt" || rc=1
  done
  record_irq_affinity "${evidence_dir}/${phase}_irq_affinity.tsv" || rc=1
  lsmod | awk '$1 == "pktgen" {print}' >"${evidence_dir}/${phase}_pktgen_module.txt" || rc=1
  if [[ -r /proc/net/pktgen/pgctrl ]]; then
    cp -- /proc/net/pktgen/pgctrl "${evidence_dir}/${phase}_pktgen_pgctrl.txt" || rc=1
  else
    printf 'not_present\n' >"${evidence_dir}/${phase}_pktgen_pgctrl.txt" || rc=1
  fi
  grep '^cpu ' /proc/stat >"${evidence_dir}/${phase}_proc_stat.txt" || rc=1
  grep -E '^(MemTotal|MemAvailable):' /proc/meminfo >"${evidence_dir}/${phase}_meminfo.txt" || rc=1
  cp -- /proc/loadavg "${evidence_dir}/${phase}_loadavg.txt" || rc=1
  return "${rc}"
}

compare_unchanged() {
  local domain="$1" before="$2" after="$3"
  if cmp -s -- "${before}" "${after}"; then
    ledger_row "${domain}" verify true restored "$(sha_file "${before}")" "$(sha_file "${after}")"
  else
    ledger_row "${domain}" verify true mismatch "$(sha_file "${before}")" "$(sha_file "${after}")"
    set_restoration_failure
  fi
}

seal_evidence() {
  local final_rc="$1"
  printf 'runner_exit_status=%s\nrestoration_failed=%s\nmutations_started=%s\n' \
    "${final_rc}" "${restoration_failed}" "${mutations_started}" >"${evidence_dir}/runner_exit_status.env"
  python3 - "${evidence_dir}" "${change_ticket}" "${final_rc}" \
    "${mutations_started}" "${restoration_failed}" <<'PY'
import json, os, pathlib, sys, tempfile
root = pathlib.Path(sys.argv[1])
value = {
    "schema_version": 1,
    "scope": "current_hardware_2_79_tpacket_single_run_raw_receipt",
    "candidate_id": "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC",
    "change_ticket": sys.argv[2],
    "runner_exit_status": int(sys.argv[3]),
    "mutations_performed": sys.argv[4] == "true",
    "restoration_verified": sys.argv[4] == "true" and sys.argv[5] == "false",
    "restoration_not_required": sys.argv[4] == "false",
    "raw_diagnostic_only": True,
    "runtime_identity_verified": False,
    "full_pipeline_qualified": False,
    "final_pareto_ingestion_allowed": False,
}
target = root / "diagnostic_receipt.json"
handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
    dir=str(root), prefix="diagnostic_receipt.", suffix=".tmp", delete=False)
with handle:
    json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
pathlib.Path(handle.name).replace(target)
PY
  (
    cd "${evidence_dir}"
    find . -type f ! -name 'evidence.sha256' ! -name 'evidence.sha256.check' \
      ! -name '*.tmp' -printf '%P\n' | LC_ALL=C sort | while IFS= read -r path; do
        sha256sum -- "${path}"
      done >evidence.sha256.tmp
    mv evidence.sha256.tmp evidence.sha256
    sha256sum -c evidence.sha256 >evidence.sha256.check.tmp
    mv evidence.sha256.check.tmp evidence.sha256.check
  )
  sync "${evidence_dir}"
}

cleanup() {
  local observed_rc="$?" final_rc restore_value irq label affinity nic stop_rc
  local restored_irqbalance_pid restored_irqbalance_ticks restored_irqbalance_exe
  if [[ "${cleanup_started}" == true ]]; then return; fi
  cleanup_started=true
  trap - EXIT
  trap '' HUP INT TERM
  set +e

  # Stop the generator and every child before touching shared host state.
  if [[ -w /proc/net/pktgen/pgctrl ]]; then
    echo stop >/proc/net/pktgen/pgctrl
    stop_rc=$?
    ledger_row pktgen stop true "$([[ ${stop_rc} -eq 0 ]] && echo stopped || echo failed)" stopped "rc=${stop_rc}"
  else
    ledger_row pktgen stop false not_present absent absent
  fi
  bounded_stop_pid irq_affinity_monitor "${monitor_pid}"
  monitor_pid=
  bounded_stop_pid generator_start "${generator_start_pid}"
  bounded_stop_pid timer "${timer_pid}"
  bounded_stop_capture_group
  bounded_stop_pid resource_monitor "${resource_monitor_pid}"

  if [[ "${irq_affinity_managed}" == true ]]; then
    if [[ -s "${evidence_dir}/before_irq_affinity.tsv" ]]; then
      while IFS=$'\t' read -r irq label affinity; do
        if printf '%s\n' "${affinity}" >"/proc/irq/${irq}/smp_affinity_list"; then
          restore_value="$(<"/proc/irq/${irq}/smp_affinity_list")"
          if [[ "${restore_value}" == "${affinity}" ]]; then
            ledger_row "irq:${irq}:${label}" restore true restored "${affinity}" "${restore_value}"
          else
            ledger_row "irq:${irq}:${label}" restore true mismatch "${affinity}" "${restore_value}"
            set_restoration_failure
          fi
        else
          ledger_row "irq:${irq}:${label}" restore true failed "${affinity}" write_failed
          set_restoration_failure
        fi
      done <"${evidence_dir}/before_irq_affinity.tsv"
    else
      ledger_row irq restore true missing_snapshot required missing
      set_restoration_failure
    fi
  else
    ledger_row irq_affinity restore false externally_managed observe_only observe_only
  fi

  if [[ "${mutations_started}" == true ]]; then
    if ethtool -G "${capture_nic}" rx "${original_rx_ring}"; then
      restore_value="$(current_rx_ring)"
      [[ "${restore_value}" == "${original_rx_ring}" ]] \
        && ledger_row ring restore true restored "${original_rx_ring}" "${restore_value}" \
        || { ledger_row ring restore true mismatch "${original_rx_ring}" "${restore_value}"; set_restoration_failure; }
    else
      ledger_row ring restore true failed "${original_rx_ring}" write_failed; set_restoration_failure
    fi
    if ethtool -C "${capture_nic}" rx-usecs "${original_rx_usecs}"; then
      restore_value="$(current_rx_usecs)"
      [[ "${restore_value}" == "${original_rx_usecs}" ]] \
        && ledger_row coalesce restore true restored "${original_rx_usecs}" "${restore_value}" \
        || { ledger_row coalesce restore true mismatch "${original_rx_usecs}" "${restore_value}"; set_restoration_failure; }
    else
      ledger_row coalesce restore true failed "${original_rx_usecs}" write_failed; set_restoration_failure
    fi
    if lsmod | awk '{print $1}' | grep -qx pktgen; then
      if rmmod pktgen; then ledger_row pktgen unload true restored absent absent
      else ledger_row pktgen unload true failed absent loaded; set_restoration_failure; fi
    else
      ledger_row pktgen unload false already_absent absent absent
    fi
  fi

  # IRQ affinity is restored while irqbalance is still stopped. Only then is
  # the originally active unit started again and its new process identity
  # frozen. A failed/partial stop that left the original identity active does
  # not trigger a redundant start.
  if [[ "${irqbalance_initial_active}" == true && "${irqbalance_stop_attempted}" == true ]]; then
    if verify_irqbalance_identity; then
      ledger_row irqbalance_service restore false original_identity_still_active \
        "pid=${irqbalance_pid},ticks=${irqbalance_start_ticks}" stable
      irq_affinity_restoration_daemon_managed=true
    else
      systemctl cat irqbalance --no-pager >"${evidence_dir}/irqbalance_systemd_config_pre_restore.txt" 2>&1 || true
      if ! cmp -s "${evidence_dir}/irqbalance_systemd_config.txt" \
        "${evidence_dir}/irqbalance_systemd_config_pre_restore.txt"; then
        ledger_row irqbalance_unit_config verify true drifted \
          "$(sha_file "${evidence_dir}/irqbalance_systemd_config.txt")" \
          "$(sha_file "${evidence_dir}/irqbalance_systemd_config_pre_restore.txt")"
        set_restoration_failure
      else
        ledger_row irqbalance_unit_config verify true unchanged \
          "$(sha_file "${evidence_dir}/irqbalance_systemd_config.txt")" \
          "$(sha_file "${evidence_dir}/irqbalance_systemd_config_pre_restore.txt")"
      fi
    if timeout 15 systemctl start irqbalance; then
      systemctl show irqbalance --no-pager >"${evidence_dir}/irqbalance_systemd_show_restored.txt" 2>&1 || true
      restored_irqbalance_pid="$(systemctl show irqbalance -p MainPID --value 2>/dev/null || true)"
      if [[ "$(systemctl is-active irqbalance 2>/dev/null || true)" == active \
        && "${restored_irqbalance_pid}" =~ ^[1-9][0-9]*$ \
        && -r "/proc/${restored_irqbalance_pid}/stat" ]]; then
        restored_irqbalance_ticks="$(awk '{print $22}' "/proc/${restored_irqbalance_pid}/stat")"
        restored_irqbalance_exe="$(readlink -f -- "/proc/${restored_irqbalance_pid}/exe" 2>/dev/null || true)"
        printf 'pid=%s\nstart_ticks=%s\nexe=%s\ncmdline=%s\n' \
          "${restored_irqbalance_pid}" "${restored_irqbalance_ticks}" "${restored_irqbalance_exe}" \
          "$(tr '\0' ' ' <"/proc/${restored_irqbalance_pid}/cmdline" 2>/dev/null || true)" \
          >"${evidence_dir}/irqbalance_process_identity_restored.env"
        if [[ -n "${restored_irqbalance_ticks}" && "${restored_irqbalance_exe}" == "${irqbalance_exe}" \
          && ( "${restored_irqbalance_pid}:${restored_irqbalance_ticks}" \
            != "${irqbalance_pid}:${irqbalance_start_ticks}" ) ]]; then
          ledger_row irqbalance_service restore true restored_active_new_identity \
            "exe=${irqbalance_exe}" \
            "pid=${restored_irqbalance_pid},ticks=${restored_irqbalance_ticks},exe=${restored_irqbalance_exe}"
          irq_affinity_restoration_daemon_managed=true
        else
          ledger_row irqbalance_service restore true identity_mismatch \
            "new identity,exe=${irqbalance_exe}" \
            "pid=${restored_irqbalance_pid},ticks=${restored_irqbalance_ticks},exe=${restored_irqbalance_exe}"
          set_restoration_failure
        fi
      else
        ledger_row irqbalance_service restore true not_active active \
          "state=$(systemctl is-active irqbalance 2>/dev/null || true),pid=${restored_irqbalance_pid:-}"
        set_restoration_failure
      fi
    else
      ledger_row irqbalance_service restore true start_failed active \
        "state=$(systemctl is-active irqbalance 2>/dev/null || true)"
      set_restoration_failure
    fi
    fi
  elif [[ "${irqbalance_initial_active}" == false ]]; then
    if verify_irqbalance_inactive; then
      ledger_row irqbalance_service restore false remained_inactive inactive inactive
    else
      ledger_row irqbalance_service restore false unexpected_state inactive \
        "state=$(systemctl is-active irqbalance 2>/dev/null || true)"
      set_restoration_failure
    fi
  fi
  systemctl is-enabled irqbalance >"${evidence_dir}/irqbalance_enabled_state_restored.txt" 2>&1 || true
  if cmp -s "${evidence_dir}/irqbalance_enabled_state.txt" \
    "${evidence_dir}/irqbalance_enabled_state_restored.txt"; then
    ledger_row irqbalance_enablement verify true unchanged \
      "$(sha_file "${evidence_dir}/irqbalance_enabled_state.txt")" \
      "$(sha_file "${evidence_dir}/irqbalance_enabled_state_restored.txt")"
  else
    ledger_row irqbalance_enablement verify true drifted \
      "$(sha_file "${evidence_dir}/irqbalance_enabled_state.txt")" \
      "$(sha_file "${evidence_dir}/irqbalance_enabled_state_restored.txt")"
    set_restoration_failure
  fi

  if snapshot_state after; then
    if [[ -f "${evidence_dir}/before_irq_affinity.tsv" ]]; then
      if [[ "${irq_affinity_managed}" == true \
        && "${irq_affinity_restoration_daemon_managed}" == false ]]; then
        compare_unchanged irq_affinity "${evidence_dir}/before_irq_affinity.tsv" "${evidence_dir}/after_irq_affinity.tsv"
      else
        ledger_row irq_affinity verify false externally_managed daemon_managed_after_service_restore \
          "before=$(sha_file "${evidence_dir}/before_irq_affinity.tsv"),after=$(sha_file "${evidence_dir}/after_irq_affinity.tsv")"
      fi
      for nic in "${capture_nic}" "${replay_nic}"; do
        for domain in interface addresses driver link ring coalesce features channels xdp qdisc; do
          compare_unchanged "${nic}:${domain}" \
            "${evidence_dir}/before_${nic}_${domain}.txt" "${evidence_dir}/after_${nic}_${domain}.txt"
        done
      done
      compare_unchanged pktgen_module "${evidence_dir}/before_pktgen_module.txt" "${evidence_dir}/after_pktgen_module.txt"
    else
      ledger_row host_state verify false not_needed no_mutation no_before_snapshot
    fi
  elif [[ "${mutations_started}" == true ]]; then
    ledger_row host_state snapshot_after true failed required unavailable
    set_restoration_failure
  fi

  final_rc="${observed_rc}"
  if [[ "${mutations_started}" == true && "${restoration_failed}" == true ]]; then final_rc=97; fi
  seal_evidence "${final_rc}" || final_rc=98
  exit "${final_rc}"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

# Exact process, port, NIC, driver, link, IP, queue, NUMA, and CPU gates occur
# before the first mutation. An active irqbalance unit may only be stopped after
# all gates pass and the dedicated stop/start authorization has been validated.
find_competing_pipeline >"${evidence_dir}/competing_pipeline_preflight.tsv"
[[ ! -s "${evidence_dir}/competing_pipeline_preflight.tsv" ]] || {
  echo "another tpacket_v3_full_pipeline executable is running" >&2; exit 78; }
if ss -H -ltn "sport = :${reverse_port}" | grep -q .; then
  echo "reverse GPU listener port ${reverse_port} is already owned" >&2; exit 78
fi
lsmod | awk '{print $1}' | grep -qx pktgen && {
  echo "pktgen is already loaded; refusing shared generator state" >&2; exit 78; }
systemctl is-active irqbalance >"${evidence_dir}/irqbalance_state.txt" 2>&1 || true
systemctl is-enabled irqbalance >"${evidence_dir}/irqbalance_enabled_state.txt" 2>&1 || true
systemctl show irqbalance --no-pager >"${evidence_dir}/irqbalance_systemd_show.txt" 2>&1 || true
systemctl cat irqbalance --no-pager >"${evidence_dir}/irqbalance_systemd_config.txt" 2>&1 || true
irqbalance_pid="$(systemctl show irqbalance -p MainPID --value 2>/dev/null || true)"
if [[ "${irqbalance_pid}" =~ ^[1-9][0-9]*$ && -r "/proc/${irqbalance_pid}/stat" ]]; then
  irqbalance_start_ticks="$(awk '{print $22}' "/proc/${irqbalance_pid}/stat")"
  irqbalance_cmdline="$(tr '\0' ' ' <"/proc/${irqbalance_pid}/cmdline" 2>/dev/null || true)"
  irqbalance_exe="$(readlink -f -- "/proc/${irqbalance_pid}/exe" 2>/dev/null || true)"
else
  irqbalance_start_ticks=; irqbalance_cmdline=; irqbalance_exe=
fi
printf 'pid=%s\nstart_ticks=%s\nexe=%s\ncmdline=%s\n' "${irqbalance_pid}" "${irqbalance_start_ticks}" \
  "${irqbalance_exe}" "${irqbalance_cmdline}" >"${evidence_dir}/irqbalance_process_identity.env"
irqbalance_initial_state="$(<"${evidence_dir}/irqbalance_state.txt")"
if [[ "${irqbalance_initial_state}" == active ]]; then
  [[ -n "${irqbalance_pid}" && -n "${irqbalance_start_ticks}" && -n "${irqbalance_exe}" ]] || {
    echo "active irqbalance identity cannot be frozen" >&2; exit 78; }
  irqbalance_initial_active=true
  verify_irqbalance_identity || { echo "irqbalance identity changed during preflight" >&2; exit 78; }
elif [[ "${irqbalance_initial_state}" == inactive && "${irqbalance_pid}" == 0 ]]; then
  irqbalance_initial_active=false
else
  echo "irqbalance must be exactly active with a frozen identity or inactive with MainPID=0" >&2
  exit 78
fi
ps -eLo pid,tid,psr,pcpu,comm,args --sort=psr >"${evidence_dir}/process_threads_preflight.txt"
ss -H -ltnp >"${evidence_dir}/listening_tcp_preflight.txt"

for nic in "${capture_nic}" "${replay_nic}"; do
  [[ -d "/sys/class/net/${nic}/device" ]] || { echo "${nic} is not a PCI NIC" >&2; exit 79; }
  [[ "$(basename "$(readlink -f "/sys/class/net/${nic}/device/driver")")" == bnx2x ]] || {
    echo "${nic} is not bound to bnx2x" >&2; exit 79; }
  [[ "$(<"/sys/class/net/${nic}/device/numa_node")" == 1 ]] || { echo "${nic} NUMA mismatch" >&2; exit 79; }
  [[ "$(<"/sys/class/net/${nic}/operstate")" == up && "$(<"/sys/class/net/${nic}/carrier")" == 1 ]] || {
    echo "${nic} link is not up with carrier" >&2; exit 79; }
  [[ -z "$(ip -o addr show dev "${nic}")" ]] || { echo "${nic} has an IP address" >&2; exit 79; }
  ethtool -l "${nic}" | awk '/Current hardware settings:/{seen=1;next} seen && /^Combined:/{ok=($2==8)} END{exit !ok}' || {
    echo "${nic} does not expose exactly eight active combined channels" >&2; exit 79; }
done
[[ "$(readlink -f "/sys/class/net/${capture_nic}/device")" != "$(readlink -f "/sys/class/net/${replay_nic}/device")" ]] || {
  echo "capture and replay interfaces resolve to one PF" >&2; exit 79; }
mapfile -t capture_irqs < <(irq_rows "${capture_nic}")
mapfile -t replay_irqs < <(irq_rows "${replay_nic}")
[[ ${#capture_irqs[@]} -eq 8 && ${#replay_irqs[@]} -eq 8 ]] || {
  echo "expected exactly eight queue IRQs per interface" >&2; exit 79; }
printf '%s\n' "${capture_irqs[@]}" "${replay_irqs[@]}" | awk '{print $1}' | sort -n -u \
  >"${evidence_dir}/irqbalance_target_irqs.txt"
[[ "$(wc -l <"${evidence_dir}/irqbalance_target_irqs.txt")" -eq 16 ]] || {
  echo "irqbalance target IRQ set is not exactly 16 unique IRQs" >&2; exit 79; }

python3 - "${evidence_dir}/cpu_preflight.json" <<'PY'
import json, os, pathlib, time
primary = list(range(28, 55))
reserved = set(primary)
for cpu in primary:
    siblings = pathlib.Path(f"/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list")
    if not siblings.is_file(): raise SystemExit(f"SMT sibling topology missing for CPU {cpu}")
    for part in siblings.read_text().strip().split(","):
        if "-" in part:
            a, b = map(int, part.split("-", 1)); reserved.update(range(a, b + 1))
        else: reserved.add(int(part))
reserved = sorted(reserved)
def read():
    rows = {}
    for line in pathlib.Path("/proc/stat").read_text().splitlines():
        fields = line.split()
        if fields and fields[0].startswith("cpu") and fields[0][3:].isdigit():
            nums = [int(x) for x in fields[1:]]
            rows[int(fields[0][3:])] = (sum(nums), nums[3] + (nums[4] if len(nums) > 4 else 0))
    return rows
for cpu in reserved:
    online = pathlib.Path(f"/sys/devices/system/cpu/cpu{cpu}/online")
    if not pathlib.Path(f"/sys/devices/system/cpu/cpu{cpu}").is_dir() or (online.exists() and online.read_text().strip() != "1"):
        raise SystemExit(f"reserved CPU {cpu} is absent or offline")
busy_samples = {str(cpu): [] for cpu in reserved}
a = read()
for _ in range(5):
    time.sleep(1); b = read()
    for cpu in reserved:
        total = b[cpu][0] - a[cpu][0]; idle = b[cpu][1] - a[cpu][1]
        busy_samples[str(cpu)].append(1.0 - idle / total if total > 0 else 1.0)
    a = b
average_busy = {cpu: sum(samples) / len(samples) for cpu, samples in busy_samples.items()}
max_busy = {cpu: max(samples) for cpu, samples in busy_samples.items()}
evidence_complete = (set(map(int, busy_samples)) == set(reserved)
                     and all(len(samples) == 5 for samples in busy_samples.values()))
value = {"schema_version": 1, "primary_reserved_cpus": primary,
         "reserved_cpus_including_smt_siblings": reserved, "sample_count": 5,
         "sample_seconds": 1, "average_busy_fraction_max": 0.85,
         "single_sample_busy_fraction_block": 0.98,
         "busy_fraction_samples": busy_samples,
         "per_cpu_average_busy_fraction": average_busy,
         "per_cpu_max_busy_fraction": max_busy,
         "evidence_complete": evidence_complete,
         "passed": evidence_complete and all(v <= 0.85 for v in average_busy.values())
                   and all(v < 0.98 for v in max_busy.values())}
pathlib.Path(os.sys.argv[1]).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
if not value["passed"]: raise SystemExit("reserved CPU idle preflight failed")
PY

# Close the preflight-to-mutation race as far as the host interface permits.
find_competing_pipeline >"${evidence_dir}/competing_pipeline_pre_mutation.tsv"
[[ ! -s "${evidence_dir}/competing_pipeline_pre_mutation.tsv" ]] || {
  echo "a competing full-pipeline process appeared during preflight" >&2; exit 78; }
if ss -H -ltn "sport = :${reverse_port}" | grep -q .; then
  echo "reverse GPU port became occupied during preflight" >&2; exit 78
fi
lsmod | awk '{print $1}' | grep -qx pktgen && {
  echo "pktgen appeared during preflight" >&2; exit 78; }
verify_frozen || { echo "frozen artifacts drifted during preflight" >&2; exit 75; }

snapshot_state before
original_rx_ring="$(current_rx_ring)"
original_rx_usecs="$(current_rx_usecs)"
[[ "${original_rx_ring}" =~ ^[0-9]+$ && "${original_rx_usecs}" =~ ^[0-9]+$ ]] || {
  echo "cannot read restorable ring/coalesce state" >&2; exit 79; }

# Repeat every volatile ownership gate immediately before the first mutation.
find_competing_pipeline >"${evidence_dir}/competing_pipeline_final_pre_mutation.tsv"
[[ ! -s "${evidence_dir}/competing_pipeline_final_pre_mutation.tsv" ]] || {
  echo "a competing full-pipeline process appeared before mutation" >&2; exit 78; }
if ss -H -ltn "sport = :${reverse_port}" | grep -q .; then
  echo "reverse GPU port became occupied before mutation" >&2; exit 78
fi
lsmod | awk '{print $1}' | grep -qx pktgen && {
  echo "pktgen appeared before mutation" >&2; exit 78; }
verify_frozen || { echo "frozen artifacts drifted before mutation" >&2; exit 75; }
mutations_started=true
event mutations_started
if [[ "${irqbalance_initial_active}" == true ]]; then
  verify_irqbalance_identity || { echo "irqbalance identity changed before authorized stop" >&2; exit 78; }
  irqbalance_stop_attempted=true
  event irqbalance_stop_attempted
  timeout 15 systemctl stop irqbalance || {
    echo "authorized irqbalance stop command failed or timed out" >&2; exit 83; }
  verify_irqbalance_inactive || {
    echo "irqbalance did not reach exact inactive/MainPID=0 state" >&2; exit 83; }
  irqbalance_stopped=true
  systemctl show irqbalance --no-pager >"${evidence_dir}/irqbalance_systemd_show_stopped.txt" 2>&1 || true
  event irqbalance_stopped
else
  verify_irqbalance_inactive || { echo "irqbalance state changed before mutation" >&2; exit 78; }
fi
ethtool -G "${capture_nic}" rx 4078
ethtool -C "${capture_nic}" rx-usecs 12
modprobe pktgen

for index in "${!capture_irqs[@]}"; do
  IFS=$'\t' read -r irq _label <<<"${capture_irqs[$index]}"
  printf '%s\n' "$((capture_irq_first_cpu + index))" >"/proc/irq/${irq}/smp_affinity_list"
done
for index in "${!replay_irqs[@]}"; do
  IFS=$'\t' read -r irq _label <<<"${replay_irqs[$index]}"
  printf '%s\n' "$((replay_irq_first_cpu + index))" >"/proc/irq/${irq}/smp_affinity_list"
done
irq_affinity_managed=true
verify_target_irq_affinity >"${evidence_dir}/irq_affinity_after_write.tsv" || {
  echo "target IRQ affinity write did not hold" >&2; exit 82; }
snapshot_state active

pgset() {
  local file="$1"; shift
  printf '%s\n' "$*" >"${file}"
  grep -q 'Result: OK:' "${file}"
}
for index in $(seq 0 7); do
  cpu="${pktgen_cpus[$index]}"; device="${replay_nic}@${index}"
  thread="/proc/net/pktgen/kpktgend_${cpu}"
  control="/proc/net/pktgen/${device}"
  pgset "${thread}" rem_device_all
  pgset "${thread}" add_device "${device}"
  pgset "${control}" count 30000000
  pgset "${control}" clone_skb 64
  pgset "${control}" burst 8
  pgset "${control}" flows 144
  pgset "${control}" flowlen 36
  pgset "${control}" pkt_size 64
  pgset "${control}" delay 0
  pgset "${control}" queue_map_min "${index}"
  pgset "${control}" queue_map_max "${index}"
  pgset "${control}" dst_mac 02:00:00:00:00:01
  pgset "${control}" src_mac 02:00:00:00:00:02
  pgset "${control}" src_min "10.${index}.0.1"
  pgset "${control}" src_max "10.${index}.0.1"
  pgset "${control}" dst_min "11.${index}.0.1"
  # Linux 5.10 pktgen stores daddr_max as exclusive; .1 through .144 therefore
  # require an exclusive .145 upper bound.
  pgset "${control}" dst_max "11.${index}.0.145"
  pgset "${control}" udp_src_min "$((10000 + index))"
  pgset "${control}" udp_src_max "$((10000 + index))"
  pgset "${control}" udp_dst_min 53
  pgset "${control}" udp_dst_max 53
  pgset "${control}" flag FLOW_SEQ
  pgset "${control}" flag NO_TIMESTAMP
  cp -- "${control}" "${evidence_dir}/pktgen_configured_${index}.txt"
done

python3 - "${evidence_dir}" <<'PY'
import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
for index in range(8):
    path = root / f"pktgen_configured_{index}.txt"
    text = path.read_text(encoding="utf-8")
    checks = {
        "clone_skb": r"\bclone_skb:\s*64\b",
        "flows": r"\bflows:\s*144\b",
        "flowlen": r"\bflowlen:\s*36\b",
        "queue_map": rf"\bqueue_map_min:\s*{index}\s+queue_map_max:\s*{index}\b",
        "dst_range": rf"\bdst_min:\s*11\.{index}\.0\.1\s+dst_max:\s*11\.{index}\.0\.145\b",
        "udp_dst": r"\budp_dst_min:\s*53\s+udp_dst_max:\s*53\b",
        "flow_seq": r"^\s*Flags:.*\bFLOW_SEQ\b",
        "no_timestamp": r"^\s*Flags:.*\bNO_TIMESTAMP\b",
    }
    failed = [name for name, pattern in checks.items()
              if re.search(pattern, text, re.MULTILINE) is None]
    if failed: raise SystemExit(f"pktgen Params mismatch queue {index}: {failed}")
(root / "pktgen_params_validation.txt").write_text(
    "profile=deterministic_multiflow_v2\nqueues_validated=8\nstatus=passed\n",
    encoding="ascii")
PY

verify_frozen || { echo "frozen artifacts drifted before execution" >&2; exit 75; }
setsid "${frozen_binary}" \
  --interface "${capture_nic}" \
  --fanout-mode qm \
  --allow-qm-with-verified-flow-affinity \
  --flow-affinity-evidence-max-distinct-per-worker 65536 \
  --worker-cpus 36 37 38 39 40 41 42 43 \
  --scheduler-cpu "${scheduler_cpu}" \
  --block-size 65536 --block-count 256 --frame-size 256 \
  --retire-block-timeout-ms 1 --start-delay-ms 13000 --duration-s 21 \
  --gpu-endpoint listen://0.0.0.0:50052 --gpu-startup-wait-ms 120000 \
  --batch-size 8 --feature-flush-us 1000 --gpu-timeout-ms 150 \
  --feature-queue-capacity 8192 --gpu-queue-capacity 8192 \
  --idle-timeout-s 120 --active-timeout-s 1 \
  --ready-file "${evidence_dir}/pipeline_ready.json" \
  --output "${evidence_dir}/pipeline_raw.json" \
  >"${evidence_dir}/pipeline.stdout" 2>"${evidence_dir}/pipeline.stderr" &
capture_pid=$!
event pipeline_spawned
for _ in $(seq 1 40); do
  capture_pgid="$(ps -o pgid= -p "${capture_pid}" 2>/dev/null | tr -d ' ')"
  capture_exe="$(readlink -f -- "/proc/${capture_pid}/exe" 2>/dev/null || true)"
  capture_cmdline="$(tr '\0' ' ' <"/proc/${capture_pid}/cmdline" 2>/dev/null || true)"
  if [[ "${capture_pgid}" == "${capture_pid}" && "${capture_exe}" == "${frozen_binary}" \
    && "${capture_cmdline}" == *"--output ${evidence_dir}/pipeline_raw.json"* \
    && "${capture_cmdline}" == *"--ready-file ${evidence_dir}/pipeline_ready.json"* ]]; then
    capture_identity_verified=true
    printf 'pid=%s\npgid=%s\nexe=%s\ncmdline=%s\n' "${capture_pid}" "${capture_pgid}" \
      "${capture_exe}" "${capture_cmdline}" >"${evidence_dir}/pipeline_process_identity.env"
    break
  fi
  kill -0 "${capture_pid}" 2>/dev/null || break
  sleep 0.05
done
if [[ "${capture_identity_verified}" != true ]]; then
  echo "spawned capture process identity could not be proven" >&2
  exit 81
fi
monitor_target_irq_affinity >"${evidence_dir}/irq_affinity_monitor.stdout" \
  2>"${evidence_dir}/irq_affinity_monitor.stderr" &
monitor_pid=$!

ready=false
for _ in $(seq 1 2400); do
  if [[ -s "${evidence_dir}/pipeline_ready.json" ]] && python3 - "${evidence_dir}/pipeline_ready.json" <<'PY'
import json, pathlib, sys
v=json.loads(pathlib.Path(sys.argv[1]).read_text())
raise SystemExit(0 if v.get("ready") is True and v.get("gpu_ready_at_start") is True
                 and v.get("fanout_mode") == "qm" and v.get("workers") == 8 else 1)
PY
  then ready=true; break; fi
  kill -0 "${capture_pid}" 2>/dev/null || { echo "pipeline exited before GPU reverse ready" >&2; exit 80; }
  sleep 0.05
done
[[ "${ready}" == true ]] || { echo "GPU reverse connection did not become ready" >&2; exit 80; }
event gpu_reverse_ready
grep -E '^(Name|Pid|PPid|VmRSS|VmHWM|Threads|Cpus_allowed_list):' "/proc/${capture_pid}/status" \
  >"${evidence_dir}/pipeline_process_status_ready.txt"

if command -v mpstat >/dev/null 2>&1; then
  LC_ALL=C mpstat -P ALL 1 21 >"${evidence_dir}/mpstat.txt" 2>&1 & resource_monitor_pid=$!
else
  printf 'mpstat unavailable\n' >"${evidence_dir}/mpstat.txt"
fi

# The ready receipt is written only after the reverse worker is connected. Wait
# Preserve the former 13-second stabilization interval while irqbalance is
# stopped; the strict 100-ms target-affinity monitor must remain alive.
sleep 11
kill -0 "${monitor_pid}" 2>/dev/null || {
  echo "IRQ/irqbalance monitor exited during the stability wait" >&2; exit 82; }
verify_irqbalance_inactive || { echo "irqbalance became active before generator start" >&2; exit 82; }
sleep 2
verify_target_irq_affinity >"${evidence_dir}/irq_affinity_generator_start_check.tsv" || {
  echo "target IRQ affinity drifted before generator start" >&2; exit 82; }
kill -0 "${monitor_pid}" 2>/dev/null || {
  echo "IRQ affinity monitor exited before generator start" >&2; exit 82; }
taskset -c "${generator_control_cpu}" bash -c 'echo start >/proc/net/pktgen/pgctrl' &
generator_start_pid=$!
event generator_started
sleep 19 & timer_pid=$!
wait "${timer_pid}"
timer_pid=
echo stop >/proc/net/pktgen/pgctrl
event generator_stopped
wait "${generator_start_pid}" 2>/dev/null || true
generator_start_pid=

for index in $(seq 0 7); do
  cp -- "/proc/net/pktgen/${replay_nic}@${index}" "${evidence_dir}/pktgen_device_${index}.txt"
done
cp -- /proc/net/pktgen/pgctrl "${evidence_dir}/pktgen_pgctrl.txt"
wait "${capture_pid}"
capture_pid=
event pipeline_completed
bounded_stop_pid irq_affinity_monitor "${monitor_pid}"
monitor_pid=
bounded_stop_pid mpstat "${resource_monitor_pid}"
resource_monitor_pid=
snapshot_state pre_restore
verify_frozen || { echo "frozen artifacts drifted during execution" >&2; exit 75; }

python3 - "${evidence_dir}/before_${capture_nic}_statistics.txt" \
  "${evidence_dir}/pre_restore_${capture_nic}_statistics.txt" \
  "${evidence_dir}/nic_rx_discards_gate.json" <<'PY'
import json, os, pathlib, re, sys, tempfile
def parse(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    totals = re.findall(r"^\s+rx_discards:\s*([0-9]+)\s*$", text, re.MULTILINE)
    if len(totals) != 1: raise SystemExit("unique total rx_discards counter missing")
    queues = {int(q): int(v) for q, v in re.findall(
        r"^\s+\[([0-9]+)\]: rx_discards:\s*([0-9]+)\s*$", text, re.MULTILINE)}
    if set(queues) != set(range(8)): raise SystemExit("per-queue rx_discards evidence incomplete")
    return int(totals[0]), queues
before_total, before_queues = parse(sys.argv[1])
after_total, after_queues = parse(sys.argv[2])
delta = after_total - before_total
queue_delta = {str(q): after_queues[q] - before_queues[q] for q in range(8)}
value = {"schema_version": 1, "counter": "capture_nic_rx_discards",
         "before": before_total, "after": after_total, "delta": delta,
         "per_queue_delta": queue_delta, "maximum_allowed_delta": 0,
         "passed": delta == 0 and all(v == 0 for v in queue_delta.values())}
target = pathlib.Path(sys.argv[3])
handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
    dir=str(target.parent), prefix=target.name + ".", suffix=".tmp", delete=False)
with handle:
    json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
    handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
pathlib.Path(handle.name).replace(target)
if not value["passed"]: raise SystemExit("capture NIC rx_discards delta is nonzero")
PY

# Raw shape only. Qualification is deliberately left to the independent gate.
python3 - "${evidence_dir}/pipeline_raw.json" <<'PY'
import json, pathlib, sys
v=json.loads(pathlib.Path(sys.argv[1]).read_text())
required = {
    "schema_version": 2,
    "scope": "hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw",
    "fanout_mode": "qm",
    "gpu_ready_at_start": True,
    "runtime_identity_verified": False,
    "full_pipeline_qualified": False,
    "final_pareto_ingestion_allowed": False,
}
for key, expected in required.items():
    if v.get(key) != expected: raise SystemExit(f"raw pipeline shape mismatch: {key}")
affinity = v.get("qm_flow_affinity_evidence")
if not isinstance(affinity, dict):
    raise SystemExit("QM runtime flow-affinity evidence is missing")
affinity_required = {
    "hash_algorithm": "dual_fnv1a64_v1",
    "evidence_overflow": False,
    "evidence_complete": True,
    "runtime_verified": True,
    "cross_worker_collision_count": 0,
}
for key, expected in affinity_required.items():
    if affinity.get(key) != expected:
        raise SystemExit(f"QM runtime flow-affinity evidence mismatch: {key}")
if affinity.get("closed_flow_observations") != v.get("flows_closed"):
    raise SystemExit("QM flow-affinity evidence does not cover every closed-flow observation")
if not isinstance(affinity.get("distinct_flow_hashes"), int) or affinity["distinct_flow_hashes"] <= 0:
    raise SystemExit("QM flow-affinity evidence has no distinct flow")
if v.get("parser_profile_id") != "deterministic_multiflow_v2_fixed64_ipv4_udp_strict_v1":
    raise SystemExit("fixed64 parser profile identity mismatch")
fast = v.get("fixed_profile_fast_parsed")
fallback = v.get("fixed_profile_general_fallback")
parsed = v.get("packets_parsed")
if not isinstance(fast, int) or fast <= 0 or not isinstance(fallback, int) or fallback < 0:
    raise SystemExit("fixed64 parser counters missing")
if not isinstance(parsed, int) or fast + fallback != parsed:
    raise SystemExit("fixed64 fast/fallback conservation failed")
if fallback != 0:
    raise SystemExit("traffic-v2 unexpectedly entered general parser fallback")
if v.get("full_epoch_windows", 0) < 15:
    raise SystemExit("fewer than 15 complete one-second windows")
windows = v.get("full_epoch_windows", 0)
flows = v.get("flows_closed", 0)
if not isinstance(flows, int) or flows < windows * 1000:
    raise SystemExit("aggregate closed-flow density is below 1000 per full window")
# This aggregate density check does not prove each individual window. The raw
# runner therefore keeps every qualification field false.
PY

exit 0
