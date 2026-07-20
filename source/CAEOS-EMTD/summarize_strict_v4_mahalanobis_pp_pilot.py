from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from summarize_strict_v4_pilot import METRICS, aggregate_table, report_metrics


METHODS = ("mahalanobis_pp", "mlp_mahalanobis", "opendetect")
UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def output_for(root: Path, key: str) -> Path:
    suite, scenario = key.split("/", 1)
    return root / suite / f"{scenario}_seed7_mahalanobis_pp"


def current_hashes(root: Path, relative: str) -> dict[str, str]:
    run = root / relative
    return {
        name: file_hash(run / name) for name in ("metrics.json", "scores.npz", "model.pt")
    }


def oriented_gain(candidate: dict[str, float], reference: dict[str, float]) -> float:
    gains = []
    for metric in UNKNOWN_METRICS:
        if metric == "unknown_fpr95":
            gains.append(reference[metric] - candidate[metric])
        else:
            gains.append(candidate[metric] - reference[metric])
    return float(sum(gains) / len(gains))


def validate_and_load(
    protocol: dict[str, Any], pilot_root: Path
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    mlp_root = Path(protocol["mlp_root"])
    opendetect_root = Path(protocol["opendetect_root"])
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    artifact_checks = 0
    split_checks = 0
    for key, source in sorted(protocol["sources"].items()):
        output = output_for(pilot_root, key)
        required = ("metrics.json", "scores.npz", "provenance.json")
        missing = [name for name in required if not (output / name).is_file()]
        if missing:
            raise ValueError(f"missing Mahalanobis++ artifacts under {output}: {missing}")
        metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
        provenance = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
        mlp_run = mlp_root / source["mlp_relative_path"]
        comparator_run = opendetect_root / source["opendetect_relative_path"]
        if current_hashes(mlp_root, source["mlp_relative_path"]) != source[
            "mlp_artifact_sha256"
        ]:
            raise ValueError(f"frozen MLP source changed after protocol freeze: {key}")
        if current_hashes(opendetect_root, source["opendetect_relative_path"]) != source[
            "opendetect_artifact_sha256"
        ]:
            raise ValueError(f"frozen OpenDetect source changed after protocol freeze: {key}")
        if provenance.get("source_artifact_sha256") != source["mlp_artifact_sha256"]:
            raise ValueError(f"Mahalanobis++ source SHA binding mismatch: {key}")
        if set(metrics.get("reports", {})) != {"mahalanobis_pp"}:
            raise ValueError(f"Mahalanobis++ report set mismatch: {key}")
        selection = metrics.get("selection_evidence", {})
        if selection.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            raise ValueError(f"Mahalanobis++ leakage guard failed: {key}")
        if selection.get("postprocessor", {}).get("unknown_or_test_labels_used") is not False:
            raise ValueError(f"Mahalanobis++ calibrator leakage guard failed: {key}")
        mlp_metrics = json.loads((mlp_run / "metrics.json").read_text(encoding="utf-8"))
        comparator_metrics = json.loads(
            (comparator_run / "metrics.json").read_text(encoding="utf-8")
        )
        fingerprints = {
            metrics["split_metadata"]["split_fingerprint"]["combined"],
            mlp_metrics["split_metadata"]["split_fingerprint"]["combined"],
            comparator_metrics["split_metadata"]["split_fingerprint"]["combined"],
            source["split_fingerprint"],
        }
        if len(fingerprints) != 1:
            raise ValueError(f"Mahalanobis++ split fingerprint mismatch: {key}")
        blocks[key] = {
            "mahalanobis_pp": report_metrics(
                metrics["reports"]["mahalanobis_pp"], f"{key}/mahalanobis_pp"
            ),
            "mlp_mahalanobis": report_metrics(
                mlp_metrics["reports"]["mahalanobis"], f"{key}/mlp_mahalanobis"
            ),
            "opendetect": report_metrics(
                comparator_metrics["reports"]["opendetect"], f"{key}/opendetect"
            ),
        }
        artifact_checks += 9
        split_checks += 1
    expected = int(protocol["expected_scenarios"])
    if len(blocks) != expected:
        raise ValueError(f"Mahalanobis++ scenario coverage mismatch: {len(blocks)}/{expected}")
    return blocks, {
        "passes": True,
        "scenario_count": len(blocks),
        "artifact_sha_checks": artifact_checks,
        "split_fingerprint_triplet_checks": split_checks,
        "failure_count": 0,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }


def analyze(protocol: dict[str, Any], blocks: dict[str, Any]) -> dict[str, Any]:
    overall = aggregate_table(blocks)
    by_suite = {
        suite: aggregate_table(
            {key: value for key, value in blocks.items() if key.startswith(f"{suite}/")}
        )
        for suite in sorted({key.split("/", 1)[0] for key in blocks})
    }
    by_name = {row["method"]: row for row in overall}
    overall_gain = oriented_gain(
        by_name["mahalanobis_pp"], by_name["mlp_mahalanobis"]
    )
    suite_gains = {}
    for suite, rows in by_suite.items():
        suite_by_name = {row["method"]: row for row in rows}
        suite_gains[suite] = oriented_gain(
            suite_by_name["mahalanobis_pp"], suite_by_name["mlp_mahalanobis"]
        )
    known_difference = max(
        abs(
            methods["mahalanobis_pp"]["known_macro_f1"]
            - methods["mlp_mahalanobis"]["known_macro_f1"]
        )
        for methods in blocks.values()
    )
    candidate_rank = float(by_name["mahalanobis_pp"]["mean_unknown_metric_rank"])
    gate = protocol["expansion_gate"]
    checks = {
        "all_14_runs_complete": len(blocks) == protocol["expected_scenarios"],
        "failure_count": 0 == gate["failure_count"],
        "split_and_source_sha_checks_pass": True,
        "known_f1_nonregression": known_difference
        <= gate["known_f1_max_absolute_difference_from_source_mlp"],
        "overall_gain": overall_gain
        >= gate["four_unknown_metric_oriented_mean_gain_vs_mahalanobis_minimum"],
        "suite_robustness": sum(value >= 0.0 for value in suite_gains.values())
        >= gate["suite_nonnegative_gain_count_vs_mahalanobis_minimum"],
        "top_two_rank": candidate_rank
        <= gate["mean_unknown_metric_rank_among_three_maximum"],
    }
    return {
        "overall": overall,
        "by_suite": by_suite,
        "mahalanobis_pp_vs_mahalanobis_four_metric_mean_gain": overall_gain,
        "mahalanobis_pp_vs_mahalanobis_suite_mean_gains": suite_gains,
        "known_f1_max_absolute_difference": known_difference,
        "expansion_checks": checks,
        "decision": {
            "expand_to_full102": all(checks.values()),
            "development_screen_only": True,
            "confirmatory_claim_allowed": False,
        },
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 Mahalanobis++ 冻结试点",
        "",
        f"场景：`{report['validation']['scenario_count']}/14`；失败："
        f"`{report['validation']['failure_count']}`；扩展 full102："
        f"`{str(report['decision']['expand_to_full102']).lower()}`。",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["overall"]:
        lines.append(
            f"| {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"相对标准 Mahalanobis 的四指标有向平均增益："
            f"`{report['mahalanobis_pp_vs_mahalanobis_four_metric_mean_gain']:+.6f}`。",
            "该结果仅为 seed7 发展试点，不能单独用于确认性 SOTA 声明。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("Mahalanobis++ protocol SHA mismatch")
    marker = args.pilot_root / "pilot_complete"
    if not marker.is_file() or marker.read_text(encoding="ascii").strip() != protocol[
        "manifest_sha256"
    ]:
        raise ValueError("Mahalanobis++ pilot completion marker is absent or stale")
    blocks, validation = validate_and_load(protocol, args.pilot_root)
    report = {
        "schema_version": "strict_v4_mahalanobis_pp_pilot_analysis_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "validation": validation,
        **analyze(protocol, blocks),
        "analysis_implementation_sha256": file_hash(Path(__file__).resolve()),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(report), encoding="utf-8")
    (args.output_dir / "expansion_gate.json").write_text(
        json.dumps(
            {
                "schema_version": "strict_v4_mahalanobis_pp_expansion_decision_v1",
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "checks": report["expansion_checks"],
                "expand_to_full102": report["decision"]["expand_to_full102"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "pilot_analysis_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )
    print(json.dumps(report["decision"], sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
