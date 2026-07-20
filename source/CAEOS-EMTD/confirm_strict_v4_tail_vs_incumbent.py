from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate
from summarize_strict_v4_full103 import PAIRWISE_METHOD


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} manifest SHA mismatch")


def decision(
    inference: dict[str, Any], by_suite: dict[str, dict[str, float]]
) -> dict[str, Any]:
    metrics = inference["metrics"]
    means = {
        metric: metrics[metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    bootstrap = {
        metric: metrics[metric]["bootstrap_95_ci"]["lower"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    holm = {
        metric: (
            metrics[metric]["wilcoxon"]["holm_adjusted_p_value"] is not None
            and metrics[metric]["wilcoxon"]["holm_adjusted_p_value"] < 0.05
        )
        for metric in UNKNOWN_METRICS
    }
    suite_safe = {
        suite: {metric: value >= -1e-12 for metric, value in values.items()}
        for suite, values in by_suite.items()
    }
    checks = {
        "all_four_unknown_metric_means_strictly_positive": all(means.values()),
        "all_four_bootstrap_lowers_strictly_positive": all(bootstrap.values()),
        "all_four_holm_p_values_below_0_05": all(holm.values()),
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
        "mean_checks": means,
        "bootstrap_checks": bootstrap,
        "holm_checks": holm,
        "suite_checks": suite_safe,
    }


def build_rows(
    protocol: dict[str, Any],
    router: dict[str, Any],
    incumbent: dict[str, Any],
    tail_root: Path,
    pairwise_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    head = protocol["head_to_head"]
    seeds = {int(seed) for seed in head["seeds"]}
    registry = protocol["coverage"]["scenario_registry"]
    expected = {
        (suite, scenario, seed)
        for suite, scenarios in registry.items()
        for scenario in scenarios
        for seed in seeds
    }
    incumbent_algorithm = incumbent["selected_algorithm"]
    if incumbent_algorithm not in {"caeos_domain_safe_router", "caeos_pairwise"}:
        raise ValueError("unexpected incumbent algorithm")
    rows = []
    artifact_checks = 0
    split_checks = 0
    for suite, scenario, seed in sorted(expected):
        tail_dir = tail_root / suite / f"{scenario}_seed{seed}"
        pairwise_dir = pairwise_root / suite / f"{scenario}_seed{seed}"
        for directory in (tail_dir, pairwise_dir):
            missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()]
            if missing:
                raise ValueError(f"missing tournament artifacts under {directory}: {missing}")
            artifact_checks += len(REQUIRED_ARTIFACTS)
        tail = json.loads((tail_dir / "metrics.json").read_text(encoding="utf-8"))
        pairwise = json.loads((pairwise_dir / "metrics.json").read_text(encoding="utf-8"))
        if tail.get("risk_policy") != "strict_v4_tail_aware_pairwise_confirmation_v1":
            raise ValueError("tail-aware tournament policy mismatch")
        if pairwise.get("risk_policy") != head["pairwise_risk_policy"]:
            raise ValueError("pairwise tournament policy mismatch")
        for payload in (tail, pairwise):
            if payload.get("risk_selection_details", {}).get(
                "unknown_or_test_labels_used_for_selection"
            ) is not False:
                raise ValueError("tournament runtime leakage guard failed")
        tail_fingerprint = tail["split_metadata"]["split_fingerprint"]
        pairwise_fingerprint = pairwise["split_metadata"]["split_fingerprint"]
        if tail_fingerprint != pairwise_fingerprint:
            raise ValueError("tournament split fingerprint mismatch")
        split_checks += 1
        candidate_report = tail["selected_report"]
        if incumbent_algorithm == "caeos_pairwise":
            incumbent_method = PAIRWISE_METHOD
            incumbent_report = pairwise["selected_report"]
        else:
            incumbent_method = router["routing"][suite]["method"]
            incumbent_report = (
                pairwise["selected_report"]
                if incumbent_method == PAIRWISE_METHOD
                else pairwise["reports"][incumbent_method]
            )
        for report in (candidate_report, incumbent_report):
            if any(metric not in report for metric in METRICS):
                raise ValueError("tournament report is incomplete")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": tail["selected_risk"],
                "reference_selected": incumbent_method,
                "candidate_report": candidate_report,
                "reference_report": incumbent_report,
            }
        )
    if len(rows) != int(head["expected_pairwise_runs"]):
        raise ValueError("tournament run count mismatch")
    return rows, {
        "passes": True,
        "paired_runs": len(rows),
        "scenario_count": int(protocol["coverage"]["scenario_count"]),
        "seeds": sorted(seeds),
        "artifact_checks": artifact_checks,
        "split_fingerprint_pair_checks": split_checks,
        "incumbent_algorithm": incumbent_algorithm,
        "unknown_or_test_labels_used_for_runtime_selection": False,
    }


def suite_gains(rows: list[dict[str, Any]], repetitions: int, seed: int) -> dict[str, dict[str, float]]:
    output = {}
    for suite in sorted({row["suite"] for row in rows}):
        result = aggregate([row for row in rows if row["suite"] == suite], repetitions, seed)
        output[suite] = {
            metric: float(result["metrics"][metric]["oriented_mean_improvement"])
            for metric in UNKNOWN_METRICS
        }
    return output


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 tail-aware challenger vs incumbent",
        "",
        f"Incumbent: `{result['validation']['incumbent_algorithm']}`.",
        f"Replacement gate: **{'PASS' if result['decision']['passes'] else 'FAIL'}**.",
        "",
        "| Metric | Incumbent | Tail-aware | Gain | 95% CI | Holm p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = result["scenario_blocked_inference"]["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        p = item["wilcoxon"]["holm_adjusted_p_value"]
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{'NA' if p is None else f'{p:.3g}'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--incumbent-decision", type=Path, required=True)
    parser.add_argument("--tail-root", type=Path, required=True)
    parser.add_argument("--pairwise-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    incumbent = json.loads(args.incumbent_decision.read_text(encoding="utf-8"))
    validate_manifest(protocol, "strict_v4_self_algorithm_tournament_protocol_v1", "tournament protocol")
    validate_manifest(router, "strict_v4_domain_safe_router_candidate_v1", "router")
    if incumbent.get("schema_version") != "strict_v4_final_algorithm_decision_v1":
        raise ValueError("unexpected incumbent decision schema")
    if incumbent.get("manifest_sha256") != canonical_hash(incumbent):
        raise ValueError("incumbent decision SHA mismatch")
    rows, validation = build_rows(protocol, router, incumbent, args.tail_root, args.pairwise_root)
    head = protocol["head_to_head"]
    inference = aggregate(rows, int(head["bootstrap_repetitions"]), int(head["bootstrap_seed"]))
    by_suite = suite_gains(rows, int(head["bootstrap_repetitions"]), int(head["bootstrap_seed"]))
    result = {
        "schema_version": "strict_v4_tail_vs_incumbent_confirmation_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "validation": validation,
        "scenario_blocked_inference": inference,
        "suite_oriented_mean_gains": by_suite,
        "decision": decision(inference, by_suite),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "head_to_head.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "head_to_head.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
