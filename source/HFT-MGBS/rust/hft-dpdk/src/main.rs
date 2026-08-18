use anyhow::{bail, Context, Result};
use clap::{Parser, ValueEnum};
use serde::Serialize;
use std::collections::HashSet;
use std::ffi::{c_char, c_void, CString};
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{mpsc, Arc};
use std::thread;
use std::time::{Duration, Instant};

const UDP_TIMESTAMP_OFFSET: u16 = 42;
const TCP_RSS_DIAGNOSTIC_TIMESTAMP_OFFSET: u16 = 54;
const TEMPLATE_COUNT: usize = 256;
const RATE_HEADROOM_RATIO: f64 = 1.01;
const WORKER_SETUP_WATCHDOG_TIMEOUT: Duration = Duration::from_secs(15);
const WORKER_READY_TIMEOUT: Duration = Duration::from_secs(5);
const RX_DRAIN_QUIET_PERIOD: Duration = Duration::from_millis(200);
const RX_LIFECYCLE_GRACE: Duration = Duration::from_secs(1);
const WORKER_SHUTDOWN_GRACE: Duration = Duration::from_secs(2);
const WORKER_WATCHDOG_EXIT_CODE: i32 = 124;
const ZERO_POLL_HOUSEKEEPING_INTERVAL: u64 = 64;
const REQUESTED_RX_DESCRIPTORS: u16 = 1024;
const REQUESTED_TX_DESCRIPTORS: u16 = 1024;

#[derive(Clone, Copy, Debug, Eq, PartialEq, ValueEnum)]
enum TrafficProfile {
    UdpCompat,
    TcpRssDiagnostic,
}

impl TrafficProfile {
    const fn as_str(self) -> &'static str {
        match self {
            Self::UdpCompat => "udp_compat",
            Self::TcpRssDiagnostic => "tcp_rss_diagnostic",
        }
    }

    const fn port_profile(self) -> u32 {
        match self {
            Self::UdpCompat => 0,
            Self::TcpRssDiagnostic => 1,
        }
    }

    const fn ip_protocol(self) -> u8 {
        match self {
            Self::UdpCompat => 17,
            Self::TcpRssDiagnostic => 6,
        }
    }

    const fn timestamp_offset(self) -> u16 {
        match self {
            Self::UdpCompat => UDP_TIMESTAMP_OFFSET,
            Self::TcpRssDiagnostic => TCP_RSS_DIAGNOSTIC_TIMESTAMP_OFFSET,
        }
    }

    const fn port_configuration(self) -> &'static str {
        match self {
            Self::UdpCompat => "ethdev_udp_rss_request_when_multiqueue",
            Self::TcpRssDiagnostic => "stock_bnx2x_implicit_tcp_rss_mq_none_hf_zero",
        }
    }
}

#[repr(C)]
#[derive(Clone, Copy, Default, Serialize)]
struct DpdkStats {
    ipackets: u64,
    ibytes: u64,
    imissed: u64,
    ierrors: u64,
    rx_nombuf: u64,
    opackets: u64,
    obytes: u64,
    oerrors: u64,
}

extern "C" {
    fn hft_dpdk_eal_init(argc: i32, argv: *mut *mut c_char) -> i32;
    fn hft_dpdk_eal_cleanup() -> i32;
    fn hft_dpdk_thread_register() -> i32;
    fn hft_dpdk_thread_unregister();
    fn hft_dpdk_port_count() -> u16;
    fn hft_dpdk_find_port(name: *const c_char, port_id: *mut u16) -> i32;
    fn hft_dpdk_port_init(
        port_id: u16,
        mempool: *mut c_void,
        rx_desc: u16,
        tx_desc: u16,
        queue_count: u16,
        traffic_profile: u32,
        actual_rx_desc: *mut u16,
        actual_tx_desc: *mut u16,
    ) -> i32;
    fn hft_dpdk_port_mac(port_id: u16, mac: *mut u8) -> i32;
    fn hft_dpdk_port_link(port_id: u16, speed_mbps: *mut u32, up: *mut u8) -> i32;
    fn hft_dpdk_port_stats(port_id: u16, stats: *mut DpdkStats) -> i32;
    fn hft_dpdk_port_stop_close(port_id: u16);
    fn hft_dpdk_mempool_create(
        name: *const c_char,
        count: u32,
        cache_size: u32,
        socket_id: i32,
    ) -> *mut c_void;
    fn hft_dpdk_mempool_counts(mempool: *mut c_void, available: *mut u32, in_use: *mut u32) -> i32;
    fn hft_dpdk_socket_id() -> i32;
    fn hft_dpdk_tsc_hz() -> u64;
    fn hft_dpdk_rdtsc() -> u64;
    fn hft_dpdk_prepare_synthetic_burst(
        mempool: *mut c_void,
        packets: *mut *mut c_void,
        count: u16,
        templates: *const u8,
        template_count: u16,
        frame_size: u16,
        sequence: u64,
        timestamp_cycles: u64,
        timestamp_offset: u16,
    ) -> i32;
    fn hft_dpdk_tx_burst(port_id: u16, queue_id: u16, packets: *mut *mut c_void, count: u16)
        -> u16;
    fn hft_dpdk_rx_burst(
        port_id: u16,
        queue_id: u16,
        packets: *mut *mut c_void,
        capacity: u16,
    ) -> u16;
    fn hft_dpdk_burst_bytes(packets: *mut *mut c_void, count: u16) -> u64;
    fn hft_dpdk_first_timestamp(
        packets: *mut *mut c_void,
        count: u16,
        timestamp_offset: u16,
    ) -> u64;
    fn hft_dpdk_free_burst(packets: *mut *mut c_void, count: u16);
    fn hft_dpdk_free_burst_from(packets: *mut *mut c_void, start: u16, count: u16);
}

#[derive(Debug, Parser)]
struct Args {
    #[arg(long)]
    candidate_id: String,
    #[arg(long)]
    frozen_thresholds_sha256: String,
    #[arg(long)]
    capture_pci: String,
    #[arg(long)]
    replay_pci: String,
    #[arg(long)]
    file_prefix: Option<String>,
    #[arg(long, value_delimiter = ',', default_value = "36")]
    rx_cpus: Vec<usize>,
    #[arg(long, value_delimiter = ',', default_value = "44")]
    tx_cpus: Vec<usize>,
    #[arg(long, default_value_t = 1)]
    queue_count: usize,
    #[arg(long, default_value_t = 0)]
    realtime_priority: i32,
    #[arg(long, default_value_t = 28)]
    main_cpu: usize,
    #[arg(long)]
    duration_s: u64,
    #[arg(long)]
    target_mpps: f64,
    #[arg(long, default_value_t = 256)]
    burst_size: usize,
    #[arg(long, default_value_t = 64)]
    frame_size: usize,
    #[arg(long, value_enum, default_value_t = TrafficProfile::UdpCompat)]
    traffic_profile: TrafficProfile,
    #[arg(long)]
    max_end_to_end_p99_us: f64,
    #[arg(long)]
    max_end_to_end_p999_us: f64,
    #[arg(long)]
    output: PathBuf,
}

#[derive(Serialize)]
struct WorkerReport {
    packets: u64,
    bytes: u64,
    elapsed_s: f64,
    cpu_cores_average: f64,
    min_mpps_1s: Option<f64>,
    full_rate_windows: u64,
    stalls: u64,
    hotpath: HotpathCounters,
    latency_cycles: Vec<u64>,
}

#[derive(Clone, Copy, Default, Serialize)]
struct HotpathCounters {
    prepare_calls: u64,
    alloc_fail: u64,
    tx_calls: u64,
    tx_zero: u64,
    tx_partial: u64,
    tx_full: u64,
    tx_successful_bursts: u64,
    rx_polls: u64,
    rx_nonzero: u64,
    rx_zero: u64,
}

#[derive(Clone, Copy, Serialize)]
struct PortDescriptorConfiguration {
    port_id: u16,
    requested_rx: u16,
    actual_rx: u16,
    requested_tx: u16,
    actual_tx: u16,
}

#[derive(Clone, Copy, Serialize)]
struct MempoolSnapshot {
    available: u32,
    in_use: u32,
    observed_total: u64,
}

struct TxConfig {
    port: u16,
    queue_id: u16,
    mempool: usize,
    cpu: usize,
    realtime_priority: i32,
    duration: Duration,
    target_mpps: f64,
    burst_size: usize,
    frame_size: usize,
    timestamp_offset: u16,
    templates: Vec<u8>,
}

