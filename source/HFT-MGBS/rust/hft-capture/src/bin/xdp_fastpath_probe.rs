use anyhow::{bail, Context, Result};
use clap::{Parser, ValueEnum};
use hft_capture::xdp_capture::{HftXdpCapture, HftXdpMode};
use probe_agent::capture::Capturer;
use serde::Serialize;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const LATENCY_SAMPLE_STRIDE: u64 = 1024;
const MAX_LATENCY_SAMPLES: usize = 1_000_000;

#[derive(Clone, Copy, Debug, ValueEnum)]
enum ProbeMode {
    Native,
    Skb,
}

#[derive(Debug, Parser)]
#[command(about = "Borrowed-UMEM AF_XDP capture-only capacity probe")]
struct Args {
    #[arg(long)]
    interface: String,
    #[arg(long, value_enum, default_value = "skb")]
    mode: ProbeMode,
    #[arg(long, default_value_t = 0)]
    queue_count: u32,
    #[arg(long, default_value_t = 4096)]
    frames_per_queue: usize,
    #[arg(long, default_value_t = 256)]
    receive_batch_size: usize,
    #[arg(long)]
    ebpf_object: PathBuf,
    #[arg(long, default_value_t = 15)]
    duration_s: u64,
    #[arg(long)]
    output: PathBuf,
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
struct ProbeReport {
    schema_version: u32,
    scope: &'static str,
    interface: String,
    mode: &'static str,
    duration_s: f64,
    packets: u64,
    bytes: u64,
    capture_packets_dropped: u64,
    achieved_mpps: f64,
    achieved_gbps: f64,
    process_cpu_cores_average: f64,
    queue_packets: Vec<u64>,
    latency_sample_stride: u64,
    kernel_entry_to_borrowed_callback_latency: Percentiles,
    payload_guard: u64,
    final_pareto_ingestion_allowed: bool,
}

fn process_cpu_time() -> Result<Duration> {
    let mut value: libc::timespec = unsafe { std::mem::zeroed() };
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

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    if args.duration_s == 0 {
        bail!("--duration-s must be positive");
    }
    if !(1..=256).contains(&args.receive_batch_size) || !args.receive_batch_size.is_power_of_two() {
        bail!("--receive-batch-size must be a power of two in 1..=256");
    }
    let mode = match args.mode {
        ProbeMode::Native => HftXdpMode::Native,
        ProbeMode::Skb => HftXdpMode::Skb,
    };
    let mut capture = HftXdpCapture::new(
        args.interface.clone(),
        mode,
        args.queue_count,
        args.frames_per_queue,
        args.receive_batch_size,
        args.ebpf_object,
        None,
    )?;
    capture.start().await?;
    let started = Instant::now();
    let cpu_started = process_cpu_time()?;
    let duration = Duration::from_secs(args.duration_s);
    let mut packets = 0u64;
    let mut bytes = 0u64;
    let mut queue_packets = vec![0u64; 64];
    let mut latency_samples = Vec::with_capacity(64 * 1024);
    let mut payload_guard = 0u64;
    while started.elapsed() < duration {
        capture.poll_borrowed(|queue_id, data, timestamp_us| {
            packets = packets.saturating_add(1);
            bytes = bytes.saturating_add(data.len() as u64);
            if let Some(counter) = queue_packets.get_mut(queue_id as usize) {
                *counter = counter.saturating_add(1);
            }
            if let Some(first) = data.first() {
                payload_guard = payload_guard.wrapping_add(u64::from(*first));
            }
            if packets.is_multiple_of(LATENCY_SAMPLE_STRIDE)
                && latency_samples.len() < MAX_LATENCY_SAMPLES
            {
                let now_us = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .context("system clock precedes UNIX epoch")?
                    .as_micros()
                    .min(u64::MAX as u128) as u64;
                if let Some(elapsed) = now_us.checked_sub(timestamp_us) {
                    latency_samples.push(elapsed);
                }
            }
            Ok(())
        })?;
    }
    capture.stop().await?;
    let elapsed = started.elapsed().as_secs_f64();
    let cpu_elapsed = process_cpu_time()?
        .checked_sub(cpu_started)
        .context("process CPU clock moved backwards")?
        .as_secs_f64();
    let capture_stats = capture.stats();
    while queue_packets.last() == Some(&0) {
        queue_packets.pop();
    }
    let report = ProbeReport {
        schema_version: 1,
        scope: "borrowed_umem_capture_only_diagnostic",
        interface: args.interface,
        mode: match mode {
            HftXdpMode::Native => "native",
            HftXdpMode::Skb => "skb",
        },
        duration_s: elapsed,
        packets,
        bytes,
        capture_packets_dropped: capture_stats.packets_dropped,
        achieved_mpps: packets as f64 / elapsed / 1_000_000.0,
        achieved_gbps: bytes as f64 * 8.0 / elapsed / 1_000_000_000.0,
        process_cpu_cores_average: cpu_elapsed / elapsed,
        queue_packets,
        latency_sample_stride: LATENCY_SAMPLE_STRIDE,
        kernel_entry_to_borrowed_callback_latency: percentiles(latency_samples),
        payload_guard,
        final_pareto_ingestion_allowed: false,
    };
    if let Some(parent) = args.output.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut output = File::create(&args.output)
        .with_context(|| format!("create probe output {}", args.output.display()))?;
    serde_json::to_writer_pretty(&mut output, &report)?;
    output.write_all(b"\n")?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}
