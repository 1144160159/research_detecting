from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

import numpy as np
from scipy.stats import rankdata, wilcoxon

from analyze_strict_v4_attention_fusion import attention_fusion, evaluate, fit_attention
from create_strict_v4_external_confirmation_protocol import canonical_hash


METHODS = (
    "f2_probability_average",
    "f3_entropy_conditioned_attention",
    "f4_edl_evidence_sum",
    "f5_reliability_gate",
    "f6_standard_ds_fusion",
    "f9_caeos_final_probability",
)
METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_ece",
)
UNKNOWN_METRICS = METRICS[1:5]


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_probability(probability: np.ndarray) -> np.ndarray:
    value = np.clip(np.asarray(probability, dtype=np.float64), 1e-12, None)
    return value / value.sum(axis=-1, keepdims=True)


def edl_evidence_sum(evidence: np.ndarray) -> np.ndarray:
    evidence = np.asarray(evidence, dtype=np.float64)
    if evidence.ndim != 3 or np.any(evidence < 0):
        raise ValueError("view evidence must be non-negative [N,M,K]")
    alpha = evidence.sum(axis=1) + 1.0
    return normalize_probability(alpha)


def reliability_gate(
    probability: np.ndarray, reliability: np.ndarray
) -> np.ndarray:
    probability = np.asarray(probability, dtype=np.float64)
    reliability = np.asarray(reliability, dtype=np.float64)
    if (
        probability.ndim != 3
        or np.any(probability < 0)
        or reliability.shape != probability.shape[:2]
        or np.any(reliability < 0)
    ):
        raise ValueError("view reliability shape or range is invalid")
    total = reliability.sum(axis=1, keepdims=True)
    if np.any(total <= 0):
        raise ValueError("every sample requires positive total reliability")
    fused = np.einsum("nm,nmk->nk", reliability, probability) / total
    return normalize_probability(fused)


