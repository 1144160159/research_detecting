from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def create_gate(protocol: dict[str, Any], observed_metrics: int) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_mlp_odin_protocol_v1":
        raise ValueError("unexpected ODIN protocol schema")
    if protocol.get("mode") != "pilot" or protocol.get("expected_runs") != 14:
        raise ValueError("ODIN expansion gate requires the 14-scenario pilot protocol")
    if protocol.get("temperature") != 1000.0 or protocol.get("noise") != 0.001:
        raise ValueError("ODIN expansion gate requires frozen T=1000 and noise=0.001")
    if protocol.get("fit_data") != "none":
        raise ValueError("ODIN expansion gate forbids OOD parameter fitting")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("ODIN pilot protocol SHA mismatch")
    if observed_metrics != 0:
        raise ValueError("ODIN expansion gate must be frozen before every pilot result")
    result = {
        "schema_version": "strict_v4_mlp_odin_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "strict_run_before_preregistration": True,
        "gate_scope": "development_budget_decision_only_not_confirmatory_evidence",
        "expansion_candidate": "odin",
        "fixed_parameters": {"temperature": 1000.0, "noise": 0.001},
        "ood_parameter_tuning": False,
        "reference_methods": ["mlp_energy", "opendetect"],
        "unknown_metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
        "oriented_metric_rule": "higher is better except lower unknown_fpr95 is better",
        "all_required_checks": {
            "pilot_runs_complete": "14/14 reports and zero failures",
            "split_integrity": "ODIN, source MLP and OpenDetect split fingerprints identical",
            "known_f1_nonregression": "absolute ODIN minus source-energy Known F1 <= 1e-12 in every scenario",
            "top_two_rank": "ODIN four-unknown-metric mean rank among three pilot methods <= 2.0",
            "metric_breadth": "ODIN has positive mean oriented gain over Energy on at least 2 of 4 metrics",
            "overall_gain": "mean of four ODIN-versus-Energy oriented mean gains is strictly positive",
            "suite_robustness": "at least 4 of 7 suites have nonnegative four-metric mean gain and worst suite >= -0.05",
        },
        "full_matrix_action": "run all 102 frozen seed7 scenarios only if every required check passes",
        "failure_action": "retain the 14-scenario negative pilot and do not spend the full-matrix budget",
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
    observed = len(list(args.pilot_root.glob("*/*/metrics.json")))
    gate = create_gate(protocol, observed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(gate, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
