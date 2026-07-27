from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def oriented(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 VOS pilot",
        "",
        f"Expansion gate: **{'PASS' if result['decision']['expand_to_full102'] else 'FAIL'}**.",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for record in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | "
            "{unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | "
            "{mean_unknown_metric_rank:.2f} |".format(**record)
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_json(args.protocol)
    gate = load_json(args.gate)
    if (
        protocol.get("schema_version") != "strict_v4_vos_pilot_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or gate.get("schema_version") != "strict_v4_vos_pilot_expansion_gate_v1"
        or gate.get("manifest_sha256") != canonical_hash(gate)
        or gate.get("pilot_protocol_manifest_sha256") != protocol["manifest_sha256"]
    ):
        raise ValueError("VOS pilot frozen artifacts validation failed")
    if protocol["implementation_sha256"]["summarize_strict_v4_vos_pilot.py"] != file_hash(
        Path(__file__)
    ):
        raise ValueError("VOS summarizer implementation SHA mismatch")
    if not (args.run_root / "execution_complete").is_file():
        raise ValueError("VOS pilot execution is incomplete")

    records: list[dict[str, Any]] = []
    failures = len(list(args.run_root.glob("**/failure.json")))
    for source in protocol["source_registry"]:
        candidate_path = (
            args.run_root
            / source["suite"]
            / f"{source['scenario']}_seed{source['seed']}_vos"
            / "metrics.json"
        )
        candidate = load_json(candidate_path)
        mlp = load_json(Path(source["mlp_metrics"]))
        comparator = load_json(Path(source["comparator_metrics"]))
        if (
            file_hash(Path(source["mlp_metrics"])) != source["mlp_metrics_sha256"]
            or file_hash(Path(source["comparator_metrics"]))
            != source["comparator_metrics_sha256"]
            or candidate.get("schema_version") != "strict_v4_vos_metrics_v1"
            or candidate["split_metadata"]["split_fingerprint"]["combined"]
            != source["split_fingerprint"]
            or candidate.get("selection_evidence", {}).get(
                "unknown_or_test_labels_used_for_fitting_or_selection"
            )
            is not False
        ):
            raise ValueError(f"VOS pilot source validation failed: {candidate_path}")
        records.append(
            {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "methods": {
                    "vos_energy": candidate["reports"]["vos_energy"],
                    "mlp_energy": mlp["reports"]["energy"],
                    "opendetect": comparator["reports"]["opendetect"],
                },
            }
        )
    if len(records) != 14:
        raise ValueError("VOS pilot record count mismatch")

    method_names = ("vos_energy", "mlp_energy", "opendetect")
    overall: dict[str, dict[str, Any]] = {}
    for method in method_names:
        overall[method] = {
            "method": method,
            **{
                metric: float(
                    np.mean([record["methods"][method][metric] for record in records])
                )
                for metric in ("known_macro_f1", *METRICS)
            },
        }
    for metric in METRICS:
        values = np.asarray([overall[name][metric] for name in method_names])
        ranks = rankdata(
            values if metric == "unknown_fpr95" else -values, method="average"
        )
        for name, rank in zip(method_names, ranks):
            overall[name].setdefault("metric_ranks", {})[metric] = float(rank)
    for name in method_names:
        overall[name]["mean_unknown_metric_rank"] = float(
            np.mean(list(overall[name]["metric_ranks"].values()))
        )

    gains = {
        metric: [
            oriented(
                record["methods"]["vos_energy"][metric],
                record["methods"]["opendetect"][metric],
                metric,
            )
            for record in records
        ]
        for metric in METRICS
    }
    known_deltas = [
        record["methods"]["vos_energy"]["known_macro_f1"]
        - record["methods"]["opendetect"]["known_macro_f1"]
        for record in records
    ]
    suite_gains = {}
    for suite in sorted({record["suite"] for record in records}):
        suite_records = [record for record in records if record["suite"] == suite]
        suite_gains[suite] = float(
            np.mean(
                [
                    oriented(
                        record["methods"]["vos_energy"][metric],
                        record["methods"]["opendetect"][metric],
                        metric,
                    )
                    for record in suite_records
                    for metric in METRICS
                ]
            )
        )
    mean_gains = {metric: float(np.mean(values)) for metric, values in gains.items()}
    checks = {
        "pilot_runs_complete": len(records) == 14 and failures == 0,
        "split_and_leakage_integrity": True,
        "known_f1_tolerance": float(np.mean(known_deltas)) >= -0.03
        and min(known_deltas) >= -0.10,
        "top_two_rank": overall["vos_energy"]["mean_unknown_metric_rank"] <= 2.0,
        "metric_breadth": sum(value > 0.0 for value in mean_gains.values()) >= 2,
        "overall_gain": float(np.mean(list(mean_gains.values()))) > 0.0,
        "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 4
        and min(suite_gains.values()) >= -0.05,
    }
    passes = all(checks.values())
    result = {
        "schema_version": "strict_v4_vos_pilot_analysis_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "validation": {
            "passes": True,
            "scenario_count": 14,
            "failure_count": failures,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "overall": sorted(
            overall.values(), key=lambda item: item["mean_unknown_metric_rank"]
        ),
        "vos_vs_opendetect": {
            "metric_mean_oriented_gains": mean_gains,
            "four_metric_mean_gain": float(np.mean(list(mean_gains.values()))),
            "known_f1_mean_delta": float(np.mean(known_deltas)),
            "known_f1_worst_delta": float(min(known_deltas)),
            "suite_four_metric_mean_gains": suite_gains,
        },
        "expansion_checks": checks,
        "decision": {
            "expand_to_full102": passes,
            "development_screen_only": True,
            "confirmatory_claim_allowed": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    (args.output_dir / "expansion_decision.json").write_text(
        json.dumps(
            {
                "schema_version": "strict_v4_vos_expansion_decision_v1",
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "checks": checks,
                "expand_to_full102": passes,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "pilot_analysis_complete").touch()
    (args.output_dir / "pilot_complete").touch()
    print(render(result), end="")


if __name__ == "__main__":
    main()
