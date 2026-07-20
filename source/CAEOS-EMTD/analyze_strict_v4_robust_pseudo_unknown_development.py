from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from analyze_strict_v4_pseudo_unknown_development import (
    CANDIDATE,
    REFERENCE,
    REQUIRED_ARTIFACTS,
    UNKNOWN_METRICS,
    canonical_hash,
    metric_report,
    replay_policy_report,
)
from summarize_paired_confirmation import aggregate


COHORTS = {
    "original_development": {
        "cic_ton_iot": ("injection", "password", "scanning"),
        "cic_iot2023": (
            "browser_hijacking",
            "ddos_http_flood",
            "recon_host_discovery",
        ),
    },
    "failed_confirmation": {
        "cic_ton_iot": ("backdoor", "ddos", "dos"),
        "cic_iot2023": (
            "command_injection",
            "mirai_greip_flood",
            "vulnerability_scan",
        ),
    },
}
CONFIRMATION_SCENARIOS = {
    "cic_ton_iot": ("mitm", "ransomware", "xss"),
    "cic_iot2023": ("ddos_syn_flood", "dns_spoofing", "recon_port_scan"),
}
CONFIRMATION_SEEDS = (83, 89)
ALPHAS = (0.1, 0.25, 0.5)
MINIMUM_FOLD_GAINS = (-0.2, -0.175, -0.15, -0.125, -0.1, -0.075, -0.05)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_seed(directory: Path) -> tuple[str, int]:
    match = re.fullmatch(r"(.+)_seed(\d+)", directory.name)
    if match is None:
        raise ValueError(f"unexpected run directory: {directory}")
    return match.group(1), int(match.group(2))


