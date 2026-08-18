use anyhow::{bail, Context, Result};
use clap::{Parser, ValueEnum};
use hft_capture::a09_fallback::{ExpectedPortableA09Identity, VerifiedLocalFallback};
use hft_capture::flow::{ClosedFlow, HftFlowTable};
use hft_capture::gpu::{ExpectedBackendIdentity, GpuDispatcher};
use hft_capture::kernel_af_packet::{require_linux, KernelTimestampAfPacket};
use hft_capture::metrics::{should_sample_packet_latency, RuntimeMetrics};
use hft_capture::scheduler::BudgetScheduler;
use hft_capture::xdp_capture::{HftXdpCapture, HftXdpMode};
use probe_agent::capture::{
    create_capturer, CaptureConfig, CaptureMode, Capturer, PcapReplayer, ReplaySpeed,
};
use probe_agent::parser::PacketParser;
use std::fs::File;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::Ordering;
use std::sync::Arc;
use std::time::{Duration, Instant};

const PLATFORM_HEAD: &str = "a6df362989ac3d19d0f55d2520c3e64e8a33d04d";
const PLATFORM_RUST_TREE: &str = "e642d4beb27c385ccc4c43f7420cbae1c89def9a";
const FLOW_EXPIRY_SCAN_PACKET_INTERVAL: u64 = 16_384;
const FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US: u64 = 1_000_000;

#[derive(Clone, Debug, ValueEnum)]
enum Driver {
    Xdp,
    XdpSkb,
    AfPacket,
    AfPacketTs,
}

#[derive(Clone, Copy, Debug, ValueEnum)]
enum FallbackDriver {
    AfPacketTs,
}

