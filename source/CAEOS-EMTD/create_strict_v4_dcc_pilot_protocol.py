from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


SMOKE_EXCLUSIONS = {"cic_iot2023/ddos_pshack_flood"}


def load_metrics(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def combined_fingerprint(metrics: dict[str, Any]) -> str:
    value = metrics.get("split_metadata", {}).get("split_fingerprint", {}).get("combined")
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
        raise ValueError("DCC pilot requires the seven-suite coverage registry")
    selected: dict[str, list[str]] = {}
    for suite, entry in sorted(registry.items()):
        candidates = [
            str(scenario)
            for scenario in entry.get("scenarios", [])
            if f"{suite}/{scenario}" not in SMOKE_EXCLUSIONS
        ]
        if len(candidates) < 2:
            raise ValueError(f"suite {suite} lacks two non-smoke pilot scenarios")
        selected[suite] = sorted(
            candidates,
            key=lambda scenario: hashlib.sha256(
                f"{manifest_sha}:{suite}:{scenario}:dcc_v1".encode("utf-8")
            ).hexdigest(),
        )[:2]
    return selected


def create_protocol(
    coverage: dict[str, Any],
    coverage_sha256: str,
    mlp_root: Path,
    opendetect_root: Path,
    mahalanobis_pp_root: Path,
    implementation_paths: dict[str, Path],
) -> dict[str, Any]:
    selected = select_scenarios(coverage)
    if sum(map(len, selected.values())) != 14 or len(selected) != 7:
        raise ValueError("DCC pilot requires two scenarios from each of seven suites")

    sources: dict[str, Any] = {}
    for suite, scenarios in sorted(selected.items()):
        for scenario in sorted(scenarios):
            key = f"{suite}/{scenario}"
            relative = Path(suite) / f"{scenario}_seed7_mlp"
            comparator_relative = Path(suite) / f"{scenario}_seed7_opendetect"
            pp_relative = Path(suite) / f"{scenario}_seed7_mahalanobis_pp"
            mlp_paths = {
                name: mlp_root / relative / name
                for name in ("metrics.json", "scores.npz", "model.pt")
            }
            comparator_paths = {
                name: opendetect_root / comparator_relative / name
                for name in ("metrics.json", "scores.npz", "model.pt")
            }
            pp_paths = {
                name: mahalanobis_pp_root / pp_relative / name
                for name in ("metrics.json", "scores.npz", "provenance.json")
            }
            missing = [
                str(path)
                for path in (*mlp_paths.values(), *comparator_paths.values(), *pp_paths.values())
                if not path.is_file()
            ]
            if missing:
                raise FileNotFoundError("missing frozen DCC pilot sources: " + ", ".join(missing))
            mlp_metrics = load_metrics(mlp_paths["metrics.json"])
            comparator_metrics = load_metrics(comparator_paths["metrics.json"])
            pp_metrics = load_metrics(pp_paths["metrics.json"])
            if mlp_metrics.get("model") != "mlp" or "mahalanobis" not in mlp_metrics.get("reports", {}):
                raise ValueError(f"invalid frozen MLP source for {key}")
            if comparator_metrics.get("model") != "opendetect" or set(comparator_metrics.get("reports", {})) != {"opendetect"}:
                raise ValueError(f"invalid frozen OpenDetect source for {key}")
            if set(pp_metrics.get("reports", {})) != {"mahalanobis_pp"}:
                raise ValueError(f"invalid frozen Mahalanobis++ source for {key}")
            fingerprints = {
                combined_fingerprint(mlp_metrics),
                combined_fingerprint(comparator_metrics),
                combined_fingerprint(pp_metrics),
            }
            if len(fingerprints) != 1:
                raise ValueError(f"MLP/comparator split mismatch for {key}")
            sources[key] = {
                "mlp_relative_path": relative.as_posix(),
                "opendetect_relative_path": comparator_relative.as_posix(),
                "mahalanobis_pp_relative_path": pp_relative.as_posix(),
                "split_fingerprint": fingerprints.pop(),
                "mlp_artifact_sha256": {name: file_hash(path) for name, path in mlp_paths.items()},
                "opendetect_artifact_sha256": {name: file_hash(path) for name, path in comparator_paths.items()},
                "mahalanobis_pp_artifact_sha256": {name: file_hash(path) for name, path in pp_paths.items()},
            }

    missing_implementations = [str(path) for path in implementation_paths.values() if not path.is_file()]
    if missing_implementations:
        raise FileNotFoundError("missing DCC implementations: " + ", ".join(missing_implementations))
    protocol = {
        "schema_version": "strict_v4_dcc_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "method": "dcc",
        "paper": "https://proceedings.mlr.press/v267/guo25m.html",
        "official_code": "https://github.com/workerbcd/ooddcc",
        "venue": "ICML 2025",
        "scope": "development_budget_screen_not_confirmatory_inference",
        "selection_rule": (
            "two minimum SHA256 identities per suite from the frozen coverage registry "
            "after excluding the isolated implementation smoke; independent of DCC results"
        ),
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_manifest_file_sha256": coverage_sha256,
        "excluded_observed_smoke_scenarios": sorted(SMOKE_EXCLUSIONS),
        "selected_scenarios": selected,
        "expected_scenarios": 14,
        "seed": 7,
        "mlp_root": str(mlp_root.resolve()),
        "opendetect_root": str(opendetect_root.resolve()),
        "mahalanobis_pp_root": str(mahalanobis_pp_root.resolve()),
        "sources": sources,
        "fit_data": "known_training_features_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_development_metrics_and_prefrozen_expansion_gate_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "method_definition": {
            "feature_transform": "row_wise_l2_normalization",
            "dynamic_covariance": "known_train_covariance_minus_query_residual_projection_outer_product",
            "requested_residual_dimension": 50,
            "effective_residual_dimension": "min(50,d-1)",
            "ridge": 1e-6,
            "relative_eigenvalue_floor": 1e-8,
            "epsilon": 1e-12,
            "parameters_frozen_without_ood_validation": True,
        },
        "expansion_gate": {
            "all_14_runs_complete": True,
            "failure_count": 0,
            "split_and_source_sha_checks_pass": True,
            "known_f1_max_absolute_difference_from_source_mlp": 1e-12,
            "four_unknown_metric_oriented_mean_gain_vs_mahalanobis_pp_minimum": 0.0,
            "suite_nonnegative_gain_count_vs_mahalanobis_pp_minimum": 5,
            "mean_unknown_metric_rank_among_four_maximum": 2.0,
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
    parser.add_argument("--mahalanobis-pp-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parent
    implementations = {
        "calibrator": root / "caeos" / "dynamic_covariance_calibration.py",
        "evaluator": root / "evaluate_mlp_dcc.py",
        "protocol_creator": Path(__file__).resolve(),
        "runner": root / "run_strict_v4_dcc_pilot.py",
        "summarizer": root / "summarize_strict_v4_dcc_pilot.py",
    }
    protocol = create_protocol(
        coverage,
        file_hash(args.coverage_manifest),
        args.mlp_root,
        args.opendetect_root,
        args.mahalanobis_pp_root,
        implementations,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.is_file():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing DCC pilot protocol differs from frozen inputs")
    else:
        args.output.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
