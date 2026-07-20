from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any, Optional

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
METHODS = ("gen", "shannon_entropy", "mlp_energy", "opendetect")


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return payload


def _report(payload: dict[str, Any], method: str, path: Path) -> dict[str, float]:
    report = payload.get("reports", {}).get(method)
    if not isinstance(report, dict):
        raise ValueError(f"missing report {method}: {path}")
    result = {}
    for metric in METRICS:
        value = float(report[metric])
        if not math.isfinite(value):
            raise ValueError(f"non-finite {method}.{metric}: {path}")
        result[metric] = value
    return result


def _fingerprint(payload: dict[str, Any]) -> Optional[str]:
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def analyze(
    pilot_root: Path,
    source_root: Path,
    opendetect_root: Path,
    gate: dict[str, Any],
) -> dict[str, Any]:
    protocol = _read(pilot_root / "protocol_manifest.json")
    if gate.get("schema_version") != "strict_v4_mlp_logit_posthoc_expansion_gate_v1":
        raise ValueError("unexpected expansion gate schema")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("expansion gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("expansion gate protocol binding mismatch")

    blocks = []
    failures = list(pilot_root.glob("**/failure.json"))
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            new_path = pilot_root / suite / f"{scenario}_seed7" / "metrics.json"
            source_path = source_root / suite / f"{scenario}_seed7_mlp" / "metrics.json"
            external_path = (
                opendetect_root / suite / f"{scenario}_seed7_opendetect" / "metrics.json"
            )
            new = _read(new_path)
            source = _read(source_path)
            external = _read(external_path)
            fingerprints = [_fingerprint(item) for item in (new, source, external)]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError(f"split fingerprint mismatch for {suite}/{scenario}")
            blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "reports": {
                        "gen": _report(new, "gen", new_path),
                        "shannon_entropy": _report(new, "shannon_entropy", new_path),
                        "mlp_energy": _report(source, "energy", source_path),
                        "opendetect": _report(external, "opendetect", external_path),
                    },
                }
            )

    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / len(blocks)
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-value for value in values], method="average")
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / len(UNKNOWN_METRICS)
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))

    oriented_gains = {}
    for metric in UNKNOWN_METRICS:
        raw = [
            (
                block["reports"]["mlp_energy"][metric]
                - block["reports"]["gen"][metric]
                if metric == "unknown_fpr95"
                else block["reports"]["gen"][metric]
                - block["reports"]["mlp_energy"][metric]
            )
            for block in blocks
        ]
        oriented_gains[metric] = sum(raw) / len(raw)

    by_suite = defaultdict(list)
    for block in blocks:
        gains = []
        for metric in UNKNOWN_METRICS:
            candidate = block["reports"]["gen"][metric]
            reference = block["reports"]["mlp_energy"][metric]
            gains.append(reference - candidate if metric == "unknown_fpr95" else candidate - reference)
        by_suite[block["suite"]].append(sum(gains) / len(gains))
    suite_gains = {
        suite: sum(values) / len(values) for suite, values in sorted(by_suite.items())
    }
    gen_row = next(row for row in overall if row["method"] == "gen")
    known_f1_max_difference = max(
        abs(block["reports"]["gen"]["known_macro_f1"] - block["reports"]["mlp_energy"]["known_macro_f1"])
        for block in blocks
    )
    checks = {
        "pilot_runs_complete": len(blocks) == 14 and not failures,
        "split_integrity": True,
        "known_f1_nonregression": known_f1_max_difference <= 1e-12,
        "top_half_rank": gen_row["mean_unknown_metric_rank"] <= 2.5,
        "metric_breadth": sum(value > 0.0 for value in oriented_gains.values()) >= 2,
        "overall_gain": sum(oriented_gains.values()) / len(oriented_gains) > 0.0,
        "suite_robustness": (
            sum(value >= 0.0 for value in suite_gains.values()) >= 4
            and min(suite_gains.values()) >= -0.05
        ),
    }
    return {
        "schema_version": "strict_v4_mlp_logit_posthoc_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks),
        "failure_count": len(failures),
        "overall": overall,
        "gen_vs_mlp_energy_oriented_mean_gains": oriented_gains,
        "gen_vs_mlp_energy_four_metric_mean_gain": sum(oriented_gains.values()) / len(oriented_gains),
        "gen_vs_mlp_energy_suite_mean_gains": suite_gains,
        "known_f1_max_absolute_difference": known_f1_max_difference,
        "expansion_checks": checks,
        "decision": {
            "expand_gen_to_full102": all(checks.values()),
            "shannon_entropy_is_diagnostic_only": True,
        },
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 GEN pilot analysis",
        "",
        f"Expand GEN to full 102: `{'YES' if result['decision']['expand_gen_to_full102'] else 'NO'}`.",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | "
            "{unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | "
            "{mean_unknown_metric_rank:.2f} |".format(**row)
        )
    lines.extend(["", "## Expansion gate", ""])
    for name, passed in result["expansion_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    gate = _read(args.gate)
    result = analyze(args.pilot_root, args.source_root, args.opendetect_root, gate)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
