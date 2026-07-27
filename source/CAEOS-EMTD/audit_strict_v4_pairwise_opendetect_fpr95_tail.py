from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import roc_curve

from analyze_caeos_closr_fusion import empirical_percentile
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from summarize_strict_v4_full103 import load_blocks


FULL102_SUMMARY_FILE_SHA256 = (
    "fb2ed5a99d57ffde364db3791e90cfbae7b93f0ececcd9a93ea89210882aab6b"
)
COVERAGE_MANIFEST_FILE_SHA256 = (
    "b0426e466d58dabed3b5b5b16a14fef59bc2719ab24916f21568690236c81fbc"
)
RAW_FUSION_FILE_SHA256 = (
    "a13d365aa6109548c41874679bc66825433b7b400615d3dbec6cd51d1fd296a7"
)
ROUTER_MANIFEST_FILE_SHA256 = (
    "d523996471848c7658d2f1e38f4b14c755c6c623b9a91cda92043be64390ead0"
)
INCUMBENT_AUDIT_FILE_SHA256 = (
    "927634bc86c2616590a2e7c5441b5bedf9219d827405fdea14f6135c3ea61d2a"
)
PAIRWISE = "caeos_pairwise"
OPENDETECT = "opendetect"
BASE_RISK = "cauchy_modality_support_union"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_hash(path: Path, expected: str, label: str) -> str:
    observed = file_hash(path)
    if observed != expected:
        raise ValueError(f"{label} file SHA drifted: {observed}")
    return observed


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def fpr95_details(target: np.ndarray, risk: np.ndarray) -> dict[str, float]:
    target = np.asarray(target, dtype=np.int64).reshape(-1)
    risk = np.asarray(risk, dtype=np.float64).reshape(-1)
    if target.shape != risk.shape or set(np.unique(target)) != {0, 1}:
        raise ValueError("binary target and risk must have matching non-empty shapes")
    fpr, tpr, thresholds = roc_curve(target, risk)
    selected = np.flatnonzero(tpr >= 0.95)
    if not len(selected):
        return {"fpr95": 1.0, "threshold": float("-inf"), "tpr": 0.0}
    index = int(selected[0])
    return {
        "fpr95": float(fpr[index]),
        "threshold": float(thresholds[index]),
        "tpr": float(tpr[index]),
    }


def largest_tie_fraction(values: np.ndarray) -> float:
    values = np.asarray(values).reshape(-1)
    if not len(values):
        raise ValueError("tie fraction requires at least one value")
    return float(np.unique(values, return_counts=True)[1].max() / len(values))


def plateau_stats(risk: np.ndarray, unknown: np.ndarray) -> dict[str, Any]:
    risk = np.asarray(risk, dtype=np.float64).reshape(-1)
    unknown = np.asarray(unknown, dtype=bool).reshape(-1)
    if risk.shape != unknown.shape or not unknown.any() or unknown.all():
        raise ValueError("risk requires both known and unknown samples")
    minimum = float(risk.min())
    at_minimum = risk == minimum
    known = ~unknown
    unknown_minimum_fraction = float(at_minimum[unknown].mean())
    known_minimum_fraction = float(at_minimum[known].mean())
    details = fpr95_details(unknown.astype(np.int64), risk)
    floor_explains_one = (
        close(details["fpr95"], 1.0)
        and unknown_minimum_fraction > 0.05
        and known_minimum_fraction > 0.0
    )
    return {
        "sample_count": int(len(risk)),
        "known_count": int(known.sum()),
        "unknown_count": int(unknown.sum()),
        "minimum": minimum,
        "minimum_is_exact_zero": minimum == 0.0,
        "known_at_minimum_fraction": known_minimum_fraction,
        "unknown_at_minimum_fraction": unknown_minimum_fraction,
        "known_largest_tie_fraction": largest_tie_fraction(risk[known]),
        "unknown_largest_tie_fraction": largest_tie_fraction(risk[unknown]),
        "known_quantile_05": float(np.quantile(risk[known], 0.05)),
        "unknown_quantile_05": float(np.quantile(risk[unknown], 0.05)),
        "unique_value_count": int(np.unique(risk).size),
        "fpr95": details["fpr95"],
        "fpr95_threshold": details["threshold"],
        "fpr95_observed_tpr": details["tpr"],
        "minimum_plateau_explains_fpr95_one": floor_explains_one,
    }