#[derive(Debug, Parser)]
#[command(about = "HFT-MGBS Rust capture, feature extraction and bounded GPU dispatch")]
struct Args {
    #[arg(long, conflicts_with = "interface")]
    pcap: Option<PathBuf>,
    #[arg(long, conflicts_with = "pcap")]
    interface: Option<String>,
    #[arg(long, value_enum, default_value = "af-packet")]
    driver: Driver,
    #[arg(long, value_enum)]
    capture_fallback_driver: Option<FallbackDriver>,
    #[arg(long)]
    diagnostic_xdp_fail_after_packets: Option<u64>,
    #[arg(long, default_value_t = false)]
    allow_diagnostic_fault_injection: bool,
    #[arg(long, default_value_t = 0)]
    xdp_queue_count: u32,
    #[arg(long, default_value_t = 4096)]
    xdp_frames_per_queue: usize,
    #[arg(long, default_value_t = 64)]
    xdp_receive_batch_size: usize,
    #[arg(long)]
    xdp_ebpf_object: Option<PathBuf>,
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
    #[arg(long)]
    metrics: PathBuf,
    #[arg(long, default_value_t = 512)]
    batch_size: usize,
    #[arg(long, default_value_t = 1000)]
    feature_flush_us: u64,
    #[arg(long, default_value_t = 5000.0)]
    budget_us: f64,
    #[arg(long, default_value_t = 0.50)]
    execution_budget_safety_ratio: f64,
    #[arg(long, default_value_t = 0.80)]
    budget_target_utilization: f64,
    #[arg(long, default_value_t = 0.20)]
    budget_ema_alpha: f64,
    #[arg(long, default_value_t = 0.25)]
    budget_minimum_ratio: f64,
    #[arg(long, default_value_t = 8192)]
    gpu_queue_capacity: usize,
    #[arg(long, default_value_t = 100)]
    gpu_timeout_ms: u64,
    #[arg(long, default_value_t = 5000)]
    gpu_startup_wait_ms: u64,
    #[arg(long, default_value_t = 1_000_000)]
    max_active_flows: usize,
    #[arg(long, default_value_t = 120)]
    idle_timeout_s: u64,
    #[arg(long, default_value_t = 1800)]
    active_timeout_s: u64,
    #[arg(long, default_value_t = 256)]
    max_payload_sample: usize,
    #[arg(long)]
    max_packets: Option<u64>,
    #[arg(long)]
    max_duration_s: Option<u64>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    if args.pcap.is_none() && args.interface.is_none() {
        bail!("one of --pcap or --interface is required");
    }
    if !(0.0..=1.0).contains(&args.execution_budget_safety_ratio)
        || args.execution_budget_safety_ratio == 0.0
    {
        bail!("--execution-budget-safety-ratio must be in (0, 1]");
    }
    if !(0.0..=1.0).contains(&args.budget_target_utilization)
        || args.budget_target_utilization == 0.0
    {
        bail!("--budget-target-utilization must be in (0, 1]");
    }
    if !(0.0..=1.0).contains(&args.budget_ema_alpha) || args.budget_ema_alpha == 0.0 {
        bail!("--budget-ema-alpha must be in (0, 1]");
    }
    if !(0.0..=args.execution_budget_safety_ratio).contains(&args.budget_minimum_ratio)
        || args.budget_minimum_ratio == 0.0
    {
        bail!("--budget-minimum-ratio must be in (0, execution budget safety ratio]");
    }
    if args.max_duration_s == Some(0) {
        bail!("--max-duration-s must be positive");
    }
    if args.feature_flush_us == 0 {
        bail!("--feature-flush-us must be positive");
    }
    if args.xdp_frames_per_queue == 0 {
        bail!("--xdp-frames-per-queue must be positive");
    }
    if !(1..=256).contains(&args.xdp_receive_batch_size)
        || !args.xdp_receive_batch_size.is_power_of_two()
    {
        bail!("--xdp-receive-batch-size must be a power of two in 1..=256");
    }
    if args.capture_fallback_driver.is_some() && !matches!(args.driver, Driver::XdpSkb) {
        bail!("capture fallback is currently supported only for --driver xdp-skb");
    }
    if args.diagnostic_xdp_fail_after_packets.is_some() && !args.allow_diagnostic_fault_injection {
        bail!(
            "--diagnostic-xdp-fail-after-packets requires \
             --allow-diagnostic-fault-injection"
        );
    }
    if args.diagnostic_xdp_fail_after_packets == Some(0) {
        bail!("--diagnostic-xdp-fail-after-packets must be positive");
    }
    let (
        source_kind,
        source,
        mut driver_name,
        timestamp_divisor,
        mut timestamp_provenance,
        kernel_timestamp_verified,
        mut capturer,
    ) = build_capturer(&args).await?;
    let metrics = Arc::new(RuntimeMetrics::default());
    let expected_backend = ExpectedBackendIdentity {
        candidate_id: args.expected_gpu_candidate.clone(),
        schema_version: args.expected_gpu_schema,
        model_sha256: args.expected_gpu_model_sha256.clone(),
        inference_engine: args.expected_gpu_inference_engine.clone(),
    };
    let local_fallback = load_local_fallback(&args)?;
    let local_fallback_backend_identity = local_fallback
        .as_ref()
        .map(VerifiedLocalFallback::backend_identity)
        .unwrap_or_else(|| hft_capture::metrics::LOCAL_FALLBACK_BACKEND_IDENTITY.to_string());
    let local_fallback_quality_qualified = local_fallback.is_some();
    let dispatcher = match local_fallback {
        Some(fallback) => GpuDispatcher::start_with_local_fallback(
            args.gpu_endpoint.clone(),
            args.batch_size,
            args.gpu_queue_capacity,
            Duration::from_millis(args.gpu_timeout_ms),
            Arc::clone(&metrics),
            kernel_timestamp_verified,
            expected_backend,
            fallback,
        )?,
        None => GpuDispatcher::start(
            args.gpu_endpoint.clone(),
            args.batch_size,
            args.gpu_queue_capacity,
            Duration::from_millis(args.gpu_timeout_ms),
            Arc::clone(&metrics),
            kernel_timestamp_verified,
            expected_backend,
        )?,
    };
    let _gpu_ready = dispatcher.wait_ready(Duration::from_millis(args.gpu_startup_wait_ms));
    let mut scheduler = BudgetScheduler::with_adaptive_feedback(
        args.budget_us,
        args.execution_budget_safety_ratio,
        args.budget_target_utilization,
        args.budget_minimum_ratio,
        args.budget_ema_alpha,
    )
    .map_err(anyhow::Error::msg)?;
    let mut flow_table = HftFlowTable::new(
        args.max_active_flows,
        args.idle_timeout_s,
        args.active_timeout_s,
        args.max_payload_sample,
    );
    let mut pending: Vec<ClosedFlow> = Vec::with_capacity(args.batch_size);
    let started = Instant::now();
    let mut capture_drop_accumulated = 0u64;
    let mut capture_driver_fallback_count = 0u64;
    let mut capture_driver_fallback_recovery_ms = 0.0f64;
    let mut capture_driver_fallback_reason: Option<String> = None;
    let mut capture_driver_fallback_started_received: Option<u64> = None;
    if let Err(error) = capturer.start().await {
        if args.capture_fallback_driver.is_none() {
            return Err(error).context("start capture driver");
        }
        let recovery_started = Instant::now();
        stop_and_accumulate_capture_drops(
            capturer.as_mut(),
            &mut capture_drop_accumulated,
            "clean primary capture driver after startup failure",
        )
        .await?;
        capturer = build_started_af_packet_fallback(&args).await?;
        capture_driver_fallback_count = 1;
        capture_driver_fallback_recovery_ms = recovery_started.elapsed().as_secs_f64() * 1000.0;
        capture_driver_fallback_reason = Some(format!("primary_start_failed: {error:#}"));
        capture_driver_fallback_started_received = Some(0);
        driver_name = "xdp_skb_to_af_packet_ts".to_string();
        timestamp_provenance =
            "mixed_xdp_bpf_ktime_and_kernel_software_receive_realtime".to_string();
        eprintln!(
            "hft_capture_fallback phase=startup recovery_ms={:.6} reason={:#}",
            capture_driver_fallback_recovery_ms, error
        );
    }
    let mut last_expire_packet = 0u64;
    let mut last_expire_timestamp_us = 0u64;
    let mut last_timestamp_us = 0u64;

