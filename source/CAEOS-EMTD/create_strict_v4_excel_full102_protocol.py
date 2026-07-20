from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def combined_fingerprint(metrics: dict[str, Any]) -> str:
    value = metrics.get("split_metadata", {}).get("split_fingerprint", {}).get("combined")
    if not isinstance(value, str) or not value:
        raise ValueError("source metrics lack a combined split fingerprint")
    return value


def create_protocol(
    coverage: dict[str, Any], coverage_file_sha256: str, mlp_root: Path,
    implementation_paths: dict[str, Path],
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage schema")
    if coverage.get("datasets") != 7 or coverage.get("scenario_inference_units") != 102:
        raise ValueError("ExCeL full102 requires the frozen seven-suite registry")
    sources: dict[str, Any] = {}
    for suite, entry in sorted(coverage.get("scenario_registry", {}).items()):
        scenarios = entry.get("scenarios", [])
        if len(scenarios) != entry.get("count"):
            raise ValueError(f"invalid scenario registry for {suite}")
        for scenario in scenarios:
            key = f"{suite}/{scenario}"
            relative = Path(suite) / f"{scenario}_seed7_mlp"
            run = mlp_root / relative
            paths = {name: run / name for name in ("metrics.json", "scores.npz", "model.pt")}
            missing = [str(path) for path in paths.values() if not path.is_file()]
            if missing:
                raise FileNotFoundError("missing frozen ExCeL source: " + ", ".join(missing))
            metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
            if metrics.get("model") != "mlp" or "max_logit" not in metrics.get("reports", {}):
                raise ValueError(f"invalid frozen MLP source for {key}")
            sources[key] = {
                "mlp_relative_path": relative.as_posix(),
                "split_fingerprint": combined_fingerprint(metrics),
                "mlp_artifact_sha256": {name: file_hash(path) for name, path in paths.items()},
            }
    if len(sources) != 102:
        raise ValueError(f"ExCeL source coverage mismatch: {len(sources)}/102")
    missing_implementations = [str(path) for path in implementation_paths.values() if not path.is_file()]
    if missing_implementations:
        raise FileNotFoundError("missing ExCeL implementations: " + ", ".join(missing_implementations))
    protocol = {
        "schema_version": "strict_v4_excel_full102_protocol_v1",
        "status": "frozen_before_any_excel_result",
        "method": "excel",
        "paper": "https://arxiv.org/abs/2311.14754",
        "venue": "TMLR 2025",
        "scope": "seed7_development_screen_not_confirmatory_inference",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_manifest_file_sha256": coverage_file_sha256,
        "expected_scenarios": 102,
        "seed": 7,
        "mlp_root": str(mlp_root.resolve()),
        "sources": sources,
        "method_definition": {
            "class_probability_matrix_fit": "correctly_classified_known_training_logits_only",
            "reward_a": 10.0,
            "high_probability_b": 5.0,
            "alpha": 0.8,
            "hyperparameter_policy": "paper_CIFAR100_ImageNet200_values_fixed_a_priori_no_ood_validation_tuning",
            "score": "negative_of_alpha_rank_score_plus_one_minus_alpha_max_logit",
        },
        "threshold_data": "known_validation_only",
        "test_labels": "final_development_metrics_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "implementation_sha256": {name: file_hash(path) for name, path in sorted(implementation_paths.items())},
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.result_root.exists() and any(args.result_root.glob("**/metrics.json")):
        raise ValueError("ExCeL protocol must be frozen before any formal result exists")
    root = Path(__file__).resolve().parent
    implementations = {
        "calibrator": root / "caeos" / "excel_ood.py",
        "evaluator": root / "evaluate_mlp_excel.py",
        "protocol_creator": Path(__file__).resolve(),
        "runner": root / "run_strict_v4_excel_full102.py",
        "summarizer": root / "summarize_strict_v4_excel_full102.py",
    }
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    protocol = create_protocol(coverage, file_hash(args.coverage_manifest), args.mlp_root, implementations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.is_file():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing ExCeL protocol differs from frozen inputs")
    else:
        args.output.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
