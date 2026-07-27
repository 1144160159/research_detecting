from __future__ import annotations

import unittest

from audit_strict_v4_postselection_corruption_suite_gate import (
    create_audit,
    wrapper_record_hash,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_postselection_corruption_suite_gate_protocol import (
    create_protocol,
)


FAMILIES = ["a", "b", "c", "d", "e"]
SUITES = {
    "suite_0": 32,
    "suite_1": 9,
    "suite_2": 14,
    "suite_3": 14,
    "suite_4": 14,
    "suite_5": 9,
    "suite_6": 10,
}
THRESHOLDS = {
    "known_macro_f1": 0.10,
    "unknown_auroc": 0.15,
    "unknown_aupr": 0.15,
    "unknown_fpr95": 0.20,
    "oscr": 0.15,
}
METRICS = [*THRESHOLDS, "ece"]


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs() -> tuple[dict, dict]:
    coverage = canonical(
        {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "scenario_registry": {
                suite: {
                    "count": count,
                    "scenarios": [f"x_{index}" for index in range(count)],
                }
                for suite, count in SUITES.items()
            },
        }
    )
    base = canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_protocol_v1"
            ),
            "selected_algorithm": "caeos_pairwise",
            "coverage_manifest_sha256": coverage["manifest_sha256"],
            "reported_metrics": METRICS,
            "full102_confirmation": {"corruption_families": FAMILIES},
            "confirmatory_graceful_degradation_gate": {
                "maximum_mean_degradation": THRESHOLDS
            },
        }
    )
    return base, coverage


def suite_protocol(base: dict, coverage: dict) -> dict:
    protocol = create_protocol(
        base,
        coverage,
        base_file_sha256="1" * 64,
        coverage_file_sha256="2" * 64,
        summarizer_sha256="3" * 64,
        auditor_sha256="4" * 64,
        authority_summary_count_at_freeze=0,
        suite_audit_count_at_freeze=0,
    )
    return protocol


def summary(base: dict, value: float = 0.0) -> dict:
    return canonical(
        {
            "schema_version": (
                "strict_v4_postselection_corruption_summary_v1"
            ),
            "status": "complete",
            "protocol_manifest_sha256": base["manifest_sha256"],
            "validation": {
                "expected_runs": 783,
                "observed_runs": 783,
                "full102_runs": 510,
                "passes": True,
            },
            "full102_confirmation": {
                family: {
                    "by_suite_mean_degradation": {
                        suite: {metric: value for metric in METRICS}
                        for suite in SUITES
                    }
                }
                for family in FAMILIES
            },
            "confirmatory_gate": {"passes": True},
        }
    )


def observed(value: float = 0.0) -> dict:
    return {
        family: {
            suite: {
                metric: [value] * count for metric in METRICS
            }
            for suite, count in SUITES.items()
        }
        for family in FAMILIES
    }


class CorruptionSuiteGateTests(unittest.TestCase):
    def test_wrapper_hash_excludes_its_self_field(self) -> None:
        wrapper = {"schema_version": "x", "value": 1}
        wrapper["record_sha256"] = canonical_hash(wrapper)
        self.assertEqual(
            wrapper["record_sha256"], wrapper_record_hash(wrapper)
        )

    def test_protocol_preserves_ece_as_descriptive(self) -> None:
        base, coverage = inputs()
        protocol = create_protocol(
            base,
            coverage,
            base_file_sha256="1" * 64,
            coverage_file_sha256="2" * 64,
            summarizer_sha256="3" * 64,
            auditor_sha256="4" * 64,
            authority_summary_count_at_freeze=0,
            suite_audit_count_at_freeze=0,
        )
        self.assertEqual(protocol["thresholded_metrics"], list(THRESHOLDS))
        self.assertEqual(
            protocol["descriptive_metrics_without_frozen_threshold"],
            ["ece"],
        )
        self.assertEqual(
            protocol["gate_contract"]["threshold_check_count"], 175
        )

    def test_protocol_rejects_post_summary_freeze(self) -> None:
        base, coverage = inputs()
        with self.assertRaisesRegex(ValueError, "before the authority"):
            create_protocol(
                base,
                coverage,
                base_file_sha256="1" * 64,
                coverage_file_sha256="2" * 64,
                summarizer_sha256="3" * 64,
                auditor_sha256="4" * 64,
                authority_summary_count_at_freeze=1,
                suite_audit_count_at_freeze=0,
            )

    def test_all_suite_thresholds_can_pass(self) -> None:
        base, coverage = inputs()
        result = create_audit(
            protocol=suite_protocol(base, coverage),
            base=base,
            coverage=coverage,
            summary=summary(base),
            values=observed(),
        )
        self.assertTrue(result["passes"])
        self.assertEqual(
            result["validation"]["suite_threshold_checks"], 175
        )

    def test_one_bad_suite_blocks_gate(self) -> None:
        base, coverage = inputs()
        values = observed()
        values["a"]["suite_0"]["known_macro_f1"] = [0.11] * SUITES[
            "suite_0"
        ]
        authority = summary(base)
        authority["full102_confirmation"]["a"][
            "by_suite_mean_degradation"
        ]["suite_0"]["known_macro_f1"] = 0.11
        authority["manifest_sha256"] = canonical_hash(authority)
        result = create_audit(
            protocol=suite_protocol(base, coverage),
            base=base,
            coverage=coverage,
            summary=authority,
            values=values,
        )
        self.assertFalse(result["passes"])
        self.assertFalse(result["all_175_suite_threshold_checks_pass"])


if __name__ == "__main__":
    unittest.main()
