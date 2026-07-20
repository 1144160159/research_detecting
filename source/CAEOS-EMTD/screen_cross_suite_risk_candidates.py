from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from screen_edge_risk_candidates import METRICS, REQUIRED_ARTIFACTS, screen


REFERENCE = "__current_policy__"
DEFAULT_SUITES = {"nf_cse": 14, "ustc_tfc2016": 10}
LEGACY_POLICY = (
    "frozen_suite_conditional_density_v1[suites=edge_iiot;"
    "fallback=nested_hierarchical_joint_gate;weight=0.3;minimum_gain=0.02;"
    "minimum_known_classes=8]"
)
LEGACY_SELECTION = "nested_hierarchical_joint_gate"
LEGACY_RULE = (
    "hierarchical anchor gate with joint uncertainty-distance-conflict-"
    "disagreement fallback on the conflict branch when robust-objective gain "
    "> 0.055000"
)
LEGACY_CODE_HASH = "887dfbb99b64c7049fdad89eb17368d9d39c283b5192a35fc72bf50845da37b6"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze suite-level fixed-risk candidates from one development seed"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--development-seed", type=int, default=7)
    parser.add_argument("--confirmation-seeds", default="83,89,97,101")
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    return parser.parse_args()


def metric_report(payload: object, context: str) -> dict[str, float]:
    if not isinstance(payload, dict):
        raise ValueError(f"missing metric report for {context}")
    missing = [metric for metric in METRICS if metric not in payload]
    if missing:
        raise ValueError(f"metric report for {context} misses {missing}")
    values = {metric: float(payload[metric]) for metric in METRICS}
    if not all(np.isfinite(value) for value in values.values()):
        raise ValueError(f"non-finite metric report for {context}")
    return values


