use anyhow::{bail, Context, Result};
use clap::Parser;
use hft_capture::xdp_capture::{HftXdpCapture, HftXdpMode, HftXdpQueueWorker};
use probe_agent::capture::Capturer;
use serde::Serialize;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const LATENCY_SAMPLE_STRIDE: u64 = 1024;
const MAX_LATENCY_SAMPLES_PER_WORKER: usize = 250_000;

#[derive(Debug, Parser)]
#[command(about = "Per-queue sharded borrowed-UMEM AF_XDP capacity probe")]
struct Args {
    #[arg(long)]
    interface: String,
    #[arg(long, default_value_t = 0)]
    queue_count: u32,
    #[arg(long, default_value_t = 4096)]
    frames_per_queue: usize,
    #[arg(long, default_value_t = 256)]
    receive_batch_size: usize,
    #[arg(long)]
    ebpf_object: PathBuf,
    #[arg(long)]
    worker_cpus: String,
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
    architecture: &'static str,
    interface: String,
    mode: &'static str,
    duration_s: f64,
    packets: u64,
    bytes: u64,
    capture_packets_dropped: u64,
    achieved_mpps: f64,
    achieved_gbps: f64,
    process_cpu_cores_average: f64,
    worker_cpu_ids: Vec<usize>,
    worker_cpu_cores_average: Vec<f64>,
    queue_packets: Vec<u64>,
    latency_sample_stride: u64,
    kernel_entry_to_borrowed_callback_latency: Percentiles,
    payload_guard: u64,
    final_pareto_ingestion_allowed: bool,
}

struct WorkerOutcome {
    worker: HftXdpQueueWorker,
    cpu_seconds: f64,
    latency_samples: Vec<u64>,
    payload_guard: u64,
    error: Option<String>,
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
            .with_context(|| format!("pin worker to CPU {cpu}"));
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

fn run_worker(mut worker: HftXdpQueueWorker, cpu: usize, deadline: Instant) -> WorkerOutcome {
    let mut latency_samples = Vec::with_capacity(64 * 1024);
    let mut payload_guard = 0u64;
    let mut sampled_packet_count = 0u64;
    let result = (|| -> Result<f64> {
        pin_current_thread(cpu)?;
        let cpu_started = thread_cpu_time()?;
        while Instant::now() < deadline {
            worker.poll_borrowed_busy(|_queue_id, data, timestamp_us| {
                sampled_packet_count = sampled_packet_count.saturating_add(1);
                if let Some(first) = data.first() {
                    payload_guard = payload_guard.wrapping_add(u64::from(*first));
                }
                if sampled_packet_count.is_multiple_of(LATENCY_SAMPLE_STRIDE)
                    && latency_samples.len() < MAX_LATENCY_SAMPLES_PER_WORKER
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
        Ok(thread_cpu_time()?
            .checked_sub(cpu_started)
            .context("thread CPU clock moved backwards")?
            .as_secs_f64())
    })();
    WorkerOutcome {
        worker,
        cpu_seconds: result.as_ref().copied().unwrap_or(0.0),
        latency_samples,
        payload_guard,
        error: result.err().map(|error| format!("{error:#}")),
    }
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
    let worker_cpus = parse_cpu_list(&args.worker_cpus)?;
    let mut capture = HftXdpCapture::new(
        args.interface.clone(),
        HftXdpMode::Skb,
        args.queue_count,
        args.frames_per_queue,
        args.receive_batch_size,
        args.ebpf_object,
        None,
    )?;
    capture.start().await?;
    let workers = capture.take_queue_workers()?;
    if workers.len() != worker_cpus.len() {
        capture.restore_queue_workers(workers)?;
        capture.stop().await?;
        bail!(
            "worker CPU count {} does not match active RX queue count",
            worker_cpus.len()
        );
    }

    let started = Instant::now();
    let deadline = started + Duration::from_secs(args.duration_s);
    let mut handles = Vec::with_capacity(workers.len());
    for (worker, cpu) in workers.into_iter().zip(worker_cpus.iter().copied()) {
        handles.push(
            thread::Builder::new()
                .name(format!("hft-xdp-q{}", worker.queue_id()))
                .spawn(move || run_worker(worker, cpu, deadline))
                .context("spawn XDP queue worker")?,
        );
    }

    let mut returned_workers = Vec::with_capacity(handles.len());
    let mut worker_cpu_seconds = Vec::with_capacity(handles.len());
    let mut latency_samples = Vec::new();
    let mut payload_guard = 0u64;
    let mut first_error = None;
    for handle in handles {
        let outcome = handle
            .join()
            .map_err(|_| anyhow::anyhow!("XDP queue worker panicked"))?;
        if first_error.is_none() {
            first_error = outcome.error;
        }
        worker_cpu_seconds.push(outcome.cpu_seconds);
        latency_samples.extend(outcome.latency_samples);
        payload_guard = payload_guard.wrapping_add(outcome.payload_guard);
        returned_workers.push(outcome.worker);
    }
    let elapsed = started.elapsed().as_secs_f64();
    let mut queue_packets = vec![0u64; returned_workers.len()];
    let mut packets = 0u64;
    let mut bytes = 0u64;
    for worker in &returned_workers {
        let queue_id = worker.queue_id() as usize;
        queue_packets[queue_id] = worker.packets();
        packets = packets.saturating_add(worker.packets());
        bytes = bytes.saturating_add(worker.bytes());
    }
    capture.restore_queue_workers(returned_workers)?;
    capture.stop().await?;
    if let Some(error) = first_error {
        bail!("XDP queue worker failed: {}", error);
    }
    let capture_stats = capture.stats();
    let report = ProbeReport {
        schema_version: 1,
        scope: "borrowed_umem_capture_only_diagnostic",
        architecture: "one_thread_per_xsk_rx_queue",
        interface: args.interface,
        mode: "skb",
        duration_s: elapsed,
        packets,
        bytes,
        capture_packets_dropped: capture_stats.packets_dropped,
        achieved_mpps: packets as f64 / elapsed / 1_000_000.0,
        achieved_gbps: bytes as f64 * 8.0 / elapsed / 1_000_000_000.0,
        process_cpu_cores_average: worker_cpu_seconds.iter().sum::<f64>() / elapsed,
        worker_cpu_ids: worker_cpus,
        worker_cpu_cores_average: worker_cpu_seconds
            .into_iter()
            .map(|seconds| seconds / elapsed)
            .collect(),
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