struct RxConfig {
    port: u16,
    queue_id: u16,
    cpu: usize,
    realtime_priority: i32,
    burst_size: usize,
    duration: Duration,
    timestamp_offset: u16,
}

type ReadySignal = std::result::Result<(), String>;

#[derive(Serialize)]
struct RunReport {
    schema_version: u32,
    scope: &'static str,
    backend: &'static str,
    candidate_id: String,
    frozen_thresholds_sha256: String,
    capture_pci: String,
    replay_pci: String,
    capture_port_id: u16,
    replay_port_id: u16,
    capture_mac: String,
    replay_mac: String,
    queue_count: usize,
    realtime_priority: i32,
    main_cpu: usize,
    rx_cpus: Vec<usize>,
    tx_cpus: Vec<usize>,
    traffic_profile: &'static str,
    synthetic_flow_count: usize,
    ip_protocol: u8,
    timestamp_offset_bytes: u16,
    port_configuration: &'static str,
    target_mpps: f64,
    frame_size_bytes: usize,
    burst_size: usize,
    descriptor_configuration: Vec<PortDescriptorConfiguration>,
    mempool_configured_capacity: u32,
    mempool_before: MempoolSnapshot,
    mempool_after: MempoolSnapshot,
    max_end_to_end_p99_us: f64,
    max_end_to_end_p999_us: f64,
    duration_s: f64,
    offered_packets: u64,
    received_packets: u64,
    offered_received_gap: i128,
    observed_tx_mpps_min_1s: Option<f64>,
    observed_rx_mpps_min_1s: Option<f64>,
    rate_window_alignment: &'static str,
    tx_rate_full_windows: u64,
    rx_rate_full_windows: u64,
    achieved_tx_mpps: f64,
    achieved_rx_mpps: f64,
    capture_stats_delta: DpdkStats,
    replay_stats_delta: DpdkStats,
    latency_sample_stride: u64,
    latency_timestamp_source: &'static str,
    end_to_end_latency_us: Percentiles,
    rx_cpu_cores_average: f64,
    tx_cpu_cores_average: f64,
    rx_stalls: u64,
    tx_stalls: u64,
    rx_hotpath_counters: Vec<HotpathCounters>,
    tx_hotpath_counters: Vec<HotpathCounters>,
    rx_queue_packets: Vec<u64>,
    tx_queue_packets: Vec<u64>,
    data_plane_qualified: bool,
    resource_gate_evaluated: bool,
    r0_capture_only_qualified: bool,
    hard_gate_errors: Vec<&'static str>,
    full_pipeline_qualified: bool,
    final_pareto_ingestion_allowed: bool,
}

struct EalGuard;

impl Drop for EalGuard {
    fn drop(&mut self) {
        unsafe {
            let _ = hft_dpdk_eal_cleanup();
        }
    }
}

struct DpdkThreadGuard;

impl Drop for DpdkThreadGuard {
    fn drop(&mut self) {
        unsafe {
            hft_dpdk_thread_unregister();
        }
    }
}

struct PortGuard {
    ports: Vec<u16>,
}

impl Drop for PortGuard {
    fn drop(&mut self) {
        for port in self.ports.iter().rev() {
            unsafe {
                hft_dpdk_port_stop_close(*port);
            }
        }
    }
}

struct TxCompletionGuard {
    remaining: Arc<AtomicUsize>,
    done: Arc<AtomicBool>,
}

impl TxCompletionGuard {
    fn new(remaining: Arc<AtomicUsize>, done: Arc<AtomicBool>) -> Self {
        Self { remaining, done }
    }
}

impl Drop for TxCompletionGuard {
    fn drop(&mut self) {
        let previous = self
            .remaining
            .fetch_update(Ordering::AcqRel, Ordering::Acquire, |value| {
                value.checked_sub(1)
            });
        if matches!(previous, Ok(1) | Err(0)) {
            self.done.store(true, Ordering::Release);
        }
    }
}

#[derive(Debug, Clone, Copy)]
enum WatchdogCommand {
    Rearm(Instant),
    Disarm,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum WatchdogOutcome {
    Disarmed,
    Expired,
}

fn wait_for_watchdog(
    receiver: mpsc::Receiver<WatchdogCommand>,
    mut deadline: Instant,
) -> WatchdogOutcome {
    loop {
        let timeout = deadline.saturating_duration_since(Instant::now());
        match receiver.recv_timeout(timeout) {
            Ok(WatchdogCommand::Rearm(new_deadline)) => deadline = new_deadline,
            Ok(WatchdogCommand::Disarm) | Err(mpsc::RecvTimeoutError::Disconnected) => {
                return WatchdogOutcome::Disarmed;
            }
            Err(mpsc::RecvTimeoutError::Timeout) => return WatchdogOutcome::Expired,
        }
    }
}

struct WorkerWatchdog {
    sender: Option<mpsc::Sender<WatchdogCommand>>,
    handle: Option<thread::JoinHandle<()>>,
}

impl WorkerWatchdog {
    fn spawn(initial_deadline: Instant) -> Result<Self> {
        let (sender, receiver) = mpsc::channel();
        let handle = thread::Builder::new()
            .name("hft-dpdk-lifecycle-watchdog".to_owned())
            .spawn(move || {
                if wait_for_watchdog(receiver, initial_deadline) == WatchdogOutcome::Expired {
                    eprintln!(
                        "DPDK lifecycle watchdog expired; terminating with exit code {}",
                        WORKER_WATCHDOG_EXIT_CODE
                    );
                    std::process::exit(WORKER_WATCHDOG_EXIT_CODE);
                }
            })
            .context("spawn DPDK lifecycle watchdog")?;
        Ok(Self {
            sender: Some(sender),
            handle: Some(handle),
        })
    }

