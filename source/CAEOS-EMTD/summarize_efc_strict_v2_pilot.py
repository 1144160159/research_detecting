from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
EFC_METHOD = "efc_energy_margin"
RONETC_METHOD = "ronetc"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize the strict-v2 EFC pilot")
    parser.add_argument("--efc-root", required=True)
    parser.add_argument("--gate-root", required=True)
    parser.add_argument("--ronetc-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", required=True)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(f"missing JSON artifact: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return payload


def fingerprint(payload: dict[str, object], path: Path) -> str:
    try:
        value = payload["split_metadata"]["split_fingerprint"]["combined"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"missing split fingerprint: {path}") from exc
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"invalid split fingerprint: {path}")
    return value


def metric_report(payload: object, label: str) -> dict[str, float]:
    if not isinstance(payload, dict):
        raise ValueError(f"invalid metric report: {label}")
    report = {}
    for metric in METRICS:
        value = float(payload[metric])
        if not np.isfinite(value):
            raise ValueError(f"non-finite {metric}: {label}")
        report[metric] = value
    return report


def summarize(
    efc_root: Path,
    gate_root: Path,
    ronet_root: Path,
    manifest_path: Path,
) -> dict[str, object]:
    manifest = read_json(manifest_path)
    if manifest.get("status") != "frozen_before_real_results":
        raise ValueError("EFC pilot manifest is not frozen")
    tasks = manifest.get("pilot")
    if not isinstance(tasks, list) or len(tasks) != 3:
        raise ValueError("EFC pilot manifest must contain exactly three tasks")

    rows = []
    fingerprints = 0
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("invalid pilot task")
        suite = str(task["suite"])
        scenario = str(task["scenario"])
        seed = int(task["seed"])
        efc_dir = efc_root / suite / f"{scenario}_seed{seed}_efc"
        for artifact in ("metrics.json", "scores.npz", "provenance.json"):
            if not (efc_dir / artifact).is_file():
                raise ValueError(f"missing EFC artifact: {efc_dir / artifact}")
        efc_path = efc_dir / "metrics.json"
        gate_path = gate_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
        ronet_path = (
            ronet_root / suite / f"{scenario}_seed{seed}_ronetc" / "metrics.json"
        )
        efc = read_json(efc_path)
        gate = read_json(gate_path)
        ronet = read_json(ronet_path)
        identities = {
            fingerprint(efc, efc_path),
            fingerprint(gate, gate_path),
            fingerprint(ronet, ronet_path),
        }
        if len(identities) != 1:
            raise ValueError(f"split fingerprint mismatch for {suite}/{scenario}/seed{seed}")
        fingerprints += 2
        evidence = efc.get("selection_evidence")
        if not isinstance(evidence, dict) or any(
            evidence.get(key) is not False
            for key in (
                "unknown_or_test_labels_used_for_training",
                "unknown_or_test_labels_used_for_preprocessing",
                "unknown_or_test_labels_used_for_thresholds",
            )
        ):
            raise ValueError(f"invalid EFC leakage declaration: {efc_path}")
        if efc.get("upstream", {}).get("commit") != manifest["upstream"]["commit"]:
            raise ValueError(f"EFC upstream commit mismatch: {efc_path}")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "split_fingerprint": next(iter(identities)),
                "reports": {
                    "efc": metric_report(efc["reports"][EFC_METHOD], str(efc_path)),
                    "caeos": metric_report(gate["selected_report"], str(gate_path)),
                    "ronetc": metric_report(
                        ronet["reports"][RONETC_METHOD], str(ronet_path)
                    ),
                },
            }
        )

    means = {
        method: {
            metric: float(np.mean([row["reports"][method][metric] for row in rows]))
            for metric in METRICS
        }
        for method in ("efc", "caeos", "ronetc")
    }

    def oriented(method: str, reference: str, metric: str) -> float:
        raw = means[method][metric] - means[reference][metric]
        return float(-raw if metric == "unknown_fpr95" else raw)

    efc_vs_ronetc = {
        metric: oriented("efc", "ronetc", metric) for metric in METRICS
    }
    efc_vs_caeos = {
        metric: oriented("efc", "caeos", metric) for metric in METRICS
    }
    per_task_auroc = [
        row["reports"]["efc"]["unknown_auroc"]
        - row["reports"]["ronetc"]["unknown_auroc"]
        for row in rows
    ]
    budget_gate = {
        "mean_auroc_not_worse": efc_vs_ronetc["unknown_auroc"] >= 0.0,
        "mean_oscr_within_0_02": efc_vs_ronetc["oscr"] >= -0.02,
        "mean_known_f1_within_0_02": efc_vs_ronetc["known_macro_f1"] >= -0.02,
        "every_task_auroc_within_0_10": min(per_task_auroc) >= -0.10,
    }
    expand = all(budget_gate.values())
    return {
        "schema_version": "efc_strict_v2_pilot_summary_v1",
        "state": "complete",
        "task_count": len(rows),
        "split_fingerprint_pair_checks": fingerprints,
        "rows": rows,
        "means": means,
        "oriented_improvement": {
            "efc_vs_ronetc": efc_vs_ronetc,
            "efc_vs_caeos": efc_vs_caeos,
        },
        "budget_gate": budget_gate,
        "decision": "expand_strict_v2_190" if expand else "retain_three_task_pilot",
        "decision_scope": "compute_budget_only_not_statistical_superiority",
    }


def markdown(summary: dict[str, object]) -> str:
    lines = [
        "# EFC strict-v2 pilot",
        "",
        f"Decision: `{summary['decision']}`. This gate controls compute budget only.",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method in ("efc", "caeos", "ronetc"):
        row = summary["means"][method]
        lines.append(
            f"| {method} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} |"
        )
    lines.extend(["", "## Budget gate", ""])
    for name, passed in summary["budget_gate"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    summary = summarize(
        Path(args.efc_root),
        Path(args.gate_root),
        Path(args.ronetc_root),
        Path(args.manifest),
    )
    Path(args.output).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    Path(args.markdown_output).write_text(markdown(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
