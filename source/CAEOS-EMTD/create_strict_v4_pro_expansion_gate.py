from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def create_gate(protocol: dict[str, Any], observed_metrics: int) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_mlp_pro_msp_fixed_protocol_v1":
        raise ValueError("unexpected PRO protocol schema")
    if protocol.get("mode") != "pilot" or protocol.get("expected_runs") != 14:
        raise ValueError("PRO gate requires the 14-scenario pilot protocol")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("PRO pilot protocol SHA mismatch")
    if observed_metrics != 0:
        raise ValueError("PRO gate must be frozen before every pilot result")
    result = {
        "schema_version": "strict_v4_mlp_pro_msp_fixed_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "strict_run_before_preregistration": True,
        "gate_scope": "development_budget_decision_only_not_confirmatory_evidence",
        "expansion_candidate": "pro_msp_fixed",
        "reference_methods": ["mlp_msp", "mlp_energy", "opendetect"],
        "unknown_metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
        "all_required_checks": {
            "pilot_runs_complete": "14/14 reports and zero failures",
            "split_integrity": "PRO, source MLP and OpenDetect splits identical",
            "known_f1_nonregression": "absolute PRO minus source MLP Known F1 <= 1e-12",
            "formula_integrity": "official PROv2-MSP defaults and path minimum verified",
            "top_two_rank": "PRO mean rank among four methods <= 2.0",
            "metric_breadth": "positive mean gain over MSP on at least 3 of 4 metrics",
            "overall_gain": "four-metric mean gain over MSP is positive",
            "suite_robustness": "at least 5/7 suites nonnegative and worst >= -0.03",
        },
        "full_matrix_action": "run all 102 seed7 scenarios only if every check passes",
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
