#[cfg(not(target_os = "linux"))]
compile_error!("tpacket_v3_fastpath_probe is Linux-only");

use anyhow::{bail, Context, Result};
use clap::{Parser, ValueEnum};
use serde::Serialize;
use std::collections::BTreeMap;
use std::fs::File;
use std::io::Write;
use std::mem::{size_of, zeroed};
use std::os::fd::RawFd;
use std::path::PathBuf;
use std::ptr;
use std::sync::atomic::{fence, Ordering};
use std::sync::{Arc, Barrier};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const ETH_P_ALL: u16 = 0x0003;
const PACKET_RX_RING: libc::c_int = 5;
const PACKET_STATISTICS: libc::c_int = 6;
const PACKET_ADD_MEMBERSHIP: libc::c_int = 1;
const PACKET_VERSION: libc::c_int = 10;
const PACKET_FANOUT: libc::c_int = 18;
const PACKET_MR_PROMISC: u16 = 1;
const TPACKET_V3: libc::c_int = 2;
const TP_STATUS_KERNEL: u32 = 0;
const TP_STATUS_USER: u32 = 1;
const TP_FT_REQ_FILL_RXHASH: u32 = 1;
const LATENCY_SAMPLE_STRIDE: u64 = 1024;
const MAX_LATENCY_SAMPLES: usize = 1_000_000;

#[derive(Clone, Copy, Debug, ValueEnum)]
enum FanoutMode {
    Hash,
    Qm,
}

impl FanoutMode {
    fn kernel_value(self) -> u16 {
        match self {
            Self::Hash => 0,
            Self::Qm => 5,
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Hash => "hash",
            Self::Qm => "qm",
        }
    }
}

#[derive(Debug, Parser)]
#[command(about = "TPACKET_V3 capture-only capacity probe with PACKET_FANOUT")]
struct Args {
    #[arg(long)]
    interface: String,
    #[arg(long, value_enum, default_value = "hash")]
    fanout_mode: FanoutMode,
    #[arg(long, default_value_t = 23117)]
    fanout_id: u16,
    #[arg(long, value_delimiter = ',', num_args = 1..)]
    worker_cpus: Vec<usize>,
    #[arg(long, default_value_t = 65_536)]
    block_size: u32,
    #[arg(long, default_value_t = 256)]
    block_count: u32,
    #[arg(long, default_value_t = 256)]
    frame_size: u32,
    #[arg(long, default_value_t = 1)]
    retire_block_timeout_ms: u32,
    #[arg(long, default_value_t = 2_000)]
    start_delay_ms: u64,
    #[arg(long, default_value_t = 15)]
    duration_s: u64,
    #[arg(long)]
    ready_file: Option<PathBuf>,
    #[arg(long)]
    output: PathBuf,
}

