from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from screen_strict_v4_risk_candidates import canonical_hash
from summarize_paired_confirmation import METRICS


REFERENCE = "cauchy_modality_support_union"
UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
DEVELOPMENT = {
    "pilot": {
        "cic_ton_iot": {
            "ransomware": (7,),
            "scanning": (7,),
            "xss": (7,),
        },
        "cic_iot2023": {
            "command_injection": (7,),
            "ddos_icmp_flood": (7,),
            "mirai_udpplain": (7,),
        },
    },
    "failed_confirmation": {
        "cic_ton_iot": {
            "backdoor": (11, 19),
            "ddos": (11, 19),
            "password": (11, 19),
        },
        "cic_iot2023": {
            "browser_hijacking": (11, 19),
            "dns_spoofing": (11, 19),
            "recon_port_scan": (11, 19),
        },
    },
}
NEXT_CONFIRMATION = {
    "seeds": [23, 37],
    "scenarios": {
        "cic_ton_iot": ["dos", "injection", "mitm"],
        "cic_iot2023": [
            "backdoor_malware",
            "ddos_http_flood",
            "dictionary_bruteforce",
        ],
    },
}


def metric_report(value: object, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"missing metric report for {label}")
    missing = [metric for metric in METRICS if metric not in value]
    if missing:
        raise ValueError(f"metric report for {label} misses {missing}")
    report = {metric: float(value[metric]) for metric in METRICS}
    if not all(np.isfinite(value) for value in report.values()):
        raise ValueError(f"non-finite metric report for {label}")
    return report


def load_rows(roots: dict[str, Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    method_set: set[str] | None = None
    source_metrics: list[dict[str, str]] = []
    fingerprints: set[str] = set()
    artifact_checks = 0
    for phase, suites in DEVELOPMENT.items():
        root = roots[phase]
        for suite, scenarios in suites.items():
            for scenario, seeds in scenarios.items():
                for seed in seeds:
                    directory = root / suite / f"{scenario}_seed{seed}"
                    missing = [
                        name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()
                    ]
                    if missing:
                        raise ValueError(f"missing artifacts under {directory}: {missing}")
                    artifact_checks += len(REQUIRED_ARTIFACTS)
                    path = directory / "metrics.json"
                    raw = path.read_bytes()
                    payload = json.loads(raw.decode("utf-8"))
                    if int(payload.get("seed", -1)) != seed:
                        raise ValueError(f"seed mismatch under {directory}")
                    details = payload.get("risk_selection_details", {})
                    guard = details.get("unknown_or_test_labels_used_for_selection")
                    if guard is not False and phase != "pilot":
                        raise ValueError(f"runtime leakage guard failed under {directory}")
                    reports = payload.get("reports")
                    if not isinstance(reports, dict) or REFERENCE not in reports:
                        raise ValueError(f"fixed-risk reports are incomplete under {directory}")
                    observed = set(reports)
                    if method_set is None:
                        method_set = observed
                    elif observed != method_set:
                        raise ValueError(f"fixed-risk method set mismatch under {directory}")
                    normalized = {
                        method: metric_report(report, f"{suite}/{scenario}/{seed}/{method}")
                        for method, report in reports.items()
                    }
                    fingerprint = (
                        payload.get("split_metadata", {})
                        .get("split_fingerprint", {})
                        .get("combined")
                    )
                    if not fingerprint:
                        raise ValueError(f"missing split fingerprint under {directory}")
                    fingerprints.add(str(fingerprint))
                    rows.append(
                        {
                            "phase": phase,
                            "suite": suite,
                            "scenario": scenario,
                            "seed": seed,
                            "reports": normalized,
                            "split_fingerprint": str(fingerprint),
                        }
                    )
                    source_metrics.append(
                        {
                            "phase": phase,
                            "path": path.relative_to(root).as_posix(),
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    )
    if method_set is None:
        raise ValueError("no development rows found")
    expected_runs = sum(
        len(seeds)
        for suites in DEVELOPMENT.values()
        for scenarios in suites.values()
        for seeds in scenarios.values()
    )
    if len(rows) != expected_runs:
        raise ValueError(f"development run count mismatch: {len(rows)} != {expected_runs}")
    combined_hash = hashlib.sha256(
        json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": sum(
            len(scenarios)
            for suites in DEVELOPMENT.values()
            for scenarios in suites.values()
        ),
        "fixed_risk_method_count": len(method_set),
        "fixed_risk_methods": sorted(method_set),
        "artifact_checks": artifact_checks,
        "split_fingerprint_checks": len(fingerprints),
        "source_metrics": source_metrics,
        "source_metrics_combined_sha256": combined_hash,
        "development_candidate_screening_uses_test_unknown_labels": True,
        "runtime_policy_uses_unknown_or_test_labels": False,
    }


def oriented_delta(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def scenario_blocks(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["suite"], row["scenario"])].append(row)
    blocks = []
    for (suite, scenario), repeats in sorted(grouped.items()):
        methods = set(repeats[0]["reports"])
        if any(set(row["reports"]) != methods for row in repeats):
            raise ValueError(f"repeat method mismatch for {suite}/{scenario}")
        deltas = {}
        for method in methods:
            deltas[method] = {
                metric: float(
                    np.mean(
                        [
                            oriented_delta(
                                row["reports"][method][metric],
                                row["reports"][REFERENCE][metric],
                                metric,
                            )
                            for row in repeats
                        ]
                    )
                )
                for metric in UNKNOWN_METRICS
            }
        blocks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed_count": len(repeats),
                "deltas": deltas,
            }
        )
    return blocks


