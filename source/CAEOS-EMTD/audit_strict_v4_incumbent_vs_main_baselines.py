from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


FULL102_SUMMARY_FILE_SHA256 = (
    "fb2ed5a99d57ffde364db3791e90cfbae7b93f0ececcd9a93ea89210882aab6b"
)
CLASSICAL_PROTOCOL_FILE_SHA256 = (
    "0c50885ffeddb86c4d9fdb8f0677cea266328ece34d533a0662f67e6f5a0b347"
)
FINAL_DECISION_FILE_SHA256 = (
    "a815ce79f2c152c43ec17e1815bb78f6d5260c784c0ccc8c74aaa62056e9b1a9"
)
OPTIMAL_DECISION_FILE_SHA256 = (
    "ed35254e5dbb91591b06d7f6c7b8c89b1af1a32ad5cf186e85d7de30f50ad6d0"
)
METRICS = (
    ("known_macro_f1", "higher"),
    ("unknown_auroc", "higher"),
    ("unknown_aupr", "higher"),
    ("unknown_fpr95", "lower"),
    ("oscr", "higher"),
)
COMMON_FULL102_BASELINES = {
    "mlp_msp",
    "mlp_energy",
    "mlp_openmax",
    "mlp_knn",
    "mlp_vim",
    "opendetect",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def metric_values(row: dict[str, Any]) -> dict[str, float]:
    values = {}
    for metric, _direction in METRICS:
        value = row.get(metric)
        if not isinstance(value, (int, float)):
            raise ValueError(f"numeric {metric} required: {row.get('method')}")
        values[metric] = float(value)
    return values


def index_rows(rows: Any, expected_count: int, label: str) -> dict[str, Any]:
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError(f"exactly {expected_count} {label} rows required")
    indexed = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("method"), str):
            raise ValueError(f"invalid {label} row")
        method = str(row["method"])
        if method in indexed:
            raise ValueError(f"duplicate {label} method: {method}")
        metric_values(row)
        indexed[method] = row
    return indexed


def oriented_comparison(
    candidate: dict[str, Any], reference: dict[str, Any]
) -> dict[str, Any]:
    candidate_values = metric_values(candidate)
    reference_values = metric_values(reference)
    metrics = {}
    wins = 0
    ties = 0
    losses = 0
    for metric, direction in METRICS:
        raw_delta = candidate_values[metric] - reference_values[metric]
        oriented_delta = raw_delta if direction == "higher" else -raw_delta
        if close(oriented_delta, 0.0):
            outcome = "tie"
            ties += 1
        elif oriented_delta > 0.0:
            outcome = "win"
            wins += 1
        else:
            outcome = "loss"
            losses += 1
        metrics[metric] = {
            "direction": direction,
            "candidate": candidate_values[metric],
            "reference": reference_values[metric],
            "raw_delta": raw_delta,
            "oriented_delta": oriented_delta,
            "outcome": outcome,
        }
    return {
        "candidate": candidate["method"],
        "reference": reference["method"],
        "metrics": metrics,
        "win_count": wins,
        "tie_count": ties,
        "loss_count": losses,
        "strictly_dominates_all_five_metrics": wins == len(METRICS),
        "noninferior_on_all_five_metrics": losses == 0,
    }


