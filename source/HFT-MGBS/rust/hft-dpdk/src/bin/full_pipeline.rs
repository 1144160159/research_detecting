use anyhow::{bail, Context, Result};
use clap::Parser;
use hft_capture::a09_fallback::{ExpectedPortableA09Identity, VerifiedLocalFallback};
use hft_capture::flow::{ClosedFlow, HftFlowTable};
use hft_capture::gpu::{ExpectedBackendIdentity, GpuDispatcher};
use hft_capture::metrics::{should_sample_packet_latency, MetricsReport, RuntimeMetrics};
use hft_capture::scheduler::BudgetScheduler;
use hft_dpdk::{
    DpdkEnvironment, DpdkEnvironmentConfig, DpdkPortConfiguration, DpdkRxQueue, DpdkStats,
};
use probe_agent::parser::PacketParser;
use serde::Serialize;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::{Component, Path, PathBuf};
use std::sync::atomic::Ordering;
use std::sync::{mpsc, Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const FLOW_EXPIRY_SCAN_PACKET_INTERVAL: u64 = 16_384;
const FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US: u64 = 1_000_000;
const MINIMUM_FULL_WINDOWS: usize = 15;

#[derive(Debug, Parser)]
#[command(
    about = "DPDK RX -> parser -> flow table -> budget scheduler -> verified GPU full pipeline"
)]
struct Args {
    #[arg(long)]
    candidate_id: String,
    #[arg(long)]
    frozen_thresholds_sha256: String,
    #[arg(long)]
    capture_pci: String,
    #[arg(long)]
    file_prefix: String,
    #[arg(long, value_delimiter = ',')]
    rx_cpus: Vec<usize>,
    #[arg(long)]
    main_cpu: usize,
    #[arg(long, default_value_t = 0)]
    realtime_priority: i32,
    #[arg(long, default_value_t = 21)]
    duration_s: u64,
    #[arg(long)]
    target_mpps: f64,
    #[arg(long, default_value_t = 256)]
    burst_size: usize,
    #[arg(long, default_value_t = 262_143)]
    mempool_capacity: u32,
    #[arg(long, default_value_t = 10_000)]
    minimum_link_speed_mbps: u32,
    #[arg(long, default_value = "listen://0.0.0.0:50052")]
    gpu_endpoint: String,
    #[arg(long)]
    expected_gpu_candidate: String,
    #[arg(long)]
    expected_gpu_schema: u32,
    #[arg(long)]
    expected_gpu_model_sha256: String,
    #[arg(long)]
    expected_gpu_inference_engine: String,
    #[arg(long)]
    local_fallback_artifact: Option<PathBuf>,
    #[arg(long)]
    local_fallback_quality_receipt: Option<PathBuf>,
    #[arg(long)]
    expected_local_fallback_quality_receipt_sha256: Option<String>,
    #[arg(long)]
    expected_local_fallback_artifact_sha256: Option<String>,
    #[arg(long)]
    expected_local_fallback_source_model_sha256: Option<String>,
    #[arg(long)]
    expected_local_fallback_numpy_engine_sha256: Option<String>,
    #[arg(long)]
    expected_local_fallback_campaign_contract_sha256: Option<String>,
    #[arg(long, default_value_t = 512)]
    batch_size: usize,
    #[arg(long, default_value_t = 5000.0)]
    budget_us: f64,
    #[arg(long, default_value_t = 0.50)]
    execution_budget_safety_ratio: f64,
    #[arg(long, default_value_t = 8192)]
    gpu_queue_capacity: usize,
    #[arg(long, default_value_t = 100)]
    gpu_timeout_ms: u64,
    #[arg(long, default_value_t = 5000)]
    gpu_startup_wait_ms: u64,
    #[arg(long, default_value_t = 1_000_000)]
    max_active_flows_per_queue: usize,
    #[arg(long, default_value_t = 1)]
    idle_timeout_s: u64,
    #[arg(long, default_value_t = 1)]
    active_timeout_s: u64,
    #[arg(long, default_value_t = 256)]
    max_payload_sample: usize,
    #[arg(long, default_value_t = 0.99)]
    minimum_key_flow_coverage: f64,
    #[arg(long)]
    max_gpu_batch_p99_us: f64,
    #[arg(long)]
    max_gpu_batch_p999_us: f64,
    #[arg(long)]
    platform_probe_head: String,
    #[arg(long)]
    platform_rust_tree: String,
    #[arg(long)]
    output: PathBuf,
}

