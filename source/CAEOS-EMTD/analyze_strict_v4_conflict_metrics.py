from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

import numpy as np
from scipy.stats import chi2, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = (
    "d1_label_disagreement",
    "d2_cosine_distance",
    "d3_jensen_shannon",
    "d4_symmetric_kl",
    "d5_raw_ds_conflict",
    "d6_conditional_ds_conflict",
    "d7_reliability_conditional_conflict",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pair_indices(modality_count: int) -> list[tuple[int, int]]:
    return [
        (left, right)
        for left in range(modality_count)
        for right in range(left + 1, modality_count)
    ]


def conflict_metric_vectors(
    probability: np.ndarray,
    evidence: np.ndarray,
    reliability: np.ndarray,
) -> dict[str, np.ndarray]:
    probability = np.asarray(probability, dtype=np.float64)
    evidence = np.asarray(evidence, dtype=np.float64)
    reliability = np.asarray(reliability, dtype=np.float64)
    if probability.ndim != 3 or evidence.shape != probability.shape:
        raise ValueError("probability/evidence must have matching [N,M,K] shapes")
    if reliability.shape != probability.shape[:2]:
        raise ValueError("reliability must have shape [N,M]")
    if probability.shape[1] < 2:
        raise ValueError("at least two modalities are required")
    probability = probability / np.clip(
        probability.sum(axis=2, keepdims=True), 1e-12, None
    )
    pairs = pair_indices(probability.shape[1])
    values: dict[str, list[np.ndarray]] = {
        name: [] for name in METRICS[:-1]
    }
    conditional_pairs = []
    reliability_weights = []
    labels = probability.argmax(axis=2)
    for left, right in pairs:
        p = probability[:, left]
        q = probability[:, right]
        values["d1_label_disagreement"].append(
            (labels[:, left] != labels[:, right]).astype(np.float64)
        )
        cosine = np.sum(p * q, axis=1) / np.clip(
            np.linalg.norm(p, axis=1) * np.linalg.norm(q, axis=1), 1e-12, None
        )
        values["d2_cosine_distance"].append(np.clip(1.0 - cosine, 0.0, 2.0))
        p_log = np.clip(p, 1e-12, None)
        q_log = np.clip(q, 1e-12, None)
        p_log = p_log / p_log.sum(axis=1, keepdims=True)
        q_log = q_log / q_log.sum(axis=1, keepdims=True)
        midpoint = 0.5 * (p_log + q_log)
        js = 0.5 * (
            np.sum(p_log * np.log(p_log / midpoint), axis=1)
            + np.sum(q_log * np.log(q_log / midpoint), axis=1)
        ) / math.log(2.0)
        values["d3_jensen_shannon"].append(js)
        symmetric_kl = 0.5 * (
            np.sum(
                p_log * np.log(p_log / q_log),
                axis=1,
            )
            + np.sum(
                q_log * np.log(q_log / p_log),
                axis=1,
            )
        )
        values["d4_symmetric_kl"].append(symmetric_kl)
        left_evidence = np.clip(evidence[:, left], 0.0, None)
        right_evidence = np.clip(evidence[:, right], 0.0, None)
        left_mass = left_evidence.sum(axis=1)
        right_mass = right_evidence.sum(axis=1)
        raw = (
            left_mass * right_mass
            - np.sum(left_evidence * right_evidence, axis=1)
        )
        raw = np.clip(raw, 0.0, None)
        conditional = raw / np.clip(left_mass * right_mass, 1e-12, None)
        values["d5_raw_ds_conflict"].append(raw)
        values["d6_conditional_ds_conflict"].append(conditional)
        conditional_pairs.append(conditional)
        reliability_weights.append(reliability[:, left] * reliability[:, right])
    result = {
        name: np.mean(np.stack(items, axis=1), axis=1)
        for name, items in values.items()
    }
    conditional_matrix = np.stack(conditional_pairs, axis=1)
    weight_matrix = np.stack(reliability_weights, axis=1)
    result["d7_reliability_conditional_conflict"] = np.sum(
        conditional_matrix * weight_matrix, axis=1
    ) / np.clip(weight_matrix.sum(axis=1), 1e-12, None)
    for name, vector in result.items():
        if not np.isfinite(vector).all():
            raise ValueError("non-finite conflict metric: %s" % name)
    return result


def logistic_likelihood_gain(
    uncertainty: np.ndarray, metric: np.ndarray, unknown: np.ndarray
) -> dict[str, float]:
    uncertainty = np.asarray(uncertainty, dtype=np.float64)
    metric = np.asarray(metric, dtype=np.float64)
    y = np.asarray(unknown, dtype=np.int64)
    if np.unique(y).size != 2:
        raise ValueError("logistic outcome must contain known and unknown samples")
    if float(np.std(metric)) < 1e-12:
        return {
            "log_likelihood_gain": 0.0,
            "metric_coefficient": 0.0,
            "likelihood_ratio_pvalue": 1.0,
        }

    def fit(values: np.ndarray) -> tuple[float, np.ndarray]:
        scaled = StandardScaler().fit_transform(values)
        model = LogisticRegression(C=1e4, max_iter=1000, solver="lbfgs")
        model.fit(scaled, y)
        probability = np.clip(model.predict_proba(scaled)[:, 1], 1e-12, 1 - 1e-12)
        log_likelihood = float(
            np.sum(y * np.log(probability) + (1 - y) * np.log(1 - probability))
        )
        return log_likelihood, model.coef_[0]

    base_likelihood, _ = fit(uncertainty.reshape(-1, 1))
    full_likelihood, coefficients = fit(
        np.column_stack([uncertainty, metric])
    )
    return {
        "log_likelihood_gain": (full_likelihood - base_likelihood) / len(y),
        "metric_coefficient": float(coefficients[1]),
        "likelihood_ratio_pvalue": float(
            chi2.sf(2.0 * max(full_likelihood - base_likelihood, 0.0), 1)
        ),
    }


def scenario_analysis(
    probability: np.ndarray,
    evidence: np.ndarray,
    reliability: np.ndarray,
    view_uncertainty: np.ndarray,
    unknown: np.ndarray,
) -> dict[str, Any]:
    unknown = np.asarray(unknown, dtype=bool)
    if np.unique(unknown).size != 2:
        raise ValueError("scenario must contain known and unknown test samples")
    control = np.asarray(view_uncertainty, dtype=np.float64).mean(axis=1)
    vectors = conflict_metric_vectors(probability, evidence, reliability)
    result = {}
    for name, vector in vectors.items():
        auroc = float(roc_auc_score(unknown, vector))
        if float(np.std(vector)) < 1e-12 or float(np.std(control)) < 1e-12:
            correlation = 0.0
        else:
            correlation = float(spearmanr(vector, control)[0])
        if not math.isfinite(float(correlation)):
            correlation = 0.0
        logistic = logistic_likelihood_gain(control, vector, unknown)
        result[name] = {
            "unknown_auroc": auroc,
            "rank_biserial_effect": 2.0 * auroc - 1.0,
            "spearman_with_uncertainty": float(correlation),
            **logistic,
        }
    return result


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


def analyze(protocol: dict[str, Any]) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_conflict_metric_protocol_v3":
        raise ValueError("unexpected conflict protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("conflict protocol SHA mismatch")
    if protocol.get("expected_scenarios") != 102 or protocol.get("metrics") != list(METRICS):
        raise ValueError("unexpected conflict analysis contract")
    if protocol.get("probability_floor_for_divergences") != 1e-12:
        raise ValueError("unexpected divergence floor")
    if protocol.get("logistic_regularization_C") != 1e4:
        raise ValueError("unexpected logistic regularization")
    run_root = Path(protocol["source_run_root"])
    per_scenario = []
    for record in protocol["sources"]:
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
                raise ValueError("source drift detected: %s" % path)
        with np.load(evidence_path, allow_pickle=False) as evidence:
            probability = evidence["test_view_probability"]
            view_evidence = evidence["test_view_evidence"]
            reliability = evidence["test_view_reliability"]
            view_uncertainty = evidence["test_view_uncertainty"]
            if "test_unknown" in evidence.files or "test_labels" in evidence.files:
                raise ValueError("evidence package contains forbidden test truth")
        with np.load(scores_path, allow_pickle=False) as scores:
            unknown = scores["test_unknown"]
        if len(unknown) != len(probability):
            raise ValueError("source test length mismatch: %s" % scenario_dir)
        suite, scenario_seed = record["scenario_dir"].split("/")
        result = scenario_analysis(
            probability, view_evidence, reliability, view_uncertainty, unknown
        )
        per_scenario.append(
            {
                "suite": suite,
                "scenario": scenario_seed.removesuffix("_seed7"),
                "sample_count": int(len(unknown)),
                "known_count": int((~unknown).sum()),
                "unknown_count": int(unknown.sum()),
                "metrics": result,
            }
        )
    if len(per_scenario) != 102:
        raise ValueError("conflict analysis is incomplete")
    aggregate = {}
    for name in METRICS:
        aggregate[name] = {}
        for outcome in (
            "unknown_auroc",
            "rank_biserial_effect",
            "spearman_with_uncertainty",
            "log_likelihood_gain",
            "metric_coefficient",
            "likelihood_ratio_pvalue",
        ):
            aggregate[name][outcome] = distribution(
                [row["metrics"][name][outcome] for row in per_scenario]
            )
        aggregate[name]["positive_likelihood_gain_rate"] = mean(
            row["metrics"][name]["log_likelihood_gain"] > 1e-9
            for row in per_scenario
        )
        aggregate[name]["positive_coefficient_rate"] = mean(
            row["metrics"][name]["metric_coefficient"] > 0
            for row in per_scenario
        )
        aggregate[name]["significant_positive_increment_rate"] = mean(
            row["metrics"][name]["metric_coefficient"] > 0
            and row["metrics"][name]["likelihood_ratio_pvalue"] < 0.05
            for row in per_scenario
        )
    suites = sorted({row["suite"] for row in per_scenario})
    suite_aggregate = {
        suite: {
            name: mean(
                row["metrics"][name]["unknown_auroc"]
                for row in per_scenario
                if row["suite"] == suite
            )
            for name in METRICS
        }
        for suite in suites
    }
    d6_minus_d5 = [
        row["metrics"]["d6_conditional_ds_conflict"]["unknown_auroc"]
        - row["metrics"]["d5_raw_ds_conflict"]["unknown_auroc"]
        for row in per_scenario
    ]
    d7_minus_d6 = [
        row["metrics"]["d7_reliability_conditional_conflict"]["unknown_auroc"]
        - row["metrics"]["d6_conditional_ds_conflict"]["unknown_auroc"]
        for row in per_scenario
    ]
    decisions = {
        "conditional_normalization_supported": (
            mean(d6_minus_d5) > 0
            and mean(value > 0 for value in d6_minus_d5) > 0.5
        ),
        "reliability_weighting_supported": (
            mean(d7_minus_d6) > 0
            and mean(value > 0 for value in d7_minus_d6) > 0.5
        ),
        "conditional_conflict_has_incremental_information": (
            aggregate["d6_conditional_ds_conflict"][
                "log_likelihood_gain"
            ]["mean"]
            > 0
            and aggregate["d6_conditional_ds_conflict"][
                "significant_positive_increment_rate"
            ]
            > 0.5
        ),
    }
    return {
        "schema_version": "strict_v4_conflict_metric_analysis_v2",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_count": len(per_scenario),
        "source_integrity_checks": len(per_scenario) * 3,
        "test_truth_isolated_from_evidence_package": True,
        "claim_scope": "posthoc_mechanism_analysis_not_deployment_selection",
        "aggregate": aggregate,
        "suite_auroc": suite_aggregate,
        "paired": {
            "d6_minus_d5_auroc": {
                **distribution(d6_minus_d5),
                "positive_rate": mean(value > 0 for value in d6_minus_d5),
            },
            "d7_minus_d6_auroc": {
                **distribution(d7_minus_d6),
                "positive_rate": mean(value > 0 for value in d7_minus_d6),
            },
        },
        "decisions": decisions,
        "per_scenario": per_scenario,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 D1-D7 conflict metric analysis",
        "",
        "Posthoc mechanism analysis on 102 frozen seed7 scenarios; test labels are used only for statistical evaluation.",
        "",
        "| Metric | AUROC mean | Effect mean | Spearman(U) | LL gain | Sig. positive rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in METRICS:
        value = result["aggregate"][name]
        lines.append(
            "| %s | %.6f | %.6f | %.6f | %.8f | %.3f |"
            % (
                name,
                value["unknown_auroc"]["mean"],
                value["rank_biserial_effect"]["mean"],
                value["spearman_with_uncertainty"]["mean"],
                value["log_likelihood_gain"]["mean"],
                value["significant_positive_increment_rate"],
            )
        )
    lines.extend(
        [
            "",
            "D6-D5 AUROC: mean %+.6f, positive rate %.3f."
            % (
                result["paired"]["d6_minus_d5_auroc"]["mean"],
                result["paired"]["d6_minus_d5_auroc"]["positive_rate"],
            ),
            "D7-D6 AUROC: mean %+.6f, positive rate %.3f."
            % (
                result["paired"]["d7_minus_d6_auroc"]["mean"],
                result["paired"]["d7_minus_d6_auroc"]["positive_rate"],
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
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = analyze(protocol)
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
