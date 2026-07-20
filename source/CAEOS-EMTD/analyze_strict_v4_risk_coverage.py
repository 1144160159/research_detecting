from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


QUANTILES = (0.95, 0.975)
COVERAGE_GRID = tuple(index / 20.0 for index in range(1, 21))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def selective_metrics(
    labels: np.ndarray,
    unknown: np.ndarray,
    predictions: np.ndarray,
    risk: np.ndarray,
    coverage_grid: tuple[float, ...] = COVERAGE_GRID,
) -> dict[str, Any]:
    labels = np.asarray(labels).reshape(-1)
    unknown = np.asarray(unknown, dtype=bool).reshape(-1)
    predictions = np.asarray(predictions).reshape(-1)
    risk = np.asarray(risk, dtype=np.float64).reshape(-1)
    size = len(labels)
    if size == 0 or any(len(values) != size for values in (unknown, predictions, risk)):
        raise ValueError("selective metric arrays must have the same non-zero length")
    if not np.isfinite(risk).all():
        raise ValueError("risk values must be finite")
    errors = unknown | ((~unknown) & (predictions != labels))
    order = np.argsort(risk, kind="mergesort")
    cumulative = np.cumsum(errors[order], dtype=np.float64) / np.arange(1, size + 1)
    oracle = np.cumsum(np.sort(errors.astype(np.float64))) / np.arange(1, size + 1)
    curve = {}
    for coverage in coverage_grid:
        if not 0.0 < coverage <= 1.0:
            raise ValueError("coverage grid values must be in (0, 1]")
        accepted = max(1, int(math.ceil(coverage * size)))
        curve[f"{coverage:.3f}"] = float(cumulative[accepted - 1])
    return {
        "aurc": float(cumulative.mean()),
        "oracle_aurc": float(oracle.mean()),
        "eaurc": float(cumulative.mean() - oracle.mean()),
        "base_open_set_error": float(errors.mean()),
        "selective_risk_by_coverage": curve,
    }


def fixed_operating_point(
    validation_risk: np.ndarray,
    labels: np.ndarray,
    unknown: np.ndarray,
    predictions: np.ndarray,
    test_risk: np.ndarray,
    quantile: float,
) -> dict[str, float]:
    validation_risk = np.asarray(validation_risk, dtype=np.float64).reshape(-1)
    labels = np.asarray(labels).reshape(-1)
    unknown = np.asarray(unknown, dtype=bool).reshape(-1)
    predictions = np.asarray(predictions).reshape(-1)
    test_risk = np.asarray(test_risk, dtype=np.float64).reshape(-1)
    if not 0.0 < quantile < 1.0:
        raise ValueError("known acceptance quantile must be in (0, 1)")
    if len(validation_risk) == 0 or not np.isfinite(validation_risk).all():
        raise ValueError("validation risk must be finite and non-empty")
    if len(labels) == 0 or any(len(item) != len(labels) for item in (unknown, predictions, test_risk)):
        raise ValueError("test arrays must have the same non-zero length")
    threshold = float(np.quantile(validation_risk, quantile))
    accepted = test_risk <= threshold
    known = ~unknown
    accepted_known = accepted & known
    accepted_errors = unknown[accepted] | (predictions[accepted] != labels[accepted])
    open_set_correct = (accepted_known & (predictions == labels)) | ((~accepted) & unknown)
    return {
        "threshold": threshold,
        "coverage": float(accepted.mean()),
        "known_acceptance_rate": float(accepted[known].mean()),
        "unknown_rejection_rate": float((~accepted[unknown]).mean()),
        "known_accuracy_when_accepted": (
            float((predictions[accepted_known] == labels[accepted_known]).mean())
            if accepted_known.any()
            else 0.0
        ),
        "selective_risk": float(accepted_errors.mean()) if accepted.any() else 0.0,
        "open_set_accuracy": float(open_set_correct.mean()),
    }


def _fingerprint(payload: dict[str, Any]) -> str:
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    if value is None:
        raise ValueError("missing split fingerprint")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values))