#[derive(Debug, Serialize)]
struct WorkerReport {
    queue_id: usize,
    cpu: usize,
    packets: u64,
    bytes: u64,
    invalid_mbuf_frames: u64,
    parse_rejected: u64,
    closed_flows_delivered: u64,
    closed_flows_delivery_dropped: u64,
    rx_polls: u64,
    rx_zero_polls: u64,
    elapsed_s: f64,
    one_second_packets: Vec<u64>,
}

#[derive(Debug, Serialize)]
struct FullWindow {
    window_index: usize,
    packets: u64,
    mpps: f64,
    meets_target: bool,
}

#[derive(Debug, Serialize)]
struct DpdkFullPipelineReport {
    schema_version: u32,
    scope: &'static str,
    candidate_id: String,
    frozen_thresholds_sha256: String,
    port_configuration: DpdkPortConfiguration,
    port_stats_before: DpdkStats,
    port_stats_after: DpdkStats,
    port_stats_delta: DpdkStats,
    worker_reports: Vec<WorkerReport>,
    full_windows: Vec<FullWindow>,
    minimum_full_window_mpps: Option<f64>,
    pipeline_metrics: MetricsReport,
    hard_gate_errors: Vec<String>,
    data_path_qualified: bool,
    production_release_accepted: bool,
    final_pareto_ingestion_allowed: bool,
}

struct WorkerConfig {
    port_id: u16,
    queue_id: usize,
    cpu: usize,
    realtime_priority: i32,
    burst_size: usize,
    duration: Duration,
    duration_s: usize,
    start_epoch_us: u64,
    max_active_flows: usize,
    idle_timeout_s: u64,
    active_timeout_s: u64,
    max_payload_sample: usize,
}

