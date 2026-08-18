use crate::a09_fallback::VerifiedLocalFallback;
use crate::flow::ScheduledFlow;
use crate::metrics::{GpuBatchEvidence, RuntimeMetrics};
use anyhow::{bail, Context, Result};
use crossbeam_channel::{bounded, Receiver, RecvTimeoutError, Sender, TryRecvError, TrySendError};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

const CIRCUIT_OPEN_DURATION: Duration = Duration::from_millis(200);
const SHUTDOWN_RECOVERY_GRACE: Duration = Duration::from_secs(2);

#[derive(Serialize)]
struct InferenceRequest {
    schema_version: u32,
    request_id: String,
    candidate_id: String,
    feature_encoding: &'static str,
    prediction_encoding: &'static str,
    flows: Vec<DispatchItem>,
}

#[derive(Clone, Debug, Serialize)]
pub struct ExpectedBackendIdentity {
    pub candidate_id: String,
    pub schema_version: u32,
    pub model_sha256: String,
    pub inference_engine: String,
}

impl ExpectedBackendIdentity {
    pub fn validate(&self) -> Result<()> {
        if self.candidate_id.is_empty()
            || self.model_sha256.len() != 64
            || !self
                .model_sha256
                .bytes()
                .all(|value| value.is_ascii_hexdigit())
            || self.inference_engine.is_empty()
        {
            bail!("expected GPU backend identity is incomplete or malformed");
        }
        Ok(())
    }

    pub fn evidence_identity(&self) -> String {
        format!(
            "candidate={};schema={};model_sha256={};engine={}",
            self.candidate_id,
            self.schema_version,
            self.model_sha256.to_ascii_lowercase(),
            self.inference_engine
        )
    }
}

#[derive(Serialize)]
struct HealthRequest {
    op: &'static str,
}

#[derive(Deserialize)]
struct HealthResponse {
    ok: bool,
    schema_version: Option<u32>,
    candidate_id: Option<String>,
    model_sha256: Option<String>,
    inference_engine: Option<String>,
}

#[derive(Deserialize)]
struct InferenceResponse {
    ok: bool,
    schema_version: Option<u32>,
    request_id: Option<String>,
    candidate_id: Option<String>,
    predictions: Option<Vec<serde_json::Value>>,
    error: Option<String>,
}

#[derive(Serialize)]
struct DispatchItem {
    #[serde(flatten)]
    flow: ScheduledFlow,
    #[serde(skip)]
    recovery_attempts: u32,
    #[serde(skip)]
    first_failure_epoch_us: Option<u64>,
}

impl DispatchItem {
    fn new(flow: ScheduledFlow) -> Self {
        Self {
            flow,
            recovery_attempts: 0,
            first_failure_epoch_us: None,
        }
    }

    fn is_key_flow(&self) -> bool {
        self.flow.is_key_flow
    }

    fn is_recovery(&self) -> bool {
        self.recovery_attempts > 0
    }
}

struct InferenceAck {
    scored: u64,
}

pub struct GpuDispatcher {
    key_tx: Option<Sender<ScheduledFlow>>,
    normal_tx: Option<Sender<ScheduledFlow>>,
    worker: Option<JoinHandle<()>>,
    metrics: Arc<RuntimeMetrics>,
    ready: Arc<AtomicBool>,
    kernel_timestamp_verified: bool,
}

impl GpuDispatcher {
    pub fn start(
        endpoint: String,
        batch_size: usize,
        queue_capacity: usize,
        timeout: Duration,
        metrics: Arc<RuntimeMetrics>,
        kernel_timestamp_verified: bool,
        expected_identity: ExpectedBackendIdentity,
    ) -> Result<Self> {
        Self::start_inner(
            endpoint,
            batch_size,
            queue_capacity,
            timeout,
            metrics,
            kernel_timestamp_verified,
            expected_identity,
            None,
        )
    }

    #[allow(clippy::too_many_arguments)]
    pub fn start_with_local_fallback(
        endpoint: String,
        batch_size: usize,
        queue_capacity: usize,
        timeout: Duration,
        metrics: Arc<RuntimeMetrics>,
        kernel_timestamp_verified: bool,
        expected_identity: ExpectedBackendIdentity,
        local_fallback: VerifiedLocalFallback,
    ) -> Result<Self> {
        Self::start_inner(
            endpoint,
            batch_size,
            queue_capacity,
            timeout,
            metrics,
            kernel_timestamp_verified,
            expected_identity,
            Some(Arc::new(local_fallback)),
        )
    }

