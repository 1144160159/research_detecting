from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def create_gate(
    protocol: dict[str, Any], observed_metrics: int
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_mlp_klnd_protocol_v1":
        raise ValueError("unexpected k-LND protocol schema")
    if protocol.get("mode") != "pilot" or protocol.get("expected_runs") != 14:
        raise ValueError("k-LND expansion gate requires a 14-scenario pilot")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("k-LND pilot protocol SHA mismatch")
    if protocol.get("class_center_data") != (
        "correctly_classified_known_training_logits_only"
    ):
        raise ValueError("k-LND centers must use correct known training logits")
    if protocol.get("native_threshold_data") != (
        "correctly_classified_known_validation_logits_only"
    ):
        raise ValueError("k-LND native thresholds must use known validation")
    if protocol.get("ood_parameter_sweep") is not False:
        raise ValueError("k-LND gate forbids OOD parameter sweeping")
    if observed_metrics != 0:
        raise ValueError("k-LND gate must be frozen before every pilot result")
    result = {
        "schema_version": "strict_v4_mlp_klnd_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "gate_scope": "development_budget_decision_only_not_confirmatory_evidence",
        "candidate_variants": ["klnd1", "klnd2", "klnd3"],
        "variant_selection_rule": (
            "lowest four-unknown-metric mean rank over the frozen 14 scenarios; "
            "lexicographic method name breaks exact ties"
        ),
        "reference_methods": ["mlp_msp", "mlp_energy", "opendetect"],
        "unknown_metrics": [
            "unknown_auroc",
            "unknown_aupr",
            "unknown_fpr95",
            "oscr",
        ],
        "oriented_metric_rule": (
            "higher is better except lower unknown_fpr95 is better"
        ),
        "all_required_checks": {
            "pilot_runs_complete": "14/14 runs, 42 reports and zero failures",
            "split_integrity": (
                "k-LND, source MLP and OpenDetect split fingerprints identical"
            ),
            "known_only_fit": (
                "every class has correct train and validation support; no OOD fitting"
            ),
            "nondegenerate_score": (
                "all three validation and test risk standard deviations exceed 1e-12"
            ),
            "known_f1_tolerance": (
                "selected variant minus source-MSP mean >= -0.01 and worst >= -0.05"
            ),
            "top_half_rank": (
                "selected variant mean rank among six methods <= 3.0"
            ),
            "metric_breadth": (
                "selected variant beats MLP Energy on at least 2 of 4 mean metrics"
            ),
            "overall_gain": (
                "selected variant four-metric oriented mean gain over MLP Energy > 0"
            ),
            "suite_robustness": (
                "at least 4/7 suites nonnegative and worst suite >= -0.05"
            ),
        },
        "full_matrix_action": (
            "run all 102 frozen seed7 scenarios only if every required check passes"
        ),
        "failure_action": (
            "retain the 14-scenario three-variant pilot and do not spend full102 budget"
        ),
        "test_labels_used_for_gate": True,
        "gate_is_development_only": True,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(
        (args.pilot_root / "protocol_manifest.json").read_text(encoding="utf-8")
    )
    gate = create_gate(
        protocol, len(list(args.pilot_root.glob("*/*/metrics.json")))
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(gate, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