fn main() -> Result<()> {
    let args = Args::parse();
    validate_args(&args)?;
    pin_current_thread(args.main_cpu)?;

    let identity = ExpectedBackendIdentity {
        candidate_id: args.expected_gpu_candidate.clone(),
        schema_version: args.expected_gpu_schema,
        model_sha256: args.expected_gpu_model_sha256.clone(),
        inference_engine: args.expected_gpu_inference_engine.clone(),
    };
    identity.validate()?;
    let remote_identity = identity.evidence_identity();
    let local_fallback = load_local_fallback(&args)?;
    let local_fallback_backend_identity = local_fallback
        .as_ref()
        .map(VerifiedLocalFallback::backend_identity)
        .unwrap_or_else(|| hft_capture::metrics::LOCAL_FALLBACK_BACKEND_IDENTITY.to_string());
    let local_fallback_quality_qualified = local_fallback.is_some();
    let metrics = Arc::new(RuntimeMetrics::default());
    let dispatcher = match local_fallback {
        Some(fallback) => GpuDispatcher::start_with_local_fallback(
            args.gpu_endpoint.clone(),
            args.batch_size,
            args.gpu_queue_capacity,
            Duration::from_millis(args.gpu_timeout_ms),
            Arc::clone(&metrics),
            false,
            identity,
            fallback,
        )?,
        None => GpuDispatcher::start(
            args.gpu_endpoint.clone(),
            args.batch_size,
            args.gpu_queue_capacity,
            Duration::from_millis(args.gpu_timeout_ms),
            Arc::clone(&metrics),
            false,
            identity,
        )?,
    };
    let gpu_ready = dispatcher.wait_ready(Duration::from_millis(args.gpu_startup_wait_ms));

    let environment = DpdkEnvironment::initialize(&DpdkEnvironmentConfig {
        capture_pci: args.capture_pci.clone(),
        file_prefix: args.file_prefix.clone(),
        main_cpu: args.main_cpu,
        queue_count: args.rx_cpus.len(),
        mempool_capacity: args.mempool_capacity,
        minimum_link_speed_mbps: args.minimum_link_speed_mbps,
    })?;
    let port_configuration = environment.configuration();
    let port_stats_before = environment.stats()?;
    let barrier = Arc::new(Barrier::new(args.rx_cpus.len() + 1));
    let (flow_tx, flow_rx) = mpsc::sync_channel::<Vec<ClosedFlow>>(4096);
    let start_epoch_us = epoch_us();
    let mut workers = Vec::with_capacity(args.rx_cpus.len());
    for (queue_id, cpu) in args.rx_cpus.iter().copied().enumerate() {
        let config = WorkerConfig {
            port_id: environment.port_id(),
            queue_id,
            cpu,
            realtime_priority: args.realtime_priority,
            burst_size: args.burst_size,
            duration: Duration::from_secs(args.duration_s),
            duration_s: args.duration_s as usize,
            start_epoch_us,
            max_active_flows: args.max_active_flows_per_queue,
            idle_timeout_s: args.idle_timeout_s,
            active_timeout_s: args.active_timeout_s,
            max_payload_sample: args.max_payload_sample,
        };
        let worker_barrier = Arc::clone(&barrier);
        let worker_metrics = Arc::clone(&metrics);
        let worker_tx = flow_tx.clone();
        workers.push(thread::spawn(move || {
            run_rx_worker(config, worker_barrier, worker_metrics, worker_tx)
        }));
    }
    drop(flow_tx);

    let scheduler = BudgetScheduler::new(args.budget_us, args.execution_budget_safety_ratio);
    barrier.wait();
    let capture_started = Instant::now();
    while workers.iter().any(|worker| !worker.is_finished()) {
        match flow_rx.recv_timeout(Duration::from_millis(1)) {
            Ok(flows) => dispatch_flows(flows, &scheduler, &dispatcher, &metrics),
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => break,
        }
    }
    while let Ok(flows) = flow_rx.try_recv() {
        dispatch_flows(flows, &scheduler, &dispatcher, &metrics);
    }

    let mut worker_reports = Vec::with_capacity(workers.len());
    let mut worker_errors = Vec::new();
    for (queue_id, worker) in workers.into_iter().enumerate() {
        match worker.join() {
            Ok(Ok(report)) => worker_reports.push(report),
            Ok(Err(error)) => worker_errors.push(format!("queue {queue_id} worker: {error:#}")),
            Err(_) => worker_errors.push(format!("queue {queue_id} worker panicked")),
        }
    }
    dispatcher.finish();
    let elapsed = capture_started.elapsed();
    let port_stats_after = environment.stats()?;
    let port_stats_delta = port_stats_after.delta(port_stats_before);
    let full_windows =
        aggregate_full_windows(&worker_reports, args.duration_s as usize, args.target_mpps);
    let minimum_full_window_mpps = full_windows
        .iter()
        .map(|window| window.mpps)
        .reduce(f64::min);
    let pipeline_metrics = metrics.report(
        "live_dpdk_port".to_string(),
        args.capture_pci.clone(),
        "dpdk_ethdev_full_pipeline".to_string(),
        args.platform_probe_head.clone(),
        args.platform_rust_tree.clone(),
        "dpdk_poll_monotonic_derived_epoch_unverified_for_kernel_e2e".to_string(),
        elapsed,
        port_stats_delta.receive_drop_count(),
        0,
        0.0,
        None,
        0,
        args.candidate_id.clone(),
        remote_identity,
        local_fallback_backend_identity,
        local_fallback_quality_qualified,
    );
    let mut hard_gate_errors = hard_gate_errors(
        &args,
        gpu_ready,
        &worker_reports,
        &full_windows,
        port_stats_delta,
        &pipeline_metrics,
    );
    hard_gate_errors.extend(worker_errors);
    let report = DpdkFullPipelineReport {
        schema_version: 1,
        scope: "hft_mgbs_dpdk_full_pipeline_raw_v1",
        candidate_id: args.candidate_id.clone(),
        frozen_thresholds_sha256: args.frozen_thresholds_sha256.clone(),
        port_configuration,
        port_stats_before,
        port_stats_after,
        port_stats_delta,
        worker_reports,
        full_windows,
        minimum_full_window_mpps,
        pipeline_metrics,
        data_path_qualified: hard_gate_errors.is_empty(),
        hard_gate_errors,
        production_release_accepted: false,
        final_pareto_ingestion_allowed: false,
    };
    write_json_create_only(&args.output, &report)?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    if !report.data_path_qualified {
        std::process::exit(2);
    }
    Ok(())
}

