use crate::flow::ScheduledFlow;
use serde::Serialize;
use std::collections::BTreeMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Mutex, OnceLock};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const MAX_LATENCY_SAMPLES: usize = 1_000_000;
const MAX_GPU_RAW_EVIDENCE: usize = 100_000;
static METRICS_MONOTONIC_ORIGIN: OnceLock<Instant> = OnceLock::new();
pub const PACKET_LATENCY_SAMPLE_STRIDE: u64 = 1024;
pub const REMOTE_BACKEND_IDENTITY: &str = "A09/schema_v1/ordered_v1";
pub const LOCAL_FALLBACK_BACKEND_IDENTITY: &str = "none_without_equivalent_a09_model";

pub fn should_sample_packet_latency(packet_sequence: u64) -> bool {
    packet_sequence == 1 || packet_sequence.is_multiple_of(PACKET_LATENCY_SAMPLE_STRIDE)
}

#[derive(Default)]
pub struct RuntimeMetrics {
    pub packets_received: AtomicU64,
    pub packets_parsed: AtomicU64,
    pub parse_rejected: AtomicU64,
    pub flows_emitted: AtomicU64,
    pub key_flows_total: AtomicU64,
    pub key_flows_base_materialized: AtomicU64,
    pub key_flows_deep_selected: AtomicU64,
    pub key_flows_enqueued: AtomicU64,
    pub key_flows_enqueue_failed: AtomicU64,
    pub key_flows_scored: AtomicU64,
    pub key_flows_inference_failed: AtomicU64,
    pub key_flows_local_fallback_completed: AtomicU64,
    pub key_flows_recovery_cached: AtomicU64,
    pub key_flows_recovery_retried: AtomicU64,
    pub key_flows_recovery_remote_scored: AtomicU64,
    pub key_flows_terminal_unresolved: AtomicU64,
    pub key_flows_recovery_pending: AtomicU64,
    pub gpu_flows_enqueued: AtomicU64,
    pub gpu_flows_scored: AtomicU64,
    pub gpu_queue_full: AtomicU64,
    pub gpu_batches_ok: AtomicU64,
    pub gpu_batches_failed: AtomicU64,
    pub gpu_backend_identity_failures: AtomicU64,
    pub gpu_worker_join_failures: AtomicU64,
    pub fallback_flows: AtomicU64,
    pub deep_flows_selected: AtomicU64,
    pub deep_flows_deferred: AtomicU64,
    pub budget_overrun_count: AtomicU64,
    pub kernel_timestamp_anomalies: AtomicU64,
    pub realtime_clock_step_count: AtomicU64,
    packet_latency_us: Mutex<Vec<f64>>,
    feature_event_enqueue_latency_us: Mutex<Vec<f64>>,
    kernel_to_feature_enqueue_latency_us: Mutex<Vec<f64>>,
    realtime_clock_reference: Mutex<Option<(u64, Instant)>>,
    gpu_batch_latency_us: Mutex<Vec<f64>>,
    budget_planned_deep_cost_us: Mutex<Vec<f64>>,
    budget_actual_deep_cost_us: Mutex<Vec<f64>>,
    raw_latency_sequence: AtomicU64,
    raw_latency_receipts: Mutex<Vec<LatencySampleReceipt>>,
    raw_latency_receipts_truncated: AtomicU64,
    flow_completion_receipts: Mutex<Vec<FlowCompletionReceipt>>,
    flow_completion_receipts_truncated: AtomicU64,
    local_fallback_completion_receipts: Mutex<Vec<LocalFallbackCompletionReceipt>>,
    local_fallback_completion_receipts_truncated: AtomicU64,
    gpu_evidence: Mutex<GpuEvidenceStore>,
}

