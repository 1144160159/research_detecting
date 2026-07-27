from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from caeos.class_conditional_reliability_fusion import (
    fit_class_conditional_reliability,
    reliability_fused_candidate,
)
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.validation_gated_reliability_fusion import (
    apply_validation_gate,
    validation_safety_gate,
)
from evaluate_budgeted_conformal_uplift import file_hash, higher_quantile


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    with np.load(args.evidence_package, allow_pickle=False) as evidence, np.load(
        args.scores, allow_pickle=False
    ) as scores:
        validation_labels = np.asarray(scores["validation_labels"], dtype=np.int64)
        test_labels = np.asarray(scores["test_labels"], dtype=np.int64)
        test_unknown = np.asarray(scores["test_unknown"], dtype=bool)
        incumbent_test_prediction = np.asarray(scores["test_prediction"], dtype=np.int64)
        fit = fit_class_conditional_reliability(
            evidence["validation_view_probability"], validation_labels,
            shrinkage=args.shrinkage, minimum_reliability=args.minimum_reliability,
        )
        common = {"class_reliability": fit["reliability"], "risk_blend": args.risk_blend}
        validation = reliability_fused_candidate(
            view_probability=evidence["validation_view_probability"],
            global_probability=evidence["validation_global_probability"],
            incumbent_view_fused_probability=evidence["validation_view_fused_probability"],
            incumbent_gate=evidence["validation_gate"],
            incumbent_final_probability=evidence["validation_final_probability"],
            incumbent_risk=evidence["validation_selected_risk"], **common,
        )
        test = reliability_fused_candidate(
            view_probability=evidence["test_view_probability"],
            global_probability=evidence["test_global_probability"],
            incumbent_view_fused_probability=evidence["test_view_fused_probability"],
            incumbent_gate=evidence["test_gate"],
            incumbent_final_probability=evidence["test_final_probability"],
            incumbent_risk=evidence["test_selected_risk"], **common,
        )
        incumbent_validation_probability = np.asarray(
            evidence["validation_final_probability"], dtype=np.float64
        )
        incumbent_test_probability = np.asarray(evidence["test_final_probability"], dtype=np.float64)
        incumbent_validation_risk = np.asarray(evidence["validation_selected_risk"], dtype=np.float64)
        incumbent_test_risk = np.asarray(evidence["test_selected_risk"], dtype=np.float64)

    gate = validation_safety_gate(
        labels=validation_labels,
        incumbent_probability=incumbent_validation_probability,
        candidate_probability=np.asarray(validation["candidate_probability"]),
        incumbent_risk=incumbent_validation_risk,
        candidate_risk=np.asarray(validation["candidate_risk"]),
        minimum_f1_gain=args.minimum_f1_gain,
        maximum_correct_risk_increase=args.maximum_correct_risk_increase,
        minimum_auc_gain=args.minimum_auc_gain,
        minimum_separation_gain=args.minimum_separation_gain,
        minimum_strict_proxy_gain=args.minimum_strict_proxy_gain,
    )
    selected_validation_probability, selected_validation_risk = apply_validation_gate(
        gate=gate,
        incumbent_probability=incumbent_validation_probability,
        candidate_probability=np.asarray(validation["candidate_probability"]),
        incumbent_risk=incumbent_validation_risk,
        candidate_risk=np.asarray(validation["candidate_risk"]),
    )
    selected_test_probability, selected_test_risk = apply_validation_gate(
        gate=gate,
        incumbent_probability=incumbent_test_probability,
        candidate_probability=np.asarray(test["candidate_probability"]),
        incumbent_risk=incumbent_test_risk,
        candidate_risk=np.asarray(test["candidate_risk"]),
    )
    selected_test_prediction = selected_test_probability.argmax(axis=1)
    reference_threshold = higher_quantile(incumbent_validation_risk, args.known_rejection_quantile)
    selected_threshold = higher_quantile(selected_validation_risk, args.known_rejection_quantile)
    reference_report = evaluate_hybrid_open_set(
        test_labels, test_unknown, incumbent_test_prediction, incumbent_test_risk, reference_threshold
    )
    selected_report = evaluate_hybrid_open_set(
        test_labels, test_unknown, selected_test_prediction, selected_test_risk, selected_threshold
    )
    result = {
        "schema_version": "strict_v4_validation_gated_reliability_fusion_metrics_v1",
        "protocol_manifest_sha256": args.protocol_manifest_sha256,
        "suite": args.suite, "scenario": args.scenario, "seed": args.seed,
        "reference_risk": "paired_current_trainer_pairwise_selected_risk",
        "candidate_risk": "validation_gated_class_conditional_reliability_fusion",
        "parameters": {
            "shrinkage": args.shrinkage,
            "minimum_reliability": args.minimum_reliability,
            "risk_blend": args.risk_blend,
            "known_rejection_quantile": args.known_rejection_quantile,
            "minimum_f1_gain": args.minimum_f1_gain,
            "maximum_correct_risk_increase": args.maximum_correct_risk_increase,
            "minimum_auc_gain": args.minimum_auc_gain,
            "minimum_separation_gain": args.minimum_separation_gain,
            "minimum_strict_proxy_gain": args.minimum_strict_proxy_gain,
        },
        "validation_gate": gate,
        "thresholds": {"reference": reference_threshold, "candidate": selected_threshold},
        "reports": {"reference": reference_report, "candidate": selected_report},
        "diagnostics": {
            "enabled": gate["enabled"] is True,
            "exact_fallback": bool(
                gate["enabled"] is not True
                and np.array_equal(selected_validation_probability, incumbent_validation_probability)
                and np.array_equal(selected_validation_risk, incumbent_validation_risk)
                and np.array_equal(selected_test_probability, incumbent_test_probability)
                and np.array_equal(selected_test_risk, incumbent_test_risk)
            ),
            "known_macro_f1_gain": float(selected_report["known_macro_f1"] - reference_report["known_macro_f1"]),
            "prediction_change_rate": float(np.mean(selected_test_prediction != incumbent_test_prediction)),
            "validation_temperature_reconstruction_max_abs_error": float(validation["temperature_reconstruction_max_abs_error"]),
            "test_temperature_reconstruction_max_abs_error": float(test["temperature_reconstruction_max_abs_error"]),
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "input_sha256": {
            "evidence_package": file_hash(args.evidence_package),
            "scores": file_hash(args.scores),
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    np.savez_compressed(
        args.output_dir / "scores.npz",
        validation_gate_enabled=np.asarray(bool(gate["enabled"])),
        validation_selected_risk=selected_validation_risk,
        test_selected_risk=selected_test_risk,
        test_selected_prediction=selected_test_prediction,
        test_labels=test_labels, test_unknown=test_unknown,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-package", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--protocol-manifest-sha256", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, default=307)
    parser.add_argument("--shrinkage", type=float, default=20.0)
    parser.add_argument("--minimum-reliability", type=float, default=0.05)
    parser.add_argument("--risk-blend", type=float, default=0.25)
    parser.add_argument("--known-rejection-quantile", type=float, default=0.95)
    parser.add_argument("--minimum-f1-gain", type=float, default=-0.002)
    parser.add_argument("--maximum-correct-risk-increase", type=float, default=0.01)
    parser.add_argument("--minimum-auc-gain", type=float, default=0.0)
    parser.add_argument("--minimum-separation-gain", type=float, default=0.0)
    parser.add_argument("--minimum-strict-proxy-gain", type=float, default=0.005)
    evaluate(parser.parse_args())


if __name__ == "__main__":
    main()