def load_runs(roots: dict[str, Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runs = []
    source_metrics = []
    expected = 0
    for cohort, suites in COHORTS.items():
        root = roots[cohort]
        for suite, scenarios in suites.items():
            for scenario in scenarios:
                matches = sorted((root / suite).glob(f"{scenario}_seed*/metrics.json"))
                required = 1 if cohort == "original_development" else 2
                if len(matches) != required:
                    raise ValueError(
                        f"expected {required} runs for {cohort}/{suite}/{scenario}, "
                        f"found {len(matches)}"
                    )
                expected += required
                for path in matches:
                    parsed_scenario, seed = parse_seed(path.parent)
                    if parsed_scenario != scenario:
                        raise ValueError(f"scenario parse mismatch under {path.parent}")
                    missing = [
                        name for name in REQUIRED_ARTIFACTS if not (path.parent / name).is_file()
                    ]
                    if missing:
                        raise ValueError(f"missing artifacts under {path.parent}: {missing}")
                    raw = path.read_bytes()
                    payload = json.loads(raw.decode("utf-8"))
                    if payload.get("arguments", {}).get("risk_selection") != "nested_pseudo_unknown_blend":
                        raise ValueError(f"source policy mismatch under {path.parent}")
                    learned = payload.get("risk_selection_details", {}).get(
                        "pseudo_unknown_learned_blend", {}
                    )
                    summary = learned.get("selected_summary", {})
                    minimum_fold = float(summary.get("minimum_fold_metric_gain", float("nan")))
                    if not np.isfinite(minimum_fold):
                        raise ValueError(f"missing minimum fold gain under {path.parent}")
                    reports = payload.get("reports", {})
                    reference = metric_report(reports.get(REFERENCE), "reference")
                    replayed = {
                        alpha: replay_policy_report(path.parent, payload, alpha)[0]
                        for alpha in ALPHAS
                    }
                    runs.append(
                        {
                            "cohort": cohort,
                            "suite": suite,
                            "scenario": scenario,
                            "seed": seed,
                            "directory": path.parent,
                            "reference_report": reference,
                            "candidate_by_alpha": replayed,
                            "minimum_fold_metric_gain": minimum_fold,
                        }
                    )
                    source_metrics.append(
                        {
                            "path": f"{cohort}/{path.relative_to(root).as_posix()}",
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    )
    if len(runs) != expected or expected != 18:
        raise ValueError("robust pseudo-unknown development run count mismatch")
    return runs, {
        "passes": True,
        "run_count": len(runs),
        "scenario_count": 12,
        "artifact_checks": len(runs) * len(REQUIRED_ARTIFACTS),
        "runtime_uses_unknown_or_test_labels": False,
        "development_aggregate_opens_prior_unknown_test_outcomes": True,
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def materialize(
    runs: list[dict[str, Any]], alpha: float, minimum_fold_gain: float
) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        active = run["minimum_fold_metric_gain"] >= minimum_fold_gain
        candidate = run["candidate_by_alpha"][alpha] if active else run["reference_report"]
        rows.append(
            {
                "cohort": run["cohort"],
                "suite": run["suite"],
                "scenario": run["scenario"],
                "seed": run["seed"],
                "candidate_selected": CANDIDATE if active else REFERENCE,
                "reference_selected": REFERENCE,
                "candidate_report": candidate,
                "reference_report": run["reference_report"],
                "minimum_fold_metric_gain": run["minimum_fold_metric_gain"],
            }
        )
    return rows


def oriented_means(rows: list[dict[str, Any]]) -> dict[str, float]:
    values = {metric: [] for metric in UNKNOWN_METRICS}
    for row in rows:
        for metric in UNKNOWN_METRICS:
            candidate = row["candidate_report"][metric]
            reference = row["reference_report"][metric]
            values[metric].append(
                reference - candidate if metric == "unknown_fpr95" else candidate - reference
            )
    return {metric: float(np.mean(gains)) for metric, gains in values.items()}


def screen(runs: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    screening = {}
    materialized = {}
    for alpha in ALPHAS:
        for minimum_fold_gain in MINIMUM_FOLD_GAINS:
            rows = materialize(runs, alpha, minimum_fold_gain)
            groups = {}
            for cohort in COHORTS:
                for suite in COHORTS[cohort]:
                    group_rows = [
                        row
                        for row in rows
                        if row["cohort"] == cohort and row["suite"] == suite
                    ]
                    groups[f"{cohort}/{suite}"] = oriented_means(group_rows)
            gains = [value for group in groups.values() for value in group.values()]
            endpoints = Counter(row["candidate_selected"] for row in rows)
            key = f"alpha={alpha}|minimum_fold_gain={minimum_fold_gain}"
            screening[key] = {
                "alpha": alpha,
                "minimum_fold_gain": minimum_fold_gain,
                "minimum_cohort_suite_metric_gain": float(min(gains)),
                "mean_cohort_suite_metric_gain": float(np.mean(gains)),
                "endpoint_counts": dict(endpoints),
                "by_cohort_suite": groups,
            }
            materialized[key] = rows
    selected_key = max(
        screening,
        key=lambda key: (
            screening[key]["minimum_cohort_suite_metric_gain"],
            screening[key]["mean_cohort_suite_metric_gain"],
            -screening[key]["alpha"],
            -abs(screening[key]["minimum_fold_gain"]),
        ),
    )
    return {"selected_key": selected_key, "candidates": screening}, materialized[selected_key]


def analyze(
    roots: dict[str, Path],
    project_root: Path,
    output_dir: Path,
    repetitions: int,
    seed: int,
) -> dict[str, Any]:
    runs, validation = load_runs(roots)
    screening, rows = screen(runs)
    selected = screening["candidates"][screening["selected_key"]]
    grouped = {
        key: aggregate(
            [
                row
                for row in rows
                if f"{row['cohort']}/{row['suite']}" == key
            ],
            repetitions,
            seed,
        )
        for key in selected["by_cohort_suite"]
    }
    combined = aggregate(rows, repetitions, seed)
    nonnegative = selected["minimum_cohort_suite_metric_gain"] >= -1e-12
    endpoint_counts = Counter(row["candidate_selected"] for row in rows)
    suites_exercised = {
        suite: any(
            row["suite"] == suite and row["candidate_selected"] == CANDIDATE for row in rows
        )
        for suite in CONFIRMATION_SCENARIOS
    }
    combined_positive = all(
        combined["metrics"][metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    )
    freeze = bool(
        validation["passes"]
        and nonnegative
        and combined_positive
        and endpoint_counts[CANDIDATE] >= 6
        and all(suites_exercised.values())
    )
    report = {
        "schema_version": "strict_v4_robust_pseudo_unknown_development_v1",
        "state": "frozen_unconfirmed" if freeze else "rejected_development",
        "freeze_candidate": freeze,
        "validation": validation,
        "selected_policy": selected,
        "screening": screening,
        "combined": combined,
        "by_cohort_suite": grouped,
        "endpoint_counts": dict(endpoint_counts),
        "suites_exercised": suites_exercised,
        "rows": rows,
    }
    if freeze:
        implementation = (
            project_root / "caeos" / "pseudo_unknown_risk.py",
            project_root / "train_hybrid_open_set.py",
            project_root / "run_nested_gate_matrix.py",
        )
        manifest = {
            "schema_version": "strict_v4_robust_pseudo_unknown_candidate_v1",
            "status": "frozen_unconfirmed",
            "candidate": {
                "name": "nested_robust_pseudo_unknown_blend_v2",
                "risk_selection": "nested_robust_pseudo_unknown_blend",
                "maximum_alpha": selected["alpha"],
                "minimum_fold_gain": selected["minimum_fold_gain"],
                "runtime_uses_unknown_or_test_labels": False,
                "implementation_sha256": {
                    path.relative_to(project_root).as_posix(): file_hash(path)
                    for path in implementation
                },
            },
            "development": {
                "source_metrics_combined_sha256": validation[
                    "source_metrics_combined_sha256"
                ],
                "selected_key": screening["selected_key"],
                "run_count": validation["run_count"],
                "prior_failed_confirmation_reclassified_as_development": True,
            },
            "confirmation": {
                "seeds": list(CONFIRMATION_SEEDS),
                "scenarios": {
                    suite: list(scenarios)
                    for suite, scenarios in CONFIRMATION_SCENARIOS.items()
                },
                "expected_run_count": 12,
                "expected_scenario_count": 6,
                "seed_disjoint": True,
                "scenario_disjoint_from_policy_development": True,
                "scenario_boundary": (
                    "new scenarios for this robust policy and new cache seeds; some "
                    "scenarios may have appeared in earlier unrelated project pilots"
                ),
            },
        }
        manifest["manifest_sha256"] = canonical_hash(manifest)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "candidate_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        report["manifest_sha256"] = manifest["manifest_sha256"]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    selected = report["selected_policy"]
    lines = [
        "# Strict-v4 robust pseudo-unknown development",
        "",
        f"State: **{report['state']}**; runs: {report['validation']['run_count']}.",
        f"Selected alpha: `{selected['alpha']}`; minimum fold gain: "
        f"`{selected['minimum_fold_gain']}`.",
        f"Endpoint counts: `{report['endpoint_counts']}`.",
        "Prior failed confirmation outcomes are development evidence for this new policy.",
        "",
        "| Cohort / suite | AUROC | AUPR | FPR95 oriented | OSCR |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, values in selected["by_cohort_suite"].items():
        lines.append(
            f"| {key} | {values['unknown_auroc']:+.6f} | "
            f"{values['unknown_aupr']:+.6f} | {values['unknown_fpr95']:+.6f} | "
            f"{values['oscr']:+.6f} |"
        )
    lines.extend(
        [
            "",
            f"Frozen candidate: **{str(report['freeze_candidate']).lower()}**.",
            f"Manifest: `{report.get('manifest_sha256', 'not_frozen')}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-development-root", type=Path, required=True)
    parser.add_argument("--failed-confirmation-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260718)
    args = parser.parse_args()
    report = analyze(
        {
            "original_development": args.original_development_root,
            "failed_confirmation": args.failed_confirmation_root,
        },
        args.project_root.resolve(),
        args.output_dir,
        args.bootstrap_repetitions,
        args.bootstrap_seed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))


if __name__ == "__main__":
    main()
