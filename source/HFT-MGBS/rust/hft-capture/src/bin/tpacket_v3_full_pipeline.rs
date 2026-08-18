#[cfg(not(target_os = "linux"))]
compile_error!("tpacket_v3_full_pipeline is Linux-only");

use anyhow::{bail, Context, Result};
use clap::{Parser, ValueEnum};
use crossbeam_channel::{bounded, Receiver, RecvTimeoutError, Sender, TryRecvError, TrySendError};
use hft_capture::a09_fallback::{ExpectedPortableA09Identity, VerifiedLocalFallback};
use hft_capture::fixed_profile_parse::{parse_profile_or_fallback, ProfileParse};
use hft_capture::flow::{ClosedFlow, HftFlowTable};
use hft_capture::gpu::{ExpectedBackendIdentity, GpuDispatcher};
use hft_capture::metrics::{should_sample_packet_latency, MetricsReport, RuntimeMetrics};
use hft_capture::packet_continuity::{
    merge_packet_continuity, PacketContinuityReport, PacketContinuityShard,
};
use hft_capture::scheduler::{AdaptiveBudgetSnapshot, BudgetScheduler};
use hft_capture::tpacket_v3::{
    pin_current_thread, FanoutMode, PacketRing, RingConfig, SocketStatistics,
};
use serde::Serialize;
use std::collections::{BTreeMap, BTreeSet};
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use std::time::{SystemTime, UNIX_EPOCH};

const REQUIRED_CAPTURE_WORKERS: usize = 8;
const FLOW_EXPIRY_SCAN_PACKET_INTERVAL: u64 = 16_384;
const FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US: u64 = 1_000_000;
const SOCKET_STATS_INTERVAL: Duration = Duration::from_secs(1);
const MAX_WORKER_LATENCY_SAMPLES: usize = 128 * 1024;
const MAX_QM_COLLISION_EXAMPLES: usize = 32;
static TERMINATE_REQUESTED: AtomicBool = AtomicBool::new(false);

extern "C" fn request_termination(_: libc::c_int) {
    TERMINATE_REQUESTED.store(true, Ordering::Release);
}

#[derive(Clone, Copy, Debug, ValueEnum)]
enum CliFanoutMode {
    Hash,
    Qm,
}

impl From<CliFanoutMode> for FanoutMode {
    fn from(value: CliFanoutMode) -> Self {
        match value {
            CliFanoutMode::Hash => Self::Hash,
            CliFanoutMode::Qm => Self::Qm,
        }
    }
}

#[derive(Debug, Parser)]
#[command(about = "Borrowed and sharded TPACKET_V3 HFT full-pipeline raw evidence runner")]
struct Args {
    #[arg(long)]
    interface: String,
    #[arg(long, value_enum, default_value = "hash")]
    fanout_mode: CliFanoutMode,
    #[arg(long, default_value_t = false)]
    allow_qm_with_verified_flow_affinity: bool,
    #[arg(long, default_value_t = 65_536)]
    flow_affinity_evidence_max_distinct_per_worker: usize,
    #[arg(long)]
    fanout_id: Option<u16>,
    #[arg(long, default_value_t = false)]
    allow_explicit_fanout_id: bool,
    #[arg(long, value_delimiter = ',', num_args = REQUIRED_CAPTURE_WORKERS)]
    worker_cpus: Vec<usize>,
    #[arg(long)]
    scheduler_cpu: usize,
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
    #[arg(long, default_value_t = false)]
    allow_unready_gpu_diagnostic: bool,
    #[arg(long, default_value_t = 128)]
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
    feature_queue_capacity: usize,
    #[arg(long, default_value_t = 8192)]
    gpu_queue_capacity: usize,
    #[arg(long, default_value_t = 150)]
    gpu_timeout_ms: u64,
    #[arg(long, default_value_t = 5000)]
    gpu_startup_wait_ms: u64,
    #[arg(long, default_value_t = 125_000)]
    max_active_flows_per_worker: usize,
    #[arg(long, default_value_t = 120)]
    idle_timeout_s: u64,
    #[arg(long, default_value_t = 1800)]
    active_timeout_s: u64,
    #[arg(long, default_value_t = 256)]
    max_payload_sample: usize,
    #[arg(long)]
    ready_file: Option<PathBuf>,
    #[arg(long)]
    output: PathBuf,
}

#[derive(Debug, Default, Serialize)]
struct AccumulatedSocketStatistics {
    packets: u64,
    drops: u64,
    freeze_queue_count: u64,
    destructive_reads: u64,
    windows: Vec<SocketStatisticsWindow>,
}

impl AccumulatedSocketStatistics {
    fn add(&mut self, elapsed_second: u64, stats: SocketStatistics) {
        self.packets = self.packets.saturating_add(u64::from(stats.packets));
        self.drops = self.drops.saturating_add(u64::from(stats.drops));
        self.freeze_queue_count = self
            .freeze_queue_count
            .saturating_add(u64::from(stats.freeze_queue_count));
        self.destructive_reads = self.destructive_reads.saturating_add(1);
        self.windows.push(SocketStatisticsWindow {
            elapsed_second,
            packets: stats.packets,
            drops: stats.drops,
            freeze_queue_count: stats.freeze_queue_count,
        });
    }
}

#[derive(Debug, Serialize)]
struct SocketStatisticsWindow {
    elapsed_second: u64,
    packets: u32,
    drops: u32,
    freeze_queue_count: u32,
}

#[derive(Debug, Default, Serialize)]
struct WorkerReport {
    worker_index: usize,
    cpu: usize,
    packets: u64,
    bytes: u64,
    blocks: u64,
    packets_parsed: u64,
    parse_rejected: u64,
    fixed_profile_fast_parsed: u64,
    fixed_profile_general_fallback: u64,
    flows_closed: u64,
    expire_scan_calls: u64,
    expire_scan_closed_total: u64,
    expire_scan_event_time_delta_us_min: Option<u64>,
    expire_scan_event_time_delta_us_max: Option<u64>,
    expire_scan_event_time_delta_samples: u64,
    expire_scan_first_delta_omitted: bool,
    flush_closed: u64,
    flow_affinity_hash_counts: BTreeMap<String, u64>,
    flow_affinity_evidence_overflow: bool,
    feature_queue_submitted: u64,
    feature_queue_drops: u64,
    key_feature_queue_drops: u64,
    epoch_second_counts: BTreeMap<u64, u64>,
    epoch_out_of_order_packets: u64,
    socket_statistics: AccumulatedSocketStatistics,
    thread_cpu_seconds: f64,
    parse_flow_latency_sample_stride: u64,
    parse_flow_latency_samples_us: Vec<u64>,
    warmup_packets_drained: u64,
    fatal_error: Option<String>,
    #[serde(skip)]
    packet_continuity: PacketContinuityShard,
}

