from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from summarize_strict_v4_pilot import METRICS, report_metrics
from summarize_strict_v4_posthoc_ood import merged_tables
from run_strict_v4_excel_full102 import output_for


def validate_and_load(protocol: dict[str, Any], result_root: Path) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    mlp_root = Path(protocol["mlp_root"])
    blocks = {}
    for key, source in sorted(protocol["sources"].items()):
        output = output_for(result_root, key)
        paths = {name: output / name for name in ("metrics.json", "scores.npz", "provenance.json")}
        if any(not path.is_file() for path in paths.values()):
            raise ValueError(f"missing ExCeL full102 output for {key}")
        metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
        provenance = json.loads(paths["provenance.json"].read_text(encoding="utf-8"))
        mlp_run = mlp_root / source["mlp_relative_path"]
        current = {name: file_hash(mlp_run / name) for name in ("metrics.json", "scores.npz", "model.pt")}
        if current != source["mlp_artifact_sha256"] or provenance.get("source_artifact_sha256") != current:
            raise ValueError(f"frozen ExCeL source SHA mismatch: {key}")
        if set(metrics.get("reports", {})) != {"excel"}:
            raise ValueError(f"ExCeL report mismatch: {key}")
        selection = metrics.get("selection_evidence", {})
        if selection.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            raise ValueError(f"ExCeL leakage guard failed: {key}")
        source_metrics = json.loads((mlp_run / "metrics.json").read_text(encoding="utf-8"))
        fingerprints = {
            metrics["split_metadata"]["split_fingerprint"]["combined"],
            source_metrics["split_metadata"]["split_fingerprint"]["combined"],
            source["split_fingerprint"],
        }
        if len(fingerprints) != 1:
            raise ValueError(f"ExCeL split mismatch: {key}")
        blocks[key] = {"excel": report_metrics(metrics["reports"]["excel"], f"{key}/excel")}
    if len(blocks) != 102:
        raise ValueError(f"ExCeL scenario coverage mismatch: {len(blocks)}/102")
    return blocks, {
        "passes": True, "scenario_count": len(blocks), "artifact_checks": len(blocks) * 6,
        "split_fingerprint_checks": len(blocks), "failure_count": 0,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }


def merge_and_decide(existing: dict[str, Any], blocks: dict[str, dict[str, dict[str, float]]]):
    overall, by_suite = merged_tables(existing, blocks)
    candidates = [row for row in overall if not row["method"].startswith("caeos_")]
    selected = min(candidates, key=lambda row: (float(row["mean_unknown_metric_rank"]), -float(row["unknown_auroc"]), row["method"]))
    decision = {
        "selection_rule": "minimum four-unknown-metric mean rank, then higher AUROC",
        "selected_comparator": selected["method"],
        "selected_metrics": {metric: selected[metric] for metric in METRICS},
        "selected_mean_unknown_metric_rank": selected["mean_unknown_metric_rank"],
        "existing_opendetect_protocol_remains_valid": selected["method"] == "opendetect",
        "next_action": "retain_frozen_opendetect_confirmation" if selected["method"] == "opendetect" else "freeze_new_external_comparator_confirmation",
    }
    return overall, by_suite, decision


def render(report: dict[str, Any]) -> str:
    row = next(item for item in report["overall"] if item["method"] == "excel")
    decision = report["comparator_decision"]
    return (
        "# Strict-v4 ExCeL full102\n\n"
        f"完整性：**PASS**；场景 `{report['validation']['scenario_count']}/102`；合并后方法 `{report['method_count']}`。\n\n"
        f"ExCeL：Known F1 `{row['known_macro_f1']:.6f}`，AUROC `{row['unknown_auroc']:.6f}`，"
        f"AUPR `{row['unknown_aupr']:.6f}`，FPR95 `{row['unknown_fpr95']:.6f}`，"
        f"OSCR `{row['oscr']:.6f}`，四指标平均秩 `{row['mean_unknown_metric_rank']:.3f}`。\n\n"
        f"冻结外部比较器：`{decision['selected_comparator']}`；OpenDetect 协议继续有效："
        f"`{str(decision['existing_opendetect_protocol_remains_valid']).lower()}`。\n\n"
        "该表仍是 seed7 发展屏幕，不能单独支撑确认性 SOTA 声明。\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--existing-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("ExCeL protocol SHA mismatch")
    marker = args.result_root / "full102_complete"
    if not marker.is_file() or marker.read_text(encoding="ascii").strip() != protocol["manifest_sha256"]:
        raise ValueError("ExCeL completion marker is absent or stale")
    existing = json.loads(args.existing_summary.read_text(encoding="utf-8"))
    if existing.get("method_count") != 29:
        raise ValueError("ExCeL must merge into the frozen 29-method summary")
    blocks, validation = validate_and_load(protocol, args.result_root)
    overall, by_suite, decision = merge_and_decide(existing, blocks)
    report = {
        "schema_version": "strict_v4_excel_30method_screen_v1", "status": "complete",
        "method_count": len(overall), "added_methods": ["excel"], "overall": overall,
        "by_suite": by_suite, "validation": validation, "comparator_decision": decision,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "existing_29method_summary_sha256": file_hash(args.existing_summary),
        "analysis_implementation_sha256": file_hash(Path(__file__).resolve()),
    }
    if report["method_count"] != 30:
        raise ValueError(f"ExCeL merged method count mismatch: {report['method_count']}/30")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "summary.md").write_text(render(report), encoding="utf-8")
    (args.output_dir / "comparator_decision_complete").write_text(decision["selected_comparator"] + "\n", encoding="ascii")
    print(json.dumps(decision, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
