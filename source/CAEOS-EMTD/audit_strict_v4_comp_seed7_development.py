from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from analyze_caeos_closr_fusion import empirical_percentile
from caeos.continuous_outer_min_p import reconstruct_candidate_risks
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from evaluate_strict_v4_comp_confirmation import aggregate, report_values


DIAGNOSIS_FILE_SHA256 = (
    "1bfed984c44a9e95cb2e2f2b0a3d75dab779c2fcff2e94f6da7355a56c3a2da8"
)
PROTOCOL_FILE_SHA256 = (
    "00411a25500270d9773d4a63750628bb5c98e23e48c9885aded49e42f8d47720"
)
RAW_FUSION_FILE_SHA256 = (
    "a13d365aa6109548c41874679bc66825433b7b400615d3dbec6cd51d1fd296a7"
)
SUMMARY_FILE_SHA256 = (
    "fb2ed5a99d57ffde364db3791e90cfbae7b93f0ececcd9a93ea89210882aab6b"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_hash(path: Path, expected: str, label: str) -> None:
    observed = file_hash(path)
    if observed != expected:
        raise ValueError(f"{label} file SHA drifted: {observed}")


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def create_audit(
    *,
    diagnosis_path: Path,
    protocol_path: Path,
    raw_path: Path,
    summary_path: Path,
    gate_root: Path,
    baseline_root: Path,
    implementation_sha256: str,
) -> dict[str, Any]:
    require_hash(diagnosis_path, DIAGNOSIS_FILE_SHA256, "diagnosis")
    require_hash(protocol_path, PROTOCOL_FILE_SHA256, "confirmation protocol")
    require_hash(raw_path, RAW_FUSION_FILE_SHA256, "raw fusion")
    require_hash(summary_path, SUMMARY_FILE_SHA256, "full102 summary")
    diagnosis = load(diagnosis_path)
    protocol = load(protocol_path)
    raw = load(raw_path)
    summary = load(summary_path)
    if (
        diagnosis.get("manifest_sha256") != canonical_hash(diagnosis)
        or diagnosis.get("passes") is not True
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("candidate", {}).get("method") != "caeos_comp"
        or summary.get("validation", {}).get("scenario_count") != 102
    ):
        raise ValueError("canonical frozen development inputs required")

    rows = []
    artifact_hashes = {}
    for run in raw.get("runs", []):
        suite = str(run["suite"])
        scenario, seed_text = str(run["task"]).rsplit("_seed", 1)
        if int(seed_text) != 7:
            raise ValueError("seed7 development runs required")
        gate_dir = gate_root / suite / f"{scenario}_seed7"
        baseline_dir = baseline_root / suite / f"{scenario}_seed7_opendetect"
        paths = {
            "pairwise_metrics": gate_dir / "metrics.json",
            "pairwise_scores": gate_dir / "scores.npz",
            "pairwise_evidence": gate_dir / "evidence_package.npz",
            "opendetect_metrics": baseline_dir / "metrics.json",
        }
        if any(not path.is_file() for path in paths.values()):
            raise ValueError(f"development artifact is absent: {suite}/{scenario}")
        pairwise_metrics = load(paths["pairwise_metrics"])
        opendetect_metrics = load(paths["opendetect_metrics"])
        if (
            pairwise_metrics.get("risk_selection_details", {}).get(
                "unknown_or_test_labels_used_for_selection"
            )
            is not False
            or run.get("gate_selected_risk")
            != pairwise_metrics.get("selected_risk")
        ):
            raise ValueError(f"Pairwise selection boundary drifted: {suite}/{scenario}")
        with np.load(paths["pairwise_scores"], allow_pickle=False) as scores, np.load(
            paths["pairwise_evidence"], allow_pickle=False
        ) as evidence:
            risks = reconstruct_candidate_risks(scores, evidence)
            reference_validation = empirical_percentile(
                risks["validation_reference"], risks["validation_reference"]
            )
            reference_test = empirical_percentile(
                risks["validation_reference"], risks["test_reference"]
            )
            candidate_validation = empirical_percentile(
                risks["validation_candidate"], risks["validation_candidate"]
            )
            candidate_test = empirical_percentile(
                risks["validation_candidate"], risks["test_candidate"]
            )
            pairwise_report = evaluate_hybrid_open_set(
                scores["test_labels"],
                scores["test_unknown"].astype(bool),
                scores["test_prediction"],
                reference_test,
                float(np.quantile(reference_validation, 0.95)),
            )
            candidate_report = evaluate_hybrid_open_set(
                scores["test_labels"],
                scores["test_unknown"].astype(bool),
                scores["test_prediction"],
                candidate_test,
                float(np.quantile(candidate_validation, 0.95)),
            )
        for metric in (
            "known_macro_f1",
            "unknown_auroc",
            "unknown_aupr",
            "unknown_fpr95",
            "oscr",
        ):
            if not close(pairwise_report[metric], run["gate_report"][metric]):
                raise ValueError(
                    f"Pairwise report does not reconcile: {suite}/{scenario}/{metric}"
                )
        opendetect_report = opendetect_metrics.get("reports", {}).get("opendetect")
        if not isinstance(opendetect_report, dict):
            raise ValueError("OpenDetect report is absent")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": 7,
                "route": risks["route"],
                "changed": bool(risks["changed"]),
                "pairwise": report_values(pairwise_report),
                "caeos_comp": report_values(candidate_report),
                "opendetect": report_values(opendetect_report),
            }
        )
        artifact_hashes.update(
            {
                f"{suite}/{scenario}/{name}": file_hash(path)
                for name, path in paths.items()
            }
        )
    if len(rows) != 102:
        raise ValueError("exactly 102 seed7 development rows required")

    vs_pairwise = aggregate(rows, "caeos_comp", "pairwise")
    vs_opendetect = aggregate(rows, "caeos_comp", "opendetect")
    by_suite: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_suite[row["suite"]].append(row)
    suite_summary = {}
    for suite, suite_rows in sorted(by_suite.items()):
        comparison = aggregate(suite_rows, "caeos_comp", "pairwise")
        suite_summary[suite] = {
            "scenario_count": len(suite_rows),
            "changed_count": sum(row["changed"] for row in suite_rows),
            "unknown_fpr95": comparison["metrics"]["unknown_fpr95"],
        }
    fpr = vs_pairwise["metrics"]["unknown_fpr95"]
    known_f1 = vs_pairwise["metrics"]["known_macro_f1"]
    audit: dict[str, Any] = {
        "schema_version": "strict_v4_comp_seed7_development_audit_v1",
        "state": "post_freeze_seed7_development_effect_complete",
        "passes": True,
        "validation": {
            "scenario_count": len(rows),
            "suite_count": len(by_suite),
            "changed_count": sum(row["changed"] for row in rows),
            "route_distribution": dict(Counter(row["route"] for row in rows)),
            "artifact_hash_count": len(artifact_hashes),
            "pairwise_reports_recomputed_and_reconciled": True,
            "known_macro_f1_invariant": close(
                known_f1["oriented_mean_delta"], 0.0
            ),
        },
        "candidate_vs_pairwise": vs_pairwise,
        "candidate_vs_opendetect": vs_opendetect,
        "by_suite": suite_summary,
        "development_observation": {
            "unknown_fpr95_win_count": fpr["win_count"],
            "unknown_fpr95_tie_count": fpr["tie_count"],
            "unknown_fpr95_loss_count": fpr["loss_count"],
            "unknown_fpr95_oriented_mean_improvement": fpr[
                "oriented_mean_delta"
            ],
            "all_five_overall_metrics_nonregress": all(
                evidence["oriented_mean_delta"] >= -1e-12
                for evidence in vs_pairwise["metrics"].values()
            ),
        },
        "tasks": rows,
        "input_evidence": {
            "diagnosis_file_sha256": DIAGNOSIS_FILE_SHA256,
            "protocol_file_sha256": PROTOCOL_FILE_SHA256,
            "raw_fusion_file_sha256": RAW_FUSION_FILE_SHA256,
            "summary_file_sha256": SUMMARY_FILE_SHA256,
            "artifact_sha256": dict(sorted(artifact_hashes.items())),
        },
        "implementation_sha256": {
            "audit_strict_v4_comp_seed7_development.py": implementation_sha256
        },
        "claim_boundary": {
            "uses_seed7_test_labels_for_development_metrics": True,
            "candidate_formula_was_frozen_in_diagnosis_before_effect_audit": True,
            "does_not_admit_candidate": True,
            "does_not_replace_pairwise": True,
            "does_not_authorize_universal_sota": True,
            "fresh_seed_protocol_is_the_only_pilot_admission_gate": True,
        },
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    return audit


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
        "--protocol",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/protocol.json"),
    )
    parser.add_argument(
        "--raw-fusion",
        type=Path,
        default=Path("results/strict_v4_full103_seed7/raw_fusion.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/strict_v4_full103_seed7/summary.json"),
    )
    parser.add_argument(
        "--gate-root",
        type=Path,
        default=Path("runs/strict_v4_full103_pairwise_caeos_seed7"),
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
            "results/strict_v4_comp_seed7_development_audit_v1/audit.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    audit = create_audit(
        diagnosis_path=resolve(args.diagnosis),
        protocol_path=resolve(args.protocol),
        raw_path=resolve(args.raw_fusion),
        summary_path=resolve(args.summary),
        gate_root=resolve(args.gate_root),
        baseline_root=resolve(args.baseline_root),
        implementation_sha256=file_hash(Path(__file__).resolve()),
    )
    output = resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit["development_observation"], indent=2, sort_keys=True))
    print(f"manifest_sha256={audit['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