    #[allow(clippy::too_many_arguments)]
    fn start_inner(
        endpoint: String,
        batch_size: usize,
        queue_capacity: usize,
        timeout: Duration,
        metrics: Arc<RuntimeMetrics>,
        kernel_timestamp_verified: bool,
        expected_identity: ExpectedBackendIdentity,
        local_fallback: Option<Arc<VerifiedLocalFallback>>,
    ) -> Result<Self> {
        expected_identity.validate()?;
        let key_capacity = queue_capacity.max(batch_size);
        let (key_tx, key_rx) = bounded(key_capacity);
        let (normal_tx, normal_rx) = bounded(queue_capacity);
        let worker_metrics = Arc::clone(&metrics);
        let ready = Arc::new(AtomicBool::new(false));
        let worker_ready = Arc::clone(&ready);
        let transport = if let Some(listen) = endpoint.strip_prefix("listen://") {
            let listener = TcpListener::bind(listen)
                .with_context(|| format!("bind reverse GPU listener {listen}"))?;
            listener.set_nonblocking(true)?;
            WorkerTransport::Reverse {
                listener,
                stream: None,
                identity_verified: false,
            }
        } else {
            WorkerTransport::DirectUnsupported { endpoint }
        };
        let worker = thread::spawn(move || {
            run_worker(
                transport,
                batch_size,
                key_capacity,
                timeout,
                key_rx,
                normal_rx,
                worker_metrics,
                worker_ready,
                expected_identity,
                local_fallback,
            )
        });
        Ok(Self {
            key_tx: Some(key_tx),
            normal_tx: Some(normal_tx),
            worker: Some(worker),
            metrics,
            ready,
            kernel_timestamp_verified,
        })
    }

    pub fn wait_ready(&self, timeout: Duration) -> bool {
        let deadline = Instant::now() + timeout;
        while Instant::now() < deadline {
            if self.ready.load(Ordering::Acquire) {
                return true;
            }
            thread::sleep(Duration::from_millis(10));
        }
        self.ready.load(Ordering::Acquire)
    }

    pub fn mark_fault_injection(&self, label: impl Into<String>) -> u64 {
        self.metrics.mark_gpu_fault_injection(label)
    }

    pub fn enqueue(&self, flow: ScheduledFlow) {
        let is_key = flow.is_key_flow;
        let ready_at = flow.ready_at;
        let trigger_timestamp_us = flow.trigger_timestamp_us;
        let sender = if is_key {
            self.key_tx.as_ref()
        } else {
            self.normal_tx.as_ref()
        };
        let Some(sender) = sender else {
            self.metrics.fallback_flows.fetch_add(1, Ordering::Relaxed);
            self.metrics.record_gpu_enqueue_failure(is_key);
            if is_key {
                self.metrics
                    .key_flows_enqueue_failed
                    .fetch_add(1, Ordering::Relaxed);
            }
            return;
        };
        match sender.try_send(flow) {
            Ok(()) => {
                self.metrics
                    .observe_feature_event_enqueue_latency(ready_at.elapsed());
                if self.kernel_timestamp_verified {
                    if let Some(timestamp_us) = trigger_timestamp_us {
                        self.metrics.observe_kernel_to_feature_enqueue(timestamp_us);
                    }
                }
                self.metrics
                    .gpu_flows_enqueued
                    .fetch_add(1, Ordering::Relaxed);
                self.metrics.record_gpu_enqueue(is_key);
                if is_key {
                    self.metrics
                        .key_flows_enqueued
                        .fetch_add(1, Ordering::Relaxed);
                }
            }
            Err(TrySendError::Full(_)) | Err(TrySendError::Disconnected(_)) => {
                self.metrics.gpu_queue_full.fetch_add(1, Ordering::Relaxed);
                self.metrics.fallback_flows.fetch_add(1, Ordering::Relaxed);
                self.metrics.record_gpu_enqueue_failure(is_key);
                if is_key {
                    self.metrics
                        .key_flows_enqueue_failed
                        .fetch_add(1, Ordering::Relaxed);
                }
            }
        }
    }

    pub fn finish(mut self) {
        self.key_tx.take();
        self.normal_tx.take();
        if let Some(worker) = self.worker.take() {
            if worker.join().is_err() {
                self.metrics
                    .gpu_worker_join_failures
                    .fetch_add(1, Ordering::Relaxed);
            }
        }
    }
}

enum WorkerTransport {
    DirectUnsupported {
        endpoint: String,
    },
    Reverse {
        listener: TcpListener,
        stream: Option<TcpStream>,
        identity_verified: bool,
    },
}

