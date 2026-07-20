from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


METHODS = ("closr", "cade", "sieve")
SELECTED_SCENARIOS = {
    "cic_iot2023": ["ddos_icmp_fragmentation", "ddos_rstfin_flood"],
    "cic_ton_iot": ["ddos", "mitm"],
    "cicids2017": ["dos_hulk", "heartbleed"],
    "edge_iiot": ["ddos_icmp", "sql_injection"],
    "nf_cse": ["dos_slowhttptest", "ssh_bruteforce"],
    "nf_unsw": ["generic", "shellcode"],
    "ustc_tfc2016": ["htbot", "tinba"],
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_protocol(
    coverage: dict[str, Any], project_root: Path, observed_metrics: int
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage schema")
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("strict-v4 coverage SHA mismatch")
    if observed_metrics != 0:
        raise ValueError("external training pilot protocol must be frozen at zero results")
    registry = coverage.get("scenario_registry", {})
    for suite, scenarios in SELECTED_SCENARIOS.items():
        available = set(registry.get(suite, {}).get("scenarios", []))
        if not set(scenarios) <= available:
            raise ValueError("pilot scenario is outside coverage registry: %s" % suite)
    implementations = (
        "run_neural_baseline_matrix.py",
        "train_neural_open_set.py",
        "train_sieve_open_set.py",
    )
    result = {
        "schema_version": "strict_v4_external_training_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "scope": "development_budget_screen_not_confirmatory_inference",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": "two scenarios per suite selected by the existing coverage-SHA pilot registry",
        "selected_scenarios": SELECTED_SCENARIOS,
        "seed": 7,
        "methods": list(METHODS),
        "expected_scenarios": 14,
        "expected_runs": 42,
        "paper_aligned_epoch_budgets": {"closr": 100, "cade": 250, "sieve": 100},
        "fit_data": "known_training_only",
        "checkpoint_and_threshold_data": "known_validation_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "test_labels": "final_development_metrics_and_prefrozen_expansion_gate_only",
        "ood_parameter_sweep": False,
        "comparison_reference": "opendetect_on_identical_frozen_seed7_splits",
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in implementations
        },
        "pilot_metrics_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def create_gate(protocol: dict[str, Any]) -> dict[str, Any]:
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("external training pilot protocol SHA mismatch")
    result = {
        "schema_version": "strict_v4_external_training_pilot_expansion_gate_v1",
        "status": "frozen_before_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": protocol["pilot_metrics_observed_at_freeze"],
        "candidates": list(METHODS),
        "reference": "opendetect",
        "unknown_metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
        "oriented_metric_rule": "higher is better except lower unknown_fpr95 is better",
        "required_checks_per_candidate": {
            "pilot_runs_complete": "14/14 reports and zero failures",
            "split_and_leakage_integrity": "candidate, source MLP, and OpenDetect splits match; no unknown/test fitting",
            "known_f1_tolerance": "mean candidate-minus-OpenDetect Known F1 >= -0.03 and worst scenario >= -0.10",
            "top_two_rank": "candidate four-unknown-metric mean rank among candidate set plus OpenDetect <= 2.0",
            "metric_breadth": "candidate has positive oriented mean gain over OpenDetect on at least 2 of 4 metrics",
            "overall_gain": "candidate four-metric oriented mean gain over OpenDetect is strictly positive",
            "suite_robustness": "at least 4 of 7 suites are nonnegative and worst suite >= -0.05",
        },
        "full_matrix_action": "expand a candidate to all 102 frozen seed7 scenarios only if every check passes",
        "failure_action": "retain the pilot as negative strong-baseline evidence and do not spend full102 budget",
        "gate_is_development_only": True,
        "test_labels_used_for_gate": True,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--pilot-root", type=Path, required=True)
    args = parser.parse_args()
    observed = len(list(args.pilot_root.glob("*/*/metrics.json"))) if args.pilot_root.is_dir() else 0
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    protocol = create_protocol(coverage, args.project_root.resolve(), observed)
    gate = create_gate(protocol)
    args.pilot_root.mkdir(parents=True, exist_ok=True)
    outputs = {
        args.pilot_root / "protocol_manifest.json": protocol,
        args.pilot_root / "expansion_gate.json": gate,
    }
    for path, payload in outputs.items():
        if path.is_file() and json.loads(path.read_text(encoding="utf-8")) != payload:
            raise ValueError("existing frozen artifact differs: %s" % path)
        if not path.is_file():
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    print(json.dumps({"protocol": protocol["manifest_sha256"], "gate": gate["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
