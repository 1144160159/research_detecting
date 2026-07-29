from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evaluate_strict_v4_benign_calibrated_warning import build_evaluation


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any], path: Path) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"canonical manifest mismatch: {path}")


def identity_coverage(
    records: list[dict[str, Any]],
    seeds: list[int],
    scenarios: list[str],
) -> dict[str, Any]:
    identities = [
        (str(record["suite"]), str(record["scenario"]), int(record["seed"]))
        for record in records
    ]
    expected = {
        ("cicids2017", scenario, seed)
        for scenario in scenarios
        for seed in seeds
    }
    observed = set(identities)
    return {
        "record_count": len(records),
        "unique_identity_count": len(observed),
        "duplicate_identity_count": len(identities) - len(observed),
        "missing_identities": [
            {"suite": suite, "scenario": scenario, "seed": seed}
            for suite, scenario, seed in sorted(expected - observed)
        ],
        "unexpected_identities": [
            {"suite": suite, "scenario": scenario, "seed": seed}
            for suite, scenario, seed in sorted(observed - expected)
        ],
        "passes": observed == expected and len(identities) == len(expected),
    }


def audit(
    *,
    project_root: Path,
    protocol_path: Path,
    evaluation_path: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol = load(protocol_path)
    verify_canonical(protocol, protocol_path)
    evaluation = load(evaluation_path)
    verify_canonical(evaluation, evaluation_path)

    seeds = [int(value) for value in protocol["seeds"]]
    scenarios = [str(value) for value in protocol["scenarios"]]
    budget = float(
        protocol["development_selection"][
            "selected_validation_benign_fpr_budget"
        ]
    )
    run_root = project_root / protocol["execution"]["run_root"]
    recomputed = build_evaluation(
        run_root,
        ["cicids2017"],
        budget,
        str(protocol["algorithm"]["alert_mode"]),
        seeds,
    )
    coverage = identity_coverage(evaluation["records"], seeds, scenarios)
    recomputed_coverage = identity_coverage(
        recomputed["records"], seeds, scenarios
    )

    evaluation_body = dict(evaluation)
    evaluation_body.pop("manifest_sha256", None)
    recomputed_body = dict(recomputed)
    recomputed_body.pop("manifest_sha256", None)
    exact_recomputation_match = evaluation_body == recomputed_body
    per_seed = evaluation.get("by_seed", {})
    expected_seed_keys = {str(seed) for seed in seeds}
    per_seed_scenario_counts_valid = (
        set(per_seed) == expected_seed_keys
        and all(
            int(per_seed[str(seed)]["scenario_count"]) == len(scenarios)
            for seed in seeds
        )
    )
    calibration_all_feasible = (
        evaluation["by_suite"]["cicids2017"][
            "calibration_feasible_count"
        ]
        == len(seeds) * len(scenarios)
    )
    integrity_checks = {
        "protocol_schema_valid": (
            protocol.get("schema_version")
            == "strict_v4_core_warning_execution_protocol_v1"
        ),
        "protocol_zero_result_status_valid": (
            protocol.get("status")
            == "frozen_zero_result_before_fresh_confirmation"
        ),
        "evaluation_schema_valid": (
            evaluation.get("schema_version")
            == "strict_v4_benign_calibrated_warning_evaluation_v1"
        ),
        "suite_valid": evaluation.get("suites") == ["cicids2017"],
        "seed_set_valid": evaluation.get("observed_seeds") == seeds,
        "budget_valid": (
            float(evaluation.get("validation_benign_fpr_budget", -1.0))
            == budget
        ),
        "alert_mode_valid": (
            evaluation.get("alert_mode")
            == protocol["algorithm"]["alert_mode"]
        ),
        "identity_coverage_valid": coverage["passes"],
        "recomputed_identity_coverage_valid": recomputed_coverage["passes"],
        "per_seed_scenario_counts_valid": per_seed_scenario_counts_valid,
        "calibration_all_feasible": calibration_all_feasible,
        "exact_recomputation_match": exact_recomputation_match,
        "unknown_or_test_labels_used_for_threshold": (
            evaluation.get("claim_boundary", {}).get(
                "unknown_or_test_labels_used_for_threshold"
            )
            is False
        ),
    }
    integrity_passes = all(integrity_checks.values())
    effect = {
        "all_seed_basic_warning_95_5_gate": bool(
            evaluation.get("all_seed_basic_warning_95_5_gate")
        ),
        "all_seed_full_known_unknown_95_5_gate": bool(
            evaluation.get("all_seed_full_known_unknown_95_5_gate")
        ),
        "per_seed": per_seed,
        "aggregate_gates": evaluation["aggregate_gates"],
        "suite_equal_mean": evaluation["suite_equal_mean"],
    }
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_core_warning_confirmation_audit_v1",
        "state": "complete" if integrity_passes else "invalid",
        "integrity_passes": integrity_passes,
        "eligible_basic_warning_claim": bool(
            integrity_passes
            and effect["all_seed_basic_warning_95_5_gate"]
        ),
        "eligible_full_open_set_claim": bool(
            integrity_passes
            and effect["all_seed_full_known_unknown_95_5_gate"]
        ),
        "integrity_checks": integrity_checks,
        "identity_coverage": coverage,
        "recomputed_identity_coverage": recomputed_coverage,
        "effect": effect,
        "bindings": {
            "protocol_path": str(protocol_path.resolve()),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "evaluation_path": str(evaluation_path.resolve()),
            "evaluation_file_sha256": file_hash(evaluation_path),
            "evaluation_manifest_sha256": evaluation["manifest_sha256"],
            "recomputed_manifest_sha256": recomputed["manifest_sha256"],
        },
        "claim_boundary": {
            "integrity_pass_does_not_imply_effect_pass": True,
            "basic_warning_pass_does_not_imply_full_open_set_pass": True,
            "single_suite_does_not_imply_comprehensive_sota": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(
        project_root=args.project_root,
        protocol_path=args.protocol,
        evaluation_path=args.evaluation,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "state": payload["state"],
                "integrity_passes": payload["integrity_passes"],
                "eligible_basic_warning_claim": payload[
                    "eligible_basic_warning_claim"
                ],
                "eligible_full_open_set_claim": payload[
                    "eligible_full_open_set_claim"
                ],
                "manifest_sha256": payload["manifest_sha256"],
            },
            sort_keys=True,
        )
    )
    if not payload["integrity_passes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
