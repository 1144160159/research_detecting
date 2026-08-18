use anyhow::{bail, Context, Result};
use clap::Parser;
use probe_agent::capture::xdp_sys::XDP_COPY;
use probe_agent::capture::{Umem, UmemConfig, XdpDesc, XskSocket, XskSocketConfig};
use serde::Serialize;
use std::ffi::CString;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant};

const XSK_RING_SIZE: u32 = 2048;
const UMEM_FRAME_SIZE: usize = 4096;
const UMEM_FRAME_COUNT: usize = 4096;
const UMEM_HEADROOM: usize = 16;
const RATE_HEADROOM_RATIO: f64 = 1.01;

#[derive(Debug, Parser)]
#[command(about = "NUMA-pinned multi-queue synthetic AF_XDP COPY-mode generator")]
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
    xsk_ring_size: u32,
    umem_frames_per_worker: usize,
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
    tx_ring_stalls: u64,
    send_would_block_retries: u64,
}

struct WorkerReport {
    packets: u64,
    bytes: u64,
    elapsed_s: f64,
    cpu_seconds: f64,
    min_mpps_1s: Option<f64>,
    min_gbps_1s: Option<f64>,
    stalls: u64,
}

struct WorkerConfig {
    ifindex: u32,
    cpu: usize,
    queue_id: u32,
    frame_size: usize,
    batch_size: usize,
    worker_count: usize,
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
            .with_context(|| format!("pin AF_XDP injector worker to CPU {cpu}"));
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

fn interface_index(interface: &str) -> Result<u32> {
    let name = CString::new(interface).context("interface contains a NUL byte")?;
    let ifindex = unsafe { libc::if_nametoindex(name.as_ptr()) };
    if ifindex == 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("resolve interface {interface}"));
    }
    Ok(ifindex)
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
    let source = 0x0a00_0001u32.wrapping_add(flow_id & 0x0000_ffff);
    let destination = 0x0a01_0001u32.wrapping_add(flow_id.rotate_left(7) & 0x0000_ffff);
    frame[ip + 12..ip + 16].copy_from_slice(&source.to_be_bytes());
    frame[ip + 16..ip + 20].copy_from_slice(&destination.to_be_bytes());
    let checksum = internet_checksum(&frame[ip..ip + 20]);
    frame[ip + 10..ip + 12].copy_from_slice(&checksum.to_be_bytes());
    let udp = ip + 20;
    let source_port = 1024u16.wrapping_add((flow_id & 0x7fff) as u16);
    let destination_port = 20_000u16.wrapping_add(((flow_id >> 4) & 0x7fff) as u16);
    frame[udp..udp + 2].copy_from_slice(&source_port.to_be_bytes());
    frame[udp + 2..udp + 4].copy_from_slice(&destination_port.to_be_bytes());
    frame[udp + 4..udp + 6].copy_from_slice(&((frame_size - udp) as u16).to_be_bytes());
    for (index, byte) in frame[udp + 8..].iter_mut().enumerate() {
        *byte = flow_id.wrapping_add(index as u32) as u8;
    }
    Ok(frame)
}

fn reclaim_completions(
    socket: &mut XskSocket,
    completions: &mut [u64],
    free_frames: &mut Vec<usize>,
    in_flight: &mut [bool],
) -> Result<usize> {
    let completed = socket.comp_queue.complete(completions);
    for &address in completions.iter().take(completed) {
        if address < UMEM_HEADROOM as u64 {
            bail!("AF_XDP completion address {} is below headroom", address);
        }
        let index = ((address as usize) - UMEM_HEADROOM) / UMEM_FRAME_SIZE;
        if index >= in_flight.len() {
            bail!("AF_XDP completion frame {} is out of range", index);
        }
        if !in_flight[index] {
            bail!(
                "AF_XDP returned duplicate/non-owned completion frame {}",
                index
            );
        }
        in_flight[index] = false;
        free_frames.push(index);
    }
    Ok(completed)
}