impl WorkerTransport {
    fn poll_connection(
        &mut self,
        timeout: Duration,
        ready: &AtomicBool,
        expected: &ExpectedBackendIdentity,
    ) {
        match self {
            // The current direct Python server closes a connection after one
            // request. A health response therefore cannot bind identity to the
            // later inference connection, so readiness is deliberately closed.
            Self::DirectUnsupported { endpoint } => {
                let _ = endpoint;
                ready.store(false, Ordering::Release);
            }
            Self::Reverse {
                listener,
                stream,
                identity_verified,
            } if stream.is_none() => match listener.accept() {
                Ok((accepted, _)) => {
                    if configure_stream(&accepted, timeout).is_ok() {
                        let mut accepted = accepted;
                        match health_stream(&mut accepted, expected) {
                            Ok(()) => {
                                *stream = Some(accepted);
                                *identity_verified = true;
                                ready.store(true, Ordering::Release);
                            }
                            Err(_) => {
                                *identity_verified = false;
                                ready.store(false, Ordering::Release);
                            }
                        }
                    } else {
                        *identity_verified = false;
                        ready.store(false, Ordering::Release);
                    }
                }
                Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {}
                Err(_) => {
                    ready.store(false, Ordering::Release);
                }
            },
            Self::Reverse {
                identity_verified, ..
            } => {
                ready.store(*identity_verified, Ordering::Release);
            }
        }
    }

    fn infer(
        &mut self,
        _timeout: Duration,
        request: &InferenceRequest,
        ready: &AtomicBool,
    ) -> Result<InferenceAck> {
        let result = match self {
            Self::DirectUnsupported { endpoint } => {
                bail!("direct GPU transport is fail-closed because health and inference cannot be bound to one connection: {endpoint}")
            }
            Self::Reverse {
                stream,
                identity_verified,
                ..
            } => {
                if !*identity_verified {
                    bail!("reverse GPU identity handshake is not verified");
                }
                let result = infer_stream(
                    stream
                        .as_mut()
                        .context("reverse GPU worker is not connected")?,
                    request,
                );
                if result.is_err() {
                    *stream = None;
                    *identity_verified = false;
                }
                result
            }
        };
        ready.store(result.is_ok(), Ordering::Release);
        result
    }
}