fn validate_args(args: &Args) -> Result<()> {
    if args.candidate_id.is_empty() || args.candidate_id != args.expected_gpu_candidate {
        bail!("candidate and expected GPU candidate must be the same non-empty identity");
    }
    require_sha256("frozen thresholds", &args.frozen_thresholds_sha256)?;
    require_sha256("platform head", &args.platform_probe_head)?;
    require_sha256("platform Rust tree", &args.platform_rust_tree)?;
    if args.rx_cpus.is_empty() || args.rx_cpus.len() > u16::MAX as usize {
        bail!("--rx-cpus must contain 1..={} CPUs", u16::MAX);
    }
    let mut unique = args.rx_cpus.clone();
    unique.sort_unstable();
    unique.dedup();
    if unique.len() != args.rx_cpus.len() || unique.contains(&args.main_cpu) {
        bail!("RX CPUs must be unique and must not contain the main CPU");
    }
    if args.duration_s < (MINIMUM_FULL_WINDOWS + 2) as u64 {
        bail!("duration must allow at least {MINIMUM_FULL_WINDOWS} complete one-second windows");
    }
    if !args.target_mpps.is_finite() || args.target_mpps <= 0.0 {
        bail!("target Mpps must be finite and positive");
    }
    if args.burst_size == 0 || args.burst_size > u16::MAX as usize {
        bail!("burst size must be in 1..={}", u16::MAX);
    }
    if args.batch_size == 0 || args.max_active_flows_per_queue == 0 {
        bail!("batch size and max active flows must be positive");
    }
    if !(0.0..=1.0).contains(&args.execution_budget_safety_ratio)
        || args.execution_budget_safety_ratio == 0.0
        || !(0.0..=1.0).contains(&args.minimum_key_flow_coverage)
    {
        bail!("coverage and execution safety ratios must be within their valid domains");
    }
    if args.realtime_priority < 0 || args.realtime_priority > 99 {
        bail!("realtime priority must be in 0..=99");
    }
    validate_output_path(&args.output)?;
    Ok(())
}

fn load_local_fallback(args: &Args) -> Result<Option<VerifiedLocalFallback>> {
    let values = [
        args.local_fallback_artifact.is_some(),
        args.local_fallback_quality_receipt.is_some(),
        args.expected_local_fallback_quality_receipt_sha256
            .is_some(),
        args.expected_local_fallback_artifact_sha256.is_some(),
        args.expected_local_fallback_source_model_sha256.is_some(),
        args.expected_local_fallback_numpy_engine_sha256.is_some(),
        args.expected_local_fallback_campaign_contract_sha256
            .is_some(),
    ];
    if values.iter().all(|value| !value) {
        return Ok(None);
    }
    if !values.iter().all(|value| *value) || args.expected_gpu_candidate != "A09" {
        bail!("local fallback requires all seven frozen A09 artifact and receipt arguments");
    }
    let expected = ExpectedPortableA09Identity {
        artifact_sha256: args
            .expected_local_fallback_artifact_sha256
            .clone()
            .unwrap(),
        source_model_sha256: args
            .expected_local_fallback_source_model_sha256
            .clone()
            .unwrap(),
        numpy_engine_sha256: args
            .expected_local_fallback_numpy_engine_sha256
            .clone()
            .unwrap(),
        campaign_contract_sha256: args
            .expected_local_fallback_campaign_contract_sha256
            .clone()
            .unwrap(),
    };
    VerifiedLocalFallback::load(
        args.local_fallback_artifact.as_ref().unwrap(),
        args.local_fallback_quality_receipt.as_ref().unwrap(),
        args.expected_local_fallback_quality_receipt_sha256
            .as_deref()
            .unwrap(),
        &expected,
    )
    .map(Some)
}

