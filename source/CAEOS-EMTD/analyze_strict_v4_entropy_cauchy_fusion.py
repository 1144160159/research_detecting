from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from analyze_entropy_cauchy_fusion import task_report
from screen_strict_v4_risk_candidates_v2 import (
    REFERENCE,
    UNKNOWN_METRICS,
    oriented_delta,
    screen,
)


PHASES = {
    "pilot": {
        "cic_ton_iot": {
            "ransomware": (7,),
            "scanning": (7,),
            "xss": (7,),
        },
        "cic_iot2023": {
            "command_injection": (7,),
            "ddos_icmp_flood": (7,),
            "mirai_udpplain": (7,),
        },
    },
    "confirmation_v1": {
        "cic_ton_iot": {
            "backdoor": (11, 19),
            "ddos": (11, 19),
            "password": (11, 19),
        },
        "cic_iot2023": {
            "browser_hijacking": (11, 19),
            "dns_spoofing": (11, 19),
            "recon_port_scan": (11, 19),
        },
    },
    "confirmation_v2": {
        "cic_ton_iot": {
            "dos": (23, 37),
            "injection": (23, 37),
            "mitm": (23, 37),
        },
        "cic_iot2023": {
            "backdoor_malware": (23, 37),
            "ddos_http_flood": (23, 37),
            "dictionary_bruteforce": (23, 37),
        },
    },
}


def load_runs(roots: dict[str, Path], acceptance: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runs = []
    sources = []
    endpoint_checks = 0
    for phase, suites in PHASES.items():
        root = roots[phase]
        for suite, scenarios in suites.items():
            for scenario, seeds in scenarios.items():
                for seed in seeds:
                    directory = root / suite / f"{scenario}_seed{seed}"
                    result = task_report(directory, acceptance)
                    metrics_path = directory / "metrics.json"
                    metrics_raw = metrics_path.read_bytes()
                    metrics = json.loads(metrics_raw.decode("utf-8"))
                    current = metrics.get("reports", {}).get(REFERENCE)
                    if not isinstance(current, dict):
                        raise ValueError(f"missing {REFERENCE} under {directory}")
                    result["reports"][REFERENCE] = {
                        metric: float(current[metric])
                        for metric in (
                            "known_macro_f1",
                            "unknown_auroc",
                            "unknown_aupr",
                            "unknown_fpr95",
                            "oscr",
                            "known_acceptance_rate",
                            "unknown_rejection_rate",
                        )
                    }
                    result.update(
                        {
                            "phase": phase,
                            "suite": suite,
                            "scenario": scenario,
                            "seed": seed,
                        }
                    )
                    runs.append(result)
                    endpoint_checks += int(result["endpoint_replay_checks"])
                    sources.append(
                        {
                            "phase": phase,
                            "path": metrics_path.relative_to(root).as_posix(),
                            "sha256": hashlib.sha256(metrics_raw).hexdigest(),
                        }
                    )
    expected = sum(
        len(seeds)
        for suites in PHASES.values()
        for scenarios in suites.values()
        for seeds in scenarios.values()
    )
    if len(runs) != expected:
        raise ValueError(f"run count mismatch: {len(runs)} != {expected}")
    source_hash = hashlib.sha256(
        json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return runs, {
        "passes": True,
        "run_count": len(runs),
        "scenario_count": sum(
            len(scenarios)
            for suites in PHASES.values()
            for scenarios in suites.values()
        ),
        "endpoint_replay_checks": endpoint_checks,
        "source_metrics_combined_sha256": source_hash,
        "development_screening_uses_test_unknown_labels": True,
        "runtime_fusion_uses_unknown_or_test_labels": False,
        "calibration": "each endpoint empirical CDF and fusion threshold use known validation only",
    }


def build_blocks(runs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        grouped[(run["suite"], run["scenario"])].append(run)
    methods = sorted(set(runs[0]["reports"]))
    blocks = []
    for (suite, scenario), repeats in sorted(grouped.items()):
        if any(set(run["reports"]) != set(methods) for run in repeats):
            raise ValueError(f"fusion method mismatch for {suite}/{scenario}")
        deltas = {
            method: {
                metric: float(
                    np.mean(
                        [
                            oriented_delta(
                                run["reports"][method][metric],
                                run["reports"][REFERENCE][metric],
                                metric,
                            )
                            for run in repeats
                        ]
                    )
                )
                for metric in UNKNOWN_METRICS
            }
            for method in methods
        }
        blocks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed_count": len(repeats),
                "deltas": deltas,
            }
        )
    return blocks, methods


def markdown(report: dict[str, Any]) -> str:
    screening = report["screening"]
    lines = [
        "# Strict-v4 entropy-Cauchy fusion development analysis",
        "",
        f"Runs: {report['validation']['run_count']}; scenario blocks: "
        f"{report['validation']['scenario_count']}; endpoint replay checks: "
        f"{report['validation']['endpoint_replay_checks']}.",
        "All previously opened strict-v4 results are development evidence. This report does not freeze a confirmation claim.",
        f"Development-selected candidate: `{screening['selected_candidate']}`; eligible: {screening['eligible_count']}.",
        "",
        "| Method | Eligible | AUROC | AUPR | FPR95 oriented | OSCR | Worst suite-metric | Worst LOSO-metric |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in screening["method_table"]:
        values = row["combined"]
        lines.append(
            f"| {row['method']} | {str(row['eligible']).lower()} | "
            f"{values['unknown_auroc']:+.6f} | {values['unknown_aupr']:+.6f} | "
            f"{values['unknown_fpr95']:+.6f} | {values['oscr']:+.6f} | "
            f"{row['worst_suite_metric_gain']:+.6f} | "
            f"{row['worst_loso_metric_gain']:+.6f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze validation-calibrated entropy/Cauchy fusions on strict-v4"
    )
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--confirmation-v1-root", type=Path, required=True)
    parser.add_argument("--confirmation-v2-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    args = parser.parse_args()
    runs, validation = load_runs(
        {
            "pilot": args.pilot_root,
            "confirmation_v1": args.confirmation_v1_root,
            "confirmation_v2": args.confirmation_v2_root,
        },
        args.known_acceptance,
    )
    blocks, methods = build_blocks(runs)
    screening = screen(blocks, methods)
    report = {
        "schema_version": "strict_v4_entropy_cauchy_fusion_development_v1",
        "status": "development_only",
        "validation": validation,
        "scenario_blocks": blocks,
        "screening": screening,
        "runs": runs,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "selected_candidate": screening["selected_candidate"],
                "eligible_count": screening["eligible_count"],
                "eligible_ranking": screening["eligible_ranking"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