fn record_expire_event_time_delta(
    report: &mut WorkerReport,
    previous_timestamp_us: u64,
    current_timestamp_us: u64,
) {
    if previous_timestamp_us == 0 {
        report.expire_scan_first_delta_omitted = true;
        return;
    }
    let delta = current_timestamp_us.saturating_sub(previous_timestamp_us);
    report.expire_scan_event_time_delta_us_min = Some(
        report
            .expire_scan_event_time_delta_us_min
            .map_or(delta, |value| value.min(delta)),
    );
    report.expire_scan_event_time_delta_us_max = Some(
        report
            .expire_scan_event_time_delta_us_max
            .map_or(delta, |value| value.max(delta)),
    );
    report.expire_scan_event_time_delta_samples = report
        .expire_scan_event_time_delta_samples
        .saturating_add(1);
}

#[derive(Debug, Default)]
struct EpochSecondAccumulator {
    completed: BTreeMap<u64, u64>,
    current_second: Option<u64>,
    current_count: u64,
    out_of_order_packets: u64,
}

impl EpochSecondAccumulator {
    #[inline]
    fn record(&mut self, second: u64) {
        match self.current_second {
            None => {
                self.current_second = Some(second);
                self.current_count = 1;
            }
            Some(current) if second == current => {
                self.current_count = self.current_count.saturating_add(1);
            }
            Some(current) if second > current => {
                *self.completed.entry(current).or_insert(0) += self.current_count;
                self.current_second = Some(second);
                self.current_count = 1;
            }
            Some(_) => {
                *self.completed.entry(second).or_insert(0) += 1;
                self.out_of_order_packets = self.out_of_order_packets.saturating_add(1);
            }
        }
    }

    fn finish(mut self) -> (BTreeMap<u64, u64>, u64) {
        if let Some(current) = self.current_second {
            *self.completed.entry(current).or_insert(0) += self.current_count;
        }
        (self.completed, self.out_of_order_packets)
    }
}

#[derive(Debug, Default, Serialize)]
struct FlowAffinityEvidence {
    hash_algorithm: &'static str,
    closed_flow_observations: u64,
    distinct_flow_hashes: usize,
    same_worker_reopen_observations: u64,
    cross_worker_collision_count: usize,
    cross_worker_collision_examples: Vec<String>,
    worker_observation_counts: BTreeMap<usize, u64>,
    worker_distinct_hash_counts: BTreeMap<usize, usize>,
    evidence_overflow: bool,
    evidence_complete: bool,
    runtime_verified: bool,
}

#[derive(Debug, Default, Serialize)]
struct SchedulerReport {
    cpu: usize,
    batches_scheduled: u64,
    flows_scheduled: u64,
    input_channel_drained: bool,
    dispatcher_finish_called: bool,
    adaptive_budget: Option<AdaptiveBudgetSnapshot>,
    fatal_error: Option<String>,
}

#[derive(Serialize)]
struct ShutdownReport {
    stop_flag_observed: bool,
    capture_workers_joined: usize,
    capture_workers_expected: usize,
    scheduler_thread_joined: bool,
    scheduler_input_channel_drained: bool,
    dispatcher_finish_called: bool,
}

#[derive(Serialize)]
struct FullPipelineReport {
    schema_version: u32,
    scope: &'static str,
    backend: &'static str,
    interface: String,
    fanout_mode: &'static str,
    fanout_id: u16,
    fanout_id_source: &'static str,
    fanout_lock_path: String,
    qm_flow_affinity_authorized: bool,
    qm_flow_affinity_evidence: FlowAffinityEvidence,
    worker_cpus: Vec<usize>,
    scheduler_cpu: usize,
    duration_s: f64,
    block_size: u32,
    block_count_per_worker: u32,
    frame_size: u32,
    ring_memory_bytes: u64,
    feature_queue_capacity: usize,
    gpu_queue_capacity: usize,
    gpu_ready_at_start: bool,
    expected_gpu_identity: ExpectedBackendIdentity,
    packets: u64,
    bytes: u64,
    achieved_mpps: f64,
    achieved_gbps: f64,
    packets_parsed: u64,
    parse_rejected: u64,
    parser_profile_id: &'static str,
    fixed_profile_fast_parsed: u64,
    fixed_profile_general_fallback: u64,
    flows_closed: u64,
    feature_queue_submitted: u64,
    feature_queue_drops: u64,
    key_feature_queue_drops: u64,
    packet_socket_statistics_packets: u64,
    packet_socket_drops: u64,
    packet_socket_freeze_queue_count: u64,
    packet_socket_statistics_destructive_reads: u64,
    full_epoch_windows: usize,
    min_full_epoch_mpps: Option<f64>,
    epoch_second_counts: BTreeMap<u64, u64>,
    packet_continuity_windows: Vec<hft_capture::packet_continuity::PacketContinuityWindow>,
    packet_gap: u64,
    packet_continuity: PacketContinuityReport,
    process_cpu_cores_average: f64,
    workers: Vec<WorkerReport>,
    scheduler: SchedulerReport,
    pipeline_metrics: MetricsReport,
    shutdown: ShutdownReport,
    all_workers_error_free: bool,
    internal_delivery_lossless: bool,
    capture_lossless: bool,
    raw_full_pipeline_observation: bool,
    runtime_identity_verified: bool,
    full_pipeline_qualified: bool,
    final_pareto_ingestion_allowed: bool,
}

#[derive(Default)]
struct StartGate {
    start: Mutex<Option<Instant>>,
    wake: Condvar,
}

#[derive(Debug)]
struct FanoutReservation {
    id: u16,
    source: &'static str,
    path: PathBuf,
    _file: File,
}

impl Drop for FanoutReservation {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.path);
    }
}

impl StartGate {
    fn publish(&self, start: Instant) {
        *self.start.lock().expect("start gate mutex poisoned") = Some(start);
        self.wake.notify_all();
    }

    fn wait(&self, stop: &AtomicBool) -> Option<Instant> {
        let mut guard = self.start.lock().expect("start gate mutex poisoned");
        while guard.is_none() && !stop.load(Ordering::Acquire) {
            guard = self
                .wake
                .wait_timeout(guard, Duration::from_millis(100))
                .expect("start gate condvar poisoned")
                .0;
        }
        *guard
    }
}

