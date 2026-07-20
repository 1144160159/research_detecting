from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from screen_cross_suite_risk_candidates import (
    REFERENCE,
    load_development_blocks,
)
from screen_edge_risk_candidates import screen


SUITES = {"cic_ton_iot": 3, "cic_iot2023": 3}
DEVELOPMENT_SCENARIOS = {
    "cic_ton_iot": {"xss", "scanning", "ransomware"},
    "cic_iot2023": {
        "command_injection",
        "ddos_icmp_flood",
        "mirai_udpplain",
    },
}
CONFIRMATION_SCENARIOS = {
    "cic_ton_iot": {"password", "backdoor", "ddos"},
    "cic_iot2023": {"browser_hijacking", "dns_spoofing", "recon_port_scan"},
}


def canonical_hash(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_manifest(
    validation: dict[str, Any],
    screenings: dict[str, dict[str, Any]],
    screening_sha256: str,
    confirmation_seeds: list[int],
) -> dict[str, Any]:
    selected = {
        suite: str(report["selected_candidate"])
        for suite, report in sorted(screenings.items())
    }
    if set(selected) != set(SUITES):
        raise ValueError("strict-v4 suite coverage is incomplete")
    if any(
        DEVELOPMENT_SCENARIOS[suite] & CONFIRMATION_SCENARIOS[suite]
        for suite in SUITES
    ):
        raise ValueError("development and confirmation scenarios overlap")
    if not confirmation_seeds or 7 in confirmation_seeds:
        raise ValueError("confirmation seeds must be nonempty and exclude seed 7")
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_fixed_risk_candidate_manifest_v1",
        "status": "frozen_unconfirmed",
        "frozen_before_confirmation": True,
        "selected_suite_risks": selected,
        "reference_risk": "cauchy_modality_support_union",
        "development": {
            "seed": 7,
            "scenarios": {
                suite: sorted(values)
                for suite, values in DEVELOPMENT_SCENARIOS.items()
            },
            "run_count": validation["run_count"],
            "fixed_risk_method_count": validation["fixed_risk_method_count"],
            "source_metrics_combined_sha256": validation[
                "source_metrics_combined_sha256"
            ],
            "screening_sha256": screening_sha256,
            "candidate_screening_uses_test_unknown_labels": True,
        },
        "confirmation": {
            "seeds": sorted(confirmation_seeds),
            "scenarios": {
                suite: sorted(values)
                for suite, values in CONFIRMATION_SCENARIOS.items()
            },
            "expected_run_count": sum(
                len(values) for values in CONFIRMATION_SCENARIOS.values()
            )
            * len(confirmation_seeds),
            "scenario_disjoint": True,
            "seed_disjoint": True,
        },
        "runtime_policy": {
            "routing": "fixed risk by known suite identity",
            "uses_unknown_or_test_labels": False,
        },
        "confirmation_gate": {
            "unit": "scenario mean across confirmation seeds",
            "combined_unknown_auroc_mean_improvement_required": True,
            "combined_unknown_auroc_scenario_bootstrap_ci_lower_gt_zero": True,
            "unknown_aupr_nonregression_tolerance": 0.01,
            "unknown_fpr95_oriented_nonregression_tolerance": 0.01,
            "oscr_nonregression_tolerance": 0.01,
            "each_suite_all_four_oriented_means_positive": True,
            "fallback": "retain cauchy_modality_support_union for the suite",
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    return manifest


def render_markdown(
    validation: dict[str, Any],
    screenings: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
) -> str:
    lines = [
        "# Strict-v4 fixed-risk development screening",
        "",
        f"Runs: {validation['run_count']}; fixed risks: "
        f"{validation['fixed_risk_method_count']}.",
        "Development screening uses unknown test labels and is not confirmation.",
        f"Manifest: `{manifest['manifest_sha256']}`.",
        "",
        "| Suite | Candidate | AUROC | AUPR | FPR95 oriented | OSCR | LOSO paths |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for suite, report in sorted(screenings.items()):
        candidate = report["selected_candidate"]
        row = next(
            item for item in report["method_table"] if item["method"] == candidate
        )
        delta = row["versus_final"]
        lines.append(
            f"| {suite} | {candidate} | {delta['unknown_auroc']:+.6f} | "
            f"{delta['unknown_aupr']:+.6f} | {delta['unknown_fpr95']:+.6f} | "
            f"{delta['oscr']:+.6f} | {report['loso']['selected_paths']} |"
        )
    lines.extend(
        [
            "",
            "Candidates may only be evaluated on the disjoint scenarios and seeds in the frozen manifest.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Screen and freeze strict-v4 suite-specific fixed risks"
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--confirmation-seeds", default="11,19")
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    args = parser.parse_args()
    confirmation_seeds = [
        int(value) for value in args.confirmation_seeds.split(",") if value.strip()
    ]
    blocks, validation = load_development_blocks(args.root, SUITES, 7)
    observed = {
        suite: {key.split("/", 1)[1] for key in values}
        for suite, values in blocks.items()
    }
    if observed != DEVELOPMENT_SCENARIOS:
        raise ValueError(f"development scenario identity mismatch: {observed}")
    screenings = {
        suite: screen(values, REFERENCE, args.nonregression_tolerance)
        for suite, values in blocks.items()
    }
    screening_payload = {"validation": validation, "screenings": screenings}
    screening_bytes = (
        json.dumps(screening_payload, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    screening_sha = hashlib.sha256(screening_bytes).hexdigest()
    manifest = build_manifest(
        validation, screenings, screening_sha, confirmation_seeds
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "screening.json").write_bytes(screening_bytes)
    (args.output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "screening.md").write_text(
        render_markdown(validation, screenings, manifest), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "selected_suite_risks": manifest["selected_suite_risks"],
                "manifest_sha256": manifest["manifest_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
