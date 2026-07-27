from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


ECE = "ece"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def create_protocol(
    base: dict[str, Any],
    coverage: dict[str, Any],
    *,
    base_file_sha256: str,
    coverage_file_sha256: str,
    summarizer_sha256: str,
    auditor_sha256: str,
    authority_summary_count_at_freeze: int,
    suite_audit_count_at_freeze: int,
) -> dict[str, Any]:
    if (
        base.get("schema_version")
        != "strict_v4_postselection_corruption_protocol_v1"
        or base.get("manifest_sha256") != canonical_hash(base)
    ):
        raise ValueError("invalid base corruption protocol")
    if (
        coverage.get("schema_version") != "strict_v4_coverage_manifest_v2"
        or coverage.get("manifest_sha256") != canonical_hash(coverage)
    ):
        raise ValueError("invalid coverage manifest")
    if base.get("coverage_manifest_sha256") != coverage["manifest_sha256"]:
        raise ValueError("base protocol coverage binding mismatch")
    if int(authority_summary_count_at_freeze) != 0:
        raise ValueError("suite gate must freeze before the authority summary")
    if int(suite_audit_count_at_freeze) != 0:
        raise ValueError("suite gate must freeze before suite audit output")

    registry = coverage.get("scenario_registry")
    if not isinstance(registry, dict) or len(registry) != 7:
        raise ValueError("seven-suite scenario registry is required")
    suite_counts: dict[str, int] = {}
    for suite, record in sorted(registry.items()):
        if not isinstance(record, dict):
            raise ValueError(f"invalid coverage record: {suite}")
        scenarios = record.get("scenarios")
        count = record.get("count")
        if (
            not isinstance(scenarios, list)
            or not isinstance(count, int)
            or count <= 0
            or len(scenarios) != count
            or len(set(scenarios)) != count
        ):
            raise ValueError(f"invalid scenario registry: {suite}")
        suite_counts[suite] = count
    if sum(suite_counts.values()) != 102:
        raise ValueError("suite scenario counts must sum to 102")

    reported = base.get("reported_metrics")
    if not isinstance(reported, list) or ECE not in reported:
        raise ValueError("base protocol must report ECE")
    thresholds = base.get("confirmatory_graceful_degradation_gate", {}).get(
        "maximum_mean_degradation"
    )
    if not isinstance(thresholds, dict) or not thresholds:
        raise ValueError("base frozen degradation thresholds are missing")
    if ECE in thresholds:
        raise ValueError("unexpected ECE threshold in the base protocol")
    if set(thresholds) != set(reported) - {ECE}:
        raise ValueError("reported and thresholded metric sets are inconsistent")

    families = base.get("full102_confirmation", {}).get(
        "corruption_families"
    )
    if not isinstance(families, list) or len(families) != 5:
        raise ValueError("five frozen corruption families are required")

    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_postselection_corruption_suite_gate_protocol_v1"
        ),
        "status": "frozen_before_authority_summary_without_effect_read",
        "effect_metrics_read": False,
        "authority_summary_count_at_freeze": 0,
        "suite_audit_count_at_freeze": 0,
        "selected_algorithm_anchor": base["selected_algorithm"],
        "base_protocol_manifest_sha256": base["manifest_sha256"],
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "input_file_sha256": {
            "base_protocol": base_file_sha256,
            "coverage_manifest": coverage_file_sha256,
        },
        "implementation_sha256": {
            "summarizer": summarizer_sha256,
            "suite_auditor": auditor_sha256,
        },
        "suite_scenario_counts": suite_counts,
        "expected_full102_runs": 102 * len(families),
        "corruption_families": families,
        "reported_metrics": reported,
        "thresholded_metrics": list(thresholds),
        "descriptive_metrics_without_frozen_threshold": [ECE],
        "maximum_mean_degradation": thresholds,
        "gate_contract": {
            "unit": "corruption_family_x_dataset_suite",
            "all_175_frozen_threshold_checks_must_pass": True,
            "threshold_check_count": (
                len(families) * len(suite_counts) * len(thresholds)
            ),
            "ece_suite_value_count": len(families) * len(suite_counts),
            "ece_must_be_finite_and_reported": True,
            "ece_is_not_thresholded_because_no_threshold_was_frozen": True,
            "aggregate_family_gate_must_also_pass": True,
            "auditor_recomputes_from_all_full102_wrappers": True,
            "no_threshold_tuning_or_condition_selection": True,
        },
        "claim_policy": {
            "aggregate_family_means_cannot_substitute_for_suite_gates": True,
            "failed_suite_gate_must_be_reported_as_negative_result": True,
            "no_suite_robustness_superlative_without_complete_gate": True,
            "does_not_upgrade_ece_to_a_confirmatory_metric": True,
        },
    }
    if value["gate_contract"]["threshold_check_count"] != 175:
        raise ValueError("expected exactly 175 frozen suite threshold checks")
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--summarizer", type=Path, required=True)
    parser.add_argument("--auditor", type=Path, required=True)
    parser.add_argument("--authority-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    authority_count = int(args.authority_summary.exists())
    suite_audit_count = int((args.output.parent / "audit.json").exists())
    value = create_protocol(
        load(args.base_protocol),
        load(args.coverage),
        base_file_sha256=file_hash(args.base_protocol),
        coverage_file_sha256=file_hash(args.coverage),
        summarizer_sha256=file_hash(args.summarizer),
        auditor_sha256=file_hash(args.auditor),
        authority_summary_count_at_freeze=authority_count,
        suite_audit_count_at_freeze=suite_audit_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
