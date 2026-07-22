from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def create_gate(protocol: dict[str, Any], observed_metrics: int) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_mlp_cadref_family_protocol_v1":
        raise ValueError("unexpected CADRef protocol schema")
    if protocol.get("mode") != "pilot" or protocol.get("expected_runs") != 14:
        raise ValueError("CADRef gate requires the 14-scenario pilot protocol")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("CADRef pilot protocol SHA mismatch")
    if observed_metrics != 0:
        raise ValueError("CADRef gate must be frozen before every pilot result")
    result = {
        "schema_version": "strict_v4_mlp_cadref_family_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "gate_scope": "development_budget_decision_only_not_confirmatory_evidence",
        "expansion_candidates": ["caref", "cadref_energy_fixed"],
        "reference_methods": ["mlp_energy", "opendetect"],
        "unknown_metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
        "per_candidate_required_checks": {
            "pilot_runs_complete": "14/14 reports and zero failures",
            "split_integrity": "candidate, source MLP and OpenDetect splits identical",
            "known_f1_nonregression": "absolute candidate-source Known F1 <= 1e-12",
            "formula_integrity": "official Eq.5/Eq.6/Eq.10 and Energy verified",
            "score_nonconstant": "validation and test score standard deviation > 1e-12",
            "top_two_rank": "candidate mean rank among four methods <= 2.0",
            "metric_breadth": "positive mean gain over Energy on at least 3/4 metrics",
            "overall_gain": "four-metric mean gain over Energy is positive",
            "suite_robustness": "at least 5/7 suites nonnegative and worst >= -0.03",
        },
        "full_matrix_action": "run both shared-pass methods on all 102 scenarios if either passes",
        "failure_action": "retain negative pilot and stop expansion",
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
    gate = create_gate(protocol, len(list(args.pilot_root.glob("*/*/metrics.json"))))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