def selected_risk_name(evidence: Any) -> str:
    value = np.asarray(evidence["selected_risk_name"])
    if value.size != 1:
        raise ValueError("selected_risk_name must be scalar")
    return str(value.item())


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("mean requires values")
    return float(np.mean(np.asarray(values, dtype=np.float64)))


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = Counter(row["outcome_vs_opendetect"] for row in rows)
    return {
        "scenario_count": len(rows),
        "pairwise_mean_fpr95": mean([row["pairwise_fpr95"] for row in rows]),
        "opendetect_mean_fpr95": mean([row["opendetect_fpr95"] for row in rows]),
        "pairwise_minus_opendetect_mean_fpr95": mean(
            [row["pairwise_minus_opendetect_fpr95"] for row in rows]
        ),
        "pairwise_win_count": outcomes["win"],
        "tie_count": outcomes["tie"],
        "pairwise_loss_count": outcomes["loss"],
        "pairwise_fpr95_one_count": sum(
            close(row["pairwise_fpr95"], 1.0) for row in rows
        ),
        "minimum_plateau_explains_fpr95_one_count": sum(
            row["pairwise_plateau"]["minimum_plateau_explains_fpr95_one"]
            for row in rows
        ),
        "base_bonferroni_zero_floor_count": sum(
            row["selected_risk"] == BASE_RISK
            and row["pairwise_raw_plateau"]["minimum_is_exact_zero"]
            for row in rows
        ),
    }


def find_overall(summary: dict[str, Any], method: str) -> dict[str, Any]:
    matches = [
        row
        for row in summary.get("overall", [])
        if isinstance(row, dict) and row.get("method") == method
    ]
    if len(matches) != 1:
        raise ValueError(f"exactly one overall row required for {method}")
    return matches[0]


