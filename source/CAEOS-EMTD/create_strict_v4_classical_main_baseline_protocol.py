from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SOURCE_SUMMARY_SHA256 = (
    "2919a4fc34cc256ded0f308f606df1cda29b78f0c6121a8ab2125dcf139bf75e"
)
SOURCE_SCHEMA = "strict_v4_mahalanobis_pp_29method_screen_v1"
EXPECTED_SUITES = (
    "cic_iot2023",
    "cic_ton_iot",
    "cicids2017",
    "edge_iiot",
    "nf_cse",
    "nf_unsw",
    "ustc_tfc2016",
)
METRICS = (
    ("known_macro_f1", "higher"),
    ("unknown_auroc", "higher"),
    ("unknown_aupr", "higher"),
    ("unknown_fpr95", "lower"),
    ("oscr", "higher"),
)
MAIN_BASELINES = (
    {
        "display_name": "MSP",
        "method": "mlp_msp",
        "mechanism_family": "maximum_softmax_confidence",
        "selection_role": "historical_confidence_anchor",
    },
    {
        "display_name": "Energy",
        "method": "mlp_energy",
        "mechanism_family": "logit_energy_score",
        "selection_role": "modern_logit_score_anchor",
    },
    {
        "display_name": "OpenMax",
        "method": "mlp_openmax",
        "mechanism_family": "extreme_value_logit_calibration",
        "selection_role": "classical_open_set_calibration_anchor",
    },
    {
        "display_name": "kNN",
        "method": "mlp_knn",
        "mechanism_family": "local_feature_distance",
        "selection_role": "strong_nonparametric_distance_baseline",
    },
    {
        "display_name": "ViM",
        "method": "mlp_vim",
        "mechanism_family": "logit_feature_residual_subspace",
        "selection_role": "feature_logit_hybrid_baseline",
    },
    {
        "display_name": "Mahalanobis++",
        "method": "mahalanobis_pp",
        "mechanism_family": "enhanced_class_conditional_distance",
        "selection_role": "strong_parametric_distance_baseline",
    },
    {
        "display_name": "OpenDetect",
        "method": "opendetect",
        "mechanism_family": "direct_open_set_domain_training",
        "selection_role": "frozen_strongest_external_comparator",
    },
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _validate_metric_row(row: dict[str, Any], method: str) -> None:
    if row.get("method") != method:
        raise ValueError(f"method identity mismatch: {method}")
    for metric, _direction in METRICS:
        value = row.get(metric)
        if not isinstance(value, (int, float)):
            raise ValueError(f"missing numeric {metric}: {method}")
    ranks = row.get("metric_ranks")
    if (
        not isinstance(ranks, dict)
        or set(ranks)
        != {"unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"}
        or not all(isinstance(value, (int, float)) for value in ranks.values())
        or not isinstance(row.get("mean_unknown_metric_rank"), (int, float))
    ):
        raise ValueError(f"invalid rank evidence: {method}")


def validate_source_summary(
    summary: dict[str, Any], summary_file_sha256: str
) -> dict[str, dict[str, Any]]:
    if summary_file_sha256 != SOURCE_SUMMARY_SHA256:
        raise ValueError("authoritative 29-method summary file SHA drifted")
    validation = summary.get("validation", {})
    if (
        summary.get("schema_version") != SOURCE_SCHEMA
        or summary.get("status") != "complete"
        or summary.get("method_count") != 29
        or validation.get("passes") is not True
        or validation.get("scenario_count") != 102
        or validation.get("artifact_checks") != 612
        or validation.get("split_fingerprint_checks") != 102
        or validation.get("failure_count") != 0
        or validation.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError("authoritative 29-method validation boundary drifted")
    by_suite = summary.get("by_suite")
    if not isinstance(by_suite, dict) or tuple(sorted(by_suite)) != EXPECTED_SUITES:
        raise ValueError("authoritative seven-suite coverage drifted")
    overall = summary.get("overall")
    if not isinstance(overall, list) or len(overall) != 29:
        raise ValueError("exactly 29 overall method rows are required")
    rows: dict[str, dict[str, Any]] = {}
    for row in overall:
        if not isinstance(row, dict) or not isinstance(row.get("method"), str):
            raise ValueError("invalid overall method row")
        method = str(row["method"])
        if method in rows:
            raise ValueError(f"duplicate overall method row: {method}")
        _validate_metric_row(row, method)
        rows[method] = row
    selected_methods = {str(item["method"]) for item in MAIN_BASELINES}
    if not selected_methods.issubset(rows):
        missing = sorted(selected_methods.difference(rows))
        raise ValueError(f"missing frozen main baselines: {missing}")
    decision = summary.get("comparator_decision", {})
    if (
        decision.get("selected_comparator") != "opendetect"
        or decision.get("selection_rule")
        != "minimum four-unknown-metric mean rank, then higher AUROC"
        or decision.get("existing_opendetect_protocol_remains_valid")
        is not True
    ):
        raise ValueError("frozen strongest-comparator decision drifted")
    return rows


def create_protocol(
    summary: dict[str, Any],
    *,
    summary_path: Path,
    summary_file_sha256: str,
    implementation_sha256: str,
) -> dict[str, Any]:
    rows = validate_source_summary(summary, summary_file_sha256)
    selected = []
    for definition in MAIN_BASELINES:
        method = str(definition["method"])
        selected.append(
            {
                **definition,
                "overall_evidence": rows[method],
            }
        )
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_classical_main_baseline_protocol_v1",
        "status": "frozen_before_krc_or_rrc_confirmation_outcomes",
        "purpose": (
            "freeze a concise, mechanism-diverse and evidence-backed classical "
            "main table while retaining the complete 29-method screen"
        ),
        "main_table": {
            "baseline_count": len(selected),
            "method_order": [item["method"] for item in selected],
            "baselines": selected,
            "selection_dimensions": [
                "historical recognizability",
                "mechanism-family diversity",
                "strong current comparator coverage",
                "availability under the same strict-v4 protocol",
            ],
            "selection_rule": (
                "retain exactly seven predeclared external baselines; weak "
                "historical anchors remain for interpretability and strong "
                "methods remain for competitiveness"
            ),
        },
        "comprehensive_appendix": {
            "method_count": 29,
            "methods": sorted(rows),
            "same_source_summary_required": True,
            "main_table_is_not_a_replacement_for_full_screen": True,
        },
        "metrics": [
            {"name": metric, "direction": direction}
            for metric, direction in METRICS
        ],
        "source_evidence": {
            "summary_path": str(summary_path.resolve()),
            "summary_schema_version": summary["schema_version"],
            "summary_file_sha256": summary_file_sha256,
            "scenario_count": 102,
            "suite_count": 7,
            "suites": list(EXPECTED_SUITES),
            "artifact_checks": 612,
            "split_fingerprint_checks": 102,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "strongest_external_comparator": {
            "method": "opendetect",
            "selection_rule": summary["comparator_decision"]["selection_rule"],
            "mean_unknown_metric_rank": rows["opendetect"][
                "mean_unknown_metric_rank"
            ],
            "overall_evidence": rows["opendetect"],
        },
        "self_algorithm_boundary": {
            "excluded_from_classical_baselines": [
                "embedded_pairwise",
                "krc_csr_caeos_v1",
                "rrc_csr_caeos_v1",
            ],
            "self_algorithm_results_must_not_change_main_baseline_membership": True,
            "krc_or_rrc_outcomes_used_for_selection": False,
        },
        "anti_posthoc_rules": {
            "no_baseline_replacement_after_self_algorithm_outcomes": True,
            "no_metric_specific_method_splicing": True,
            "no_suite_specific_method_splicing": True,
            "no_removal_of_weak_anchor_due_to_low_rank": True,
            "no_claim_that_seven_methods_are_the_complete_sota_screen": True,
            "all_29_methods_remain_reportable_in_appendix": True,
        },
        "claim_boundary": {
            "main_table_claim": (
                "concise representative comparison across seven mechanism "
                "families under one frozen strict-v4 evidence source"
            ),
            "comprehensive_claim": (
                "the bound 29-method, 102-scenario screen is the exhaustive "
                "internal comparator evidence for this experiment stage"
            ),
            "does_not_prove_self_algorithm_sota": True,
            "self_algorithm_sota_requires_independent_confirmation": True,
        },
        "implementation_sha256": {
            "create_strict_v4_classical_main_baseline_protocol.py": (
                implementation_sha256
            )
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    args = parser.parse_args()
    summary_path = args.summary.resolve()
    implementation_path = (
        args.project_root.resolve()
        / "create_strict_v4_classical_main_baseline_protocol.py"
    )
    protocol = create_protocol(
        load(summary_path),
        summary_path=summary_path,
        summary_file_sha256=file_hash(summary_path),
        implementation_sha256=file_hash(implementation_path),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
