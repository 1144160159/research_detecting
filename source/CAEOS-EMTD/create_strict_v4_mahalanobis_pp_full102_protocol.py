from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from create_strict_v4_mahalanobis_pp_pilot_protocol import combined_fingerprint, load_metrics


def create_protocol(
    coverage: dict[str, Any],
    coverage_file_sha256: str,
    pilot_protocol: dict[str, Any],
    pilot_protocol_file_sha256: str,
    pilot_analysis: dict[str, Any],
    pilot_analysis_file_sha256: str,
    mlp_root: Path,
    opendetect_root: Path,
    implementation_paths: dict[str, Path],
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage manifest schema")
    if pilot_protocol.get("schema_version") != "strict_v4_mahalanobis_pp_pilot_protocol_v1":
        raise ValueError("unexpected Mahalanobis++ pilot protocol schema")
    if pilot_protocol.get("manifest_sha256") != canonical_hash(pilot_protocol):
        raise ValueError("Mahalanobis++ pilot protocol SHA mismatch")
    if pilot_protocol.get("coverage_manifest_sha256") != coverage.get("manifest_sha256"):
        raise ValueError("pilot protocol coverage binding mismatch")
    if pilot_analysis.get("schema_version") != "strict_v4_mahalanobis_pp_pilot_analysis_v1":
        raise ValueError("unexpected Mahalanobis++ pilot analysis schema")
    if pilot_analysis.get("protocol_manifest_sha256") != pilot_protocol.get(
        "manifest_sha256"
    ):
        raise ValueError("pilot analysis protocol binding mismatch")
    if pilot_analysis.get("decision", {}).get("expand_to_full102") is not True:
        raise ValueError("Mahalanobis++ did not pass its frozen full102 expansion gate")
    validation = pilot_analysis.get("validation", {})
    if (
        validation.get("passes") is not True
        or validation.get("scenario_count") != 14
        or validation.get("failure_count") != 0
        or validation.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False
    ):
        raise ValueError("Mahalanobis++ pilot validation is incomplete or unsafe")

    sources: dict[str, Any] = {}
    registry = coverage.get("scenario_registry", {})
    for suite, entry in sorted(registry.items()):
        for scenario in entry.get("scenarios", []):
            scenario = str(scenario)
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
                for path in list(mlp_paths.values()) + list(comparator_paths.values())
                if not path.is_file()
            ]
            if missing:
                raise FileNotFoundError("missing frozen full102 sources: " + ", ".join(missing))
            mlp_metrics = load_metrics(mlp_paths["metrics.json"])
            comparator_metrics = load_metrics(comparator_paths["metrics.json"])
            if mlp_metrics.get("model") != "mlp" or "mahalanobis" not in mlp_metrics.get(
                "reports", {}
            ):
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
    expected = int(coverage.get("expected_runs", {}).get("per_method", 102))
    if expected != 102 or len(sources) != expected:
        raise ValueError(f"Mahalanobis++ full source coverage mismatch: {len(sources)}/{expected}")
    missing_implementations = [
        str(path) for path in implementation_paths.values() if not path.is_file()
    ]
    if missing_implementations:
        raise FileNotFoundError(
            "missing Mahalanobis++ full implementations: "
            + ", ".join(missing_implementations)
        )
    protocol = {
        "schema_version": "strict_v4_mahalanobis_pp_full102_protocol_v1",
        "status": "frozen_before_full102_results",
        "method": "mahalanobis_pp",
        "paper": "https://arxiv.org/abs/2505.18032",
        "venue": "ICML 2025",
        "scope": "seed7_development_full_screen_not_confirmatory_inference",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_manifest_file_sha256": coverage_file_sha256,
        "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
        "pilot_protocol_file_sha256": pilot_protocol_file_sha256,
        "pilot_analysis_file_sha256": pilot_analysis_file_sha256,
        "pilot_expansion_checks": pilot_analysis["expansion_checks"],
        "expected_scenarios": 102,
        "seed": 7,
        "mlp_root": str(mlp_root.resolve()),
        "opendetect_root": str(opendetect_root.resolve()),
        "sources": sources,
        "fit_data": "known_training_features_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_seed7_development_metrics_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "method_definition": pilot_protocol["method_definition"],
        "comparator_rule": (
            "merge into the existing 28-method table and select the non-CAEOS method "
            "with minimum four-unknown-metric mean rank, then higher AUROC"
        ),
        "implementation_sha256": {
            name: file_hash(path) for name, path in sorted(implementation_paths.items())
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    pilot_protocol = json.loads(args.pilot_protocol.read_text(encoding="utf-8"))
    pilot_analysis = json.loads(args.pilot_analysis.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parent
    implementations = {
        "calibrator": root / "caeos" / "mahalanobis_pp.py",
        "evaluator": root / "evaluate_mlp_mahalanobis_pp.py",
        "full_protocol_creator": Path(__file__).resolve(),
        "full_runner": root / "run_strict_v4_mahalanobis_pp_full102.py",
        "full_summarizer": root / "summarize_strict_v4_mahalanobis_pp_full102.py",
        "pilot_runner_helper": root / "run_strict_v4_mahalanobis_pp_pilot.py",
    }
    protocol = create_protocol(
        coverage,
        file_hash(args.coverage_manifest),
        pilot_protocol,
        file_hash(args.pilot_protocol),
        pilot_analysis,
        file_hash(args.pilot_analysis),
        args.mlp_root,
        args.opendetect_root,
        implementations,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.is_file():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing Mahalanobis++ full102 protocol differs from frozen inputs")
    else:
        args.output.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