    fn rearm(&self, deadline: Instant) -> Result<()> {
        self.sender
            .as_ref()
            .context("DPDK lifecycle watchdog sender is unavailable")?
            .send(WatchdogCommand::Rearm(deadline))
            .context("rearm DPDK lifecycle watchdog")
    }
}

impl Drop for WorkerWatchdog {
    fn drop(&mut self) {
        if let Some(sender) = self.sender.take() {
            let _ = sender.send(WatchdogCommand::Disarm);
        }
        if let Some(handle) = self.handle.take() {
            let _ = handle.join();
        }
    }
}

#[derive(Default, Serialize)]
struct Percentiles {
    samples: usize,
    p50: Option<f64>,
    p99: Option<f64>,
    p999: Option<f64>,
    max: Option<f64>,
}

fn validate_realtime_priority(priority: i32) -> Result<()> {
    if !(0..=20).contains(&priority) {
        bail!("realtime priority must be in 0..=20");
    }
    Ok(())
}

fn configure_current_thread(cpu: usize, realtime_priority: i32) -> Result<()> {
    validate_realtime_priority(realtime_priority)?;
    if cpu >= libc::CPU_SETSIZE as usize {
        bail!("CPU {} exceeds CPU_SETSIZE", cpu);
    }
    let mut set: libc::cpu_set_t = unsafe { std::mem::zeroed() };
    unsafe {
        libc::CPU_ZERO(&mut set);
        libc::CPU_SET(cpu, &mut set);
    }
    let status = unsafe {
        libc::pthread_setaffinity_np(
            libc::pthread_self(),
            std::mem::size_of::<libc::cpu_set_t>(),
            &set,
        )
    };
    if status != 0 {
        return Err(std::io::Error::from_raw_os_error(status))
            .with_context(|| format!("pin DPDK worker to CPU {cpu}"));
    }
    if realtime_priority > 0 {
        let parameters = libc::sched_param {
            sched_priority: realtime_priority,
        };
        let status = unsafe {
            libc::pthread_setschedparam(libc::pthread_self(), libc::SCHED_FIFO, &parameters)
        };
        if status != 0 {
            return Err(std::io::Error::from_raw_os_error(status)).with_context(|| {
                format!("set DPDK worker on CPU {cpu} to SCHED_FIFO priority {realtime_priority}")
            });
        }
    }
    Ok(())
}

fn prepare_dpdk_worker(
    cpu: usize,
    realtime_priority: i32,
    role: &str,
    ready: &mpsc::Sender<ReadySignal>,
) -> Result<()> {
    let setup_result = (|| -> Result<()> {
        configure_current_thread(cpu, realtime_priority)?;
        if unsafe { hft_dpdk_thread_register() } != 0 {
            bail!("rte_thread_register failed");
        }
        Ok(())
    })();
    if let Err(error) = setup_result {
        let message = format!(
            "{role} worker setup failed on CPU {cpu} with realtime priority \
             {realtime_priority}: {error:#}"
        );
        let _ = ready.send(Err(message.clone()));
        bail!(message);
    }
    if ready.send(Ok(())).is_err() {
        unsafe { hft_dpdk_thread_unregister() };
        bail!("{role} worker ready receiver closed");
    }
    Ok(())
}

fn thread_cpu_time() -> Result<Duration> {
    let mut value: libc::timespec = unsafe { std::mem::zeroed() };
    let status = unsafe { libc::clock_gettime(libc::CLOCK_THREAD_CPUTIME_ID, &mut value) };
    if status != 0 {
        return Err(std::io::Error::last_os_error()).context("read thread CPU clock");
    }
    Ok(Duration::new(value.tv_sec as u64, value.tv_nsec as u32))
}

fn internet_checksum(bytes: &[u8]) -> u16 {
    let mut sum = 0u32;
    let mut chunks = bytes.chunks_exact(2);
    for chunk in &mut chunks {
        sum += u32::from(u16::from_be_bytes([chunk[0], chunk[1]]));
    }
    if let Some(last) = chunks.remainder().first() {
        sum += u32::from(*last) << 8;
    }
    while sum >> 16 != 0 {
        sum = (sum & 0xffff) + (sum >> 16);
    }
    !(sum as u16)
}

fn ipv4_transport_checksum(
    source: u32,
    destination: u32,
    protocol: u8,
    segment: &[u8],
) -> Result<u16> {
    let segment_length =
        u16::try_from(segment.len()).context("IPv4 transport segment too large")?;
    let mut pseudo_header = Vec::with_capacity(12 + segment.len());
    pseudo_header.extend_from_slice(&source.to_be_bytes());
    pseudo_header.extend_from_slice(&destination.to_be_bytes());
    pseudo_header.push(0);
    pseudo_header.push(protocol);
    pseudo_header.extend_from_slice(&segment_length.to_be_bytes());
    pseudo_header.extend_from_slice(segment);
    Ok(internet_checksum(&pseudo_header))
}

fn synthetic_frame(
    traffic_profile: TrafficProfile,
    frame_size: usize,
    flow_id: u32,
    destination_mac: [u8; 6],
    source_mac: [u8; 6],
) -> Result<Vec<u8>> {
    if !(64..=1500).contains(&frame_size) {
        bail!("frame size must be in 64..=1500");
    }
    let mut frame = vec![0u8; frame_size];
    frame[0..6].copy_from_slice(&destination_mac);
    frame[6..12].copy_from_slice(&source_mac);
    frame[12..14].copy_from_slice(&0x0800u16.to_be_bytes());
    let ip = 14usize;
    frame[ip] = 0x45;
    let ip_total_length = match traffic_profile {
        TrafficProfile::UdpCompat => u16::try_from(frame_size - ip)?,
        TrafficProfile::TcpRssDiagnostic => {
            if frame_size != 64 {
                bail!("TCP RSS diagnostic profile requires an exact 64-byte frame");
            }
            40
        }
    };
    frame[ip + 2..ip + 4].copy_from_slice(&ip_total_length.to_be_bytes());
    frame[ip + 4..ip + 6].copy_from_slice(&(flow_id as u16).to_be_bytes());
    frame[ip + 6..ip + 8].copy_from_slice(&0x4000u16.to_be_bytes());
    frame[ip + 8] = 64;
    frame[ip + 9] = traffic_profile.ip_protocol();
    let source = 0x0a00_0001u32.wrapping_add(flow_id & 0xffff);
    let destination = 0x0a01_0001u32.wrapping_add(flow_id.rotate_left(7) & 0xffff);
    frame[ip + 12..ip + 16].copy_from_slice(&source.to_be_bytes());
    frame[ip + 16..ip + 20].copy_from_slice(&destination.to_be_bytes());
    let checksum = internet_checksum(&frame[ip..ip + 20]);
    frame[ip + 10..ip + 12].copy_from_slice(&checksum.to_be_bytes());
    let transport = ip + 20;
    let source_port = (1024 + flow_id) as u16;
    let destination_port = (20_000 + flow_id.rotate_left(3)) as u16;
    frame[transport..transport + 2].copy_from_slice(&source_port.to_be_bytes());
    frame[transport + 2..transport + 4].copy_from_slice(&destination_port.to_be_bytes());
    match traffic_profile {
        TrafficProfile::UdpCompat => {
            frame[transport + 4..transport + 6]
                .copy_from_slice(&((frame_size - transport) as u16).to_be_bytes());
        }
        TrafficProfile::TcpRssDiagnostic => {
            let tcp_header_length = 20usize;
            frame[transport + 4..transport + 8].copy_from_slice(&flow_id.to_be_bytes());
            frame[transport + 12] = 5 << 4;
            frame[transport + 13] = 0x02;
            frame[transport + 14..transport + 16].copy_from_slice(&64_240u16.to_be_bytes());
            let tcp_checksum = ipv4_transport_checksum(
                source,
                destination,
                traffic_profile.ip_protocol(),
                &frame[transport..transport + tcp_header_length],
            )?;
            frame[transport + 16..transport + 18].copy_from_slice(&tcp_checksum.to_be_bytes());
        }
    }
    Ok(frame)
}

fn build_templates(
    traffic_profile: TrafficProfile,
    frame_size: usize,
    destination_mac: [u8; 6],
    source_mac: [u8; 6],
) -> Result<Vec<u8>> {
    let mut templates = Vec::with_capacity(TEMPLATE_COUNT * frame_size);
    for index in 0..TEMPLATE_COUNT {
        templates.extend_from_slice(&synthetic_frame(
            traffic_profile,
            frame_size,
            index as u32,
            destination_mac,
            source_mac,
        )?);
    }
    Ok(templates)
}

fn port_mac(port: u16) -> Result<[u8; 6]> {
    let mut mac = [0u8; 6];
    let status = unsafe { hft_dpdk_port_mac(port, mac.as_mut_ptr()) };
    if status != 0 {
        bail!("read DPDK port {port} MAC failed: {status}");
    }
    Ok(mac)
}

fn format_mac(mac: [u8; 6]) -> String {
    format!(
        "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}",
        mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]
    )
}

fn initialize_eal(args: &Args) -> Result<()> {
    let prefix = args
        .file_prefix
        .clone()
        .unwrap_or_else(|| format!("hft-{}", std::process::id()));
    validate_file_prefix(&prefix)?;
    let values = vec![
        "hft-dpdk-r0".to_owned(),
        "-l".to_owned(),
        args.main_cpu.to_string(),
        "-n".to_owned(),
        "4".to_owned(),
        "--main-lcore".to_owned(),
        args.main_cpu.to_string(),
        "--file-prefix".to_owned(),
        prefix,
        "--huge-unlink=always".to_owned(),
        "--iova-mode".to_owned(),
        "pa".to_owned(),
        "-a".to_owned(),
        args.capture_pci.clone(),
        "-a".to_owned(),
        args.replay_pci.clone(),
    ];
    let mut strings = values
        .iter()
        .map(|value| CString::new(value.as_str()).context("EAL argument contains NUL"))
        .collect::<Result<Vec<_>>>()?;
    let mut pointers = strings
        .iter_mut()
        .map(|value| value.as_ptr() as *mut c_char)
        .collect::<Vec<_>>();
    let status = unsafe { hft_dpdk_eal_init(pointers.len() as i32, pointers.as_mut_ptr()) };
    if status < 0 {
        bail!("rte_eal_init failed with {}", status);
    }
    Ok(())
}

fn validate_file_prefix(value: &str) -> Result<()> {
    if value.is_empty()
        || value.len() > 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-' || byte == b'_')
    {
        bail!("file prefix must contain 1..=64 ASCII letters, digits, '-' or '_'");
    }
    Ok(())
}

fn validate_traffic_profile(
    traffic_profile: TrafficProfile,
    queue_count: usize,
    frame_size: usize,
) -> Result<()> {
    if traffic_profile == TrafficProfile::TcpRssDiagnostic {
        if queue_count < 2 {
            bail!("TCP RSS diagnostic profile requires at least two symmetric queues");
        }
        if frame_size != 64 {
            bail!("TCP RSS diagnostic profile requires an exact 64-byte frame");
        }
    }
    let timestamp_end = usize::from(traffic_profile.timestamp_offset())
        .checked_add(std::mem::size_of::<u64>())
        .context("timestamp offset overflow")?;
    if timestamp_end > frame_size {
        bail!("traffic profile timestamp does not fit in the frame");
    }
    Ok(())
}