    'capture: loop {
        if pending.first().is_some_and(|flow| {
            flow.ready_at.elapsed() >= Duration::from_micros(args.feature_flush_us)
        }) {
            dispatch_pending(
                &mut pending,
                &mut scheduler,
                &dispatcher,
                &metrics,
                args.batch_size,
                args.gpu_queue_capacity,
            );
        }
        if args
            .max_duration_s
            .is_some_and(|limit| started.elapsed() >= Duration::from_secs(limit))
        {
            break;
        }
        let batch = match capturer.poll() {
            Ok(batch) => batch,
            Err(error)
                if args.capture_fallback_driver.is_some() && capture_driver_fallback_count == 0 =>
            {
                let recovery_started = Instant::now();
                stop_and_accumulate_capture_drops(
                    capturer.as_mut(),
                    &mut capture_drop_accumulated,
                    "clean primary capture driver before runtime fallback",
                )
                .await?;
                capturer = build_started_af_packet_fallback(&args).await?;
                capture_driver_fallback_count = 1;
                capture_driver_fallback_recovery_ms =
                    recovery_started.elapsed().as_secs_f64() * 1000.0;
                capture_driver_fallback_reason = Some(format!("primary_poll_failed: {error:#}"));
                capture_driver_fallback_started_received =
                    Some(metrics.packets_received.load(Ordering::Relaxed));
                driver_name = "xdp_skb_to_af_packet_ts".to_string();
                timestamp_provenance =
                    "mixed_xdp_bpf_ktime_and_kernel_software_receive_realtime".to_string();
                eprintln!(
                    "hft_capture_fallback phase=runtime recovery_ms={:.6} \
                     received_before={} reason={:#}",
                    capture_driver_fallback_recovery_ms,
                    capture_driver_fallback_started_received.unwrap_or(0),
                    error
                );
                continue;
            }
            Err(error) => return Err(error).context("poll capture driver"),
        };
        let Some(batch) = batch else {
            if args.interface.is_some() {
                continue;
            }
            break;
        };
        for (frame, raw_timestamp) in batch.iter() {
            if args
                .max_duration_s
                .is_some_and(|limit| started.elapsed() >= Duration::from_secs(limit))
            {
                break 'capture;
            }
            let timestamp_us = raw_timestamp / timestamp_divisor;
            last_timestamp_us = last_timestamp_us.max(timestamp_us);
            let received = metrics
                .packets_received
                .fetch_add(1, Ordering::Relaxed)
                .saturating_add(1);
            let packet_started = should_sample_packet_latency(received).then(Instant::now);
            match PacketParser::parse(frame, timestamp_us) {
                Ok(Some(parsed)) => {
                    metrics.packets_parsed.fetch_add(1, Ordering::Relaxed);
                    flow_table.update_into(&parsed, frame, &mut pending);
                }
                Ok(None) | Err(_) => {
                    metrics.parse_rejected.fetch_add(1, Ordering::Relaxed);
                }
            }
            if should_expire_flows(
                received,
                last_expire_packet,
                last_timestamp_us,
                last_expire_timestamp_us,
            ) {
                pending.extend(flow_table.expire(last_timestamp_us));
                last_expire_packet = received;
                last_expire_timestamp_us = last_timestamp_us;
            }
            if pending.len() >= args.batch_size {
                dispatch_pending(
                    &mut pending,
                    &mut scheduler,
                    &dispatcher,
                    &metrics,
                    args.batch_size,
                    args.gpu_queue_capacity,
                );
            }
            if let Some(packet_started) = packet_started {
                metrics.observe_packet_latency(packet_started.elapsed());
            }
            if args.max_packets.is_some_and(|limit| received >= limit) {
                break 'capture;
            }
        }
    }
    pending.extend(flow_table.flush());
    dispatch_pending(
        &mut pending,
        &mut scheduler,
        &dispatcher,
        &metrics,
        args.batch_size,
        args.gpu_queue_capacity,
    );
    capturer.stop().await?;
    let capture_stats = capturer.stats();
    capture_drop_accumulated =
        capture_drop_accumulated.saturating_add(capture_stats.packets_dropped);
    dispatcher.finish();
    let fallback_packets = capture_driver_fallback_started_received
        .map(|before| {
            metrics
                .packets_received
                .load(Ordering::Relaxed)
                .saturating_sub(before)
        })
        .unwrap_or(0);
    let report = metrics.report(
        source_kind,
        source,
        driver_name,
        PLATFORM_HEAD.to_string(),
        PLATFORM_RUST_TREE.to_string(),
        timestamp_provenance,
        started.elapsed(),
        capture_drop_accumulated,
        capture_driver_fallback_count,
        capture_driver_fallback_recovery_ms,
        capture_driver_fallback_reason,
        fallback_packets,
        args.expected_gpu_candidate.clone(),
        ExpectedBackendIdentity {
            candidate_id: args.expected_gpu_candidate.clone(),
            schema_version: args.expected_gpu_schema,
            model_sha256: args.expected_gpu_model_sha256.clone(),
            inference_engine: args.expected_gpu_inference_engine.clone(),
        }
        .evidence_identity(),
        local_fallback_backend_identity,
        local_fallback_quality_qualified,
    );
    if let Some(parent) = args.metrics.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut output = File::create(&args.metrics)
        .with_context(|| format!("create metrics file {}", args.metrics.display()))?;
    serde_json::to_writer_pretty(&mut output, &report)?;
    output.write_all(b"\n")?;
    println!("{}", serde_json::to_string_pretty(&report)?);
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

