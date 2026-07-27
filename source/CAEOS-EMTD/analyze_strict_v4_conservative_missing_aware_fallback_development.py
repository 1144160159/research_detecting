from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analyze_strict_v4_missing_aware_fallback_development import (
    CANDIDATE_RISK,
    METRICS,
    degradation,
    report_metrics,
    summarize,
)
from audit_strict_v4_postselection_corruption_suite_gate import (
    load,
    wrapper_record_hash,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_postselection_corruption import build_tasks, task_key


CONSERVATIVE_CANDIDATE = (
    "selected_risk_compatible_missing_aware_fallback_v1"
)


def should_activate(selected_risk: str) -> bool:
    return selected_risk == "cauchy_modality_support_union"


def require(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"invalid {label}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--base-protocol", type=Path, required=True)
    parser.add_argument("--suite-protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--authority-summary", type=Path, required=True)
    parser.add_argument("--suite-audit", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    base, protocol, coverage = (
        load(args.base_protocol),
        load(args.suite_protocol),
        load(args.coverage),
    )
    authority, suite_audit = (
        load(args.authority_summary),
        load(args.suite_audit),
    )
    for value, schema, label in (
        (
            base,
            "strict_v4_postselection_corruption_protocol_v1",
            "base protocol",
        ),
        (
            protocol,
            "strict_v4_postselection_corruption_suite_gate_protocol_v1",
            "suite protocol",
        ),
        (
            coverage,
            "strict_v4_coverage_manifest_v2",
            "coverage",
        ),
        (
            authority,
            "strict_v4_postselection_corruption_summary_v1",
            "authority summary",
        ),
        (
            suite_audit,
            "strict_v4_postselection_corruption_suite_gate_audit_v1",
            "suite audit",
        ),
    ):
        require(value, schema, label)
    if (
        authority.get("confirmatory_gate", {}).get("passes") is not False
        or suite_audit.get("passes") is not False
    ):
        raise ValueError("development requires completed negative gates")

    candidate: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    incumbent: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    clean_differences = {metric: [] for metric in METRICS}
    activation_by_family: Counter[str] = Counter()
    activation_by_suite: Counter[str] = Counter()
    observed = 0
    for task in build_tasks(base, coverage):
        if task.tier != "full102":
            continue
        wrapper_path = (
            args.run_root / task_key(task) / "corruption_metrics.json"
        )
        wrapper = load(wrapper_path)
        if (
            wrapper.get("record_sha256") != wrapper_record_hash(wrapper)
            or wrapper.get("validation_passes") is not True
            or wrapper.get(
                "unknown_or_test_labels_used_for_generation_fitting_or_selection"
            )
            is not False
            or wrapper.get("task") != task.__dict__
        ):
            raise ValueError(f"invalid wrapper: {wrapper_path}")
        metrics_path = Path(wrapper["metrics_path"])
        clean_path = (
            project
            / base["clean_anchor"]["root"]
            / task.suite
            / f"{task.scenario}_seed7"
            / "metrics.json"
        )
        if (
            file_hash(metrics_path) != wrapper["metrics_sha256"]
            or file_hash(clean_path) != wrapper["clean_metrics_sha256"]
        ):
            raise ValueError(f"metric SHA mismatch: {wrapper_path}")
        corrupted, clean = load(metrics_path), load(clean_path)
        if corrupted.get("selected_risk") != clean.get("selected_risk"):
            raise ValueError("test-only corruption changed selected risk")
        activated = should_activate(str(clean.get("selected_risk")))
        if activated:
            diagnostics = corrupted.get("missing_aware_diagnostics", {})
            if (
                diagnostics.get("uses_unknown_or_test_labels") is not False
                or CANDIDATE_RISK not in corrupted.get("reports", {})
            ):
                raise ValueError("missing-aware activation contract failed")
            corrupted_candidate = report_metrics(
                corrupted["reports"][CANDIDATE_RISK]
            )
            activation_by_family[task.corruption] += 1
            activation_by_suite[task.suite] += 1
        else:
            corrupted_candidate = report_metrics(
                corrupted["selected_report"]
            )
        corrupted_incumbent = report_metrics(corrupted["selected_report"])
        clean_incumbent = report_metrics(clean["selected_report"])
        clean_candidate = clean_incumbent
        for metric in METRICS:
            candidate[task.corruption][task.suite][metric].append(
                degradation(
                    clean_candidate, corrupted_candidate, metric
                )
            )
            incumbent[task.corruption][task.suite][metric].append(
                degradation(
                    clean_incumbent, corrupted_incumbent, metric
                )
            )
            clean_differences[metric].append(0.0)
        observed += 1

    result = summarize(
        protocol=protocol,
        suite_counts=protocol["suite_scenario_counts"],
        candidate=candidate,
        incumbent=incumbent,
        clean_differences=clean_differences,
        observed_runs=observed,
    )
    result["candidate_risk"] = CONSERVATIVE_CANDIDATE
    result.update(
        {
            "schema_version": (
                "strict_v4_conservative_missing_aware_fallback_"
                "development_analysis_v1"
            ),
            "status": "complete_posthoc_development_only",
            "posthoc_development_only": True,
            "scenario_activation_rule": (
                "activate only when frozen known-only selected_risk equals "
                "cauchy_modality_support_union"
            ),
            "activation_uses_test_labels_or_unknown_indicator": False,
            "activated_full102_runs": sum(activation_by_family.values()),
            "activation_by_family": dict(activation_by_family),
            "activation_by_suite": dict(activation_by_suite),
            "new_seed_confirmation_required": True,
            "validation": {
                "expected_runs": 510,
                "observed_runs": observed,
                "clean_fallback_constructed_exactly": True,
                "passes": observed == 510,
            },
            "input_manifest_sha256": {
                "base_protocol": base["manifest_sha256"],
                "suite_protocol": protocol["manifest_sha256"],
                "authority_summary": authority["manifest_sha256"],
                "suite_audit": suite_audit["manifest_sha256"],
            },
            "claim_boundary": {
                "cannot_relabel_seed7_as_confirmation": True,
                "cannot_change_existing_negative_robustness_result": True,
                "candidate_is_not_the_final_selected_algorithm": True,
                "fresh_training_and_corruption_seeds_required": True,
            },
        }
    )
    result["analysis_implementation_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    result["manifest_sha256"] = canonical_hash(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["decision"])


if __name__ == "__main__":
    main()
