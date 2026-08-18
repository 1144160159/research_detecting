use anyhow::{bail, Context, Result};
use clap::Parser;
use serde::Serialize;
use std::ffi::CString;
use std::fs::File;
use std::io::Write;
use std::os::fd::RawFd;
use std::path::PathBuf;
use std::sync::atomic::{fence, Ordering};
use std::thread;
use std::time::{Duration, Instant};

const PACKET_QDISC_BYPASS: libc::c_int = 20;
const PACKET_VERSION: libc::c_int = 10;
const PACKET_TX_RING: libc::c_int = 13;
const TPACKET_V2: libc::c_int = 1;
const TP_STATUS_AVAILABLE: u32 = 0;
const TP_STATUS_SEND_REQUEST: u32 = 1;
const TP_STATUS_SENDING: u32 = 2;
const TP_STATUS_WRONG_FORMAT: u32 = 4;
const TPACKET_ALIGNMENT: usize = 16;
const TX_BLOCK_SIZE: usize = 1 << 20;
const TX_BLOCK_COUNT: usize = 2;
const RATE_HEADROOM_RATIO: f64 = 1.01;

#[derive(Debug, Parser)]
#[command(about = "NUMA-pinned multi-thread synthetic 64B AF_PACKET generator")]
struct Args {
    #[arg(long)]
    interface: String,
    #[arg(long)]
    duration_s: u64,
    #[arg(long)]
    target_mpps: f64,
    #[arg(long)]
    worker_cpus: String,
    #[arg(long, default_value_t = 256)]
    batch_size: usize,
    #[arg(long, default_value_t = 64)]
    frame_size: usize,
    #[arg(long)]
    output: PathBuf,
}

#[derive(Serialize)]
struct InjectorReport {
    schema_version: u32,
    scope: &'static str,
    interface: String,
    source: &'static str,
    duration_s: f64,
    configured_target_mpps: f64,
    frame_size_bytes: usize,
    backend: &'static str,
    tx_ring_frames_per_worker: usize,
    worker_cpu_ids: Vec<usize>,
    worker_packets: Vec<u64>,
    worker_cpu_cores_average: Vec<f64>,
    rate_headroom_ratio: f64,
    offered_packets: u64,
    offered_bytes: u64,
    achieved_mpps: f64,
    achieved_gbps: f64,
    observed_mpps_min_1s: Option<f64>,
    observed_gbps_min_1s: Option<f64>,
    send_would_block_retries: u64,
}

struct Socket(RawFd);

impl Drop for Socket {
    fn drop(&mut self) {
        unsafe {
            libc::close(self.0);
        }
    }
}

#[repr(C)]
struct TpacketReq {
    tp_block_size: u32,
    tp_block_nr: u32,
    tp_frame_size: u32,
    tp_frame_nr: u32,
}

#[repr(C)]
struct Tpacket2Hdr {
    tp_status: u32,
    tp_len: u32,
    tp_snaplen: u32,
    tp_mac: u16,
    tp_net: u16,
    tp_sec: u32,
    tp_nsec: u32,
    tp_vlan_tci: u16,
    tp_vlan_tpid: u16,
    tp_padding: [u8; 4],
}

struct TxRing {
    socket: Socket,
    mapping: *mut u8,
    mapping_len: usize,
    ring_frame_size: usize,
    frame_count: usize,
    next_frame: usize,
}

impl Drop for TxRing {
    fn drop(&mut self) {
        unsafe {
            libc::munmap(self.mapping.cast(), self.mapping_len);
        }
    }
}

struct WorkerReport {
    packets: u64,
    bytes: u64,
    elapsed_s: f64,
    cpu_seconds: f64,
    min_mpps_1s: Option<f64>,
    min_gbps_1s: Option<f64>,
    retries: u64,
}

struct WorkerConfig {
    interface: String,
    cpu: usize,
    worker_index: usize,
    worker_count: usize,
    batch_size: usize,
    frame_size: usize,
    target_mpps: f64,
    duration: Duration,
}

