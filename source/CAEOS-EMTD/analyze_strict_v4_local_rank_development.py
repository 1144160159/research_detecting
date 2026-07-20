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
    REFERENCE,
    REQUIRED_ARTIFACTS,
    UNKNOWN_METRICS,
    canonical_hash,
    metric_report,
)
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.pseudo_unknown_risk import quantile_local_rank_blend
from summarize_paired_confirmation import aggregate


CANDIDATE = "pseudo_unknown_local_rank_blend"
COHORTS = {
    "old_development": {
        "cic_ton_iot": ("injection", "password", "scanning"),
        "cic_iot2023": (
            "browser_hijacking",
            "ddos_http_flood",
            "recon_host_discovery",
        ),
    },
    "old_confirmation": {
        "cic_ton_iot": ("backdoor", "ddos", "dos"),
        "cic_iot2023": (
            "command_injection",
            "mirai_greip_flood",
            "vulnerability_scan",
        ),
    },
    "robust_confirmation": {
        "cic_ton_iot": ("mitm", "ransomware", "xss"),
        "cic_iot2023": ("ddos_syn_flood", "dns_spoofing", "recon_port_scan"),
    },
}
GRID = {
    "bins": (5, 10, 20, 50),
    "beta": (0.2, 0.5, 0.75, 1.0),
    "minimum_fold_gain": (-0.125, -0.1, -0.075, -0.05, -0.025),
}