fn run_rx_worker(
    config: WorkerConfig,
    barrier: Arc<Barrier>,
    metrics: Arc<RuntimeMetrics>,
    flow_tx: mpsc::SyncSender<Vec<ClosedFlow>>,
) -> Result<WorkerReport> {
    pin_current_thread(config.cpu)?;
    set_realtime_priority(config.realtime_priority)?;
    let mut queue =
        DpdkRxQueue::register(config.port_id, config.queue_id as u16, config.burst_size)?;
    let mut flow_table = HftFlowTable::new(
        config.max_active_flows,
        config.idle_timeout_s,
        config.active_timeout_s,
        config.max_payload_sample,
    );
    let mut report = WorkerReport {
        queue_id: config.queue_id,
        cpu: config.cpu,
        packets: 0,
        bytes: 0,
        invalid_mbuf_frames: 0,
        parse_rejected: 0,
        closed_flows_delivered: 0,
        closed_flows_delivery_dropped: 0,
        rx_polls: 0,
        rx_zero_polls: 0,
        elapsed_s: 0.0,
        one_second_packets: vec![0; config.duration_s],
    };
    let mut pending = Vec::with_capacity(1024);
    let mut last_expire_packet = 0u64;
    let mut last_expire_timestamp_us = config.start_epoch_us;
    barrier.wait();
    let started = Instant::now();
    while started.elapsed() < config.duration {
        report.rx_polls = report.rx_polls.saturating_add(1);
        let burst = queue.poll();
        if burst.is_empty() {
            report.rx_zero_polls = report.rx_zero_polls.saturating_add(1);
            if report.rx_zero_polls % 64 == 0 {
                thread::yield_now();
            }
            continue;
        }
        for index in 0..burst.len() {
            let packet_started =
                should_sample_packet_latency(report.packets.saturating_add(1)).then(Instant::now);
            let frame = match burst.packet(index) {
                Ok(frame) => frame,
                Err(_) => {
                    report.invalid_mbuf_frames = report.invalid_mbuf_frames.saturating_add(1);
                    metrics.parse_rejected.fetch_add(1, Ordering::Relaxed);
                    continue;
                }
            };
            let observed = started.elapsed();
            let timestamp_us = config
                .start_epoch_us
                .saturating_add(observed.as_micros().min(u64::MAX as u128) as u64);
            report.packets = report.packets.saturating_add(1);
            report.bytes = report.bytes.saturating_add(frame.len() as u64);
            let window = observed.as_secs() as usize;
            if let Some(count) = report.one_second_packets.get_mut(window) {
                *count = count.saturating_add(1);
            }
            let received = metrics.packets_received.fetch_add(1, Ordering::Relaxed) + 1;
            match PacketParser::parse(frame, timestamp_us) {
                Ok(Some(parsed)) => {
                    metrics.packets_parsed.fetch_add(1, Ordering::Relaxed);
                    flow_table.update_into(&parsed, frame, &mut pending);
                }
                Ok(None) | Err(_) => {
                    report.parse_rejected = report.parse_rejected.saturating_add(1);
                    metrics.parse_rejected.fetch_add(1, Ordering::Relaxed);
                }
            }
            if received.saturating_sub(last_expire_packet) >= FLOW_EXPIRY_SCAN_PACKET_INTERVAL
                && timestamp_us.saturating_sub(last_expire_timestamp_us)
                    >= FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US
            {
                pending.extend(flow_table.expire(timestamp_us));
                last_expire_packet = received;
                last_expire_timestamp_us = timestamp_us;
            }
            if pending.len() >= 512 {
                deliver_flows(&flow_tx, &mut pending, &mut report, false)?;
            }
            if let Some(packet_started) = packet_started {
                metrics.observe_packet_latency(packet_started.elapsed());
            }
        }
    }
    pending.extend(flow_table.flush());
    deliver_flows(&flow_tx, &mut pending, &mut report, true)?;
    report.elapsed_s = started.elapsed().as_secs_f64();
    Ok(report)
}