#[repr(C)]
#[derive(Clone, Copy, Default)]
struct TpacketReq3 {
    tp_block_size: u32,
    tp_block_nr: u32,
    tp_frame_size: u32,
    tp_frame_nr: u32,
    tp_retire_blk_tov: u32,
    tp_sizeof_priv: u32,
    tp_feature_req_word: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct TpacketBdTs {
    ts_sec: u32,
    ts_nsec: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct TpacketHdrV1 {
    block_status: u32,
    num_pkts: u32,
    offset_to_first_pkt: u32,
    blk_len: u32,
    seq_num: u64,
    ts_first_pkt: TpacketBdTs,
    ts_last_pkt: TpacketBdTs,
}

#[repr(C)]
struct TpacketBlockDesc {
    version: u32,
    offset_to_priv: u32,
    hdr: TpacketHdrV1,
}

#[repr(C)]
struct Tpacket3Hdr {
    tp_next_offset: u32,
    tp_sec: u32,
    tp_nsec: u32,
    tp_snaplen: u32,
    tp_len: u32,
    tp_status: u32,
    tp_mac: u16,
    tp_net: u16,
}

#[repr(C)]
#[derive(Clone, Copy, Default, Serialize)]
struct TpacketStatsV3 {
    tp_packets: u32,
    tp_drops: u32,
    tp_freeze_q_cnt: u32,
}

#[repr(C)]
#[derive(Clone, Copy, Default)]
struct PacketMreq {
    mr_ifindex: libc::c_int,
    mr_type: u16,
    mr_alen: u16,
    mr_address: [u8; 8],
}

struct PacketRing {
    fd: RawFd,
    base: *mut u8,
    map_len: usize,
    request: TpacketReq3,
}

unsafe impl Send for PacketRing {}

impl Drop for PacketRing {
    fn drop(&mut self) {
        if !self.base.is_null() && self.map_len != 0 {
            unsafe {
                libc::munmap(self.base.cast(), self.map_len);
            }
        }
        if self.fd >= 0 {
            unsafe {
                libc::close(self.fd);
            }
        }
    }
}

#[derive(Serialize)]
struct Percentiles {
    samples: usize,
    p50_us: Option<u64>,
    p99_us: Option<u64>,
    p999_us: Option<u64>,
    max_us: Option<u64>,
}

#[derive(Serialize)]
struct WorkerReport {
    worker_index: usize,
    cpu: usize,
    packets: u64,
    synthetic_test_packets: u64,
    bytes: u64,
    blocks: u64,
    payload_guard: u64,
    ring_statistics: TpacketStatsV3,
    synthetic_epoch_second_counts: BTreeMap<u64, u64>,
    latency_samples_us: Vec<u64>,
}

#[derive(Serialize)]
struct ProbeReport {
    schema_version: u32,
    scope: &'static str,
    backend: &'static str,
    interface: String,
    fanout_mode: &'static str,
    fanout_id: u16,
    worker_cpus: Vec<usize>,
    block_size: u32,
    block_count_per_worker: u32,
    frame_size: u32,
    ring_memory_bytes: u64,
    promiscuous_membership: bool,
    duration_s: f64,
    packets: u64,
    synthetic_test_packets: u64,
    non_test_packets: u64,
    bytes: u64,
    achieved_mpps: f64,
    achieved_gbps: f64,
    synthetic_rx_full_epoch_windows: usize,
    synthetic_rx_min_full_epoch_mpps: Option<f64>,
    packet_socket_statistics_packets: u64,
    packet_socket_drops: u64,
    packet_socket_freeze_queue_count: u64,
    process_cpu_cores_average: f64,
    latency_sample_stride: u64,
    latency_timestamp_source: &'static str,
    packet_socket_timestamp_to_userspace_latency: Percentiles,
    workers: Vec<WorkerSummary>,
    raw_capture_only_observation: bool,
    r0_capture_only_qualified: bool,
    full_pipeline_qualified: bool,
    final_pareto_ingestion_allowed: bool,
}

#[derive(Serialize)]
struct WorkerSummary {
    worker_index: usize,
    cpu: usize,
    packets: u64,
    synthetic_test_packets: u64,
    bytes: u64,
    blocks: u64,
    payload_guard: u64,
    ring_statistics: TpacketStatsV3,
}

fn validate_args(args: &Args) -> Result<()> {
    if args.worker_cpus.is_empty() || args.worker_cpus.len() > 64 {
        bail!("--worker-cpus must contain 1..=64 CPUs");
    }
    let mut cpus = args.worker_cpus.clone();
    cpus.sort_unstable();
    cpus.dedup();
    if cpus.len() != args.worker_cpus.len() {
        bail!("--worker-cpus must not contain duplicates");
    }
    if args.fanout_id == 0 {
        bail!("--fanout-id must be non-zero");
    }
    if args.duration_s == 0 || args.duration_s > 3_600 {
        bail!("--duration-s must be in 1..=3600");
    }
    if args.block_size == 0
        || args.block_count == 0
        || args.frame_size == 0
        || !args.frame_size.is_multiple_of(16)
        || !args.block_size.is_multiple_of(args.frame_size)
    {
        bail!(
            "ring sizes must be positive; frame size must be 16-byte aligned and divide block size"
        );
    }
    let page_size = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
    if page_size <= 0 || !args.block_size.is_multiple_of(page_size as u32) {
        bail!("--block-size must be a multiple of the system page size");
    }
    let map_len = u64::from(args.block_size)
        .checked_mul(u64::from(args.block_count))
        .and_then(|size| size.checked_mul(args.worker_cpus.len() as u64))
        .context("ring memory size overflow")?;
    if map_len > 8 * 1024 * 1024 * 1024 {
        bail!("total ring memory must not exceed 8 GiB");
    }
    Ok(())
}

fn set_socket_option<T>(fd: RawFd, option: libc::c_int, value: &T) -> Result<()> {
    let status = unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_PACKET,
            option,
            (value as *const T).cast(),
            size_of::<T>() as libc::socklen_t,
        )
    };
    if status != 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("setsockopt SOL_PACKET option {option}"));
    }
    Ok(())
}