def mean_deltas(blocks: list[dict[str, Any]], method: str) -> dict[str, float]:
    return {
        metric: float(np.mean([block["deltas"][method][metric] for block in blocks]))
        for metric in UNKNOWN_METRICS
    }


def screen(
    blocks: list[dict[str, Any]],
    methods: Iterable[str],
    suite_tolerance: float = 0.005,
    loso_tolerance: float = 0.005,
    minimum_combined_auroc_gain: float = 0.005,
) -> dict[str, Any]:
    suites = sorted({block["suite"] for block in blocks})
    table = []
    for method in sorted(set(methods) - {REFERENCE}):
        combined = mean_deltas(blocks, method)
        by_suite = {
            suite: mean_deltas(
                [block for block in blocks if block["suite"] == suite], method
            )
            for suite in suites
        }
        loso = []
        for held_out in blocks:
            retained = [block for block in blocks if block is not held_out]
            loso.append(
                {
                    "held_out": f"{held_out['suite']}/{held_out['scenario']}",
                    "deltas": mean_deltas(retained, method),
                }
            )
        worst_suite_metric_gain = min(
            values[metric] for values in by_suite.values() for metric in UNKNOWN_METRICS
        )
        worst_loso_metric_gain = min(
            fold["deltas"][metric] for fold in loso for metric in UNKNOWN_METRICS
        )
        combined_all_positive = all(value > 0.0 for value in combined.values())
        suite_safe = all(
            value >= -suite_tolerance
            for values in by_suite.values()
            for value in values.values()
        )
        loso_safe = all(
            value >= -loso_tolerance
            for fold in loso
            for value in fold["deltas"].values()
        )
        eligible = all(
            [
                combined_all_positive,
                suite_safe,
                loso_safe,
                combined["unknown_auroc"] >= minimum_combined_auroc_gain,
            ]
        )
        table.append(
            {
                "method": method,
                "combined": combined,
                "by_suite": by_suite,
                "worst_suite_metric_gain": worst_suite_metric_gain,
                "worst_loso_metric_gain": worst_loso_metric_gain,
                "combined_mean_gain": float(np.mean(list(combined.values()))),
                "combined_all_positive": combined_all_positive,
                "suite_safe": suite_safe,
                "loso_safe": loso_safe,
                "eligible": eligible,
                "loso": loso,
            }
        )
    eligible_rows = [row for row in table if row["eligible"]]
    ranked = sorted(
        eligible_rows,
        key=lambda row: (
            row["worst_suite_metric_gain"],
            row["worst_loso_metric_gain"],
            row["combined"]["unknown_auroc"],
            row["combined_mean_gain"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "selection_rule": {
            "scope": "one uniform fixed risk across both strict-v4 suites",
            "combined_all_four_oriented_means_gt_zero": True,
            "minimum_combined_auroc_gain": minimum_combined_auroc_gain,
            "suite_nonregression_tolerance": suite_tolerance,
            "leave_one_scenario_out_nonregression_tolerance": loso_tolerance,
            "ranking": [
                "maximize worst suite-by-metric gain",
                "maximize worst LOSO metric gain",
                "maximize combined AUROC gain",
                "maximize combined four-metric mean gain",
            ],
        },
        "selected_candidate": ranked[0]["method"] if ranked else None,
        "eligible_count": len(ranked),
        "eligible_ranking": [row["method"] for row in ranked],
        "method_table": sorted(
            table,
            key=lambda row: (
                not row["eligible"],
                -row["worst_suite_metric_gain"],
                -row["combined_mean_gain"],
                row["method"],
            ),
        ),
    }


def build_manifest(
    validation: dict[str, Any], screening: dict[str, Any]
) -> dict[str, Any]:
    selected = screening["selected_candidate"]
    status = "frozen_unconfirmed" if selected else "no_eligible_candidate"
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_fixed_risk_candidate_manifest_v1",
        "status": status,
        "frozen_before_confirmation": bool(selected),
        "selected_suite_risks": (
            {suite: selected for suite in sorted(NEXT_CONFIRMATION["scenarios"])}
            if selected
            else {}
        ),
        "reference_risk": REFERENCE,
        "development": {
            "phases": DEVELOPMENT,
            "run_count": validation["run_count"],
            "scenario_count": validation["scenario_count"],
            "fixed_risk_method_count": validation["fixed_risk_method_count"],
            "source_metrics_combined_sha256": validation[
                "source_metrics_combined_sha256"
            ],
            "candidate_screening_uses_test_unknown_labels": True,
            "selection_rule": screening["selection_rule"],
        },
        "confirmation": {
            **NEXT_CONFIRMATION,
            "expected_run_count": sum(
                len(values) for values in NEXT_CONFIRMATION["scenarios"].values()
            )
            * len(NEXT_CONFIRMATION["seeds"]),
            "scenario_disjoint": True,
            "seed_disjoint": True,
        },
        "runtime_policy": {
            "routing": "one frozen fixed risk for both known strict-v4 suites",
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
            "fallback": "retain cauchy_modality_support_union for both suites",
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    return manifest


def render_markdown(
    validation: dict[str, Any], screening: dict[str, Any], manifest: dict[str, Any]
) -> str:
    candidate = screening["selected_candidate"]
    lines = [
        "# Strict-v4 expanded-development risk screening",
        "",
        f"Runs: {validation['run_count']}; scenario blocks: "
        f"{validation['scenario_count']}; fixed risks: "
        f"{validation['fixed_risk_method_count']}.",
        "The failed confirmation set is now development evidence. Screening uses "
        "unknown test labels and cannot itself support a final claim.",
        f"State: **{manifest['status']}**; candidate: `{candidate}`.",
        f"Manifest: `{manifest['manifest_sha256']}`.",
        "",
        "| Method | Eligible | AUROC | AUPR | FPR95 oriented | OSCR | Worst suite-metric | Worst LOSO-metric |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in screening["method_table"][:15]:
        delta = row["combined"]
        lines.append(
            f"| {row['method']} | {str(row['eligible']).lower()} | "
            f"{delta['unknown_auroc']:+.6f} | {delta['unknown_aupr']:+.6f} | "
            f"{delta['unknown_fpr95']:+.6f} | {delta['oscr']:+.6f} | "
            f"{row['worst_suite_metric_gain']:+.6f} | "
            f"{row['worst_loso_metric_gain']:+.6f} |"
        )
    lines.extend(
        [
            "",
            "A candidate is frozen only when one fixed risk is jointly safe across both "
            "suites and every leave-one-scenario-out fold.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Screen a robust uniform strict-v4 risk on expanded development"
    )
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--failed-confirmation-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, validation = load_rows(
        {
            "pilot": args.pilot_root,
            "failed_confirmation": args.failed_confirmation_root,
        }
    )
    blocks = scenario_blocks(rows)
    screening = screen(blocks, validation["fixed_risk_methods"])
    manifest = build_manifest(validation, screening)
    payload = {
        "schema_version": "strict_v4_expanded_development_screening_v1",
        "validation": validation,
        "scenario_blocks": blocks,
        "screening": screening,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "screening.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "screening.md").write_text(
        render_markdown(validation, screening, manifest), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "selected_candidate": screening["selected_candidate"],
                "eligible_count": screening["eligible_count"],
                "manifest_sha256": manifest["manifest_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
