from __future__ import annotations

import argparse
import hashlib
import json
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


SCENARIOS = {
    "cic_ton_iot": ("injection", "password", "scanning"),
    "cic_iot2023": (
        "browser_hijacking",
        "ddos_http_flood",
        "recon_host_discovery",
    ),
}
MAXIMUM_ALPHAS = (0.1, 0.25, 0.5)
MINIMUM_FOLD_GAINS = (-0.35, -0.1, -0.075, -0.05, -0.025)


def load_runs(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runs = []
    source = []
    fingerprints = set()
    for suite, scenarios in SCENARIOS.items():
        for scenario in scenarios:
            directory = root / suite / f"{scenario}_seed7"
            missing = [
                name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()
            ]
            if missing:
                raise ValueError(f"missing artifacts under {directory}: {missing}")
            path = directory / "metrics.json"
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8"))
            if payload.get("arguments", {}).get("risk_selection") != "nested_boundary_pseudo_unknown_blend":
                raise ValueError(f"boundary policy mismatch under {directory}")
            learned = payload["risk_selection_details"]["pseudo_unknown_learned_blend"]
            if learned.get("unknown_or_test_labels_used") is not False:
                raise ValueError(f"boundary leakage declaration failed under {directory}")
            if learned.get("pseudo_unknown_source") != (
                "known validation attack labels plus known-only boundary interpolation"
            ):
                raise ValueError(f"boundary source mismatch under {directory}")
            distribution = learned.get("training_distribution", {})
            if distribution.get("enabled") is not True:
                raise ValueError(f"boundary distribution missing under {directory}")
            if distribution.get("unknown_or_test_labels_used") is not False:
                raise ValueError(f"boundary distribution leakage under {directory}")
            fingerprint = (
                payload.get("split_metadata", {})
                .get("split_fingerprint", {})
                .get("combined")
            )
            if not fingerprint:
                raise ValueError(f"missing split fingerprint under {directory}")
            fingerprints.add(str(fingerprint))
            runs.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "seed": 7,
                    "directory": directory,
                    "payload": payload,
                    "minimum_fold_metric_gain": float(
                        learned["selected_summary"]["minimum_fold_metric_gain"]
                    ),
                    "reference_report": metric_report(
                        payload["reports"][REFERENCE], "reference"
                    ),
                    "synthetic_boundary_samples": int(
                        sum(
                            row["synthetic_boundary_samples"]
                            for row in distribution["tasks"]
                        )
                    ),
                }
            )
            source.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
    if len(runs) != 6:
        raise ValueError("boundary development requires six runs")
    return runs, {
        "passes": True,
        "run_count": len(runs),
        "scenario_count": len(runs),
        "seed": 7,
        "artifact_checks": len(runs) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "runtime_uses_unknown_or_test_labels": False,
        "development_aggregate_opens_unknown_test_outcomes": True,
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def materialize(
    runs: list[dict[str, Any]], maximum_alpha: float, minimum_fold_gain: float
) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        active = run["minimum_fold_metric_gain"] >= minimum_fold_gain
        candidate, replay_alpha = replay_policy_report(
            run["directory"], run["payload"], maximum_alpha
        )
        if not active:
            candidate = run["reference_report"]
            replay_alpha = 0.0
        rows.append(
            {
                "suite": run["suite"],
                "scenario": run["scenario"],
                "seed": run["seed"],
                "candidate_selected": CANDIDATE if active else REFERENCE,
                "reference_selected": REFERENCE,
                "candidate_report": candidate,
                "reference_report": run["reference_report"],
                "minimum_fold_metric_gain": run["minimum_fold_metric_gain"],
                "replay_alpha": replay_alpha,
                "synthetic_boundary_samples": run["synthetic_boundary_samples"],
            }
        )
    return rows


def suite_means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    result = {}
    for suite in SCENARIOS:
        selected = [row for row in rows if row["suite"] == suite]
        result[suite] = {}
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
            result[suite][metric] = float(np.mean(gains))
    return result


def analyze(root: Path, project_root: Path, output_dir: Path, repetitions: int) -> dict[str, Any]:
    runs, validation = load_runs(root)
    screening = {}
    row_sets = {}
    for maximum_alpha in MAXIMUM_ALPHAS:
        for minimum_fold_gain in MINIMUM_FOLD_GAINS:
            key = f"maximum_alpha={maximum_alpha}|minimum_fold_gain={minimum_fold_gain}"
            rows = materialize(runs, maximum_alpha, minimum_fold_gain)
            suites = suite_means(rows)
            gains = [value for values in suites.values() for value in values.values()]
            screening[key] = {
                "maximum_alpha": maximum_alpha,
                "minimum_fold_gain": minimum_fold_gain,
                "minimum_suite_metric_gain": float(min(gains)),
                "mean_suite_metric_gain": float(np.mean(gains)),
                "suite_metric_gains": suites,
                "endpoint_counts": dict(
                    Counter(row["candidate_selected"] for row in rows)
                ),
            }
            row_sets[key] = rows
    selected_key = max(
        screening,
        key=lambda key: (
            screening[key]["minimum_suite_metric_gain"],
            screening[key]["mean_suite_metric_gain"],
            -screening[key]["maximum_alpha"],
            -abs(screening[key]["minimum_fold_gain"]),
        ),
    )
    selected = screening[selected_key]
    rows = row_sets[selected_key]
    combined = aggregate(rows, repetitions, 20260718)
    freeze = bool(
        validation["passes"]
        and selected["minimum_suite_metric_gain"] >= -1e-12
        and selected["endpoint_counts"].get(CANDIDATE, 0) >= 3
        and all(
            combined["metrics"][metric]["oriented_mean_improvement"] > 0.0
            for metric in UNKNOWN_METRICS
        )
    )
    report = {
        "schema_version": "strict_v4_boundary_pseudo_unknown_development_v1",
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
            "schema_version": "strict_v4_boundary_pseudo_unknown_candidate_v1",
            "status": "frozen_unconfirmed",
            "candidate": {
                "name": "nested_boundary_pseudo_unknown_blend_v1",
                "risk_selection": "nested_boundary_pseudo_unknown_blend",
                "maximum_alpha": selected["maximum_alpha"],
                "minimum_fold_gain": selected["minimum_fold_gain"],
                "hard_pseudo_fraction": 0.5,
                "interpolation": 0.5,
                "max_per_task": 512,
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
            },
            "confirmation": {
                "seeds": [107, 109],
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
                "scenario_disjoint_from_boundary_development": True,
                "scenario_boundary": (
                    "scenarios are disjoint from boundary-candidate development and "
                    "all caches use new seeds; scenarios may appear in earlier unrelated policies"
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
        "# Strict-v4 boundary pseudo-unknown development",
        "",
        f"State: **{report['state']}**; runs: {report['validation']['run_count']}.",
        f"Maximum alpha: `{selected['maximum_alpha']}`; minimum fold gain: "
        f"`{selected['minimum_fold_gain']}`.",
        f"Endpoint counts: `{selected['endpoint_counts']}`.",
        "",
        "| Suite | AUROC | AUPR | FPR95 oriented | OSCR |",
        "|---|---:|---:|---:|---:|",
    ]
    for suite, values in selected["suite_metric_gains"].items():
        lines.append(
            f"| {suite} | {values['unknown_auroc']:+.6f} | "
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
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    args = parser.parse_args()
    report = analyze(
        args.root,
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
