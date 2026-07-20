from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from summarize_paired_confirmation import METRICS, aggregate


REFERENCE = "cauchy_modality_support_union"
CANDIDATE = "pseudo_unknown_learned_blend"
UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
DEVELOPMENT_SCENARIOS = {
    "cic_ton_iot": ("injection", "password", "scanning"),
    "cic_iot2023": (
        "browser_hijacking",
        "ddos_http_flood",
        "recon_host_discovery",
    ),
}
CONFIRMATION_SCENARIOS = {
    "cic_ton_iot": ("backdoor", "ddos", "dos"),
    "cic_iot2023": (
        "command_injection",
        "mirai_greip_flood",
        "vulnerability_scan",
    ),
}
REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)


def canonical_hash(payload: dict[str, Any]) -> str:
    value = {key: item for key, item in payload.items() if key != "manifest_sha256"}
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric_report(value: object, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"missing metric report for {label}")
    missing = [metric for metric in METRICS if metric not in value]
    if missing:
        raise ValueError(f"metric report for {label} misses {missing}")
    return {metric: float(value[metric]) for metric in METRICS}


def validate_pseudo_unknown_protocol(
    payload: dict[str, Any],
    label: str,
    expected_maximum_alpha: float | None = None,
) -> dict[str, Any]:
    arguments = payload.get("arguments", {})
    if arguments.get("risk_selection") != "nested_pseudo_unknown_blend":
        raise ValueError(f"risk selection mismatch for {label}")
    details = payload.get("risk_selection_details", {})
    if details.get("unknown_or_test_labels_used_for_selection") is not False:
        raise ValueError(f"runtime leakage guard failed for {label}")
    learned = details.get("pseudo_unknown_learned_blend", {})
    if learned.get("unknown_or_test_labels_used") is not False:
        raise ValueError(f"pseudo-unknown leakage declaration failed for {label}")
    if learned.get("pseudo_unknown_source") != "known validation attack labels only":
        raise ValueError(f"pseudo-unknown source mismatch for {label}")
    folds = learned.get("folds", [])
    if len(folds) < 3:
        raise ValueError(f"fewer than three cross-fitting folds for {label}")
    for fold in folds:
        if fold.get("task") in fold.get("training_tasks", []):
            raise ValueError(f"cross-fitting leakage for {label}/{fold.get('task')}")
    weights = details.get("learned_nonnegative_weights", {})
    features = details.get("learned_feature_names", [])
    if list(weights) != list(features):
        raise ValueError(f"learned feature/weight order mismatch for {label}")
    if any(float(value) < 0.0 for value in weights.values()):
        raise ValueError(f"negative learned weight for {label}")
    if abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-6:
        raise ValueError(f"learned weights do not sum to one for {label}")
    selected = payload.get("selected_risk")
    if selected not in {REFERENCE, CANDIDATE}:
        raise ValueError(f"unexpected selected risk for {label}: {selected!r}")
    expected = CANDIDATE if learned.get("passes") else REFERENCE
    if selected != expected:
        raise ValueError(f"internal gate/endpoint mismatch for {label}")
    observed_maximum_alpha = float(
        details.get(
            "pseudo_unknown_max_alpha",
            arguments.get("pseudo_unknown_max_alpha", 1.0),
        )
    )
    if float(learned.get("selected_alpha", 0.0)) > observed_maximum_alpha + 1e-12:
        raise ValueError(f"selected alpha exceeds configured maximum for {label}")
    if (
        expected_maximum_alpha is not None
        and abs(observed_maximum_alpha - expected_maximum_alpha) > 1e-12
    ):
        raise ValueError(f"maximum alpha mismatch for {label}")
    return {
        "fold_count": len(folds),
        "gate_passes": bool(learned.get("passes")),
        "selected_alpha": float(learned.get("selected_alpha", 0.0)),
        "configured_maximum_alpha": observed_maximum_alpha,
    }