def load_development_blocks(
    root: Path,
    suites: dict[str, int],
    development_seed: int,
) -> tuple[dict[str, dict[str, dict[str, dict[str, float]]]], dict[str, object]]:
    all_blocks: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    source_metrics = []
    risk_policies: set[str] = set()
    method_set: set[str] | None = None
    artifact_checks = 0
    fingerprint_checks = 0
    explicit_no_leakage_guards = 0
    legacy_inferred_no_leakage_guards = 0
    provenance_code_hashes: set[str] = set()

    for suite, expected_scenarios in suites.items():
        blocks: dict[str, dict[str, dict[str, float]]] = {}
        paths = sorted((root / suite).glob(f"*_seed{development_seed}/metrics.json"))
        if len(paths) != expected_scenarios:
            raise ValueError(
                f"scenario coverage mismatch for {suite}: "
                f"expected={expected_scenarios}, actual={len(paths)}"
            )
        for path in paths:
            run_name = path.parent.name
            suffix = f"_seed{development_seed}"
            if not run_name.endswith(suffix):
                raise ValueError(f"unexpected run name: {run_name}")
            scenario = run_name[: -len(suffix)]
            missing_artifacts = [
                name for name in REQUIRED_ARTIFACTS if not (path.parent / name).is_file()
            ]
            if missing_artifacts:
                raise ValueError(
                    f"missing development artifacts for {suite}/{scenario}: "
                    f"{missing_artifacts}"
                )
            artifact_checks += len(REQUIRED_ARTIFACTS)
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8"))
            if int(payload.get("seed", -1)) != development_seed:
                raise ValueError(f"seed mismatch for {suite}/{scenario}")
            provenance = json.loads((path.parent / "provenance.json").read_text("utf-8"))
            code_hash = str(provenance.get("code", {}).get("sha256", ""))
            if not code_hash:
                raise ValueError(f"missing provenance code hash for {suite}/{scenario}")
            provenance_code_hashes.add(code_hash)
            details = payload.get("risk_selection_details", {})
            guard = details.get("unknown_or_test_labels_used_for_selection")
            if guard is False:
                explicit_no_leakage_guards += 1
            elif (
                "unknown_or_test_labels_used_for_selection" not in details
                and payload.get("risk_policy") == LEGACY_POLICY
                and payload.get("risk_selection") == LEGACY_SELECTION
                and details.get("selection_rule") == LEGACY_RULE
                and code_hash == LEGACY_CODE_HASH
            ):
                legacy_inferred_no_leakage_guards += 1
            else:
                raise ValueError(
                    f"runtime selection leakage guard failed for {suite}/{scenario}"
                )
            fingerprint = (
                payload.get("split_metadata", {})
                .get("split_fingerprint", {})
                .get("combined")
            )
            if not fingerprint:
                raise ValueError(f"missing split fingerprint for {suite}/{scenario}")
            fingerprint_checks += 1
            reports = payload.get("reports")
            if not isinstance(reports, dict) or not reports:
                raise ValueError(f"missing fixed-risk reports for {suite}/{scenario}")
            observed_methods = set(reports)
            if method_set is None:
                method_set = observed_methods
            elif observed_methods != method_set:
                raise ValueError(
                    f"fixed-risk method set mismatch for {suite}/{scenario}"
                )
            normalized = {
                method: metric_report(report, f"{suite}/{scenario}/{method}")
                for method, report in reports.items()
            }
            selected_risk = str(payload.get("selected_risk", ""))
            if selected_risk not in normalized:
                raise ValueError(f"selected risk is not reported for {suite}/{scenario}")
            selected = metric_report(
                payload.get("selected_report"), f"{suite}/{scenario}/selected"
            )
            if any(
                not np.isclose(selected[metric], normalized[selected_risk][metric], atol=1e-12)
                for metric in METRICS
            ):
                raise ValueError(f"selected report mismatch for {suite}/{scenario}")
            normalized[REFERENCE] = selected
            blocks[f"{suite}/{scenario}"] = normalized
            risk_policies.add(str(payload.get("risk_policy", "")))
            source_metrics.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
        all_blocks[suite] = blocks

    if method_set is None:
        raise ValueError("no development metrics found")
    combined_hash = hashlib.sha256(
        json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    return all_blocks, {
        "passes": True,
        "development_seed": development_seed,
        "suite_scenario_counts": suites,
        "scenario_count": sum(suites.values()),
        "run_count": sum(suites.values()),
        "fixed_risk_method_count": len(method_set),
        "fixed_risk_methods": sorted(method_set),
        "reference": REFERENCE,
        "risk_policies": sorted(risk_policies),
        "artifact_checks": artifact_checks,
        "split_fingerprint_checks": fingerprint_checks,
        "explicit_no_leakage_guard_count": explicit_no_leakage_guards,
        "legacy_inferred_no_leakage_guard_count": legacy_inferred_no_leakage_guards,
        "legacy_inference_contract": {
            "risk_policy": LEGACY_POLICY,
            "risk_selection": LEGACY_SELECTION,
            "risk_selection_rule": LEGACY_RULE,
            "provenance_code_sha256": LEGACY_CODE_HASH,
        },
        "provenance_code_hashes": sorted(provenance_code_hashes),
        "runtime_selection_uses_unknown_or_test_labels": False,
        "development_candidate_screening_uses_test_unknown_labels": True,
        "source_metrics_combined_sha256": combined_hash,
        "source_metrics": source_metrics,
    }


def canonical_manifest_hash(payload: dict[str, object]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_manifest(
    validation: dict[str, object],
    screenings: dict[str, dict[str, object]],
    confirmation_seeds: set[int],
) -> dict[str, object]:
    if not confirmation_seeds:
        raise ValueError("confirmation seeds must not be empty")
    if int(validation["development_seed"]) in confirmation_seeds:
        raise ValueError("development seed must not appear in confirmation seeds")
    selected = {
        suite: result["selected_candidate"]
        for suite, result in sorted(screenings.items())
    }
    manifest: dict[str, object] = {
        "schema_version": "cross_suite_fixed_risk_candidate_manifest_v1",
        "status": "frozen_unconfirmed",
        "frozen_before_confirmation": True,
        "selected_suite_risks": selected,
        "reference_policy": REFERENCE,
        "selection_rules": {
            suite: result["selection_rule"]
            for suite, result in sorted(screenings.items())
        },
        "development_seed": validation["development_seed"],
        "development_scenario_count": validation["scenario_count"],
        "confirmation_seeds": sorted(confirmation_seeds),
        "development_source_metrics_combined_sha256": validation[
            "source_metrics_combined_sha256"
        ],
        "development_candidate_screening_uses_test_unknown_labels": True,
        "runtime_policy_uses_unknown_or_test_labels": False,
        "runtime_policy": (
            "fixed risk selected by known suite identity; no per-task validation, "
            "unknown label or test label routing"
        ),
        "confirmation_gate": {
            "unit": "scenario mean across confirmation seeds",
            "combined_suites": ["nf_cse", "ustc_tfc2016"],
            "unknown_auroc_mean_improvement_required": True,
            "unknown_auroc_scenario_bootstrap_ci_lower_gt_zero": True,
            "unknown_aupr_nonregression_tolerance": 0.01,
            "unknown_fpr95_oriented_nonregression_tolerance": 0.01,
            "oscr_nonregression_tolerance": 0.01,
            "each_suite_all_four_oriented_means_positive": True,
            "fallback": "retain current confirmed suite policy",
        },
    }
    manifest["manifest_sha256"] = canonical_manifest_hash(manifest)
    return manifest


def markdown_report(
    validation: dict[str, object],
    screenings: dict[str, dict[str, object]],
    manifest: dict[str, object],
) -> str:
    lines = [
        "# NF-CSE / USTC 固定风险开发筛查",
        "",
        f"- 开发种子：`{validation['development_seed']}`。",
        f"- 场景块：`{validation['scenario_count']}`。",
        f"- 固定风险：`{validation['fixed_risk_method_count']}`。",
        "- 状态：`frozen_unconfirmed`，开发筛查使用未知测试标签，只能生成候选。",
        f"- manifest SHA-256：`{manifest['manifest_sha256']}`。",
        "",
    ]
    for suite, result in screenings.items():
        selected = str(result["selected_candidate"])
        row = next(item for item in result["method_table"] if item["method"] == selected)
        delta = row["versus_final"]
        lines.extend(
            [
                f"## {suite}",
                "",
                f"选择 `{selected}`；LOSO 路径为 `{result['loso']['selected_paths']}`。",
                "",
                "| AUROC | AUPR | FPR95 有向 | OSCR |",
                "|---:|---:|---:|---:|",
                (
                    f"| {delta['unknown_auroc']:+.6f} | "
                    f"{delta['unknown_aupr']:+.6f} | "
                    f"{delta['unknown_fpr95']:+.6f} | "
                    f"{delta['oscr']:+.6f} |"
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## 确认边界",
            "",
            "候选只允许在全新种子 `83/89/97/101` 上确认。运行时仅按已知数据集标识使用固定风险，不允许用未知类或测试标签切换。若组合 AUROC 的场景块 bootstrap 下界不大于 0、任一安全指标回退超过 0.01，或任一数据集四项有向均值不全为正，则保留当前确认策略。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_arguments()
    seeds = {int(value) for value in args.confirmation_seeds.split(",") if value.strip()}
    blocks, validation = load_development_blocks(
        Path(args.root), DEFAULT_SUITES, args.development_seed
    )
    screenings = {
        suite: screen(suite_blocks, REFERENCE, args.nonregression_tolerance)
        for suite, suite_blocks in blocks.items()
    }
    manifest = build_manifest(validation, screenings, seeds)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "screening.json").write_text(
        json.dumps(
            {"validation": validation, "screenings": screenings},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = markdown_report(validation, screenings, manifest)
    (output / "screening.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