#[derive(Debug, Clone, Serialize)]
pub struct LatencySampleReceipt {
    pub source_id: String,
    pub metric: &'static str,
    pub observed_epoch_us: u64,
    pub observed_monotonic_us: u64,
    pub window_id: u64,
    pub source_event_epoch_us: Option<u64>,
    pub value_us: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct GpuBatchEvidence {
    pub sequence: u64,
    pub source_id: String,
    pub event_epoch_us: u64,
    pub window_id: u64,
    pub request_id: Option<u64>,
    pub attempt_kind: String,
    pub outcome: String,
    pub flows: u64,
    pub key_flows: u64,
    pub remote_scored: u64,
    pub key_remote_scored: u64,
    pub key_cached: u64,
    pub key_terminal_unresolved: u64,
    pub round_trip_us: Option<f64>,
    pub failure_code: Option<String>,
    pub backend_identity: Option<String>,
}

#[derive(Debug, Clone, Default, Serialize)]
pub struct GpuWindowEvidence {
    pub epoch_second: u64,
    pub window_source_id: String,
    pub key_flows_eligible: u64,
    pub key_flows_deep_selected: u64,
    pub flows_enqueued: u64,
    pub key_flows_enqueued: u64,
    pub key_flows_enqueue_failed: u64,
    pub batches_attempted: u64,
    pub batches_ok: u64,
    pub batches_failed: u64,
    pub circuit_open_batches: u64,
    pub flows_remote_scored: u64,
    pub key_flows_remote_scored: u64,
    pub key_flows_cached: u64,
    pub key_flows_terminal_unresolved: u64,
    pub key_flows_recovery_pending_after_event: u64,
    pub gpu_queue_full: u64,
}

#[derive(Debug, Clone, Serialize)]
pub struct GpuFaultRecoveryEvidence {
    pub episode: u64,
    pub fault_injection_epoch_us: Option<u64>,
    pub fault_injection_monotonic_ns: Option<u64>,
    pub fault_injection_label: Option<String>,
    pub fault_detected_epoch_us: u64,
    pub fault_detected_monotonic_ns: u64,
    pub failure_code: String,
    pub key_flows_cached: u64,
    pub recovery_epoch_us: Option<u64>,
    pub recovery_monotonic_ns: Option<u64>,
    pub recovery_us: Option<u64>,
    pub recovered_backend_identity: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct FlowCompletionReceipt {
    pub source_id: String,
    pub flow_id: String,
    pub flow_id_hash_fnv1a64: String,
    pub request_id: u64,
    pub response_index: u64,
    pub window_id: u64,
    pub trigger_timestamp_us: Option<u64>,
    pub materialization_epoch_us: u64,
    pub completion_epoch_us: u64,
    pub materialization_to_remote_completion_us: u64,
    pub kernel_to_remote_completion_us: Option<u64>,
    pub recovery_attempts: u32,
    pub backend_identity: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct FlowCompletionConservation {
    pub remote_scored_flows: u64,
    pub completion_receipts: u64,
    pub truncated_receipts: u64,
    pub remote_scored_equals_receipts_plus_truncated: bool,
    pub absolute_delta: u64,
}

#[derive(Debug, Clone, Serialize)]
pub struct LocalFallbackCompletionReceipt {
    pub source_id: String,
    pub flow_id: String,
    pub flow_id_hash_fnv1a64: String,
    pub request_id: u64,
    pub response_index: u64,
    pub window_id: u64,
    pub trigger_timestamp_us: Option<u64>,
    pub materialization_epoch_us: u64,
    pub completion_epoch_us: u64,
    pub materialization_to_local_completion_us: u64,
    pub kernel_to_local_completion_us: Option<u64>,
    pub recovery_attempts: u32,
    pub probability: f64,
    pub label: u8,
    pub node_visits: u32,
    pub backend_identity: String,
    pub quality_receipt_sha256: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct LocalFallbackCompletionConservation {
    pub local_fallback_completed_flows: u64,
    pub completion_receipts: u64,
    pub truncated_receipts: u64,
    pub completed_equals_receipts_plus_truncated: bool,
    pub absolute_delta: u64,
}

#[derive(Debug, Clone, Serialize)]
pub struct KeyFlowConservation {
    pub eligible: u64,
    pub enqueued: u64,
    pub enqueue_failed: u64,
    pub remote_scored: u64,
    pub local_fallback_completed: u64,
    pub terminal_unresolved: u64,
    pub recovery_pending: u64,
    pub eligible_equals_enqueue_outcomes: bool,
    pub enqueued_equals_completion_outcomes: bool,
    pub eligible_conservation_abs_delta: u64,
    pub completion_conservation_abs_delta: u64,
}

#[derive(Default)]
struct GpuEvidenceStore {
    batches: Vec<GpuBatchEvidence>,
    windows: BTreeMap<u64, GpuWindowEvidence>,
    faults: Vec<GpuFaultRecoveryEvidence>,
    active_fault: Option<(usize, Instant)>,
    pending_injection: Option<(u64, u64, String)>,
    truncated_batches: u64,
    truncated_windows: u64,
    truncated_faults: u64,
}

impl GpuEvidenceStore {
    fn window_mut(&mut self, epoch_second: u64) -> &mut GpuWindowEvidence {
        if !self.windows.contains_key(&epoch_second) && self.windows.len() >= MAX_GPU_RAW_EVIDENCE {
            if let Some(oldest) = self.windows.keys().next().copied() {
                self.windows.remove(&oldest);
                self.truncated_windows = self.truncated_windows.saturating_add(1);
            }
        }
        self.windows
            .entry(epoch_second)
            .or_insert_with(|| GpuWindowEvidence {
                epoch_second,
                window_source_id: format!("gpu_window:{epoch_second}"),
                ..GpuWindowEvidence::default()
            })
    }
}

#[derive(Debug, Serialize)]
pub struct Percentiles {
    pub samples: usize,
    pub p50_us: f64,
    pub p99_us: f64,
    pub p999_us: f64,
    pub max_us: f64,
}

#[derive(Debug, Serialize)]
pub struct MetricsReport {
    pub schema_version: u32,
    pub evidence_scope: &'static str,
    pub source_kind: String,
    pub source: String,
    pub capture_driver: String,
    pub platform_probe_head: String,
    pub platform_rust_tree: String,
    pub candidate_id: String,
    pub timestamp_provenance: String,
    pub elapsed_s: f64,
    pub packets_received: u64,
    pub packets_parsed: u64,
    pub parse_rejected: u64,
    pub parse_reject_rate: f64,
    pub capture_packets_dropped: u64,
    pub capture_drop_rate: f64,
    pub capture_driver_fallback_count: u64,
    pub capture_driver_fallback_recovery_ms: f64,
    pub capture_driver_fallback_reason: Option<String>,
    pub capture_driver_fallback_packets: u64,
    pub flows_emitted: u64,
    pub key_flows_total: u64,
    pub key_flows_base_materialized: u64,
    pub key_flows_deep_selected: u64,
    pub key_flows_enqueued: u64,
    pub key_flows_enqueue_failed: u64,
    pub key_flows_scored: u64,
    pub key_flows_inference_failed: u64,
    pub key_flows_local_fallback_completed: u64,
    pub key_flows_recovery_cached: u64,
    pub key_flows_recovery_retried: u64,
    pub key_flows_recovery_remote_scored: u64,
    pub key_flows_terminal_unresolved: u64,
    pub key_flows_recovery_pending: u64,
    pub key_flow_enqueue_coverage: Option<f64>,
    pub key_flow_deep_coverage: Option<f64>,
    pub key_flow_completion_coverage: Option<f64>,
    pub key_flow_coverage: Option<f64>,
    pub key_flow_coverage_basis: &'static str,
    pub key_flow_conservation: KeyFlowConservation,
    pub remote_backend_identity: String,
    pub local_fallback_backend_identity: String,
    pub local_fallback_quality_qualified: bool,
    pub key_flow_quality_qualified: bool,
    pub gpu_flows_enqueued: u64,
    pub gpu_flows_scored: u64,
    pub gpu_queue_full: u64,
    pub gpu_batches_ok: u64,
    pub gpu_batches_failed: u64,
    pub gpu_backend_identity_failures: u64,
    pub gpu_worker_join_failures: u64,
    pub fallback_flows: u64,
    pub deep_flows_selected: u64,
    pub deep_flows_deferred: u64,
    pub budget_overrun_count: u64,
    pub kernel_timestamp_anomalies: u64,
    pub realtime_clock_step_count: u64,
    pub packet_processing_latency: Percentiles,
    pub packet_processing_latency_sample_stride: u64,
    pub flow_materialization_to_feature_enqueue_latency: Percentiles,
    pub kernel_receive_to_feature_enqueue_latency: Percentiles,
    pub gpu_batch_round_trip_latency: Percentiles,
    pub budget_planned_deep_cost: Percentiles,
    pub budget_actual_deep_cost: Percentiles,
    pub raw_latency_sample_receipts: Vec<LatencySampleReceipt>,
    pub raw_latency_sample_receipts_truncated: u64,
    pub gpu_batch_evidence: Vec<GpuBatchEvidence>,
    pub gpu_window_evidence: Vec<GpuWindowEvidence>,
    pub gpu_fault_recovery_evidence: Vec<GpuFaultRecoveryEvidence>,
    pub flow_completion_receipts: Vec<FlowCompletionReceipt>,
    pub flow_completion_receipts_truncated: u64,
    pub flow_completion_conservation: FlowCompletionConservation,
    pub local_fallback_completion_receipts: Vec<LocalFallbackCompletionReceipt>,
    pub local_fallback_completion_receipts_truncated: u64,
    pub local_fallback_completion_conservation: LocalFallbackCompletionConservation,
    pub gpu_batch_evidence_truncated: u64,
    pub gpu_window_evidence_truncated: u64,
    pub gpu_fault_recovery_evidence_truncated: u64,
}

impl RuntimeMetrics {
    fn epoch_us() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_micros()
            .min(u64::MAX as u128) as u64
    }

    fn monotonic_ns() -> u64 {
        #[cfg(target_os = "linux")]
        {
            let mut value = libc::timespec {
                tv_sec: 0,
                tv_nsec: 0,
            };
            let status = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut value) };
            if status == 0 {
                return (value.tv_sec as u64)
                    .saturating_mul(1_000_000_000)
                    .saturating_add(value.tv_nsec as u64);
            }
        }
        METRICS_MONOTONIC_ORIGIN
            .get_or_init(Instant::now)
            .elapsed()
            .as_nanos()
            .min(u64::MAX as u128) as u64
    }