fn deliver_flows(
    sender: &mpsc::SyncSender<Vec<ClosedFlow>>,
    pending: &mut Vec<ClosedFlow>,
    report: &mut WorkerReport,
    final_delivery: bool,
) -> Result<()> {
    if pending.is_empty() {
        return Ok(());
    }
    let count = pending.len() as u64;
    let flows = std::mem::take(pending);
    if final_delivery {
        sender.send(flows).context("deliver final closed flows")?;
        report.closed_flows_delivered = report.closed_flows_delivered.saturating_add(count);
        return Ok(());
    }
    match sender.try_send(flows) {
        Ok(()) => {
            report.closed_flows_delivered = report.closed_flows_delivered.saturating_add(count)
        }
        Err(mpsc::TrySendError::Full(_)) => {
            report.closed_flows_delivery_dropped =
                report.closed_flows_delivery_dropped.saturating_add(count)
        }
        Err(mpsc::TrySendError::Disconnected(_)) => bail!("closed-flow consumer disconnected"),
    }
    Ok(())
}

fn dispatch_flows(
    flows: Vec<ClosedFlow>,
    scheduler: &BudgetScheduler,
    dispatcher: &GpuDispatcher,
    metrics: &RuntimeMetrics,
) {
    metrics
        .flows_emitted
        .fetch_add(flows.len() as u64, Ordering::Relaxed);
    for flow in scheduler.schedule(flows, metrics) {
        dispatcher.enqueue(flow);
    }
}

fn aggregate_full_windows(
    workers: &[WorkerReport],
    duration_s: usize,
    target_mpps: f64,
) -> Vec<FullWindow> {
    if duration_s < 3 || workers.is_empty() {
        return Vec::new();
    }
    (1..duration_s - 1)
        .map(|window_index| {
            let packets = workers
                .iter()
                .map(|worker| {
                    worker
                        .one_second_packets
                        .get(window_index)
                        .copied()
                        .unwrap_or(0)
                })
                .sum();
            let mpps = packets as f64 / 1_000_000.0;
            FullWindow {
                window_index,
                packets,
                mpps,
                meets_target: mpps >= target_mpps,
            }
        })
        .collect()
}

