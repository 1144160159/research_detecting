from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from caeos.pseudo_unknown_gated_continuous import PUG_GATE_V1
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


FAILURE_AUDIT_FILE_SHA256 = (
    "b41d3037de99b53877616faaa74106bd6e5c001e313dee5ce5c0856d33edf5be"
)
FAILURE_AUDIT_MANIFEST_SHA256 = (
    "fe77ed48305d5e2d9f07d6d3a3d1bd4ea18f63c03890937842023f50af3ab257"
)
COMP_CONFIRMATION_FILE_SHA256 = (
    "19b5c9031c6e82c98939568cb2c4210272f3a77ea5a484f1ff47495a994c4c34"
)
COMP_CONFIRMATION_MANIFEST_SHA256 = (
    "70a2eab357696dd4f8aebfd17eead4c2bbd8a80a15d7bf278bad603e9f034132"
)
DIAGNOSIS_FILE_SHA256 = (
    "1bfed984c44a9e95cb2e2f2b0a3d75dab779c2fcff2e94f6da7355a56c3a2da8"
)
DIAGNOSIS_MANIFEST_SHA256 = (
    "b1e1aa709fc3307cd5d7dbca3b4f495f0481881270ffb1b8427694a437d76404"
)
PAIRWISE_MANIFEST_FILE_SHA256 = (
    "14c36f8dd26f2b094def0626f1f008081918ece6f2987ea87c756aff4d7ffa4f"
)
PAIRWISE_MANIFEST_SHA256 = (
    "9fb6ba9a4c28be1cd3ef63153d814b4b5b956999890e24d35fbfd749d8091f01"
)