    fn fnv1a64(value: &str) -> u64 {
        value.bytes().fold(0xcbf29ce484222325u64, |hash, byte| {
            (hash ^ u64::from(byte)).wrapping_mul(0x100000001b3)
        })
    }

    fn push_raw_latency(
        &self,
        metric: &'static str,
        value_us: f64,
        source_event_epoch_us: Option<u64>,
    ) {
        let observed_epoch_us = Self::epoch_us();
        let sequence = self
            .raw_latency_sequence
            .fetch_add(1, Ordering::Relaxed)
            .saturating_add(1);
        let receipt = LatencySampleReceipt {
            source_id: format!("{metric}:{sequence}"),
            metric,
            observed_epoch_us,
            observed_monotonic_us: METRICS_MONOTONIC_ORIGIN
                .get_or_init(Instant::now)
                .elapsed()
                .as_micros()
                .min(u64::MAX as u128) as u64,
            window_id: observed_epoch_us / 1_000_000,
            source_event_epoch_us,
            value_us,
        };
        let mut receipts = self
            .raw_latency_receipts
            .lock()
            .expect("raw latency receipt mutex poisoned");
        if receipts.len() < MAX_LATENCY_SAMPLES {
            receipts.push(receipt);
        } else {
            self.raw_latency_receipts_truncated
                .fetch_add(1, Ordering::Relaxed);
        }
    }