fn validate_args(args: &Args, fanout_id: u16) -> Result<RingConfig> {
    if args.worker_cpus.len() != REQUIRED_CAPTURE_WORKERS {
        bail!("exactly {REQUIRED_CAPTURE_WORKERS} capture worker CPUs are required");
    }
    let mut cpus = args.worker_cpus.clone();
    cpus.sort_unstable();
    cpus.dedup();
    if cpus.len() != args.worker_cpus.len() {
        bail!("worker CPUs must be unique");
    }
    if args.worker_cpus.contains(&args.scheduler_cpu) {
        bail!("scheduler CPU must not overlap a capture worker CPU");
    }
    if matches!(args.fanout_mode, CliFanoutMode::Qm) && !args.allow_qm_with_verified_flow_affinity {
        bail!("QM requires --allow-qm-with-verified-flow-affinity");
    }
    if args.duration_s == 0 || args.duration_s > 3_600 {
        bail!("duration must be in 1..=3600 seconds");
    }
    if args.batch_size == 0
        || args.feature_flush_us == 0
        || args.feature_queue_capacity == 0
        || args.gpu_queue_capacity == 0
        || args.max_active_flows_per_worker == 0
        || args.flow_affinity_evidence_max_distinct_per_worker == 0
    {
        bail!("batch, flush, queue and flow capacities must be positive");
    }
    if !(0.0..=1.0).contains(&args.execution_budget_safety_ratio)
        || args.execution_budget_safety_ratio == 0.0
    {
        bail!("execution budget safety ratio must be in (0, 1]");
    }
    if !(0.0..=1.0).contains(&args.budget_target_utilization)
        || args.budget_target_utilization == 0.0
        || !(0.0..=1.0).contains(&args.budget_ema_alpha)
        || args.budget_ema_alpha == 0.0
        || args.budget_minimum_ratio <= 0.0
        || args.budget_minimum_ratio > args.execution_budget_safety_ratio
    {
        bail!("adaptive budget parameters must satisfy target/alpha in (0,1] and minimum ratio in (0,safety]");
    }
    let ring = RingConfig {
        interface: args.interface.clone(),
        fanout_mode: args.fanout_mode.into(),
        fanout_id,
        block_size: args.block_size,
        block_count: args.block_count,
        frame_size: args.frame_size,
        retire_block_timeout_ms: args.retire_block_timeout_ms,
    };
    ring.validate()?;
    let total_ring_memory = u64::from(args.block_size)
        .checked_mul(u64::from(args.block_count))
        .and_then(|value| value.checked_mul(REQUIRED_CAPTURE_WORKERS as u64))
        .context("total ring memory overflow")?;
    if total_ring_memory > 8 * 1024 * 1024 * 1024 {
        bail!("total ring memory must not exceed 8 GiB");
    }
    Ok(ring)
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

fn reserve_fanout_id(requested: Option<u16>, allow_explicit: bool) -> Result<FanoutReservation> {
    if requested.is_some() && !allow_explicit {
        bail!("--fanout-id requires --allow-explicit-fanout-id");
    }
    let netns = std::fs::read_link("/proc/self/ns/net")
        .context("read current network namespace identity")?
        .to_string_lossy()
        .replace(['[', ']'], "");
    let seed = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .context("system clock precedes UNIX epoch")?
        .as_nanos()
        ^ u128::from(std::process::id());
    for attempt in 0..256u128 {
        let id = requested.unwrap_or_else(|| {
            let mixed = seed
                .wrapping_add(attempt.wrapping_mul(0x9e37_79b9))
                .wrapping_mul(0xbf58_476d_1ce4_e5b9);
            1024 + (mixed % u128::from(u16::MAX - 1023)) as u16
        });
        if id == 0 {
            bail!("fanout id must be non-zero");
        }
        let path = PathBuf::from(format!(
            "/run/lock/hft-mgbs-tpacket-fanout-{netns}-{id}.lock"
        ));
        match OpenOptions::new().write(true).create_new(true).open(&path) {
            Ok(mut file) => {
                writeln!(
                    file,
                    "pid={} netns={} fanout_id={}",
                    std::process::id(),
                    netns,
                    id
                )?;
                return Ok(FanoutReservation {
                    id,
                    source: if requested.is_some() {
                        "explicit_authorized_locked"
                    } else {
                        "automatic_randomized_locked"
                    },
                    path,
                    _file: file,
                });
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                if requested.is_some() {
                    return Err(error).context("explicit fanout id lock conflict");
                }
            }
            Err(error) => return Err(error).context("reserve fanout id lock"),
        }
    }
    bail!("unable to reserve a collision-free automatic fanout id")
}

fn thread_cpu_time() -> Result<Duration> {
    let mut value: libc::timespec = unsafe { std::mem::zeroed() };
    let status = unsafe { libc::clock_gettime(libc::CLOCK_THREAD_CPUTIME_ID, &mut value) };
    if status != 0 {
        return Err(std::io::Error::last_os_error()).context("read thread CPU clock");
    }
    Ok(Duration::new(value.tv_sec as u64, value.tv_nsec as u32))
}

fn process_cpu_time() -> Result<Duration> {
    let mut value: libc::timespec = unsafe { std::mem::zeroed() };
    let status = unsafe { libc::clock_gettime(libc::CLOCK_PROCESS_CPUTIME_ID, &mut value) };
    if status != 0 {
        return Err(std::io::Error::last_os_error()).context("read process CPU clock");
    }
    Ok(Duration::new(value.tv_sec as u64, value.tv_nsec as u32))
}

fn record_send_result<T>(
    result: std::result::Result<(), TrySendError<T>>,
    is_key_flow: bool,
    report: &mut WorkerReport,
    metrics: &RuntimeMetrics,
) {
    metrics.flows_emitted.fetch_add(1, Ordering::Relaxed);
    match result {
        Ok(()) => report.feature_queue_submitted += 1,
        Err(TrySendError::Full(_)) | Err(TrySendError::Disconnected(_)) => {
            report.feature_queue_drops += 1;
            metrics.fallback_flows.fetch_add(1, Ordering::Relaxed);
            if is_key_flow {
                report.key_feature_queue_drops += 1;
                metrics.key_flows_total.fetch_add(1, Ordering::Relaxed);
                metrics
                    .key_flows_base_materialized
                    .fetch_add(1, Ordering::Relaxed);
                metrics
                    .key_flows_enqueue_failed
                    .fetch_add(1, Ordering::Relaxed);
            }
        }
    }
}

fn submit_closed_flows(
    closed: &mut Vec<ClosedFlow>,
    sender: &Sender<ClosedFlow>,
    report: &mut WorkerReport,
    metrics: &RuntimeMetrics,
    affinity_evidence_max_distinct: usize,
) {
    report.flows_closed = report.flows_closed.saturating_add(closed.len() as u64);
    for flow in closed.drain(..) {
        let flow_hash = stable_flow_id_hash(&flow.flow_id);
        if let Some(count) = report.flow_affinity_hash_counts.get_mut(&flow_hash) {
            *count = count.saturating_add(1);
        } else if report.flow_affinity_hash_counts.len() < affinity_evidence_max_distinct {
            report.flow_affinity_hash_counts.insert(flow_hash, 1);
        } else {
            report.flow_affinity_evidence_overflow = true;
        }
        let is_key_flow = flow.is_key_flow;
        record_send_result(sender.try_send(flow), is_key_flow, report, metrics);
    }
}

fn fnv1a64(bytes: &[u8], offset: u64) -> u64 {
    bytes.iter().fold(offset, |hash, byte| {
        (hash ^ u64::from(*byte)).wrapping_mul(0x0000_0100_0000_01B3)
    })
}

fn stable_flow_id_hash(flow_id: &str) -> String {
    let bytes = flow_id.as_bytes();
    format!(
        "{:016x}{:016x}",
        fnv1a64(bytes, 0xCBF2_9CE4_8422_2325),
        fnv1a64(bytes, 0x8422_2325_CBF2_9CE4)
    )
}

fn build_flow_affinity_evidence(workers: &[WorkerReport]) -> FlowAffinityEvidence {
    let mut owners: BTreeMap<&str, BTreeSet<usize>> = BTreeMap::new();
    let mut closed_flow_observations = 0u64;
    let mut worker_observation_counts = BTreeMap::new();
    let mut worker_distinct_hash_counts = BTreeMap::new();
    let mut evidence_overflow = false;
    for worker in workers {
        let observations = worker
            .flow_affinity_hash_counts
            .values()
            .copied()
            .sum::<u64>();
        closed_flow_observations = closed_flow_observations.saturating_add(observations);
        worker_observation_counts.insert(worker.worker_index, observations);
        worker_distinct_hash_counts
            .insert(worker.worker_index, worker.flow_affinity_hash_counts.len());
        evidence_overflow |= worker.flow_affinity_evidence_overflow;
        for hash in worker.flow_affinity_hash_counts.keys() {
            owners
                .entry(hash.as_str())
                .or_default()
                .insert(worker.worker_index);
        }
    }
    let collisions = owners
        .iter()
        .filter(|(_, worker_ids)| worker_ids.len() > 1)
        .map(|(hash, worker_ids)| {
            format!(
                "{hash}:{}",
                worker_ids
                    .iter()
                    .map(usize::to_string)
                    .collect::<Vec<_>>()
                    .join(",")
            )
        })
        .collect::<Vec<_>>();
    let total_flows_closed = workers
        .iter()
        .map(|worker| worker.flows_closed)
        .sum::<u64>();
    let distinct_flow_hashes = owners.len();
    let evidence_complete = !evidence_overflow && closed_flow_observations == total_flows_closed;
    FlowAffinityEvidence {
        hash_algorithm: "dual_fnv1a64_v1",
        closed_flow_observations,
        distinct_flow_hashes,
        same_worker_reopen_observations: closed_flow_observations
            .saturating_sub(distinct_flow_hashes as u64),
        cross_worker_collision_count: collisions.len(),
        cross_worker_collision_examples: collisions
            .into_iter()
            .take(MAX_QM_COLLISION_EXAMPLES)
            .collect(),
        worker_observation_counts,
        worker_distinct_hash_counts,
        evidence_overflow,
        evidence_complete,
        runtime_verified: evidence_complete
            && distinct_flow_hashes > 0
            && owners.values().all(|ids| ids.len() == 1),
    }
}

fn take_stats(
    ring: &PacketRing,
    report: &mut WorkerReport,
    stop: &AtomicBool,
    phase: &str,
    elapsed_second: u64,
) -> bool {
    match ring.take_socket_statistics() {
        Ok(stats) => {
            report.socket_statistics.add(elapsed_second, stats);
            true
        }
        Err(error) => {
            report.fatal_error = Some(format!("{phase}: {error:#}"));
            stop.store(true, Ordering::Release);
            false
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn run_capture_worker(
    mut ring: PacketRing,
    worker_index: usize,
    cpu: usize,
    duration: Duration,
    gate: Arc<StartGate>,
    setup: Sender<std::result::Result<(), String>>,
    stop: Arc<AtomicBool>,
    sender: Sender<ClosedFlow>,
    metrics: Arc<RuntimeMetrics>,
    max_active_flows: usize,
    idle_timeout_s: u64,
    active_timeout_s: u64,
    max_payload_sample: usize,
    affinity_evidence_max_distinct: usize,
) -> WorkerReport {
    let mut report = WorkerReport {
        worker_index,
        cpu,
        parse_flow_latency_sample_stride: hft_capture::metrics::PACKET_LATENCY_SAMPLE_STRIDE,
        parse_flow_latency_samples_us: Vec::with_capacity(16 * 1024),
        ..WorkerReport::default()
    };
    let pinned = pin_current_thread(cpu).map_err(|error| format!("pin_worker: {error:#}"));
    let _ = setup.send(pinned.clone());
    let Some(start) = gate.wait(&stop) else {
        report.fatal_error = Some("start_cancelled".to_string());
        return report;
    };
    if let Err(error) = pinned {
        report.fatal_error = Some(error);
        stop.store(true, Ordering::Release);
        return report;
    }

    while Instant::now() < start && !stop.load(Ordering::Acquire) {
        match ring.poll_borrowed(|_, _, _| Ok(())) {
            Ok(Some(stats)) => {
                report.warmup_packets_drained =
                    report.warmup_packets_drained.saturating_add(stats.packets);
            }
            Ok(None) => std::hint::spin_loop(),
            Err(error) => {
                report.fatal_error = Some(format!("warmup_poll: {error:#}"));
                stop.store(true, Ordering::Release);
                return report;
            }
        }
    }
    if let Err(error) = ring.take_socket_statistics() {
        report.fatal_error = Some(format!("clear_warmup_socket_statistics: {error:#}"));
        stop.store(true, Ordering::Release);
        return report;
    }

    let cpu_started = thread_cpu_time().ok();
    let end = start + duration;
    let mut next_stats = start + SOCKET_STATS_INTERVAL;
    let mut flow_table = HftFlowTable::new(
        max_active_flows,
        idle_timeout_s,
        active_timeout_s,
        max_payload_sample,
    );
    let mut closed = Vec::with_capacity(256);
    let mut epoch_counts = EpochSecondAccumulator::default();
    let mut last_timestamp_us = 0u64;
    let mut last_expire_packet = 0u64;
    let mut last_expire_timestamp_us = 0u64;

    while Instant::now() < end
        && !stop.load(Ordering::Acquire)
        && !TERMINATE_REQUESTED.load(Ordering::Acquire)
    {
        let poll_result = ring.poll_borrowed(|frame, timestamp_us, original_len| {
            let sequence = report.packets.saturating_add(1);
            let latency_started = should_sample_packet_latency(sequence).then(Instant::now);
            report.packets = sequence;
            report.bytes = report.bytes.saturating_add(u64::from(original_len));
            epoch_counts.record(timestamp_us / 1_000_000);
            last_timestamp_us = last_timestamp_us.max(timestamp_us);
            match parse_profile_or_fallback(frame, timestamp_us) {
                Ok(parsed) => {
                    match &parsed {
                        ProfileParse::Fast(_) => {
                            report
                                .packet_continuity
                                .observe_fixed_profile(frame, timestamp_us);
                            report.fixed_profile_fast_parsed =
                                report.fixed_profile_fast_parsed.saturating_add(1);
                        }
                        ProfileParse::Fallback(_) => {
                            report.packet_continuity.observe_non_profile(timestamp_us);
                            report.fixed_profile_general_fallback =
                                report.fixed_profile_general_fallback.saturating_add(1);
                        }
                    }
                    if let Some(parsed) = parsed.into_packet() {
                        report.packets_parsed = report.packets_parsed.saturating_add(1);
                        flow_table.update_into(&parsed, frame, &mut closed);
                    } else {
                        report.parse_rejected = report.parse_rejected.saturating_add(1);
                    }
                }
                Err(_) => {
                    report.packet_continuity.observe_non_profile(timestamp_us);
                    report.parse_rejected = report.parse_rejected.saturating_add(1);
                }
            }
            if sequence.saturating_sub(last_expire_packet) >= FLOW_EXPIRY_SCAN_PACKET_INTERVAL
                && last_timestamp_us.saturating_sub(last_expire_timestamp_us)
                    >= FLOW_EXPIRY_SCAN_TIMESTAMP_INTERVAL_US
            {
                // Preserve the historical first expiry invocation while not
                // reporting epoch-scale `timestamp - 0` as a scan interval.
                let expired = flow_table.expire(last_timestamp_us);
                report.expire_scan_calls = report.expire_scan_calls.saturating_add(1);
                report.expire_scan_closed_total = report
                    .expire_scan_closed_total
                    .saturating_add(expired.len() as u64);
                record_expire_event_time_delta(
                    &mut report,
                    last_expire_timestamp_us,
                    last_timestamp_us,
                );
                closed.extend(expired);
                last_expire_packet = sequence;
                last_expire_timestamp_us = last_timestamp_us;
            }
            if let Some(started) = latency_started {
                if report.parse_flow_latency_samples_us.len() < MAX_WORKER_LATENCY_SAMPLES {
                    report
                        .parse_flow_latency_samples_us
                        .push(started.elapsed().as_micros().min(u64::MAX as u128) as u64);
                }
            }
            Ok(())
        });
        match poll_result {
            Ok(Some(_)) => {
                report.blocks = report.blocks.saturating_add(1);
                submit_closed_flows(
                    &mut closed,
                    &sender,
                    &mut report,
                    &metrics,
                    affinity_evidence_max_distinct,
                );
            }
            Ok(None) => std::hint::spin_loop(),
            Err(error) => {
                report.fatal_error = Some(format!("poll_borrowed: {error:#}"));
                stop.store(true, Ordering::Release);
                break;
            }
        }
        if Instant::now() >= next_stats {
            let elapsed_second = Instant::now().saturating_duration_since(start).as_secs();
            if !take_stats(
                &ring,
                &mut report,
                &stop,
                "periodic_socket_statistics",
                elapsed_second,
            ) {
                break;
            }
            next_stats += SOCKET_STATS_INTERVAL;
        }
    }
    let flushed = flow_table.flush();
    report.flush_closed = flushed.len() as u64;
    closed.extend(flushed);
    (
        report.epoch_second_counts,
        report.epoch_out_of_order_packets,
    ) = epoch_counts.finish();
    submit_closed_flows(
        &mut closed,
        &sender,
        &mut report,
        &metrics,
        affinity_evidence_max_distinct,
    );
    take_stats(
        &ring,
        &mut report,
        &stop,
        "final_socket_statistics",
        Instant::now().saturating_duration_since(start).as_secs(),
    );
    if let (Some(started), Ok(finished)) = (cpu_started, thread_cpu_time()) {
        report.thread_cpu_seconds = finished.saturating_sub(started).as_secs_f64();
    }
    report
}

fn dispatch_batch(
    batch: Vec<ClosedFlow>,
    scheduler: &mut BudgetScheduler,
    dispatcher: &GpuDispatcher,
    metrics: &RuntimeMetrics,
    report: &mut SchedulerReport,
    queue_pressure: f64,
) {
    if batch.is_empty() {
        return;
    }
    report.batches_scheduled = report.batches_scheduled.saturating_add(1);
    report.flows_scheduled = report.flows_scheduled.saturating_add(batch.len() as u64);
    for flow in scheduler.schedule_with_pressure(batch, metrics, queue_pressure) {
        dispatcher.enqueue(flow);
    }
}

#[allow(clippy::too_many_arguments)]
fn run_scheduler(
    receiver: Receiver<ClosedFlow>,
    dispatcher: GpuDispatcher,
    metrics: Arc<RuntimeMetrics>,
    cpu: usize,
    batch_size: usize,
    flush: Duration,
    budget_us: f64,
    safety_ratio: f64,
    target_utilization: f64,
    ema_alpha: f64,
    minimum_budget_ratio: f64,
    feature_queue_capacity: usize,
) -> SchedulerReport {
    let mut report = SchedulerReport {
        cpu,
        ..SchedulerReport::default()
    };
    if let Err(error) = pin_current_thread(cpu) {
        report.fatal_error = Some(format!("pin_scheduler: {error:#}"));
    }
    let mut scheduler = match BudgetScheduler::with_adaptive_feedback(
        budget_us,
        safety_ratio,
        target_utilization,
        minimum_budget_ratio,
        ema_alpha,
    ) {
        Ok(scheduler) => scheduler,
        Err(error) => {
            report.fatal_error = Some(format!("adaptive_budget_configuration: {error}"));
            return report;
        }
    };
    let mut disconnected = false;
    while !disconnected {
        let first = match receiver.recv_timeout(flush) {
            Ok(flow) => Some(flow),
            Err(RecvTimeoutError::Timeout) => None,
            Err(RecvTimeoutError::Disconnected) => {
                disconnected = true;
                None
            }
        };
        let Some(first) = first else {
            continue;
        };
        let mut batch = Vec::with_capacity(batch_size);
        batch.push(first);
        let deadline = Instant::now() + flush;
        while batch.len() < batch_size {
            match receiver.try_recv() {
                Ok(flow) => batch.push(flow),
                Err(TryRecvError::Disconnected) => {
                    disconnected = true;
                    break;
                }
                Err(TryRecvError::Empty) if Instant::now() < deadline => {
                    std::hint::spin_loop();
                }
                Err(TryRecvError::Empty) => break,
            }
        }
        let queue_pressure = (receiver.len().saturating_add(batch.len())) as f64
            / feature_queue_capacity.max(1) as f64;
        dispatch_batch(
            batch,
            &mut scheduler,
            &dispatcher,
            &metrics,
            &mut report,
            queue_pressure,
        );
    }
    let tail = receiver.try_iter().collect::<Vec<_>>();
    let tail_pressure = tail.len() as f64 / feature_queue_capacity.max(1) as f64;
    dispatch_batch(
        tail,
        &mut scheduler,
        &dispatcher,
        &metrics,
        &mut report,
        tail_pressure,
    );
    report.input_channel_drained = receiver.is_empty();
    dispatcher.finish();
    report.dispatcher_finish_called = true;
    report.adaptive_budget = Some(scheduler.snapshot());
    report
}

fn merge_epoch_counts(workers: &[WorkerReport]) -> BTreeMap<u64, u64> {
    let mut merged = BTreeMap::new();
    for worker in workers {
        for (second, count) in &worker.epoch_second_counts {
            *merged.entry(*second).or_insert(0) += *count;
        }
    }
    merged
}

fn full_epoch_counts(counts: &BTreeMap<u64, u64>) -> Vec<u64> {
    let first = counts.keys().next().copied();
    let last = counts.keys().next_back().copied();
    counts
        .iter()
        .filter_map(|(second, count)| match (first, last) {
            (Some(first), Some(last)) if *second > first && *second < last => Some(*count),
            _ => None,
        })
        .collect()
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

fn install_signal_handlers() -> Result<()> {
    let mut action: libc::sigaction = unsafe { std::mem::zeroed() };
    action.sa_sigaction = request_termination as *const () as usize;
    unsafe {
        libc::sigemptyset(&mut action.sa_mask);
    }
    let term_status = unsafe { libc::sigaction(libc::SIGTERM, &action, std::ptr::null_mut()) };
    let interrupt_status = unsafe { libc::sigaction(libc::SIGINT, &action, std::ptr::null_mut()) };
    if term_status != 0 || interrupt_status != 0 {
        return Err(std::io::Error::last_os_error()).context("install termination handlers");
    }
    Ok(())
}

fn main() -> Result<()> {
    let args = Args::parse();
    install_signal_handlers()?;
    let fanout_reservation = reserve_fanout_id(args.fanout_id, args.allow_explicit_fanout_id)?;
    let ring_config = validate_args(&args, fanout_reservation.id)?;
    let rings = (0..REQUIRED_CAPTURE_WORKERS)
        .map(|_| PacketRing::open(&ring_config))
        .collect::<Result<Vec<_>>>()?;
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
            true,
            expected_backend,
            fallback,
        )?,
        None => GpuDispatcher::start(
            args.gpu_endpoint.clone(),
            args.batch_size,
            args.gpu_queue_capacity,
            Duration::from_millis(args.gpu_timeout_ms),
            Arc::clone(&metrics),
            true,
            expected_backend,
        )?,
    };
    let gpu_ready_at_start = dispatcher.wait_ready(Duration::from_millis(args.gpu_startup_wait_ms));
    if !gpu_ready_at_start && !args.allow_unready_gpu_diagnostic {
        dispatcher.finish();
        bail!("GPU reverse connection is not ready; diagnostic override was not authorized");
    }
    let (feature_tx, feature_rx) = bounded(args.feature_queue_capacity);
    let scheduler_metrics = Arc::clone(&metrics);
    let scheduler_cpu = args.scheduler_cpu;
    let scheduler_batch_size = args.batch_size;
    let scheduler_flush = Duration::from_micros(args.feature_flush_us);
    let scheduler_budget = args.budget_us;
    let scheduler_safety = args.execution_budget_safety_ratio;
    let scheduler_target_utilization = args.budget_target_utilization;
    let scheduler_ema_alpha = args.budget_ema_alpha;
    let scheduler_minimum_ratio = args.budget_minimum_ratio;
    let scheduler_feature_queue_capacity = args.feature_queue_capacity;
    let scheduler_handle = thread::Builder::new()
        .name("hft-scheduler-dispatch".to_string())
        .spawn(move || {
            run_scheduler(
                feature_rx,
                dispatcher,
                scheduler_metrics,
                scheduler_cpu,
                scheduler_batch_size,
                scheduler_flush,
                scheduler_budget,
                scheduler_safety,
                scheduler_target_utilization,
                scheduler_ema_alpha,
                scheduler_minimum_ratio,
                scheduler_feature_queue_capacity,
            )
        })
        .context("spawn scheduler and dispatcher thread")?;

    let duration = Duration::from_secs(args.duration_s);
    let gate = Arc::new(StartGate::default());
    let stop = Arc::new(AtomicBool::new(false));
    let (setup_tx, setup_rx) = bounded(REQUIRED_CAPTURE_WORKERS);
    let cpu_started = process_cpu_time()?;
    let worker_handles = rings
        .into_iter()
        .zip(args.worker_cpus.iter().copied())
        .enumerate()
        .map(|(worker_index, (ring, cpu))| {
            let worker_gate = Arc::clone(&gate);
            let worker_setup = setup_tx.clone();
            let worker_stop = Arc::clone(&stop);
            let worker_sender = feature_tx.clone();
            let worker_metrics = Arc::clone(&metrics);
            let max_active_flows = args.max_active_flows_per_worker;
            let idle_timeout_s = args.idle_timeout_s;
            let active_timeout_s = args.active_timeout_s;
            let max_payload_sample = args.max_payload_sample;
            let affinity_evidence_max_distinct =
                args.flow_affinity_evidence_max_distinct_per_worker;
            thread::Builder::new()
                .name(format!("hft-tpacket-{worker_index}"))
                .spawn(move || {
                    run_capture_worker(
                        ring,
                        worker_index,
                        cpu,
                        duration,
                        worker_gate,
                        worker_setup,
                        worker_stop,
                        worker_sender,
                        worker_metrics,
                        max_active_flows,
                        idle_timeout_s,
                        active_timeout_s,
                        max_payload_sample,
                        affinity_evidence_max_distinct,
                    )
                })
                .context("spawn TPACKET capture worker")
        })
        .collect::<Result<Vec<_>>>()?;
    drop(setup_tx);
    drop(feature_tx);

    let mut setup_results = Vec::with_capacity(REQUIRED_CAPTURE_WORKERS);
    for _ in 0..REQUIRED_CAPTURE_WORKERS {
        match setup_rx.recv_timeout(Duration::from_secs(5)) {
            Ok(result) => setup_results.push(result),
            Err(error) => {
                setup_results.push(Err(format!("capture worker setup channel: {error}")));
                stop.store(true, Ordering::Release);
                break;
            }
        }
    }
    let all_setup_ok = setup_results.iter().all(Result::is_ok);
    if !all_setup_ok {
        stop.store(true, Ordering::Release);
    }
    let start = Instant::now() + Duration::from_millis(args.start_delay_ms);
    gate.publish(start);
    if let Some(path) = &args.ready_file {
        write_json(
            path,
            &serde_json::json!({
                "ready": all_setup_ok && gpu_ready_at_start,
                "interface": args.interface,
                "workers": REQUIRED_CAPTURE_WORKERS,
                "worker_cpus": args.worker_cpus,
                "scheduler_cpu": args.scheduler_cpu,
                "fanout_mode": ring_config.fanout_mode.label(),
                "fanout_id": fanout_reservation.id,
                "fanout_id_source": fanout_reservation.source,
                "start_delay_ms": args.start_delay_ms,
                "gpu_ready_at_start": gpu_ready_at_start
            }),
        )?;
    }

    let mut workers = Vec::with_capacity(REQUIRED_CAPTURE_WORKERS);
    for handle in worker_handles {
        workers.push(
            handle
                .join()
                .map_err(|_| anyhow::anyhow!("capture worker panicked"))?,
        );
    }
    let scheduler = scheduler_handle
        .join()
        .map_err(|_| anyhow::anyhow!("scheduler and dispatcher thread panicked"))?;
    let cpu_elapsed = process_cpu_time()?
        .saturating_sub(cpu_started)
        .as_secs_f64();

    let packets = workers.iter().map(|worker| worker.packets).sum::<u64>();
    let bytes = workers.iter().map(|worker| worker.bytes).sum::<u64>();
    let packets_parsed = workers
        .iter()
        .map(|worker| worker.packets_parsed)
        .sum::<u64>();
    let parse_rejected = workers
        .iter()
        .map(|worker| worker.parse_rejected)
        .sum::<u64>();
    let fixed_profile_fast_parsed = workers
        .iter()
        .map(|worker| worker.fixed_profile_fast_parsed)
        .sum::<u64>();
    let fixed_profile_general_fallback = workers
        .iter()
        .map(|worker| worker.fixed_profile_general_fallback)
        .sum::<u64>();
    let flows_closed = workers
        .iter()
        .map(|worker| worker.flows_closed)
        .sum::<u64>();
    let feature_queue_submitted = workers
        .iter()
        .map(|worker| worker.feature_queue_submitted)
        .sum::<u64>();
    let feature_queue_drops = workers
        .iter()
        .map(|worker| worker.feature_queue_drops)
        .sum::<u64>();
    let key_feature_queue_drops = workers
        .iter()
        .map(|worker| worker.key_feature_queue_drops)
        .sum::<u64>();
    let statistics_packets = workers
        .iter()
        .map(|worker| worker.socket_statistics.packets)
        .sum::<u64>();
    let socket_drops = workers
        .iter()
        .map(|worker| worker.socket_statistics.drops)
        .sum::<u64>();
    let freeze_count = workers
        .iter()
        .map(|worker| worker.socket_statistics.freeze_queue_count)
        .sum::<u64>();
    let stats_reads = workers
        .iter()
        .map(|worker| worker.socket_statistics.destructive_reads)
        .sum::<u64>();
    metrics
        .packets_received
        .fetch_add(packets, Ordering::Relaxed);
    metrics
        .packets_parsed
        .fetch_add(packets_parsed, Ordering::Relaxed);
    metrics
        .parse_rejected
        .fetch_add(parse_rejected, Ordering::Relaxed);
    for sample in workers
        .iter()
        .flat_map(|worker| worker.parse_flow_latency_samples_us.iter())
    {
        metrics.observe_packet_latency(Duration::from_micros(*sample));
    }
    let epoch_second_counts = merge_epoch_counts(&workers);
    let packet_continuity =
        merge_packet_continuity(workers.iter().map(|worker| &worker.packet_continuity));
    let full_counts = full_epoch_counts(&epoch_second_counts);
    let elapsed = duration.as_secs_f64();
    let all_workers_error_free = workers.iter().all(|worker| worker.fatal_error.is_none());
    let scheduler_error_free = scheduler.fatal_error.is_none();
    let qm_flow_affinity_evidence = build_flow_affinity_evidence(&workers);
    let qm_runtime_gate = !matches!(args.fanout_mode, CliFanoutMode::Qm)
        || qm_flow_affinity_evidence.runtime_verified;
    let pipeline_metrics = metrics.report(
        "live_interface".to_string(),
        args.interface.clone(),
        "tpacket_v3_borrowed_packet_fanout".to_string(),
        "not_sealed_by_raw_runner".to_string(),
        "hft_mgbs_tpacket_v3_full_pipeline".to_string(),
        "tpacket_v3_software_receive_timestamp".to_string(),
        duration,
        socket_drops,
        0,
        0.0,
        None,
        0,
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
    let packet_continuity_windows = packet_continuity.packet_continuity_windows.clone();
    let packet_gap = packet_continuity.packet_gap;
    let packet_continuity_gate = packet_continuity.supported
        && packet_continuity.input_conservation_ok
        && packet_continuity.ownership_merge_conservation_ok
        && packet_continuity.packet_gap == 0
        && packet_continuity.duplicate_packets == 0
        && packet_continuity.reordered_group_packets == 0;
    let report = FullPipelineReport {
        schema_version: 2,
        scope: "hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw",
        backend: "tpacket_v3_packet_fanout_borrowed",
        interface: args.interface,
        fanout_mode: ring_config.fanout_mode.label(),
        fanout_id: fanout_reservation.id,
        fanout_id_source: fanout_reservation.source,
        fanout_lock_path: fanout_reservation.path.display().to_string(),
        qm_flow_affinity_authorized: args.allow_qm_with_verified_flow_affinity,
        qm_flow_affinity_evidence,
        worker_cpus: args.worker_cpus,
        scheduler_cpu: args.scheduler_cpu,
        duration_s: elapsed,
        block_size: args.block_size,
        block_count_per_worker: args.block_count,
        frame_size: args.frame_size,
        ring_memory_bytes: u64::from(args.block_size)
            * u64::from(args.block_count)
            * REQUIRED_CAPTURE_WORKERS as u64,
        feature_queue_capacity: args.feature_queue_capacity,
        gpu_queue_capacity: args.gpu_queue_capacity,
        gpu_ready_at_start,
        expected_gpu_identity: ExpectedBackendIdentity {
            candidate_id: args.expected_gpu_candidate.clone(),
            schema_version: args.expected_gpu_schema,
            model_sha256: args.expected_gpu_model_sha256.clone(),
            inference_engine: args.expected_gpu_inference_engine.clone(),
        },
        packets,
        bytes,
        achieved_mpps: packets as f64 / elapsed / 1_000_000.0,
        achieved_gbps: bytes as f64 * 8.0 / elapsed / 1_000_000_000.0,
        packets_parsed,
        parse_rejected,
        parser_profile_id: "deterministic_multiflow_v2_fixed64_ipv4_udp_strict_v1",
        fixed_profile_fast_parsed,
        fixed_profile_general_fallback,
        flows_closed,
        feature_queue_submitted,
        feature_queue_drops,
        key_feature_queue_drops,
        packet_socket_statistics_packets: statistics_packets,
        packet_socket_drops: socket_drops,
        packet_socket_freeze_queue_count: freeze_count,
        packet_socket_statistics_destructive_reads: stats_reads,
        full_epoch_windows: full_counts.len(),
        min_full_epoch_mpps: full_counts
            .iter()
            .copied()
            .min()
            .map(|count| count as f64 / 1_000_000.0),
        epoch_second_counts,
        packet_continuity_windows,
        packet_gap,
        packet_continuity,
        process_cpu_cores_average: cpu_elapsed / elapsed,
        shutdown: ShutdownReport {
            stop_flag_observed: stop.load(Ordering::Acquire)
                || TERMINATE_REQUESTED.load(Ordering::Acquire),
            capture_workers_joined: workers.len(),
            capture_workers_expected: REQUIRED_CAPTURE_WORKERS,
            scheduler_thread_joined: true,
            scheduler_input_channel_drained: scheduler.input_channel_drained,
            dispatcher_finish_called: scheduler.dispatcher_finish_called,
        },
        all_workers_error_free,
        internal_delivery_lossless: feature_queue_drops == 0,
        capture_lossless: socket_drops == 0 && freeze_count == 0,
        raw_full_pipeline_observation: all_workers_error_free
            && scheduler_error_free
            && gpu_ready_at_start
            && qm_runtime_gate
            && packet_continuity_gate
            && !stop.load(Ordering::Acquire)
            && !TERMINATE_REQUESTED.load(Ordering::Acquire),
        runtime_identity_verified: false,
        full_pipeline_qualified: false,
        final_pareto_ingestion_allowed: false,
        workers,
        scheduler,
        pipeline_metrics,
    };
    write_json(&args.output, &report)?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    if !report.all_workers_error_free || report.scheduler.fatal_error.is_some() {
        bail!("raw full-pipeline run completed with worker or scheduler errors");
    }
    if matches!(args.fanout_mode, CliFanoutMode::Qm)
        && !report.qm_flow_affinity_evidence.runtime_verified
    {
        bail!("QM runtime flow-affinity evidence is incomplete or has cross-worker collisions");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bounded_queue_drop_is_explicit_and_affects_key_coverage() {
        let (sender, _receiver) = bounded::<u8>(1);
        sender.try_send(1).unwrap();
        let metrics = RuntimeMetrics::default();
        let mut report = WorkerReport::default();
        record_send_result(sender.try_send(2), true, &mut report, &metrics);
        assert_eq!(report.feature_queue_drops, 1);
        assert_eq!(report.key_feature_queue_drops, 1);
        assert_eq!(metrics.flows_emitted.load(Ordering::Relaxed), 1);
        assert_eq!(metrics.key_flows_total.load(Ordering::Relaxed), 1);
        assert_eq!(metrics.key_flows_enqueue_failed.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn full_epoch_windows_exclude_partial_edges() {
        let counts = BTreeMap::from([(10, 4), (11, 8), (12, 9), (13, 2)]);
        assert_eq!(full_epoch_counts(&counts), vec![8, 9]);
    }

    #[test]
    fn expiry_delta_observation_omits_epoch_sized_first_sample_without_changing_scan_count() {
        let mut report = WorkerReport {
            expire_scan_calls: 1,
            ..WorkerReport::default()
        };
        record_expire_event_time_delta(&mut report, 0, 1_720_000_000_000_000);
        assert!(report.expire_scan_first_delta_omitted);
        assert_eq!(report.expire_scan_calls, 1);
        assert_eq!(report.expire_scan_event_time_delta_samples, 0);
        assert_eq!(report.expire_scan_event_time_delta_us_min, None);
        assert_eq!(report.expire_scan_event_time_delta_us_max, None);

        record_expire_event_time_delta(&mut report, 1_720_000_000_000_000, 1_720_000_001_250_000);
        record_expire_event_time_delta(&mut report, 1_720_000_001_250_000, 1_720_000_002_100_000);
        assert_eq!(report.expire_scan_calls, 1);
        assert_eq!(report.expire_scan_event_time_delta_samples, 2);
        assert_eq!(report.expire_scan_event_time_delta_us_min, Some(850_000));
        assert_eq!(report.expire_scan_event_time_delta_us_max, Some(1_250_000));
    }

    #[test]
    fn epoch_accumulator_matches_per_packet_btree_for_monotonic_and_disordered_input() {
        let seconds = [10, 10, 10, 11, 11, 13, 12, 13, 9, 14, 14];
        let mut expected = BTreeMap::new();
        for second in seconds {
            *expected.entry(second).or_insert(0) += 1;
        }
        let mut accumulator = EpochSecondAccumulator::default();
        for second in seconds {
            accumulator.record(second);
        }
        let (actual, out_of_order) = accumulator.finish();
        assert_eq!(actual, expected);
        assert_eq!(out_of_order, 2);
    }

    #[test]
    fn epoch_accumulator_avoids_tree_updates_within_one_second() {
        let mut accumulator = EpochSecondAccumulator::default();
        for _ in 0..1_000_000 {
            accumulator.record(42);
        }
        assert!(accumulator.completed.is_empty());
        let (counts, out_of_order) = accumulator.finish();
        assert_eq!(counts, BTreeMap::from([(42, 1_000_000)]));
        assert_eq!(out_of_order, 0);
    }

    #[test]
    #[ignore = "informational release microbenchmark; run explicitly"]
    fn microbench_epoch_scalar_accumulator_against_per_packet_btree() {
        use std::hint::black_box;
        const ITERATIONS: u64 = 20_000_000;
        let mut optimized = EpochSecondAccumulator::default();
        let optimized_started = Instant::now();
        for _ in 0..ITERATIONS {
            optimized.record(black_box(42));
        }
        let optimized_elapsed = optimized_started.elapsed();
        let (optimized_counts, _) = optimized.finish();

        let mut reference = BTreeMap::new();
        let reference_started = Instant::now();
        for _ in 0..ITERATIONS {
            *reference.entry(black_box(42)).or_insert(0) += 1;
        }
        let reference_elapsed = reference_started.elapsed();
        assert_eq!(optimized_counts, reference);
        eprintln!(
            "epoch_scalar_accumulator iterations={ITERATIONS} optimized_ns={} reference_ns={} speedup={:.3}",
            optimized_elapsed.as_nanos(),
            reference_elapsed.as_nanos(),
            reference_elapsed.as_secs_f64() / optimized_elapsed.as_secs_f64()
        );
    }

    #[test]
    fn disconnected_queue_is_counted_as_drop() {
        let (sender, receiver) = bounded::<u8>(1);
        drop(receiver);
        let metrics = RuntimeMetrics::default();
        let mut report = WorkerReport::default();
        record_send_result(sender.try_send(1), false, &mut report, &metrics);
        assert_eq!(report.feature_queue_drops, 1);
        assert_eq!(metrics.fallback_flows.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn explicit_fanout_id_requires_collision_override() {
        let error = reserve_fanout_id(Some(12), false).unwrap_err();
        assert!(error.to_string().contains("--allow-explicit-fanout-id"));
    }

    fn affinity_worker(index: usize, flows: &[(&str, u64)]) -> WorkerReport {
        WorkerReport {
            worker_index: index,
            flows_closed: flows.iter().map(|(_, count)| count).sum(),
            flow_affinity_hash_counts: flows
                .iter()
                .map(|(flow, count)| (stable_flow_id_hash(flow), *count))
                .collect(),
            ..WorkerReport::default()
        }
    }

    #[test]
    fn qm_runtime_affinity_requires_complete_nonempty_zero_collision_evidence() {
        let evidence = build_flow_affinity_evidence(&[
            affinity_worker(0, &[("flow-a", 3)]),
            affinity_worker(1, &[("flow-b", 2)]),
        ]);
        assert_eq!(evidence.closed_flow_observations, 5);
        assert_eq!(evidence.distinct_flow_hashes, 2);
        assert_eq!(evidence.same_worker_reopen_observations, 3);
        assert_eq!(evidence.cross_worker_collision_count, 0);
        assert!(evidence.evidence_complete);
        assert!(evidence.runtime_verified);
    }

    #[test]
    fn qm_runtime_affinity_rejects_one_flow_seen_by_two_workers() {
        let evidence = build_flow_affinity_evidence(&[
            affinity_worker(0, &[("same-flow", 1)]),
            affinity_worker(7, &[("same-flow", 1)]),
        ]);
        assert_eq!(evidence.distinct_flow_hashes, 1);
        assert_eq!(evidence.cross_worker_collision_count, 1);
        assert!(!evidence.runtime_verified);
        assert_eq!(evidence.cross_worker_collision_examples.len(), 1);
    }

    #[test]
    fn qm_runtime_affinity_rejects_bounded_evidence_overflow() {
        let mut worker = affinity_worker(0, &[("flow-a", 1)]);
        worker.flows_closed = 2;
        worker.flow_affinity_evidence_overflow = true;
        let evidence = build_flow_affinity_evidence(&[worker]);
        assert!(evidence.evidence_overflow);
        assert!(!evidence.evidence_complete);
        assert!(!evidence.runtime_verified);
    }
}