fn run_worker(
    mut transport: WorkerTransport,
    batch_size: usize,
    recovery_capacity: usize,
    timeout: Duration,
    key_rx: Receiver<ScheduledFlow>,
    normal_rx: Receiver<ScheduledFlow>,
    metrics: Arc<RuntimeMetrics>,
    ready: Arc<AtomicBool>,
    expected_identity: ExpectedBackendIdentity,
    local_fallback: Option<Arc<VerifiedLocalFallback>>,
) {
    let remote_backend_identity = expected_identity.evidence_identity();
    let mut request_id = 0u64;
    let mut circuit_open_until: Option<Instant> = None;
    let mut recovery_queue = VecDeque::<DispatchItem>::with_capacity(recovery_capacity);
    let mut key_closed = false;
    let mut normal_closed = false;
    let mut shutdown_grace_started = None;
    loop {
        transport.poll_connection(timeout, &ready, &expected_identity);
        if key_closed && normal_closed && shutdown_grace_started.is_none() {
            shutdown_grace_started = Some(Instant::now());
        }
        if key_closed && normal_closed && recovery_queue.is_empty() {
            break;
        }
        if shutdown_grace_started
            .is_some_and(|started| started.elapsed() >= SHUTDOWN_RECOVERY_GRACE)
            && !recovery_queue.is_empty()
        {
            let unresolved = recovery_queue.len() as u64;
            metrics
                .key_flows_recovery_pending
                .store(0, Ordering::Relaxed);
            metrics
                .key_flows_terminal_unresolved
                .fetch_add(unresolved, Ordering::Relaxed);
            metrics
                .key_flows_inference_failed
                .fetch_add(unresolved, Ordering::Relaxed);
            record_batch_evidence(
                &metrics,
                request_id,
                "shutdown_recovery_expired",
                "terminal_unresolved",
                unresolved,
                unresolved,
                0,
                0,
                0,
                unresolved,
                None,
                Some("shutdown_recovery_grace_expired"),
                None,
            );
            recovery_queue.clear();
            break;
        }
        let mut batch = Vec::with_capacity(batch_size);
        let circuit_closed = circuit_open_until.is_none_or(|until| Instant::now() >= until);
        if circuit_closed && !recovery_queue.is_empty() {
            while batch.len() < batch_size {
                let Some(flow) = recovery_queue.pop_front() else {
                    break;
                };
                metrics
                    .key_flows_recovery_pending
                    .fetch_sub(1, Ordering::Relaxed);
                metrics
                    .key_flows_recovery_retried
                    .fetch_add(1, Ordering::Relaxed);
                batch.push(flow);
            }
        }
        if batch.is_empty() && !key_closed {
            match key_rx.try_recv() {
                Ok(flow) => batch.push(DispatchItem::new(flow)),
                Err(TryRecvError::Empty) => {}
                Err(TryRecvError::Disconnected) => key_closed = true,
            }
        }
        if batch.is_empty() && !normal_closed {
            match normal_rx.recv_timeout(Duration::from_millis(2)) {
                Ok(flow) => batch.push(DispatchItem::new(flow)),
                Err(RecvTimeoutError::Timeout) => {}
                Err(RecvTimeoutError::Disconnected) => normal_closed = true,
            }
        }
        if batch.is_empty() && normal_closed && !key_closed {
            match key_rx.recv_timeout(Duration::from_millis(2)) {
                Ok(flow) => batch.push(DispatchItem::new(flow)),
                Err(RecvTimeoutError::Timeout) => {}
                Err(RecvTimeoutError::Disconnected) => key_closed = true,
            }
        }
        if batch.is_empty() {
            continue;
        }
        let collect_until = Instant::now() + Duration::from_millis(2);
        while batch.len() < batch_size && Instant::now() < collect_until {
            if !key_closed {
                match key_rx.try_recv() {
                    Ok(flow) => {
                        batch.push(DispatchItem::new(flow));
                        continue;
                    }
                    Err(TryRecvError::Disconnected) => key_closed = true,
                    Err(TryRecvError::Empty) => {}
                }
            }
            if !normal_closed {
                match normal_rx.try_recv() {
                    Ok(flow) => {
                        batch.push(DispatchItem::new(flow));
                        continue;
                    }
                    Err(TryRecvError::Disconnected) => normal_closed = true,
                    Err(TryRecvError::Empty) => {}
                }
            }
            thread::yield_now();
        }
        let key_flow_count = batch.iter().filter(|flow| flow.is_key_flow()).count() as u64;
        let recovery_key_count = batch
            .iter()
            .filter(|flow| flow.is_key_flow() && flow.is_recovery())
            .count() as u64;
        if circuit_open_until.is_some_and(|until| Instant::now() < until) {
            request_id = request_id.saturating_add(1);
            let flow_count = batch.len() as u64;
            let (batch, local_completed) =
                complete_local_key_flows(batch, local_fallback.as_deref(), &metrics, request_id);
            let (cached, unresolved) = cache_key_flows(
                &mut recovery_queue,
                batch,
                recovery_capacity,
                &metrics,
                "circuit_open",
            );
            metrics
                .fallback_flows
                .fetch_add(flow_count, Ordering::Relaxed);
            record_batch_evidence(
                &metrics,
                request_id,
                "circuit_open",
                if local_completed > 0 {
                    "circuit_open_local_completed_or_cached"
                } else {
                    "circuit_open_cached_or_dropped"
                },
                flow_count,
                key_flow_count,
                0,
                0,
                cached,
                unresolved,
                None,
                Some("circuit_open"),
                None,
            );
            continue;
        }
        request_id += 1;
        let flow_count = batch.len() as u64;
        let request = InferenceRequest {
            schema_version: 1,
            request_id: request_id.to_string(),
            candidate_id: expected_identity.candidate_id.clone(),
            feature_encoding: "raw_v1",
            prediction_encoding: "ordered_v1",
            flows: batch,
        };
        let started = Instant::now();
        let infer_result = transport.infer(timeout, &request, &ready);
        let elapsed = started.elapsed();
        match infer_result {
            Ok(ack) if ack.scored == flow_count => {
                metrics.gpu_batches_ok.fetch_add(1, Ordering::Relaxed);
                metrics
                    .gpu_flows_scored
                    .fetch_add(ack.scored, Ordering::Relaxed);
                metrics
                    .key_flows_scored
                    .fetch_add(key_flow_count, Ordering::Relaxed);
                metrics
                    .key_flows_recovery_remote_scored
                    .fetch_add(recovery_key_count, Ordering::Relaxed);
                metrics.observe_gpu_latency(elapsed);
                record_batch_evidence(
                    &metrics,
                    request_id,
                    if recovery_key_count > 0 {
                        "recovery"
                    } else {
                        "live"
                    },
                    "remote_scored",
                    flow_count,
                    key_flow_count,
                    ack.scored,
                    key_flow_count,
                    0,
                    0,
                    Some(elapsed),
                    None,
                    Some(&remote_backend_identity),
                );
                metrics.record_gpu_fault_recovered(&remote_backend_identity);
                for (response_index, item) in request.flows.iter().enumerate() {
                    metrics.record_flow_completion(
                        request_id,
                        response_index as u64,
                        &item.flow,
                        item.recovery_attempts,
                        &remote_backend_identity,
                    );
                }
                circuit_open_until = None;
            }
            Ok(ack) => {
                let failure = format!("prediction_count_mismatch:{}:{flow_count}", ack.scored);
                fail_batch(
                    request,
                    request_id,
                    recovery_capacity,
                    &mut recovery_queue,
                    &metrics,
                    &failure,
                    elapsed,
                    local_fallback.as_deref(),
                );
                circuit_open_until = Some(Instant::now() + CIRCUIT_OPEN_DURATION);
            }
            Err(error) => {
                let failure = format!("{}", error.root_cause());
                fail_batch(
                    request,
                    request_id,
                    recovery_capacity,
                    &mut recovery_queue,
                    &metrics,
                    &failure,
                    elapsed,
                    local_fallback.as_deref(),
                );
                circuit_open_until = Some(Instant::now() + CIRCUIT_OPEN_DURATION);
            }
        }
    }
}