    pub fn record_key_schedule(&self, eligible: u64, deep_selected: u64) {
        let epoch_second = Self::epoch_us() / 1_000_000;
        let mut evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        let window = evidence.window_mut(epoch_second);
        window.key_flows_eligible = window.key_flows_eligible.saturating_add(eligible);
        window.key_flows_deep_selected =
            window.key_flows_deep_selected.saturating_add(deep_selected);
    }

    pub fn record_gpu_enqueue_failure(&self, is_key_flow: bool) {
        let epoch_second = Self::epoch_us() / 1_000_000;
        let mut evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        let window = evidence.window_mut(epoch_second);
        window.gpu_queue_full = window.gpu_queue_full.saturating_add(1);
        if is_key_flow {
            window.key_flows_enqueue_failed = window.key_flows_enqueue_failed.saturating_add(1);
        }
    }

    /// Mark the instant at which an external fault injector changes GPU
    /// connectivity. The marker does not inject a fault by itself; the next
    /// observed transport/protocol failure consumes it as auditable evidence.
    pub fn mark_gpu_fault_injection(&self, label: impl Into<String>) -> u64 {
        let epoch_us = Self::epoch_us();
        let monotonic_ns = Self::monotonic_ns();
        self.gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned")
            .pending_injection = Some((epoch_us, monotonic_ns, label.into()));
        epoch_us
    }

    pub fn record_flow_completion(
        &self,
        request_id: u64,
        response_index: u64,
        flow: &ScheduledFlow,
        recovery_attempts: u32,
        backend_identity: &str,
    ) {
        let completion_epoch_us = Self::epoch_us();
        let materialization_to_remote_completion_us =
            flow.ready_at.elapsed().as_micros().min(u64::MAX as u128) as u64;
        let materialization_epoch_us =
            completion_epoch_us.saturating_sub(materialization_to_remote_completion_us);
        let flow_hash = Self::fnv1a64(&flow.flow_id);
        let receipt = FlowCompletionReceipt {
            source_id: format!(
                "gpu_flow_completion:{request_id}:{response_index}:{flow_hash:016x}"
            ),
            flow_id: flow.flow_id.clone(),
            flow_id_hash_fnv1a64: format!("{flow_hash:016x}"),
            request_id,
            response_index,
            window_id: completion_epoch_us / 1_000_000,
            trigger_timestamp_us: flow.trigger_timestamp_us,
            materialization_epoch_us,
            completion_epoch_us,
            materialization_to_remote_completion_us,
            kernel_to_remote_completion_us: flow
                .trigger_timestamp_us
                .and_then(|trigger| completion_epoch_us.checked_sub(trigger)),
            recovery_attempts,
            backend_identity: backend_identity.to_string(),
        };
        let mut receipts = self
            .flow_completion_receipts
            .lock()
            .expect("flow completion receipt mutex poisoned");
        if receipts.len() < MAX_LATENCY_SAMPLES {
            receipts.push(receipt);
        } else {
            self.flow_completion_receipts_truncated
                .fetch_add(1, Ordering::Relaxed);
        }
    }

    #[allow(clippy::too_many_arguments)]
    pub fn record_local_fallback_completion(
        &self,
        request_id: u64,
        response_index: u64,
        flow: &ScheduledFlow,
        recovery_attempts: u32,
        probability: f64,
        label: u8,
        node_visits: u32,
        backend_identity: &str,
        quality_receipt_sha256: &str,
    ) {
        let completion_epoch_us = Self::epoch_us();
        let materialization_to_local_completion_us =
            flow.ready_at.elapsed().as_micros().min(u64::MAX as u128) as u64;
        let materialization_epoch_us =
            completion_epoch_us.saturating_sub(materialization_to_local_completion_us);
        let flow_hash = Self::fnv1a64(&flow.flow_id);
        let receipt = LocalFallbackCompletionReceipt {
            source_id: format!(
                "local_fallback_completion:{request_id}:{response_index}:{flow_hash:016x}"
            ),
            flow_id: flow.flow_id.clone(),
            flow_id_hash_fnv1a64: format!("{flow_hash:016x}"),
            request_id,
            response_index,
            window_id: completion_epoch_us / 1_000_000,
            trigger_timestamp_us: flow.trigger_timestamp_us,
            materialization_epoch_us,
            completion_epoch_us,
            materialization_to_local_completion_us,
            kernel_to_local_completion_us: flow
                .trigger_timestamp_us
                .and_then(|trigger| completion_epoch_us.checked_sub(trigger)),
            recovery_attempts,
            probability,
            label,
            node_visits,
            backend_identity: backend_identity.to_string(),
            quality_receipt_sha256: quality_receipt_sha256.to_string(),
        };
        let mut receipts = self
            .local_fallback_completion_receipts
            .lock()
            .expect("local fallback completion receipt mutex poisoned");
        if receipts.len() < MAX_LATENCY_SAMPLES {
            receipts.push(receipt);
        } else {
            self.local_fallback_completion_receipts_truncated
                .fetch_add(1, Ordering::Relaxed);
        }
    }

    pub fn record_gpu_enqueue(&self, is_key_flow: bool) {
        let epoch_second = Self::epoch_us() / 1_000_000;
        let mut evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        let window = evidence.window_mut(epoch_second);
        window.flows_enqueued = window.flows_enqueued.saturating_add(1);
        if is_key_flow {
            window.key_flows_enqueued = window.key_flows_enqueued.saturating_add(1);
        }
    }

