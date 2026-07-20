from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from summarize_neural_comparison_strict_v2 import (
    REPORT_METRICS,
    build_report,
    extract_report_resource_usage,
    parse_inference_seeds,
    validate_split_fingerprint,
)


def split_fingerprint(tag: str) -> dict[str, object]:
    fingerprint: dict[str, object] = {
        "schema_version": "1.0",
        "algorithm": "sha256_over_ordered_canonical_pandas_row_hashes",
        "columns": ["feature", "Label"],
        "train": hashlib.sha256(f"{tag}:train".encode()).hexdigest(),
        "validation": hashlib.sha256(f"{tag}:validation".encode()).hexdigest(),
        "test": hashlib.sha256(f"{tag}:test".encode()).hexdigest(),
    }
    combined = hashlib.sha256()
    for name in ("train", "validation", "test"):
        combined.update(name.encode("ascii"))
        combined.update(str(fingerprint[name]).encode("ascii"))
    fingerprint["combined"] = combined.hexdigest()
    return fingerprint


def report(gate_value: float, gate_fpr95: float) -> dict[str, float]:
    values = {metric: gate_value for metric in REPORT_METRICS}
    values["unknown_fpr95"] = gate_fpr95
    return values


def shared_metrics(seed: int, fingerprint: dict[str, object]) -> dict[str, object]:
    return {
        "unknown_classes": "Attack",
        "seed": seed,
        "known_class_names": ["Normal", "KnownAttack"],
        "sample_counts": {"Normal": 100, "KnownAttack": 100, "Attack": 100},
        "split_sizes": {
            "train": 120,
            "validation": 40,
            "test": 140,
            "test_unknown": 100,
        },
        "split_metadata": {
            "strategy": "fingerprint_grouped",
            "split_fingerprint": fingerprint,
        },
        "arguments": {
            "csv": "cache.csv",
            "config": "configs/edge_iiot.json",
            "split_strategy": "fingerprint_grouped",
            "max_per_class": 1000,
            "benign_class": "Normal",
        },
    }


def gate_metrics(
    seed: int,
    fingerprint: dict[str, object],
    gate_value: float = 0.6,
) -> dict[str, object]:
    return {
        **shared_metrics(seed, fingerprint),
        "risk_selection": "nested_density_reliability_gate",
        "selected_risk": "density_reliability_blend",
        "selected_report": report(gate_value, 1.0 - gate_value),
    }


def policy_gate_metrics(
    seed: int,
    fingerprint: dict[str, object],
    risk_selection: str,
    policy: str,
) -> dict[str, object]:
    payload = gate_metrics(seed, fingerprint)
    payload["risk_selection"] = risk_selection
    payload["risk_policy"] = policy
    payload["arguments"]["risk_selection"] = risk_selection
    payload["arguments"]["risk_policy"] = policy
    return payload


def neural_metrics(
    seed: int,
    fingerprint: dict[str, object],
    baseline_value: float,
    training_seconds: Optional[float] = None,
    method: str = "sieve",
) -> dict[str, object]:
    payload = {
        **shared_metrics(seed, fingerprint),
        "reports": {
            method: report(baseline_value, 1.0 - baseline_value),
        },
    }
    if training_seconds is not None:
        payload["training_seconds"] = training_seconds
    return payload


