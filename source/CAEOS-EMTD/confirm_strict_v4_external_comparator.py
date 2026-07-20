from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from confirm_strict_v4_domain_safe_router import build_rows, validate_manifest
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate
from summarize_strict_v4_full103 import UNKNOWN_METRICS


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def confirmation_decision(
    inference: dict[str, Any], by_suite: dict[str, dict[str, float]]
) -> dict[str, Any]:
    metrics = inference["metrics"]
    means = {
        metric: metrics[metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    holm = {
        metric: metrics[metric]["wilcoxon"]["holm_adjusted_p_value"] < 0.05
        for metric in UNKNOWN_METRICS
    }
    suite_safe = {
        suite: {metric: value >= -1e-12 for metric, value in values.items()}
        for suite, values in by_suite.items()
    }
    checks = {
        "all_four_unknown_metric_means_strictly_positive": all(means.values()),
        "auroc_bootstrap_lower_strictly_positive": metrics["unknown_auroc"][
            "bootstrap_95_ci"
        ]["lower"]
        > 0.0,
        "aupr_bootstrap_lower_strictly_positive": metrics["unknown_aupr"][
            "bootstrap_95_ci"
        ]["lower"]
        > 0.0,
        "all_four_unknown_metric_holm_p_below_0_05": all(holm.values()),
        "all_suite_unknown_metric_means_nonnegative": all(
            value for values in suite_safe.values() for value in values.values()
        ),
        "known_macro_f1_nonnegative": metrics["known_macro_f1"][
            "oriented_mean_improvement"
        ]
        >= -1e-12,
    }
    return {
        "passes": all(checks.values()),
        "checks": checks,
        "unknown_metric_mean_checks": means,
        "unknown_metric_holm_checks": holm,
        "suite_nonregression_checks": suite_safe,
    }


def _comparator_directory(
    method: str, suite: str, scenario: str, seed: int, mlp_root: Path, external_root: Path
) -> tuple[Path, str]:
    if method.startswith("mlp_"):
        return mlp_root / suite / f"{scenario}_seed{seed}_mlp", method[4:]
    if method == "opendetect":
        return external_root / suite / f"{scenario}_seed{seed}_opendetect", method
    return external_root / suite / f"{scenario}_seed{seed}_classical_ood", method


def build_comparison_rows(
    candidate_rows: list[dict[str, Any]],
    final_algorithm: str,
    comparator: str,
    mlp_root: Path,
    external_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    artifact_checks = 0
    split_checks = 0
    for row in candidate_rows:
        suite, scenario, seed = row["suite"], row["scenario"], int(row["seed"])
        candidate = (
            row["candidate_report"]
            if final_algorithm == "caeos_domain_safe_router"
            else row["reference_report"]
        )
        directory, report_name = _comparator_directory(
            comparator, suite, scenario, seed, mlp_root, external_root
        )
        missing = [
            name
            for name in ("metrics.json", "scores.npz", "provenance.json")
            if not (directory / name).is_file()
        ]
        if missing:
            raise ValueError(f"missing comparator artifacts under {directory}: {missing}")
        artifact_checks += 3
        payload = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
        reports = payload.get("reports", {})
        if report_name not in reports:
            raise ValueError(f"comparator report {report_name} missing under {directory}")
        evidence = payload.get("selection_evidence", {})
        if comparator.startswith("mlp_") or comparator == "opendetect":
            if evidence.get(
                "unknown_or_test_labels_used_for_fitting_or_selection"
            ) is not False:
                raise ValueError(f"neural comparator leakage guard failed under {directory}")
        elif not (
            evidence.get("unknown_or_test_labels_used_for_training") is False
            and evidence.get("unknown_or_test_labels_used_for_thresholds") is False
        ):
            raise ValueError(f"classical comparator leakage guard failed under {directory}")
        fingerprint = payload["split_metadata"]["split_fingerprint"]["combined"]
        mlp_directory = mlp_root / suite / f"{scenario}_seed{seed}_mlp"
        mlp_payload = json.loads(
            (mlp_directory / "metrics.json").read_text(encoding="utf-8")
        )
        mlp_fingerprint = mlp_payload["split_metadata"]["split_fingerprint"][
            "combined"
        ]
        if fingerprint != mlp_fingerprint:
            raise ValueError(f"comparator split fingerprint mismatch under {directory}")
        split_checks += 1
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": final_algorithm,
                "reference_selected": comparator,
                "candidate_report": candidate,
                "reference_report": reports[report_name],
            }
        )
    return rows, {
        "passes": True,
        "paired_runs": len(rows),
        "artifact_checks": artifact_checks,
        "split_fingerprint_checks": split_checks,
        "unknown_or_test_labels_used_for_comparator_selection_or_fitting": False,
    }


def suite_gains(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    output = {}
    for suite in sorted({row["suite"] for row in rows}):
        inference = aggregate(
            [row for row in rows if row["suite"] == suite], 10000, 20260720
        )
        output[suite] = {
            metric: float(inference["metrics"][metric]["oriented_mean_improvement"])
            for metric in UNKNOWN_METRICS
        }
    return output


def render(result: dict[str, Any]) -> str:
    inference = result["scenario_blocked_inference"]
    lines = [
        "# Strict-v4 final algorithm vs strongest external comparator",
        "",
        f"Candidate: `{result['selected_algorithm']}`; comparator: "
        f"`{result['selected_comparator']}`.",
        "",
        "| Metric | Comparator | Candidate | Gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = inference["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        p_value = item["wilcoxon"]["holm_adjusted_p_value"]
        p_text = "NA" if p_value is None else f"{p_value:.3g}"
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{item['wins']}/{item['ties']}/{item['losses']} | {p_text} |"
        )
    lines.extend(
        [
            "",
            f"Confirmation gate: **{'PASS' if result['decision']['passes'] else 'FAIL'}**.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-protocol", type=Path, required=True)
    parser.add_argument("--router-protocol", type=Path, required=True)
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--final-decision", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    external_protocol = json.loads(args.external_protocol.read_text(encoding="utf-8"))
    router_protocol = json.loads(args.router_protocol.read_text(encoding="utf-8"))
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    raw = json.loads(args.raw_fusion.read_text(encoding="utf-8"))
    final_decision = json.loads(args.final_decision.read_text(encoding="utf-8"))
    validate_manifest(
        external_protocol, "strict_v4_external_confirmation_protocol_v1", "external protocol"
    )
    validate_manifest(
        router_protocol,
        "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "router protocol",
    )
    validate_manifest(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate_manifest(router, "strict_v4_domain_safe_router_candidate_v1", "router")
    if external_protocol["coverage_manifest_sha256"] != coverage["manifest_sha256"]:
        raise ValueError("external protocol coverage binding mismatch")
    if (
        external_protocol["router_confirmation_protocol_sha256"]
        != router_protocol["manifest_sha256"]
    ):
        raise ValueError("external protocol router binding mismatch")
    if final_decision.get("schema_version") != "strict_v4_final_algorithm_decision_v1":
        raise ValueError("unexpected final algorithm decision schema")
    if final_decision.get("manifest_sha256") != canonical_hash(final_decision):
        raise ValueError("final algorithm decision SHA mismatch")
    if (
        final_decision.get("protocol_manifest_sha256")
        != router_protocol["manifest_sha256"]
    ):
        raise ValueError("final algorithm decision protocol binding mismatch")
    final_algorithm = final_decision["selected_algorithm"]
    if final_algorithm not in {"caeos_domain_safe_router", "caeos_pairwise"}:
        raise ValueError("unsupported final algorithm")
    candidate_rows, candidate_validation = build_rows(
        raw, coverage, router, router_protocol
    )
    rows, comparator_validation = build_comparison_rows(
        candidate_rows,
        final_algorithm,
        external_protocol["selected_comparator"],
        args.mlp_root,
        args.external_root,
    )
    expected = external_protocol["expected_comparator_runs"]
    if len(rows) != expected:
        raise ValueError("external comparator confirmation coverage is incomplete")
    inference = aggregate(rows, 20000, 20260720)
    by_suite = suite_gains(rows)
    result = {
        "schema_version": "strict_v4_external_comparator_confirmation_v1",
        "selected_algorithm": final_algorithm,
        "selected_comparator": external_protocol["selected_comparator"],
        "external_protocol_manifest_sha256": external_protocol["manifest_sha256"],
        "candidate_validation": candidate_validation,
        "comparator_validation": comparator_validation,
        "scenario_blocked_inference": inference,
        "suite_oriented_mean_gains": by_suite,
        "decision": confirmation_decision(inference, by_suite),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