fn backend_name(traffic_profile: TrafficProfile, queue_count: usize) -> &'static str {
    match (traffic_profile, queue_count) {
        (TrafficProfile::UdpCompat, 1) => "dpdk_bnx2x_single_queue",
        (TrafficProfile::UdpCompat, _) => "dpdk_bnx2x_multiqueue_experimental",
        (TrafficProfile::TcpRssDiagnostic, _) => "dpdk_bnx2x_stock_tcp_rss_diagnostic",
    }
}

fn find_port(pci: &str) -> Result<u16> {
    let name = CString::new(pci).context("PCI address contains NUL")?;
    let mut port = u16::MAX;
    let status = unsafe { hft_dpdk_find_port(name.as_ptr(), &mut port) };
    if status != 0 {
        bail!("DPDK port {} not found: {}", pci, status);
    }
    Ok(port)
}

fn wait_link(port: u16) -> Result<u32> {
    let started = Instant::now();
    loop {
        let mut speed = 0u32;
        let mut up = 0u8;
        let status = unsafe { hft_dpdk_port_link(port, &mut speed, &mut up) };
        if status != 0 {
            bail!("query DPDK port {} link failed: {}", port, status);
        }
        if up == 1 && speed == 10_000 {
            return Ok(speed);
        }
        if started.elapsed() >= Duration::from_secs(5) {
            bail!(
                "DPDK port {} is not 10GbE UP (speed={}, up={})",
                port,
                speed,
                up
            );
        }
        thread::sleep(Duration::from_millis(100));
    }
}

fn read_stats(port: u16) -> Result<DpdkStats> {
    let mut stats = DpdkStats::default();
    let status = unsafe { hft_dpdk_port_stats(port, &mut stats) };
    if status != 0 {
        bail!("read DPDK port {} stats failed: {}", port, status);
    }
    Ok(stats)
}

fn read_mempool_snapshot(mempool: *mut c_void) -> Result<MempoolSnapshot> {
    let mut available = 0u32;
    let mut in_use = 0u32;
    let status = unsafe { hft_dpdk_mempool_counts(mempool, &mut available, &mut in_use) };
    if status != 0 {
        bail!("read DPDK mempool counters failed: {status}");
    }
    Ok(MempoolSnapshot {
        available,
        in_use,
        observed_total: u64::from(available) + u64::from(in_use),
    })
}

fn stats_delta(after: DpdkStats, before: DpdkStats) -> DpdkStats {
    DpdkStats {
        ipackets: after.ipackets.saturating_sub(before.ipackets),
        ibytes: after.ibytes.saturating_sub(before.ibytes),
        imissed: after.imissed.saturating_sub(before.imissed),
        ierrors: after.ierrors.saturating_sub(before.ierrors),
        rx_nombuf: after.rx_nombuf.saturating_sub(before.rx_nombuf),
        opackets: after.opackets.saturating_sub(before.opackets),
        obytes: after.obytes.saturating_sub(before.obytes),
        oerrors: after.oerrors.saturating_sub(before.oerrors),
    }
}

fn wait_for_start_epoch(started: Instant) {
    loop {
        let now = Instant::now();
        if now >= started {
            break;
        }
        let remaining = started.duration_since(now);
        if remaining > Duration::from_micros(100) {
            thread::sleep(remaining - Duration::from_micros(50));
        } else {
            std::hint::spin_loop();
        }
    }
}

fn lifecycle_deadline(started: Instant, duration: Duration, grace: Duration) -> Result<Instant> {
    started
        .checked_add(duration)
        .and_then(|deadline| deadline.checked_add(grace))
        .context("DPDK lifecycle deadline overflow")
}

fn zero_poll_requires_housekeeping(consecutive_zero_polls: u64) -> bool {
    consecutive_zero_polls != 0
        && consecutive_zero_polls.is_multiple_of(ZERO_POLL_HOUSEKEEPING_INTERVAL)
}

fn close_full_rate_windows(
    started: Instant,
    duration: Duration,
    full_windows: &mut u64,
    window_packets: &mut u64,
    min_mpps: &mut Option<f64>,
) {
    let elapsed = started.elapsed();
    while *full_windows < duration.as_secs()
        && elapsed >= Duration::from_secs((*full_windows).saturating_add(1))
    {
        let mpps = *window_packets as f64 / 1_000_000.0;
        *min_mpps = Some(min_mpps.map_or(mpps, |current| current.min(mpps)));
        *window_packets = 0;
        *full_windows = (*full_windows).saturating_add(1);
    }
}

fn run_tx(
    config: TxConfig,
    start: mpsc::Receiver<Instant>,
    ready: mpsc::Sender<ReadySignal>,
) -> Result<WorkerReport> {
    let TxConfig {
        port,
        queue_id,
        mempool,
        cpu,
        realtime_priority,
        duration,
        target_mpps,
        burst_size,
        frame_size,
        timestamp_offset,
        templates,
    } = config;
    prepare_dpdk_worker(cpu, realtime_priority, "TX", &ready)?;
    let _thread_guard = DpdkThreadGuard;
    let started = start.recv()?;
    wait_for_start_epoch(started);
    let cpu_started = thread_cpu_time()?;
    let mut packets = vec![std::ptr::null_mut::<c_void>(); burst_size];
    let mut total_packets = 0u64;
    let mut total_bytes = 0u64;
    let mut hotpath = HotpathCounters::default();
    let mut window_packets = 0u64;
    let mut full_rate_windows = 0u64;
    let mut min_mpps: Option<f64> = None;
    while started.elapsed() < duration {
        let timestamp = unsafe { hft_dpdk_rdtsc() };
        hotpath.prepare_calls = hotpath.prepare_calls.saturating_add(1);
        let status = unsafe {
            hft_dpdk_prepare_synthetic_burst(
                mempool as *mut c_void,
                packets.as_mut_ptr(),
                burst_size as u16,
                templates.as_ptr(),
                TEMPLATE_COUNT as u16,
                frame_size as u16,
                total_packets,
                timestamp,
                timestamp_offset,
            )
        };
        if status != 0 {
            if status != -libc::ENOBUFS {
                bail!(
                    "prepare DPDK synthetic burst on TX queue {} failed: {}",
                    queue_id,
                    status
                );
            }
            hotpath.alloc_fail = hotpath.alloc_fail.saturating_add(1);
            close_full_rate_windows(
                started,
                duration,
                &mut full_rate_windows,
                &mut window_packets,
                &mut min_mpps,
            );
            std::hint::spin_loop();
            continue;
        }
        let mut sent = 0usize;
        let mut consecutive_zero_polls = 0u64;
        let mut deadline_reached = false;
        while sent < burst_size {
            let remaining = burst_size - sent;
            hotpath.tx_calls = hotpath.tx_calls.saturating_add(1);
            let count = unsafe {
                hft_dpdk_tx_burst(
                    port,
                    queue_id,
                    packets[sent..].as_mut_ptr(),
                    remaining as u16,
                )
            } as usize;
            if count == 0 {
                hotpath.tx_zero = hotpath.tx_zero.saturating_add(1);
                consecutive_zero_polls = consecutive_zero_polls.saturating_add(1);
                if zero_poll_requires_housekeeping(consecutive_zero_polls) {
                    close_full_rate_windows(
                        started,
                        duration,
                        &mut full_rate_windows,
                        &mut window_packets,
                        &mut min_mpps,
                    );
                    if started.elapsed() >= duration {
                        deadline_reached = true;
                        break;
                    }
                }
                std::hint::spin_loop();
                continue;
            }
            consecutive_zero_polls = 0;
            if count < remaining {
                hotpath.tx_partial = hotpath.tx_partial.saturating_add(1);
            } else {
                hotpath.tx_full = hotpath.tx_full.saturating_add(1);
            }
            sent += count;
            close_full_rate_windows(
                started,
                duration,
                &mut full_rate_windows,
                &mut window_packets,
                &mut min_mpps,
            );
            total_packets = total_packets.saturating_add(count as u64);
            total_bytes = total_bytes.saturating_add((count * frame_size) as u64);
            window_packets = window_packets.saturating_add(count as u64);
            if started.elapsed() >= duration {
                deadline_reached = true;
                break;
            }
        }
        if sent == burst_size {
            hotpath.tx_successful_bursts = hotpath.tx_successful_bursts.saturating_add(1);
        }
        if sent < burst_size {
            unsafe {
                hft_dpdk_free_burst_from(packets.as_mut_ptr(), sent as u16, burst_size as u16)
            };
        }
        if deadline_reached {
            break;
        }
        let target_elapsed =
            total_packets as f64 / (target_mpps * 1_000_000.0 * RATE_HEADROOM_RATIO);
        let actual_elapsed = started.elapsed().as_secs_f64();
        if target_elapsed > actual_elapsed {
            let remaining = target_elapsed - actual_elapsed;
            if remaining > 0.000_050 {
                thread::sleep(Duration::from_secs_f64(remaining - 0.000_025));
            } else {
                std::hint::spin_loop();
            }
        }
        close_full_rate_windows(
            started,
            duration,
            &mut full_rate_windows,
            &mut window_packets,
            &mut min_mpps,
        );
    }
    close_full_rate_windows(
        started,
        duration,
        &mut full_rate_windows,
        &mut window_packets,
        &mut min_mpps,
    );
    let elapsed_s = started.elapsed().as_secs_f64();
    let cpu_seconds = thread_cpu_time()?
        .checked_sub(cpu_started)
        .context("TX CPU clock moved backwards")?
        .as_secs_f64();
    Ok(WorkerReport {
        packets: total_packets,
        bytes: total_bytes,
        elapsed_s,
        cpu_cores_average: cpu_seconds / elapsed_s,
        min_mpps_1s: min_mpps,
        full_rate_windows,
        stalls: hotpath.alloc_fail.saturating_add(hotpath.tx_zero),
        hotpath,
        latency_cycles: Vec::new(),
    })
}