fn parse_cpu_list(raw: &str) -> Result<Vec<usize>> {
    let mut cpus = Vec::new();
    for token in raw.split(',') {
        let cpu = token
            .trim()
            .parse::<usize>()
            .with_context(|| format!("invalid worker CPU {token:?}"))?;
        if cpu >= libc::CPU_SETSIZE as usize {
            bail!("worker CPU {} exceeds CPU_SETSIZE", cpu);
        }
        if cpus.contains(&cpu) {
            bail!("duplicate worker CPU {}", cpu);
        }
        cpus.push(cpu);
    }
    if cpus.is_empty() {
        bail!("--worker-cpus must contain at least one CPU");
    }
    Ok(cpus)
}

fn pin_current_thread(cpu: usize) -> Result<()> {
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
            .with_context(|| format!("pin injector worker to CPU {cpu}"));
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

fn tpacket_align(value: usize) -> usize {
    (value + TPACKET_ALIGNMENT - 1) & !(TPACKET_ALIGNMENT - 1)
}

fn tx_ring_frame_size(packet_size: usize) -> usize {
    let payload_offset = tpacket_align(std::mem::size_of::<Tpacket2Hdr>());
    tpacket_align(payload_offset + packet_size)
        .next_power_of_two()
        .max(128)
}

fn set_socket_option<T>(
    fd: RawFd,
    option: libc::c_int,
    value: &T,
    description: &str,
) -> Result<()> {
    let status = unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_PACKET,
            option,
            value as *const T as *const libc::c_void,
            std::mem::size_of_val(value) as libc::socklen_t,
        )
    };
    if status < 0 {
        return Err(std::io::Error::last_os_error()).with_context(|| description.to_owned());
    }
    Ok(())
}

fn open_tx_ring(interface: &str, packet_size: usize) -> Result<TxRing> {
    let name = CString::new(interface).context("interface contains a NUL byte")?;
    let ifindex = unsafe { libc::if_nametoindex(name.as_ptr()) };
    if ifindex == 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("resolve interface {interface}"));
    }
    let fd = unsafe { libc::socket(libc::AF_PACKET, libc::SOCK_RAW | libc::SOCK_NONBLOCK, 0) };
    if fd < 0 {
        return Err(std::io::Error::last_os_error()).context("create AF_PACKET TX socket");
    }
    let socket = Socket(fd);
    set_socket_option(socket.0, PACKET_VERSION, &TPACKET_V2, "set TPACKET_V2")?;
    let enable: libc::c_int = 1;
    set_socket_option(
        socket.0,
        PACKET_QDISC_BYPASS,
        &enable,
        "enable PACKET_QDISC_BYPASS",
    )?;
    let ring_frame_size = tx_ring_frame_size(packet_size);
    if !TX_BLOCK_SIZE.is_multiple_of(ring_frame_size) {
        bail!(
            "TX block size {} is not divisible by ring frame size {}",
            TX_BLOCK_SIZE,
            ring_frame_size
        );
    }
    let frame_count = TX_BLOCK_SIZE / ring_frame_size * TX_BLOCK_COUNT;
    let request = TpacketReq {
        tp_block_size: TX_BLOCK_SIZE as u32,
        tp_block_nr: TX_BLOCK_COUNT as u32,
        tp_frame_size: ring_frame_size as u32,
        tp_frame_nr: frame_count as u32,
    };
    set_socket_option(
        socket.0,
        PACKET_TX_RING,
        &request,
        "allocate PACKET_TX_RING",
    )?;
    let mut address: libc::sockaddr_ll = unsafe { std::mem::zeroed() };
    address.sll_family = libc::AF_PACKET as u16;
    address.sll_protocol = 0;
    address.sll_ifindex = ifindex as i32;
    let bind_status = unsafe {
        libc::bind(
            socket.0,
            &address as *const libc::sockaddr_ll as *const libc::sockaddr,
            std::mem::size_of::<libc::sockaddr_ll>() as libc::socklen_t,
        )
    };
    if bind_status < 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("bind AF_PACKET TX socket to {interface}"));
    }
    let mapping_len = TX_BLOCK_SIZE * TX_BLOCK_COUNT;
    let mapping = unsafe {
        libc::mmap(
            std::ptr::null_mut(),
            mapping_len,
            libc::PROT_READ | libc::PROT_WRITE,
            libc::MAP_SHARED,
            socket.0,
            0,
        )
    };
    if mapping == libc::MAP_FAILED {
        return Err(std::io::Error::last_os_error()).context("mmap PACKET_TX_RING");
    }
    Ok(TxRing {
        socket,
        mapping: mapping.cast(),
        mapping_len,
        ring_frame_size,
        frame_count,
        next_frame: 0,
    })
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

