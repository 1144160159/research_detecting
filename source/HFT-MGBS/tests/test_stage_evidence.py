from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.production_pareto import METRIC_NAMES
from hft_mgbs.release_materializer import materialize_stage_campaign
from hft_mgbs.stage_evidence import (
    PARETO_NUMERIC_FIELDS,
    aggregate_stage_evidence,
    canonical_json_bytes,
    load_contract,
    validate_stage_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(
    ROOT / "configs" / "production_stage_receipt_contract_v1.json"
)
STEPS = CONTRACT.payload["fallback_restoration"]["required_steps"]


def digest(seed: int) -> str:
    return format(seed, "064x")


def canonical_digest(value) -> str:
    import hashlib

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def identity_manifests(stage: str, backend: str, identity: dict):
    code_files = [
        {
            "path": "hft_mgbs/inference.py",
            "sha256": digest(601),
            "size_bytes": 4096,
            "language": "python",
            "role": "inference",
        },
        {
            "path": "rust/hft-dpdk/src/main.rs",
            "sha256": digest(602),
            "size_bytes": 8192,
            "language": "rust",
            "role": "capture",
        },
    ]
    code = {
        "schema_version": 1,
        "scope": "hft_mgbs_code_identity_manifest",
        "candidate_id": "A09",
        "source_revision_sha256": digest(603),
        "source_tree_sha256": canonical_digest(code_files),
        "files": code_files,
    }
    input_sources = [
        {
            "source_id": "production-evaluation-pcap",
            "role": "evaluation",
            "sha256": digest(611),
            "byte_count": 100_000_000,
            "record_count": 1_000_000,
            "provenance_uri": "dataset://hft/production-evaluation-pcap",
        }
    ]
    input_document = {
        "schema_version": 1,
        "scope": "hft_mgbs_input_identity_manifest",
        "candidate_id": "A09",
        "dataset_id": "hft-production-evaluation-v1",
        "split_id": "sealed-independent-test-v1",
        "feature_schema_sha256": digest(612),
        "source_set_sha256": canonical_digest(input_sources),
        "sources": input_sources,
    }
    identity["code_sha256"] = canonical_digest(code)
    identity["input_sha256"] = canonical_digest(input_document)
    model_artifacts = [
        {
            "path": "models/a09/model.bin",
            "role": "inference_model",
            "sha256": digest(621),
            "size_bytes": 1_000_000,
        }
    ]
    model = {
        "schema_version": 1,
        "scope": "hft_mgbs_model_identity_manifest",
        "candidate_id": "A09",
        "model_id": "A09",
        "algorithm_id": "adaptive-budget-a09-v1",
        "training_input_manifest_sha256": identity["input_sha256"],
        "feature_schema_sha256": input_document["feature_schema_sha256"],
        "artifact_set_sha256": canonical_digest(model_artifacts),
        "artifacts": model_artifacts,
    }
    identity["model_sha256"] = canonical_digest(model)
    runtime_components = [
        {
            "name": "gpu-inference",
            "role": "inference",
            "version": "1.0.0",
            "binary_sha256": digest(631),
        },
        {
            "name": "rust-capture",
            "role": "capture",
            "version": "1.0.0",
            "binary_sha256": identity["capture_binary_sha256"],
        },
    ]
    runtime = {
        "schema_version": 1,
        "scope": "hft_mgbs_runtime_identity_manifest",
        "candidate_id": "A09",
        "backend": backend,
        "hardware_identity": identity["hardware_identity"],
        "code_manifest_sha256": identity["code_sha256"],
        "model_manifest_sha256": identity["model_sha256"],
        "capture_binary_sha256": identity["capture_binary_sha256"],
        "host_roles": {
            "capture_host": "physical-10.0.5.8",
            "inference_host": "gpu-10.0.5.103",
        },
        "component_set_sha256": canonical_digest(runtime_components),
        "components": runtime_components,
    }
    identity["runtime_manifest_sha256"] = canonical_digest(runtime)
    parameters = {
        "target_mpps": 10.0,
        "window_duration_s": 60 if stage.startswith("r4_") else 1,
    }
    stage_config = {
        "schema_version": 1,
        "scope": "hft_mgbs_stage_config_identity_manifest",
        "candidate_id": "A09",
        "stage": stage,
        "backend": backend,
        "contract_sha256": identity["contract_sha256"],
        "hardware_identity": identity["hardware_identity"],
        "code_manifest_sha256": identity["code_sha256"],
        "input_manifest_sha256": identity["input_sha256"],
        "runtime_manifest_sha256": identity["runtime_manifest_sha256"],
        "model_manifest_sha256": identity["model_sha256"],
        "capture_binary_sha256": identity["capture_binary_sha256"],
        "parameters": parameters,
        "parameters_sha256": canonical_digest(parameters),
    }
    identity["stage_config_sha256"] = canonical_digest(stage_config)
    return {
        "code": code,
        "input": input_document,
        "stage_config": stage_config,
        "runtime": runtime,
        "model": model,
    }


def histogram(kind: str):
    if kind == "kernel_entry_to_shard":
        bounds = [50.0, 100.0, 500.0]
    elif kind == "internal_feature_enqueue":
        bounds = [1000.0, 5000.0, 6000.0]
    elif kind == "kernel_entry_to_feature_enqueue":
        bounds = [1000.0, 5000.0, 10000.0, 50000.0]
    else:
        bounds = [1000.0, 10000.0, 50000.0]
    counts = [990, 9, 1] + ([0] if len(bounds) == 4 else [])
    return {
        "upper_bounds_us": bounds,
        "bucket_counts": counts,
        "overflow_count": 0,
    }


def quality_raw():
    confusion = {"tp": 900, "fp": 40, "fn": 100, "tn": 960}
    bins = []
    for index in range(10):
        midpoint = (index + 0.5) / 10
        bins.append(
            {
                "bin_index": index,
                "lower_bound": index / 10,
                "upper_bound": (index + 1) / 10,
                "count": 200,
                "positive_count": 10 + 20 * index,
                "confidence_sum": midpoint * 200,
            }
        )
    return {
        "group_confusions": [
            {"group_id": "g1", **confusion},
            {"group_id": "g2", **confusion},
        ],
        "independent_confusion": confusion,
        "score_buckets_descending": [
            {"score_threshold": 0.9, "positive_count": 600, "negative_count": 10},
            {"score_threshold": 0.5, "positive_count": 300, "negative_count": 90},
            {"score_threshold": 0.1, "positive_count": 100, "negative_count": 900},
        ],
        "calibration_bins": bins,
        "ground_truth_event_total": 100,
        "ground_truth_event_matched": 80,
    }


def make_receipt(stage: str, repeat: int = 0, identity_seed: int = 100):
    gate = CONTRACT.payload["stage_gates"][stage]
    count = gate.get("minimum_full_windows", gate.get("required_windows"))
    duration_s = gate.get("window_duration_s", 1)
    received = int(10_100_000 * duration_s)
    latency_names = {
        "r1": ("kernel_entry_to_shard",),
        "r2": ("kernel_entry_to_feature_enqueue", "internal_feature_enqueue"),
        "r3": ("end_to_end",),
        "r4_24h": ("end_to_end",),
        "r4_72h": ("end_to_end",),
    }[stage]
    stage_number = ("r1", "r2", "r3", "r4_24h", "r4_72h").index(stage)
    base_ns = 2_000_000_000_000_000_000 + stage_number * 1_000_000_000_000_000
    windows = []
    for index in range(count):
        start = base_ns + index * duration_s * 1_000_000_000
        window = {
            "window_index": index,
            "start_unix_ns": start,
            "end_unix_ns": start + duration_s * 1_000_000_000,
            "packets_offered": received,
            "packets_received": received,
            "packets_parsed": received,
            "parse_reject_count": 0,
            "l2_bytes_received": received * 64,
            "shard_packet_count": received,
            "shard_byte_count": received * 64,
            "loss": {
                "nic_rx_missed": 0,
                "nic_rx_errors": 0,
                "socket_drops": 0,
                "sequence_gaps": 0,
            },
            "latency_histograms": {
                name: histogram(name) for name in latency_names
            },
        }
        if stage != "r1":
            window.update(
                {
                    "base_feature_update_count": received,
                    "feature_update_reject_count": 0,
                    "budget_overrun_count": 0,
                    "key_flow_total": 100,
                    "key_flow_covered": 100,
                    "key_flow_skipped_due_budget": 0,
                }
            )
        if stage in ("r3", "r4_24h", "r4_72h"):
            window.update(
                {
                    "gpu_queue_full_count": 0,
                    "gpu_batches_failed_count": 0,
                    "normal_fallback_unit_count": 0,
                    "closed_flow_or_window_unit_count": 2000 if stage == "r3" and index == 0 else 0,
                    "a09_scored_unit_count": 2000 if stage == "r3" and index == 0 else 0,
                    "local_fallback_unit_count": 0,
                }
            )
        if stage.startswith("r4_"):
            window.update(
                {
                    "clock_step_count": 0,
                    "runtime_manifest_sha256": digest(4),
                    "resource": {"host_memory_fraction": 0.4},
                }
            )
        windows.append(window)
    identity = {
        "run_bundle_identity": digest(identity_seed),
        "generator_run_identity": digest(identity_seed + 100),
        "hardware_identity": digest(1),
        "code_sha256": digest(2),
        "input_sha256": digest(3),
        "contract_sha256": CONTRACT.sha256,
        "stage_config_sha256": digest(2000 + stage_number),
        "runtime_manifest_sha256": digest(4),
        "model_sha256": digest(5),
        "capture_binary_sha256": digest(6),
        "evidence_manifest_sha256": digest(identity_seed + 200),
    }
    receipt = {
        "schema_version": 1,
        "scope": "hft_mgbs_production_stage_raw_receipt",
        "stage": stage,
        "candidate_id": "A09",
        "backend": "dpdk",
        "standalone_receipt_trusted": False,
        "identity": identity,
        "identity_manifests": identity_manifests(stage, "dpdk", identity),
        "windows": windows,
    }
    if stage.startswith("r4_"):
        for window in receipt["windows"]:
            window["runtime_manifest_sha256"] = identity[
                "runtime_manifest_sha256"
            ]
    if stage in ("r3", "r4_24h", "r4_72h"):
        sample_count = gate.get("resource_samples_min", 10)
        receipt["resource_samples"] = [
            {
                "timestamp_unix_ns": base_ns + (index + 1) * 1_000_000_000,
                "host_cpu_fraction": 0.5,
                "host_memory_fraction": 0.4,
                "service_gpu_utilization_fraction": 0.3,
                "service_gpu_memory_fraction": 0.2,
            }
            for index in range(sample_count)
        ]
        trial_count = gate.get("fallback_trials_min", gate.get("fault_injections_min"))
        receipt["fallback_trials"] = [
            {
                "trial_id": f"{stage}-fallback-{index}",
                "fault_injected_unix_ns": base_ns + (index + 1) * 1_000_000_000,
                "recovery_completed_unix_ns": base_ns + (index + 1) * 1_000_000_000 + 200_000_000,
                "recovery_ns": 200_000_000,
                "transition_packet_gap": 0,
                "capture_drop_count": 0,
                "post_switch_packets": 1000,
                "steps": {name: True for name in STEPS},
            }
            for index in range(trial_count)
        ]
        receipt["restoration_steps"] = {name: True for name in STEPS}
    if stage == "r3":
        receipt["quality_raw"] = quality_raw()
        receipt["efficiency_raw"] = {
            "baseline_independent_macro_f1": 0.7,
            "optional_cpu_us": 20.0,
            "total_cpu_us": 100.0,
        }
        receipt["complexity_raw"] = {
            "feature_count": 40,
            "tree_count": 500,
            "model_bytes": 100_000_000,
            "deployed_process_count": 3,
            "fallback_branch_count": 2,
        }
    return receipt


def campaign():
    receipts = []
    seed = 100
    for stage in ("r1", "r2", "r3"):
        for repeat in range(3):
            receipts.append(make_receipt(stage, repeat, seed))
            seed += 1
    receipts.append(make_receipt("r4_24h", 0, seed))
    receipts.append(make_receipt("r4_72h", 0, seed + 1))
    return receipts


def dual_backend_campaign():
    """Return a complete primary/fallback campaign with paired stage roles."""

    receipts = campaign()
    primary = "native_af_xdp_forced_zerocopy"
    fallback = "dpdk_multiqueue_rss_tss"
    paired = []
    next_seed = 10_000
    for receipt in receipts:
        stage_number = (
            "r1",
            "r2",
            "r3",
            "r4_24h",
            "r4_72h",
        ).index(receipt["stage"])
        primary_receipt = copy.deepcopy(receipt)
        primary_receipt["backend"] = primary
        primary_receipt["backend_role"] = "primary"
        primary_receipt["identity_manifests"] = identity_manifests(
            primary_receipt["stage"], primary, primary_receipt["identity"]
        )
        if primary_receipt["stage"].startswith("r4_"):
            for window in primary_receipt["windows"]:
                window["runtime_manifest_sha256"] = primary_receipt["identity"][
                    "runtime_manifest_sha256"
                ]
        paired.append(primary_receipt)

        fallback_receipt = copy.deepcopy(receipt)
        fallback_receipt["backend"] = fallback
        fallback_receipt["backend_role"] = "fallback"
        fallback_receipt["identity"]["run_bundle_identity"] = digest(next_seed)
        fallback_receipt["identity"]["generator_run_identity"] = digest(
            next_seed + 100
        )
        fallback_receipt["identity"]["evidence_manifest_sha256"] = digest(
            next_seed + 200
        )
        fallback_receipt["identity"]["capture_binary_sha256"] = digest(30_000)
        fallback_receipt["identity"]["runtime_manifest_sha256"] = digest(40_000)
        fallback_receipt["identity"]["stage_config_sha256"] = digest(
            50_000 + stage_number
        )
        fallback_receipt["identity_manifests"] = identity_manifests(
            fallback_receipt["stage"], fallback, fallback_receipt["identity"]
        )
        if fallback_receipt["stage"].startswith("r4_"):
            for window in fallback_receipt["windows"]:
                window["runtime_manifest_sha256"] = fallback_receipt["identity"][
                    "runtime_manifest_sha256"
                ]
        paired.append(fallback_receipt)
        next_seed += 1
    return paired


class StageEvidenceTests(unittest.TestCase):
    def test_complete_campaign_can_be_atomically_materialized(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = []
            for index, receipt in enumerate(campaign()):
                path = root / "raw-{:02d}.json".format(index)
                path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
                sources.append(path)
            output = root / "sealed-campaign"
            result = materialize_stage_campaign(
                raw_receipt_paths=sources,
                contract_path=ROOT / "configs" / "production_stage_receipt_contract_v1.json",
                output_dir=output,
            )
            self.assertTrue(result["qualified"])
            self.assertEqual(result["receipt_count"], len(sources))
            self.assertTrue((output / "campaign_receipt.json").is_file())
            self.assertTrue((output / "manifest.json").is_file())

    def test_contract_exactly_matches_final_pareto_metric_schema(self):
        exact = CONTRACT.payload["derived_production_pareto_metrics"]["exact_fields"]
        self.assertEqual(set(PARETO_NUMERIC_FIELDS), set(METRIC_NAMES))
        self.assertEqual(set(exact), set(METRIC_NAMES) | {"name"})

    def test_full_campaign_recomputes_metrics_without_receipt_verdict(self):
        result = aggregate_stage_evidence(campaign(), CONTRACT)
        self.assertTrue(result["qualified"], result["errors"][:10])
        self.assertTrue(all(result["stage_qualified"].values()))
        metrics = result["derived_production_pareto_metrics"]
        self.assertEqual(set(metrics), set(METRIC_NAMES) | {"name"})
        self.assertEqual(metrics["name"], "A09")
        self.assertGreaterEqual(metrics["throughput_mpps"], 10.0)
        self.assertEqual(metrics["packet_drop_count"], 0)
        self.assertIsInstance(metrics["packet_drop_count"], int)
        self.assertEqual(metrics["budget_overrun_count"], 0)
        self.assertIsInstance(metrics["budget_overrun_count"], int)
        self.assertEqual(metrics["key_flow_coverage"], 1.0)
        self.assertEqual(metrics["fallback_recovery_s"], 0.2)

    def test_dual_backend_campaign_requires_primary_and_fallback_per_stage(self):
        result = aggregate_stage_evidence(
            dual_backend_campaign(),
            CONTRACT,
            backend_binding={
                "primary_backend": "native_af_xdp_forced_zerocopy",
                "fallback_backend": "dpdk_multiqueue_rss_tss",
            },
        )

        self.assertTrue(result["qualified"], result["errors"][:10])
        self.assertEqual(
            result["backend_roles_qualified"],
            {"primary": True, "fallback": True},
        )

    def test_dual_backend_campaign_rejects_missing_fallback_role(self):
        receipts = [
            receipt
            for receipt in dual_backend_campaign()
            if receipt["backend_role"] != "fallback"
        ]

        result = aggregate_stage_evidence(
            receipts,
            CONTRACT,
            backend_binding={
                "primary_backend": "native_af_xdp_forced_zerocopy",
                "fallback_backend": "dpdk_multiqueue_rss_tss",
            },
        )

        self.assertFalse(result["qualified"])
        self.assertIn("campaign.r1.fallback.repeat_count", result["errors"])
        self.assertFalse(result["backend_roles_qualified"]["fallback"])

    def test_dual_backend_campaign_rejects_role_backend_swap(self):
        receipts = dual_backend_campaign()
        receipts[0]["backend"] = "dpdk_multiqueue_rss_tss"
        receipts[0]["identity_manifests"] = identity_manifests(
            receipts[0]["stage"], receipts[0]["backend"], receipts[0]["identity"]
        )

        result = aggregate_stage_evidence(
            receipts,
            CONTRACT,
            backend_binding={
                "primary_backend": "native_af_xdp_forced_zerocopy",
                "fallback_backend": "dpdk_multiqueue_rss_tss",
            },
        )

        self.assertFalse(result["qualified"])
        self.assertIn("campaign.receipt.0.backend_role_binding", result["errors"])

    def test_self_reported_qualified_is_rejected(self):
        receipt = make_receipt("r1")
        receipt["qualified"] = True
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r1.self_reported_verdict", result["errors"])

    def test_r1_loss_is_recomputed_from_independent_counters(self):
        receipt = make_receipt("r1")
        receipt["windows"][0]["packets_offered"] += 1
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r1.window.0.loss_accounting", result["errors"])

    def test_r2_key_flow_denominator_cannot_be_vacuous(self):
        receipt = make_receipt("r2")
        for window in receipt["windows"]:
            window["key_flow_total"] = 0
            window["key_flow_covered"] = 0
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r2.key_flow_nonempty", result["errors"])

    def test_r3_quality_bins_and_resource_are_recomputed(self):
        receipt = make_receipt("r3")
        receipt["quality_raw"]["calibration_bins"][0]["positive_count"] += 1
        receipt["resource_samples"][0]["host_cpu_fraction"] = 0.9
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r3.quality.calibration_positive_accounting", result["errors"])
        self.assertIn("r3.resource.host_cpu_fraction", result["errors"])

    def test_r4_requires_complete_time_axis_and_no_drift(self):
        receipt = make_receipt("r4_24h")
        receipt["windows"][100]["start_unix_ns"] += 1
        receipt["windows"][100]["end_unix_ns"] += 1
        for window in receipt["windows"][-360:]:
            window["packets_received"] = int(window["packets_received"] * 0.94)
            window["packets_offered"] = window["packets_received"]
            window["packets_parsed"] = window["packets_received"]
            window["l2_bytes_received"] = window["packets_received"] * 64
            window["shard_packet_count"] = window["packets_received"]
            window["shard_byte_count"] = window["l2_bytes_received"]
            window["base_feature_update_count"] = window["packets_received"]
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r4_24h.window.100.continuity", result["errors"])
        self.assertIn("r4_24h.drift.throughput", result["errors"])

    def test_duplicate_repeat_identity_blocks_campaign(self):
        receipts = campaign()
        receipts[1]["identity"]["run_bundle_identity"] = receipts[0]["identity"]["run_bundle_identity"]
        result = aggregate_stage_evidence(receipts, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIsNone(result["derived_production_pareto_metrics"])
        self.assertIn("campaign.independence.run_bundle_identity", result["errors"])

    def test_contract_hash_binding_is_mandatory(self):
        receipt = make_receipt("r1")
        receipt["identity"]["contract_sha256"] = digest(9999)
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r1.identity.contract_sha256", result["errors"])

    def test_resources_and_fallback_must_overlap_the_same_run(self):
        receipt = make_receipt("r3")
        receipt["resource_samples"][0]["timestamp_unix_ns"] -= 10_000_000_000
        receipt["fallback_trials"][0]["fault_injected_unix_ns"] -= 10_000_000_000
        receipt["fallback_trials"][0]["recovery_completed_unix_ns"] -= 10_000_000_000
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r3.resource_sample.0.run_window", result["errors"])
        self.assertIn("r3.fallback_trial.0.recovery_ns", result["errors"])

    def test_duplicate_fallback_trial_cannot_satisfy_repeat_count(self):
        receipt = make_receipt("r3")
        receipt["fallback_trials"][1] = copy.deepcopy(receipt["fallback_trials"][0])
        result = validate_stage_receipt(receipt, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("r3.fallback_trial.1.trial_id", result["errors"])
        self.assertIn("r3.fallback_trial.1.recovery_ns", result["errors"])
        self.assertIn("r3.fallback_trials.distinct_valid_count", result["errors"])

    def test_fallback_completion_axis_is_unique_increasing_and_non_overlapping(self):
        receipt = make_receipt("r3")
        first = receipt["fallback_trials"][0]
        second = receipt["fallback_trials"][1]
        second["fault_injected_unix_ns"] = first["fault_injected_unix_ns"] + 100_000_000
        second["recovery_completed_unix_ns"] = first["recovery_completed_unix_ns"]
        second["recovery_ns"] = 100_000_000

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn(
            "r3.fallback_trial.1.recovery_completed_unix_ns", result["errors"]
        )
        self.assertIn("r3.fallback_trial.1.overlap", result["errors"])
        self.assertIn("r3.fallback_trials.distinct_valid_count", result["errors"])

    def test_hash_self_consistent_dummy_code_manifest_is_rejected(self):
        receipt = make_receipt("r1")
        dummy = {"code": "frozen"}
        receipt["identity_manifests"]["code"] = dummy
        receipt["identity"]["code_sha256"] = canonical_digest(dummy)

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn("r1.identity_manifest.code.fields", result["errors"])
        self.assertIn("r1.identity_manifest.code.schema", result["errors"])

    def test_model_provenance_must_bind_the_input_manifest(self):
        receipt = make_receipt("r3")
        receipt["identity_manifests"]["model"][
            "training_input_manifest_sha256"
        ] = digest(9991)

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn("r3.identity_manifest.model.training_input", result["errors"])

    def test_input_source_manifest_requires_addressable_content_provenance(self):
        receipt = make_receipt("r2")
        input_document = receipt["identity_manifests"]["input"]
        input_document["sources"] = [{"source_id": "dummy"}]
        input_document["source_set_sha256"] = canonical_digest(
            input_document["sources"]
        )

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn(
            "r2.identity_manifest.input.sources.0.fields", result["errors"]
        )
        self.assertIn(
            "r2.identity_manifest.input.sources.0.provenance_uri", result["errors"]
        )

    def test_model_manifest_requires_a_nonempty_hashed_artifact_set(self):
        receipt = make_receipt("r3")
        model = receipt["identity_manifests"]["model"]
        model["artifacts"] = []
        model["artifact_set_sha256"] = canonical_digest([])

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn("r3.identity_manifest.model.artifacts", result["errors"])

    def test_runtime_capture_component_must_bind_capture_binary(self):
        receipt = make_receipt("r3")
        runtime = receipt["identity_manifests"]["runtime"]
        runtime["components"][1]["binary_sha256"] = digest(9992)
        runtime["component_set_sha256"] = canonical_digest(runtime["components"])

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn(
            "r3.identity_manifest.runtime.capture_component", result["errors"]
        )

    def test_stage_config_must_cross_bind_the_runtime_manifest(self):
        receipt = make_receipt("r2")
        receipt["identity_manifests"]["stage_config"][
            "runtime_manifest_sha256"
        ] = digest(9993)

        result = validate_stage_receipt(receipt, CONTRACT)

        self.assertFalse(result["qualified"])
        self.assertIn(
            "r2.identity_manifest.stage_config.runtime_manifest_sha256",
            result["errors"],
        )

    def test_input_hash_is_frozen_across_stages(self):
        receipts = campaign()
        receipts[-1]["identity"]["input_sha256"] = digest(9998)
        result = aggregate_stage_evidence(receipts, CONTRACT)
        self.assertFalse(result["qualified"])
        self.assertIn("campaign.identity.input_sha256", result["errors"])


if __name__ == "__main__":
    unittest.main()