def load_runs(roots: dict[str, Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runs = []
    source = []
    for cohort, suites in COHORTS.items():
        root = roots[cohort]
        repeats = 1 if cohort == "old_development" else 2
        for suite, scenarios in suites.items():
            for scenario in scenarios:
                paths = sorted((root / suite).glob(f"{scenario}_seed*/metrics.json"))
                if len(paths) != repeats:
                    raise ValueError(f"coverage mismatch for {cohort}/{suite}/{scenario}")
                for path in paths:
                    missing = [
                        name for name in REQUIRED_ARTIFACTS if not (path.parent / name).is_file()
                    ]
                    if missing:
                        raise ValueError(f"missing artifacts under {path.parent}: {missing}")
                    match = re.fullmatch(r"(.+)_seed(\d+)", path.parent.name)
                    if match is None or match.group(1) != scenario:
                        raise ValueError(f"run naming mismatch under {path.parent}")
                    raw = path.read_bytes()
                    payload = json.loads(raw.decode("utf-8"))
                    learned = payload["risk_selection_details"][
                        "pseudo_unknown_learned_blend"
                    ]
                    alpha = float(learned["development_selected_alpha"])
                    archive = np.load(path.parent / "scores.npz")
                    validation_reference = archive[
                        "validation_cauchy_modality_support_union"
                    ]
                    test_reference = archive["test_cauchy_modality_support_union"]
                    validation_blend = archive["validation_pseudo_unknown_learned_blend"]
                    test_blend = archive["test_pseudo_unknown_learned_blend"]
                    validation_learned = (
                        validation_blend - (1.0 - alpha) * validation_reference
                    ) / alpha
                    test_learned = (
                        test_blend - (1.0 - alpha) * test_reference
                    ) / alpha
                    runs.append(
                        {
                            "cohort": cohort,
                            "suite": suite,
                            "scenario": scenario,
                            "seed": int(match.group(2)),
                            "payload": payload,
                            "archive": archive,
                            "validation_reference": validation_reference,
                            "test_reference": test_reference,
                            "validation_learned": validation_learned,
                            "test_learned": test_learned,
                            "minimum_fold_metric_gain": float(
                                learned["selected_summary"]["minimum_fold_metric_gain"]
                            ),
                            "reference_report": metric_report(
                                payload["reports"][REFERENCE], "reference"
                            ),
                        }
                    )
                    source.append(
                        {
                            "path": f"{cohort}/{path.relative_to(root).as_posix()}",
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    )
    if len(runs) != 30:
        raise ValueError("local-rank development requires 30 runs")
    return runs, {
        "passes": True,
        "run_count": len(runs),
        "scenario_count": 18,
        "artifact_checks": len(runs) * len(REQUIRED_ARTIFACTS),
        "runtime_uses_unknown_or_test_labels": False,
        "development_aggregate_opens_prior_unknown_test_outcomes": True,
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def candidate_report(run: dict[str, Any], bins: int, beta: float) -> dict[str, float]:
    validation, test = quantile_local_rank_blend(
        run["validation_reference"],
        run["test_reference"],
        run["validation_learned"],
        run["test_learned"],
        bins=bins,
        beta=beta,
    )
    threshold = float(
        np.quantile(
            validation,
            float(run["payload"].get("arguments", {}).get("known_acceptance", 0.95)),
        )
    )
    archive = run["archive"]
    return metric_report(
        evaluate_hybrid_open_set(
            archive["test_labels"],
            archive["test_unknown"],
            archive["test_prediction"],
            test,
            threshold,
        ),
        "local-rank candidate",
    )


def materialize(
    runs: list[dict[str, Any]], bins: int, beta: float, minimum_fold_gain: float
) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        active = run["minimum_fold_metric_gain"] >= minimum_fold_gain
        candidate = candidate_report(run, bins, beta) if active else run["reference_report"]
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


def group_means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    groups = {}
    for cohort in COHORTS:
        for suite in COHORTS[cohort]:
            selected = [
                row for row in rows if row["cohort"] == cohort and row["suite"] == suite
            ]
            values = {}
            for metric in UNKNOWN_METRICS:
                gains = []
                for row in selected:
                    candidate = row["candidate_report"][metric]
                    reference = row["reference_report"][metric]
                    gains.append(
                        reference - candidate
                        if metric == "unknown_fpr95"
                        else candidate - reference
                    )
                values[metric] = float(np.mean(gains))
            groups[f"{cohort}/{suite}"] = values
    return groups


def analyze(
    roots: dict[str, Path], project_root: Path, output_dir: Path, repetitions: int
) -> dict[str, Any]:
    runs, validation = load_runs(roots)
    screening = {}
    row_sets = {}
    for bins in GRID["bins"]:
        for beta in GRID["beta"]:
            for minimum_fold_gain in GRID["minimum_fold_gain"]:
                key = f"bins={bins}|beta={beta}|minimum_fold_gain={minimum_fold_gain}"
                rows = materialize(runs, bins, beta, minimum_fold_gain)
                groups = group_means(rows)
                gains = [value for group in groups.values() for value in group.values()]
                screening[key] = {
                    "bins": bins,
                    "beta": beta,
                    "minimum_fold_gain": minimum_fold_gain,
                    "minimum_group_metric_gain": float(min(gains)),
                    "mean_group_metric_gain": float(np.mean(gains)),
                    "endpoint_counts": dict(
                        Counter(row["candidate_selected"] for row in rows)
                    ),
                    "by_cohort_suite": groups,
                }
                row_sets[key] = rows
    selected_key = max(
        screening,
        key=lambda key: (
            screening[key]["minimum_group_metric_gain"],
            screening[key]["mean_group_metric_gain"],
            -screening[key]["bins"],
            -screening[key]["beta"],
            -abs(screening[key]["minimum_fold_gain"]),
        ),
    )
    selected = screening[selected_key]
    rows = row_sets[selected_key]
    combined = aggregate(rows, repetitions, 20260718)
    freeze = bool(
        validation["passes"]
        and selected["minimum_group_metric_gain"] >= -1e-12
        and selected["endpoint_counts"].get(CANDIDATE, 0) >= 6
        and all(
            combined["metrics"][metric]["oriented_mean_improvement"] > 0.0
            for metric in UNKNOWN_METRICS
        )
    )
    report = {
        "schema_version": "strict_v4_local_rank_development_v1",
        "state": "frozen_unconfirmed" if freeze else "rejected_development",
        "freeze_candidate": freeze,
        "validation": validation,
        "selected_key": selected_key,
        "selected_policy": selected,
        "screening": screening,
        "combined": combined,
        "rows": rows,
    }
    if freeze:
        files = (
            project_root / "caeos" / "pseudo_unknown_risk.py",
            project_root / "train_hybrid_open_set.py",
            project_root / "run_nested_gate_matrix.py",
        )
        manifest = {
            "schema_version": "strict_v4_local_rank_candidate_v1",
            "status": "frozen_unconfirmed",
            "candidate": {
                "name": "nested_local_rank_pseudo_unknown_blend_v3",
                "risk_selection": "nested_local_rank_pseudo_unknown_blend",
                "maximum_alpha": 0.5,
                "minimum_fold_gain": selected["minimum_fold_gain"],
                "local_rank_bins": selected["bins"],
                "local_rank_beta": selected["beta"],
                "runtime_uses_unknown_or_test_labels": False,
                "implementation_sha256": {
                    path.relative_to(project_root).as_posix(): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in files
                },
            },
            "development": {
                "run_count": validation["run_count"],
                "source_metrics_combined_sha256": validation[
                    "source_metrics_combined_sha256"
                ],
                "selected_key": selected_key,
                "all_prior_confirmation_outcomes_reclassified_as_development": True,
            },
            "confirmation": {
                "seeds": [97, 101],
                "scenarios": {
                    "cic_ton_iot": ["mitm", "ransomware", "xss"],
                    "cic_iot2023": [
                        "backdoor_malware",
                        "ddos_udp_flood",
                        "recon_os_scan",
                    ],
                },
                "expected_run_count": 12,
                "expected_scenario_count": 6,
                "seed_disjoint": True,
                "cic_iot2023_scenarios_disjoint": True,
                "ton_scenarios_repeated_with_new_seeds": True,
                "scenario_boundary": (
                    "CICIoT2023 scenarios and all seeds are new for this policy; "
                    "ToN scenarios repeat with new stratified cache seeds"
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


def render(report: dict[str, Any]) -> str:
    selected = report["selected_policy"]
    lines = [
        "# Strict-v4 local-rank pseudo-unknown development",
        "",
        f"State: **{report['state']}**; runs: {report['validation']['run_count']}.",
        f"Policy: bins `{selected['bins']}`, beta `{selected['beta']}`, minimum fold "
        f"gain `{selected['minimum_fold_gain']}`.",
        f"Endpoint counts: `{selected['endpoint_counts']}`.",
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
    parser.add_argument("--old-development-root", type=Path, required=True)
    parser.add_argument("--old-confirmation-root", type=Path, required=True)
    parser.add_argument("--robust-confirmation-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    args = parser.parse_args()
    report = analyze(
        {
            "old_development": args.old_development_root,
            "old_confirmation": args.old_confirmation_root,
            "robust_confirmation": args.robust_confirmation_root,
        },
        args.project_root.resolve(),
        args.output_dir,
        args.bootstrap_repetitions,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(report), encoding="utf-8")
    print(render(report))


if __name__ == "__main__":
    main()