def evidence_to_opinion(evidence: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    evidence = np.asarray(evidence, dtype=np.float64)
    classes = evidence.shape[-1]
    strength = evidence.sum(axis=-1, keepdims=True) + classes
    return evidence / strength, classes / strength


def standard_ds_fusion(evidence: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    evidence = np.asarray(evidence, dtype=np.float64)
    if evidence.ndim != 3 or evidence.shape[1] < 2 or np.any(evidence < 0):
        raise ValueError("standard DS requires non-negative [N,M,K] evidence")
    belief, uncertainty = evidence_to_opinion(evidence)
    joint_belief = belief[:, 0]
    joint_uncertainty = uncertainty[:, 0]
    for index in range(1, evidence.shape[1]):
        second_belief = belief[:, index]
        second_uncertainty = uncertainty[:, index]
        committed = joint_belief.sum(axis=1, keepdims=True) * second_belief.sum(
            axis=1, keepdims=True
        )
        agreement = (joint_belief * second_belief).sum(axis=1, keepdims=True)
        conflict = np.clip(committed - agreement, 0.0, 1.0)
        normalizer = np.maximum(1.0 - conflict, eps)
        joint_belief = (
            joint_belief * second_belief
            + joint_belief * second_uncertainty
            + second_belief * joint_uncertainty
        ) / normalizer
        joint_uncertainty = joint_uncertainty * second_uncertainty / normalizer
        total = np.maximum(joint_belief.sum(axis=1, keepdims=True) + joint_uncertainty, eps)
        joint_belief /= total
        joint_uncertainty /= total
    classes = evidence.shape[-1]
    strength = classes / np.maximum(joint_uncertainty, eps)
    alpha = joint_belief * strength + 1.0
    return normalize_probability(alpha)


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


def analyze(protocol: dict[str, Any], source_protocol: dict[str, Any]) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_fusion_operator_protocol_v2":
        raise ValueError("unexpected fusion operator protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("fusion operator protocol SHA mismatch")
    if source_protocol.get("manifest_sha256") != canonical_hash(source_protocol):
        raise ValueError("source protocol SHA mismatch")
    if protocol.get("source_protocol_manifest_sha256") != source_protocol.get(
        "manifest_sha256"
    ):
        raise ValueError("fusion operator source chain mismatch")
    run_root = Path(source_protocol["source_run_root"])
    per_scenario = []
    for record in source_protocol["sources"]:
        scenario_dir = run_root / record["scenario_dir"]
        paths = {
            "evidence": scenario_dir / "evidence_package.npz",
            "scores": scenario_dir / "scores.npz",
            "metrics": scenario_dir / "metrics.json",
        }
        for name, key in (
            ("evidence", "evidence_sha256"),
            ("scores", "scores_sha256"),
            ("metrics", "metrics_sha256"),
        ):
            if file_hash(paths[name]) != record[key]:
                raise ValueError("fusion operator source drift: %s" % paths[name])
        with np.load(paths["evidence"], allow_pickle=False) as evidence:
            if "test_labels" in evidence.files or "test_unknown" in evidence.files:
                raise ValueError("evidence package contains forbidden test truth")
            validation_probability = evidence["validation_view_probability"]
            test_probability = evidence["test_view_probability"]
            test_evidence = evidence["test_view_evidence"]
            test_reliability = evidence["test_view_reliability"]
            final_probability = evidence["test_final_probability"]
        with np.load(paths["scores"], allow_pickle=False) as scores:
            validation_labels = scores["validation_labels"]
            test_labels = scores["test_labels"]
            test_unknown = scores["test_unknown"]
        fitted = fit_attention(validation_probability, validation_labels)
        attention_probability, _ = attention_fusion(
            test_probability, np.asarray(fitted["parameters"])
        )
        reports = {
            "f2_probability_average": evaluate(
                normalize_probability(test_probability).mean(axis=1),
                test_labels,
                test_unknown,
            ),
            "f3_entropy_conditioned_attention": evaluate(
                attention_probability, test_labels, test_unknown
            ),
            "f4_edl_evidence_sum": evaluate(
                edl_evidence_sum(test_evidence), test_labels, test_unknown
            ),
            "f5_reliability_gate": evaluate(
                reliability_gate(test_probability, test_reliability),
                test_labels,
                test_unknown,
            ),
            "f6_standard_ds_fusion": evaluate(
                standard_ds_fusion(test_evidence), test_labels, test_unknown
            ),
            "f9_caeos_final_probability": evaluate(
                final_probability, test_labels, test_unknown
            ),
        }
        suite, scenario_seed = record["scenario_dir"].split("/")
        per_scenario.append(
            {
                "suite": suite,
                "scenario": scenario_seed.removesuffix("_seed7"),
                "reports": reports,
            }
        )
    if len(per_scenario) != 102:
        raise ValueError("fusion operator analysis is incomplete")
    aggregate = {
        method: {
            metric: distribution(
                [row["reports"][method][metric] for row in per_scenario]
            )
            for metric in METRICS
        }
        for method in METHODS
    }
    rank_rows = []
    for method in METHODS:
        row = {"method": method, "metric_ranks": {}}
        rank_rows.append(row)
    for metric in UNKNOWN_METRICS:
        values = [aggregate[method][metric]["mean"] for method in METHODS]
        oriented = values if metric == "unknown_fpr95" else [-value for value in values]
        for row, rank in zip(rank_rows, rankdata(oriented, method="average")):
            row["metric_ranks"][metric] = float(rank)
    for row in rank_rows:
        row["mean_unknown_metric_rank"] = mean(row["metric_ranks"].values())
    rank_rows.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))
    reference = "f9_caeos_final_probability"
    paired = {}
    for method in METHODS[:-1]:
        paired[method] = {}
        for metric in METRICS:
            gains = [
                directed_gain(
                    metric,
                    row["reports"][reference][metric],
                    row["reports"][method][metric],
                )
                for row in per_scenario
            ]
            nonzero = [gain for gain in gains if abs(gain) > 1e-15]
            pvalue = (
                float(wilcoxon(nonzero, alternative="greater", method="auto").pvalue)
                if nonzero
                else 1.0
            )
            paired[method][metric] = {
                **distribution(gains),
                "positive_rate": mean(gain > 0 for gain in gains),
                "one_sided_wilcoxon_pvalue": pvalue,
            }
    return {
        "schema_version": "strict_v4_fusion_operator_analysis_v2",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source_protocol_manifest_sha256": source_protocol["manifest_sha256"],
        "scenario_count": len(per_scenario),
        "source_integrity_checks": len(per_scenario) * 3,
        "test_truth_isolated_from_evidence_package": True,
        "pollution_claim_allowed": False,
        "aggregate": aggregate,
        "unknown_metric_ranks": rank_rows,
        "caeos_directed_gain_vs_baseline": paired,
        "per_scenario": per_scenario,
    }


def render(result: dict[str, Any]) -> str:
    ranks = {
        row["method"]: row["mean_unknown_metric_rank"]
        for row in result["unknown_metric_ranks"]
    }
    lines = [
        "# Strict-v4 fusion operator analysis",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | ECE | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        value = result["aggregate"][method]
        lines.append(
            "| %s | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %.2f |"
            % (
                method,
                value["known_macro_f1"]["mean"],
                value["unknown_auroc"]["mean"],
                value["unknown_aupr"]["mean"],
                value["unknown_fpr95"]["mean"],
                value["oscr"]["mean"],
                value["known_ece"]["mean"],
                ranks[method],
            )
        )
    return "\n".join(lines) + "\n"


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