async fn stop_and_accumulate_capture_drops(
    capturer: &mut dyn Capturer,
    accumulated: &mut u64,
    error_context: &str,
) -> Result<()> {
    capturer.stop().await.context(error_context.to_string())?;
    *accumulated = (*accumulated).saturating_add(capturer.stats().packets_dropped);
    Ok(())
}

async fn build_started_af_packet_fallback(args: &Args) -> Result<Box<dyn Capturer>> {
    if !matches!(
        args.capture_fallback_driver,
        Some(FallbackDriver::AfPacketTs)
    ) {
        bail!("AF_PACKET timestamp fallback is not configured");
    }
    let interface = args.interface.as_deref().context("missing interface")?;
    let mut fallback: Box<dyn Capturer> = Box::new(KernelTimestampAfPacket::new(interface)?);
    fallback
        .start()
        .await
        .context("start timestamped AF_PACKET fallback")?;
    Ok(fallback)
}

fn dispatch_pending(
    pending: &mut Vec<ClosedFlow>,
    scheduler: &mut BudgetScheduler,
    dispatcher: &GpuDispatcher,
    metrics: &RuntimeMetrics,
    batch_size: usize,
    queue_capacity: usize,
) {
    while !pending.is_empty() {
        let queue_pressure = pending.len() as f64 / queue_capacity.max(1) as f64;
        let take = pending.len().min(batch_size);
        let chunk: Vec<ClosedFlow> = pending.drain(..take).collect();
        metrics
            .flows_emitted
            .fetch_add(chunk.len() as u64, Ordering::Relaxed);
        for flow in scheduler.schedule_with_pressure(chunk, metrics, queue_pressure) {
            dispatcher.enqueue(flow);
        }
    }
}

