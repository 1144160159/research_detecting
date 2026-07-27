from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rerank(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for metric in METRICS:
        values = np.asarray([float(record[metric]) for record in records])
        ranks = rankdata(values if metric == "unknown_fpr95" else -values, method="average")
        for record, rank in zip(records, ranks):
            record.setdefault("metric_ranks", {})[metric] = float(rank)
    for record in records:
        record["mean_unknown_metric_rank"] = float(
            np.mean([record["metric_ranks"][metric] for metric in METRICS])
        )
    return sorted(records, key=lambda record: (record["mean_unknown_metric_rank"], -record["unknown_auroc"], record["method"]))


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "method": "npos_knn",
        **{
            metric: float(np.mean([row[metric] for row in rows]))
            for metric in ("known_macro_f1", *METRICS)
        },
    }


def render(summary: dict[str, Any]) -> str:
    npos = next(item for item in summary["overall"] if item["method"] == "npos_knn")
    decision = summary["comparator_decision"]
    return (
        "# Strict-v4 NPOS full102\n\n"
        f"NPOS mean unknown rank: **{npos['mean_unknown_metric_rank']:.2f}**.\n\n"
        f"Selected external comparator: **{decision['selected_comparator']}**.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--existing-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_json(args.protocol)
    existing = load_json(args.existing_summary)
    if (
        protocol.get("schema_version") != "strict_v4_npos_full102_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or existing.get("schema_version") != "strict_v4_excel_30method_screen_v1"
        or existing.get("status") != "complete"
        or protocol["implementation_sha256"]["summarize_strict_v4_npos_full102.py"]
        != file_hash(Path(__file__))
    ):
        raise ValueError("NPOS full102 summary input validation failed")
    if not (args.run_root / "execution_complete").is_file():
        raise ValueError("NPOS full102 execution is incomplete")
    by_suite_rows: dict[str, list[dict[str, Any]]] = {}
    all_rows = []
    artifact_checks = 0
    for source in protocol["source_registry"]:
        directory = args.run_root / source["suite"] / f"{source['scenario']}_seed7_npos"
        metrics = load_json(directory / "metrics.json")
        if (
            metrics.get("schema_version") != "strict_v4_npos_metrics_v1"
            or metrics["split_metadata"]["split_fingerprint"]["combined"] != source["split_fingerprint"]
            or metrics.get("selection_evidence", {}).get(
                "unknown_or_test_labels_used_for_fitting_or_selection"
            ) is not False
        ):
            raise ValueError(f"NPOS full102 result validation failed: {directory}")
        for name in ("metrics.json", "scores.npz", "model.pt", "provenance.json"):
            if not (directory / name).is_file():
                raise FileNotFoundError(directory / name)
            artifact_checks += 1
        row = metrics["reports"]["npos_knn"]
        all_rows.append(row)
        by_suite_rows.setdefault(source["suite"], []).append(row)
    if len(all_rows) != 102:
        raise ValueError("NPOS full102 scenario count mismatch")
    overall = copy.deepcopy(existing["overall"])
    overall.append(aggregate(all_rows))
    overall = rerank(overall)
    by_suite = copy.deepcopy(existing["by_suite"])
    for suite, rows in by_suite_rows.items():
        by_suite[suite].append(aggregate(rows))
        by_suite[suite] = rerank(by_suite[suite])
    npos = next(item for item in overall if item["method"] == "npos_knn")
    opendetect = next(item for item in overall if item["method"] == "opendetect")
    candidates = [npos, opendetect]
    selected = min(
        candidates,
        key=lambda item: (item["mean_unknown_metric_rank"], -item["unknown_auroc"]),
    )
    summary = {
        "schema_version": "strict_v4_npos_31method_screen_v1",
        "status": "complete",
        "method_count": 31,
        "added_methods": ["npos_knn"],
        "overall": overall,
        "by_suite": by_suite,
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "artifact_checks": artifact_checks,
            "failure_count": len(list(args.run_root.glob("**/failure.json"))),
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "comparator_decision": {
            "selection_rule": "lower 31-method four-unknown-metric mean rank, then higher AUROC",
            "previous_comparator": "opendetect",
            "selected_comparator": selected["method"],
            "selected_mean_unknown_metric_rank": selected["mean_unknown_metric_rank"],
            "selected_metrics": {metric: selected[metric] for metric in ("known_macro_f1", *METRICS)},
            "comparator_changed": selected["method"] != "opendetect",
            "new_npos_three_seed_confirmation_required": selected["method"] == "npos_knn",
            "existing_opendetect_confirmation_remains_primary": selected["method"] == "opendetect",
        },
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "existing_30method_summary_sha256": file_hash(args.existing_summary),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(render(summary), encoding="utf-8")
    (args.output_dir / "full102_complete").touch()
    print(render(summary), end="")


if __name__ == "__main__":
    main()