fn cache_key_flows(
    recovery_queue: &mut VecDeque<DispatchItem>,
    items: Vec<DispatchItem>,
    capacity: usize,
    metrics: &RuntimeMetrics,
    failure_code: &str,
) -> (u64, u64) {
    let mut cached = 0u64;
    let mut unresolved = 0u64;
    for mut item in items {
        if !item.is_key_flow() {
            continue;
        }
        if recovery_queue.len() < capacity {
            item.recovery_attempts = item.recovery_attempts.saturating_add(1);
            item.first_failure_epoch_us.get_or_insert_with(epoch_us);
            recovery_queue.push_back(item);
            cached = cached.saturating_add(1);
        } else {
            unresolved = unresolved.saturating_add(1);
        }
    }
    metrics
        .key_flows_recovery_cached
        .fetch_add(cached, Ordering::Relaxed);
    metrics
        .key_flows_recovery_pending
        .fetch_add(cached, Ordering::Relaxed);
    metrics
        .key_flows_terminal_unresolved
        .fetch_add(unresolved, Ordering::Relaxed);
    metrics
        .key_flows_inference_failed
        .fetch_add(unresolved, Ordering::Relaxed);
    metrics.record_gpu_fault_observed(failure_code, cached);
    (cached, unresolved)
}

#[allow(clippy::too_many_arguments)]
fn fail_batch(
    request: InferenceRequest,
    request_id: u64,
    recovery_capacity: usize,
    recovery_queue: &mut VecDeque<DispatchItem>,
    metrics: &RuntimeMetrics,
    failure: &str,
    elapsed: Duration,
    local_fallback: Option<&VerifiedLocalFallback>,
) {
    let flow_count = request.flows.len() as u64;
    let key_flow_count = request
        .flows
        .iter()
        .filter(|flow| flow.is_key_flow())
        .count() as u64;
    let (remaining, local_completed) =
        complete_local_key_flows(request.flows, local_fallback, metrics, request_id);
    let (cached, unresolved) = cache_key_flows(
        recovery_queue,
        remaining,
        recovery_capacity,
        metrics,
        failure,
    );
    if failure.starts_with("GPU backend identity mismatch") {
        metrics
            .gpu_backend_identity_failures
            .fetch_add(1, Ordering::Relaxed);
    }
    metrics.gpu_batches_failed.fetch_add(1, Ordering::Relaxed);
    metrics
        .fallback_flows
        .fetch_add(flow_count, Ordering::Relaxed);
    record_batch_evidence(
        metrics,
        request_id,
        "remote_attempt",
        if local_completed > 0 {
            "failed_local_completed_or_cached"
        } else {
            "failed_cached_or_dropped"
        },
        flow_count,
        key_flow_count,
        0,
        0,
        cached,
        unresolved,
        Some(elapsed),
        Some(failure),
        None,
    );
}

fn complete_local_key_flows(
    items: Vec<DispatchItem>,
    local_fallback: Option<&VerifiedLocalFallback>,
    metrics: &RuntimeMetrics,
    request_id: u64,
) -> (Vec<DispatchItem>, u64) {
    let Some(local_fallback) = local_fallback else {
        return (items, 0);
    };
    let backend_identity = local_fallback.backend_identity();
    let mut remaining = Vec::with_capacity(items.len());
    let mut completed = 0u64;
    for (response_index, item) in items.into_iter().enumerate() {
        if !item.is_key_flow() {
            remaining.push(item);
            continue;
        }
        match local_fallback.predict_raw(&item.flow.features) {
            Ok(prediction) => {
                metrics
                    .key_flows_local_fallback_completed
                    .fetch_add(1, Ordering::Relaxed);
                metrics.record_local_fallback_completion(
                    request_id,
                    response_index as u64,
                    &item.flow,
                    item.recovery_attempts.saturating_add(1),
                    prediction.probability,
                    prediction.label,
                    prediction.node_visits,
                    &backend_identity,
                    local_fallback.quality_receipt_sha256(),
                );
                completed = completed.saturating_add(1);
            }
            Err(_) => remaining.push(item),
        }
    }
    (remaining, completed)
}