fn should_expire_flows(
    received: u64,
    last_expire_packet: u64,
    timestamp_us: u64,
    last_expire_timestamp_us: u64,
) -> bool {
    received.saturating_sub(last_expire_packet) >= FLOW_EXPIRY_SCAN_PACKET_INTERVAL
        && timestamp_us.saturating_sub(last_expire_timestamp_us)
            >= FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US
}

async fn build_capturer(
    args: &Args,
) -> Result<(String, String, String, u64, String, bool, Box<dyn Capturer>)> {
    if let Some(path) = &args.pcap {
        let divisor = pcap_timestamp_divisor(path)?;
        let replayer = PcapReplayer::new(
            path.to_str().context("PCAP path is not UTF-8")?,
            ReplaySpeed::MaxSpeed,
            false,
        )?;
        return Ok((
            "pcap_offline".to_string(),
            path.display().to_string(),
            "traffic-analysis-platform/PcapReplayer".to_string(),
            divisor,
            "pcap_file_timestamp_unverified_for_live_latency".to_string(),
            false,
            Box::new(replayer),
        ));
    }
    let interface = args.interface.clone().context("missing interface")?;
    if matches!(args.driver, Driver::AfPacketTs) {
        require_linux()?;
        let capturer = KernelTimestampAfPacket::new(&interface)?;
        return Ok((
            "live_interface".to_string(),
            interface,
            "af_packet_ts".to_string(),
            1,
            "kernel_software_receive_realtime_so_timestampns".to_string(),
            true,
            Box::new(capturer),
        ));
    }
    if matches!(args.driver, Driver::Xdp | Driver::XdpSkb) {
        require_linux()?;
        let mode = match args.driver {
            Driver::Xdp => HftXdpMode::Native,
            Driver::XdpSkb => HftXdpMode::Skb,
            _ => unreachable!(),
        };
        let capturer = HftXdpCapture::new(
            interface.clone(),
            mode,
            args.xdp_queue_count,
            args.xdp_frames_per_queue,
            args.xdp_receive_batch_size,
            args.xdp_ebpf_object
                .clone()
                .context("--xdp-ebpf-object is required for XDP capture")?,
            args.diagnostic_xdp_fail_after_packets,
        )?;
        return Ok((
            "live_interface".to_string(),
            interface,
            match mode {
                HftXdpMode::Native => "native_af_xdp_forced_zerocopy",
                HftXdpMode::Skb => "xdp_skb",
            }
            .to_string(),
            1,
            "xdp_bpf_ktime_get_ns_converted_realtime_metadata".to_string(),
            true,
            Box::new(capturer),
        ));
    }
    let mode = match args.driver {
        Driver::AfPacket => CaptureMode::AfPacket,
        Driver::Xdp | Driver::XdpSkb | Driver::AfPacketTs => unreachable!(),
    };
    let config = CaptureConfig {
        interface: interface.clone(),
        mode,
        promiscuous_mode: true,
        ..CaptureConfig::default()
    };
    let capturer = create_capturer(&config).await?;
    Ok((
        "live_interface".to_string(),
        interface,
        mode.as_str().to_string(),
        1,
        "capture_driver_timestamp_unverified".to_string(),
        false,
        capturer,
    ))
}

