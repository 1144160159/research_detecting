from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_strict_v4_validation_router import (
    CAUCHY,
    REFERENCE,
    canonical_hash,
    choose_rule,
    load_runs,
    nested_loso,
)


EARLY_PHASES = {
    "pilot": {
        "cic_ton_iot": {"ransomware": (7,), "scanning": (7,), "xss": (7,)},
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

PHASES = {
    **EARLY_PHASES,
    "router_confirmation_v1": {
        "cic_ton_iot": {
            name: (47, 53)
            for name in (
                "backdoor",
                "ddos",
                "dos",
                "injection",
                "mitm",
                "password",
                "ransomware",
                "scanning",
                "xss",
            )
        },
        "cic_iot2023": {
            name: (47, 53)
            for name in (
                "ddos_ack_fragmentation",
                "ddos_slowloris",
                "dos_syn_flood",
                "mitm_arp_spoofing",
                "recon_os_scan",
                "vulnerability_scan",
            )
        },
    },
}

CONFIRMATION = {
    "seeds": [59, 61],
    "scenarios": {
        "cic_ton_iot": [
            "backdoor",
            "ddos",
            "dos",
            "injection",
            "mitm",
            "password",
            "ransomware",
            "scanning",
            "xss",
        ],
        "cic_iot2023": [
            "ddos_icmp_fragmentation",
            "ddos_pshack_flood",
            "ddos_rstfin_flood",
            "dos_http_flood",
            "recon_host_discovery",
            "sql_injection",
        ],
    },
}


def analyze(runs: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    suites = sorted({run["suite"] for run in runs})
    by_suite = {}
    for suite in suites:
        suite_runs = [run for run in runs if run["suite"] == suite]
        selected, screening = choose_rule(suite_runs)
        nested = nested_loso(suite_runs)
        by_suite[suite] = {
            "run_count": len(suite_runs),
            "scenario_count": len({run["scenario"] for run in suite_runs}),
            "selected_rule": selected,
            "selected_rule_name": selected["name"] if selected else None,
            "screening": screening,
            "nested_loso": nested,
            "passes": selected is not None and nested["passes"],
        }
    freeze = all(report["passes"] for report in by_suite.values())
    return {
        "schema_version": "strict_v4_known_validation_suite_router_development_v1",
        "status": "freeze_candidate" if freeze else "rejected_development_candidate",
        "freeze_candidate": freeze,
        "validation": validation,
        "by_suite": by_suite,
    }


def build_manifest(report: dict[str, Any]) -> dict[str, Any]:
    frozen = bool(report["freeze_candidate"])
    selected_rules = {
        suite: values["selected_rule"]
        for suite, values in report["by_suite"].items()
    } if frozen else {}
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_validation_suite_router_candidate_v1",
        "status": "frozen_unconfirmed" if frozen else "no_candidate",
        "frozen_before_confirmation": frozen,
        "candidate": {
            "name": "known_validation_suite_class_tail_router_v2",
            "selected_rules": selected_rules,
            "candidate_endpoint": CAUCHY,
            "fallback_endpoint": REFERENCE,
            "runtime_features_use_known_validation_only": True,
            "runtime_routing_uses_known_suite_identity": True,
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "development": {
            "phases": PHASES,
            "run_count": report["validation"]["run_count"],
            "scenario_count": report["validation"]["scenario_count"],
            "source_metrics_combined_sha256": report["validation"][
                "source_metrics_combined_sha256"
            ],
            "rule_selection_uses_test_unknown_labels": True,
            "nested_loso_by_suite": {
                suite: values["nested_loso"]
                for suite, values in report["by_suite"].items()
            },
        },
        "confirmation": {
            **CONFIRMATION,
            "expected_run_count": sum(
                len(values) for values in CONFIRMATION["scenarios"].values()
            ) * len(CONFIRMATION["seeds"]),
            "seed_disjoint": True,
            "scenario_boundary": {
                "cic_iot2023": "unseen_attack_scenarios_and_unseen_seeds",
                "cic_ton_iot": "all_attack_scenarios_cross_seed_replication",
            },
        },
        "confirmation_gate": {
            "unit": "scenario mean across confirmation seeds",
            "combined_unknown_auroc_mean_improvement_required": True,
            "combined_unknown_auroc_scenario_bootstrap_ci_lower_gt_zero": True,
            "unknown_aupr_nonregression_tolerance": 0.01,
            "unknown_fpr95_oriented_nonregression_tolerance": 0.01,
            "oscr_nonregression_tolerance": 0.01,
            "each_suite_all_four_oriented_means_positive": True,
            "both_endpoints_must_be_exercised": True,
            "fallback": REFERENCE,
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    return manifest


def markdown(report: dict[str, Any], manifest: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 suite-aware known-validation router development",
        "",
        f"Runs: {report['validation']['run_count']}; unique suite/scenario blocks: "
        f"{report['validation']['scenario_count']}.",
        f"Freeze candidate: **{str(report['freeze_candidate']).lower()}**; manifest: "
        f"`{manifest['manifest_sha256']}`.",
        "",
        "| Suite | Rule | AUROC | AUPR | FPR95 oriented | OSCR | Nested pass |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for suite, values in report["by_suite"].items():
        gains = values["nested_loso"]["combined"]
        lines.append(
            f"| {suite} | {values['selected_rule_name']} | "
            f"{gains['unknown_auroc']:+.6f} | {gains['unknown_aupr']:+.6f} | "
            f"{gains['unknown_fpr95']:+.6f} | {gains['oscr']:+.6f} | "
            f"{str(values['nested_loso']['passes']).lower()} |"
        )
    lines.extend(
        [
            "",
            "Rules may use known suite identity and known-validation features only. "
            "All opened test outcomes are development evidence, not confirmation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Develop suite-aware strict-v4 validation routers")
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--confirmation-v1-root", type=Path, required=True)
    parser.add_argument("--confirmation-v2-root", type=Path, required=True)
    parser.add_argument("--router-confirmation-v1-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    runs, validation = load_runs(
        {
            "pilot": args.pilot_root,
            "confirmation_v1": args.confirmation_v1_root,
            "confirmation_v2": args.confirmation_v2_root,
            "router_confirmation_v1": args.router_confirmation_v1_root,
        },
        PHASES,
    )
    report = analyze(runs, validation)
    manifest = build_manifest(report)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(markdown(report, manifest), encoding="utf-8")
    (args.output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "selected_rules": {
                    suite: values["selected_rule_name"]
                    for suite, values in report["by_suite"].items()
                },
                "manifest_sha256": manifest["manifest_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