    pub fn record_gpu_batch(&self, mut batch: GpuBatchEvidence) {
        let epoch_second = batch.event_epoch_us / 1_000_000;
        let mut evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        batch.sequence = evidence
            .truncated_batches
            .saturating_add(evidence.batches.len() as u64)
            .saturating_add(1);
        batch.source_id = format!("gpu_batch:{}", batch.sequence);
        batch.window_id = epoch_second;
        let window = evidence.window_mut(epoch_second);
        if batch.request_id.is_some() {
            window.batches_attempted = window.batches_attempted.saturating_add(1);
        }
        match batch.outcome.as_str() {
            "remote_scored" => window.batches_ok = window.batches_ok.saturating_add(1),
            "circuit_open_cached_or_dropped" => {
                window.circuit_open_batches = window.circuit_open_batches.saturating_add(1)
            }
            _ => window.batches_failed = window.batches_failed.saturating_add(1),
        }
        window.flows_remote_scored = window
            .flows_remote_scored
            .saturating_add(batch.remote_scored);
        window.key_flows_remote_scored = window
            .key_flows_remote_scored
            .saturating_add(batch.key_remote_scored);
        window.key_flows_cached = window.key_flows_cached.saturating_add(batch.key_cached);
        window.key_flows_terminal_unresolved = window
            .key_flows_terminal_unresolved
            .saturating_add(batch.key_terminal_unresolved);
        window.key_flows_recovery_pending_after_event =
            self.key_flows_recovery_pending.load(Ordering::Relaxed);
        if evidence.batches.len() < MAX_GPU_RAW_EVIDENCE {
            evidence.batches.push(batch);
        } else {
            evidence.truncated_batches = evidence.truncated_batches.saturating_add(1);
        }
    }

    pub fn record_gpu_fault_observed(&self, failure_code: &str, key_flows_cached: u64) {
        let mut evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        if let Some((index, _)) = evidence.active_fault {
            evidence.faults[index].key_flows_cached = evidence.faults[index]
                .key_flows_cached
                .saturating_add(key_flows_cached);
            return;
        }
        let (fault_injection_epoch_us, fault_injection_monotonic_ns, fault_injection_label) =
            evidence
                .pending_injection
                .take()
                .map_or((None, None, None), |(epoch_us, monotonic_ns, label)| {
                    (Some(epoch_us), Some(monotonic_ns), Some(label))
                });
        if evidence.faults.len() >= MAX_GPU_RAW_EVIDENCE {
            evidence.faults.remove(0);
            evidence.truncated_faults = evidence.truncated_faults.saturating_add(1);
        }
        let index = evidence.faults.len();
        let episode = evidence.truncated_faults + index as u64 + 1;
        evidence.faults.push(GpuFaultRecoveryEvidence {
            episode,
            fault_injection_epoch_us,
            fault_injection_monotonic_ns,
            fault_injection_label,
            fault_detected_epoch_us: Self::epoch_us(),
            fault_detected_monotonic_ns: Self::monotonic_ns(),
            failure_code: failure_code.to_string(),
            key_flows_cached,
            recovery_epoch_us: None,
            recovery_monotonic_ns: None,
            recovery_us: None,
            recovered_backend_identity: None,
        });
        evidence.active_fault = Some((index, Instant::now()));
    }

    pub fn record_gpu_fault_recovered(&self, backend_identity: &str) {
        let mut evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        let Some((index, started)) = evidence.active_fault.take() else {
            return;
        };
        evidence.faults[index].recovery_epoch_us = Some(Self::epoch_us());
        evidence.faults[index].recovery_monotonic_ns = Some(Self::monotonic_ns());
        evidence.faults[index].recovery_us =
            Some(started.elapsed().as_micros().min(u64::MAX as u128) as u64);
        evidence.faults[index].recovered_backend_identity = Some(backend_identity.to_string());
    }

    pub fn observe_packet_latency(&self, elapsed: Duration) {
        let value_us = elapsed.as_secs_f64() * 1_000_000.0;
        Self::push_bounded(&self.packet_latency_us, value_us);
        self.push_raw_latency("packet_processing", value_us, None);
    }

    pub fn observe_gpu_latency(&self, elapsed: Duration) {
        let value_us = elapsed.as_secs_f64() * 1_000_000.0;
        Self::push_bounded(&self.gpu_batch_latency_us, value_us);
        self.push_raw_latency("gpu_batch_round_trip", value_us, None);
    }

    pub fn observe_budget_cost(&self, planned_us: f64, actual_us: f64) {
        Self::push_bounded(&self.budget_planned_deep_cost_us, planned_us);
        Self::push_bounded(&self.budget_actual_deep_cost_us, actual_us);
        self.push_raw_latency("budget_planned_deep_cost", planned_us, None);
        self.push_raw_latency("budget_actual_deep_cost", actual_us, None);
    }

    pub fn observe_feature_event_enqueue_latency(&self, elapsed: Duration) {
        let value_us = elapsed.as_secs_f64() * 1_000_000.0;
        Self::push_bounded(&self.feature_event_enqueue_latency_us, value_us);
        self.push_raw_latency("flow_materialization_to_feature_enqueue", value_us, None);
    }