fn open_ring(args: &Args) -> Result<PacketRing> {
    let protocol = ETH_P_ALL.to_be() as libc::c_int;
    let fd = unsafe {
        libc::socket(
            libc::AF_PACKET,
            libc::SOCK_RAW | libc::SOCK_CLOEXEC,
            protocol,
        )
    };
    if fd < 0 {
        return Err(std::io::Error::last_os_error()).context("open AF_PACKET socket");
    }
    let mut ring = PacketRing {
        fd,
        base: ptr::null_mut(),
        map_len: 0,
        request: TpacketReq3::default(),
    };

    set_socket_option(ring.fd, PACKET_VERSION, &TPACKET_V3)?;
    let frames_per_block = args.block_size / args.frame_size;
    ring.request = TpacketReq3 {
        tp_block_size: args.block_size,
        tp_block_nr: args.block_count,
        tp_frame_size: args.frame_size,
        tp_frame_nr: frames_per_block
            .checked_mul(args.block_count)
            .context("ring frame count overflow")?,
        tp_retire_blk_tov: args.retire_block_timeout_ms,
        tp_sizeof_priv: 0,
        tp_feature_req_word: TP_FT_REQ_FILL_RXHASH,
    };
    set_socket_option(ring.fd, PACKET_RX_RING, &ring.request)?;

    ring.map_len = (args.block_size as usize)
        .checked_mul(args.block_count as usize)
        .context("ring map size overflow")?;
    let base = unsafe {
        libc::mmap(
            ptr::null_mut(),
            ring.map_len,
            libc::PROT_READ | libc::PROT_WRITE,
            libc::MAP_SHARED,
            ring.fd,
            0,
        )
    };
    if base == libc::MAP_FAILED {
        return Err(std::io::Error::last_os_error()).context("mmap TPACKET_V3 ring");
    }
    ring.base = base.cast();

    let interface = std::ffi::CString::new(args.interface.as_str())
        .context("interface contains an embedded NUL")?;
    let interface_index = unsafe { libc::if_nametoindex(interface.as_ptr()) };
    if interface_index == 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("resolve interface {}", args.interface));
    }
    let mut address: libc::sockaddr_ll = unsafe { zeroed() };
    address.sll_family = libc::AF_PACKET as u16;
    address.sll_protocol = ETH_P_ALL.to_be();
    address.sll_ifindex = interface_index as i32;
    let status = unsafe {
        libc::bind(
            ring.fd,
            (&address as *const libc::sockaddr_ll).cast(),
            size_of::<libc::sockaddr_ll>() as libc::socklen_t,
        )
    };
    if status != 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("bind AF_PACKET socket to {}", args.interface));
    }

    let membership = PacketMreq {
        mr_ifindex: interface_index as libc::c_int,
        mr_type: PACKET_MR_PROMISC,
        mr_alen: 0,
        mr_address: [0; 8],
    };
    set_socket_option(ring.fd, PACKET_ADD_MEMBERSHIP, &membership)
        .context("enable per-socket PACKET_MR_PROMISC membership")?;

    let fanout = u32::from(args.fanout_id) | (u32::from(args.fanout_mode.kernel_value()) << 16);
    set_socket_option(ring.fd, PACKET_FANOUT, &fanout)?;
    Ok(ring)
}

fn pin_current_thread(cpu: usize) -> Result<()> {
    if cpu >= 1024 {
        bail!("CPU {cpu} exceeds cpu_set_t capacity");
    }
    let mut set: libc::cpu_set_t = unsafe { zeroed() };
    unsafe {
        libc::CPU_ZERO(&mut set);
        libc::CPU_SET(cpu, &mut set);
    }
    let status = unsafe {
        libc::pthread_setaffinity_np(libc::pthread_self(), size_of::<libc::cpu_set_t>(), &set)
    };
    if status != 0 {
        return Err(std::io::Error::from_raw_os_error(status))
            .with_context(|| format!("pin capture worker to CPU {cpu}"));
    }
    Ok(())
}

fn packet_socket_statistics(fd: RawFd) -> Result<TpacketStatsV3> {
    let mut stats = TpacketStatsV3::default();
    let mut length = size_of::<TpacketStatsV3>() as libc::socklen_t;
    let status = unsafe {
        libc::getsockopt(
            fd,
            libc::SOL_PACKET,
            PACKET_STATISTICS,
            (&mut stats as *mut TpacketStatsV3).cast(),
            &mut length,
        )
    };
    if status != 0 {
        return Err(std::io::Error::last_os_error()).context("read PACKET_STATISTICS");
    }
    if length as usize != size_of::<TpacketStatsV3>() {
        bail!("PACKET_STATISTICS returned unexpected length {length}");
    }
    Ok(stats)
}

