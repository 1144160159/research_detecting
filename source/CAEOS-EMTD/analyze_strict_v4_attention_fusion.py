from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.stats import wilcoxon
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    roc_auc_score,
)

from caeos.metrics import (
    expected_calibration_error,
    fpr_at_95_tpr,
    open_set_classification_rate,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


METHODS = (
    "uniform_probability_average",
    "entropy_conditioned_learnable_attention",
    "caeos_reliability_fusion",
)
METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_ece",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_probability(probability: np.ndarray) -> np.ndarray:
    value = np.clip(np.asarray(probability, dtype=np.float64), 1e-12, None)
    return value / value.sum(axis=-1, keepdims=True)


def attention_fusion(
    probability: np.ndarray, parameters: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    probability = normalize_probability(probability)
    if probability.ndim != 3:
        raise ValueError("view probabilities must have shape [N,M,K]")
    modality_count = probability.shape[1]
    parameters = np.asarray(parameters, dtype=np.float64)
    if parameters.shape != (modality_count + 1,):
        raise ValueError("attention parameter count mismatch")
    bias = parameters[:modality_count] - parameters[:modality_count].mean()
    beta = parameters[-1]
    entropy = -np.sum(probability * np.log(probability), axis=2) / math.log(
        probability.shape[2]
    )
    logits = bias[None, :] + beta * (1.0 - entropy)
    logits -= logits.max(axis=1, keepdims=True)
    weights = np.exp(logits)
    weights /= weights.sum(axis=1, keepdims=True)
    fused = np.sum(weights[:, :, None] * probability, axis=1)
    return normalize_probability(fused), weights


def fit_attention(
    probability: np.ndarray,
    labels: np.ndarray,
    l2_penalty: float = 1e-4,
    parameter_bound: float = 8.0,
) -> dict[str, Any]:
    probability = normalize_probability(probability)
    labels = np.asarray(labels, dtype=np.int64)
    if labels.min() < 0 or labels.max() >= probability.shape[2]:
        raise ValueError("validation labels are outside known class range")

    def objective(parameters: np.ndarray) -> float:
        fused, _ = attention_fusion(probability, parameters)
        nll = -np.mean(np.log(fused[np.arange(len(labels)), labels]))
        return float(nll + l2_penalty * np.sum(parameters**2))

    initial = np.zeros(probability.shape[1] + 1, dtype=np.float64)
    result = minimize(
        objective,
        initial,
        method="L-BFGS-B",
        bounds=[(-parameter_bound, parameter_bound)] * len(initial),
        options={"maxiter": 500, "ftol": 1e-12},
    )
    if not result.success or not np.isfinite(result.fun):
        raise ValueError("attention optimization failed: %s" % result.message)
    fused, weights = attention_fusion(probability, result.x)
    uniform = probability.mean(axis=1)
    labels_index = np.arange(len(labels))
    return {
        "parameters": result.x.tolist(),
        "validation_objective": float(result.fun),
        "validation_nll": float(
            -np.mean(np.log(fused[labels_index, labels]))
        ),
        "uniform_validation_nll": float(
            -np.mean(np.log(uniform[labels_index, labels]))
        ),
        "mean_validation_weights": weights.mean(axis=0).tolist(),
        "iterations": int(result.nit),
    }


def evaluate(
    probability: np.ndarray, labels: np.ndarray, unknown: np.ndarray
) -> dict[str, float]:
    probability = normalize_probability(probability)
    labels = np.asarray(labels, dtype=np.int64)
    unknown = np.asarray(unknown, dtype=bool)
    known = ~unknown
    prediction = probability.argmax(axis=1)
    risk = 1.0 - probability.max(axis=1)
    target = unknown.astype(np.int64)
    return {
        "known_macro_f1": float(
            f1_score(
                labels[known],
                prediction[known],
                average="macro",
                zero_division=0,
            )
        ),
        "unknown_auroc": float(roc_auc_score(target, risk)),
        "unknown_aupr": float(average_precision_score(target, risk)),
        "unknown_fpr95": float(fpr_at_95_tpr(target, risk)),
        "oscr": float(
            open_set_classification_rate(labels, prediction, unknown, risk)
        ),
        "known_ece": float(
            expected_calibration_error(probability[known], labels[known])
        ),
    }


def distribution(values: list[float]) -> dict[str, float]:
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("aggregate values must be finite and non-empty")
    return {
        "mean": mean(values),
        "std": pstdev(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
    }


def directed_gain(metric: str, candidate: float, reference: float) -> float:
    if metric in {"unknown_fpr95", "known_ece"}:
        return reference - candidate
    return candidate - reference


def analyze(
    protocol: dict[str, Any], source_protocol: dict[str, Any]
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_attention_fusion_protocol_v1":
        raise ValueError("unexpected attention protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("attention protocol SHA mismatch")
    if source_protocol.get("manifest_sha256") != canonical_hash(source_protocol):
        raise ValueError("source protocol SHA mismatch")
    if (
        protocol.get("source_protocol_manifest_sha256")
        != source_protocol.get("manifest_sha256")
        or protocol.get("source_manifest_sha256")
        != source_protocol.get("source_manifest_sha256")
    ):
        raise ValueError("attention source chain mismatch")
    run_root = Path(source_protocol["source_run_root"])
    per_scenario = []
    for record in source_protocol["sources"]:
        scenario_dir = run_root / record["scenario_dir"]
        evidence_path = scenario_dir / "evidence_package.npz"
        scores_path = scenario_dir / "scores.npz"
        metrics_path = scenario_dir / "metrics.json"
        for path, key in (
            (evidence_path, "evidence_sha256"),
            (scores_path, "scores_sha256"),
            (metrics_path, "metrics_sha256"),
        ):
            if file_hash(path) != record[key]:
                raise ValueError("attention source drift: %s" % path)
        with np.load(evidence_path, allow_pickle=False) as evidence:
            validation_probability = evidence["validation_view_probability"]
            test_probability = evidence["test_view_probability"]
            reliability_fusion = evidence["test_view_fused_probability"]
            if "test_labels" in evidence.files or "test_unknown" in evidence.files:
                raise ValueError("evidence package contains forbidden test truth")
        with np.load(scores_path, allow_pickle=False) as scores:
            validation_labels = scores["validation_labels"]
            test_labels = scores["test_labels"]
            test_unknown = scores["test_unknown"]
        if len(test_labels) != len(test_probability):
            raise ValueError("attention source length mismatch")
        fitted = fit_attention(
            validation_probability,
            validation_labels,
            float(protocol["l2_penalty"]),
            float(protocol["parameter_bound"]),
        )
        attention_probability, test_weights = attention_fusion(
            test_probability, np.asarray(fitted["parameters"])
        )
        uniform_probability = normalize_probability(test_probability).mean(axis=1)
        reports = {
            "uniform_probability_average": evaluate(
                uniform_probability, test_labels, test_unknown
            ),
            "entropy_conditioned_learnable_attention": evaluate(
                attention_probability, test_labels, test_unknown
            ),
            "caeos_reliability_fusion": evaluate(
                reliability_fusion, test_labels, test_unknown
            ),
        }
        suite, scenario_seed = record["scenario_dir"].split("/")
        per_scenario.append(
            {
                "suite": suite,
                "scenario": scenario_seed.removesuffix("_seed7"),
                "fit": fitted,
                "mean_test_weights": test_weights.mean(axis=0).tolist(),
                "reports": reports,
            }
        )
    if len(per_scenario) != 102:
        raise ValueError("attention analysis is incomplete")
    aggregate = {
        method: {
            metric: distribution(
                [row["reports"][method][metric] for row in per_scenario]
            )
            for metric in METRICS
        }
        for method in METHODS
    }
    paired = {}
    candidate = "entropy_conditioned_learnable_attention"
    for reference in (
        "uniform_probability_average",
        "caeos_reliability_fusion",
    ):
        paired[reference] = {}
        for metric in METRICS:
            gains = [
                directed_gain(
                    metric,
                    row["reports"][candidate][metric],
                    row["reports"][reference][metric],
                )
                for row in per_scenario
            ]
            nonzero = [gain for gain in gains if abs(gain) > 1e-15]
            if nonzero:
                test = wilcoxon(
                    nonzero,
                    alternative="greater",
                    zero_method="wilcox",
                    method="auto",
                )
                pvalue = float(test.pvalue)
            else:
                pvalue = 1.0
            paired[reference][metric] = {
                **distribution(gains),
                "positive_rate": mean(gain > 0 for gain in gains),
                "one_sided_wilcoxon_pvalue": pvalue,
            }
    unknown_metrics = (
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    )
    decisions = {}
    for reference in paired:
        mean_gain = mean(paired[reference][metric]["mean"] for metric in unknown_metrics)
        decisions["attention_beats_%s" % reference] = (
            mean_gain > 0
            and sum(paired[reference][metric]["mean"] > 0 for metric in unknown_metrics)
            >= 3
            and paired[reference]["known_macro_f1"]["mean"] >= -0.01
        )
    return {
        "schema_version": "strict_v4_attention_fusion_analysis_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source_protocol_manifest_sha256": source_protocol["manifest_sha256"],
        "scenario_count": len(per_scenario),
        "source_integrity_checks": len(per_scenario) * 3,
        "test_truth_isolated_from_evidence_package": True,
        "claim_scope": "lightweight_attention_fusion_baseline",
        "aggregate": aggregate,
        "paired_directed_gain": paired,
        "decisions": decisions,
        "per_scenario": per_scenario,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 entropy-conditioned attention fusion",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | ECE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        value = result["aggregate"][method]
        lines.append(
            "| %s | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |"
            % (
                method,
                value["known_macro_f1"]["mean"],
                value["unknown_auroc"]["mean"],
                value["unknown_aupr"]["mean"],
                value["unknown_fpr95"]["mean"],
                value["oscr"]["mean"],
                value["known_ece"]["mean"],
            )
        )
    lines.extend(
        [
            "",
            "Decisions: `%s`." % json.dumps(result["decisions"], sort_keys=True),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--source-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    source = json.loads(args.source_protocol.read_text(encoding="utf-8"))
    result = analyze(protocol, source)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    text = render(result)
    (args.output_dir / "analysis.md").write_text(text, encoding="utf-8")
    (args.output_dir / "analysis_complete").write_text(
        result["protocol_manifest_sha256"] + "\n", encoding="ascii"
    )
    print(text, end="")


if __name__ == "__main__":
    main()
