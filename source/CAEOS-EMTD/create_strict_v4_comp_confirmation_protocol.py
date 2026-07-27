from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


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
SEEDS = [139, 149, 163]
SCENARIOS = {
    "stress": [
        "recon_os_scan",
        "ddos_udp_flood",
        "ddos_synonymous_ip_flood",
    ],
    "control": [
        "ddos_rstfin_flood",
        "ddos_http_flood",
        "ddos_slowloris",
    ],
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def scenario_index(diagnosis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = diagnosis.get("scenario_diagnostics")
    if not isinstance(rows, list) or len(rows) != 102:
        raise ValueError("diagnosis must contain 102 scenario rows")
    indexed = {}
    for row in rows:
        if row.get("suite") != "cic_iot2023":
            continue
        scenario = row.get("scenario")
        if not isinstance(scenario, str) or scenario in indexed:
            raise ValueError("invalid CIC-IoT2023 diagnosis row")
        indexed[scenario] = row
    if len(indexed) != 32:
        raise ValueError("exactly 32 CIC-IoT2023 scenarios required")
    return indexed


def create_protocol(
    *,
    diagnosis: dict[str, Any],
    diagnosis_path: Path,
    pairwise_manifest: dict[str, Any],
    pairwise_manifest_path: Path,
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    if (
        file_hash(diagnosis_path) != DIAGNOSIS_FILE_SHA256
        or diagnosis.get("manifest_sha256") != DIAGNOSIS_MANIFEST_SHA256
        or diagnosis.get("manifest_sha256") != canonical_hash(diagnosis)
        or diagnosis.get("passes") is not True
    ):
        raise ValueError("canonical Pairwise FPR95 diagnosis required")
    if (
        file_hash(pairwise_manifest_path) != PAIRWISE_MANIFEST_FILE_SHA256
        or pairwise_manifest.get("manifest_sha256") != PAIRWISE_MANIFEST_SHA256
        or pairwise_manifest.get("manifest_sha256")
        != canonical_hash(pairwise_manifest)
    ):
        raise ValueError("canonical frozen Pairwise manifest required")
    indexed = scenario_index(diagnosis)
    selected = set(SCENARIOS["stress"] + SCENARIOS["control"])
    if len(selected) != 6 or not selected <= set(indexed):
        raise ValueError("six unique frozen pilot scenarios required")
    for scenario in SCENARIOS["stress"]:
        row = indexed[scenario]
        if (
            row["outcome_vs_opendetect"] != "loss"
            or row["pairwise_plateau"][
                "minimum_plateau_explains_fpr95_one"
            ]
            is not True
        ):
            raise ValueError(f"stress scenario boundary drifted: {scenario}")
    for scenario in SCENARIOS["control"]:
        row = indexed[scenario]
        if row["pairwise_plateau"]["minimum_plateau_explains_fpr95_one"]:
            raise ValueError(f"control scenario has a forced floor: {scenario}")

    tasks = []
    for group, scenarios in SCENARIOS.items():
        for scenario in scenarios:
            development = indexed[scenario]
            for seed in SEEDS:
                tasks.append(
                    {
                        "suite": "cic_iot2023",
                        "scenario": scenario,
                        "group": group,
                        "seed": seed,
                        "development_seed7_pairwise_fpr95": development[
                            "pairwise_fpr95"
                        ],
                        "development_seed7_opendetect_fpr95": development[
                            "opendetect_fpr95"
                        ],
                    }
                )
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_comp_confirmation_protocol_v1",
        "state": "frozen_before_fresh_seed_execution",
        "candidate": {
            "method": "caeos_comp",
            "display_name": "CAEOS-COMP",
            "formula": "max(cauchy_evidence, modality_support_union)",
            "reference_formula": (
                "max(0, 2*max(cauchy_evidence, modality_support_union)-1)"
            ),
            "route": (
                "refine only when frozen training-time selected risk is "
                "cauchy_modality_support_union; otherwise preserve Pairwise"
            ),
            "threshold_calibration": "known_validation_empirical_percentile_q95",
            "unknown_or_test_labels_used_for_routing": False,
            "unknown_or_test_labels_used_for_threshold": False,
        },
        "pilot_scope": {
            "suite": "cic_iot2023",
            "stress_scenarios": SCENARIOS["stress"],
            "control_scenarios": SCENARIOS["control"],
            "seeds": SEEDS,
            "expected_pairwise_runs": len(tasks),
            "expected_opendetect_runs": len(tasks),
            "paired_task_count": len(tasks),
            "max_per_class": 1000,
        },
        "tasks": tasks,
        "execution": {
            "pairwise_risk_selection": (
                "nested_boundary_pairwise_pseudo_unknown_blend"
            ),
            "pairwise_policy_name": "strict_v4_comp_confirmation_pairwise_v1",
            "estimators": 80,
            "model_jobs": 8,
            "workers": 2,
            "opendetect_epochs": 0,
            "cache_must_be_seed_specific": True,
            "split_fingerprints_must_match_within_each_pair": True,
        },
        "admission_gate": {
            "candidate_vs_pairwise": {
                "mean_unknown_fpr95_oriented_improvement_minimum": 0.02,
                "mean_unknown_auroc_oriented_nonregression": -0.01,
                "mean_unknown_aupr_oriented_nonregression": -0.01,
                "mean_oscr_oriented_nonregression": -0.01,
                "known_macro_f1_absolute_tolerance": 1e-12,
                "per_task_unknown_fpr95_regression_tolerance": 0.02,
                "stress_group_fpr95_win_minimum": 5,
            },
            "candidate_vs_opendetect": {
                "mean_unknown_fpr95_noninferiority_margin": 0.01,
            },
            "all_checks_required": True,
            "passing_pilot_does_not_authorize_universal_sota": True,
            "passing_pilot_requires_cross_suite_expansion": True,
        },
        "input_evidence": {
            "diagnosis": {
                "path": str(diagnosis_path.resolve()),
                "file_sha256": DIAGNOSIS_FILE_SHA256,
                "manifest_sha256": DIAGNOSIS_MANIFEST_SHA256,
            },
            "pairwise_manifest": {
                "path": str(pairwise_manifest_path.resolve()),
                "file_sha256": PAIRWISE_MANIFEST_FILE_SHA256,
                "manifest_sha256": PAIRWISE_MANIFEST_SHA256,
            },
        },
        "implementation_sha256": implementation_sha256,
        "claim_boundary": {
            "seed7_candidate_effects_are_development_only": True,
            "fresh_seeds_have_not_been_used_for_candidate_selection": True,
            "scenario_identities_are_development_selected": True,
            "pilot_is_not_full102_confirmation": True,
            "pairwise_remains_incumbent_until_gate_passes": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
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
        default=Path(
            "results/strict_v4_comp_confirmation_v1/protocol.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    diagnosis_path = resolve(args.diagnosis)
    pairwise_manifest_path = resolve(args.pairwise_manifest)
    implementation_files = [
        Path(__file__).resolve(),
        root / "caeos/continuous_outer_min_p.py",
        root / "evaluate_strict_v4_comp_confirmation.py",
        root / "scripts/run_strict_v4_comp_confirmation.sh",
    ]
    implementation_sha256 = {
        str(path.relative_to(root)): file_hash(path) for path in implementation_files
    }
    protocol = create_protocol(
        diagnosis=load(diagnosis_path),
        diagnosis_path=diagnosis_path,
        pairwise_manifest=load(pairwise_manifest_path),
        pairwise_manifest_path=pairwise_manifest_path,
        implementation_sha256=implementation_sha256,
    )
    output = resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"manifest_sha256={protocol['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