#[allow(clippy::too_many_arguments)]
fn record_batch_evidence(
    metrics: &RuntimeMetrics,
    sequence: u64,
    attempt_kind: &str,
    outcome: &str,
    flows: u64,
    key_flows: u64,
    remote_scored: u64,
    key_remote_scored: u64,
    key_cached: u64,
    key_terminal_unresolved: u64,
    round_trip: Option<Duration>,
    failure_code: Option<&str>,
    backend_identity: Option<&str>,
) {
    metrics.record_gpu_batch(GpuBatchEvidence {
        sequence,
        source_id: String::new(),
        event_epoch_us: epoch_us(),
        window_id: 0,
        request_id: (attempt_kind != "circuit_open" && attempt_kind != "shutdown_recovery_expired")
            .then_some(sequence),
        attempt_kind: attempt_kind.to_string(),
        outcome: outcome.to_string(),
        flows,
        key_flows,
        remote_scored,
        key_remote_scored,
        key_cached,
        key_terminal_unresolved,
        round_trip_us: round_trip.map(|value| value.as_secs_f64() * 1_000_000.0),
        failure_code: failure_code.map(str::to_string),
        backend_identity: backend_identity.map(str::to_string),
    });
}

fn epoch_us() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_micros()
        .min(u64::MAX as u128) as u64
}

fn configure_stream(stream: &TcpStream, timeout: Duration) -> Result<()> {
    stream.set_read_timeout(Some(timeout))?;
    stream.set_write_timeout(Some(timeout))?;
    stream.set_nodelay(true)?;
    if !stream.nodelay()? {
        bail!("TCP_NODELAY verification failed");
    }
    Ok(())
}

fn health_stream(stream: &mut TcpStream, expected: &ExpectedBackendIdentity) -> Result<()> {
    serde_json::to_writer(&mut *stream, &HealthRequest { op: "health" })?;
    stream.write_all(b"\n")?;
    stream.flush()?;
    let mut line = String::new();
    BufReader::new(stream.try_clone()?).read_line(&mut line)?;
    let response: HealthResponse = serde_json::from_str(&line)?;
    if !response.ok
        || response.schema_version != Some(expected.schema_version)
        || response.candidate_id.as_deref() != Some(expected.candidate_id.as_str())
        || response.model_sha256.as_deref() != Some(expected.model_sha256.as_str())
        || response.inference_engine.as_deref() != Some(expected.inference_engine.as_str())
    {
        bail!(
            "GPU health identity mismatch: schema={:?} candidate={:?} model={:?} engine={:?}",
            response.schema_version,
            response.candidate_id,
            response.model_sha256,
            response.inference_engine
        );
    }
    Ok(())
}