fn synthetic_frame(frame_size: usize, flow_id: u32) -> Result<Vec<u8>> {
    if !(64..=1500).contains(&frame_size) {
        bail!("synthetic frame size must be in 64..=1500");
    }
    let mut frame = vec![0u8; frame_size];
    frame[0..6].copy_from_slice(&[0x02, 0, 0, 0, 0, 1]);
    frame[6..12].copy_from_slice(&[0x02, 0, 0, 0, 0, 2]);
    frame[12..14].copy_from_slice(&0x0800u16.to_be_bytes());
    let ip = 14usize;
    frame[ip] = 0x45;
    frame[ip + 2..ip + 4].copy_from_slice(&((frame_size - ip) as u16).to_be_bytes());
    frame[ip + 4..ip + 6].copy_from_slice(&(flow_id as u16).to_be_bytes());
    frame[ip + 6..ip + 8].copy_from_slice(&0x4000u16.to_be_bytes());
    frame[ip + 8] = 64;
    frame[ip + 9] = 17;
    let source = 0x0a00_0001u32.wrapping_add(flow_id & 0x000f_ffff);
    let destination = 0x0b00_0001u32.wrapping_add(flow_id.rotate_left(7) & 0x000f_ffff);
    frame[ip + 12..ip + 16].copy_from_slice(&source.to_be_bytes());
    frame[ip + 16..ip + 20].copy_from_slice(&destination.to_be_bytes());
    let checksum = internet_checksum(&frame[ip..ip + 20]);
    frame[ip + 10..ip + 12].copy_from_slice(&checksum.to_be_bytes());
    let udp = ip + 20;
    let source_port = 1024u16.wrapping_add((flow_id % 60_000) as u16);
    let destination_port = 1024u16.wrapping_add((flow_id.rotate_left(11) % 60_000) as u16);
    frame[udp..udp + 2].copy_from_slice(&source_port.to_be_bytes());
    frame[udp + 2..udp + 4].copy_from_slice(&destination_port.to_be_bytes());
    frame[udp + 4..udp + 6].copy_from_slice(&((frame_size - udp) as u16).to_be_bytes());
    for (index, byte) in frame[udp + 8..].iter_mut().enumerate() {
        *byte = flow_id.wrapping_add(index as u32) as u8;
    }
    Ok(frame)
}

impl TxRing {
    fn header(&self, index: usize) -> *mut Tpacket2Hdr {
        unsafe {
            self.mapping
                .add(index * self.ring_frame_size)
                .cast::<Tpacket2Hdr>()
        }
    }

    fn kick(&self) -> Result<bool> {
        let status = unsafe { libc::send(self.socket.0, std::ptr::null(), 0, libc::MSG_DONTWAIT) };
        if status >= 0 {
            return Ok(true);
        }
        let error = std::io::Error::last_os_error();
        if error.kind() == std::io::ErrorKind::WouldBlock
            || error.raw_os_error() == Some(libc::ENOBUFS)
        {
            return Ok(false);
        }
        Err(error).context("kick PACKET_TX_RING")
    }

