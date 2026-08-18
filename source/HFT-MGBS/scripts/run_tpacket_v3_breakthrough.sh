#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 5 ]]; then
  echo "usage: $0 EVIDENCE_DIR CANDIDATE_ID CLONE_SKB BURST RX_USECS" >&2
  exit 2
fi

evidence_dir=$1
candidate_id=$2
clone_skb=$3
burst=$4
rx_usecs=$5
capture_nic=ens8f0
replay_nic=ens8f1
probe=/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture/target/release/tpacket_v3_fastpath_probe
capture_pid=
start_pid=
monitor_pid=
cleanup_started=false
original_rx_ring=
original_rx_usecs=
fanout_contract=PACKET_FANOUT_QM

[[ "$candidate_id" =~ ^B[123]_[A-Za-z0-9_]+$ ]] || {
  echo "invalid candidate id: $candidate_id" >&2
  exit 2
}
[[ "$clone_skb" =~ ^[0-9]+$ ]] || { echo "CLONE_SKB must be an integer" >&2; exit 2; }
[[ "$burst" =~ ^[1-9][0-9]*$ ]] || { echo "BURST must be a positive integer" >&2; exit 2; }
[[ "$rx_usecs" =~ ^[0-9]+$ ]] || { echo "RX_USECS must be an integer" >&2; exit 2; }
[[ ! -e "$evidence_dir" ]] || { echo "evidence directory already exists" >&2; exit 3; }
mkdir "$evidence_dir"

current_rx_ring() {
  ethtool -g "$capture_nic" |
    awk '/Current hardware settings:/{active=1;next} active && /^RX:/{print $2;exit}'
}

current_rx_usecs() {
  ethtool -c "$capture_nic" | awk '/^rx-usecs:/{print $2;exit}'
}

irq_rows() {
  local nic=$1
  awk -v nic="$nic" '$NF ~ ("^" nic "-fp-[0-9]+$") {
    irq=$1; sub(":", "", irq); print irq "\t" $NF
  }' /proc/interrupts | sort -V
}

record_irq_affinity() {
  local output=$1
  : >"$output"
  while IFS=$'\t' read -r irq label; do
    printf '%s\t%s\t%s\n' "$irq" "$label" "$(<"/proc/irq/$irq/smp_affinity_list")" >>"$output"
  done < <({ irq_rows "$capture_nic"; irq_rows "$replay_nic"; })
}

set_cleanup_error() {
  local code=$1
  if (( cleanup_rc == 0 )); then
    cleanup_rc=$code
  fi
}

