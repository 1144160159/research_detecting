from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def create_gate(protocol: dict[str, Any], observed_metrics: int) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_mlp_adascale_protocol_v1":
        raise ValueError("unexpected AdaSCALE protocol schema")
    if protocol.get("mode") != "pilot" or protocol.get("expected_runs") != 14:
        raise ValueError("AdaSCALE expansion gate requires the 14-scenario pilot protocol")
    required = {
        "p_min": 60.0,
        "p_max": 85.0,
        "k1_percent": 1.0,
        "k2_percent": 5.0,
        "lambda": 10.0,
        "perturb_fraction": 0.05,
        "epsilon": 0.5,
        "temperature": 1.0,
    }
    for name, expected in required.items():
        if protocol.get(name) != expected:
            raise ValueError("AdaSCALE protocol parameter %s is not frozen" % name)
    if protocol.get("fit_data") != "known_validation_ecdf_only":
        raise ValueError("AdaSCALE fitting must use known validation ECDF only")
    if protocol.get("ood_parameter_sweep") is not False:
        raise ValueError("AdaSCALE expansion gate forbids OOD parameter sweeping")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("AdaSCALE pilot protocol SHA mismatch")
    if observed_metrics != 0:
        raise ValueError("AdaSCALE expansion gate must be frozen before every pilot result")
    result = {
        "schema_version": "strict_v4_mlp_adascale_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "strict_run_before_preregistration": True,
        "gate_scope": "development_budget_decision_only_not_confirmatory_evidence",
        "expansion_candidate": "adascale_a_60_85",
        "fixed_parameters": required,
        "ood_parameter_tuning": False,
        "reference_methods": ["mlp_scale", "mlp_energy", "opendetect"],
        "primary_reference": "mlp_scale",
        "unknown_metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
        "oriented_metric_rule": "higher is better except lower unknown_fpr95 is better",
        "all_required_checks": {
            "pilot_runs_complete": "14/14 reports and zero failures",
            "split_integrity": "AdaSCALE, source MLP and OpenDetect fingerprints identical",
            "known_f1_tolerance": "mean AdaSCALE minus SCALE Known F1 >= -0.005 and worst >= -0.02",
            "top_two_rank": "AdaSCALE four-unknown-metric mean rank among four methods <= 2.0",
            "metric_breadth": "positive mean oriented gain over SCALE on at least 2 of 4 metrics",
            "overall_gain": "four-metric AdaSCALE-versus-SCALE oriented mean gain > 0",
            "suite_robustness": "at least 4 of 7 suites nonnegative and worst suite >= -0.05",
        },
        "full_matrix_action": "run all 102 frozen seed7 scenarios only if every check passes",
        "failure_action": "retain the 14-scenario pilot and do not spend full-matrix budget",
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