fn pcap_timestamp_divisor(path: &Path) -> Result<u64> {
    use std::io::Read;
    let mut magic = [0u8; 4];
    File::open(path)
        .with_context(|| format!("open {}", path.display()))?
        .read_exact(&mut magic)?;
    let little = u32::from_le_bytes(magic);
    let big = u32::from_be_bytes(magic);
    let nanosecond =
        little == 0xa1b23c4d || little == 0x4d3cb2a1 || big == 0xa1b23c4d || big == 0x4d3cb2a1;
    Ok(if nanosecond { 1000 } else { 1 })
}

#[cfg(test)]
mod tests {
    use super::{
        should_expire_flows, stop_and_accumulate_capture_drops, FLOW_EXPIRY_SCAN_PACKET_INTERVAL,
        FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US,
    };
    use anyhow::Result;
    use probe_agent::capture::{CaptureStats, Capturer, PacketBatch};

    struct StopPublishedDrops {
        stopped: bool,
        drops_after_stop: u64,
    }

    #[async_trait::async_trait]
    impl Capturer for StopPublishedDrops {
        async fn start(&mut self) -> Result<()> {
            Ok(())
        }

        async fn stop(&mut self) -> Result<()> {
            self.stopped = true;
            Ok(())
        }

        fn poll(&mut self) -> Result<Option<PacketBatch>> {
            Ok(None)
        }

        fn stats(&self) -> CaptureStats {
            assert!(
                self.stopped,
                "capture statistics must be read only after stop publishes final drops"
            );
            CaptureStats {
                packets_dropped: self.drops_after_stop,
                ..CaptureStats::default()
            }
        }
    }

    #[tokio::test]
    async fn fallback_reads_final_stats_after_stop_and_saturates_accumulation() {
        let mut capturer = StopPublishedDrops {
            stopped: false,
            drops_after_stop: 7,
        };
        let mut accumulated = u64::MAX - 2;

        stop_and_accumulate_capture_drops(&mut capturer, &mut accumulated, "stop test capture")
            .await
            .unwrap();

        assert!(capturer.stopped);
        assert_eq!(accumulated, u64::MAX);
    }

    #[test]
    fn flow_expiry_scan_requires_packet_and_event_time_progress() {
        assert!(!should_expire_flows(
            FLOW_EXPIRY_SCAN_PACKET_INTERVAL - 1,
            0,
            FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US,
            0,
        ));
        assert!(!should_expire_flows(
            FLOW_EXPIRY_SCAN_PACKET_INTERVAL,
            0,
            FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US - 1,
            0,
        ));
        assert!(should_expire_flows(
            FLOW_EXPIRY_SCAN_PACKET_INTERVAL,
            0,
            FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US,
            0,
        ));
    }
}