def analyze_run(
    candidate_metrics_path: Path, comparator_metrics_path: Path
) -> dict[str, Any]:
    candidate = json.loads(candidate_metrics_path.read_text(encoding="utf-8"))
    comparator = json.loads(comparator_metrics_path.read_text(encoding="utf-8"))
    if _fingerprint(candidate) != _fingerprint(comparator):
        raise ValueError(f"split fingerprint mismatch: {candidate_metrics_path}")
    candidate_risk_name = candidate.get("selected_risk")
    if not isinstance(candidate_risk_name, str):
        raise ValueError(f"candidate selected_risk is missing: {candidate_metrics_path}")
    with np.load(candidate_metrics_path.parent / "scores.npz", allow_pickle=False) as scores:
        candidate_values = {
            "labels": scores["test_labels"].copy(),
            "unknown": scores["test_unknown"].astype(bool),
            "predictions": scores["test_prediction"].copy(),
            "validation_risk": scores[f"validation_{candidate_risk_name}"].copy(),
            "test_risk": scores[f"test_{candidate_risk_name}"].copy(),
        }
    with np.load(comparator_metrics_path.parent / "scores.npz", allow_pickle=False) as scores:
        comparator_values = {
            "labels": scores["test_labels"].copy(),
            "unknown": scores["test_unknown"].astype(bool),
            "predictions": scores["prediction_opendetect"].copy(),
            "validation_risk": scores["validation_opendetect"].copy(),
            "test_risk": scores["test_opendetect"].copy(),
        }
    np.testing.assert_array_equal(candidate_values["labels"], comparator_values["labels"])
    np.testing.assert_array_equal(candidate_values["unknown"], comparator_values["unknown"])

    methods = {}
    for name, values in (
        ("caeos_pairwise", candidate_values),
        ("opendetect", comparator_values),
    ):
        result = selective_metrics(
            values["labels"], values["unknown"], values["predictions"], values["test_risk"]
        )
        result["operating_points"] = {
            f"{quantile:.3f}": fixed_operating_point(
                values["validation_risk"],
                values["labels"],
                values["unknown"],
                values["predictions"],
                values["test_risk"],
                quantile,
            )
            for quantile in QUANTILES
        }
        methods[name] = result
    return {"candidate_selected_risk": candidate_risk_name, "methods": methods}