    fn wait_available(&self, header: *mut Tpacket2Hdr) -> Result<u64> {
        let mut retries = 0u64;
        let mut spins = 0u32;
        loop {
            let status =
                unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*header).tp_status)) };
            if status == TP_STATUS_AVAILABLE {
                fence(Ordering::Acquire);
                return Ok(retries);
            }
            if status == TP_STATUS_WRONG_FORMAT {
                bail!("PACKET_TX_RING rejected a frame as wrong format");
            }
            if status != TP_STATUS_SENDING && status != TP_STATUS_SEND_REQUEST {
                bail!("unexpected PACKET_TX_RING status {}", status);
            }
            spins = spins.wrapping_add(1);
            if spins.is_multiple_of(256) && !self.kick()? {
                retries = retries.saturating_add(1);
            }
            std::hint::spin_loop();
        }
    }

    fn send_batch(&mut self, frames: &[Vec<u8>]) -> Result<(usize, u64)> {
        let payload_offset = tpacket_align(std::mem::size_of::<Tpacket2Hdr>());
        let mut retries = 0u64;
        for frame in frames {
            let header = self.header(self.next_frame);
            retries = retries.saturating_add(self.wait_available(header)?);
            unsafe {
                std::ptr::copy_nonoverlapping(
                    frame.as_ptr(),
                    (header.cast::<u8>()).add(payload_offset),
                    frame.len(),
                );
                std::ptr::write_volatile(
                    std::ptr::addr_of_mut!((*header).tp_len),
                    frame.len() as u32,
                );
                std::ptr::write_volatile(
                    std::ptr::addr_of_mut!((*header).tp_snaplen),
                    frame.len() as u32,
                );
                fence(Ordering::Release);
                std::ptr::write_volatile(
                    std::ptr::addr_of_mut!((*header).tp_status),
                    TP_STATUS_SEND_REQUEST,
                );
            }
            self.next_frame = (self.next_frame + 1) % self.frame_count;
        }
        if !self.kick()? {
            retries = retries.saturating_add(1);
        }
        Ok((frames.len(), retries))
    }

    fn drain(&self, timeout: Duration) -> Result<u64> {
        let started = Instant::now();
        let mut retries = 0u64;
        loop {
            let mut pending = 0usize;
            for index in 0..self.frame_count {
                let header = self.header(index);
                let status =
                    unsafe { std::ptr::read_volatile(std::ptr::addr_of!((*header).tp_status)) };
                if status == TP_STATUS_WRONG_FORMAT {
                    bail!("PACKET_TX_RING rejected a frame during drain");
                }
                if status != TP_STATUS_AVAILABLE {
                    pending += 1;
                }
            }
            if pending == 0 {
                return Ok(retries);
            }
            if started.elapsed() >= timeout {
                bail!(
                    "PACKET_TX_RING drain timed out with {} frames pending",
                    pending
                );
            }
            if !self.kick()? {
                retries = retries.saturating_add(1);
            }
            std::hint::spin_loop();
        }
    }
}

fn run_worker(config: WorkerConfig) -> Result<WorkerReport> {
    let WorkerConfig {
        interface,
        cpu,
        worker_index,
        worker_count,
        batch_size,
        frame_size,
        target_mpps,
        duration,
    } = config;
    pin_current_thread(cpu)?;
    let mut tx_ring = open_tx_ring(&interface, frame_size)?;
    let frames: Vec<Vec<u8>> = (0..batch_size)
        .map(|index| synthetic_frame(frame_size, (worker_index * batch_size + index) as u32))
        .collect::<Result<_>>()?;
    let started = Instant::now();
    let cpu_started = thread_cpu_time()?;
    let worker_target_pps = target_mpps * 1_000_000.0 / worker_count as f64;
    let mut packets = 0u64;
    let mut bytes = 0u64;
    let mut retries = 0u64;
    let mut window_started = Instant::now();
    let mut window_packets = 0u64;
    let mut min_mpps_1s: Option<f64> = None;
    let mut min_gbps_1s: Option<f64> = None;
    while started.elapsed() < duration {
        let (sent, batch_retries) = tx_ring.send_batch(&frames)?;
        let sent = sent as u64;
        packets = packets.saturating_add(sent);
        bytes = bytes.saturating_add(sent.saturating_mul(frame_size as u64));
        window_packets = window_packets.saturating_add(sent);
        retries = retries.saturating_add(batch_retries);
        let target_elapsed = packets as f64 / (worker_target_pps * RATE_HEADROOM_RATIO);
        let actual_elapsed = started.elapsed().as_secs_f64();
        if target_elapsed > actual_elapsed {
            let remaining = target_elapsed - actual_elapsed;
            if remaining > 0.000_050 {
                thread::sleep(Duration::from_secs_f64(remaining - 0.000_025));
            } else {
                std::hint::spin_loop();
            }
        }
        let window_elapsed = window_started.elapsed();
        if window_elapsed >= Duration::from_secs(1) {
            let seconds = window_elapsed.as_secs_f64();
            let mpps = window_packets as f64 / seconds / 1_000_000.0;
            let gbps = window_packets as f64 * frame_size as f64 * 8.0 / seconds / 1_000_000_000.0;
            min_mpps_1s = Some(min_mpps_1s.map_or(mpps, |current| current.min(mpps)));
            min_gbps_1s = Some(min_gbps_1s.map_or(gbps, |current| current.min(gbps)));
            window_started = Instant::now();
            window_packets = 0;
        }
    }
    retries = retries.saturating_add(tx_ring.drain(Duration::from_secs(2))?);
    let elapsed_s = started.elapsed().as_secs_f64();
    let cpu_seconds = thread_cpu_time()?
        .checked_sub(cpu_started)
        .context("thread CPU clock moved backwards")?
        .as_secs_f64();
    Ok(WorkerReport {
        packets,
        bytes,
        elapsed_s,
        cpu_seconds,
        min_mpps_1s,
        min_gbps_1s,
        retries,
    })
}