fn run_rx(
    config: RxConfig,
    start: mpsc::Receiver<Instant>,
    ready: mpsc::Sender<ReadySignal>,
    done: Arc<AtomicBool>,
) -> Result<WorkerReport> {
    let RxConfig {
        port,
        queue_id,
        cpu,
        realtime_priority,
        burst_size,
        duration,
        timestamp_offset,
    } = config;
    prepare_dpdk_worker(cpu, realtime_priority, "RX", &ready)?;
    let _thread_guard = DpdkThreadGuard;
    let started = start.recv()?;
    wait_for_start_epoch(started);
    let lifecycle_deadline = lifecycle_deadline(started, duration, RX_LIFECYCLE_GRACE)?;
    let cpu_started = thread_cpu_time()?;
    let mut packets = vec![std::ptr::null_mut::<c_void>(); burst_size];
    let mut total_packets = 0u64;
    let mut total_bytes = 0u64;
    let mut hotpath = HotpathCounters::default();
    let mut latency_cycles = Vec::with_capacity(262_144);
    let mut next_sample = 0u64;
    let mut last_packet = Instant::now();
    let mut window_packets = 0u64;
    let mut full_rate_windows = 0u64;
    let mut min_mpps: Option<f64> = None;
    let mut consecutive_zero_polls = 0u64;
    loop {
        hotpath.rx_polls = hotpath.rx_polls.saturating_add(1);
        let count =
            unsafe { hft_dpdk_rx_burst(port, queue_id, packets.as_mut_ptr(), burst_size as u16) }
                as usize;
        if count == 0 {
            hotpath.rx_zero = hotpath.rx_zero.saturating_add(1);
            consecutive_zero_polls = consecutive_zero_polls.saturating_add(1);
            if !zero_poll_requires_housekeeping(consecutive_zero_polls) {
                std::hint::spin_loop();
                continue;
            }
            let now = Instant::now();
            if now >= lifecycle_deadline {
                bail!(
                    "RX queue {} exceeded its lifecycle deadline while waiting for TX completion \
                     (tx_done={})",
                    queue_id,
                    done.load(Ordering::Acquire)
                );
            }
            close_full_rate_windows(
                started,
                duration,
                &mut full_rate_windows,
                &mut window_packets,
                &mut min_mpps,
            );
            if done.load(Ordering::Acquire) && last_packet.elapsed() >= RX_DRAIN_QUIET_PERIOD {
                break;
            }
            std::hint::spin_loop();
            continue;
        }
        hotpath.rx_nonzero = hotpath.rx_nonzero.saturating_add(1);
        consecutive_zero_polls = 0;
        last_packet = Instant::now();
        close_full_rate_windows(
            started,
            duration,
            &mut full_rate_windows,
            &mut window_packets,
            &mut min_mpps,
        );
        let bytes = unsafe { hft_dpdk_burst_bytes(packets.as_mut_ptr(), count as u16) };
        if total_packets >= next_sample {
            let sent = unsafe {
                hft_dpdk_first_timestamp(packets.as_mut_ptr(), count as u16, timestamp_offset)
            };
            let now = unsafe { hft_dpdk_rdtsc() };
            if sent > 0 && now >= sent {
                latency_cycles.push(now - sent);
            }
            next_sample = total_packets.saturating_add(1024);
        }
        unsafe { hft_dpdk_free_burst(packets.as_mut_ptr(), count as u16) };
        total_packets = total_packets.saturating_add(count as u64);
        total_bytes = total_bytes.saturating_add(bytes);
        window_packets = window_packets.saturating_add(count as u64);
        if Instant::now() >= lifecycle_deadline {
            bail!(
                "RX queue {} exceeded its lifecycle deadline after receiving a burst \
                 (tx_done={})",
                queue_id,
                done.load(Ordering::Acquire)
            );
        }
    }
    close_full_rate_windows(
        started,
        duration,
        &mut full_rate_windows,
        &mut window_packets,
        &mut min_mpps,
    );
    let elapsed_s = started.elapsed().as_secs_f64();
    let cpu_seconds = thread_cpu_time()?
        .checked_sub(cpu_started)
        .context("RX CPU clock moved backwards")?
        .as_secs_f64();
    Ok(WorkerReport {
        packets: total_packets,
        bytes: total_bytes,
        elapsed_s,
        cpu_cores_average: cpu_seconds / elapsed_s,
        min_mpps_1s: min_mpps,
        full_rate_windows,
        stalls: hotpath.rx_zero,
        hotpath,
        latency_cycles,
    })
}

fn join_workers(
    handles: Vec<thread::JoinHandle<Result<WorkerReport>>>,
    role: &str,
) -> Result<Vec<WorkerReport>> {
    let mut reports = Vec::with_capacity(handles.len());
    let mut first_failure = None;
    for handle in handles {
        match handle.join() {
            Ok(Ok(report)) => reports.push(report),
            Ok(Err(error)) if first_failure.is_none() => {
                first_failure = Some(format!("{role} worker failed: {error:#}"));
            }
            Err(_) if first_failure.is_none() => {
                first_failure = Some(format!("{role} worker panicked"));
            }
            _ => {}
        }
    }
    if let Some(failure) = first_failure {
        bail!("{failure}");
    }
    Ok(reports)
}

fn aggregate_min_mpps(reports: &[WorkerReport]) -> Option<f64> {
    reports.iter().try_fold(0.0, |sum, report| {
        report.min_mpps_1s.map(|value| sum + value)
    })
}

fn aggregate_full_rate_windows(reports: &[WorkerReport]) -> u64 {
    reports
        .iter()
        .map(|report| report.full_rate_windows)
        .min()
        .unwrap_or(0)
}

fn percentile(values: &[f64], quantile: f64) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let index = ((values.len() - 1) as f64 * quantile).ceil() as usize;
    values.get(index).copied()
}

fn latency_percentiles(cycles: &[u64], tsc_hz: u64) -> Percentiles {
    if cycles.is_empty() || tsc_hz == 0 {
        return Percentiles::default();
    }
    let mut values = cycles
        .iter()
        .map(|cycles| *cycles as f64 * 1_000_000.0 / tsc_hz as f64)
        .collect::<Vec<_>>();
    values.sort_by(f64::total_cmp);
    Percentiles {
        samples: values.len(),
        p50: percentile(&values, 0.50),
        p99: percentile(&values, 0.99),
        p999: percentile(&values, 0.999),
        max: values.last().copied(),
    }
}