fn hard_gate_errors(
    args: &Args,
    gpu_ready: bool,
    workers: &[WorkerReport],
    windows: &[FullWindow],
    stats: DpdkStats,
    metrics: &MetricsReport,
) -> Vec<String> {
    let mut errors = Vec::new();
    if !gpu_ready {
        errors.push("gpu.identity_ready=false".to_string());
    }
    if workers.len() != args.rx_cpus.len() {
        errors.push(format!(
            "workers.complete={}/{}",
            workers.len(),
            args.rx_cpus.len()
        ));
    }
    if windows.len() < MINIMUM_FULL_WINDOWS {
        errors.push(format!(
            "full_windows.count={}<{}",
            windows.len(),
            MINIMUM_FULL_WINDOWS
        ));
    }
    for window in windows.iter().filter(|window| !window.meets_target) {
        errors.push(format!(
            "full_window.{}.mpps={:.6}<{}",
            window.window_index, window.mpps, args.target_mpps
        ));
    }
    if stats.receive_drop_count() != 0 {
        errors.push(format!("dpdk.receive_drops={}", stats.receive_drop_count()));
    }
    if stats.oerrors != 0 {
        errors.push(format!("dpdk.tx_errors={}", stats.oerrors));
    }
    let invalid: u64 = workers
        .iter()
        .map(|worker| worker.invalid_mbuf_frames)
        .sum();
    let delivery_dropped: u64 = workers
        .iter()
        .map(|worker| worker.closed_flows_delivery_dropped)
        .sum();
    if invalid != 0 {
        errors.push(format!("dpdk.invalid_mbuf_frames={invalid}"));
    }
    if delivery_dropped != 0 {
        errors.push(format!(
            "internal.closed_flow_delivery_dropped={delivery_dropped}"
        ));
    }
    if metrics.parse_rejected != 0 {
        errors.push(format!("parser.rejected={}", metrics.parse_rejected));
    }
    if metrics.gpu_queue_full != 0
        || metrics.gpu_batches_failed != 0
        || metrics.gpu_backend_identity_failures != 0
        || metrics.gpu_worker_join_failures != 0
    {
        errors.push(format!(
            "gpu.failures=queue_full:{},batches:{},identity:{},join:{}",
            metrics.gpu_queue_full,
            metrics.gpu_batches_failed,
            metrics.gpu_backend_identity_failures,
            metrics.gpu_worker_join_failures
        ));
    }
    if metrics.budget_overrun_count != 0 {
        errors.push(format!("budget.overrun={}", metrics.budget_overrun_count));
    }
    if metrics.key_flows_total == 0 {
        errors.push("key_flow.eligible=0".to_string());
    }
    if metrics.key_flow_coverage.unwrap_or(0.0) < args.minimum_key_flow_coverage {
        errors.push(format!(
            "key_flow.coverage={:.9}<{}",
            metrics.key_flow_coverage.unwrap_or(0.0),
            args.minimum_key_flow_coverage
        ));
    }
    if !metrics
        .key_flow_conservation
        .eligible_equals_enqueue_outcomes
        || !metrics
            .key_flow_conservation
            .enqueued_equals_completion_outcomes
        || !metrics
            .flow_completion_conservation
            .remote_scored_equals_receipts_plus_truncated
    {
        errors.push("flow.conservation=false".to_string());
    }
    if metrics.gpu_batch_round_trip_latency.p99_us > args.max_gpu_batch_p99_us
        || metrics.gpu_batch_round_trip_latency.p999_us > args.max_gpu_batch_p999_us
    {
        errors.push(format!(
            "gpu.latency=p99:{:.6}/p999:{:.6}",
            metrics.gpu_batch_round_trip_latency.p99_us,
            metrics.gpu_batch_round_trip_latency.p999_us
        ));
    }
    errors
}

fn require_sha256(label: &str, value: &str) -> Result<()> {
    if value.len() != 64 || !value.bytes().all(|byte| byte.is_ascii_hexdigit()) {
        bail!("{label} SHA-256 must contain exactly 64 hexadecimal characters");
    }
    Ok(())
}

fn epoch_us() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_micros()
        .min(u64::MAX as u128) as u64
}

fn pin_current_thread(cpu: usize) -> Result<()> {
    let mut set = unsafe { std::mem::zeroed::<libc::cpu_set_t>() };
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
        bail!("pin current thread to CPU {cpu} failed: {status}");
    }
    Ok(())
}

fn set_realtime_priority(priority: i32) -> Result<()> {
    if priority == 0 {
        return Ok(());
    }
    let parameter = libc::sched_param {
        sched_priority: priority,
    };
    let status =
        unsafe { libc::pthread_setschedparam(libc::pthread_self(), libc::SCHED_FIFO, &parameter) };
    if status != 0 {
        bail!("set SCHED_FIFO priority {priority} failed: {status}");
    }
    Ok(())
}