fn is_synthetic_test_frame(frame: &[u8]) -> bool {
    frame.len() >= 14
        && frame[0..6] == [0x02, 0, 0, 0, 0, 1]
        && frame[6..12] == [0x02, 0, 0, 0, 0, 2]
        && frame[12..14] == [0x08, 0x00]
}

unsafe fn process_block(
    block: *mut u8,
    block_size: usize,
    report: &mut WorkerReport,
) -> Result<()> {
    let descriptor = &*(block.cast::<TpacketBlockDesc>());
    if descriptor.version != TPACKET_V3 as u32 {
        bail!("unexpected TPACKET block version {}", descriptor.version);
    }
    let mut offset = descriptor.hdr.offset_to_first_pkt as usize;
    let packet_count = descriptor.hdr.num_pkts as usize;
    for packet_index in 0..packet_count {
        if offset > block_size.saturating_sub(size_of::<Tpacket3Hdr>()) {
            bail!("packet header offset {offset} exceeds block size {block_size}");
        }
        let header = &*(block.add(offset).cast::<Tpacket3Hdr>());
        let mac_offset = offset.saturating_add(header.tp_mac as usize);
        let snaplen = header.tp_snaplen as usize;
        if mac_offset > block_size || snaplen > block_size.saturating_sub(mac_offset) {
            bail!("packet payload exceeds TPACKET block");
        }
        report.packets = report.packets.saturating_add(1);
        report.bytes = report.bytes.saturating_add(u64::from(header.tp_len));
        let frame = std::slice::from_raw_parts(block.add(mac_offset), snaplen);
        let is_synthetic_test_packet = is_synthetic_test_frame(frame);
        if snaplen != 0 {
            report.payload_guard = report
                .payload_guard
                .wrapping_add(u64::from(*block.add(mac_offset)));
        }
        if is_synthetic_test_packet {
            report.synthetic_test_packets = report.synthetic_test_packets.saturating_add(1);
            *report
                .synthetic_epoch_second_counts
                .entry(u64::from(header.tp_sec))
                .or_insert(0) += 1;
        }
        if is_synthetic_test_packet
            && report
                .synthetic_test_packets
                .is_multiple_of(LATENCY_SAMPLE_STRIDE)
            && report.latency_samples_us.len() < MAX_LATENCY_SAMPLES
        {
            let packet_timestamp_us = u64::from(header.tp_sec)
                .saturating_mul(1_000_000)
                .saturating_add(u64::from(header.tp_nsec) / 1_000);
            let now_us = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .context("system clock precedes UNIX epoch")?
                .as_micros()
                .min(u64::MAX as u128) as u64;
            if let Some(latency) = now_us.checked_sub(packet_timestamp_us) {
                report.latency_samples_us.push(latency);
            }
        }
        if packet_index + 1 < packet_count {
            if header.tp_next_offset == 0 {
                bail!("zero tp_next_offset before final packet in block");
            }
            offset = offset
                .checked_add(header.tp_next_offset as usize)
                .context("packet offset overflow")?;
        }
    }
    report.blocks = report.blocks.saturating_add(1);
    Ok(())
}

fn run_worker(
    ring: PacketRing,
    worker_index: usize,
    cpu: usize,
    start: Instant,
    duration: Duration,
    barrier: Arc<Barrier>,
) -> Result<WorkerReport> {
    pin_current_thread(cpu)?;
    barrier.wait();
    if let Some(wait) = start.checked_duration_since(Instant::now()) {
        std::thread::sleep(wait);
    }
    let mut report = WorkerReport {
        worker_index,
        cpu,
        packets: 0,
        synthetic_test_packets: 0,
        bytes: 0,
        blocks: 0,
        payload_guard: 0,
        ring_statistics: TpacketStatsV3::default(),
        synthetic_epoch_second_counts: BTreeMap::new(),
        latency_samples_us: Vec::with_capacity(16 * 1024),
    };
    let end = start + duration;
    let mut block_index = 0usize;
    while Instant::now() < end {
        let block = unsafe {
            ring.base
                .add(block_index * ring.request.tp_block_size as usize)
        };
        let descriptor = unsafe { &mut *(block.cast::<TpacketBlockDesc>()) };
        let status = unsafe { ptr::read_volatile(&descriptor.hdr.block_status) };
        if status & TP_STATUS_USER == 0 {
            std::hint::spin_loop();
            continue;
        }
        fence(Ordering::Acquire);
        let block_result =
            unsafe { process_block(block, ring.request.tp_block_size as usize, &mut report) };
        fence(Ordering::Release);
        unsafe {
            ptr::write_volatile(&mut descriptor.hdr.block_status, TP_STATUS_KERNEL);
        }
        block_result?;
        block_index = (block_index + 1) % ring.request.tp_block_nr as usize;
    }
    report.ring_statistics = packet_socket_statistics(ring.fd)?;
    Ok(report)
}

