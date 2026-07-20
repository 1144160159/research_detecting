from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
LOWER_IS_BETTER = {"unknown_fpr95"}
FALLBACK = "caeos_pairwise"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def suite_gains(method: dict[str, Any]) -> dict[str, float]:
    return {
        metric: float(method["metrics"][metric]["oriented_mean_delta"])
        for metric in UNKNOWN_METRICS
    }


def select_suite_method(methods: dict[str, dict[str, Any]]) -> tuple[str, dict[str, float]]:
    eligible: list[tuple[float, float, str, dict[str, float]]] = []
    for name, report in sorted(methods.items()):
        gains = suite_gains(report)
        if all(value > 0.0 for value in gains.values()):
            eligible.append((min(gains.values()), sum(gains.values()), name, gains))
    if not eligible:
        return FALLBACK, {metric: 0.0 for metric in UNKNOWN_METRICS}
    _, _, name, gains = max(eligible)
    return name, gains


def route_report(run: dict[str, Any], method: str) -> dict[str, float]:
    report = run["gate_report"] if method == FALLBACK else run["reports"][method]
    return {metric: float(report[metric]) for metric in UNKNOWN_METRICS}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    raw = json.loads(args.raw_fusion.read_text(encoding="utf-8"))
    expected = coverage["scenario_inference_units"]
    if raw.get("overall", {}).get("number_of_runs") != expected:
        raise ValueError("raw fusion coverage mismatch")
    if raw.get("selection_scope", {}).get("seeds") != [7]:
        raise ValueError("router development requires only seed7")

    routing: dict[str, dict[str, Any]] = {}
    for suite in coverage["scenario_registry"]:
        method, gains = select_suite_method(raw["by_suite"][suite]["methods"])
        routing[suite] = {
            "method": method,
            "development_oriented_mean_gains": gains,
            "enabled": method != FALLBACK,
        }

    rows = []
    for run in raw["runs"]:
        suite = run["suite"]
        method = routing[suite]["method"]
        candidate = route_report(run, method)
        reference = {metric: float(run["gate_report"][metric]) for metric in UNKNOWN_METRICS}
        gains = {
            metric: (
                reference[metric] - candidate[metric]
                if metric in LOWER_IS_BETTER
                else candidate[metric] - reference[metric]
            )
            for metric in UNKNOWN_METRICS
        }
        rows.append({
            "suite": suite,
            "task": run["task"],
            "method": method,
            "candidate_report": candidate,
            "reference_report": reference,
            "oriented_gains": gains,
        })

    overall_gains = {
        metric: sum(row["oriented_gains"][metric] for row in rows) / len(rows)
        for metric in UNKNOWN_METRICS
    }
    suite_gains_report = {
        suite: {
            metric: sum(
                row["oriented_gains"][metric]
                for row in rows
                if row["suite"] == suite
            )
            / sum(row["suite"] == suite for row in rows)
            for metric in UNKNOWN_METRICS
        }
        for suite in coverage["scenario_registry"]
    }
    if not all(value > 0.0 for value in overall_gains.values()):
        raise ValueError(f"router does not improve every overall metric: {overall_gains}")
    if any(
        value < -1e-12
        for gains in suite_gains_report.values()
        for value in gains.values()
    ):
        raise ValueError("router regresses at least one suite metric")

    payload: dict[str, Any] = {
        "schema_version": "strict_v4_domain_safe_router_candidate_v1",
        "status": "frozen_after_seed7_development_before_new_seed_confirmation",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "raw_fusion_sha256": file_hash(args.raw_fusion),
        "base_algorithm": "nested_boundary_pairwise_pseudo_unknown_blend",
        "expert_model": "mlp",
        "expert_risk": "openmax",
        "fallback": FALLBACK,
        "selection_rule": (
            "per suite, retain fixed fusions with strictly positive seed7 mean "
            "gains on AUROC, AUPR, oriented FPR95, and OSCR; maximize the "
            "minimum gain, then the gain sum, then method name; otherwise fallback"
        ),
        "routing": routing,
        "development_evidence": {
            "seed": 7,
            "scenario_count": len(rows),
            "overall_oriented_mean_gains": overall_gains,
            "suite_oriented_mean_gains": suite_gains_report,
            "all_overall_metrics_positive": True,
            "all_suite_metrics_nonnegative": True,
        },
        "inference_audit": {
            "runtime_selection_inputs": ["suite_id"],
            "unknown_or_test_labels_used_at_inference": False,
            "unknown_or_test_labels_used_for_thresholds": False,
            "test_labels_used_for_seed7_development_selection": True,
            "new_seed_confirmation_must_not_change_routing": True,
        },
        "implementation_sha256": file_hash(Path(__file__)),
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