DEVELOPMENT_SCENARIOS = [
    "recon_os_scan",
    "ddos_udp_flood",
    "ddos_synonymous_ip_flood",
    "ddos_rstfin_flood",
    "ddos_http_flood",
    "ddos_slowloris",
]
DEVELOPMENT_SEEDS = [139, 149, 163]
RESERVED_CROSS_SUITE_SEEDS = [269, 271, 277]
FRESH_SEEDS = [283, 293, 307]
FRESH_SCENARIOS = {
    "stress": [
        "ddos_syn_flood",
        "mirai_greeth_flood",
        "dos_udp_flood",
    ],
    "control": [
        "backdoor_malware",
        "dns_spoofing",
        "ddos_icmp_fragmentation",
    ],
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _require_canonical(value: dict[str, Any], schema: str, label: str) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def _scenario_index(diagnosis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = diagnosis.get("scenario_diagnostics")
    if not isinstance(rows, list) or len(rows) != 102:
        raise ValueError("diagnosis must contain exactly 102 scenarios")
    indexed = {}
    for row in rows:
        if row.get("suite") != "cic_iot2023":
            continue
        scenario = row.get("scenario")
        if not isinstance(scenario, str) or scenario in indexed:
            raise ValueError("invalid CIC-IoT2023 scenario registry")
        indexed[scenario] = row
    if len(indexed) != 32:
        raise ValueError("diagnosis must contain exactly 32 CIC-IoT2023 scenarios")
    return indexed


def create_design(
    *,
    failure_audit: dict[str, Any],
    comp_confirmation: dict[str, Any],
    diagnosis: dict[str, Any],
    pairwise_manifest: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_output_counts: dict[str, int],
) -> dict[str, Any]:
    _require_canonical(
        failure_audit,
        "strict_v4_comp_confirmation_failure_audit_v1",
        "COMP failure audit",
    )
    _require_canonical(
        comp_confirmation,
        "strict_v4_comp_confirmation_v1",
        "COMP confirmation",
    )
    _require_canonical(
        diagnosis,
        "strict_v4_pairwise_opendetect_fpr95_tail_audit_v1",
        "Pairwise FPR95 diagnosis",
    )
    _require_canonical(
        pairwise_manifest,
        "strict_v4_boundary_pairwise_candidate_v1",
        "Pairwise manifest",
    )
    if (
        failure_audit.get("state") != "posthoc_development_diagnosis_complete"
        or failure_audit.get("source_decision", {}).get("passes") is not False
        or failure_audit.get("source_decision", {}).get(
            "pairwise_remains_incumbent"
        )
        is not True
        or failure_audit.get("diagnostics", {}).get(
            "development_feasible_gate_count"
        )
        != 0
        or failure_audit.get("diagnostics", {}).get("best_development_gate")
        is not None
    ):
        raise ValueError("frozen negative COMP failure diagnosis required")
    if (
        comp_confirmation.get("decision", {}).get("passes") is not False
        or comp_confirmation.get("decision", {}).get(
            "pairwise_remains_incumbent_if_false"
        )
        is not True
    ):
        raise ValueError("frozen negative COMP confirmation required")
    if diagnosis.get("passes") is not True:
        raise ValueError("passing Pairwise FPR95 diagnosis integrity required")
    if any(int(value) != 0 for value in observed_output_counts.values()):
        raise ValueError("PUG design must freeze before result outputs exist")

    selected_scenarios = [
        *FRESH_SCENARIOS["stress"],
        *FRESH_SCENARIOS["control"],
    ]
    if (
        len(selected_scenarios) != 6
        or len(set(selected_scenarios)) != 6
        or set(selected_scenarios) & set(DEVELOPMENT_SCENARIOS)
    ):
        raise ValueError("six fresh non-overlapping PUG scenarios required")
    if set(FRESH_SEEDS) & (
        set(DEVELOPMENT_SEEDS) | set(RESERVED_CROSS_SUITE_SEEDS) | {7}
    ):
        raise ValueError("PUG confirmation seeds must be unused")

    indexed = _scenario_index(diagnosis)
    for scenario in FRESH_SCENARIOS["stress"]:
        row = indexed.get(scenario)
        if (
            row is None
            or row.get("pairwise_plateau", {}).get(
                "minimum_plateau_explains_fpr95_one"
            )
            is not True
            or row.get("outcome_vs_opendetect") != "loss"
        ):
            raise ValueError(f"fresh stress boundary drifted: {scenario}")
    for scenario in FRESH_SCENARIOS["control"]:
        row = indexed.get(scenario)
        if row is None or row.get("pairwise_plateau", {}).get(
            "minimum_plateau_explains_fpr95_one"
        ):
            raise ValueError(f"fresh control boundary drifted: {scenario}")

    tasks = [
        {
            "suite": "cic_iot2023",
            "scenario": scenario,
            "group": group,
            "seed": seed,
        }
        for group, scenarios in FRESH_SCENARIOS.items()
        for scenario in scenarios
        for seed in FRESH_SEEDS
    ]
    design: dict[str, Any] = {
        "schema_version": "strict_v4_pug_design_protocol_v1",
        "state": "frozen_before_candidate_integration_and_fresh_seed_execution",
        "candidate": {
            "method": "caeos_pug",
            "display_name": "CAEOS-PUG",
            "expansion": "Pseudo-Unknown Gated Continuous Outer Min-P",
            "reference_route": "caeos_pairwise",
            "candidate_formula": (
                "max(cauchy_evidence, modality_support_union)"
            ),
            "eligible_base_risk": "cauchy_modality_support_union",
            "ineligible_base_route": "exact_pairwise_passthrough",
            "gate_failure_route": "exact_pairwise_passthrough",
        },
        "training_time_selection": {
            "folds": "leave_one_known_attack_out",
            "fit_scope": "training_and_known_validation_only",
            "pseudo_unknown_source": "held_out_known_attack_validation_fold",
            "threshold_calibration": (
                "per_candidate_remaining_known_validation_q95"
            ),
            "unknown_or_test_labels_used": False,
            "all_available_folds_required": True,
            "gate": {**PUG_GATE_V1, "all_checks_required": True},
        },
        "fresh_pilot": {
            "suite": "cic_iot2023",
            "stress_scenarios": FRESH_SCENARIOS["stress"],
            "control_scenarios": FRESH_SCENARIOS["control"],
            "seeds": FRESH_SEEDS,
            "paired_task_count": len(tasks),
            "expected_pairwise_pug_runs": len(tasks),
            "expected_opendetect_runs": len(tasks),
            "tasks": tasks,
            "execution_admitted_at_design_freeze": False,
        },
        "fresh_pilot_admission_gate": {
            "candidate_vs_pairwise": {
                "mean_unknown_fpr95_oriented_improvement_minimum": 0.02,
                "mean_unknown_auroc_oriented_nonregression": -0.005,
                "mean_unknown_aupr_oriented_nonregression": -0.005,
                "mean_oscr_oriented_nonregression": -0.005,
                "known_macro_f1_absolute_tolerance": 1e-12,
                "per_task_unknown_fpr95_regression_tolerance": 0.02,
                "per_task_unknown_aupr_regression_tolerance": 0.02,
                "stress_group_fpr95_win_minimum": 5,
            },
            "candidate_vs_opendetect": {
                "mean_unknown_fpr95_noninferiority_margin": 0.01,
            },
            "all_checks_required": True,
            "passing_requires_fresh_cross_suite_confirmation": True,
        },
        "freshness": {
            "comp_development_scenarios_excluded": DEVELOPMENT_SCENARIOS,
            "comp_development_seeds_excluded": DEVELOPMENT_SEEDS,
            "comp_reserved_cross_suite_seeds_excluded": (
                RESERVED_CROSS_SUITE_SEEDS
            ),
            "seed7_effects_are_development_only": True,
        },
        "input_manifest_sha256": {
            "failure_audit": failure_audit["manifest_sha256"],
            "comp_confirmation": comp_confirmation["manifest_sha256"],
            "pairwise_diagnosis": diagnosis["manifest_sha256"],
            "pairwise_manifest": pairwise_manifest["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "observed_output_counts_at_freeze": observed_output_counts,
        "claim_boundary": {
            "design_is_not_candidate_effect": True,
            "design_is_not_execution_admission": True,
            "comp_test_diagnostics_do_not_select_runtime_route": True,
            "fresh_pilot_is_not_full102_confirmation": True,
            "pairwise_remains_incumbent": True,
            "universal_or_comprehensive_sota_authorized": False,
        },
    }
    design["manifest_sha256"] = canonical_hash(design)
    return design


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--failure-audit",
        type=Path,
        default=Path(
            "results/strict_v4_comp_confirmation_failure_audit_v1/audit.json"
        ),
    )
    parser.add_argument(
        "--comp-confirmation",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/confirmation.json"),
    )
    parser.add_argument(
        "--diagnosis",
        type=Path,
        default=Path(
            "results/strict_v4_pairwise_opendetect_fpr95_tail_audit_v1/audit.json"
        ),
    )
    parser.add_argument(
        "--pairwise-manifest",
        type=Path,
        default=Path(
            "results/strict_v4_boundary_pairwise_development/candidate_manifest.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/strict_v4_pug_design_v1/design_protocol.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    input_paths = {
        "failure_audit": resolve(args.failure_audit),
        "comp_confirmation": resolve(args.comp_confirmation),
        "pairwise_diagnosis": resolve(args.diagnosis),
        "pairwise_manifest": resolve(args.pairwise_manifest),
    }
    expected_hashes = {
        "failure_audit": FAILURE_AUDIT_FILE_SHA256,
        "comp_confirmation": COMP_CONFIRMATION_FILE_SHA256,
        "pairwise_diagnosis": DIAGNOSIS_FILE_SHA256,
        "pairwise_manifest": PAIRWISE_MANIFEST_FILE_SHA256,
    }
    input_file_sha256 = {
        name: file_hash(path) for name, path in input_paths.items()
    }
    if input_file_sha256 != expected_hashes:
        raise ValueError("authoritative PUG design input file SHA drift")
    output_root = root / "results/strict_v4_pug_confirmation_v1"
    observed_output_counts = {
        "execution_protocol": int(
            (output_root / "execution_protocol.json").exists()
        ),
        "task_metrics": (
            len(list((output_root / "tasks").glob("*.json")))
            if (output_root / "tasks").exists()
            else 0
        ),
        "summary": int((output_root / "summary.json").exists()),
        "audit": int((output_root / "audit.json").exists()),
        "completion": int((output_root / "completion.json").exists()),
    }
    implementation_paths = [
        Path(__file__).resolve(),
        root / "caeos/pseudo_unknown_gated_continuous.py",
        root / "caeos/continuous_outer_min_p.py",
    ]
    design = create_design(
        failure_audit=load(input_paths["failure_audit"]),
        comp_confirmation=load(input_paths["comp_confirmation"]),
        diagnosis=load(input_paths["pairwise_diagnosis"]),
        pairwise_manifest=load(input_paths["pairwise_manifest"]),
        input_file_sha256=input_file_sha256,
        implementation_sha256={
            path.relative_to(root).as_posix(): file_hash(path)
            for path in implementation_paths
        },
        observed_output_counts=observed_output_counts,
    )
    output = resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(f"manifest_sha256={design['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
