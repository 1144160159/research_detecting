from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def create_gate(protocol: dict[str, Any], observed_metrics: int) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_mlp_sirc_msp_fixed_protocol_v1":
        raise ValueError("unexpected SIRC protocol schema")
    if protocol.get("mode") != "pilot" or protocol.get("expected_runs") != 14:
        raise ValueError("SIRC expansion gate requires the 14-scenario pilot protocol")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("SIRC pilot protocol SHA mismatch")
    if protocol.get("fit_data") != "known_training_features_and_logits_only":
        raise ValueError("SIRC fitting must use known training data only")
    if protocol.get("ood_parameter_sweep") is not False:
        raise ValueError("SIRC expansion gate forbids OOD parameter sweeping")
    if observed_metrics != 0:
        raise ValueError("SIRC expansion gate must be frozen before every pilot result")
    result = {
        "schema_version": "strict_v4_mlp_sirc_msp_fixed_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0, "strict_run_before_preregistration": True,
        "gate_scope": "development_budget_decision_only_not_confirmatory_evidence",
        "expansion_candidates": list(protocol["methods"]), "reference_methods": ["mlp_msp", "opendetect"],
        "unknown_metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
        "oriented_metric_rule": "higher is better except lower unknown_fpr95 is better",
        "all_required_checks_per_candidate": {
            "pilot_runs_complete": "14/14 reports and zero failures",
            "split_integrity": "SIRC, source MLP and OpenDetect split fingerprints identical",
            "known_f1_nonregression": "absolute SIRC minus source-MSP Known F1 <= 1e-12 in every scenario",
            "nondegenerate_score": "validation/test risk and auxiliary standard deviations exceed 1e-12 in every scenario",
            "top_two_rank": "candidate four-unknown-metric mean rank among four pilot methods <= 2.0",
            "metric_breadth": "positive mean oriented gain over MSP on at least 2 of 4 metrics",
            "overall_gain": "mean of four candidate-versus-MSP oriented mean gains is strictly positive",
            "oscr_gain": "mean OSCR gain over MSP is strictly positive",
            "suite_robustness": "at least 4 of 7 suites have nonnegative four-metric mean gain and worst suite >= -0.05",
        },
        "variant_selection_rule": "evaluate both predeclared variants independently; expand every passing variant and never choose by test-OOD rank alone",
        "full_matrix_action": "run all 102 frozen seed7 scenarios for each candidate that passes every check",
        "failure_action": "retain the 14-scenario pilot for failed candidates",
        "test_labels_used_for_gate": True, "gate_is_development_only": True,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads((args.pilot_root / "protocol_manifest.json").read_text(encoding="utf-8"))
    gate = create_gate(protocol, len(list(args.pilot_root.glob("*/*/metrics.json"))))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(gate, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