    pub fn observe_kernel_to_feature_enqueue(&self, trigger_timestamp_us: u64) {
        let Ok(now) = SystemTime::now().duration_since(UNIX_EPOCH) else {
            return;
        };
        let now_us = now.as_micros().min(u64::MAX as u128) as u64;
        {
            let mut reference = self
                .realtime_clock_reference
                .lock()
                .expect("clock reference mutex poisoned");
            if let Some((previous_realtime_us, previous_monotonic)) = *reference {
                let monotonic_delta_us = previous_monotonic
                    .elapsed()
                    .as_micros()
                    .min(u64::MAX as u128) as u64;
                let realtime_delta_us = now_us.saturating_sub(previous_realtime_us);
                if now_us < previous_realtime_us
                    || realtime_delta_us.abs_diff(monotonic_delta_us) > 1000
                {
                    self.realtime_clock_step_count
                        .fetch_add(1, Ordering::Relaxed);
                }
            }
            *reference = Some((now_us, Instant::now()));
        }
        let Some(elapsed_us) = now_us.checked_sub(trigger_timestamp_us) else {
            self.kernel_timestamp_anomalies
                .fetch_add(1, Ordering::Relaxed);
            return;
        };
        if elapsed_us > 60_000_000 {
            self.kernel_timestamp_anomalies
                .fetch_add(1, Ordering::Relaxed);
            return;
        }
        Self::push_bounded(
            &self.kernel_to_feature_enqueue_latency_us,
            elapsed_us as f64,
        );
        self.push_raw_latency(
            "kernel_receive_to_feature_enqueue",
            elapsed_us as f64,
            Some(trigger_timestamp_us),
        );
    }

    fn push_bounded(store: &Mutex<Vec<f64>>, value: f64) {
        let mut values = store.lock().expect("latency mutex poisoned");
        if values.len() < MAX_LATENCY_SAMPLES {
            values.push(value);
        } else {
            let index = (value.to_bits() as usize) % MAX_LATENCY_SAMPLES;
            values[index] = value;
        }
    }

    fn percentiles(store: &Mutex<Vec<f64>>) -> Percentiles {
        let mut values = store.lock().expect("latency mutex poisoned").clone();
        if values.is_empty() {
            return Percentiles {
                samples: 0,
                p50_us: 0.0,
                p99_us: 0.0,
                p999_us: 0.0,
                max_us: 0.0,
            };
        }
        values.sort_by(f64::total_cmp);
        let at = |quantile: f64| -> f64 {
            let index = ((values.len() - 1) as f64 * quantile).ceil() as usize;
            values[index.min(values.len() - 1)]
        };
        Percentiles {
            samples: values.len(),
            p50_us: at(0.50),
            p99_us: at(0.99),
            p999_us: at(0.999),
            max_us: *values.last().unwrap_or(&0.0),
        }
    }