fn main() -> Result<()> {
    let args = Args::parse();
    if args.duration_s == 0 {
        bail!("--duration-s must be positive");
    }
    if !args.target_mpps.is_finite() || args.target_mpps <= 0.0 {
        bail!("--target-mpps must be finite and positive");
    }
    if args.batch_size == 0 || args.batch_size > 1024 {
        bail!("--batch-size must be in 1..=1024");
    }
    let cpus = parse_cpu_list(&args.worker_cpus)?;
    let duration = Duration::from_secs(args.duration_s);
    let mut handles = Vec::with_capacity(cpus.len());
    for (worker_index, cpu) in cpus.iter().copied().enumerate() {
        let interface = args.interface.clone();
        let worker_count = cpus.len();
        let batch_size = args.batch_size;
        let frame_size = args.frame_size;
        let target_mpps = args.target_mpps;
        handles.push(
            thread::Builder::new()
                .name(format!("hft-tx-{worker_index}"))
                .spawn(move || {
                    run_worker(WorkerConfig {
                        interface,
                        cpu,
                        worker_index,
                        worker_count,
                        batch_size,
                        frame_size,
                        target_mpps,
                        duration,
                    })
                })
                .context("spawn synthetic injector worker")?,
        );
    }
    let mut reports = Vec::with_capacity(handles.len());
    for handle in handles {
        reports.push(
            handle
                .join()
                .map_err(|_| anyhow::anyhow!("synthetic injector worker panicked"))??,
        );
    }
    let elapsed = reports
        .iter()
        .map(|report| report.elapsed_s)
        .fold(0.0f64, f64::max);
    let offered_packets = reports.iter().map(|report| report.packets).sum::<u64>();
    let offered_bytes = reports.iter().map(|report| report.bytes).sum::<u64>();
    let observed_mpps_min_1s = reports
        .iter()
        .map(|report| report.min_mpps_1s)
        .collect::<Option<Vec<_>>>()
        .map(|values| values.into_iter().sum());
    let observed_gbps_min_1s = reports
        .iter()
        .map(|report| report.min_gbps_1s)
        .collect::<Option<Vec<_>>>()
        .map(|values| values.into_iter().sum());
    let tx_ring_frames_per_worker =
        TX_BLOCK_SIZE / tx_ring_frame_size(args.frame_size) * TX_BLOCK_COUNT;
    let report = InjectorReport {
        schema_version: 2,
        scope: "physical_link_synthetic_small_packet_diagnostic",
        interface: args.interface,
        source: "synthetic_ipv4_udp_64B_v2",
        duration_s: elapsed,
        configured_target_mpps: args.target_mpps,
        frame_size_bytes: args.frame_size,
        backend: "packet_tx_ring_tpacket_v2",
        tx_ring_frames_per_worker,
        worker_cpu_ids: cpus,
        worker_packets: reports.iter().map(|report| report.packets).collect(),
        worker_cpu_cores_average: reports
            .iter()
            .map(|report| report.cpu_seconds / report.elapsed_s)
            .collect(),
        rate_headroom_ratio: RATE_HEADROOM_RATIO,
        offered_packets,
        offered_bytes,
        achieved_mpps: offered_packets as f64 / elapsed / 1_000_000.0,
        achieved_gbps: offered_bytes as f64 * 8.0 / elapsed / 1_000_000_000.0,
        observed_mpps_min_1s,
        observed_gbps_min_1s,
        send_would_block_retries: reports.iter().map(|report| report.retries).sum(),
    };
    if let Some(parent) = args.output.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut output = File::create(&args.output)
        .with_context(|| format!("create injector output {}", args.output.display()))?;
    serde_json::to_writer_pretty(&mut output, &report)?;
    output.write_all(b"\n")?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}
