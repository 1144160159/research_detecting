#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 EVIDENCE_DIR" >&2
  exit 2
fi

evidence_dir=$1
capture_nic=ens8f0
replay_nic=ens8f1
probe=/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture/target/release/tpacket_v3_fastpath_probe
capture_pid=
start_pid=
module_was_loaded=false
cleanup_started=false

mkdir -p "$evidence_dir"

current_rx_ring() {
  ethtool -g "$capture_nic" | awk '/Current hardware settings:/{active=1;next} active && /^RX:/{print $2;exit}'
}

original_rx_ring=$(current_rx_ring)
[[ "$original_rx_ring" =~ ^[0-9]+$ ]] || { echo "cannot read RX ring" >&2; exit 3; }
lsmod | awk '{print $1}' | grep -qx pktgen && module_was_loaded=true

cleanup() {
  local rc=$?
  [[ "$cleanup_started" == false ]] || exit "$rc"
  cleanup_started=true
  trap '' HUP INT TERM
  if [[ -w /proc/net/pktgen/pgctrl ]]; then
    echo stop >/proc/net/pktgen/pgctrl 2>/dev/null || rc=91
  fi
  [[ -z "$start_pid" ]] || kill "$start_pid" 2>/dev/null || true
  [[ -z "$capture_pid" ]] || kill "$capture_pid" 2>/dev/null || true
  wait "$start_pid" 2>/dev/null || true
  wait "$capture_pid" 2>/dev/null || true
  ethtool -G "$capture_nic" rx "$original_rx_ring" || rc=92
  if [[ "$module_was_loaded" == false ]]; then
    rmmod pktgen 2>/dev/null || rc=93
  fi
  ethtool -g "$capture_nic" >"$evidence_dir/ring_restored.txt" || rc=94
  ip -details -oneline link show "$capture_nic" >"$evidence_dir/post_link.txt" || rc=95
  exit "$rc"
}
trap cleanup EXIT HUP INT TERM

ethtool -g "$capture_nic" >"$evidence_dir/ring_before.txt"
ethtool -S "$capture_nic" >"$evidence_dir/stats_before.txt"
modprobe pktgen
ethtool -G "$capture_nic" rx 4078
ethtool -g "$capture_nic" >"$evidence_dir/ring_active.txt"

pgset() {
  local file=$1
  shift
  printf '%s\n' "$*" >"$file"
  grep -q 'Result: OK:' "$file"
}

tx_cpus=(28 30 32 34 36 38 40 42)
for index in "${!tx_cpus[@]}"; do
  cpu=${tx_cpus[$index]}
  thread=/proc/net/pktgen/kpktgend_${cpu}
  device=${replay_nic}@${index}
  pgset "$thread" rem_device_all
  pgset "$thread" add_device "$device"
  control=/proc/net/pktgen/$device
  pgset "$control" count 30000000
  pgset "$control" clone_skb 0
  pgset "$control" pkt_size 64
  pgset "$control" delay 0
  pgset "$control" queue_map_min "$index"
  pgset "$control" queue_map_max "$index"
  pgset "$control" dst_mac 02:00:00:00:00:01
  pgset "$control" src_mac 02:00:00:00:00:02
  pgset "$control" src_min "10.$index.0.1"
  pgset "$control" src_max "10.$index.255.254"
  pgset "$control" dst_min "11.$index.0.1"
  pgset "$control" dst_max "11.$index.255.254"
  pgset "$control" udp_src_min 1024
  pgset "$control" udp_src_max 61023
  pgset "$control" udp_dst_min 1024
  pgset "$control" udp_dst_max 61023
  pgset "$control" flag IPSRC_RND
  pgset "$control" flag IPDST_RND
  pgset "$control" flag UDPSRC_RND
  pgset "$control" flag UDPDST_RND
done

"$probe" \
  --interface "$capture_nic" \
  --fanout-mode hash \
  --fanout-id 23123 \
  --worker-cpus 48,50,52,54 \
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

echo start >/proc/net/pktgen/pgctrl &
start_pid=$!
sleep 15
echo stop >/proc/net/pktgen/pgctrl
wait "$start_pid" 2>/dev/null || true
start_pid=
wait "$capture_pid"
capture_pid=

ethtool -S "$capture_nic" >"$evidence_dir/stats_after.txt"
cp /proc/net/pktgen/pgctrl "$evidence_dir/pktgen_pgctrl.txt"
for index in "${!tx_cpus[@]}"; do
  cp "/proc/net/pktgen/${replay_nic}@${index}" "$evidence_dir/pktgen_device_${index}.txt"
done

trap - EXIT HUP INT TERM
cleanup