def create_audit(
    *,
    project_root: Path,
    summary_path: Path,
    manifest_path: Path,
    raw_path: Path,
    router_path: Path,
    incumbent_audit_path: Path,
    gate_root: Path,
    mlp_root: Path,
    baseline_root: Path,
    implementation_sha256: str,
) -> dict[str, Any]:
    input_hashes = {
        "full102_summary": require_hash(
            summary_path, FULL102_SUMMARY_FILE_SHA256, "full102 summary"
        ),
        "coverage_manifest": require_hash(
            manifest_path, COVERAGE_MANIFEST_FILE_SHA256, "coverage manifest"
        ),
        "raw_fusion": require_hash(
            raw_path, RAW_FUSION_FILE_SHA256, "raw fusion"
        ),
        "router_manifest": require_hash(
            router_path, ROUTER_MANIFEST_FILE_SHA256, "router manifest"
        ),
        "incumbent_audit": require_hash(
            incumbent_audit_path, INCUMBENT_AUDIT_FILE_SHA256, "incumbent audit"
        ),
    }
    summary = load(summary_path)
    manifest = load(manifest_path)
    raw = load(raw_path)
    router = load(router_path)
    incumbent_audit = load(incumbent_audit_path)
    if (
        summary.get("schema_version") != "strict_v4_full103_coverage_summary_v1"
        or incumbent_audit.get("schema_version")
        != "strict_v4_incumbent_vs_classical_main_baselines_audit_v1"
        or incumbent_audit.get("incumbent", {}).get("method") != PAIRWISE
        or incumbent_audit.get("summary", {}).get("opendetect_loss_metrics")
        != ["unknown_fpr95"]
    ):
        raise ValueError("incumbent comparison boundary drifted")

    blocks, block_validation = load_blocks(
        manifest, raw, router, gate_root, mlp_root, baseline_root
    )
    if (
        block_validation.get("passes") is not True
        or block_validation.get("scenario_count") != 102
        or block_validation.get("artifact_checks") != 1326
        or block_validation.get("split_fingerprint_pair_checks") != 102
        or block_validation.get("independent_baseline_run_checks") != 204
    ):
        raise ValueError("full102 raw-artifact validation boundary drifted")

    rows = []
    selected_paths: Counter[str] = Counter()
    by_suite: dict[str, list[dict[str, Any]]] = defaultdict(list)
    raw_runs = {}
    for run in raw["runs"]:
        scenario, seed_text = str(run["task"]).rsplit("_seed", 1)
        if int(seed_text) != 7:
            raise ValueError("raw fusion must contain only seed7 tasks")
        raw_runs[(str(run["suite"]), scenario)] = run
    for key, reports in sorted(blocks.items()):
        suite, scenario = key.split("/", 1)
        run = raw_runs[(suite, scenario)]
        gate_dir = gate_root / suite / f"{scenario}_seed7"
        baseline_dir = baseline_root / suite / f"{scenario}_seed7_opendetect"
        with np.load(gate_dir / "scores.npz", allow_pickle=False) as scores, np.load(
            gate_dir / "evidence_package.npz", allow_pickle=False
        ) as evidence, np.load(
            baseline_dir / "scores.npz", allow_pickle=False
        ) as opendetect:
            unknown = np.asarray(scores["test_unknown"], dtype=bool)
            baseline_unknown = np.asarray(opendetect["test_unknown"], dtype=bool)
            if not np.array_equal(unknown, baseline_unknown):
                raise ValueError(f"test unknown mask mismatch: {key}")
            risk_name = str(run["gate_selected_risk"])
            if (
                f"validation_{risk_name}" not in scores
                or f"test_{risk_name}" not in scores
            ):
                raise ValueError(f"selected Pairwise risk is absent: {key}/{risk_name}")
            raw_pairwise_risk = np.asarray(
                scores[f"test_{risk_name}"], dtype=np.float64
            )
            if (
                selected_risk_name(evidence) != risk_name
                or not np.array_equal(
                    np.asarray(evidence["test_selected_risk"], dtype=np.float64),
                    raw_pairwise_risk,
                )
            ):
                raise ValueError(f"Pairwise evidence package drifted: {key}")
            pairwise_risk = empirical_percentile(
                np.asarray(scores[f"validation_{risk_name}"], dtype=np.float64),
                raw_pairwise_risk,
            )
            opendetect_risk = np.asarray(
                opendetect["test_opendetect"], dtype=np.float64
            )
            selected_paths[risk_name] += 1
            pairwise_raw_plateau = plateau_stats(raw_pairwise_risk, unknown)
            pairwise_plateau = plateau_stats(pairwise_risk, unknown)
            opendetect_plateau = plateau_stats(opendetect_risk, unknown)

        reported_pairwise = float(reports[PAIRWISE]["unknown_fpr95"])
        reported_opendetect = float(reports[OPENDETECT]["unknown_fpr95"])
        if not close(pairwise_plateau["fpr95"], reported_pairwise):
            raise ValueError(f"Pairwise FPR95 recomputation mismatch: {key}")
        if not close(opendetect_plateau["fpr95"], reported_opendetect):
            raise ValueError(f"OpenDetect FPR95 recomputation mismatch: {key}")
        delta = reported_pairwise - reported_opendetect
        outcome = "tie" if close(delta, 0.0) else ("win" if delta < 0.0 else "loss")
        row = {
            "suite": suite,
            "scenario": scenario,
            "seed": 7,
            "selected_risk": risk_name,
            "pairwise_fpr95": reported_pairwise,
            "opendetect_fpr95": reported_opendetect,
            "pairwise_minus_opendetect_fpr95": delta,
            "outcome_vs_opendetect": outcome,
            "pairwise_raw_plateau": pairwise_raw_plateau,
            "pairwise_plateau": pairwise_plateau,
            "opendetect_plateau": opendetect_plateau,
        }
        rows.append(row)
        by_suite[suite].append(row)

    overall = summarize_rows(rows)
    pairwise_summary = find_overall(summary, PAIRWISE)
    opendetect_summary = find_overall(summary, OPENDETECT)
    if not close(overall["pairwise_mean_fpr95"], pairwise_summary["unknown_fpr95"]):
        raise ValueError("Pairwise overall FPR95 does not reconcile")
    if not close(
        overall["opendetect_mean_fpr95"], opendetect_summary["unknown_fpr95"]
    ):
        raise ValueError("OpenDetect overall FPR95 does not reconcile")

    plateau_failures = [
        row
        for row in rows
        if row["pairwise_plateau"]["minimum_plateau_explains_fpr95_one"]
    ]
    audit: dict[str, Any] = {
        "schema_version": "strict_v4_pairwise_opendetect_fpr95_tail_audit_v1",
        "state": "seed7_test_diagnostic_complete_candidate_not_selected",
        "passes": True,
        "validation": {
            **block_validation,
            "recomputed_pairwise_and_opendetect_fpr95_for_all_scenarios": True,
            "reconciles_authoritative_overall_summary": True,
        },
        "overall": overall,
        "by_suite": {
            suite: summarize_rows(suite_rows)
            for suite, suite_rows in sorted(by_suite.items())
        },
        "selected_risk_distribution": dict(sorted(selected_paths.items())),
        "diagnosis": {
            "pairwise_fpr95_is_only_frozen_main_baseline_loss_metric": True,
            "pairwise_fpr95_one_count": overall["pairwise_fpr95_one_count"],
            "minimum_plateau_explains_fpr95_one_count": overall[
                "minimum_plateau_explains_fpr95_one_count"
            ],
            "explained_failure_keys": [
                f"{row['suite']}/{row['scenario']}" for row in plateau_failures
            ],
            "mechanism": (
                "The raw outer Bonferroni union is "
                "max(0, 2*max(r1,r2)-1). When both constituent risks are at "
                "most 0.5, it creates an exact zero plateau. Known-validation "
                "empirical-percentile calibration maps that plateau to one "
                "shared minimum rank. If more than 5% of unknown samples share "
                "the calibrated global minimum with known samples, ROC cannot "
                "reach 95% TPR before admitting that plateau, so FPR95 jumps "
                "to 1.0."
            ),
            "heterogeneous_not_global": len(plateau_failures) < len(rows),
        },
        "single_frozen_hypothesis_for_fresh_confirmation": {
            "working_name": "continuous_outer_min_p_refinement",
            "formula": "risk = max(cauchy_evidence, modality_support_union)",
            "reference_formula": (
                "risk = max(0, 2*max(cauchy_evidence, "
                "modality_support_union)-1)"
            ),
            "rationale": (
                "Remove only the outer multiplicity-induced flat region; "
                "calibrate the operating threshold on known validation data."
            ),
            "runtime_inputs": [
                "cauchy_evidence",
                "modality_support_union",
                "known_validation_risks",
            ],
            "unknown_or_test_labels_used_at_inference": False,
            "unknown_or_test_labels_allowed_for_thresholds": False,
            "candidate_effects_on_seed7_are_not_an_admission_gate": True,
            "required_confirmation": {
                "fresh_training_seeds": [139, 149, 163],
                "freeze_formula_before_execution": True,
                "paired_against_pairwise_and_opendetect": True,
                "primary_metrics": [
                    "known_macro_f1",
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                    "oscr",
                ],
                "replacement_requires_pre_registered_gate": True,
            },
        },
        "scenario_diagnostics": sorted(
            rows,
            key=lambda row: (
                -row["pairwise_minus_opendetect_fpr95"],
                row["suite"],
                row["scenario"],
            ),
        ),
        "input_evidence": {
            "project_root": str(project_root.resolve()),
            "paths": {
                "full102_summary": str(summary_path.resolve()),
                "coverage_manifest": str(manifest_path.resolve()),
                "raw_fusion": str(raw_path.resolve()),
                "router_manifest": str(router_path.resolve()),
                "incumbent_audit": str(incumbent_audit_path.resolve()),
                "gate_root": str(gate_root.resolve()),
                "mlp_root": str(mlp_root.resolve()),
                "baseline_root": str(baseline_root.resolve()),
            },
            "file_sha256": input_hashes,
        },
        "implementation_sha256": {
            "audit_strict_v4_pairwise_opendetect_fpr95_tail.py": (
                implementation_sha256
            )
        },
        "claim_boundary": {
            "uses_seed7_test_labels_for_diagnosis_only": True,
            "current_scenario_identities_are_development_information": True,
            "does_not_authorize_posthoc_replacement": True,
            "does_not_claim_candidate_improvement": True,
            "does_not_authorize_universal_sota": True,
            "fresh_seed_confirmation_is_mandatory": True,
            "pairwise_remains_frozen_incumbent": True,
        },
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/strict_v4_full103_seed7/summary.json"),
    )
    parser.add_argument(
        "--coverage-manifest",
        type=Path,
        default=Path("results/strict_v4_full103_seed7/coverage_manifest_v2.json"),
    )
    parser.add_argument(
        "--raw-fusion",
        type=Path,
        default=Path("results/strict_v4_full103_seed7/raw_fusion.json"),
    )
    parser.add_argument(
        "--router-manifest",
        type=Path,
        default=Path(
            "results/strict_v4_domain_safe_router_development/candidate_manifest.json"
        ),
    )
    parser.add_argument(
        "--incumbent-audit",
        type=Path,
        default=Path(
            "results/strict_v4_incumbent_vs_classical_main_baselines_v1/audit.json"
        ),
    )
    parser.add_argument(
        "--gate-root",
        type=Path,
        default=Path("runs/strict_v4_full103_pairwise_caeos_seed7"),
    )
    parser.add_argument(
        "--mlp-root",
        type=Path,
        default=Path("runs/strict_v4_full103_mlp_seed7"),
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        default=Path("runs/strict_v4_full103_independent_baselines_seed7"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_pairwise_opendetect_fpr95_tail_audit_v1/audit.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else project_root / path

    implementation = Path(__file__).resolve()
    audit = create_audit(
        project_root=project_root,
        summary_path=resolve(args.summary),
        manifest_path=resolve(args.coverage_manifest),
        raw_path=resolve(args.raw_fusion),
        router_path=resolve(args.router_manifest),
        incumbent_audit_path=resolve(args.incumbent_audit),
        gate_root=resolve(args.gate_root),
        mlp_root=resolve(args.mlp_root),
        baseline_root=resolve(args.baseline_root),
        implementation_sha256=file_hash(implementation),
    )
    output = resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit["overall"], indent=2, sort_keys=True))
    print(f"manifest_sha256={audit['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
