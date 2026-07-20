from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_strict_v4_pilot import METRICS, aggregate_table, report_metrics


METHODS = ("react_energy", "dice", "she")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge strict-v4 ReAct/DICE/SHE into the 22-method seed7 screen"
    )
    parser.add_argument("--posthoc-root", type=Path, required=True)
    parser.add_argument("--existing-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def table_from_means(means: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    return aggregate_table({"means": means})


def validate_and_load(
    root: Path, protocol: dict[str, Any]
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    source_root = Path(protocol["source_root"])
    source_entries = protocol["source_artifact_sha256"]
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    artifact_checks = 0
    split_checks = 0
    for relative_text, expected_hashes in sorted(source_entries.items()):
        relative = Path(relative_text)
        source = source_root / relative
        output = root / relative.parent / relative.name.removesuffix("_mlp")
        required = ("metrics.json", "scores.npz", "provenance.json")
        missing = [name for name in required if not (output / name).is_file()]
        if missing:
            raise ValueError(f"missing post-hoc artifacts under {output}: {missing}")
        artifact_checks += len(required)
        metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
        provenance = json.loads(
            (output / "provenance.json").read_text(encoding="utf-8")
        )
        source_metrics = json.loads(
            (source / "metrics.json").read_text(encoding="utf-8")
        )
        if provenance.get("source_artifact_sha256") != expected_hashes:
            raise ValueError(f"source SHA binding mismatch for {relative}")
        current_hashes = {
            name: sha256_file(source / name)
            for name in ("metrics.json", "scores.npz", "model.pt")
        }
        if current_hashes != expected_hashes:
            raise ValueError(f"frozen MLP source changed after protocol freeze: {relative}")
        if set(metrics.get("reports", {})) != set(METHODS):
            raise ValueError(f"post-hoc report set mismatch for {relative}")
        selection = metrics.get("selection_evidence", {})
        if selection.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            raise ValueError(f"post-hoc leakage guard failed for {relative}")
        postprocessors = selection.get("postprocessors", {})
        if any(
            postprocessors.get(method, {}).get("unknown_or_test_labels_used") is not False
            for method in METHODS
        ):
            raise ValueError(f"post-hoc method leakage guard failed for {relative}")
        source_fingerprint = source_metrics["split_metadata"]["split_fingerprint"]["combined"]
        output_fingerprint = metrics["split_metadata"]["split_fingerprint"]["combined"]
        if source_fingerprint != output_fingerprint:
            raise ValueError(f"post-hoc split fingerprint mismatch for {relative}")
        split_checks += 1
        suite = relative.parent.as_posix()
        scenario = relative.name.removesuffix("_seed7_mlp")
        key = f"{suite}/{scenario}"
        blocks[key] = {
            method: report_metrics(metrics["reports"][method], f"{key}/{method}")
            for method in METHODS
        }
    expected = int(protocol["expected_runs"])
    if len(blocks) != expected:
        raise ValueError(f"post-hoc scenario coverage mismatch: {len(blocks)}/{expected}")
    return blocks, {
        "passes": True,
        "scenario_count": len(blocks),
        "method_count": len(METHODS),
        "report_count": len(blocks) * len(METHODS),
        "artifact_checks": artifact_checks,
        "split_fingerprint_pair_checks": split_checks,
        "split_fingerprints_identical": True,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }


def merged_tables(
    existing: dict[str, Any], posthoc_blocks: dict[str, dict[str, dict[str, float]]]
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    posthoc_overall = aggregate_table(posthoc_blocks)
    existing_means = {
        row["method"]: {metric: float(row[metric]) for metric in METRICS}
        for row in existing["overall"]
    }
    posthoc_means = {
        row["method"]: {metric: float(row[metric]) for metric in METRICS}
        for row in posthoc_overall
    }
    overlap = set(existing_means) & set(posthoc_means)
    if overlap:
        raise ValueError(f"post-hoc method names collide with existing table: {sorted(overlap)}")
    overall = table_from_means(existing_means | posthoc_means)

    by_suite: dict[str, list[dict[str, Any]]] = {}
    for suite, existing_table in existing["by_suite"].items():
        suite_blocks = {
            key: methods
            for key, methods in posthoc_blocks.items()
            if key.startswith(f"{suite}/")
        }
        if not suite_blocks:
            raise ValueError(f"post-hoc results do not cover suite {suite}")
        suite_posthoc = aggregate_table(suite_blocks)
        means = {
            row["method"]: {metric: float(row[metric]) for metric in METRICS}
            for row in existing_table
        }
        means.update(
            {
                row["method"]: {metric: float(row[metric]) for metric in METRICS}
                for row in suite_posthoc
            }
        )
        by_suite[suite] = table_from_means(means)
    return overall, by_suite


def render(report: dict[str, Any]) -> str:
    decision = report["comparator_decision"]
    lines = [
        "# Strict-v4 现代后处理基线扩展",
        "",
        f"完整性审计：**PASS**；场景 {report['validation']['scenario_count']}；"
        f"新增报告 {report['validation']['report_count']}；合并后方法 {report['method_count']}。",
        "ReAct、DICE、SHE 均复用冻结 MLP 检查点，仅用 known-train 拟合，"
        "known-validation 校准阈值，未知/测试标签只用于最终指标。",
        "",
        "| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(report["overall"], 1):
        lines.append(
            f"| {rank} | {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## 外部比较器冻结判定",
            "",
            f"- 最强非 CAEOS 方法：`{decision['selected_comparator']}`。",
            f"- 旧 OpenDetect 协议仍有效：`{str(decision['existing_opendetect_protocol_remains_valid']).lower()}`。",
            f"- 下一步：`{decision['next_action']}`。",
            "- 本表仍是 seed7 发展屏幕，不能单独支撑确认性 SOTA 声明。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_arguments()
    root = args.posthoc_root.resolve()
    protocol_path = root / "protocol_manifest.json"
    completion_path = root / "posthoc_ood_complete"
    if not protocol_path.is_file() or not completion_path.is_file():
        raise ValueError("post-hoc OOD matrix is not complete")
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if completion_path.read_text(encoding="ascii").strip() != protocol["manifest_sha256"]:
        raise ValueError("post-hoc completion marker does not bind the protocol")
    existing = json.loads(args.existing_summary.read_text(encoding="utf-8"))
    blocks, validation = validate_and_load(root, protocol)
    overall, by_suite = merged_tables(existing, blocks)
    non_caeos = [row for row in overall if not row["method"].startswith("caeos_")]
    selected = min(
        non_caeos,
        key=lambda row: (
            row["mean_unknown_metric_rank"],
            -row["unknown_auroc"],
            row["method"],
        ),
    )
    remains_valid = selected["method"] == "opendetect"
    decision = {
        "selection_rule": "minimum four-unknown-metric mean rank, then higher AUROC",
        "selected_comparator": selected["method"],
        "selected_metrics": {metric: selected[metric] for metric in METRICS},
        "selected_mean_unknown_metric_rank": selected["mean_unknown_metric_rank"],
        "existing_opendetect_protocol_remains_valid": remains_valid,
        "next_action": (
            "run_frozen_opendetect_external_confirmation"
            if remains_valid
            else "invalidate_opendetect_only_protocol_and_freeze_new_comparator_confirmation"
        ),
    }
    report = {
        "schema_version": "strict_v4_posthoc_ood_25method_screen_v1",
        "status": "complete",
        "method_count": len(overall),
        "added_methods": list(METHODS),
        "overall": overall,
        "by_suite": by_suite,
        "validation": validation,
        "comparator_decision": decision,
        "posthoc_protocol_manifest_sha256": protocol["manifest_sha256"],
        "existing_summary_sha256": sha256_file(args.existing_summary),
        "analysis_implementation_sha256": sha256_file(Path(__file__).resolve()),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(render(report), encoding="utf-8")
    (args.output_dir / "comparator_decision_complete").write_text(
        selected["method"] + "\n", encoding="ascii"
    )
    print(json.dumps(decision, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
