from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
from scipy.stats import wilcoxon

from analyze_strict_v4_conflict_metrics import METRICS
from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def benjamini_hochberg(pvalues: list[float]) -> list[float]:
    values = np.asarray(pvalues, dtype=np.float64)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("p-values must be a non-empty vector")
    if not np.isfinite(values).all() or np.any(values < 0) or np.any(values > 1):
        raise ValueError("p-values must be finite and within [0,1]")
    order = np.argsort(values)
    ranked = values[order]
    adjusted = ranked * len(values) / np.arange(1, len(values) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0.0, 1.0)
    result = np.empty_like(adjusted)
    result[order] = adjusted
    return result.tolist()


def bootstrap_mean_interval(
    values: list[float], repetitions: int, seed: int, interval: float
) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    if len(array) == 0 or not np.isfinite(array).all():
        raise ValueError("bootstrap values must be finite and non-empty")
    rng = np.random.default_rng(seed)
    means = np.empty(repetitions, dtype=np.float64)
    for start in range(0, repetitions, 1000):
        count = min(1000, repetitions - start)
        indices = rng.integers(0, len(array), size=(count, len(array)))
        means[start : start + count] = array[indices].mean(axis=1)
    tail = (1.0 - interval) / 2.0
    return {
        "mean": float(array.mean()),
        "lower": float(np.quantile(means, tail)),
        "upper": float(np.quantile(means, 1.0 - tail)),
    }


def audit(
    protocol: dict[str, Any],
    parent_protocol: dict[str, Any],
    analysis: dict[str, Any],
    analysis_sha256: str,
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_conflict_fdr_audit_protocol_v1":
        raise ValueError("unexpected FDR protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("FDR protocol SHA mismatch")
    if parent_protocol.get("manifest_sha256") != canonical_hash(parent_protocol):
        raise ValueError("parent conflict protocol SHA mismatch")
    if (
        protocol.get("parent_protocol_manifest_sha256")
        != parent_protocol.get("manifest_sha256")
        or analysis.get("protocol_manifest_sha256")
        != parent_protocol.get("manifest_sha256")
    ):
        raise ValueError("parent conflict chain mismatch")
    if (
        analysis.get("schema_version")
        != protocol.get("expected_parent_analysis_schema")
        or analysis.get("scenario_count") != protocol.get("expected_scenarios")
    ):
        raise ValueError("unexpected parent conflict analysis")
    alpha = float(protocol["fdr_alpha"])
    per_metric = {}
    for name in METRICS:
        rows = [row["metrics"][name] for row in analysis["per_scenario"]]
        qvalues = benjamini_hochberg(
            [float(row["likelihood_ratio_pvalue"]) for row in rows]
        )
        significant_positive = [
            float(row["metric_coefficient"]) > 0 and qvalue < alpha
            for row, qvalue in zip(rows, qvalues)
        ]
        per_metric[name] = {
            "scenario_count": len(rows),
            "positive_coefficient_count": sum(
                float(row["metric_coefficient"]) > 0 for row in rows
            ),
            "fdr_significant_count": sum(qvalue < alpha for qvalue in qvalues),
            "fdr_significant_positive_count": sum(significant_positive),
            "fdr_significant_positive_rate": mean(significant_positive),
            "qvalue_median": float(np.median(qvalues)),
            "qvalue_max": max(qvalues),
        }
    differences = [
        row["metrics"]["d6_conditional_ds_conflict"]["unknown_auroc"]
        - row["metrics"]["d5_raw_ds_conflict"]["unknown_auroc"]
        for row in analysis["per_scenario"]
    ]
    paired = wilcoxon(
        differences,
        alternative="greater",
        zero_method="wilcox",
        method="auto",
    )
    interval = bootstrap_mean_interval(
        differences,
        int(protocol["bootstrap_repetitions"]),
        int(protocol["bootstrap_seed"]),
        float(protocol["bootstrap_interval"]),
    )
    decisions = {
        "conditional_conflict_increment_survives_fdr": (
            per_metric["d6_conditional_ds_conflict"][
                "fdr_significant_positive_rate"
            ]
            > 0.5
        ),
        "conditional_normalization_paired_supported": (
            float(paired.pvalue) < alpha and interval["lower"] > 0
        ),
    }
    return {
        "schema_version": "strict_v4_conflict_fdr_audit_v1",
        "status": "pass",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "parent_protocol_manifest_sha256": parent_protocol["manifest_sha256"],
        "parent_analysis_sha256": analysis_sha256,
        "scenario_count": len(analysis["per_scenario"]),
        "per_metric": per_metric,
        "paired_d6_minus_d5": {
            "positive_rate": mean(value > 0 for value in differences),
            "wilcoxon_statistic": float(paired.statistic),
            "wilcoxon_one_sided_pvalue": float(paired.pvalue),
            "bootstrap_mean_interval": interval,
        },
        "decisions": decisions,
        "claim_scope": "multiplicity_and_paired_robustness_audit_only",
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 conflict metric FDR audit",
        "",
        "| Metric | Positive coef. | FDR significant | FDR significant positive | Rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in METRICS:
        row = result["per_metric"][name]
        lines.append(
            "| %s | %d | %d | %d | %.3f |"
            % (
                name,
                row["positive_coefficient_count"],
                row["fdr_significant_count"],
                row["fdr_significant_positive_count"],
                row["fdr_significant_positive_rate"],
            )
        )
    paired = result["paired_d6_minus_d5"]
    interval = paired["bootstrap_mean_interval"]
    lines.extend(
        [
            "",
            "D6-D5: mean %+.6f, 95%% bootstrap CI [%+.6f, %+.6f], one-sided Wilcoxon p=%.8g."
            % (
                interval["mean"],
                interval["lower"],
                interval["upper"],
                paired["wilcoxon_one_sided_pvalue"],
            ),
            "",
            "Decisions: `%s`."
            % json.dumps(result["decisions"], sort_keys=True),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    parent = json.loads(args.parent_protocol.read_text(encoding="utf-8"))
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    result = audit(protocol, parent, analysis, file_hash(args.analysis))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "fdr_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    text = render(result)
    (args.output_dir / "fdr_audit.md").write_text(text, encoding="utf-8")
    (args.output_dir / "fdr_audit_complete").write_text(
        result["protocol_manifest_sha256"] + "\n", encoding="ascii"
    )
    print(text, end="")


if __name__ == "__main__":
    main()
