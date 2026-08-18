from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.current_hardware_279 import (
    compose_current_hardware_candidate_v2,
    compose_current_hardware_raw_run_v2,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "configs" / "current_hardware_2_79_release_profile_v2.json"


def write(path: Path, data: bytes) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": path.name, "sha256": hashlib.sha256(data).hexdigest()}


def write_json(path: Path, value: object) -> dict[str, str]:
    return write(path, (json.dumps(value, sort_keys=True, allow_nan=False) + "\n").encode())


def latency(prefix: str, count: int, value: float) -> list[dict[str, object]]:
    return [
        {"sample_id": f"{prefix}-sample-{index}", "source_event_id": f"{prefix}-event-{index}", "value_us": value}
        for index in range(count)
    ]


class CurrentHardware279V2Test(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.profile_sha = hashlib.sha256(PROFILE.read_bytes()).hexdigest()
        self.campaign = "v2-campaign"
        self.candidate = "tpacket-v2"
        self.backend = "tpacket_v3"
        self.base_epoch = 1_900_000_000

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def counters(multiplier: int) -> dict[str, int]:
        packet = 2_800_000 * multiplier
        flow = 1000 * multiplier
        batch = 100 * multiplier
        return {
            "pktgen_offered": packet,
            "nic_rx_ucast": packet,
            "nic_rx_discards": 0,
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

    def labels_predictions(self, runtime_sha: str, model_sha: str):
        eligible = [
            {"event_id": f"e-{i}", "eligible_groups": [f"g-{(i // 2) % 2}"]}
            for i in range(1, 200, 2)
        ]
        relations = [
            {"sample_id": f"q-{i}", "group": f"g-{(i // 2) % 2}", "event_id": f"e-{i}"}
            for i in range(1, 200, 2)
        ]
        source_ref = write_json(
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
        labels = {
            "schema_version": 2,
            "scope": "hft_mgbs_independent_ground_truth_labels_v2",
            "source_kind": "official_labels",
            "synthetic": False,
            "independent_holdout": True,
            "source_artifact_path": "official_quality_source.json",
            "source_artifact_sha256": source_ref["sha256"],
            "records": [
                {"sample_id": f"q-{i}", "label": i % 2, "group": f"g-{(i // 2) % 2}"}
                for i in range(200)
            ],
            "eligible_events": eligible,
            "sample_event_relations": relations,
        }
        labels_ref = write_json(self.root / "labels.json", labels)
        predictions = {
            "schema_version": 2,
            "scope": "hft_mgbs_independent_predictions_v2",
            "synthetic": False,
            "labels_sha256": labels_ref["sha256"],
            "model_sha256": model_sha,
            "runtime_manifest_sha256": runtime_sha,
            "records": [
                {"sample_id": f"q-{i}", "prediction": i % 2, "score": float(i % 2)}
                for i in range(200)
            ],
        }
        return source_ref, labels_ref, write_json(self.root / "predictions.json", predictions)

    def raw_fixture(self, mode="normal", repeat=1, windows=15):
        artifact_refs: dict[str, dict[str, str]] = {}
        artifact_refs["runner"] = write(self.root / "runner.sh", b"runner-v2\n")
        artifact_refs["config"] = write(self.root / "config.json", b"{}\n")
        artifact_refs["capture_binary"] = write(self.root / "capture.bin", b"capture-v2\n")
        artifact_refs["model"] = write(self.root / "model.bin", b"model-v2\n")
        artifact_refs["service_source"] = write(self.root / "gpu_service.py", b"service-v2\n")
        artifact_refs["engine_source"] = write(self.root / "engine.py", b"engine-v2\n")
        artifact_refs["service_launcher"] = write(self.root / "launcher.sh", b"launcher-v2\n")
        runtime = {
            "schema_version": 2,
            "scope": "selected_runtime_thread_all",
            "process_start_ticks": 12345,
            "inference_engine": "numpy_exact",
            "model_sha256": artifact_refs["model"]["sha256"],
            "service_source_sha256": artifact_refs["service_source"]["sha256"],
            "numpy_engine_source_sha256": artifact_refs["engine_source"]["sha256"],
            "launcher_sha256": artifact_refs["service_launcher"]["sha256"],
        }
        artifact_refs["runtime_manifest"] = write_json(self.root / "runtime.json", runtime)
        pipeline = {
            "schema_version": 1,
            "scope": "hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw",
            "backend": "tpacket_v3_packet_fanout_borrowed",
            "gpu_ready_at_start": True,
            "all_workers_error_free": True,
            "internal_delivery_lossless": True,
            "packets": 2_800_000 * windows,
            "packets_parsed": 2_800_000 * windows,
            "parse_rejected": 0,
            "flows_closed": 1000 * windows,
            "feature_queue_submitted": 1000 * windows,
            "feature_queue_drops": 0,
            "epoch_second_counts": {str(self.base_epoch + i): 2_800_000 for i in range(windows)},
            "scheduler": {"fatal_error": None},
            "shutdown": {
                "capture_workers_joined": 8,
                "capture_workers_expected": 8,
                "scheduler_thread_joined": True,
                "scheduler_input_channel_drained": True,
                "dispatcher_finish_called": True,
            },
            "pipeline_metrics": {
                "gpu_flows_enqueued": 1000 * windows,
                "gpu_flows_scored": 1000 * windows,
                "gpu_batches_ok": 100 * windows,
                "gpu_batches_failed": 0,
                "gpu_queue_full": 0,
                "key_flows_total": 1000 * windows,
                "key_flows_enqueued": 1000 * windows,
                "key_flows_enqueue_failed": 0,
                "key_flows_scored": 1000 * windows,
                "key_flows_inference_failed": 0,
                "key_flows_local_fallback_completed": 0,
                "budget_overrun_count": 0,
                "full_pipeline_qualified": False,
            },
            "full_pipeline_qualified": False,
            "final_pareto_ingestion_allowed": False,
        }
        artifact_refs["pipeline_raw"] = write_json(self.root / "pipeline_raw.json", pipeline)
        artifact_refs["diagnostic_receipt"] = write_json(
            self.root / "receipt.json",
            {"runner_exit_status": 0, "restoration_verified": True, "full_pipeline_qualified": False},
        )
        artifact_refs["pipeline_ready"] = write_json(
            self.root / "ready.json", {"ready": True, "gpu_ready_at_start": True}
        )
        artifact_refs["execution_events"] = write(
            self.root / "events.tsv",
            b"utc\tevent\n2026-08-13T00:00:00Z\tpipeline_spawned\n2026-08-13T00:00:01Z\tgpu_reverse_ready\n2026-08-13T00:00:02Z\tgenerator_started\n2026-08-13T00:00:20Z\tgenerator_stopped\n2026-08-13T00:00:21Z\tpipeline_completed\n",
        )
        identity = {
            "schema_version": 2,
            "scope": "hft_mgbs_current_hardware_2_79_run_identity_receipt_v2",
            "campaign_id": self.campaign,
            "candidate_id": self.candidate,
            "backend": self.backend,
            "mode": mode,
            "repeat_index": repeat,
            "run_id": f"run-{mode}-{repeat}",
            "generator_run_id": f"generator-{mode}-{repeat}",
            "generator_process_start_ticks": 1000 + repeat + (100 if mode == "fallback" else 0),
            "hardware_identity_sha256": "a" * 64,
            "code_tree_sha256": "b" * 64,
        }
        artifact_refs["identity_receipt"] = write_json(self.root / "identity.json", identity)
        window_rows = []
        for index in range(windows):
            prefix = f"{mode}-{repeat}-{index}"
            window_rows.append(
                {
                    "epoch_second": self.base_epoch + index,
                    "duration_ns": 1_000_000_000,
                    "counters_start": self.counters(index),
                    "counters_end": self.counters(index + 1),
                    "packet_latency_us": latency(prefix + "-packet", 1000, 10),
                    "flow_latency_us": latency(prefix + "-flow", 1000, 100),
                    "kernel_to_feature_latency_us": latency(prefix + "-feature", 1000, 200),
                    "end_to_end_latency_us": latency(prefix + "-e2e", 1000, 500),
                    "gpu_batch_latency_us": latency(prefix + "-gpu", 100, 1000),
                }
            )
        artifact_refs["window_observations"] = write_json(
            self.root / "windows.json",
            {
                "schema_version": 2,
                "scope": "hft_mgbs_current_hardware_2_79_window_observations_v2",
                "run_id": identity["run_id"],
                "generator_run_id": identity["generator_run_id"],
                "windows": window_rows,
            },
        )
        for role in ("physical", "service"):
            rows = []
            for index in range(windows):
                row = {"epoch_second": self.base_epoch + index, "cpu_fraction": 0.5, "memory_fraction": 0.4}
                if role == "service":
                    row.update({"gpu_fraction": 0.0, "gpu_memory_fraction": 0.0})
                rows.append(row)
            artifact_refs[f"{role}_resources"] = write_json(
                self.root / f"{role}.json",
                {
                    "schema_version": 2,
                    "scope": "hft_mgbs_current_hardware_2_79_resource_samples_v2",
                    "node_role": role,
                    "run_id": identity["run_id"],
                    "samples": rows,
                },
            )
        artifact_refs["nic_statistics_before"] = write(self.root / "nic_before.txt", b"     rx_ucast_packets: 0\n     rx_discards: 0\n")
        artifact_refs["nic_statistics_after"] = write(
            self.root / "nic_after.txt", f"     rx_ucast_packets: {2_800_000 * windows}\n     rx_discards: 0\n".encode()
        )
        pktgen_ref = write(
            self.root / "pktgen.txt",
            f"Result: OK: 19000000(c1+d1) usec, {2_800_000 * windows} (64byte,0frags)\n".encode(),
        )
        source_ref, labels_ref, predictions_ref = self.labels_predictions(
            artifact_refs["runtime_manifest"]["sha256"], artifact_refs["model"]["sha256"]
        )
        manifest_lines = []
        for ref in list(artifact_refs.values()) + [pktgen_ref, source_ref, labels_ref, predictions_ref]:
            manifest_lines.append(f"{ref['sha256']}  {ref['path']}")
        manifest_ref = write(self.root / "evidence.sha256", ("\n".join(manifest_lines) + "\n").encode())
        fallback_ref = None
        if mode == "fallback":
            fallback_ref = write_json(
                self.root / "fallback.json",
                {
                    "schema_version": 2,
                    "scope": "hft_mgbs_current_hardware_2_79_fallback_events_v2",
                    "run_id": identity["run_id"],
                    "trial_id": f"trial-{repeat}",
                    "events": [
                        {"step": name, "monotonic_ns": repeat * 10_000_000_000 + index * 10_000_000}
                        for index, name in enumerate(
                            [
                                "fault_injection_observed", "local_fallback_activated", "post_switch_traffic_observed",
                                "primary_recovered", "fallback_state_cleared", "capture_backend_restored",
                                "interfaces_restored", "final_state_verification",
                            ]
                        )
                    ],
                    "transition_packet_gap": 0,
                    "capture_drop_during_fallback": 0,
                },
            )
        request = {
            "schema_version": 2,
            "scope": "hft_mgbs_current_hardware_2_79_raw_run_input_v2",
            "profile_sha256": self.profile_sha,
            "evidence_root": ".",
            "campaign_id": self.campaign,
            "candidate_id": self.candidate,
            "backend": self.backend,
            "mode": mode,
            "repeat_index": repeat,
            "evidence_manifest": manifest_ref,
            "artifacts": artifact_refs,
            "pktgen_devices": [pktgen_ref],
            "quality": {"source": source_ref, "labels": labels_ref, "predictions": predictions_ref},
            "fallback_events": fallback_ref,
        }
        input_path = self.root / "raw_input.json"
        write_json(input_path, request)
        return input_path, request

    def compose(self, mode="normal", repeat=1, windows=15):
        path, request = self.raw_fixture(mode, repeat, windows)
        return compose_current_hardware_raw_run_v2(PROFILE, path), path, request

    def rewrite_request(self, path: Path, request: dict):
        write_json(path, request)

    def mutate_json_artifact(self, path: Path, request: dict, name: str, mutator):
        ref = request["artifacts"][name]
        artifact = self.root / ref["path"]
        payload = json.loads(artifact.read_text())
        mutator(payload)
        request["artifacts"][name] = write_json(artifact, payload)
        self.rewrite_request(path, request)

    def test_positive_raw_run_recomputes_and_remains_nonproduction(self):
        result, _, _ = self.compose()
        self.assertTrue(result["run_qualified"], result["errors"])
        self.assertEqual(result["window_summary"]["consecutive_complete_windows"], 15)
        self.assertEqual(result["window_summary"]["minimum_mpps"], 2.8)
        self.assertFalse(result["candidate_evidence_qualified"])
        self.assertFalse(result["production_release_accepted"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_unmatched_eligible_event_remains_in_event_recall_denominator(self):
        result, path, request = self.compose()
        source_ref = request["quality"]["source"]
        labels_ref = request["quality"]["labels"]
        source_path = self.root / source_ref["path"]
        labels_path = self.root / labels_ref["path"]
        source = json.loads(source_path.read_text())
        labels = json.loads(labels_path.read_text())
        unmatched = {"event_id": "official-unmatched", "eligible_groups": ["g-0"]}
        source["eligible_events"].append(unmatched)
        labels["eligible_events"].append(unmatched)
        request["quality"]["source"] = write_json(source_path, source)
        labels["source_artifact_sha256"] = request["quality"]["source"]["sha256"]
        request["quality"]["labels"] = write_json(labels_path, labels)
        predictions_path = self.root / request["quality"]["predictions"]["path"]
        predictions = json.loads(predictions_path.read_text())
        predictions["labels_sha256"] = request["quality"]["labels"]["sha256"]
        request["quality"]["predictions"] = write_json(predictions_path, predictions)
        manifest_refs = list(request["artifacts"].values()) + request["pktgen_devices"] + [
            request["quality"]["source"],
            request["quality"]["labels"],
            request["quality"]["predictions"],
        ]
        request["evidence_manifest"] = write(
            self.root / "evidence.sha256",
            ("\n".join("{}  {}".format(ref["sha256"], ref["path"]) for ref in manifest_refs) + "\n").encode(),
        )
        self.rewrite_request(path, request)
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertIsNotNone(result["quality"], result["errors"])
        self.assertAlmostEqual(result["quality"]["ground_truth_event_recall"], 100 / 101)

    def test_missing_and_nonconsecutive_windows_fail_closed(self):
        result, _, _ = self.compose(windows=14)
        self.assertFalse(result["run_qualified"])
        self.assertIn("windows.consecutive_complete", result["errors"])
        result, path, request = self.compose()
        self.mutate_json_artifact(path, request, "window_observations", lambda value: value["windows"].__setitem__(7, {**value["windows"][7], "epoch_second": self.base_epoch + 30}))
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertIn("windows.consecutive_complete", result["errors"])

    def test_hash_drift_and_nic_discard_fail_closed(self):
        result, path, request = self.compose()
        artifact = self.root / request["artifacts"]["capture_binary"]["path"]
        artifact.write_bytes(b"tampered")
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertIn("artifacts.capture_binary.sha256", result["errors"])
        result, path, request = self.compose()
        self.mutate_json_artifact(path, request, "window_observations", lambda value: value["windows"][3]["counters_end"].__setitem__("nic_rx_discards", 1))
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertTrue(any("nic_rx_discards" in error or "packet_loss" in error for error in result["errors"]))

    def test_flow_sample_gate_rejects_duplicate_padding(self):
        result, path, request = self.compose()
        def duplicate(value):
            samples = value["windows"][0]["flow_latency_us"]
            samples[999] = copy.deepcopy(samples[998])
        self.mutate_json_artifact(path, request, "window_observations", duplicate)
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertIn("windows.epoch.1900000000.flow_latency_us.schema", result["errors"])

    def test_key_flow_conservation_and_quality_absence_fail_closed(self):
        result, path, request = self.compose()
        self.mutate_json_artifact(path, request, "window_observations", lambda value: value["windows"][0]["counters_end"].__setitem__("key_flows_scored", 999))
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertTrue(any("key_flow" in error for error in result["errors"]))
        result, path, request = self.compose()
        request["quality"] = None
        self.rewrite_request(path, request)
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertIn("quality.reference", result["errors"])

    def test_resource_absence_and_fallback_fake_completion_fail_closed(self):
        result, path, request = self.compose()
        self.mutate_json_artifact(path, request, "service_resources", lambda value: value["samples"].clear())
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertTrue(any("service_resource_samples" in error for error in result["errors"]))
        result, path, request = self.compose(mode="fallback")
        fallback = self.root / request["fallback_events"]["path"]
        payload = json.loads(fallback.read_text())
        payload["events"] = payload["events"][:-1]
        request["fallback_events"] = write_json(fallback, payload)
        self.rewrite_request(path, request)
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertIn("fallback.schema", result["errors"])

    def test_current_eight_flow_shape_fails_sample_gates(self):
        result, path, request = self.compose()
        def shrink(value):
            for window in value["windows"]:
                for name in ("flow_latency_us", "kernel_to_feature_latency_us", "end_to_end_latency_us"):
                    window[name] = window[name][:8]
                window["gpu_batch_latency_us"] = window["gpu_batch_latency_us"][:4]
        self.mutate_json_artifact(path, request, "window_observations", shrink)
        result = compose_current_hardware_raw_run_v2(PROFILE, path)
        self.assertFalse(result["run_qualified"])
        self.assertTrue(any("flow_latency_us.sample_count" in error for error in result["errors"]))
        self.assertTrue(any("gpu_batch_latency_us.sample_count" in error for error in result["errors"]))

    def test_candidate_duplicate_identity_and_missing_repeat_fail_closed(self):
        run_refs = []
        for mode in ("normal", "fallback"):
            for repeat in (1, 2, 3):
                result, _, _ = self.compose(mode, repeat)
                run_path = self.root / f"sealed-{mode}-{repeat}.json"
                run_refs.append({"mode": mode, "repeat": repeat, **write_json(run_path, result)})
        candidate = {
            "schema_version": 2,
            "scope": "hft_mgbs_current_hardware_2_79_candidate_input_v2",
            "profile_sha256": self.profile_sha,
            "evidence_root": ".",
            "campaign_id": self.campaign,
            "candidate_id": self.candidate,
            "backend": self.backend,
            "raw_runs": [{"path": item["path"], "sha256": item["sha256"]} for item in run_refs],
        }
        candidate_path = self.root / "candidate.json"
        write_json(candidate_path, candidate)
        positive = compose_current_hardware_candidate_v2(PROFILE, candidate_path)
        self.assertTrue(positive["candidate_evidence_qualified"], positive["errors"])
        self.assertFalse(positive["production_release_accepted"])
        missing = copy.deepcopy(candidate)
        missing["raw_runs"] = missing["raw_runs"][:-1]
        write_json(candidate_path, missing)
        result = compose_current_hardware_candidate_v2(PROFILE, candidate_path)
        self.assertFalse(result["candidate_evidence_qualified"])
        self.assertIn("campaign.repeat_matrix", result["errors"])
        duplicated = copy.deepcopy(candidate)
        source = self.root / duplicated["raw_runs"][1]["path"]
        payload = json.loads(source.read_text())
        payload["run_id"] = json.loads((self.root / duplicated["raw_runs"][0]["path"]).read_text())["run_id"]
        duplicated["raw_runs"][1] = write_json(source, payload)
        write_json(candidate_path, duplicated)
        result = compose_current_hardware_candidate_v2(PROFILE, candidate_path)
        self.assertFalse(result["candidate_evidence_qualified"])
        self.assertTrue(any("run_identity" in error for error in result["errors"]))
        duplicated_generator = copy.deepcopy(candidate)
        first_payload = json.loads((self.root / duplicated_generator["raw_runs"][0]["path"]).read_text())
        second_path = self.root / duplicated_generator["raw_runs"][1]["path"]
        second_payload = json.loads(second_path.read_text())
        second_payload["generator_run_id"] = first_payload["generator_run_id"]
        second_payload["generator_process_start_ticks"] = first_payload["generator_process_start_ticks"]
        duplicated_generator["raw_runs"][1] = write_json(second_path, second_payload)
        write_json(candidate_path, duplicated_generator)
        result = compose_current_hardware_candidate_v2(PROFILE, candidate_path)
        self.assertFalse(result["candidate_evidence_qualified"])
        self.assertTrue(any("generator_identity" in error for error in result["errors"]))

    def test_cli_raw_run_v2(self):
        _, input_path, _ = self.compose()
        output = self.root / "output.json"
        completed = subprocess.run(
            [sys.executable, "scripts/compose_current_hardware_279.py", "--kind", "raw-run-v2", "--profile", str(PROFILE), "--input", str(input_path), "--output", str(output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(output.read_text())["run_qualified"])


if __name__ == "__main__":
    unittest.main()