def validate_sources(
    *,
    full102: dict[str, Any],
    full102_file_sha256: str,
    classical: dict[str, Any],
    classical_file_sha256: str,
    final_decision: dict[str, Any],
    final_decision_file_sha256: str,
    optimal_decision: dict[str, Any],
    optimal_decision_file_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if full102_file_sha256 != FULL102_SUMMARY_FILE_SHA256:
        raise ValueError("authoritative full102 summary file SHA drifted")
    if classical_file_sha256 != CLASSICAL_PROTOCOL_FILE_SHA256:
        raise ValueError("classical main-baseline protocol file SHA drifted")
    if final_decision_file_sha256 != FINAL_DECISION_FILE_SHA256:
        raise ValueError("final self-algorithm decision file SHA drifted")
    if optimal_decision_file_sha256 != OPTIMAL_DECISION_FILE_SHA256:
        raise ValueError("optimal self-algorithm decision file SHA drifted")
    require_canonical(
        classical,
        "strict_v4_classical_main_baseline_protocol_v1",
        "classical main-baseline protocol",
    )
    require_canonical(
        final_decision,
        "strict_v4_final_algorithm_decision_v1",
        "final self-algorithm decision",
    )
    require_canonical(
        optimal_decision,
        "strict_v4_optimal_self_algorithm_decision_v1",
        "optimal self-algorithm decision",
    )
    validation = full102.get("validation", {})
    if (
        full102.get("schema_version")
        != "strict_v4_full103_coverage_summary_v1"
        or validation.get("passes") is not True
        or validation.get("dataset_count") != 7
        or validation.get("scenario_count") != 102
        or validation.get("method_count") != 22
        or validation.get("split_fingerprint_pair_checks") != 102
        or validation.get("split_fingerprints_identical") is not True
        or validation.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError("authoritative full102 validation boundary drifted")
    if (
        final_decision.get("selected_algorithm") != "caeos_pairwise"
        or final_decision.get("selection_is_pre_registered") is not True
        or final_decision.get("confirmation_gate_passes") is not False
        or optimal_decision.get("selected_algorithm") != "caeos_pairwise"
        or optimal_decision.get("incumbent_algorithm") != "caeos_pairwise"
        or optimal_decision.get("selection_is_pre_registered") is not True
        or optimal_decision.get("status") != "frozen_optimal_self_algorithm"
        or optimal_decision.get("input_file_sha256", {}).get(
            "incumbent_decision"
        )
        != final_decision_file_sha256
    ):
        raise ValueError("Pairwise incumbent decision boundary drifted")

    full_rows = index_rows(full102.get("overall"), 22, "full102")
    main_table = classical.get("main_table", {})
    baselines = main_table.get("baselines")
    if (
        main_table.get("baseline_count") != 7
        or not isinstance(baselines, list)
        or len(baselines) != 7
    ):
        raise ValueError("exactly seven frozen main baselines required")
    classical_rows = {}
    for baseline in baselines:
        method = baseline.get("method")
        evidence = baseline.get("overall_evidence")
        if (
            not isinstance(method, str)
            or not isinstance(evidence, dict)
            or evidence.get("method") != method
            or method in classical_rows
        ):
            raise ValueError("invalid frozen main-baseline evidence")
        metric_values(evidence)
        classical_rows[method] = evidence
    if set(classical_rows) != set(main_table.get("method_order", [])):
        raise ValueError("frozen main-baseline method order drifted")
    for method in COMMON_FULL102_BASELINES:
        if method not in full_rows or method not in classical_rows:
            raise ValueError(f"missing common strict-v4 method: {method}")
        for metric, _direction in METRICS:
            if not close(
                full_rows[method][metric], classical_rows[method][metric]
            ):
                raise ValueError(
                    f"cross-summary metric mismatch: {method}/{metric}"
                )
    for required in ("caeos_pairwise", "caeos_domain_safe_router"):
        if required not in full_rows:
            raise ValueError(f"missing self-algorithm row: {required}")
    return full_rows, classical_rows


def create_audit(
    *,
    full102: dict[str, Any],
    full102_path: Path,
    full102_file_sha256: str,
    classical: dict[str, Any],
    classical_path: Path,
    classical_file_sha256: str,
    final_decision: dict[str, Any],
    final_decision_path: Path,
    final_decision_file_sha256: str,
    optimal_decision: dict[str, Any],
    optimal_decision_path: Path,
    optimal_decision_file_sha256: str,
    implementation_sha256: str,
) -> dict[str, Any]:
    full_rows, classical_rows = validate_sources(
        full102=full102,
        full102_file_sha256=full102_file_sha256,
        classical=classical,
        classical_file_sha256=classical_file_sha256,
        final_decision=final_decision,
        final_decision_file_sha256=final_decision_file_sha256,
        optimal_decision=optimal_decision,
        optimal_decision_file_sha256=optimal_decision_file_sha256,
    )
    incumbent = full_rows["caeos_pairwise"]
    comparisons = []
    for method in classical["main_table"]["method_order"]:
        comparison = oriented_comparison(incumbent, classical_rows[method])
        comparison["display_name"] = next(
            baseline["display_name"]
            for baseline in classical["main_table"]["baselines"]
            if baseline["method"] == method
        )
        comparisons.append(comparison)
    router = full_rows["caeos_domain_safe_router"]
    router_comparison = oriented_comparison(router, incumbent)
    audit: dict[str, Any] = {
        "schema_version": (
            "strict_v4_incumbent_vs_classical_main_baselines_audit_v1"
        ),
        "state": "current_internal_incumbent_comparison_complete",
        "passes": True,
        "incumbent": {
            "method": "caeos_pairwise",
            "overall_evidence": incumbent,
            "selection_is_pre_registered": True,
            "selected_by_final_and_optimal_decisions": True,
        },
        "main_baseline_comparisons": comparisons,
        "summary": {
            "baseline_count": len(comparisons),
            "strict_five_metric_dominance_count": sum(
                comparison["strictly_dominates_all_five_metrics"]
                for comparison in comparisons
            ),
            "four_or_more_metric_win_count": sum(
                comparison["win_count"] >= 4 for comparison in comparisons
            ),
            "opendetect_win_count": next(
                comparison["win_count"]
                for comparison in comparisons
                if comparison["reference"] == "opendetect"
            ),
            "opendetect_loss_metrics": [
                metric
                for metric, evidence in next(
                    comparison["metrics"]
                    for comparison in comparisons
                    if comparison["reference"] == "opendetect"
                ).items()
                if evidence["outcome"] == "loss"
            ],
        },
        "unconfirmed_development_challenger": {
            "method": "caeos_domain_safe_router",
            "overall_evidence": router,
            "comparison_vs_incumbent": router_comparison,
            "confirmation_gate_passes": False,
            "confirmation_decision_checks": final_decision[
                "confirmation_decision_checks"
            ],
            "must_not_replace_incumbent": True,
        },
        "input_evidence": {
            "full102": {
                "path": str(full102_path.resolve()),
                "file_sha256": full102_file_sha256,
                "scenario_count": 102,
                "method_count": 22,
            },
            "classical_protocol": {
                "path": str(classical_path.resolve()),
                "manifest_sha256": classical["manifest_sha256"],
                "file_sha256": classical_file_sha256,
            },
            "final_decision": {
                "path": str(final_decision_path.resolve()),
                "manifest_sha256": final_decision["manifest_sha256"],
                "file_sha256": final_decision_file_sha256,
            },
            "optimal_decision": {
                "path": str(optimal_decision_path.resolve()),
                "manifest_sha256": optimal_decision["manifest_sha256"],
                "file_sha256": optimal_decision_file_sha256,
            },
        },
        "implementation_sha256": {
            "audit_strict_v4_incumbent_vs_main_baselines.py": (
                implementation_sha256
            )
        },
        "claim_boundary": {
            "internal_seed7_102_scenario_comparison_only": True,
            "does_not_authorize_universal_sota": True,
            "pairwise_does_not_strictly_dominate_every_main_baseline": True,
            "confirmation_failure_blocks_router_replacement": True,
            "krc_and_rrc_terminal_outcomes_remain_pending": True,
            "external_malicious_benign_safety_and_efficiency_remain_separate": True,
        },
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full102", type=Path, required=True)
    parser.add_argument("--classical-protocol", type=Path, required=True)
    parser.add_argument("--final-decision", type=Path, required=True)
    parser.add_argument("--optimal-decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    implementation_path = Path(__file__).resolve()
    audit = create_audit(
        full102=load(args.full102),
        full102_path=args.full102,
        full102_file_sha256=file_hash(args.full102),
        classical=load(args.classical_protocol),
        classical_path=args.classical_protocol,
        classical_file_sha256=file_hash(args.classical_protocol),
        final_decision=load(args.final_decision),
        final_decision_path=args.final_decision,
        final_decision_file_sha256=file_hash(args.final_decision),
        optimal_decision=load(args.optimal_decision),
        optimal_decision_path=args.optimal_decision,
        optimal_decision_file_sha256=file_hash(args.optimal_decision),
        implementation_sha256=file_hash(implementation_path),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(audit["manifest_sha256"])


if __name__ == "__main__":
    main()
