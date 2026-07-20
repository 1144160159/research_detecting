from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from confirm_strict_v4_tail_vs_incumbent import decision, suite_gains
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_rows(
    protocol: dict[str, Any], candidate_root: Path, comparator_root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seeds = {int(seed) for seed in protocol["seeds"]}
    expected = {
        (suite, scenario, seed)
        for suite, scenarios in protocol["scenario_registry"].items()
        for scenario in scenarios
        for seed in seeds
    }
    rows = []
    artifact_checks = 0
    split_checks = 0
    for suite, scenario, seed in sorted(expected):
        candidate_dir = candidate_root / suite / f"{scenario}_seed{seed}"
        comparator_dir = comparator_root / suite / f"{scenario}_seed{seed}_opendetect"
        for directory, artifacts in (
            (candidate_dir, ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")),
            (comparator_dir, ("metrics.json", "scores.npz", "provenance.json")),
        ):
            missing = [name for name in artifacts if not (directory / name).is_file()]
            if missing:
                raise ValueError(f"missing tail external artifacts under {directory}: {missing}")
            artifact_checks += len(artifacts)
        candidate = json.loads((candidate_dir / "metrics.json").read_text(encoding="utf-8"))
        comparator = json.loads((comparator_dir / "metrics.json").read_text(encoding="utf-8"))
        if candidate.get("risk_policy") != protocol["candidate"]["risk_policy"]:
            raise ValueError("tail external candidate policy mismatch")
        if candidate.get("risk_selection_details", {}).get(
            "unknown_or_test_labels_used_for_selection"
        ) is not False:
            raise ValueError("tail external candidate leakage guard failed")
        evidence = comparator.get("selection_evidence", {})
        if evidence.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            raise ValueError("OpenDetect external leakage guard failed")
        candidate_fingerprint = candidate["split_metadata"]["split_fingerprint"]
        comparator_fingerprint = comparator["split_metadata"]["split_fingerprint"]
        if candidate_fingerprint != comparator_fingerprint:
            raise ValueError("tail external split fingerprint mismatch")
        split_checks += 1
        candidate_report = candidate["selected_report"]
        comparator_report = comparator["reports"]["opendetect"]
        for report in (candidate_report, comparator_report):
            if any(metric not in report for metric in METRICS):
                raise ValueError("tail external report is incomplete")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": candidate["selected_risk"],
                "reference_selected": "opendetect",
                "candidate_report": candidate_report,
                "reference_report": comparator_report,
            }
        )
    if len(rows) != int(protocol["expected_candidate_runs"]):
        raise ValueError("tail external run count mismatch")
    return rows, {
        "passes": True,
        "paired_runs": len(rows),
        "scenario_count": int(protocol["scenario_count"]),
        "seeds": sorted(seeds),
        "artifact_checks": artifact_checks,
        "split_fingerprint_pair_checks": split_checks,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 tail-aware algorithm vs OpenDetect",
        "",
        f"External confirmation gate: **{'PASS' if result['decision']['passes'] else 'FAIL'}**.",
        "",
        "| Metric | OpenDetect | Tail-aware | Gain | 95% CI | Holm p |",
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
    parser.add_argument("--optimal-decision", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--comparator-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    optimal = json.loads(args.optimal_decision.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "strict_v4_tail_external_confirmation_protocol_v1":
        raise ValueError("unexpected tail external protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("tail external protocol SHA mismatch")
    if optimal.get("schema_version") != "strict_v4_optimal_self_algorithm_decision_v1":
        raise ValueError("unexpected optimal algorithm decision schema")
    if optimal.get("selected_algorithm") != protocol["selected_algorithm"]:
        raise ValueError("tail external branch activation mismatch")
    rows, validation = build_rows(protocol, args.candidate_root, args.comparator_root)
    inference_settings = protocol["inference"]
    inference = aggregate(
        rows,
        int(inference_settings["bootstrap_repetitions"]),
        int(inference_settings["bootstrap_seed"]),
    )
    by_suite = suite_gains(
        rows,
        int(inference_settings["bootstrap_repetitions"]),
        int(inference_settings["bootstrap_seed"]),
    )
    result = {
        "schema_version": "strict_v4_external_comparator_confirmation_v1",
        "selected_algorithm": protocol["selected_algorithm"],
        "selected_comparator": protocol["selected_comparator"],
        "external_protocol_manifest_sha256": protocol["manifest_sha256"],
        "candidate_validation": validation,
        "comparator_validation": validation,
        "scenario_blocked_inference": inference,
        "suite_oriented_mean_gains": by_suite,
        "decision": decision(inference, by_suite),
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
