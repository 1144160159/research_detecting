from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from audit_medaf_baseline_admission import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


SCHEMA = "strict_v4_medaf_tabular_design_v1"
OFFICIAL_COMMIT = "5d5328333af1f0857b9de20e94063ca8e6353d16"


def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_scenarios(
    coverage: Dict[str, Any],
    *,
    official_commit: str = OFFICIAL_COMMIT,
    per_suite: int = 2,
) -> Dict[str, List[str]]:
    selected: Dict[str, List[str]] = {}
    for suite, record in sorted(coverage["scenario_registry"].items()):
        scenarios = list(record["scenarios"])
        if len(scenarios) < per_suite:
            raise ValueError(f"{suite} has fewer than {per_suite} scenarios")
        ranked = sorted(
            scenarios,
            key=lambda scenario: (
                hashlib.sha256(
                    (
                        coverage["manifest_sha256"]
                        + "|"
                        + official_commit
                        + "|"
                        + suite
                        + "|"
                        + scenario
                    ).encode("utf-8")
                ).hexdigest(),
                scenario,
            ),
        )
        selected[suite] = ranked[:per_suite]
    return selected


def create_design(
    audit: Dict[str, Any],
    coverage: Dict[str, Any],
    *,
    input_file_sha256: Dict[str, str],
    implementation_sha256: Dict[str, str],
    result_count_at_freeze: int,
) -> Dict[str, Any]:
    if (
        audit.get("schema_version")
        != "strict_v4_medaf_baseline_admission_audit_v2"
        or audit.get("manifest_sha256") != canonical_hash(audit)
        or audit["decision"]["official_source_snapshot_admitted"] is not True
        or audit["decision"]["native_medaf_strict_v4_execution_admitted"]
        is not False
        or audit["decision"]["named_tabular_adapter_candidate"] is not True
    ):
        raise ValueError("canonical MEDAF v2 admission audit required")
    if (
        coverage.get("schema_version") != "strict_v4_coverage_manifest_v2"
        or coverage.get("manifest_sha256") != canonical_hash(coverage)
    ):
        raise ValueError("canonical strict-v4 coverage manifest required")
    if int(result_count_at_freeze) != 0:
        raise ValueError("MEDAF-Tabular design requires zero model results")
    scenarios = select_scenarios(coverage)
    scenario_count = sum(len(values) for values in scenarios.values())
    value: Dict[str, Any] = {
        "schema_version": SCHEMA,
        "status": "frozen_before_adapter_results",
        "method": {
            "name": "MEDAF-Tabular adapter",
            "official_method": "MEDAF",
            "official_commit": OFFICIAL_COMMIT,
            "not_native_medaf_reproduction": True,
            "formal_method_count_increment_at_design": 0,
        },
        "input_manifest_sha256": {
            "admission_audit": audit["manifest_sha256"],
            "coverage": coverage["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "mechanism": {
            "input_mapping": (
                "ordered tabular views concatenate into a shared embedding; "
                "embedding coordinates replace image spatial positions"
            ),
            "expert_count": 3,
            "class_activation_map": (
                "target-class classifier weight times expert embedding"
            ),
            "attention_diversity": (
                "official centered-positive normalized three-pair cosine sum"
            ),
            "gate": (
                "independent encoder with detached expert logits and "
                "sample-adaptive weights"
            ),
            "training_loss_weights": {
                "sum_three_expert_cross_entropy": 0.7,
                "gate_cross_entropy": 1.0,
                "attention_diversity": 0.01,
            },
            "gate_temperature": 100.0,
            "logit_temperature": 100.0,
            "risk": "one_minus_max_gated_softmax",
            "training_epochs": 150,
            "learning_rate": 0.1,
            "optimizer": "SGD",
            "momentum": 0.9,
            "weight_decay": 1e-5,
            "learning_rate_milestone": 130,
            "checkpoint": "fixed_final_epoch_150",
        },
        "leakage_policy": {
            "fit_split": "known_only_training",
            "checkpoint_selection": "none_fixed_final_epoch",
            "threshold_split": "known_only_validation",
            "known_acceptance_quantile": 0.95,
            "known_test_or_unknown_test_during_training_or_selection": False,
            "test_labels_for_final_metrics_only": True,
        },
        "pilot": {
            "training_seed": 383,
            "scenario_selection": {
                "rule": (
                    "per suite select two smallest SHA256 ranks over "
                    "coverage manifest, official commit, suite, scenario"
                ),
                "effect_metrics_used": False,
                "scenarios": scenarios,
            },
            "suite_count": len(scenarios),
            "scenario_count": scenario_count,
            "methods": [
                "medaf_tabular_adapter",
                "mlp_energy",
                "opendetect",
            ],
            "expected_reports": scenario_count * 3,
            "expansion_gate": {
                "complete_reports_required": scenario_count * 3,
                "failed_runs_maximum": 0,
                "split_fingerprint_match_required": True,
                "unknown_or_test_selection_count_maximum": 0,
                "risk_and_gate_non_degenerate_required": True,
                "unknown_metrics_improved_vs_mlp_energy_minimum": 2,
                "mean_oriented_unknown_gain_vs_mlp_energy_minimum": 0.0,
                "mean_unknown_metric_rank_maximum": 2.0,
                "known_macro_f1_mean_degradation_vs_opendetect_maximum": 0.03,
                "nonnegative_suite_gain_vs_mlp_energy_minimum": 4,
                "worst_suite_gain_vs_mlp_energy_minimum": -0.05,
            },
        },
        "full102_boundary": {
            "execution_admitted": False,
            "requires_positive_canonical_pilot_summary": True,
            "requires_separate_zero_result_protocol": True,
            "pilot_does_not_auto_launch_full102": True,
        },
        "execution_boundary": {
            "pilot_execution_admitted": False,
            "missing_before_execution": [
                "canonical 42-report pilot protocol",
                "resumable same-split runner",
                "canonical summarizer and independent auditor",
                "resource-idle watcher ordered after current queues",
            ],
        },
        "candidate_result_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    implementations: Dict[str, str] = {}
    for item in args.implementation:
        name, path = item.split("=", 1)
        implementations[name] = file_hash(Path(path))
    result_count = (
        sum(1 for _ in args.result_root.rglob("metrics.json"))
        if args.result_root.exists()
        else 0
    )
    value = create_design(
        load(args.audit),
        load(args.coverage),
        input_file_sha256={
            "admission_audit": file_hash(args.audit),
            "coverage": file_hash(args.coverage),
        },
        implementation_sha256=implementations,
        result_count_at_freeze=result_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