fn run_worker(config: WorkerConfig) -> Result<WorkerReport> {
    let WorkerConfig {
        ifindex,
        cpu,
        queue_id,
        frame_size,
        batch_size,
        worker_count,
        target_mpps,
        duration,
    } = config;
    pin_current_thread(cpu)?;
    let umem = Umem::new(&UmemConfig {
        frame_size: UMEM_FRAME_SIZE,
        frame_count: UMEM_FRAME_COUNT,
        fill_queue_size: XSK_RING_SIZE as usize,
        comp_queue_size: XSK_RING_SIZE as usize,
        headroom: UMEM_HEADROOM,
        use_huge_pages: false,
    })?;
    let mut socket = XskSocket::new(
        &umem,
        ifindex,
        queue_id,
        XskSocketConfig {
            rx_ring_size: XSK_RING_SIZE,
            tx_ring_size: XSK_RING_SIZE,
            fill_ring_size: XSK_RING_SIZE,
            comp_ring_size: XSK_RING_SIZE,
            bind_flags: XDP_COPY,
            xdp_flags: 0,
        },
    )
    .with_context(|| format!("create AF_XDP TX socket for queue {queue_id}"))?;
    for index in 0..UMEM_FRAME_COUNT {
        let packet = synthetic_frame(
            frame_size,
            (queue_id as usize * UMEM_FRAME_COUNT + index) as u32,
        )?;
        umem.get_frame_mut(index)?[..frame_size].copy_from_slice(&packet);
    }
    let mut free_frames: Vec<usize> = (0..UMEM_FRAME_COUNT).collect();
    let mut in_flight = vec![false; UMEM_FRAME_COUNT];
    let mut descriptors = Vec::with_capacity(batch_size);
    let mut descriptor_frames = Vec::with_capacity(batch_size);
    let mut completions = vec![0u64; batch_size.max(XSK_RING_SIZE as usize)];
    let started = Instant::now();
    let cpu_started = thread_cpu_time()?;
    let worker_target_pps = target_mpps * 1_000_000.0 / worker_count as f64;
    let mut packets = 0u64;
    let mut bytes = 0u64;
    let mut outstanding = 0usize;
    let mut stalls = 0u64;
    let mut window_started = Instant::now();
    let mut window_packets = 0u64;
    let mut min_mpps_1s: Option<f64> = None;
    let mut min_gbps_1s: Option<f64> = None;
    while started.elapsed() < duration {
        let completed = reclaim_completions(
            &mut socket,
            &mut completions,
            &mut free_frames,
            &mut in_flight,
        )?;
        outstanding = outstanding.saturating_sub(completed);
        let available = free_frames
            .len()
            .min(socket.tx_queue.available() as usize)
            .min(batch_size);
        if available == 0 {
            stalls = stalls.saturating_add(1);
            socket.wakeup()?;
            std::hint::spin_loop();
            continue;
        }
        descriptors.clear();
        descriptor_frames.clear();
        for &index in free_frames.iter().rev().take(available) {
            descriptors.push(XdpDesc {
                addr: umem.frame_addr(index) as u64,
                len: frame_size as u32,
                options: 0,
            });
            descriptor_frames.push(index);
        }
        let submitted = socket.tx_queue.transmit(&descriptors);
        if submitted == 0 {
            stalls = stalls.saturating_add(1);
            socket.wakeup()?;
            std::hint::spin_loop();
            continue;
        }
        for &index in descriptor_frames.iter().take(submitted) {
            if in_flight[index] {
                bail!("AF_XDP frame {} submitted twice", index);
            }
            in_flight[index] = true;
        }
        free_frames.truncate(free_frames.len() - submitted);
        outstanding += submitted;
        socket.wakeup()?;
        packets = packets.saturating_add(submitted as u64);
        bytes = bytes.saturating_add((submitted * frame_size) as u64);
        window_packets = window_packets.saturating_add(submitted as u64);
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
    let drain_started = Instant::now();
    while outstanding > 0 {
        let completed = reclaim_completions(
            &mut socket,
            &mut completions,
            &mut free_frames,
            &mut in_flight,
        )?;
        outstanding = outstanding.saturating_sub(completed);
        if outstanding == 0 {
            break;
        }
        if drain_started.elapsed() >= Duration::from_secs(2) {
            bail!(
                "AF_XDP TX drain timed out with {} descriptors outstanding",
                outstanding
            );
        }
        socket.wakeup()?;
        std::hint::spin_loop();
    }
    let elapsed_s = started.elapsed().as_secs_f64();
    let cpu_seconds = thread_cpu_time()?
        .checked_sub(cpu_started)
        .context("thread CPU clock moved backwards")?
        .as_secs_f64();
    drop(socket);
    drop(umem);
    Ok(WorkerReport {
        packets,
        bytes,
        elapsed_s,
        cpu_seconds,
        min_mpps_1s,
        min_gbps_1s,
        stalls,
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
    if args.batch_size == 0 || args.batch_size > XSK_RING_SIZE as usize {
        bail!("--batch-size must be in 1..={}", XSK_RING_SIZE);
    }
    if !(64..=1500).contains(&args.frame_size) {
        bail!("--frame-size must be in 64..=1500");
    }
    let cpus = parse_cpu_list(&args.worker_cpus)?;
    let ifindex = interface_index(&args.interface)?;
    let duration = Duration::from_secs(args.duration_s);
    let mut handles = Vec::with_capacity(cpus.len());
    for (worker_index, cpu) in cpus.iter().copied().enumerate() {
        let worker_count = cpus.len();
        let batch_size = args.batch_size;
        let frame_size = args.frame_size;
        let target_mpps = args.target_mpps;
        handles.push(
            thread::Builder::new()
                .name(format!("hft-xdp-tx-{worker_index}"))
                .spawn(move || {
                    run_worker(WorkerConfig {
                        ifindex,
                        cpu,
                        queue_id: worker_index as u32,
                        frame_size,
                        batch_size,
                        worker_count,
                        target_mpps,
                        duration,
                    })
                })
                .context("spawn AF_XDP injector worker")?,
        );
    }
    let mut reports = Vec::with_capacity(handles.len());
    for handle in handles {
        reports.push(
            handle
                .join()
                .map_err(|_| anyhow::anyhow!("AF_XDP injector worker panicked"))??,
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
    let tx_ring_stalls = reports.iter().map(|report| report.stalls).sum();
    let report = InjectorReport {
        schema_version: 1,
        scope: "physical_link_synthetic_small_packet_diagnostic",
        interface: args.interface,
        source: "synthetic_ipv4_udp_64B_xdp_v1",
        duration_s: elapsed,
        configured_target_mpps: args.target_mpps,
        frame_size_bytes: args.frame_size,
        backend: "af_xdp_skb_copy",
        xsk_ring_size: XSK_RING_SIZE,
        umem_frames_per_worker: UMEM_FRAME_COUNT,
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
        tx_ring_stalls,
        send_would_block_retries: tx_ring_stalls,
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