#[allow(clippy::too_many_arguments)]
fn qualification_errors(
    target_mpps: f64,
    observed_tx_mpps_min_1s: Option<f64>,
    observed_rx_mpps_min_1s: Option<f64>,
    tx_rate_full_windows: u64,
    rx_rate_full_windows: u64,
    required_rate_full_windows: u64,
    gap: i128,
    capture_delta: DpdkStats,
    replay_delta: DpdkStats,
    rx_queue_packets: &[u64],
    latency: &Percentiles,
    max_end_to_end_p99_us: f64,
    max_end_to_end_p999_us: f64,
) -> Vec<&'static str> {
    let mut errors = Vec::new();
    if observed_tx_mpps_min_1s.is_none_or(|value| value < target_mpps) {
        errors.push("tx_target_load");
    }
    if observed_rx_mpps_min_1s.is_none_or(|value| value < target_mpps) {
        errors.push("rx_target_load");
    }
    if tx_rate_full_windows < required_rate_full_windows
        || rx_rate_full_windows < required_rate_full_windows
    {
        errors.push("rate_window_evidence");
    }
    if gap != 0 {
        errors.push("offered_received_mismatch");
    }
    if capture_delta.imissed != 0 || capture_delta.ierrors != 0 || capture_delta.rx_nombuf != 0 {
        errors.push("capture_drop");
    }
    if replay_delta.oerrors != 0 {
        errors.push("replay_tx_error");
    }
    if rx_queue_packets.contains(&0) {
        errors.push("rss_queue_coverage");
    }
    if latency
        .p99
        .is_none_or(|value| value > max_end_to_end_p99_us)
    {
        errors.push("end_to_end_p99");
    }
    if latency
        .p999
        .is_none_or(|value| value > max_end_to_end_p999_us)
    {
        errors.push("end_to_end_p999");
    }
    errors
}

fn main() -> Result<()> {
    let args = Args::parse();
    if args.candidate_id.is_empty()
        || !args
            .candidate_id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'_' | b'-' | b'.'))
    {
        bail!("candidate ID must use only ASCII letters, digits, dot, dash or underscore");
    }
    if args.frozen_thresholds_sha256.len() != 64
        || !args
            .frozen_thresholds_sha256
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit())
    {
        bail!("frozen thresholds SHA-256 must contain exactly 64 hexadecimal characters");
    }
    if args.duration_s == 0 {
        bail!("duration must be positive");
    }
    if !args.target_mpps.is_finite() || args.target_mpps <= 0.0 {
        bail!("target Mpps must be finite and positive");
    }
    if args.burst_size == 0 || args.burst_size > 1024 {
        bail!("burst size must be in 1..=1024");
    }
    if !(64..=1500).contains(&args.frame_size) {
        bail!("frame size must be in 64..=1500");
    }
    if !args.max_end_to_end_p99_us.is_finite() || args.max_end_to_end_p99_us <= 0.0 {
        bail!("maximum end-to-end P99 must be finite and positive");
    }
    if !args.max_end_to_end_p999_us.is_finite() || args.max_end_to_end_p999_us <= 0.0 {
        bail!("maximum end-to-end P999 must be finite and positive");
    }
    if args.capture_pci == args.replay_pci {
        bail!("capture and replay PCI devices must be distinct");
    }
    if args.queue_count == 0 || args.queue_count > 16 {
        bail!("queue count must be in 1..=16");
    }
    validate_traffic_profile(args.traffic_profile, args.queue_count, args.frame_size)?;
    validate_realtime_priority(args.realtime_priority)?;
    if args.rx_cpus.len() != args.queue_count || args.tx_cpus.len() != args.queue_count {
        bail!("RX and TX CPU counts must equal queue count");
    }
    let worker_cpus = args
        .rx_cpus
        .iter()
        .chain(args.tx_cpus.iter())
        .copied()
        .collect::<HashSet<_>>();
    if worker_cpus.len() != args.queue_count * 2 || worker_cpus.contains(&args.main_cpu) {
        bail!("main, RX and TX CPUs must all be distinct");
    }
    let watchdog = WorkerWatchdog::spawn(lifecycle_deadline(
        Instant::now(),
        WORKER_SETUP_WATCHDOG_TIMEOUT,
        Duration::ZERO,
    )?)?;
    initialize_eal(&args)?;
    let eal_guard = EalGuard;
    let available = unsafe { hft_dpdk_port_count() };
    if available != 2 {
        bail!(
            "expected exactly two allow-listed DPDK ports, got {}",
            available
        );
    }
    let capture_port = find_port(&args.capture_pci)?;
    let replay_port = find_port(&args.replay_pci)?;
    let pool_name = CString::new(format!("hft_pool_{}", std::process::id()))?;
    let socket_id = unsafe { hft_dpdk_socket_id() };
    let pool_count = (args.queue_count as u32 * 16_384).max(65_535);
    let mempool =
        unsafe { hft_dpdk_mempool_create(pool_name.as_ptr(), pool_count, 256, socket_id) };
    if mempool.is_null() {
        bail!("rte_pktmbuf_pool_create failed");
    }
    let mut port_guard = PortGuard { ports: Vec::new() };
    let mut descriptor_configuration = Vec::with_capacity(2);
    for port in [capture_port, replay_port] {
        let mut actual_rx = 0u16;
        let mut actual_tx = 0u16;
        let status = unsafe {
            hft_dpdk_port_init(
                port,
                mempool,
                REQUESTED_RX_DESCRIPTORS,
                REQUESTED_TX_DESCRIPTORS,
                args.queue_count as u16,
                args.traffic_profile.port_profile(),
                &mut actual_rx,
                &mut actual_tx,
            )
        };
        if status != 0 {
            bail!("initialize DPDK port {} failed: {}", port, status);
        }
        port_guard.ports.push(port);
        descriptor_configuration.push(PortDescriptorConfiguration {
            port_id: port,
            requested_rx: REQUESTED_RX_DESCRIPTORS,
            actual_rx,
            requested_tx: REQUESTED_TX_DESCRIPTORS,
            actual_tx,
        });
    }
    for port in [capture_port, replay_port] {
        wait_link(port)?;
    }
    let capture_before = read_stats(capture_port)?;
    let replay_before = read_stats(replay_port)?;
    let capture_mac = port_mac(capture_port)?;
    let replay_mac = port_mac(replay_port)?;
    let templates = build_templates(
        args.traffic_profile,
        args.frame_size,
        capture_mac,
        replay_mac,
    )?;
    let mempool_before = read_mempool_snapshot(mempool)?;
    let duration = Duration::from_secs(args.duration_s);
    watchdog.rearm(lifecycle_deadline(
        Instant::now(),
        WORKER_READY_TIMEOUT,
        WORKER_SHUTDOWN_GRACE,
    )?)?;
    let done = Arc::new(AtomicBool::new(false));
    let tx_remaining = Arc::new(AtomicUsize::new(args.queue_count));
    let (ready_sender, ready_receiver) = mpsc::channel();
    let mempool_address = mempool as usize;
    let mut tx_handles = Vec::with_capacity(args.queue_count);
    let mut rx_handles = Vec::with_capacity(args.queue_count);
    let mut tx_start_senders = Vec::with_capacity(args.queue_count);
    let mut rx_start_senders = Vec::with_capacity(args.queue_count);
    for queue in 0..args.queue_count {
        let (start_sender, start_receiver) = mpsc::sync_channel(0);
        tx_start_senders.push(start_sender);
        let ready = ready_sender.clone();
        let done = Arc::clone(&done);
        let remaining = Arc::clone(&tx_remaining);
        let config = TxConfig {
            port: replay_port,
            queue_id: queue as u16,
            mempool: mempool_address,
            cpu: args.tx_cpus[queue],
            realtime_priority: args.realtime_priority,
            duration,
            target_mpps: args.target_mpps / args.queue_count as f64,
            burst_size: args.burst_size,
            frame_size: args.frame_size,
            timestamp_offset: args.traffic_profile.timestamp_offset(),
            templates: templates.clone(),
        };
        tx_handles.push(
            thread::Builder::new()
                .name(format!("hft-dpdk-tx-{queue}"))
                .spawn(move || {
                    let _completion = TxCompletionGuard::new(remaining, done);
                    run_tx(config, start_receiver, ready)
                })
                .context("spawn DPDK TX worker")?,
        );
    }
    for queue in 0..args.queue_count {
        let (start_sender, start_receiver) = mpsc::sync_channel(0);
        rx_start_senders.push(start_sender);
        let ready = ready_sender.clone();
        let done = Arc::clone(&done);
        let config = RxConfig {
            port: capture_port,
            queue_id: queue as u16,
            cpu: args.rx_cpus[queue],
            realtime_priority: args.realtime_priority,
            burst_size: args.burst_size,
            duration,
            timestamp_offset: args.traffic_profile.timestamp_offset(),
        };
        rx_handles.push(
            thread::Builder::new()
                .name(format!("hft-dpdk-rx-{queue}"))
                .spawn(move || run_rx(config, start_receiver, ready, done))
                .context("spawn DPDK RX worker")?,
        );
    }
    drop(ready_sender);
    for _ in 0..args.queue_count * 2 {
        let ready_status = match ready_receiver.recv_timeout(WORKER_READY_TIMEOUT) {
            Ok(status) => status,
            Err(error) => {
                drop(rx_start_senders);
                drop(tx_start_senders);
                let _ = join_workers(tx_handles, "TX");
                let _ = join_workers(rx_handles, "RX");
                bail!("DPDK workers did not become ready within 5 seconds: {error}");
            }
        };
        if let Err(message) = ready_status {
            drop(rx_start_senders);
            drop(tx_start_senders);
            let _ = join_workers(tx_handles, "TX");
            let _ = join_workers(rx_handles, "RX");
            bail!("DPDK worker initialization failed: {message}");
        }
    }
    let start_epoch = Instant::now() + Duration::from_millis(500);
    watchdog.rearm(lifecycle_deadline(
        start_epoch,
        duration,
        WORKER_SHUTDOWN_GRACE,
    )?)?;
    for sender in rx_start_senders {
        sender.send(start_epoch)?;
    }
    for sender in tx_start_senders {
        sender.send(start_epoch)?;
    }
    let tx_result = join_workers(tx_handles, "TX");
    let rx_result = join_workers(rx_handles, "RX");
    let tx_reports = tx_result?;
    let rx_reports = rx_result?;
    let capture_after = read_stats(capture_port)?;
    let replay_after = read_stats(replay_port)?;
    let mempool_after = read_mempool_snapshot(mempool)?;
    let capture_delta = stats_delta(capture_after, capture_before);
    let replay_delta = stats_delta(replay_after, replay_before);
    let tsc_hz = unsafe { hft_dpdk_tsc_hz() };
    let latency_cycles = rx_reports
        .iter()
        .flat_map(|report| report.latency_cycles.iter().copied())
        .collect::<Vec<_>>();
    let latency = latency_percentiles(&latency_cycles, tsc_hz);
    let offered_packets = tx_reports.iter().map(|report| report.packets).sum::<u64>();
    let received_packets = rx_reports.iter().map(|report| report.packets).sum::<u64>();
    let tx_elapsed = tx_reports
        .iter()
        .map(|report| report.elapsed_s)
        .fold(0.0, f64::max);
    let rx_elapsed = rx_reports
        .iter()
        .map(|report| report.elapsed_s)
        .fold(0.0, f64::max);
    let observed_tx_mpps_min_1s = aggregate_min_mpps(&tx_reports);
    let observed_rx_mpps_min_1s = aggregate_min_mpps(&rx_reports);
    let tx_rate_full_windows = aggregate_full_rate_windows(&tx_reports);
    let rx_rate_full_windows = aggregate_full_rate_windows(&rx_reports);
    let gap = i128::from(offered_packets) - i128::from(received_packets);
    let rx_queue_packets: Vec<u64> = rx_reports.iter().map(|report| report.packets).collect();
    let tx_queue_packets = tx_reports.iter().map(|report| report.packets).collect();
    let errors = qualification_errors(
        args.target_mpps,
        observed_tx_mpps_min_1s,
        observed_rx_mpps_min_1s,
        tx_rate_full_windows,
        rx_rate_full_windows,
        args.duration_s,
        gap,
        capture_delta,
        replay_delta,
        &rx_queue_packets,
        &latency,
        args.max_end_to_end_p99_us,
        args.max_end_to_end_p999_us,
    );
    let data_plane_qualified = errors.is_empty();
    let report = RunReport {
        schema_version: 5,
        scope: "r0_dpdk_bnx2x_capture_only",
        backend: backend_name(args.traffic_profile, args.queue_count),
        candidate_id: args.candidate_id,
        frozen_thresholds_sha256: args.frozen_thresholds_sha256.to_ascii_lowercase(),
        capture_pci: args.capture_pci,
        replay_pci: args.replay_pci,
        capture_port_id: capture_port,
        replay_port_id: replay_port,
        capture_mac: format_mac(capture_mac),
        replay_mac: format_mac(replay_mac),
        queue_count: args.queue_count,
        realtime_priority: args.realtime_priority,
        main_cpu: args.main_cpu,
        rx_cpus: args.rx_cpus,
        tx_cpus: args.tx_cpus,
        traffic_profile: args.traffic_profile.as_str(),
        synthetic_flow_count: TEMPLATE_COUNT,
        ip_protocol: args.traffic_profile.ip_protocol(),
        timestamp_offset_bytes: args.traffic_profile.timestamp_offset(),
        port_configuration: args.traffic_profile.port_configuration(),
        target_mpps: args.target_mpps,
        frame_size_bytes: args.frame_size,
        burst_size: args.burst_size,
        descriptor_configuration,
        mempool_configured_capacity: pool_count,
        mempool_before,
        mempool_after,
        max_end_to_end_p99_us: args.max_end_to_end_p99_us,
        max_end_to_end_p999_us: args.max_end_to_end_p999_us,
        duration_s: tx_elapsed,
        offered_packets,
        received_packets,
        offered_received_gap: gap,
        observed_tx_mpps_min_1s,
        observed_rx_mpps_min_1s,
        rate_window_alignment: "shared_monotonic_epoch_fixed_1s_v1",
        tx_rate_full_windows,
        rx_rate_full_windows,
        achieved_tx_mpps: offered_packets as f64 / tx_elapsed / 1_000_000.0,
        achieved_rx_mpps: received_packets as f64 / rx_elapsed / 1_000_000.0,
        capture_stats_delta: capture_delta,
        replay_stats_delta: replay_delta,
        latency_sample_stride: 1024,
        latency_timestamp_source: "dpdk_tsc_embedded_tx_rx_v1",
        end_to_end_latency_us: latency,
        rx_cpu_cores_average: rx_reports
            .iter()
            .map(|report| report.cpu_cores_average)
            .sum(),
        tx_cpu_cores_average: tx_reports
            .iter()
            .map(|report| report.cpu_cores_average)
            .sum(),
        rx_stalls: rx_reports.iter().map(|report| report.stalls).sum(),
        tx_stalls: tx_reports.iter().map(|report| report.stalls).sum(),
        rx_hotpath_counters: rx_reports.iter().map(|report| report.hotpath).collect(),
        tx_hotpath_counters: tx_reports.iter().map(|report| report.hotpath).collect(),
        rx_queue_packets,
        tx_queue_packets,
        data_plane_qualified,
        resource_gate_evaluated: false,
        r0_capture_only_qualified: false,
        hard_gate_errors: errors,
        full_pipeline_qualified: false,
        final_pareto_ingestion_allowed: false,
    };
    if let Some(parent) = args.output.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut output =
        File::create(&args.output).with_context(|| format!("create {}", args.output.display()))?;
    serde_json::to_writer_pretty(&mut output, &report)?;
    output.write_all(b"\n")?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    drop(port_guard);
    drop(eal_guard);
    if data_plane_qualified {
        Ok(())
    } else {
        std::process::exit(10);
    }
}

