from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def combined_fingerprint(metrics: dict[str, Any]) -> str:
    value = (
        metrics.get("split_metadata", {})
        .get("split_fingerprint", {})
        .get("combined")
    )
    if not isinstance(value, str) or not value:
        raise ValueError("source metrics lack a combined split fingerprint")
    return value


def select_scenarios(coverage: dict[str, Any]) -> dict[str, list[str]]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage manifest schema")
    manifest_sha = coverage.get("manifest_sha256")
    if not isinstance(manifest_sha, str) or not manifest_sha:
        raise ValueError("coverage manifest lacks its frozen SHA")
    registry = coverage.get("scenario_registry", {})
    if len(registry) != 7:
        raise ValueError("WDiscOOD pilot requires the seven-suite coverage registry")
    selected: dict[str, list[str]] = {}
    for suite, entry in sorted(registry.items()):
        scenarios = [str(value) for value in entry.get("scenarios", [])]
        if len(scenarios) < 2:
            raise ValueError(f"suite {suite} lacks two WDiscOOD pilot scenarios")
        selected[suite] = sorted(
            scenarios,
            key=lambda scenario: hashlib.sha256(
                f"{manifest_sha}:{suite}:{scenario}:wdiscood_v1".encode("utf-8")
            ).hexdigest(),
        )[:2]
    return selected


def create_protocol(
    coverage: dict[str, Any],
    coverage_sha256: str,
    mlp_root: Path,
    opendetect_root: Path,
    implementation_paths: dict[str, Path],
) -> dict[str, Any]:
    selected = select_scenarios(coverage)
    if len(selected) != 7 or sum(map(len, selected.values())) != 14:
        raise ValueError("WDiscOOD pilot requires two scenarios from each suite")
    sources: dict[str, Any] = {}
    for suite, scenarios in sorted(selected.items()):
        for scenario in sorted(scenarios):
            key = f"{suite}/{scenario}"
            mlp_relative = Path(suite) / f"{scenario}_seed7_mlp"
            comparator_relative = Path(suite) / f"{scenario}_seed7_opendetect"
            mlp_run = mlp_root / mlp_relative
            comparator_run = opendetect_root / comparator_relative
            mlp_paths = {
                name: mlp_run / name for name in ("metrics.json", "scores.npz", "model.pt")
            }
            comparator_paths = {
                name: comparator_run / name
                for name in ("metrics.json", "scores.npz", "model.pt")
            }
            missing = [
                str(path)
                for path in (*mlp_paths.values(), *comparator_paths.values())
                if not path.is_file()
            ]
            if missing:
                raise FileNotFoundError("missing frozen WDiscOOD sources: " + ", ".join(missing))
            mlp_metrics = json.loads(mlp_paths["metrics.json"].read_text(encoding="utf-8"))
            comparator_metrics = json.loads(
                comparator_paths["metrics.json"].read_text(encoding="utf-8")
            )
            if mlp_metrics.get("model") != "mlp" or "mahalanobis" not in mlp_metrics.get("reports", {}):
                raise ValueError(f"invalid frozen MLP source for {key}")
            if comparator_metrics.get("model") != "opendetect" or set(
                comparator_metrics.get("reports", {})
            ) != {"opendetect"}:
                raise ValueError(f"invalid frozen OpenDetect source for {key}")
            fingerprint = combined_fingerprint(mlp_metrics)
            if fingerprint != combined_fingerprint(comparator_metrics):
                raise ValueError(f"MLP/OpenDetect split mismatch for {key}")
            sources[key] = {
                "mlp_relative_path": mlp_relative.as_posix(),
                "opendetect_relative_path": comparator_relative.as_posix(),
                "split_fingerprint": fingerprint,
                "mlp_artifact_sha256": {
                    name: file_hash(path) for name, path in mlp_paths.items()
                },
                "opendetect_artifact_sha256": {
                    name: file_hash(path) for name, path in comparator_paths.items()
                },
            }
    missing = [str(path) for path in implementation_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing WDiscOOD implementations: " + ", ".join(missing))
    protocol = {
        "schema_version": "strict_v4_wdiscood_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "method": "wdiscood",
        "paper": "https://openaccess.thecvf.com/content/ICCV2023/html/Chen_WDiscOOD_Out-of-Distribution_Detection_via_Whitened_Linear_Discriminant_Analysis_ICCV_2023_paper.html",
        "official_code": "https://github.com/ivalab/WDiscOOD",
        "venue": "ICCV 2023",
        "scope": "development_budget_screen_not_confirmatory_inference",
        "selection_rule": (
            "two minimum SHA256 scenario identities per suite from the frozen coverage "
            "registry; selection is independent of all WDiscOOD results"
        ),
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_manifest_file_sha256": coverage_sha256,
        "selected_scenarios": selected,
        "expected_scenarios": 14,
        "seed": 7,
        "mlp_root": str(mlp_root.resolve()),
        "opendetect_root": str(opendetect_root.resolve()),
        "sources": sources,
        "fit_data": "known_training_features_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_development_metrics_and_prefrozen_expansion_gate_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "method_definition": {
            "feature_space": "frozen_mlp_prelogit_embedding",
            "whitening": "pooled_known_train_within_class_covariance",
            "discriminant_dimension": "min(known_class_count_minus_one, embedding_dimension_minus_one)",
            "wd_score": "nearest_known_class_center_euclidean_distance",
            "wdr_score": "distance_to_known_train_residual_center",
            "alpha": 1.0,
            "alpha_selection": "fixed_a_priori_without_unknown_data",
            "ridge": 1e-6,
        },
        "expansion_gate": {
            "all_14_runs_complete": True,
            "failure_count": 0,
            "split_and_source_sha_checks_pass": True,
            "known_f1_max_absolute_difference_from_source_mlp": 1e-12,
            "four_unknown_metric_oriented_mean_gain_vs_mahalanobis_minimum": 0.0,
            "suite_nonnegative_gain_count_vs_mahalanobis_minimum": 5,
            "mean_unknown_metric_rank_among_three_maximum": 2.0,
            "all_checks_required": True,
        },
        "implementation_sha256": {
            name: file_hash(path) for name, path in sorted(implementation_paths.items())
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parent
    implementations = {
        "calibrator": root / "caeos" / "wdiscood.py",
        "evaluator": root / "evaluate_mlp_wdiscood.py",
        "protocol_creator": Path(__file__).resolve(),
        "runner": root / "run_strict_v4_wdiscood_pilot.py",
        "summarizer": root / "summarize_strict_v4_wdiscood_pilot.py",
    }
    protocol = create_protocol(
        coverage,
        file_hash(args.coverage_manifest),
        args.mlp_root,
        args.opendetect_root,
        implementations,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.is_file():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing WDiscOOD pilot protocol differs from frozen inputs")
    else:
        args.output.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