cleanup() {
  local cleanup_rc=$?
  [[ "$cleanup_started" == false ]] || exit "$cleanup_rc"
  cleanup_started=true
  trap - EXIT
  trap '' HUP INT TERM

  if [[ -w /proc/net/pktgen/pgctrl ]]; then
    echo stop >/proc/net/pktgen/pgctrl 2>/dev/null || set_cleanup_error 91
  fi
  [[ -z "$start_pid" ]] || kill "$start_pid" 2>/dev/null || true
  [[ -z "$capture_pid" ]] || kill "$capture_pid" 2>/dev/null || true
  [[ -z "$monitor_pid" ]] || kill "$monitor_pid" 2>/dev/null || true
  wait "$start_pid" 2>/dev/null || true
  wait "$capture_pid" 2>/dev/null || true
  wait "$monitor_pid" 2>/dev/null || true

  if [[ -s "$evidence_dir/irq_affinity_before.tsv" ]]; then
    while IFS=$'\t' read -r irq _label affinity; do
      printf '%s\n' "$affinity" >"/proc/irq/$irq/smp_affinity_list" || set_cleanup_error 92
    done <"$evidence_dir/irq_affinity_before.tsv"
  fi
  if [[ -n "$original_rx_ring" ]]; then
    ethtool -G "$capture_nic" rx "$original_rx_ring" || set_cleanup_error 93
  fi
  if [[ -n "$original_rx_usecs" ]]; then
    ethtool -C "$capture_nic" rx-usecs "$original_rx_usecs" || set_cleanup_error 94
  fi
  if lsmod | awk '{print $1}' | grep -qx pktgen; then
    rmmod pktgen || set_cleanup_error 95
  fi

  record_irq_affinity "$evidence_dir/irq_affinity_restored.tsv" || set_cleanup_error 96
  ethtool -g "$capture_nic" >"$evidence_dir/ring_restored.txt" || set_cleanup_error 97
  ethtool -c "$capture_nic" >"$evidence_dir/coalesce_restored.txt" || set_cleanup_error 98
  ip -details -oneline link show "$capture_nic" >"$evidence_dir/post_capture_link.txt" || set_cleanup_error 99
  ip -details -oneline link show "$replay_nic" >"$evidence_dir/post_replay_link.txt" || set_cleanup_error 100
  lsmod | awk '$1 == "pktgen" {print}' >"$evidence_dir/pktgen_module_post.txt" || set_cleanup_error 101
  printf 'runner_exit_status=%s\n' "$cleanup_rc" >"$evidence_dir/runner_exit_status.env"
  exit "$cleanup_rc"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

[[ -x "$probe" ]] || { echo "probe binary is missing" >&2; exit 4; }
lsmod | awk '{print $1}' | grep -qx pktgen && {
  echo "pktgen is already loaded; refusing to alter shared pktgen state" >&2
  exit 5
}
[[ "$(cat "/sys/class/net/$capture_nic/device/numa_node")" == 1 ]] || exit 6
[[ "$(cat "/sys/class/net/$replay_nic/device/numa_node")" == 1 ]] || exit 6
mapfile -t capture_irqs < <(irq_rows "$capture_nic")
mapfile -t replay_irqs < <(irq_rows "$replay_nic")
[[ ${#capture_irqs[@]} -eq 8 && ${#replay_irqs[@]} -eq 8 ]] || {
  echo "expected exactly eight queue IRQs per NIC" >&2
  exit 7
}
for cpu in $(seq 28 51); do
  [[ -d "/sys/devices/system/cpu/cpu$cpu" ]] || exit 8
  [[ "$(cat "/sys/devices/system/cpu/cpu$cpu/online" 2>/dev/null || echo 1)" == 1 ]] || exit 8
done

original_rx_ring=$(current_rx_ring)
[[ "$original_rx_ring" =~ ^[0-9]+$ ]] || { echo "cannot read RX ring" >&2; exit 9; }
original_rx_usecs=$(current_rx_usecs)
[[ "$original_rx_usecs" =~ ^[0-9]+$ ]] || { echo "cannot read RX coalescing" >&2; exit 9; }
record_irq_affinity "$evidence_dir/irq_affinity_before.tsv"
ethtool -g "$capture_nic" >"$evidence_dir/ring_before.txt"
ethtool -c "$capture_nic" >"$evidence_dir/coalesce_before.txt"
ethtool -l "$capture_nic" >"$evidence_dir/channels_before.txt"
ethtool -S "$capture_nic" >"$evidence_dir/stats_before.txt"
grep '^cpu ' /proc/stat >"$evidence_dir/proc_stat_before.txt"
grep -E '^(MemTotal|MemAvailable):' /proc/meminfo >"$evidence_dir/meminfo_before.txt"
ip -details -oneline link show "$capture_nic" >"$evidence_dir/pre_capture_link.txt"
ip -details -oneline link show "$replay_nic" >"$evidence_dir/pre_replay_link.txt"
systemctl is-active irqbalance >"$evidence_dir/irqbalance_state.txt" || true
printf '{\n  "schema_version": 1,\n  "candidate_id": "%s",\n  "clone_skb": %s,\n  "burst": %s,\n  "rx_usecs": %s,\n  "fanout_contract": "%s",\n  "fanout_mode": "qm",\n  "workers": 8,\n  "capture_worker_cpus": [36,37,38,39,40,41,42,43],\n  "capture_irq_cpus": [28,29,30,31,32,33,34,35],\n  "pktgen_and_tx_irq_cpus": [44,45,46,47,48,49,50,51]\n}\n' \
  "$candidate_id" "$clone_skb" "$burst" "$rx_usecs" "$fanout_contract" >"$evidence_dir/run_config.json"

ethtool -G "$capture_nic" rx 4078
ethtool -C "$capture_nic" rx-usecs "$rx_usecs"
modprobe pktgen

for index in "${!capture_irqs[@]}"; do
  IFS=$'\t' read -r irq _label <<<"${capture_irqs[$index]}"
  printf '%s\n' "$((28 + index))" >"/proc/irq/$irq/smp_affinity_list"
done
for index in "${!replay_irqs[@]}"; do
  IFS=$'\t' read -r irq _label <<<"${replay_irqs[$index]}"
  printf '%s\n' "$((44 + index))" >"/proc/irq/$irq/smp_affinity_list"
done
record_irq_affinity "$evidence_dir/irq_affinity_active.tsv"
ethtool -g "$capture_nic" >"$evidence_dir/ring_active.txt"

pgset() {
  local file=$1
  shift
  printf '%s\n' "$*" >"$file"
  grep -q 'Result: OK:' "$file"
}

tx_cpus=(44 45 46 47 48 49 50 51)
for index in "${!tx_cpus[@]}"; do
  cpu=${tx_cpus[$index]}
  thread=/proc/net/pktgen/kpktgend_${cpu}
  device=${replay_nic}@${index}
  pgset "$thread" rem_device_all
  pgset "$thread" add_device "$device"
  control=/proc/net/pktgen/$device
  pgset "$control" count 30000000
  pgset "$control" clone_skb "$clone_skb"
  pgset "$control" burst "$burst"
  pgset "$control" pkt_size 64
  pgset "$control" delay 0
  pgset "$control" queue_map_min "$index"
  pgset "$control" queue_map_max "$index"
  pgset "$control" dst_mac 02:00:00:00:00:01
  pgset "$control" src_mac 02:00:00:00:00:02
  pgset "$control" src_min "10.$index.0.1"
  pgset "$control" src_max "10.$index.0.1"
  pgset "$control" dst_min "11.$index.0.1"
  pgset "$control" dst_max "11.$index.0.1"
  pgset "$control" udp_src_min "$((10000 + index))"
  pgset "$control" udp_src_max "$((10000 + index))"
  pgset "$control" udp_dst_min "$((20000 + index))"
  pgset "$control" udp_dst_max "$((20000 + index))"
  pgset "$control" flag NO_TIMESTAMP
done

if command -v mpstat >/dev/null 2>&1; then
  LC_ALL=C mpstat -P 28-51 1 18 >"$evidence_dir/mpstat.txt" 2>&1 &
  monitor_pid=$!
else
  printf 'mpstat unavailable\n' >"$evidence_dir/mpstat.txt"
fi

"$probe" \
  --interface "$capture_nic" \
  --fanout-mode qm \
  --fanout-id 23124 \
  --worker-cpus 36,37,38,39,40,41,42,43 \
  --block-size 4096 \
  --block-count 4096 \
  --frame-size 256 \
  --retire-block-timeout-ms 1 \
  --start-delay-ms 0 \
  --duration-s 17 \
  --ready-file "$evidence_dir/ready.json" \
  --output "$evidence_dir/capture.json" \
  >"$evidence_dir/capture.stdout" 2>"$evidence_dir/capture.stderr" &
capture_pid=$!

for _ in $(seq 1 100); do
  [[ -s "$evidence_dir/ready.json" ]] && break
  sleep 0.05
done
[[ -s "$evidence_dir/ready.json" ]]
grep -E '^(VmRSS|VmHWM|Threads):' "/proc/$capture_pid/status" >"$evidence_dir/capture_process_status.txt"

taskset -c 52 bash -c 'echo start >/proc/net/pktgen/pgctrl' &
start_pid=$!
sleep 15
echo stop >/proc/net/pktgen/pgctrl
wait "$start_pid" 2>/dev/null || true
start_pid=
wait "$capture_pid"
capture_pid=

ethtool -S "$capture_nic" >"$evidence_dir/stats_after.txt"
grep '^cpu ' /proc/stat >"$evidence_dir/proc_stat_after.txt"
grep -E '^(MemTotal|MemAvailable):' /proc/meminfo >"$evidence_dir/meminfo_after.txt"
record_irq_affinity "$evidence_dir/irq_affinity_pre_restore.tsv"
cp /proc/net/pktgen/pgctrl "$evidence_dir/pktgen_pgctrl.txt"
for index in "${!tx_cpus[@]}"; do
  cp "/proc/net/pktgen/${replay_nic}@${index}" "$evidence_dir/pktgen_device_${index}.txt"
done

cleanup