fn process_cpu_time() -> Result<Duration> {
    let mut value: libc::timespec = unsafe { zeroed() };
    let status = unsafe { libc::clock_gettime(libc::CLOCK_PROCESS_CPUTIME_ID, &mut value) };
    if status != 0 {
        return Err(std::io::Error::last_os_error()).context("read process CPU clock");
    }
    Ok(Duration::new(value.tv_sec as u64, value.tv_nsec as u32))
}

fn percentiles(mut values: Vec<u64>) -> Percentiles {
    if values.is_empty() {
        return Percentiles {
            samples: 0,
            p50_us: None,
            p99_us: None,
            p999_us: None,
            max_us: None,
        };
    }
    values.sort_unstable();
    let pick = |fraction: f64| {
        let index = ((values.len() - 1) as f64 * fraction).ceil() as usize;
        values[index]
    };
    Percentiles {
        samples: values.len(),
        p50_us: Some(pick(0.50)),
        p99_us: Some(pick(0.99)),
        p999_us: Some(pick(0.999)),
        max_us: values.last().copied(),
    }
}

fn write_json<T: Serialize>(path: &PathBuf, value: &T) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut output = File::create(path).with_context(|| format!("create {}", path.display()))?;
    serde_json::to_writer_pretty(&mut output, value)?;
    output.write_all(b"\n")?;
    Ok(())
}