fn infer_stream(stream: &mut TcpStream, request: &InferenceRequest) -> Result<InferenceAck> {
    serde_json::to_writer(&mut *stream, request)?;
    stream.write_all(b"\n")?;
    stream.flush()?;
    let mut line = String::new();
    BufReader::new(stream.try_clone()?).read_line(&mut line)?;
    let response: InferenceResponse = serde_json::from_str(&line)?;
    if !response.ok {
        bail!(
            "GPU service rejected batch: {}",
            response
                .error
                .unwrap_or_else(|| "unknown error".to_string())
        );
    }
    if response.schema_version != Some(request.schema_version)
        || response.request_id.as_deref() != Some(request.request_id.as_str())
        || response.candidate_id.as_deref() != Some(request.candidate_id.as_str())
    {
        bail!(
            "GPU backend identity mismatch: schema={:?} request_id={:?} candidate={:?}",
            response.schema_version,
            response.request_id,
            response.candidate_id
        );
    }
    Ok(InferenceAck {
        scored: response.predictions.unwrap_or_default().len() as u64,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::sync::atomic::Ordering;

    fn scheduled_key_flow(id: &str) -> ScheduledFlow {
        ScheduledFlow {
            flow_id: id.to_string(),
            is_key_flow: true,
            ready_at: Instant::now(),
            trigger_timestamp_us: None,
            features: vec![0.0; 38],
        }
    }

    fn expected_identity() -> ExpectedBackendIdentity {
        ExpectedBackendIdentity {
            candidate_id: "A09".to_string(),
            schema_version: 1,
            model_sha256: "a".repeat(64),
            inference_engine: "numpy_exact".to_string(),
        }
    }

    #[test]
    fn key_flow_is_cached_then_remote_scored_after_identity_failure() {
        let reservation = TcpListener::bind("127.0.0.1:0").expect("reserve reverse port");
        let endpoint = reservation
            .local_addr()
            .expect("reverse address")
            .to_string();
        drop(reservation);
        let dispatcher = GpuDispatcher::start(
            format!("listen://{endpoint}"),
            1,
            4,
            Duration::from_millis(200),
            Arc::new(RuntimeMetrics::default()),
            false,
            expected_identity(),
        )
        .expect("start dispatcher");
        let server = thread::spawn(move || {
            for attempt in 0..2 {
                let deadline = Instant::now() + Duration::from_secs(3);
                let mut stream = loop {
                    match TcpStream::connect(&endpoint) {
                        Ok(stream) => break stream,
                        Err(_) if Instant::now() < deadline => {
                            thread::sleep(Duration::from_millis(2))
                        }
                        Err(error) => panic!("connect mock reverse GPU: {error}"),
                    }
                };
                let mut line = String::new();
                BufReader::new(stream.try_clone().expect("clone mock stream"))
                    .read_line(&mut line)
                    .expect("read health request");
                assert_eq!(
                    serde_json::from_str::<serde_json::Value>(&line).unwrap()["op"],
                    "health"
                );
                let health = json!({
                    "ok": true,
                    "schema_version": 1,
                    "candidate_id": "A09",
                    "model_sha256": "a".repeat(64),
                    "inference_engine": "numpy_exact"
                });
                serde_json::to_writer(&mut stream, &health).expect("write health response");
                stream.write_all(b"\n").expect("terminate health response");
                stream.flush().expect("flush health response");
                line.clear();
                BufReader::new(stream.try_clone().expect("clone mock stream"))
                    .read_line(&mut line)
                    .expect("read mock inference request");
                let request: serde_json::Value =
                    serde_json::from_str(&line).expect("parse mock request");
                let candidate = if attempt == 0 { "WRONG" } else { "A09" };
                let response = json!({
                    "ok": true,
                    "schema_version": 1,
                    "request_id": request["request_id"],
                    "candidate_id": candidate,
                    "predictions": [0]
                });
                serde_json::to_writer(&mut stream, &response).expect("write mock response");
                stream.write_all(b"\n").expect("terminate mock response");
                stream.flush().expect("flush mock response");
            }
        });

        let metrics = Arc::clone(&dispatcher.metrics);
        metrics.key_flows_total.store(1, Ordering::Relaxed);
        metrics
            .key_flows_base_materialized
            .store(1, Ordering::Relaxed);
        assert!(dispatcher.wait_ready(Duration::from_secs(1)));
        dispatcher.mark_fault_injection("test_identity_failure");
        dispatcher.enqueue(scheduled_key_flow("key-1"));
        dispatcher.finish();
        server.join().expect("join mock GPU");

        let report = metrics.report(
            "test".to_string(),
            "mock".to_string(),
            "none".to_string(),
            "none".to_string(),
            "none".to_string(),
            "none".to_string(),
            Duration::from_secs(1),
            0,
            0,
            0.0,
            None,
            0,
            "A09".to_string(),
            ExpectedBackendIdentity {
                candidate_id: "A09".to_string(),
                schema_version: 1,
                model_sha256: "a".repeat(64),
                inference_engine: "numpy_exact".to_string(),
            }
            .evidence_identity(),
            "none_without_equivalent_a09_model".to_string(),
            false,
        );
        assert_eq!(report.key_flows_enqueued, 1);
        assert_eq!(report.key_flows_recovery_cached, 1);
        assert_eq!(report.key_flows_recovery_retried, 1);
        assert_eq!(report.key_flows_recovery_remote_scored, 1);
        assert_eq!(report.key_flows_scored, 1);
        assert_eq!(report.key_flows_inference_failed, 0);
        assert_eq!(report.key_flows_terminal_unresolved, 0);
        assert_eq!(report.key_flows_recovery_pending, 0);
        assert_eq!(report.gpu_backend_identity_failures, 1);
        assert!(
            report
                .key_flow_conservation
                .eligible_equals_enqueue_outcomes
        );
        assert!(
            report
                .key_flow_conservation
                .enqueued_equals_completion_outcomes
        );
        assert!(!report.local_fallback_quality_qualified);
        assert!(!report.key_flow_quality_qualified);
        assert_eq!(report.gpu_fault_recovery_evidence.len(), 1);
        assert!(report.gpu_fault_recovery_evidence[0]
            .fault_injection_epoch_us
            .is_some());
        assert!(report.gpu_fault_recovery_evidence[0]
            .fault_injection_monotonic_ns
            .is_some());
        assert!(report.gpu_fault_recovery_evidence[0].fault_detected_monotonic_ns > 0);
        assert!(report.gpu_fault_recovery_evidence[0]
            .recovery_monotonic_ns
            .is_some());
        let fault = &report.gpu_fault_recovery_evidence[0];
        assert!(fault.fault_injection_monotonic_ns.unwrap() <= fault.fault_detected_monotonic_ns);
        assert!(fault.fault_detected_monotonic_ns <= fault.recovery_monotonic_ns.unwrap());
        assert!(report.gpu_fault_recovery_evidence[0].recovery_us.is_some());
        assert_eq!(
            report.gpu_fault_recovery_evidence[0]
                .recovered_backend_identity
                .as_deref(),
            Some(
                "candidate=A09;schema=1;model_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;engine=numpy_exact"
            )
        );
        assert_eq!(report.gpu_batch_evidence.len(), 2);
        assert_eq!(report.flow_completion_receipts.len(), 1);
        let completion = &report.flow_completion_receipts[0];
        assert_eq!(completion.flow_id, "key-1");
        assert_eq!(completion.request_id, 2);
        assert_eq!(completion.response_index, 0);
        assert_eq!(completion.recovery_attempts, 1);
        assert!(completion.source_id.starts_with("gpu_flow_completion:2:0:"));
        assert!(
            report
                .flow_completion_conservation
                .remote_scored_equals_receipts_plus_truncated
        );
    }

    #[test]
    fn direct_transport_readiness_is_fail_closed() {
        let mut transport = WorkerTransport::DirectUnsupported {
            endpoint: "127.0.0.1:1".to_string(),
        };
        let ready = AtomicBool::new(true);
        transport.poll_connection(Duration::from_millis(1), &ready, &expected_identity());
        assert!(!ready.load(Ordering::Acquire));
    }

    #[test]
    fn reverse_health_mismatch_never_marks_dispatcher_ready() {
        let reservation = TcpListener::bind("127.0.0.1:0").expect("reserve reverse port");
        let endpoint = reservation
            .local_addr()
            .expect("reverse address")
            .to_string();
        drop(reservation);
        let dispatcher = GpuDispatcher::start(
            format!("listen://{endpoint}"),
            1,
            1,
            Duration::from_millis(50),
            Arc::new(RuntimeMetrics::default()),
            false,
            expected_identity(),
        )
        .expect("start dispatcher");
        let client = thread::spawn(move || {
            let deadline = Instant::now() + Duration::from_secs(2);
            let mut stream = loop {
                match TcpStream::connect(&endpoint) {
                    Ok(stream) => break stream,
                    Err(_) if Instant::now() < deadline => thread::sleep(Duration::from_millis(2)),
                    Err(error) => panic!("connect mock reverse GPU: {error}"),
                }
            };
            let mut line = String::new();
            BufReader::new(stream.try_clone().unwrap())
                .read_line(&mut line)
                .unwrap();
            let bad_health = json!({
                "ok": true,
                "schema_version": 1,
                "candidate_id": "A09",
                "model_sha256": "b".repeat(64),
                "inference_engine": "numpy_exact"
            });
            serde_json::to_writer(&mut stream, &bad_health).unwrap();
            stream.write_all(b"\n").unwrap();
            stream.flush().unwrap();
        });
        assert!(!dispatcher.wait_ready(Duration::from_millis(150)));
        dispatcher.finish();
        client.join().unwrap();
    }

    #[test]
    fn bounded_recovery_cache_exposes_terminal_unresolved_key_flow() {
        let metrics = RuntimeMetrics::default();
        let mut recovery = VecDeque::new();
        let items = vec![
            DispatchItem::new(scheduled_key_flow("key-1")),
            DispatchItem::new(scheduled_key_flow("key-2")),
        ];
        let (cached, unresolved) =
            cache_key_flows(&mut recovery, items, 1, &metrics, "test_capacity");

        assert_eq!(cached, 1);
        assert_eq!(unresolved, 1);
        assert_eq!(recovery.len(), 1);
        assert_eq!(
            metrics.key_flows_recovery_pending.load(Ordering::Relaxed),
            1
        );
        assert_eq!(
            metrics
                .key_flows_terminal_unresolved
                .load(Ordering::Relaxed),
            1
        );
        assert_eq!(
            metrics
                .key_flows_local_fallback_completed
                .load(Ordering::Relaxed),
            0
        );
    }

    #[test]
    fn accepted_reverse_stream_is_configured_with_tcp_nodelay() {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind listener");
        let address = listener.local_addr().expect("listener address");
        let client = thread::spawn(move || TcpStream::connect(address).expect("connect listener"));
        let (accepted, _) = listener.accept().expect("accept connection");
        configure_stream(&accepted, Duration::from_millis(200)).expect("configure stream");

        assert!(accepted.nodelay().expect("read TCP_NODELAY"));
        assert_eq!(
            accepted.read_timeout().expect("read timeout"),
            Some(Duration::from_millis(200))
        );
        assert_eq!(
            accepted.write_timeout().expect("write timeout"),
            Some(Duration::from_millis(200))
        );
        client.join().expect("join client");
    }
}
