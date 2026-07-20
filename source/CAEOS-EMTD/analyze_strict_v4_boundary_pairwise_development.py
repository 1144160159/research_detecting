from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import analyze_strict_v4_boundary_pseudo_unknown_development as base


RISK_SELECTION = "nested_boundary_pairwise_pseudo_unknown_blend"
EXPECTED_OBJECTIVE = "pairwise_logistic_ranking"


def load_runs(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runs = []
    source = []
    fingerprints = set()
    for suite, scenarios in base.SCENARIOS.items():
        for scenario in scenarios:
            directory = root / suite / f"{scenario}_seed7"
            missing = [
                name for name in base.REQUIRED_ARTIFACTS if not (directory / name).is_file()
            ]
            if missing:
                raise ValueError(f"missing artifacts under {directory}: {missing}")
            path = directory / "metrics.json"
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8"))
            if payload.get("arguments", {}).get("risk_selection") != RISK_SELECTION:
                raise ValueError(f"pairwise boundary policy mismatch under {directory}")
            learned = payload["risk_selection_details"]["pseudo_unknown_learned_blend"]
            if learned.get("unknown_or_test_labels_used") is not False:
                raise ValueError(f"pairwise boundary leakage declaration failed under {directory}")
            if learned.get("pseudo_unknown_source") != (
                "known validation attack labels plus known-only boundary interpolation"
            ):
                raise ValueError(f"pairwise boundary source mismatch under {directory}")
            if learned.get("training_objective") != "pairwise":
                raise ValueError(f"pairwise objective selector mismatch under {directory}")
            distribution = learned.get("training_distribution", {})
            if distribution.get("enabled") is not True:
                raise ValueError(f"pairwise boundary distribution missing under {directory}")
            if distribution.get("objective") != EXPECTED_OBJECTIVE:
                raise ValueError(f"pairwise training distribution mismatch under {directory}")
            if distribution.get("unknown_or_test_labels_used") is not False:
                raise ValueError(f"pairwise boundary distribution leakage under {directory}")
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
                    "reference_report": base.metric_report(
                        payload["reports"][base.REFERENCE], "reference"
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
        raise ValueError("pairwise boundary development requires six runs")
    return runs, {
        "passes": True,
        "run_count": len(runs),
        "scenario_count": len(runs),
        "seed": 7,
        "artifact_checks": len(runs) * len(base.REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "runtime_uses_unknown_or_test_labels": False,
        "development_aggregate_opens_unknown_test_outcomes": True,
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def pairwise_manifest(report: dict[str, Any], project_root: Path) -> dict[str, Any]:
    selected = report["selected_policy"]
    files = (
        project_root / "caeos" / "pseudo_unknown_risk.py",
        project_root / "train_hybrid_open_set.py",
        project_root / "run_nested_gate_matrix.py",
    )
    manifest = {
        "schema_version": "strict_v4_boundary_pairwise_candidate_v1",
        "status": "frozen_unconfirmed",
        "candidate": {
            "name": "nested_boundary_pairwise_pseudo_unknown_blend_v1",
            "risk_selection": RISK_SELECTION,
            "training_objective": "pairwise",
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
            "run_count": report["validation"]["run_count"],
            "source_metrics_combined_sha256": report["validation"][
                "source_metrics_combined_sha256"
            ],
            "selected_key": report["selected_key"],
        },
        "confirmation": {
            "seeds": [127, 131],
            "scenarios": {
                "cic_ton_iot": ["mitm", "ransomware", "xss"],
                "cic_iot2023": [
                    "ddos_ack_fragmentation",
                    "dictionary_bruteforce",
                    "recon_ping_sweep",
                ],
            },
            "expected_run_count": 12,
            "expected_scenario_count": 6,
            "seed_disjoint": True,
            "scenario_disjoint_from_pairwise_development": True,
            "scenario_boundary": (
                "scenarios are disjoint from pairwise-candidate development and all "
                "caches use new seeds; scenarios may appear in earlier unrelated policies"
            ),
        },
    }
    manifest["manifest_sha256"] = base.canonical_hash(manifest)
    return manifest


def render(report: dict[str, Any]) -> str:
    selected = report["selected_policy"]
    lines = [
        "# Strict-v4 pairwise boundary pseudo-unknown development",
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
    project_root = args.project_root.resolve()
    base.load_runs = load_runs
    report = base.analyze(
        args.root, project_root, args.output_dir, args.bootstrap_repetitions
    )
    report["schema_version"] = "strict_v4_boundary_pairwise_development_v1"
    if report["freeze_candidate"]:
        manifest = pairwise_manifest(report, project_root)
        report["manifest_sha256"] = manifest["manifest_sha256"]
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "candidate_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(report), encoding="utf-8")
    print(render(report))


if __name__ == "__main__":
    main()