    #[allow(clippy::too_many_arguments)]
    pub fn report(
        &self,
        source_kind: String,
        source: String,
        capture_driver: String,
        platform_probe_head: String,
        platform_rust_tree: String,
        timestamp_provenance: String,
        elapsed: Duration,
        capture_packets_dropped: u64,
        capture_driver_fallback_count: u64,
        capture_driver_fallback_recovery_ms: f64,
        capture_driver_fallback_reason: Option<String>,
        capture_driver_fallback_packets: u64,
        candidate_id: String,
        remote_backend_identity: String,
        local_fallback_backend_identity: String,
        local_fallback_quality_qualified: bool,
    ) -> MetricsReport {
        let received = self.packets_received.load(Ordering::Relaxed);
        let parsed = self.packets_parsed.load(Ordering::Relaxed);
        let rejected = self.parse_rejected.load(Ordering::Relaxed);
        let key_total = self.key_flows_total.load(Ordering::Relaxed);
        let key_base_materialized = self.key_flows_base_materialized.load(Ordering::Relaxed);
        let key_deep_selected = self.key_flows_deep_selected.load(Ordering::Relaxed);
        let key_enqueued = self.key_flows_enqueued.load(Ordering::Relaxed);
        let key_scored = self.key_flows_scored.load(Ordering::Relaxed);
        let key_local_fallback_completed = self
            .key_flows_local_fallback_completed
            .load(Ordering::Relaxed);
        let key_enqueue_failed = self.key_flows_enqueue_failed.load(Ordering::Relaxed);
        let key_terminal_unresolved = self.key_flows_terminal_unresolved.load(Ordering::Relaxed);
        let key_recovery_pending = self.key_flows_recovery_pending.load(Ordering::Relaxed);
        let key_completed = key_scored
            .saturating_add(key_local_fallback_completed)
            .min(key_total);
        let enqueue_outcomes = key_enqueued.saturating_add(key_enqueue_failed);
        let completion_outcomes = key_scored
            .saturating_add(key_local_fallback_completed)
            .saturating_add(key_terminal_unresolved)
            .saturating_add(key_recovery_pending);
        let key_flow_conservation = KeyFlowConservation {
            eligible: key_total,
            enqueued: key_enqueued,
            enqueue_failed: key_enqueue_failed,
            remote_scored: key_scored,
            local_fallback_completed: key_local_fallback_completed,
            terminal_unresolved: key_terminal_unresolved,
            recovery_pending: key_recovery_pending,
            eligible_equals_enqueue_outcomes: key_total == enqueue_outcomes,
            enqueued_equals_completion_outcomes: key_enqueued == completion_outcomes,
            eligible_conservation_abs_delta: key_total.abs_diff(enqueue_outcomes),
            completion_conservation_abs_delta: key_enqueued.abs_diff(completion_outcomes),
        };
        let evidence = self
            .gpu_evidence
            .lock()
            .expect("GPU evidence mutex poisoned");
        let gpu_batch_evidence = evidence.batches.clone();
        let gpu_window_evidence = evidence.windows.values().cloned().collect();
        let gpu_fault_recovery_evidence = evidence.faults.clone();
        let gpu_batch_evidence_truncated = evidence.truncated_batches;
        let gpu_window_evidence_truncated = evidence.truncated_windows;
        let gpu_fault_recovery_evidence_truncated = evidence.truncated_faults;
        drop(evidence);
        let raw_latency_sample_receipts = self
            .raw_latency_receipts
            .lock()
            .expect("raw latency receipt mutex poisoned")
            .clone();
        let raw_latency_sample_receipts_truncated =
            self.raw_latency_receipts_truncated.load(Ordering::Relaxed);
        let flow_completion_receipts = self
            .flow_completion_receipts
            .lock()
            .expect("flow completion receipt mutex poisoned")
            .clone();
        let flow_completion_receipts_truncated = self
            .flow_completion_receipts_truncated
            .load(Ordering::Relaxed);
        let remote_scored_flows = self.gpu_flows_scored.load(Ordering::Relaxed);
        let recorded_or_truncated = (flow_completion_receipts.len() as u64)
            .saturating_add(flow_completion_receipts_truncated);
        let flow_completion_conservation = FlowCompletionConservation {
            remote_scored_flows,
            completion_receipts: flow_completion_receipts.len() as u64,
            truncated_receipts: flow_completion_receipts_truncated,
            remote_scored_equals_receipts_plus_truncated: remote_scored_flows
                == recorded_or_truncated,
            absolute_delta: remote_scored_flows.abs_diff(recorded_or_truncated),
        };
        let local_fallback_completion_receipts = self
            .local_fallback_completion_receipts
            .lock()
            .expect("local fallback completion receipt mutex poisoned")
            .clone();
        let local_fallback_completion_receipts_truncated = self
            .local_fallback_completion_receipts_truncated
            .load(Ordering::Relaxed);
        let local_recorded_or_truncated = (local_fallback_completion_receipts.len() as u64)
            .saturating_add(local_fallback_completion_receipts_truncated);
        let local_fallback_completion_conservation = LocalFallbackCompletionConservation {
            local_fallback_completed_flows: key_local_fallback_completed,
            completion_receipts: local_fallback_completion_receipts.len() as u64,
            truncated_receipts: local_fallback_completion_receipts_truncated,
            completed_equals_receipts_plus_truncated: key_local_fallback_completed
                == local_recorded_or_truncated,
            absolute_delta: key_local_fallback_completed.abs_diff(local_recorded_or_truncated),
        };
        MetricsReport {
            schema_version: 2,
            evidence_scope:
                "physical-host-offline-replay-or-live-capture; not production quality evidence",
            source_kind,
            source,
            capture_driver,
            platform_probe_head,
            platform_rust_tree,
            candidate_id,
            timestamp_provenance,
            elapsed_s: elapsed.as_secs_f64(),
            packets_received: received,
            packets_parsed: parsed,
            parse_rejected: rejected,
            parse_reject_rate: if received == 0 {
                0.0
            } else {
                rejected as f64 / received as f64
            },
            capture_packets_dropped,
            capture_drop_rate: if received + capture_packets_dropped == 0 {
                0.0
            } else {
                capture_packets_dropped as f64 / (received + capture_packets_dropped) as f64
            },
            capture_driver_fallback_count,
            capture_driver_fallback_recovery_ms,
            capture_driver_fallback_reason,
            capture_driver_fallback_packets,
            flows_emitted: self.flows_emitted.load(Ordering::Relaxed),
            key_flows_total: key_total,
            key_flows_base_materialized: key_base_materialized,
            key_flows_deep_selected: key_deep_selected,
            key_flows_enqueued: key_enqueued,
            key_flows_enqueue_failed: key_enqueue_failed,
            key_flows_scored: key_scored,
            key_flows_inference_failed: self.key_flows_inference_failed.load(Ordering::Relaxed),
            key_flows_local_fallback_completed: key_local_fallback_completed,
            key_flows_recovery_cached: self.key_flows_recovery_cached.load(Ordering::Relaxed),
            key_flows_recovery_retried: self.key_flows_recovery_retried.load(Ordering::Relaxed),
            key_flows_recovery_remote_scored: self
                .key_flows_recovery_remote_scored
                .load(Ordering::Relaxed),
            key_flows_terminal_unresolved: key_terminal_unresolved,
            key_flows_recovery_pending: key_recovery_pending,
            key_flow_enqueue_coverage: coverage_ratio(key_enqueued, key_total),
            key_flow_deep_coverage: coverage_ratio(key_deep_selected, key_total),
            key_flow_completion_coverage: coverage_ratio(key_completed, key_total),
            key_flow_coverage: coverage_ratio(key_completed, key_total),
            key_flow_coverage_basis: "remote_scored_or_local_fallback_completed",
            key_flow_conservation,
            remote_backend_identity,
            local_fallback_backend_identity,
            local_fallback_quality_qualified,
            key_flow_quality_qualified: false,
            gpu_flows_enqueued: self.gpu_flows_enqueued.load(Ordering::Relaxed),
            gpu_flows_scored: self.gpu_flows_scored.load(Ordering::Relaxed),
            gpu_queue_full: self.gpu_queue_full.load(Ordering::Relaxed),
            gpu_batches_ok: self.gpu_batches_ok.load(Ordering::Relaxed),
            gpu_batches_failed: self.gpu_batches_failed.load(Ordering::Relaxed),
            gpu_backend_identity_failures: self
                .gpu_backend_identity_failures
                .load(Ordering::Relaxed),
            gpu_worker_join_failures: self.gpu_worker_join_failures.load(Ordering::Relaxed),
            fallback_flows: self.fallback_flows.load(Ordering::Relaxed),
            deep_flows_selected: self.deep_flows_selected.load(Ordering::Relaxed),
            deep_flows_deferred: self.deep_flows_deferred.load(Ordering::Relaxed),
            budget_overrun_count: self.budget_overrun_count.load(Ordering::Relaxed),
            kernel_timestamp_anomalies: self.kernel_timestamp_anomalies.load(Ordering::Relaxed),
            realtime_clock_step_count: self.realtime_clock_step_count.load(Ordering::Relaxed),
            packet_processing_latency: Self::percentiles(&self.packet_latency_us),
            packet_processing_latency_sample_stride: PACKET_LATENCY_SAMPLE_STRIDE,
            flow_materialization_to_feature_enqueue_latency: Self::percentiles(
                &self.feature_event_enqueue_latency_us,
            ),
            kernel_receive_to_feature_enqueue_latency: Self::percentiles(
                &self.kernel_to_feature_enqueue_latency_us,
            ),
            gpu_batch_round_trip_latency: Self::percentiles(&self.gpu_batch_latency_us),
            budget_planned_deep_cost: Self::percentiles(&self.budget_planned_deep_cost_us),
            budget_actual_deep_cost: Self::percentiles(&self.budget_actual_deep_cost_us),
            raw_latency_sample_receipts,
            raw_latency_sample_receipts_truncated,
            gpu_batch_evidence,
            gpu_window_evidence,
            gpu_fault_recovery_evidence,
            flow_completion_receipts,
            flow_completion_receipts_truncated,
            flow_completion_conservation,
            local_fallback_completion_receipts,
            local_fallback_completion_receipts_truncated,
            local_fallback_completion_conservation,
            gpu_batch_evidence_truncated,
            gpu_window_evidence_truncated,
            gpu_fault_recovery_evidence_truncated,
        }
    }
}

fn coverage_ratio(covered: u64, total: u64) -> Option<f64> {
    (total != 0).then(|| covered.min(total) as f64 / total as f64)
}

#[cfg(test)]
mod tests {
    use super::{
        coverage_ratio, should_sample_packet_latency, RuntimeMetrics,
        LOCAL_FALLBACK_BACKEND_IDENTITY, PACKET_LATENCY_SAMPLE_STRIDE, REMOTE_BACKEND_IDENTITY,
    };
    use std::collections::HashSet;
    use std::time::Duration;