def replay_policy_report(
    directory: Path, payload: dict[str, Any], maximum_alpha: float
) -> tuple[dict[str, float], float]:
    learned = payload["risk_selection_details"]["pseudo_unknown_learned_blend"]
    original_alpha = float(learned.get("selected_alpha", 0.0))
    replay_alpha = min(original_alpha, float(maximum_alpha))
    archive = np.load(directory / "scores.npz")
    validation_reference = archive["validation_cauchy_modality_support_union"]
    test_reference = archive["test_cauchy_modality_support_union"]
    if original_alpha <= 0.0:
        validation_risk = validation_reference
        test_risk = test_reference
    else:
        validation_original = archive["validation_pseudo_unknown_learned_blend"]
        test_original = archive["test_pseudo_unknown_learned_blend"]
        validation_learned = (
            validation_original - (1.0 - original_alpha) * validation_reference
        ) / original_alpha
        test_learned = (
            test_original - (1.0 - original_alpha) * test_reference
        ) / original_alpha
        validation_risk = (
            (1.0 - replay_alpha) * validation_reference
            + replay_alpha * validation_learned
        )
        test_risk = (
            (1.0 - replay_alpha) * test_reference + replay_alpha * test_learned
        )
    threshold = float(
        np.quantile(
            validation_risk,
            float(payload.get("arguments", {}).get("known_acceptance", 0.95)),
        )
    )
    report = evaluate_hybrid_open_set(
        archive["test_labels"],
        archive["test_unknown"],
        archive["test_prediction"],
        test_risk,
        threshold,
    )
    return metric_report(report, "replayed policy"), replay_alpha


def build_rows(
    root: Path, maximum_alpha: float = 1.0
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    audit_rows = []
    fingerprints = set()
    source_metrics = []
    for suite, scenarios in DEVELOPMENT_SCENARIOS.items():
        for scenario in scenarios:
            directory = root / suite / f"{scenario}_seed7"
            missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()]
            if missing:
                raise ValueError(f"missing artifacts under {directory}: {missing}")
            path = directory / "metrics.json"
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8"))
            if int(payload.get("seed", -1)) != 7:
                raise ValueError(f"seed mismatch under {directory}")
            protocol = validate_pseudo_unknown_protocol(payload, f"{suite}/{scenario}")
            reports = payload.get("reports", {})
            original_selected = str(payload["selected_risk"])
            original_report = metric_report(
                reports.get(original_selected), f"{suite}/{scenario}/original policy"
            )
            candidate, replay_alpha = replay_policy_report(
                directory, payload, maximum_alpha
            )
            selected = CANDIDATE if replay_alpha > 0.0 else REFERENCE
            reference = metric_report(reports.get(REFERENCE), f"{suite}/{scenario}/reference")
            if metric_report(payload.get("selected_report"), "selected_report") != original_report:
                raise ValueError(f"selected report mismatch under {directory}")
            fingerprint = payload.get("split_metadata", {}).get("split_fingerprint", {}).get("combined")
            if not fingerprint:
                raise ValueError(f"missing split fingerprint under {directory}")
            fingerprints.add(str(fingerprint))
            source_metrics.append(
                {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(raw).hexdigest()}
            )
            rows.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "seed": 7,
                    "candidate_selected": selected,
                    "reference_selected": REFERENCE,
                    "candidate_report": candidate,
                    "reference_report": reference,
                    "split_fingerprint": str(fingerprint),
                }
            )
            audit_rows.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "maximum_alpha": float(maximum_alpha),
                    "replay_alpha": float(replay_alpha),
                    **protocol,
                }
            )
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": len(rows),
        "seed": 7,
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "runtime_uses_unknown_or_test_labels": False,
        "development_aggregate_uses_opened_unknown_test_labels": True,
        "replayed_maximum_alpha": float(maximum_alpha),
        "audit_rows": audit_rows,
    }


