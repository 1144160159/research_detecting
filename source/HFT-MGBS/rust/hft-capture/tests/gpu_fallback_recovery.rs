use hft_capture::flow::ScheduledFlow;
use hft_capture::gpu::{ExpectedBackendIdentity, GpuDispatcher};
use hft_capture::metrics::{RuntimeMetrics, REMOTE_BACKEND_IDENTITY};
use serde_json::json;
use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::atomic::Ordering;
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

fn key_flow() -> ScheduledFlow {
    ScheduledFlow {
        flow_id: "integration-key".to_string(),
        is_key_flow: true,
        ready_at: Instant::now(),
        trigger_timestamp_us: None,
        features: vec![0.0; 38],
    }
}

#[test]
fn recovery_contract_requires_verified_remote_score_and_preserves_conservation() {
    let reservation = TcpListener::bind("127.0.0.1:0").expect("reserve mock GPU port");
    let endpoint = reservation.local_addr().expect("mock address").to_string();
    drop(reservation);
    let metrics = Arc::new(RuntimeMetrics::default());
    metrics.key_flows_total.store(1, Ordering::Relaxed);
    metrics
        .key_flows_base_materialized
        .store(1, Ordering::Relaxed);
    let dispatcher = GpuDispatcher::start(
        format!("listen://{endpoint}"),
        1,
        4,
        Duration::from_millis(200),
        Arc::clone(&metrics),
        false,
        ExpectedBackendIdentity {
            candidate_id: "A09".to_string(),
            schema_version: 1,
            model_sha256: "a".repeat(64),
            inference_engine: "numpy_exact".to_string(),
        },
    )
    .expect("start dispatcher");
    let server = thread::spawn(move || {
        for attempt in 0..2 {
            let deadline = Instant::now() + Duration::from_secs(3);
            let mut stream = loop {
                match TcpStream::connect(&endpoint) {
                    Ok(stream) => break stream,
                    Err(_) if Instant::now() < deadline => thread::sleep(Duration::from_millis(2)),
                    Err(error) => panic!("connect mock reverse GPU: {error}"),
                }
            };
            let mut line = String::new();
            BufReader::new(stream.try_clone().expect("clone mock stream"))
                .read_line(&mut line)
                .expect("read health");
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
            serde_json::to_writer(&mut stream, &health).expect("write health");
            stream.write_all(b"\n").expect("terminate health");
            stream.flush().expect("flush health");
            line.clear();
            BufReader::new(stream.try_clone().expect("clone mock stream"))
                .read_line(&mut line)
                .expect("read request");
            let request: serde_json::Value = serde_json::from_str(&line).expect("parse request");
            let response = json!({
                "ok": true,
                "schema_version": 1,
                "request_id": request["request_id"],
                "candidate_id": if attempt == 0 { "not-A09" } else { "A09" },
                "predictions": [0]
            });
            serde_json::to_writer(&mut stream, &response).expect("write response");
            stream.write_all(b"\n").expect("terminate response");
            stream.flush().expect("flush response");
        }
    });

    assert!(dispatcher.wait_ready(Duration::from_secs(1)));
    dispatcher.mark_fault_injection("integration_identity_fault");
    dispatcher.enqueue(key_flow());
    dispatcher.finish();
    server.join().expect("join mock GPU");

    let report = metrics.report(
        "integration_test".to_string(),
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
        REMOTE_BACKEND_IDENTITY.to_string(),
        "none_without_equivalent_a09_model".to_string(),
        false,
    );
    assert_eq!(report.remote_backend_identity, REMOTE_BACKEND_IDENTITY);
    assert_eq!(
        report.local_fallback_backend_identity,
        "none_without_equivalent_a09_model"
    );
    assert_eq!(report.key_flows_enqueued, 1);
    assert_eq!(report.key_flows_scored, 1);
    assert_eq!(report.key_flows_inference_failed, 0);
    assert_eq!(report.key_flows_recovery_remote_scored, 1);
    assert_eq!(report.key_flows_local_fallback_completed, 0);
    assert_eq!(report.key_flows_terminal_unresolved, 0);
    assert_eq!(report.key_flows_recovery_pending, 0);
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
    assert_eq!(report.gpu_backend_identity_failures, 1);
    assert_eq!(report.gpu_batches_failed, 1);
    assert_eq!(report.flow_completion_receipts.len(), 1);
    assert!(
        report
            .flow_completion_conservation
            .remote_scored_equals_receipts_plus_truncated
    );
    assert_eq!(report.gpu_batches_ok, 1);
    assert_eq!(report.gpu_fault_recovery_evidence.len(), 1);
    assert!(report.gpu_fault_recovery_evidence[0]
        .fault_injection_epoch_us
        .is_some());
    assert!(report.gpu_fault_recovery_evidence[0].recovery_us.is_some());
    assert_eq!(report.gpu_batch_evidence.len(), 2);
    assert_ne!(
        report.gpu_batch_evidence[0].source_id,
        report.gpu_batch_evidence[1].source_id
    );
    assert!(report
        .gpu_batch_evidence
        .iter()
        .all(|batch| batch.window_id == batch.event_epoch_us / 1_000_000));
    assert!(!report.gpu_window_evidence.is_empty());
    assert!(report
        .gpu_window_evidence
        .iter()
        .all(|window| !window.window_source_id.is_empty()));
}