    #[test]
    fn empty_key_flow_set_is_not_automatically_covered() {
        assert_eq!(coverage_ratio(0, 0), None);
    }

    #[test]
    fn key_flow_coverage_is_bounded() {
        assert_eq!(coverage_ratio(3, 4), Some(0.75));
        assert_eq!(coverage_ratio(5, 4), Some(1.0));
    }

    #[test]
    fn packet_latency_sampling_is_deterministic_and_samples_short_runs() {
        assert!(should_sample_packet_latency(1));
        assert!(!should_sample_packet_latency(2));
        assert!(!should_sample_packet_latency(
            PACKET_LATENCY_SAMPLE_STRIDE - 1
        ));
        assert!(should_sample_packet_latency(PACKET_LATENCY_SAMPLE_STRIDE));
        assert!(should_sample_packet_latency(
            PACKET_LATENCY_SAMPLE_STRIDE * 2
        ));
    }

    #[test]
    fn raw_latency_receipts_are_timestamped_and_uniquely_addressable() {
        let metrics = RuntimeMetrics::default();
        metrics.observe_packet_latency(Duration::from_micros(3));
        metrics.observe_feature_event_enqueue_latency(Duration::from_micros(7));
        metrics.observe_budget_cost(40.0, 9.0);
        let report = metrics.report(
            "test".to_string(),
            "test".to_string(),
            "test".to_string(),
            "test".to_string(),
            "test".to_string(),
            "test".to_string(),
            Duration::from_secs(1),
            0,
            0,
            0.0,
            None,
            0,
            "A09".to_string(),
            REMOTE_BACKEND_IDENTITY.to_string(),
            LOCAL_FALLBACK_BACKEND_IDENTITY.to_string(),
            false,
        );

        assert_eq!(report.raw_latency_sample_receipts.len(), 4);
        let ids = report
            .raw_latency_sample_receipts
            .iter()
            .map(|receipt| receipt.source_id.as_str())
            .collect::<HashSet<_>>();
        assert_eq!(ids.len(), 4);
        assert!(report
            .raw_latency_sample_receipts
            .iter()
            .all(|receipt| receipt.observed_epoch_us / 1_000_000 == receipt.window_id));
        assert_eq!(report.raw_latency_sample_receipts_truncated, 0);
    }
}