def positive_metrics(report: dict[str, Any]) -> dict[str, bool]:
    return {
        metric: report["metrics"][metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 pseudo-unknown risk development",
        "",
        f"State: **{report['state']}**; runs: {report['validation']['run_count']}; "
        f"candidate endpoints: `{report['endpoint_counts']}`.",
        f"Frozen maximum alpha: `{report['selected_maximum_alpha']}`.",
        "Opened unknown test outcomes are development evidence only.",
        "",
        "| Suite | AUROC | AUPR | FPR95 oriented | OSCR | Pass |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for suite, values in report["by_suite"].items():
        gains = values["metrics"]
        passed = all(report["suite_positive"][suite].values())
        lines.append(
            f"| {suite} | {gains['unknown_auroc']['oriented_mean_improvement']:+.6f} | "
            f"{gains['unknown_aupr']['oriented_mean_improvement']:+.6f} | "
            f"{gains['unknown_fpr95']['oriented_mean_improvement']:+.6f} | "
            f"{gains['oscr']['oriented_mean_improvement']:+.6f} | {str(passed).lower()} |"
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


def analyze(root: Path, project_root: Path, repetitions: int, seed: int) -> dict[str, Any]:
    screening = {}
    candidates = (0.05, 0.1, 0.25, 0.5, 0.75, 1.0)
    materialized = {}
    for maximum_alpha in candidates:
        candidate_rows, candidate_validation = build_rows(root, maximum_alpha)
        candidate_combined = aggregate(candidate_rows, repetitions, seed)
        candidate_suites = {
            suite: aggregate(
                [row for row in candidate_rows if row["suite"] == suite],
                repetitions,
                seed,
            )
            for suite in DEVELOPMENT_SCENARIOS
        }
        suite_metric_gains = [
            values["metrics"][metric]["oriented_mean_improvement"]
            for values in candidate_suites.values()
            for metric in UNKNOWN_METRICS
        ]
        global_metric_gains = [
            candidate_combined["metrics"][metric]["oriented_mean_improvement"]
            for metric in UNKNOWN_METRICS
        ]
        screening[str(maximum_alpha)] = {
            "minimum_suite_metric_mean_gain": float(min(suite_metric_gains)),
            "mean_global_metric_gain": float(np.mean(global_metric_gains)),
            "suite_metric_gains": {
                suite: {
                    metric: values["metrics"][metric]["oriented_mean_improvement"]
                    for metric in UNKNOWN_METRICS
                }
                for suite, values in candidate_suites.items()
            },
        }
        materialized[maximum_alpha] = (
            candidate_rows,
            candidate_validation,
            candidate_combined,
            candidate_suites,
        )
    selected_maximum_alpha = max(
        candidates,
        key=lambda value: (
            screening[str(value)]["minimum_suite_metric_mean_gain"],
            screening[str(value)]["mean_global_metric_gain"],
            -value,
        ),
    )
    rows, validation, combined, by_suite = materialized[selected_maximum_alpha]
    combined_positive = positive_metrics(combined)
    suite_positive = {suite: positive_metrics(value) for suite, value in by_suite.items()}
    freeze = bool(
        validation["passes"]
        and all(combined_positive.values())
        and all(value for values in suite_positive.values() for value in values.values())
    )
    report = {
        "schema_version": "strict_v4_pseudo_unknown_development_v1",
        "state": "frozen_unconfirmed" if freeze else "rejected_development",
        "freeze_candidate": freeze,
        "validation": validation,
        "combined": combined,
        "by_suite": by_suite,
        "combined_positive": combined_positive,
        "suite_positive": suite_positive,
        "endpoint_counts": dict(Counter(row["candidate_selected"] for row in rows)),
        "selected_maximum_alpha": float(selected_maximum_alpha),
        "shrinkage_screening": screening,
        "rows": rows,
    }
    if freeze:
        implementation_files = (
            project_root / "caeos" / "pseudo_unknown_risk.py",
            project_root / "train_hybrid_open_set.py",
            project_root / "run_nested_gate_matrix.py",
        )
        manifest = {
            "schema_version": "strict_v4_pseudo_unknown_candidate_v1",
            "status": "frozen_unconfirmed",
            "candidate": {
                "name": "nested_pseudo_unknown_blend_v1",
                "risk_selection": "nested_pseudo_unknown_blend",
                "reference": REFERENCE,
                "candidate_endpoint": CANDIDATE,
                "maximum_alpha": float(selected_maximum_alpha),
                "implementation_sha256": {
                    path.relative_to(project_root).as_posix(): file_hash(path)
                    for path in implementation_files
                },
                "runtime_uses_known_training_and_validation_only": True,
                "runtime_uses_unknown_or_test_labels": False,
            },
            "development": {
                "seed": 7,
                "scenarios": {key: list(value) for key, value in DEVELOPMENT_SCENARIOS.items()},
                "aggregate_uses_opened_unknown_test_labels": True,
                "source_metrics_combined_sha256": validation["source_metrics_combined_sha256"],
            },
            "confirmation": {
                "seeds": [73, 79],
                "scenarios": {key: list(value) for key, value in CONFIRMATION_SCENARIOS.items()},
                "expected_run_count": 12,
                "expected_scenario_count": 6,
                "seed_disjoint": True,
                "scenario_disjoint_from_candidate_development": True,
                "scenario_boundary": "new attack classes for this candidate and new cache seeds",
            },
        }
        manifest["manifest_sha256"] = canonical_hash(manifest)
        report["manifest_sha256"] = manifest["manifest_sha256"]
        report["candidate_manifest"] = manifest
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze strict-v4 pseudo-unknown risk candidate")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260718)
    args = parser.parse_args()
    report = analyze(args.root, args.project_root.resolve(), args.bootstrap_repetitions, args.bootstrap_seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render_markdown(report), encoding="utf-8")
    if report.get("candidate_manifest"):
        (args.output_dir / "candidate_manifest.json").write_text(
            json.dumps(report["candidate_manifest"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"state": report["state"], "manifest": report.get("manifest_sha256")}, indent=2))


if __name__ == "__main__":
    main()