#[cfg(test)]
mod tests {
    use super::{
        backend_name, build_templates, internet_checksum, ipv4_transport_checksum,
        latency_percentiles, lifecycle_deadline, percentile, qualification_errors, synthetic_frame,
        validate_file_prefix, validate_realtime_priority, validate_traffic_profile,
        wait_for_watchdog, zero_poll_requires_housekeeping, DpdkStats, Percentiles, TrafficProfile,
        TxCompletionGuard, WatchdogCommand, WatchdogOutcome, TCP_RSS_DIAGNOSTIC_TIMESTAMP_OFFSET,
        TEMPLATE_COUNT, UDP_TIMESTAMP_OFFSET,
    };
    use std::collections::HashSet;
    use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
    use std::sync::{mpsc, Arc};
    use std::time::{Duration, Instant};

    #[test]
    fn percentile_uses_conservative_upper_rank() {
        assert_eq!(percentile(&[1.0, 2.0, 3.0, 4.0], 0.99), Some(4.0));
    }

    #[test]
    fn latency_conversion_uses_tsc_frequency() {
        let value = latency_percentiles(&[1_000, 2_000], 1_000_000);
        assert_eq!(value.p50, Some(2_000.0));
        assert_eq!(value.max, Some(2_000.0));
    }

    #[test]
    fn file_prefix_rejects_paths_and_accepts_run_ids() {
        assert!(validate_file_prefix("hft_r0_dpdk_20260731T013014Z").is_ok());
        assert!(validate_file_prefix("../unsafe").is_err());
        assert!(validate_file_prefix("").is_err());
    }

