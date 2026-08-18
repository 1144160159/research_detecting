from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from current_hardware_279_v2_evidence import (  # noqa: E402
    CollectorError,
    _ClockProbeServer,
    _cross_node_clock_probe,
    _live_service_artifacts,
    _validate_fallback,
    cross_node_clock_probe_gaps,
    finalize_evidence,
    normalize_windows,
    normalize_resource_samples,
    prepare_evidence,
    validate_collection_receipt,
    validate_quality_evidence,
)
from compose_current_hardware_279_raw_run_v2 import bind_runner_evidence  # noqa: E402


CONFIG = ROOT / "configs" / "current_hardware_2_79_evidence_collector_v1.json"


def dump(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurrentHardware279EvidenceCollectorTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.model = self.root / "a09.joblib"
        self.service = self.root / "gpu_service.py"
        self.engine = self.root / "engine.py"
        self.launcher = self.root / "start.sh"
        self.official_label_source = self.root / "official-label-source.jsonl"
        for path, payload in (
            (self.model, b"model"),
            (self.service, b"service"),
            (self.engine, b"engine"),
            (self.launcher, b"launcher"),
        ):
            path.write_bytes(payload)
        self.official_label_source.write_bytes(b'{"sample_id":"s1","label":1}\n')
        self.runtime = dump(
            self.root / "runtime.json",
            {
                "schema_version": 2,
                "scope": "selected_runtime_inline_cpu6",
                "candidate_id": "A09",
                "pid": 101,
                "process_start_ticks": 9001,
                "python_executable": "/python",
                "working_directory": "/hft",
                "command_sha256": "c" * 64,
                "bind": "0.0.0.0:50051",
                "connect": "10.0.5.8:50052",
                "inference_engine": "numpy_exact",
                "model_sha256": digest(self.model),
                "service_source_sha256": digest(self.service),
                "numpy_engine_source_sha256": digest(self.engine),
                "launcher_sha256": digest(self.launcher),
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def prepare(self):
        return prepare_evidence(
            config_path=CONFIG,
            output_dir=self.root / "prepared",
            campaign_id="campaign",
            candidate_id="candidate",
            backend="tpacket_v3",
            mode="normal",
            repeat_index=1,
            runtime_manifest=self.runtime,
            model=self.model,
            service_source=self.service,
            engine_source=self.engine,
            service_launcher=self.launcher,
        )

    def test_prepare_copies_and_hash_binds_runtime_artifacts(self):
        receipt = self.prepare()
        self.assertEqual(receipt["gaps"], [])
        self.assertEqual(receipt["artifact_sha256"]["model"], digest(self.model))
        for name in ("model", "runtime_manifest", "service_source", "engine_source", "service_launcher"):
            frozen = self.root / "prepared" / receipt["artifacts"][name]["path"]
            self.assertTrue(frozen.is_file())
            self.assertFalse(frozen.is_symlink())
            self.assertEqual(receipt["artifacts"][name]["sha256"], digest(frozen))

    def test_prepare_rejects_runtime_hash_drift(self):
        self.engine.write_bytes(b"drift")
        with self.assertRaisesRegex(CollectorError, "engine_source"):
            self.prepare()

    def test_live_service_artifacts_are_hashed_from_process_argv_and_pythonpath(self):
        package = self.root / "live" / "hft_mgbs"
        package.mkdir(parents=True)
        service = package / "gpu_service.py"
        engine = package / "a09_numpy_inference.py"
        service.write_bytes(b"live-service")
        engine.write_bytes(b"live-engine")
        process = {
            "argv": [
                sys.executable,
                "-m",
                "hft_mgbs.gpu_service",
                "--model",
                str(self.model),
            ],
            "cwd": str(self.root),
            "exe": sys.executable,
            "python_path": str(self.root / "live"),
        }
        health = {
            "response": {
                "ok": True,
                "model_bundle": str(self.model),
                "model_sha256": digest(self.model),
                "inference_engine": "numpy_exact",
            }
        }

        identity, gaps = _live_service_artifacts(process, "numpy_exact", health)

        self.assertEqual(gaps, [])
        self.assertEqual(identity["sha256"]["model"], digest(self.model))
        self.assertEqual(identity["sha256"]["service_source"], digest(service))
        self.assertEqual(identity["sha256"]["engine_source"], digest(engine))
        self.assertTrue(identity["health_model_path_matches"])

    def test_resource_normalization_requires_gpu_process_attribution(self):
        raw = {
            "node_role": "service",
            "samples": [
                {
                    "boundary_epoch_second": 100,
                    "observed_epoch_ns": 100_000_000_000,
                    "sample_finished_epoch_ns": 100_010_000_000,
                    "host_cpu": [100, 0, 100, 700, 0, 0, 100, 0],
                    "memory_total_bytes": 1000,
                    "memory_available_bytes": 600,
                    "service": {"pid": 7, "start_ticks": 9, "cpu_ticks": 10, "rss_bytes": 100},
                    "nvidia": {"query_ok": True, "gpu_memory_total_bytes": 1000, "gpu_fraction": 0.5, "compute_apps": []},
                },
                {
                    "boundary_epoch_second": 101,
                    "observed_epoch_ns": 101_000_000_000,
                    "sample_finished_epoch_ns": 101_010_000_000,
                    "host_cpu": [110, 0, 110, 780, 0, 0, 100, 0],
                    "memory_total_bytes": 1000,
                    "memory_available_bytes": 500,
                    "service": {"pid": 7, "start_ticks": 9, "cpu_ticks": 20, "rss_bytes": 120},
                    "nvidia": {"query_ok": True, "gpu_memory_total_bytes": 1000, "gpu_fraction": 0.6, "compute_apps": []},
                },
            ],
            "clock_ticks_per_second": 100,
            "host_cpu_count": 10,
            "runtime_inference_engine": "numpy_exact",
        }
        rows, gaps = normalize_resource_samples(raw, [100], 250_000_000)
        self.assertEqual(gaps, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["gpu_fraction"], 0.0)
        self.assertEqual(rows[0]["gpu_memory_fraction"], 0.0)
        self.assertFalse(rows[0]["service_gpu_process_present"])
        raw["samples"][1]["nvidia"]["query_ok"] = False
        rows, gaps = normalize_resource_samples(raw, [100], 250_000_000)
        self.assertEqual(rows, [])
        self.assertIn("resources.service.epoch.100.gpu_attribution", gaps)

    def test_collection_receipts_fail_closed_on_error_or_missing_clock_proof(self):
        config_sha = digest(CONFIG)
        raw = {
            "schema_version": 1,
            "scope": "hft_mgbs_current_hardware_2_79_node_raw_boundaries_v1",
            "read_only": True,
            "service_started_or_stopped": False,
            "traffic_started_or_stopped": False,
            "node_role": "physical",
            "collector_config_sha256": config_sha,
            "samples": [{}, {}],
            "errors": ["nic_missing"],
            "clock_sync_observations": [],
        }
        gaps = validate_collection_receipt(raw, "physical", config_sha, 50_000_000)
        self.assertIn("collection.physical.errors_present", gaps)
        self.assertIn("collection.physical.clock_sync_missing", gaps)

    def test_cross_node_clock_probe_produces_bounded_nonce_receipts(self):
        server = _ClockProbeServer("127.0.0.1", 0)
        probe = _cross_node_clock_probe("127.0.0.1", int(server.address[1]), attempts=2)
        server_receipt = server.finish()
        physical = {"cross_node_clock_probe_observations": [probe, probe], "clock_probe_server": None}
        service = {"cross_node_clock_probe_observations": [], "clock_probe_server": server_receipt}

        gaps = cross_node_clock_probe_gaps(physical, service, 250_000_000)

        self.assertEqual(gaps, [])
        self.assertEqual(len(probe["observations"]), 2)
        self.assertGreaterEqual(server_receipt["queries_served"], 2)

    def test_quality_is_only_copied_when_independent_and_hash_bound(self):
        prepared = self.prepare()
        prepared_path = self.root / "prepared" / "prepare_receipt.json"
        labels = dump(
            self.root / "labels.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_independent_ground_truth_labels_v1",
                "source_kind": "official_labels",
                "synthetic": False,
                "independent_holdout": True,
                "source_artifact_path": str(self.official_label_source),
                "source_artifact_sha256": digest(self.official_label_source),
                "source_record_locator": "official:test-partition",
                "records": [{"sample_id": "s1", "label": 1, "group": "g", "event_id": "e"}],
            },
        )
        predictions = dump(
            self.root / "predictions.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_independent_predictions_v1",
                "synthetic": False,
                "generation_kind": "frozen_model_inference_on_independent_holdout",
                "source_artifact_sha256": digest(self.official_label_source),
                "labels_sha256": digest(labels),
                "model_sha256": prepared["artifact_sha256"]["model"],
                "runtime_manifest_sha256": prepared["artifact_sha256"]["runtime_manifest"],
                "records": [{"sample_id": "s1", "prediction": 1, "score": 0.9}],
            },
        )
        gaps = validate_quality_evidence(labels, predictions, prepared_path)
        self.assertEqual(gaps, [])
        value = json.loads(labels.read_text())
        value["synthetic"] = True
        dump(labels, value)
        gaps = validate_quality_evidence(labels, predictions, prepared_path)
        self.assertIn("quality.labels.not_independent_nonsynthetic", gaps)

    def test_schema2_portable_source_rejects_duplicate_relations(self):
        prepared = self.prepare()
        prepared_path = self.root / "prepared" / "prepare_receipt.json"
        source = dump(
            self.root / "portable-source.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_unsw_official_quality_source_v1",
                "source_kind": "official_unsw_ground_truth_and_frozen_pcap_inputs",
                "synthetic": False,
                "portable": True,
                "embedded_input_hash_manifest": {"schema_version": 1},
                "eligible_events": [{"event_id": "e", "eligible_groups": ["g"]}],
                "sample_event_relations": [
                    {"sample_id": "s", "group": "g", "event_id": "e"},
                    {"sample_id": "s", "group": "g", "event_id": "e"},
                ],
            },
        )
        portable_prepare = self.root / "trusted-prepare-v2.json"
        portable_prepare.write_bytes(prepared_path.read_bytes())
        labels = dump(
            self.root / "labels-v2.json",
            {
                "schema_version": 2,
                "scope": "hft_mgbs_independent_ground_truth_labels_v2",
                "source_kind": "official_labels",
                "synthetic": False,
                "independent_holdout": True,
                "source_artifact_path": source.name,
                "source_artifact_sha256": digest(source),
                "source_record_locator": "official",
                "prepare_receipt_path": portable_prepare.name,
                "prepare_receipt_sha256": digest(prepared_path),
                "records": [{"sample_id": "s", "label": 1, "group": "g"}],
                "eligible_events": [{"event_id": "e", "eligible_groups": ["g"]}],
                "sample_event_relations": [
                    {"sample_id": "s", "group": "g", "event_id": "e"},
                    {"sample_id": "s", "group": "g", "event_id": "e"},
                ],
            },
        )
        predictions = dump(
            self.root / "pred-v2.json",
            {
                "schema_version": 2,
                "scope": "hft_mgbs_independent_predictions_v2",
                "synthetic": False,
                "generation_kind": "frozen_model_inference_on_independent_holdout",
                "source_artifact_sha256": digest(source),
                "labels_sha256": digest(labels),
                "model_sha256": prepared["artifact_sha256"]["model"],
                "runtime_manifest_sha256": prepared["artifact_sha256"]["runtime_manifest"],
                "prepare_receipt_sha256": digest(prepared_path),
                "records": [{"sample_id": "s", "prediction": 1, "score": 0.9}],
            },
        )
        gaps = validate_quality_evidence(labels, predictions, prepared_path)
        self.assertIn("quality.labels.event_relations", gaps)

    def test_remote_retry_cannot_be_presented_as_local_fallback_completion(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        steps = config["fallback_required_steps"]
        events = []
        for index, step in enumerate(steps):
            row = {"step": step, "monotonic_ns": 1_000_000 + index * 1000}
            if step == "fault_injection_observed":
                row.update({"source": "external_fault_injector", "injection_receipt_sha256": "f" * 64})
            elif step == "local_fallback_activated":
                row.update({"backend_identity": "remote_retry", "quality_qualified": False})
            elif step == "post_switch_traffic_observed":
                row.update({"local_completed_delta": 0, "remote_scored_delta": 1})
            elif step == "primary_recovered":
                row["backend_identity"] = "A09/schema_v1/ordered_v1"
            elif step == "final_state_verification":
                row.update({"key_flows_outstanding": 0, "key_flows_terminal_unresolved": 0})
            events.append(row)
        path = dump(
            self.root / "fallback.json",
            {
                "schema_version": 2,
                "scope": "hft_mgbs_current_hardware_2_79_fallback_events_v2",
                "run_id": "run",
                "events": events,
            },
        )

        gaps = _validate_fallback(path, "run", config)

        self.assertEqual(gaps, ["fallback_events.not_verified_local_completion"])

    def test_finalize_old_aggregate_run_emits_gaps_and_no_window_artifact(self):
        run = self.root / "old-run"
        run.mkdir()
        dump(
            run / "pipeline_raw.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw",
                "epoch_second_counts": {"100": 2_800_000, "101": 2_800_000},
                "pipeline_metrics": {
                    "packet_processing_latency": {"samples": 1000, "p99_us": 10.0},
                    "gpu_batch_round_trip_latency": {"samples": 100, "p99_us": 1000.0},
                },
            },
        )
        result = finalize_evidence(
            config_path=CONFIG,
            output_dir=self.root / "finalized",
            evidence_dir=run,
            campaign_id="campaign",
            candidate_id="candidate",
            backend="tpacket_v3",
            mode="normal",
            repeat_index=1,
        )
        self.assertFalse(result["adapter_ready"])
        self.assertEqual(len(result["evidence_gaps"]), 11)
        self.assertIn("missing:window_observations", result["evidence_gaps"])
        self.assertIn("windows.raw_latency_receipts_missing", result["normalization_gaps"])
        self.assertIn("windows.timestamped_internal_counters_missing", result["normalization_gaps"])
        self.assertFalse((self.root / "finalized" / "window_observations_v2.json").exists())

    def test_145_flow_samples_are_reported_as_gaps_not_expanded(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        base = 1_900_000_000
        internal_names = config["internal_counters"]

        def counters(multiplier):
            values = {name: 0 for name in internal_names}
            values.update(
                {
                    "packets_received": multiplier * 2_800_000,
                    "packets_parsed": multiplier * 2_800_000,
                    "flows_emitted": multiplier * 145,
                    "feature_submitted": multiplier * 145,
                    "gpu_flows_enqueued": multiplier * 145,
                    "gpu_flows_scored": multiplier * 145,
                    "gpu_batches_ok": multiplier * 100,
                    "key_flows_total": multiplier * 145,
                    "key_flows_enqueued": multiplier * 145,
                    "key_flows_scored": multiplier * 145,
                }
            )
            return values

        receipts = []
        sequence = 0
        for metric, count in (
            ("packet_processing", 1000),
            ("flow_materialization_to_feature_enqueue", 145),
            ("kernel_receive_to_feature_enqueue", 145),
            ("kernel_receive_to_remote_completion", 145),
            ("gpu_batch_round_trip", 100),
        ):
            for _ in range(count):
                sequence += 1
                receipts.append(
                    {
                        "source_id": "observed-{}".format(sequence),
                        "metric": metric,
                        "observed_epoch_us": base * 1_000_000 + sequence,
                        "observed_monotonic_us": sequence,
                        "window_id": base,
                        "source_event_epoch_us": base * 1_000_000,
                        "value_us": 1.0,
                    }
                )
        pipeline = {
            "epoch_second_counts": {str(base): 2_800_000},
            "pipeline_metrics": {
                "counter_observations": [
                    {"boundary_epoch_second": base, "counters": counters(0)},
                    {"boundary_epoch_second": base + 1, "counters": counters(1)},
                ],
                "raw_latency_sample_receipts": receipts,
                "raw_latency_sample_receipts_truncated": 0,
            },
        }
        physical = {
            "samples": [
                {
                    "boundary_epoch_second": base + offset,
                    "external_counters": {
                        "pktgen_offered": offset * 2_800_000,
                        "nic_rx_ucast": offset * 2_800_000,
                        "nic_rx_discards": 0,
                    },
                }
                for offset in (0, 1)
            ]
        }

        payload, gaps = normalize_windows(pipeline, physical, config, "run", "generator")

        self.assertIsNone(payload)
        self.assertIn("windows.epoch.{}.flow_latency_us.sample_count".format(base), gaps)
        self.assertIn("windows.epoch.{}.kernel_to_feature_latency_us.sample_count".format(base), gaps)
        self.assertIn("windows.epoch.{}.end_to_end_latency_us.sample_count".format(base), gaps)
        self.assertNotIn("windows.epoch.{}.packet_latency_us.sample_count".format(base), gaps)
        self.assertNotIn("windows.epoch.{}.gpu_batch_latency_us.sample_count".format(base), gaps)

    def test_complete_raw_evidence_is_consumable_by_existing_adapter(self):
        prepared = self.prepare()
        run = self.root / "run"
        (run / "frozen").mkdir(parents=True)
        for name, payload in (
            ("runner.sh", b"runner\n"),
            ("config.json", b"{}\n"),
            ("tpacket_v3_full_pipeline", b"binary\n"),
        ):
            (run / "frozen" / name).write_bytes(payload)
        base = 1_900_000_000
        internal_names = json.loads(CONFIG.read_text())["internal_counters"]

        def counters(multiplier):
            packet = 2_800_000 * multiplier
            flow = 1000 * multiplier
            batch = 100 * multiplier
            values = {
                "socket_drops": 0,
                "sequence_gaps": 0,
                "packets_received": packet,
                "packets_parsed": packet,
                "parse_rejected": 0,
                "flows_emitted": flow,
                "feature_submitted": flow,
                "feature_drops": 0,
                "gpu_flows_enqueued": flow,
                "gpu_flows_scored": flow,
                "gpu_flows_failed": 0,
                "gpu_outstanding": 0,
                "gpu_batches_ok": batch,
                "gpu_batches_failed": 0,
                "gpu_queue_full": 0,
                "key_flows_total": flow,
                "key_flows_enqueued": flow,
                "key_flows_enqueue_failed": 0,
                "key_flows_scored": flow,
                "key_flows_inference_failed": 0,
                "key_flows_local_fallback_completed": 0,
                "key_flows_terminal_failed": 0,
                "key_flows_outstanding": 0,
                "key_flows_skipped_due_budget": 0,
                "budget_overrun_count": 0,
            }
            self.assertEqual(set(values), set(internal_names))
            return values

        receipts = []
        sequence = 0
        source_metrics = (
            ("packet_processing", 1000, 10.0),
            ("flow_materialization_to_feature_enqueue", 1000, 100.0),
            ("kernel_receive_to_feature_enqueue", 1000, 200.0),
            ("kernel_receive_to_remote_completion", 1000, 500.0),
            ("gpu_batch_round_trip", 100, 1000.0),
        )
        for window in range(15):
            epoch = base + window
            for metric, count, value in source_metrics:
                for _ in range(count):
                    sequence += 1
                    receipts.append(
                        {
                            "source_id": "raw-{}".format(sequence),
                            "metric": metric,
                            "observed_epoch_us": epoch * 1_000_000 + sequence % 900_000,
                            "observed_monotonic_us": sequence,
                            "window_id": epoch,
                            "source_event_epoch_us": epoch * 1_000_000,
                            "value_us": value,
                        }
                    )
        pipeline_metrics = {
            "gpu_flows_enqueued": 15_000,
            "gpu_flows_scored": 15_000,
            "gpu_batches_ok": 1_500,
            "gpu_batches_failed": 0,
            "gpu_queue_full": 0,
            "key_flows_total": 15_000,
            "key_flows_enqueued": 15_000,
            "key_flows_enqueue_failed": 0,
            "key_flows_scored": 15_000,
            "key_flows_inference_failed": 0,
            "key_flows_local_fallback_completed": 0,
            "budget_overrun_count": 0,
            "counter_observations": [
                {"boundary_epoch_second": base + index, "counters": counters(index)}
                for index in range(16)
            ],
            "raw_latency_sample_receipts": receipts,
            "raw_latency_sample_receipts_truncated": 0,
        }
        dump(
            run / "pipeline_raw.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw",
                "backend": "tpacket_v3_packet_fanout_borrowed",
                "gpu_ready_at_start": True,
                "all_workers_error_free": True,
                "internal_delivery_lossless": True,
                "packets": 42_000_000,
                "packets_parsed": 42_000_000,
                "parse_rejected": 0,
                "flows_closed": 15_000,
                "feature_queue_submitted": 15_000,
                "feature_queue_drops": 0,
                "epoch_second_counts": {str(base + index): 2_800_000 for index in range(15)},
                "scheduler": {"fatal_error": None},
                "shutdown": {
                    "capture_workers_joined": 8,
                    "capture_workers_expected": 8,
                    "scheduler_thread_joined": True,
                    "scheduler_input_channel_drained": True,
                    "dispatcher_finish_called": True,
                },
                "pipeline_metrics": pipeline_metrics,
                "full_pipeline_qualified": False,
                "final_pareto_ingestion_allowed": False,
            },
        )
        dump(run / "diagnostic_receipt.json", {"runner_exit_status": 0, "restoration_verified": True})
        dump(run / "pipeline_ready.json", {"ready": True, "gpu_ready_at_start": True})
        (run / "execution_events.tsv").write_text(
            "utc\tevent\n"
            "2026-08-13T00:00:00Z\tpipeline_spawned\n"
            "2026-08-13T00:00:01Z\tgpu_reverse_ready\n"
            "2026-08-13T00:00:02Z\tgenerator_started\n"
            "2026-08-13T00:00:20Z\tgenerator_stopped\n"
            "2026-08-13T00:00:21Z\tpipeline_completed\n",
            encoding="utf-8",
        )
        (run / "before_ens8f0_statistics.txt").write_text(
            "     rx_ucast_packets: 100\n     rx_discards: 0\n", encoding="utf-8"
        )
        (run / "pre_restore_ens8f0_statistics.txt").write_text(
            "     rx_ucast_packets: 42000100\n     rx_discards: 0\n", encoding="utf-8"
        )
        (run / "pktgen_device_0.txt").write_text(
            "Result: OK: 19000000(c1+d1) usec, 42000000 (64byte,0frags)\n", encoding="utf-8"
        )
        physical_samples = []
        service_samples = []
        for index in range(16):
            epoch = base + index
            physical_samples.append(
                {
                    "boundary_epoch_second": epoch,
                    "observed_epoch_ns": epoch * 1_000_000_000,
                    "sample_finished_epoch_ns": epoch * 1_000_000_000 + 10_000_000,
                    "host_cpu": [100 + index * 10, 0, 100 + index * 10, 700 + index * 80, 0, 0, 100, 0],
                    "memory_total_bytes": 10_000,
                    "memory_available_bytes": 6_000,
                    "external_counters": {
                        "pktgen_offered": index * 2_800_000,
                        "nic_rx_ucast": 100 + index * 2_800_000,
                        "nic_rx_discards": 0,
                    },
                }
            )
            service_samples.append(
                {
                    "boundary_epoch_second": epoch,
                    "observed_epoch_ns": epoch * 1_000_000_000,
                    "sample_finished_epoch_ns": epoch * 1_000_000_000 + 10_000_000,
                    "host_cpu": [100 + index * 10, 0, 100 + index * 10, 700 + index * 80, 0, 0, 100, 0],
                    "memory_total_bytes": 10_000,
                    "memory_available_bytes": 6_000,
                    "service": {
                        "pid": 101,
                        "start_ticks": 9001,
                        "pids": [101],
                        "cpu_ticks": 100 + index * 10,
                        "rss_bytes": 1000,
                    },
                    "nvidia": {
                        "query_ok": True,
                        "gpu_fraction": 0.7,
                        "gpu_memory_total_bytes": 10_000,
                        "compute_apps": [],
                    },
                }
            )
        physical = dump(
            self.root / "physical-raw.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_current_hardware_2_79_node_raw_boundaries_v1",
                "node_role": "physical",
                "clock_ticks_per_second": 100,
                "host_cpu_count": 10,
                "hardware_identity_material": {"boot_id": "boot"},
                "hardware_identity_sha256": "a" * 64,
                "collector_config_sha256": digest(CONFIG),
                "read_only": True,
                "service_started_or_stopped": False,
                "traffic_started_or_stopped": False,
                "errors": [],
                "clock_sync_observations": [
                    {
                        "query_ok": True,
                        "synchronized": True,
                        "source": "chronyc_tracking",
                        "absolute_clock_offset_ns": 100_000,
                    },
                    {
                        "query_ok": True,
                        "synchronized": True,
                        "source": "chronyc_tracking",
                        "absolute_clock_offset_ns": 100_000,
                    },
                ],
                "cross_node_clock_probe_observations": [
                    {
                        "query_ok": True,
                        "best_observation": {
                            "offset_interval_low_ns": -1_000_000,
                            "offset_interval_high_ns": 1_000_000,
                            "maximum_absolute_offset_bound_ns": 1_000_000,
                        },
                    },
                    {
                        "query_ok": True,
                        "best_observation": {
                            "offset_interval_low_ns": -1_000_000,
                            "offset_interval_high_ns": 1_000_000,
                            "maximum_absolute_offset_bound_ns": 1_000_000,
                        },
                    },
                ],
                "pipeline_process_identity": {"pid": 201, "start_ticks": 7001, "exe": "/capture"},
                "generator_process_identities": [{"pid": 301, "start_ticks": 8001, "exe": "kpktgend"}],
                "physical_network_identity": {
                    "gpu_health": {
                        "query_ok": True,
                        "response": {
                            "ok": True,
                            "candidate_id": "A09",
                            "service_counters": {"failures": 0},
                        },
                    },
                    "reverse_socket": {
                        "query_ok": True,
                        "listener": {"query_ok": True, "owner_pids": [201]},
                        "established": True,
                        "established_owner_pids": [201],
                    },
                },
                "samples": physical_samples,
            },
        )
        service_raw = dump(
            self.root / "service-raw.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_current_hardware_2_79_node_raw_boundaries_v1",
                "node_role": "service",
                "clock_ticks_per_second": 100,
                "host_cpu_count": 10,
                "runtime_inference_engine": "numpy_exact",
                "collector_config_sha256": digest(CONFIG),
                "read_only": True,
                "service_started_or_stopped": False,
                "traffic_started_or_stopped": False,
                "errors": [],
                "clock_sync_observations": [
                    {"query_ok": False},
                    {"query_ok": False},
                ],
                "clock_probe_server": {
                    "stopped": True,
                    "errors": [],
                    "queries_served": 10,
                },
                "service_runtime_identity": {
                    "manifest_actual_sha256": prepared["artifact_sha256"]["runtime_manifest"],
                    "manifest_declared_pid": 101,
                    "process": {
                        "pid": 101,
                        "start_ticks": 9001,
                        "exe": "/python",
                        "cwd": "/hft",
                        "cmdline_sha256": "c" * 64,
                    },
                    "live_artifacts": {
                        "resolved_paths": {},
                        "sha256": {
                            "model": prepared["artifact_sha256"]["model"],
                            "service_source": prepared["artifact_sha256"]["service_source"],
                            "engine_source": prepared["artifact_sha256"]["engine_source"],
                            "python_executable": "d" * 64,
                        },
                        "health_model_path_matches": True,
                        "health_model_sha256": prepared["artifact_sha256"]["model"],
                        "health_inference_engine": "numpy_exact",
                    },
                    "listener_50051": {"query_ok": True, "owner_pids": [101]},
                    "localhost_health": {
                        "query_ok": True,
                        "response": {
                            "ok": True,
                            "candidate_id": "A09",
                            "model_sha256": prepared["artifact_sha256"]["model"],
                            "inference_engine": "numpy_exact",
                            "service_counters": {"failures": 0},
                        },
                    },
                    "final_observation": {
                        "process": {
                            "pid": 101,
                            "start_ticks": 9001,
                            "exe": "/python",
                            "cwd": "/hft",
                            "cmdline_sha256": "c" * 64,
                        },
                        "live_artifacts": {
                            "resolved_paths": {},
                            "sha256": {
                                "model": prepared["artifact_sha256"]["model"],
                                "service_source": prepared["artifact_sha256"]["service_source"],
                                "engine_source": prepared["artifact_sha256"]["engine_source"],
                                "python_executable": "d" * 64,
                            },
                            "health_model_path_matches": True,
                            "health_model_sha256": prepared["artifact_sha256"]["model"],
                            "health_inference_engine": "numpy_exact",
                        },
                        "listener_50051": {"query_ok": True, "owner_pids": [101]},
                        "localhost_health": {
                            "query_ok": True,
                            "response": {
                                "ok": True,
                                "candidate_id": "A09",
                                "model_sha256": prepared["artifact_sha256"]["model"],
                                "inference_engine": "numpy_exact",
                                "service_counters": {"failures": 0},
                            },
                        },
                    },
                },
                "samples": service_samples,
            },
        )
        eligible = [
            {"event_id": "e{}".format(index), "eligible_groups": ["g"]}
            for index in range(1, 200, 2)
        ]
        relations = [
            {"sample_id": "q{}".format(index), "group": "g", "event_id": "e{}".format(index)}
            for index in range(1, 200, 2)
        ]
        portable_source = dump(
            self.root / "official_quality_source.json",
            {
                "schema_version": 1,
                "scope": "hft_mgbs_unsw_official_quality_source_v1",
                "source_kind": "official_unsw_ground_truth_and_frozen_pcap_inputs",
                "synthetic": False,
                "portable": True,
                "embedded_input_hash_manifest": {"schema_version": 1},
                "eligible_events": eligible,
                "sample_event_relations": relations,
            },
        )
        portable_prepare = self.root / "trusted_prepare_receipt.json"
        portable_prepare.write_bytes((self.root / "prepared" / "prepare_receipt.json").read_bytes())
        labels = dump(
            self.root / "labels-complete.json",
            {
                "schema_version": 2,
                "scope": "hft_mgbs_independent_ground_truth_labels_v2",
                "source_kind": "official_labels",
                "synthetic": False,
                "independent_holdout": True,
                "source_artifact_path": portable_source.name,
                "source_artifact_sha256": digest(portable_source),
                "source_record_locator": "official:frozen-holdout",
                "prepare_receipt_path": portable_prepare.name,
                "prepare_receipt_sha256": digest(self.root / "prepared" / "prepare_receipt.json"),
                "records": [
                    {"sample_id": "q{}".format(index), "label": index % 2, "group": "g"}
                    for index in range(200)
                ],
                "eligible_events": eligible,
                "sample_event_relations": relations,
            },
        )
        predictions = dump(
            self.root / "predictions-complete.json",
            {
                "schema_version": 2,
                "scope": "hft_mgbs_independent_predictions_v2",
                "synthetic": False,
                "generation_kind": "frozen_model_inference_on_independent_holdout",
                "source_artifact_sha256": digest(portable_source),
                "labels_sha256": digest(labels),
                "model_sha256": prepared["artifact_sha256"]["model"],
                "runtime_manifest_sha256": prepared["artifact_sha256"]["runtime_manifest"],
                "prepare_receipt_sha256": digest(self.root / "prepared" / "prepare_receipt.json"),
                "records": [
                    {"sample_id": "q{}".format(index), "prediction": index % 2, "score": float(index % 2)}
                    for index in range(200)
                ],
            },
        )
        manifest_rows = []
        for path in sorted(run.rglob("*")):
            if path.is_file():
                manifest_rows.append("{}  {}\n".format(digest(path), path.relative_to(run).as_posix()))
        source_manifest = run / "evidence.sha256"
        source_manifest.write_text("".join(manifest_rows), encoding="utf-8")
        finalized = finalize_evidence(
            config_path=CONFIG,
            output_dir=self.root / "finalized-complete",
            evidence_dir=run,
            campaign_id="campaign",
            candidate_id="candidate",
            backend="tpacket_v3",
            mode="normal",
            repeat_index=1,
            prepare_receipt=self.root / "prepared" / "prepare_receipt.json",
            physical_raw=physical,
            service_raw=service_raw,
            quality_labels=labels,
            quality_predictions=predictions,
        )
        self.assertTrue(finalized["adapter_ready"], finalized)
        staged = finalized["adapter_arguments"]
        result, _, _ = bind_runner_evidence(
            profile_path=ROOT / "configs" / "current_hardware_2_79_release_profile_v2.json",
            evidence_dir=run,
            binding_root=self.root,
            work_dir=self.root / "adapter-work-complete",
            campaign_id="campaign",
            candidate_id="candidate",
            backend="tpacket_v3",
            mode="normal",
            repeat_index=1,
            source_manifest=source_manifest,
            staged_artifacts={
                name: Path(staged[name])
                for name in (
                    "model", "runtime_manifest", "service_source", "engine_source", "service_launcher",
                    "identity_receipt", "window_observations", "physical_resources", "service_resources",
                )
            },
            quality_labels=Path(staged["quality_labels"]),
            quality_predictions=Path(staged["quality_predictions"]),
            fallback_events=None,
        )
        self.assertTrue(result["run_qualified"], result["errors"])
        self.assertEqual(result["evidence_gaps"], [])


if __name__ == "__main__":
    unittest.main()