def aggregate(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    methods = {}
    for method in ("caeos_pairwise", "opendetect"):
        summary = {
            metric: _mean([block["methods"][method][metric] for block in blocks])
            for metric in ("aurc", "oracle_aurc", "eaurc", "base_open_set_error")
        }
        summary["selective_risk_by_coverage"] = {
            key: _mean(
                [block["methods"][method]["selective_risk_by_coverage"][key] for block in blocks]
            )
            for key in blocks[0]["methods"][method]["selective_risk_by_coverage"]
        }
        summary["operating_points"] = {}
        for quantile in (f"{value:.3f}" for value in QUANTILES):
            summary["operating_points"][quantile] = {
                metric: _mean(
                    [block["methods"][method]["operating_points"][quantile][metric] for block in blocks]
                )
                for metric in (
                    "coverage",
                    "known_acceptance_rate",
                    "unknown_rejection_rate",
                    "known_accuracy_when_accepted",
                    "selective_risk",
                    "open_set_accuracy",
                )
            }
        methods[method] = summary

    gains = {
        "aurc_reduction": methods["opendetect"]["aurc"] - methods["caeos_pairwise"]["aurc"],
        "eaurc_reduction": methods["opendetect"]["eaurc"] - methods["caeos_pairwise"]["eaurc"],
    }
    for quantile in (f"{value:.3f}" for value in QUANTILES):
        for metric in ("known_acceptance_rate", "unknown_rejection_rate", "known_accuracy_when_accepted", "open_set_accuracy"):
            gains[f"{metric}_{quantile}"] = (
                methods["caeos_pairwise"]["operating_points"][quantile][metric]
                - methods["opendetect"]["operating_points"][quantile][metric]
            )
        gains[f"selective_risk_reduction_{quantile}"] = (
            methods["opendetect"]["operating_points"][quantile]["selective_risk"]
            - methods["caeos_pairwise"]["operating_points"][quantile]["selective_risk"]
        )
    return {"methods": methods, "caeos_pairwise_oriented_gains": gains}


def render(report: dict[str, Any]) -> str:
    methods = report["aggregate"]["methods"]
    lines = [
        "# Strict-v4 seed7 risk-coverage analysis",
        "",
        "This is descriptive development evidence and does not select the final algorithm.",
        "",
        "| Method | AURC | EAURC | Q=.95 known accept | Q=.95 unknown reject | Q=.95 open-set accuracy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method in ("caeos_pairwise", "opendetect"):
        value = methods[method]
        point = value["operating_points"]["0.950"]
        lines.append(
            f"| {method} | {value['aurc']:.6f} | {value['eaurc']:.6f} | "
            f"{point['known_acceptance_rate']:.6f} | {point['unknown_rejection_rate']:.6f} | "
            f"{point['open_set_accuracy']:.6f} |"
        )
    lines.extend(["", "## CAEOS oriented gains", ""])
    for name, value in report["aggregate"]["caeos_pairwise_oriented_gains"].items():
        lines.append(f"- `{name}`: `{value:+.6f}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2" or coverage.get(
        "scenario_inference_units"
    ) != 102:
        raise ValueError("risk-coverage analysis requires the strict-v4 102-scenario registry")

    candidate_paths = sorted(args.candidate_root.glob("*/*_seed7/metrics.json"))
    if len(candidate_paths) != 102:
        raise ValueError(f"expected 102 CAEOS candidate reports, found {len(candidate_paths)}")
    pairs = []
    artifact_hashes = {}
    for candidate_path in candidate_paths:
        suite = candidate_path.parent.parent.name
        scenario = candidate_path.parent.name[: -len("_seed7")]
        comparator_path = (
            args.opendetect_root / suite / f"{scenario}_seed7_opendetect" / "metrics.json"
        )
        if not comparator_path.is_file():
            raise FileNotFoundError(comparator_path)
        pairs.append((suite, scenario, candidate_path, comparator_path))
        artifact_hashes[f"{suite}/{scenario}"] = {
            "candidate_metrics": sha256_file(candidate_path),
            "candidate_scores": sha256_file(candidate_path.parent / "scores.npz"),
            "opendetect_metrics": sha256_file(comparator_path),
            "opendetect_scores": sha256_file(comparator_path.parent / "scores.npz"),
        }

    protocol = {
        "schema_version": "strict_v4_seed7_risk_coverage_protocol_v1",
        "status": "frozen_before_risk_coverage_values_are_computed",
        "scope": "development_seed7_descriptive_only",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "scenario_count": len(pairs),
        "methods": ["caeos_pairwise", "opendetect"],
        "candidate_score_rule": "use each frozen CAEOS report selected_risk and matching score arrays",
        "known_acceptance_quantiles": list(QUANTILES),
        "coverage_grid": list(COVERAGE_GRID),
        "unknown_samples_count_as_errors_when_accepted": True,
        "test_labels_used_for_reporting_only": True,
        "result_cannot_select_or_modify_the_final_algorithm": True,
        "source_artifact_sha256": artifact_hashes,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    protocol_path = args.output_dir / "protocol_manifest.json"
    if protocol_path.is_file():
        existing = json.loads(protocol_path.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing risk-coverage protocol differs from frozen inputs")
    else:
        protocol_path.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    blocks = []
    for suite, scenario, candidate_path, comparator_path in pairs:
        block = analyze_run(candidate_path, comparator_path)
        block.update({"suite": suite, "scenario": scenario})
        blocks.append(block)
    report = {
        "schema_version": "strict_v4_seed7_risk_coverage_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_count": len(blocks),
        "aggregate": aggregate(blocks),
        "per_scenario": blocks,
        "claim_boundary": "descriptive_seed7_only_not_final_algorithm_selection_or_confirmed_sota",
    }
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "analysis.md").write_text(render(report), encoding="utf-8")
    print(render(report), end="")


if __name__ == "__main__":
    main()