fn validate_output_path(path: &Path) -> Result<PathBuf> {
    if !path.is_absolute() || path.file_name().is_none() {
        bail!("output must be an absolute file path");
    }
    if path
        .components()
        .any(|component| matches!(component, Component::CurDir | Component::ParentDir))
    {
        bail!("output path may not contain lexical traversal components");
    }
    if std::fs::symlink_metadata(path).is_ok() {
        bail!("output already exists: {}", path.display());
    }
    let parent = path.parent().context("output path has no parent")?;
    let mut current = PathBuf::new();
    for component in parent.components() {
        current.push(component.as_os_str());
        let metadata = std::fs::symlink_metadata(&current).with_context(|| {
            format!(
                "output parent component is unavailable: {}",
                current.display()
            )
        })?;
        if metadata.file_type().is_symlink() || !metadata.is_dir() {
            bail!(
                "output parent component is not a real directory: {}",
                current.display()
            );
        }
    }
    let canonical = std::fs::canonicalize(parent)
        .with_context(|| format!("canonicalize output parent {}", parent.display()))?;
    if canonical != parent {
        bail!("output parent canonical identity differs from its declared path");
    }
    Ok(canonical)
}

fn write_json_create_only(path: &Path, value: &impl Serialize) -> Result<()> {
    let parent = validate_output_path(path)?;
    let name = path
        .file_name()
        .context("output path has no filename")?
        .to_string_lossy();
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .context("system clock predates UNIX epoch")?
        .as_nanos();
    let temporary = parent.join(format!(".{name}.{}.{}.tmp", std::process::id(), nonce));
    let mut output = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&temporary)
        .with_context(|| format!("create temporary output {}", temporary.display()))?;
    serde_json::to_writer_pretty(&mut output, value)?;
    output.write_all(b"\n")?;
    output.sync_all()?;
    std::fs::hard_link(&temporary, path)
        .with_context(|| format!("seal output {}", path.display()))?;
    std::fs::remove_file(&temporary)
        .with_context(|| format!("remove temporary output {}", temporary.display()))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{aggregate_full_windows, require_sha256, validate_output_path, WorkerReport};
    use std::path::PathBuf;

    fn worker(packets: Vec<u64>) -> WorkerReport {
        WorkerReport {
            queue_id: 0,
            cpu: 1,
            packets: packets.iter().sum(),
            bytes: 0,
            invalid_mbuf_frames: 0,
            parse_rejected: 0,
            closed_flows_delivered: 0,
            closed_flows_delivery_dropped: 0,
            rx_polls: 0,
            rx_zero_polls: 0,
            elapsed_s: 0.0,
            one_second_packets: packets,
        }
    }

    #[test]
    fn output_path_must_be_absolute_and_have_an_existing_real_parent() {
        assert!(validate_output_path(&PathBuf::from("relative.json")).is_err());
        let base = std::env::temp_dir().join(format!(
            "hft-dpdk-output-test-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir(&base).unwrap();
        assert_eq!(
            validate_output_path(&base.join("result.json")).unwrap(),
            base
        );
        std::fs::remove_dir(&base).unwrap();
    }

    #[test]
    fn full_windows_exclude_boundary_seconds_and_sum_queues() {
        let windows = aggregate_full_windows(
            &[
                worker(vec![1, 1_400_000, 1_395_000, 1]),
                worker(vec![1, 1_400_000, 1_395_000, 1]),
            ],
            4,
            2.79,
        );
        assert_eq!(windows.len(), 2);
        assert!(windows[0].meets_target);
        assert!(windows[1].meets_target);
    }

    #[test]
    fn frozen_hash_is_strict() {
        assert!(require_sha256("test", &"a".repeat(64)).is_ok());
        assert!(require_sha256("test", "a").is_err());
        assert!(require_sha256("test", &"z".repeat(64)).is_err());
    }
}