fn main() -> Result<()> {
    let args = Args::parse();
    validate_args(&args)?;

    let rings = (0..args.worker_cpus.len())
        .map(|_| open_ring(&args))
        .collect::<Result<Vec<_>>>()?;
    let duration = Duration::from_secs(args.duration_s);
    let start = Instant::now() + Duration::from_millis(args.start_delay_ms);
    let barrier = Arc::new(Barrier::new(rings.len() + 1));
    let cpu_started = process_cpu_time()?;
    let handles = rings
        .into_iter()
        .zip(args.worker_cpus.iter().copied())
        .enumerate()
        .map(|(worker_index, (ring, cpu))| {
            let worker_barrier = Arc::clone(&barrier);
            std::thread::spawn(move || {
                run_worker(ring, worker_index, cpu, start, duration, worker_barrier)
            })
        })
        .collect::<Vec<_>>();

    if let Some(path) = &args.ready_file {
        let ready = serde_json::json!({
            "ready": true,
            "interface": args.interface,
            "fanout_mode": args.fanout_mode.label(),
            "fanout_id": args.fanout_id,
            "workers": args.worker_cpus.len(),
            "start_delay_ms": args.start_delay_ms
        });
        write_json(path, &ready)?;
    }
    barrier.wait();
    let reports = handles
        .into_iter()
        .map(|handle| {
            handle
                .join()
                .map_err(|_| anyhow::anyhow!("capture worker panicked"))?
        })
        .collect::<Result<Vec<_>>>()?;
    let elapsed = duration.as_secs_f64();
    let cpu_elapsed = process_cpu_time()?
        .checked_sub(cpu_started)
        .context("process CPU clock moved backwards")?
        .as_secs_f64();

    let packets = reports.iter().map(|report| report.packets).sum::<u64>();
    let synthetic_test_packets = reports
        .iter()
        .map(|report| report.synthetic_test_packets)
        .sum::<u64>();
    let bytes = reports.iter().map(|report| report.bytes).sum::<u64>();
    let statistics_packets = reports
        .iter()
        .map(|report| u64::from(report.ring_statistics.tp_packets))
        .sum::<u64>();
    let drops = reports
        .iter()
        .map(|report| u64::from(report.ring_statistics.tp_drops))
        .sum::<u64>();
    let freeze_count = reports
        .iter()
        .map(|report| u64::from(report.ring_statistics.tp_freeze_q_cnt))
        .sum::<u64>();
    let mut synthetic_epoch_second_counts = BTreeMap::<u64, u64>::new();
    let mut latency_samples = Vec::new();
    for worker in &reports {
        for (epoch_second, value) in &worker.synthetic_epoch_second_counts {
            *synthetic_epoch_second_counts
                .entry(*epoch_second)
                .or_insert(0) += *value;
        }
        let remaining = MAX_LATENCY_SAMPLES.saturating_sub(latency_samples.len());
        latency_samples.extend(worker.latency_samples_us.iter().take(remaining).copied());
    }
    let first_epoch = synthetic_epoch_second_counts.keys().next().copied();
    let last_epoch = synthetic_epoch_second_counts.keys().next_back().copied();
    let full_epoch_counts = synthetic_epoch_second_counts
        .iter()
        .filter_map(|(epoch, count)| match (first_epoch, last_epoch) {
            (Some(first), Some(last)) if *epoch > first && *epoch < last => Some(*count),
            _ => None,
        })
        .collect::<Vec<_>>();
    let synthetic_rx_min_full_epoch_mpps = full_epoch_counts
        .iter()
        .copied()
        .min()
        .map(|count| count as f64 / 1_000_000.0);
    let worker_summaries = reports
        .into_iter()
        .map(|worker| WorkerSummary {
            worker_index: worker.worker_index,
            cpu: worker.cpu,
            packets: worker.packets,
            synthetic_test_packets: worker.synthetic_test_packets,
            bytes: worker.bytes,
            blocks: worker.blocks,
            payload_guard: worker.payload_guard,
            ring_statistics: worker.ring_statistics,
        })
        .collect::<Vec<_>>();
    let report = ProbeReport {
        schema_version: 1,
        scope: "r0_tpacket_v3_fanout_capture_only_raw",
        backend: "tpacket_v3_packet_fanout",
        interface: args.interface,
        fanout_mode: args.fanout_mode.label(),
        fanout_id: args.fanout_id,
        worker_cpus: args.worker_cpus.clone(),
        block_size: args.block_size,
        block_count_per_worker: args.block_count,
        frame_size: args.frame_size,
        ring_memory_bytes: u64::from(args.block_size)
            * u64::from(args.block_count)
            * args.worker_cpus.len() as u64,
        promiscuous_membership: true,
        duration_s: elapsed,
        packets,
        synthetic_test_packets,
        non_test_packets: packets.saturating_sub(synthetic_test_packets),
        bytes,
        achieved_mpps: packets as f64 / elapsed / 1_000_000.0,
        achieved_gbps: bytes as f64 * 8.0 / elapsed / 1_000_000_000.0,
        synthetic_rx_full_epoch_windows: full_epoch_counts.len(),
        synthetic_rx_min_full_epoch_mpps,
        packet_socket_statistics_packets: statistics_packets,
        packet_socket_drops: drops,
        packet_socket_freeze_queue_count: freeze_count,
        process_cpu_cores_average: cpu_elapsed / elapsed,
        latency_sample_stride: LATENCY_SAMPLE_STRIDE,
        latency_timestamp_source: "tpacket_v3_software_packet_timestamp_to_userspace_sample_v1",
        packet_socket_timestamp_to_userspace_latency: percentiles(latency_samples),
        workers: worker_summaries,
        raw_capture_only_observation: true,
        r0_capture_only_qualified: false,
        full_pipeline_qualified: false,
        final_pareto_ingestion_allowed: false,
    };
    write_json(&args.output, &report)?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fanout_values_match_linux_uapi() {
        assert_eq!(FanoutMode::Hash.kernel_value(), 0);
        assert_eq!(FanoutMode::Qm.kernel_value(), 5);
    }

    #[test]
    fn percentile_selection_is_fail_closed_for_empty_input() {
        let empty = percentiles(Vec::new());
        assert_eq!(empty.samples, 0);
        assert_eq!(empty.p99_us, None);
        let values = percentiles(vec![1, 2, 3, 4, 5]);
        assert_eq!(values.p50_us, Some(3));
        assert_eq!(values.p99_us, Some(5));
    }

    #[test]
    fn synthetic_signature_excludes_background_frames() {
        let mut frame = [0u8; 64];
        frame[0..6].copy_from_slice(&[0x02, 0, 0, 0, 0, 1]);
        frame[6..12].copy_from_slice(&[0x02, 0, 0, 0, 0, 2]);
        frame[12..14].copy_from_slice(&[0x08, 0x00]);
        assert!(is_synthetic_test_frame(&frame));
        frame[0] = 0xff;
        assert!(!is_synthetic_test_frame(&frame));
    }
}