def write_metrics(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_provenance(
    metrics_path: Path, csv_sha: str, config_sha: str
) -> None:
    payload = {
        "inputs": {
            "csv": {
                "sidecar_sha": {
                    "declared_sha256": csv_sha,
                    "sidecar_file_sha256": hashlib.sha256(
                        f"sidecar:{csv_sha}".encode()
                    ).hexdigest(),
                }
            },
            "config": {"sha256": config_sha},
        }
    }
    write_metrics(metrics_path.parent / "provenance.json", payload)


class StrictV2ComparisonTests(unittest.TestCase):
    def test_report_specific_resources_override_shared_job_total(self) -> None:
        payload = {
            "training_seconds": 30.0,
            "resource_usage_by_report": {
                "isolation_forest": {"training_seconds": 12.0},
                "one_class_svm": {"training_seconds": 18.0},
            },
        }
        isolation = extract_report_resource_usage(
            payload, Path("metrics.json"), "isolation_forest"
        )
        ocsvm = extract_report_resource_usage(
            payload, Path("metrics.json"), "one_class_svm"
        )
        self.assertEqual(12.0, isolation["training_seconds"]["value"])
        self.assertEqual(18.0, ocsvm["training_seconds"]["value"])
        self.assertEqual("missing", isolation["inference_seconds"]["status"])
        with self.assertRaisesRegex(ValueError, "missing resource usage"):
            extract_report_resource_usage(payload, Path("metrics.json"), "lof")

    def test_parse_inference_seeds_is_strict(self) -> None:
        self.assertEqual(parse_inference_seeds(None), None)
        self.assertEqual(parse_inference_seeds("23,11,19"), (11, 19, 23))
        for invalid in ("", "11,", "11,x", "11,11", "-1,11"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    parse_inference_seeds(invalid)

    def write_task(
        self,
        root: Path,
        scenario: str,
        seed: int,
        baseline_value: float,
        training_seconds: Optional[float],
        neural_fingerprint: Optional[dict[str, object]] = None,
        method: str = "sieve",
    ) -> tuple[Path, Path]:
        gate_root = root / "gate"
        neural_root = root / "neural"
        fingerprint = split_fingerprint(f"{scenario}:{seed}")
        write_metrics(
            gate_root / "edge" / f"{scenario}_seed{seed}" / "metrics.json",
            gate_metrics(seed, fingerprint),
        )
        write_metrics(
            neural_root
            / f"{scenario}_seed{seed}_{method}"
            / "metrics.json",
            neural_metrics(
                seed,
                neural_fingerprint or fingerprint,
                baseline_value,
                training_seconds,
                method,
            ),
        )
        return gate_root, neural_root

    def test_scenario_is_inference_unit_and_seed_is_repeated_measurement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root = neural_root = None
            for seed in (7, 11, 23):
                gate_root, neural_root = self.write_task(
                    root,
                    "frequent",
                    seed,
                    baseline_value=0.5,
                    training_seconds=10.0,
                )
            gate_root, neural_root = self.write_task(
                root,
                "sparse",
                7,
                baseline_value=0.8,
                training_seconds=None,
            )
            assert gate_root is not None and neural_root is not None

            result = build_report(
                gate_root,
                {"edge": [neural_root]},
                bootstrap_repetitions=500,
                bootstrap_seed=19,
            )

        summary = result["global"]
        inference = summary["methods"]["sieve"]["metrics"]["unknown_auroc"][
            "paired_inference"
        ]
        self.assertEqual(summary["scenario_inference_units"], 2)
        self.assertEqual(summary["scenario_seed_counts"], {
            "edge/frequent": 3,
            "edge/sparse": 1,
        })
        self.assertAlmostEqual(inference["mean_delta"], -0.05)
        self.assertAlmostEqual(inference["bootstrap_95_ci"]["lower"], -0.2)
        self.assertAlmostEqual(inference["bootstrap_95_ci"]["upper"], 0.1)
        self.assertEqual(inference["wins"], 1)
        self.assertEqual(inference["losses"], 1)
        self.assertEqual(
            inference["effect_sizes"]["paired_cohens_dz"]["status"],
            "computed",
        )
        self.assertAlmostEqual(
            inference["effect_sizes"]["matched_pairs_rank_biserial"]["value"],
            -1.0 / 3.0,
        )
        self.assertIsNotNone(
            inference["wilcoxon"]["holm_adjusted_p_value"]
        )

    def test_development_seed_is_validated_but_excluded_from_inference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root = neural_root = None
            for seed, baseline_value in ((7, 0.1), (11, 0.5), (19, 0.7)):
                gate_root, neural_root = self.write_task(
                    root,
                    "attack",
                    seed,
                    baseline_value=baseline_value,
                    training_seconds=10.0,
                )
            assert gate_root is not None and neural_root is not None
            result = build_report(
                gate_root,
                {"edge": [neural_root]},
                bootstrap_repetitions=100,
                inference_seeds=(11, 19),
            )

        protocol = result["inference_protocol"]
        self.assertEqual(protocol["validated_seeds"], [7, 11, 19])
        self.assertEqual(protocol["inference_seeds"], [11, 19])
        self.assertEqual(protocol["excluded_from_inference_seeds"], [7])
        self.assertEqual(protocol["validated_run_count"], 3)
        self.assertEqual(protocol["inference_run_count"], 2)
        self.assertEqual(result["global"]["run_count"], 2)
        coverage = result["coverage_validation"]["edge"]
        self.assertEqual(coverage["validated_task_count"], 3)
        self.assertEqual(coverage["inference_task_count"], 2)
        metric = result["global"]["methods"]["sieve"]["metrics"][
            "unknown_auroc"
        ]
        self.assertAlmostEqual(metric["baseline_scenario_mean"], 0.6)

    def test_each_suite_must_cover_every_requested_inference_seed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root, neural_root = self.write_task(
                root, "attack", 7, baseline_value=0.5, training_seconds=None
            )
            with self.assertRaisesRegex(ValueError, "inference seed coverage mismatch"):
                build_report(
                    gate_root,
                    {"edge": [neural_root]},
                    bootstrap_repetitions=100,
                    inference_seeds=(11,),
                )

    def test_suite_conditional_gate_policy_allows_different_effective_risks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root = root / "gate"
            neural_roots: dict[str, list[Path]] = {}
            policy = "frozen_density_edge_only_v1"
            for suite, risk_selection in (
                ("edge", "nested_density_reliability_gate"),
                ("nf_cse", "nested_hierarchical_joint_gate"),
            ):
                fingerprint = split_fingerprint(f"{suite}:attack:7")
                write_metrics(
                    gate_root / suite / "attack_seed7" / "metrics.json",
                    policy_gate_metrics(
                        7, fingerprint, risk_selection, policy
                    ),
                )
                neural_root = root / f"neural_{suite}"
                write_metrics(
                    neural_root / "attack_seed7_sieve" / "metrics.json",
                    neural_metrics(7, fingerprint, 0.5),
                )
                neural_roots[suite] = [neural_root]
            result = build_report(
                gate_root,
                neural_roots,
                bootstrap_repetitions=100,
            )

        self.assertEqual(result["global"]["gate_method"], policy)
        self.assertEqual(
            result["global"]["gate_effective_risk_selections"],
            [
                "nested_density_reliability_gate",
                "nested_hierarchical_joint_gate",
            ],
        )

    def test_explicit_composite_policy_preserves_source_policies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root = root / "gate"
            neural_roots: dict[str, list[Path]] = {}
            for suite, policy in (("edge", "edge_policy"), ("nf", "nf_policy")):
                fingerprint = split_fingerprint(f"{suite}:attack:7")
                write_metrics(
                    gate_root / suite / "attack_seed7" / "metrics.json",
                    policy_gate_metrics(7, fingerprint, "fixed_risk", policy),
                )
                neural_root = root / f"neural_{suite}"
                write_metrics(
                    neural_root / "attack_seed7_sieve" / "metrics.json",
                    neural_metrics(7, fingerprint, 0.5),
                )
                neural_roots[suite] = [neural_root]
            with self.assertRaisesRegex(ValueError, "inconsistent gate methods"):
                build_report(
                    gate_root, neural_roots, bootstrap_repetitions=100
                )
            result = build_report(
                gate_root,
                neural_roots,
                bootstrap_repetitions=100,
                gate_policy_name="confirmed_composite_v1",
            )

        self.assertEqual(result["global"]["gate_method"], "confirmed_composite_v1")
        self.assertEqual(
            result["global"]["gate_source_methods"],
            ["edge_policy", "nf_policy"],
        )

    def test_resource_missingness_is_explicit_and_never_imputed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root, neural_root = self.write_task(
                root, "a", 7, baseline_value=0.5, training_seconds=12.0
            )
            self.write_task(
                root, "b", 7, baseline_value=0.5, training_seconds=None
            )
            for scenario, inference_seconds, memory_mb in (
                ("a", 0.25, 512.0),
                ("b", 0.50, 768.0),
            ):
                metrics_path = (
                    neural_root / f"{scenario}_seed7_sieve" / "metrics.json"
                )
                payload = json.loads(metrics_path.read_text(encoding="utf-8"))
                payload["inference_seconds"] = inference_seconds
                payload["peak_gpu_memory_mb"] = memory_mb
                write_metrics(metrics_path, payload)
            result = build_report(
                gate_root,
                {"edge": [neural_root]},
                bootstrap_repetitions=100,
            )

        resources = result["global"]["resource_summary"]
        self.assertEqual(resources["gate"]["training_seconds"]["status"], "missing")
        self.assertIsNone(
            resources["gate"]["training_seconds"]["descriptive"]
        )
        neural_training = resources["sieve"]["training_seconds"]
        self.assertEqual(neural_training["status"], "partially_recorded")
        self.assertEqual(neural_training["recorded_count"], 1)
        self.assertEqual(neural_training["missing_count"], 1)
        self.assertEqual(neural_training["descriptive"]["mean"], 12.0)
        inference = resources["sieve"]["inference_seconds"]
        self.assertEqual(inference["status"], "recorded")
        self.assertEqual(inference["descriptive"]["mean"], 0.375)
        memory = resources["sieve"]["peak_gpu_memory_mb"]
        self.assertEqual(memory["status"], "recorded")
        self.assertEqual(memory["descriptive"]["mean"], 640.0)

    def test_every_neural_root_must_cover_authoritative_gate_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root, neural_root = self.write_task(
                root, "a", 7, baseline_value=0.5, training_seconds=None
            )
            fingerprint = split_fingerprint("b:7")
            write_metrics(
                gate_root / "edge" / "b_seed7" / "metrics.json",
                gate_metrics(7, fingerprint),
            )

            with self.assertRaisesRegex(ValueError, "task coverage mismatch"):
                build_report(
                    gate_root,
                    {"edge": [neural_root]},
                    bootstrap_repetitions=100,
                )

    def test_split_fingerprint_must_match_and_be_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root, neural_root = self.write_task(
                root,
                "a",
                7,
                baseline_value=0.5,
                training_seconds=None,
                neural_fingerprint=split_fingerprint("different"),
            )
            with self.assertRaisesRegex(ValueError, "split_fingerprint"):
                build_report(
                    gate_root,
                    {"edge": [neural_root]},
                    bootstrap_repetitions=100,
                )

            invalid = gate_metrics(7, split_fingerprint("invalid"))
            invalid["split_metadata"]["split_fingerprint"]["combined"] = "0" * 64
            path = root / "invalid.json"
            write_metrics(path, invalid)
            with self.assertRaisesRegex(ValueError, "not reproducible"):
                validate_split_fingerprint(invalid, path)

    def test_path_arguments_use_provenance_content_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root, neural_root = self.write_task(
                root, "a", 7, baseline_value=0.5, training_seconds=None
            )
            gate_path = gate_root / "edge" / "a_seed7" / "metrics.json"
            neural_path = neural_root / "a_seed7_sieve" / "metrics.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            neural = json.loads(neural_path.read_text(encoding="utf-8"))
            gate["arguments"]["csv"] = "/snapshot-a/cache.csv"
            gate["arguments"]["config"] = "/snapshot-a/config.json"
            neural["arguments"]["csv"] = "/snapshot-b/cache.csv"
            neural["arguments"]["config"] = "/snapshot-b/config.json"
            write_metrics(gate_path, gate)
            write_metrics(neural_path, neural)

            csv_sha = hashlib.sha256(b"same-cache").hexdigest()
            config_sha = hashlib.sha256(b"same-config").hexdigest()
            write_provenance(gate_path, csv_sha, config_sha)
            write_provenance(neural_path, csv_sha, config_sha)
            result = build_report(
                gate_root,
                {"edge": [neural_root]},
                bootstrap_repetitions=100,
            )
            self.assertEqual(result["global"]["run_count"], 1)

            write_provenance(
                neural_path,
                csv_sha,
                hashlib.sha256(b"different-config").hexdigest(),
            )
            with self.assertRaisesRegex(ValueError, "arguments.config"):
                build_report(
                    gate_root,
                    {"edge": [neural_root]},
                    bootstrap_repetitions=100,
                )

    def test_method_level_coverage_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_root, neural_root = self.write_task(
                root, "a", 7, baseline_value=0.5, training_seconds=None
            )
            self.write_task(
                root,
                "b",
                7,
                baseline_value=0.5,
                training_seconds=None,
                method="opendetect",
            )
            with self.assertRaisesRegex(ValueError, "task coverage mismatch"):
                build_report(
                    gate_root,
                    {"edge": [neural_root]},
                    bootstrap_repetitions=100,
                )


if __name__ == "__main__":
    unittest.main()