    #[test]
    fn realtime_priority_is_bounded_and_can_be_disabled() {
        assert!(validate_realtime_priority(0).is_ok());
        assert!(validate_realtime_priority(10).is_ok());
        assert!(validate_realtime_priority(-1).is_err());
        assert!(validate_realtime_priority(21).is_err());
    }

    #[test]
    fn tx_completion_guard_signals_the_last_worker_during_unwind() {
        let remaining = Arc::new(AtomicUsize::new(1));
        let done = Arc::new(AtomicBool::new(false));
        let unwind = std::panic::catch_unwind({
            let remaining = Arc::clone(&remaining);
            let done = Arc::clone(&done);
            move || {
                let _completion = TxCompletionGuard::new(remaining, done);
                panic!("synthetic TX worker panic");
            }
        });
        assert!(unwind.is_err());
        assert_eq!(remaining.load(Ordering::Acquire), 0);
        assert!(done.load(Ordering::Acquire));
    }

    #[test]
    fn tx_completion_guard_waits_for_every_worker() {
        let remaining = Arc::new(AtomicUsize::new(2));
        let done = Arc::new(AtomicBool::new(false));
        let first = TxCompletionGuard::new(Arc::clone(&remaining), Arc::clone(&done));
        let second = TxCompletionGuard::new(Arc::clone(&remaining), Arc::clone(&done));
        drop(first);
        assert_eq!(remaining.load(Ordering::Acquire), 1);
        assert!(!done.load(Ordering::Acquire));
        drop(second);
        assert_eq!(remaining.load(Ordering::Acquire), 0);
        assert!(done.load(Ordering::Acquire));
    }

    #[test]
    fn watchdog_can_be_rearmed_then_disarmed() {
        let (sender, receiver) = mpsc::channel();
        sender
            .send(WatchdogCommand::Rearm(
                Instant::now() + Duration::from_secs(60),
            ))
            .expect("queue watchdog rearm");
        sender
            .send(WatchdogCommand::Disarm)
            .expect("queue watchdog disarm");
        assert_eq!(
            wait_for_watchdog(receiver, Instant::now() + Duration::from_secs(60)),
            WatchdogOutcome::Disarmed
        );
    }

    #[test]
    fn watchdog_expires_at_an_elapsed_deadline() {
        let (_sender, receiver) = mpsc::channel();
        assert_eq!(
            wait_for_watchdog(receiver, Instant::now()),
            WatchdogOutcome::Expired
        );
    }

    #[test]
    fn lifecycle_deadline_includes_duration_and_grace() {
        let started = Instant::now();
        let deadline = lifecycle_deadline(started, Duration::from_secs(15), Duration::from_secs(2))
            .expect("lifecycle deadline");
        assert_eq!(deadline.duration_since(started), Duration::from_secs(17));
    }

    #[test]
    fn zero_poll_housekeeping_runs_once_per_sixty_four_empty_polls() {
        assert!(!zero_poll_requires_housekeeping(0));
        assert!(!zero_poll_requires_housekeeping(1));
        assert!(!zero_poll_requires_housekeeping(63));
        assert!(zero_poll_requires_housekeeping(64));
        assert!(!zero_poll_requires_housekeeping(65));
        assert!(zero_poll_requires_housekeeping(128));
    }

    #[test]
    fn synthetic_frame_uses_runtime_port_addresses() {
        let destination = [0x18, 0xc0, 0x09, 0x1c, 0x53, 0x69];
        let source = [0x18, 0xc0, 0x09, 0x1c, 0x53, 0x6b];
        let frame = synthetic_frame(TrafficProfile::UdpCompat, 64, 7, destination, source)
            .expect("synthetic frame");
        assert_eq!(&frame[0..6], &destination);
        assert_eq!(&frame[6..12], &source);
        assert_eq!(frame[23], 17);
        assert_eq!(UDP_TIMESTAMP_OFFSET, 42);
    }

    #[test]
    fn tcp_rss_diagnostic_frame_has_valid_headers_and_padding_timestamp_space() {
        let frame = synthetic_frame(
            TrafficProfile::TcpRssDiagnostic,
            64,
            7,
            [0x18, 0xc0, 0x09, 0x1c, 0x53, 0x69],
            [0x18, 0xc0, 0x09, 0x1c, 0x53, 0x6b],
        )
        .expect("TCP RSS diagnostic frame");
        let ip = 14usize;
        let tcp = 34usize;
        let ip_total_length = u16::from_be_bytes([frame[ip + 2], frame[ip + 3]]);
        assert_eq!(ip_total_length, 40);
        assert_eq!(frame[ip + 9], 6);
        assert_eq!(internet_checksum(&frame[ip..ip + 20]), 0);
        assert_eq!(frame[tcp + 12] >> 4, 5);
        assert_eq!(frame[tcp + 13], 0x02);
        let source = u32::from_be_bytes(frame[ip + 12..ip + 16].try_into().unwrap());
        let destination = u32::from_be_bytes(frame[ip + 16..ip + 20].try_into().unwrap());
        assert_eq!(
            ipv4_transport_checksum(source, destination, 6, &frame[tcp..tcp + 20])
                .expect("verify TCP checksum"),
            0
        );
        let ip_end = ip + usize::from(ip_total_length);
        assert_eq!(ip_end, usize::from(TCP_RSS_DIAGNOSTIC_TIMESTAMP_OFFSET));
        assert!(usize::from(TCP_RSS_DIAGNOSTIC_TIMESTAMP_OFFSET) + 8 <= frame.len());
        assert!(frame[ip_end..].iter().all(|byte| *byte == 0));
    }

    #[test]
    fn tcp_rss_diagnostic_templates_have_256_unique_five_tuples() {
        let templates = build_templates(
            TrafficProfile::TcpRssDiagnostic,
            64,
            [0x18, 0xc0, 0x09, 0x1c, 0x53, 0x69],
            [0x18, 0xc0, 0x09, 0x1c, 0x53, 0x6b],
        )
        .expect("TCP templates");
        let tuples = templates
            .chunks_exact(64)
            .map(|frame| {
                let mut tuple = Vec::with_capacity(13);
                tuple.extend_from_slice(&frame[26..34]);
                tuple.extend_from_slice(&frame[34..38]);
                tuple.push(frame[23]);
                tuple
            })
            .collect::<HashSet<_>>();
        assert_eq!(tuples.len(), TEMPLATE_COUNT);
    }

    #[test]
    fn tcp_rss_diagnostic_profile_is_explicit_and_fail_closed() {
        assert!(validate_traffic_profile(TrafficProfile::UdpCompat, 1, 64).is_ok());
        assert!(validate_traffic_profile(TrafficProfile::TcpRssDiagnostic, 1, 64).is_err());
        assert!(validate_traffic_profile(TrafficProfile::TcpRssDiagnostic, 2, 128).is_err());
        assert!(validate_traffic_profile(TrafficProfile::TcpRssDiagnostic, 2, 64).is_ok());
        assert_eq!(
            backend_name(TrafficProfile::TcpRssDiagnostic, 2),
            "dpdk_bnx2x_stock_tcp_rss_diagnostic"
        );
    }

    #[test]
    fn qualification_requires_rx_rate_independently() {
        let latency = Percentiles {
            samples: 10,
            p50: Some(1.0),
            p99: Some(10.0),
            p999: Some(20.0),
            max: Some(20.0),
        };
        let errors = qualification_errors(
            1.0,
            Some(1.0),
            Some(0.999_999),
            15,
            15,
            15,
            0,
            DpdkStats::default(),
            DpdkStats::default(),
            &[1],
            &latency,
            100.0,
            500.0,
        );
        assert_eq!(errors, vec!["rx_target_load"]);
    }

    #[test]
    fn qualification_enforces_replay_errors_and_runtime_latency_limits() {
        let replay = DpdkStats {
            oerrors: 1,
            ..DpdkStats::default()
        };
        let latency = Percentiles {
            samples: 10,
            p50: Some(1.0),
            p99: Some(101.0),
            p999: Some(501.0),
            max: Some(501.0),
        };
        let errors = qualification_errors(
            1.0,
            Some(1.0),
            Some(1.0),
            15,
            15,
            15,
            0,
            DpdkStats::default(),
            replay,
            &[1],
            &latency,
            100.0,
            500.0,
        );
        assert_eq!(
            errors,
            vec!["replay_tx_error", "end_to_end_p99", "end_to_end_p999"]
        );
    }
}
