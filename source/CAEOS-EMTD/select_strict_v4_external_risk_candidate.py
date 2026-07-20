from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
DEVELOPMENT_SCENARIOS = {
    "cic_ton_iot": ("xss", "scanning", "ransomware"),
    "cic_iot2023": ("ddos_icmp_flood", "mirai_udpplain", "command_injection"),
}
CONFIRMATION_SCENARIOS = {
    "cic_ton_iot": ("injection", "password", "mitm"),
    "cic_iot2023": (
        "ddos_ack_fragmentation",
        "dictionary_bruteforce",
        "recon_ping_sweep",
    ),
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    value = {key: item for key, item in payload.items() if key != "manifest_sha256"}
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def parse_task(task: str) -> tuple[str, int]:
    if "_seed" not in task:
        raise ValueError(f"task has no seed suffix: {task!r}")
    scenario, seed = task.rsplit("_seed", 1)
    return scenario, int(seed)


def candidate_score(payload: dict[str, Any], method: str) -> tuple[float, float, float]:
    suite_gains = [
        payload["by_suite"][suite]["methods"][method]["metrics"][metric][
            "oriented_mean_delta"
        ]
        for suite in sorted(DEVELOPMENT_SCENARIOS)
        for metric in UNKNOWN_METRICS
    ]
    overall = payload["overall"]["methods"][method]
    total_gain = sum(
        overall["metrics"][metric]["oriented_mean_delta"]
        for metric in UNKNOWN_METRICS
    )
    return min(suite_gains), overall["mean_delta_vs_gate"], total_gain


def validate_analysis(path: Path, payload: dict[str, Any]) -> str:
    if payload.get("calibration") != (
        "each expert empirical CDF fitted on known validation only"
    ):
        raise ValueError(f"unexpected calibration declaration in {path}")
    if payload.get("selection_scope", {}).get("seeds") != [7]:
        raise ValueError(f"development seed is not frozen to 7 in {path}")
    expert = payload["overall"].get("expert_name")
    if expert != path.stem:
        raise ValueError(f"expert/file mismatch in {path}: {expert!r}")
    observed: set[tuple[str, str, int]] = set()
    for run in payload["runs"]:
        scenario, seed = parse_task(run["task"])
        observed.add((run["suite"], scenario, seed))
        audit = run.get("audit", {})
        if not (
            audit.get("split_fingerprints_identical") is True
            and audit.get("caeos_unknown_or_test_labels_used_for_selection") is False
            and audit.get(
                "expert_unknown_or_test_labels_used_for_fitting_or_selection"
            )
            is False
            and audit.get("fusion_calibration_split") == "known_only_validation"
            and audit.get("test_labels_used_for_final_metrics_only") is True
        ):
            raise ValueError(f"leakage/split audit failed in {path}")
    expected = {
        (suite, scenario, 7)
        for suite, scenarios in DEVELOPMENT_SCENARIOS.items()
        for scenario in scenarios
    }
    if observed != expected:
        raise ValueError(f"development coverage mismatch in {path}")
    return expert


def select_candidate(analyses: list[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    records = []
    for path, payload in analyses:
        expert = validate_analysis(path, payload)
        for method, report in payload["overall"]["methods"].items():
            score = candidate_score(payload, method)
            known_gain = report["metrics"]["known_macro_f1"][
                "oriented_mean_delta"
            ]
            if score[0] >= 0.0 and abs(known_gain) <= 1e-12:
                records.append(
                    {
                        "expert_risk": expert,
                        "fusion": method,
                        "score": score,
                        "overall": report,
                        "by_suite": {
                            suite: payload["by_suite"][suite]["methods"][method]
                            for suite in sorted(DEVELOPMENT_SCENARIOS)
                        },
                        "source": path,
                    }
                )
    if not records:
        raise ValueError("no candidate passes the cross-suite non-regression gate")
    return max(
        records,
        key=lambda item: (
            item["score"],
            item["expert_risk"],
            item["fusion"],
        ),
    )


def render(manifest: dict[str, Any]) -> str:
    candidate = manifest["candidate"]
    gains = candidate["development_evidence"]["overall_oriented_gains"]
    lines = [
        "# Strict-v4 external-risk candidate freeze",
        "",
        f"Status: **{manifest['status']}**.",
        f"Candidate: `{candidate['expert_model']}/{candidate['expert_risk']}` + "
        f"`{candidate['fusion']}`.",
        f"Manifest SHA256: `{manifest['manifest_sha256']}`.",
        "",
        "| Metric | Development oriented gain |",
        "|---|---:|",
    ]
    for metric in UNKNOWN_METRICS:
        lines.append(f"| {metric} | {gains[metric]:+.6f} |")
    lines.extend(
        [
            "",
            f"Minimum suite-metric gain: "
            f"`{candidate['development_evidence']['minimum_suite_metric_gain']:+.6f}`.",
            "Confirmation is frozen to six development-disjoint scenarios and seeds "
            "`127,131`; confirmation outcomes may not change this candidate.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--base-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    sources = []
    for path in sorted(args.analysis_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if "overall" in payload and "runs" in payload:
            sources.append((path, payload))
    if len(sources) != 12:
        raise ValueError(f"expected 12 expert analyses, found {len(sources)}")
    selected = select_candidate(sources)
    if (selected["expert_risk"], selected["fusion"]) != ("openmax", "rank_union"):
        raise ValueError("frozen deterministic selector did not choose openmax/rank_union")

    base_manifest = json.loads(args.base_manifest.read_text(encoding="utf-8"))
    base_sha = base_manifest.get("manifest_sha256")
    if not isinstance(base_sha, str):
        raise ValueError("base candidate manifest has no canonical SHA")
    project_root = args.project_root.resolve()
    implementation = project_root / "analyze_caeos_closr_fusion.py"
    report = selected["overall"]
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_external_risk_candidate_v1",
        "status": "frozen_unconfirmed",
        "selection_rule": {
            "candidate_count": 72,
            "eligibility": (
                "all 8 suite-by-metric oriented gains nonnegative and known F1 unchanged"
            ),
            "lexicographic_objective": [
                "maximize minimum suite-by-metric oriented gain",
                "maximize overall AUROC oriented gain",
                "maximize sum of four overall unknown-metric oriented gains",
            ],
            "selection_data": "development scenarios at seed 7 only",
        },
        "candidate": {
            "base_algorithm": "nested_boundary_pairwise_pseudo_unknown_blend",
            "base_manifest_sha256": base_sha,
            "base_manifest_file_sha256": file_hash(args.base_manifest),
            "expert_model": "mlp",
            "expert_risk": selected["expert_risk"],
            "fusion": selected["fusion"],
            "fusion_formula": "1 - (1 - caeos_cdf) * (1 - expert_cdf)",
            "calibration": "known-validation empirical CDF per risk",
            "known_class_prediction_source": "CAEOS",
            "implementation_sha256": {
                "analyze_caeos_closr_fusion.py": file_hash(implementation)
            },
            "development_evidence": {
                "seed": 7,
                "scenarios": DEVELOPMENT_SCENARIOS,
                "minimum_suite_metric_gain": selected["score"][0],
                "overall_oriented_gains": {
                    metric: report["metrics"][metric]["oriented_mean_delta"]
                    for metric in UNKNOWN_METRICS
                },
                "by_suite": selected["by_suite"],
                "source_sha256": {
                    path.name: file_hash(path) for path, _ in sources
                },
            },
        },
        "confirmation": {
            "seeds": [127, 131],
            "scenarios": CONFIRMATION_SCENARIOS,
            "expected_scenario_count": 6,
            "expected_run_count": 12,
            "scenario_disjoint_from_external_fusion_development": True,
            "seed_disjoint": True,
            "single_shot_no_retuning": True,
            "decision_gate": {
                "all_combined_unknown_metrics_positive": True,
                "combined_auroc_bootstrap_lower_gt_zero": True,
                "all_suite_unknown_metrics_nonnegative": True,
                "known_macro_f1_unchanged": True,
            },
        },
        "leakage_guards": {
            "base_risk_selection_uses_unknown_or_test_labels": False,
            "expert_fitting_or_selection_uses_unknown_or_test_labels": False,
            "fusion_calibration_uses_unknown_or_test_labels": False,
            "test_labels_used_for_final_metrics_only": True,
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "candidate_manifest.md").write_text(
        render(manifest), encoding="utf-8"
    )
    print(render(manifest))


if __name__ == "__main__":
    main()
