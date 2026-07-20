from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from screen_strict_v4_risk_candidates_v2 import (
    REFERENCE,
    UNKNOWN_METRICS,
    oriented_delta,
    screen,
)


CAUCHY = "cauchy_all"
COMPONENTS = ("uncertainty", "distance", "conflict", "tree_disagreement")
QUANTILES = (0.20, 0.35, 0.50, 0.65, 0.80)
CONFIRMATION = {
    "seeds": [47, 53],
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
            "ddos_ack_fragmentation",
            "ddos_slowloris",
            "dos_syn_flood",
            "mitm_arp_spoofing",
            "recon_os_scan",
            "vulnerability_scan",
        ],
    },
}


def empirical_percentile(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    ref = np.sort(np.asarray(reference, dtype=np.float64).reshape(-1))
    query = np.asarray(values, dtype=np.float64).reshape(-1)
    if not len(ref) or not np.isfinite(ref).all() or not np.isfinite(query).all():
        raise ValueError("empirical percentile requires finite validation values")
    return (np.searchsorted(ref, query, side="right") + 0.5) / (len(ref) + 1.0)


def cauchy_combined_risk(
    tail_risk: dict[str, np.ndarray], names: tuple[str, ...]
) -> np.ndarray:
    p_values = np.stack(
        [
            np.clip(1.0 - np.asarray(tail_risk[name]), 1e-6, 1.0 - 1e-6)
            for name in names
        ],
        axis=1,
    )
    statistic = np.tan((0.5 - p_values) * np.pi).mean(axis=1)
    combined_p = 0.5 - np.arctan(statistic) / np.pi
    return np.clip(1.0 - combined_p, 0.0, 1.0)


def _safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    value = float(np.corrcoef(left, right)[0, 1])
    return value if np.isfinite(value) else 0.0


def _class_tail_features(risk_rank: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    classes = np.unique(labels)
    q95 = np.asarray([np.quantile(risk_rank[labels == value], 0.95) for value in classes])
    threshold = float(np.quantile(risk_rank, 0.95))
    rejection = np.asarray(
        [np.mean(risk_rank[labels == value] > threshold) for value in classes]
    )
    return float(np.std(q95)), float(np.std(rejection))


def validation_features(directory: Path) -> dict[str, float]:
    with np.load(directory / "scores.npz") as scores, np.load(
        directory / "evidence_package.npz"
    ) as evidence:
        labels = np.asarray(scores["validation_labels"])
        current = np.asarray(
            scores["validation_cauchy_modality_support_union"], dtype=np.float64
        )
        tails = {
            name: np.asarray(evidence[f"validation_tail_{name}"], dtype=np.float64)
            for name in COMPONENTS
        }
        cauchy = cauchy_combined_risk(tails, COMPONENTS)
    current_rank = empirical_percentile(current, current)
    cauchy_rank = empirical_percentile(cauchy, cauchy)
    current_q95_std, current_rejection_std = _class_tail_features(current_rank, labels)
    cauchy_q95_std, cauchy_rejection_std = _class_tail_features(cauchy_rank, labels)
    top_current = current_rank >= np.quantile(current_rank, 0.95)
    top_cauchy = cauchy_rank >= np.quantile(cauchy_rank, 0.95)
    union = int(np.sum(top_current | top_cauchy))
    overlap = float(np.sum(top_current & top_cauchy) / union) if union else 1.0
    return {
        "rank_correlation": _safe_corr(current_rank, cauchy_rank),
        "mean_absolute_rank_difference": float(np.mean(np.abs(current_rank - cauchy_rank))),
        "top5_jaccard": overlap,
        "current_class_q95_std": current_q95_std,
        "cauchy_class_q95_std": cauchy_q95_std,
        "class_q95_std_delta": cauchy_q95_std - current_q95_std,
        "current_class_rejection_std": current_rejection_std,
        "cauchy_class_rejection_std": cauchy_rejection_std,
        "class_rejection_std_delta": cauchy_rejection_std - current_rejection_std,
        "known_class_count": float(len(np.unique(labels))),
    }


def load_runs(roots: dict[str, Path], phase_spec: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    runs = []
    sources = []
    for phase, suites in phase_spec.items():
        root = roots[phase]
        for suite, scenarios in suites.items():
            for scenario, seeds in scenarios.items():
                for seed in seeds:
                    directory = root / suite / f"{scenario}_seed{seed}"
                    path = directory / "metrics.json"
                    raw = path.read_bytes()
                    metrics = json.loads(raw.decode("utf-8"))
                    reports = metrics.get("reports", {})
                    if REFERENCE not in reports or CAUCHY not in reports:
                        raise ValueError(f"router endpoints absent under {directory}")
                    details = metrics.get("risk_selection_details", {})
                    if phase != "pilot" and details.get(
                        "unknown_or_test_labels_used_for_selection"
                    ) is not False:
                        raise ValueError(f"runtime leakage guard failed under {directory}")
                    runs.append(
                        {
                            "phase": phase,
                            "suite": suite,
                            "scenario": scenario,
                            "seed": seed,
                            "features": validation_features(directory),
                            "reports": {
                                name: {
                                    metric: float(reports[name][metric])
                                    for metric in UNKNOWN_METRICS
                                }
                                for name in (REFERENCE, CAUCHY)
                            },
                        }
                    )
                    sources.append(
                        {
                            "phase": phase,
                            "path": path.relative_to(root).as_posix(),
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    )
    source_hash = hashlib.sha256(
        json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return runs, {
        "passes": True,
        "run_count": len(runs),
        "scenario_count": len({(run["suite"], run["scenario"]) for run in runs}),
        "source_metrics_combined_sha256": source_hash,
        "runtime_features_use_known_validation_only": True,
        "development_rule_selection_uses_test_unknown_labels": True,
    }


def make_rules(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feature_names = sorted(runs[0]["features"])
    rules = []
    for feature in feature_names:
        values = np.asarray([run["features"][feature] for run in runs], dtype=float)
        for quantile in QUANTILES:
            threshold = float(np.quantile(values, quantile))
            for operator in ("ge", "le"):
                rules.append(
                    {
                        "name": f"cauchy_if_{feature}_{operator}_q{int(quantile * 100):02d}",
                        "feature": feature,
                        "operator": operator,
                        "threshold": threshold,
                        "threshold_quantile": quantile,
                    }
                )
    names = [rule["name"] for rule in rules]
    if len(names) != len(set(names)):
        raise AssertionError("validation router rule names must be unique")
    return rules


def select_endpoint(rule: dict[str, Any], run: dict[str, Any]) -> str:
    value = float(run["features"][rule["feature"]])
    condition = value >= float(rule["threshold"])
    if rule["operator"] == "le":
        condition = value <= float(rule["threshold"])
    return CAUCHY if condition else REFERENCE


def rule_blocks(runs: list[dict[str, Any]], rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        grouped[(run["suite"], run["scenario"])].append(run)
    blocks = []
    for (suite, scenario), repeats in sorted(grouped.items()):
        deltas = {
            REFERENCE: {metric: 0.0 for metric in UNKNOWN_METRICS},
        }
        for rule in rules:
            deltas[rule["name"]] = {
                metric: float(
                    np.mean(
                        [
                            oriented_delta(
                                run["reports"][select_endpoint(rule, run)][metric],
                                run["reports"][REFERENCE][metric],
                                metric,
                            )
                            for run in repeats
                        ]
                    )
                )
                for metric in UNKNOWN_METRICS
            }
        blocks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed_count": len(repeats),
                "deltas": deltas,
            }
        )
    return blocks


def choose_rule(runs: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    rules = make_rules(runs)
    blocks = rule_blocks(runs, rules)
    result = screen(blocks, [REFERENCE, *[rule["name"] for rule in rules]])
    selected_name = result["selected_candidate"]
    selected = next((rule for rule in rules if rule["name"] == selected_name), None)
    return selected, result


def nested_loso(runs: list[dict[str, Any]]) -> dict[str, Any]:
    scenarios = sorted({(run["suite"], run["scenario"]) for run in runs})
    held_out_rows = []
    selected_paths: Counter[str] = Counter()
    for suite, scenario in scenarios:
        train = [
            run
            for run in runs
            if (run["suite"], run["scenario"]) != (suite, scenario)
        ]
        held_out = [
            run
            for run in runs
            if (run["suite"], run["scenario"]) == (suite, scenario)
        ]
        rule, _ = choose_rule(train)
        selected_paths[rule["name"] if rule else "fallback_current"] += 1
        gains = {}
        for metric in UNKNOWN_METRICS:
            values = []
            for run in held_out:
                endpoint = select_endpoint(rule, run) if rule else REFERENCE
                values.append(
                    oriented_delta(
                        run["reports"][endpoint][metric],
                        run["reports"][REFERENCE][metric],
                        metric,
                    )
                )
            gains[metric] = float(np.mean(values))
        held_out_rows.append(
            {"suite": suite, "scenario": scenario, "selected_rule": rule, "gains": gains}
        )
    combined = {
        metric: float(np.mean([row["gains"][metric] for row in held_out_rows]))
        for metric in UNKNOWN_METRICS
    }
    by_suite = {
        suite: {
            metric: float(
                np.mean(
                    [
                        row["gains"][metric]
                        for row in held_out_rows
                        if row["suite"] == suite
                    ]
                )
            )
            for metric in UNKNOWN_METRICS
        }
        for suite in sorted({row["suite"] for row in held_out_rows})
    }
    passes = all(value > 0.0 for value in combined.values()) and all(
        value >= -0.005 for values in by_suite.values() for value in values.values()
    )
    return {
        "inference_unit": "held-out scenario",
        "combined": combined,
        "by_suite": by_suite,
        "selected_paths": dict(selected_paths),
        "folds": held_out_rows,
        "passes": passes,
    }


def markdown(report: dict[str, Any]) -> str:
    full = report["full_development"]
    nested = report["nested_loso"]
    lines = [
        "# Strict-v4 known-validation router development analysis",
        "",
        f"Runs: {report['validation']['run_count']}; scenarios: {report['validation']['scenario_count']}.",
        f"Full-development rule: `{full['selected_rule_name']}`.",
        f"Freeze candidate: **{str(report['freeze_candidate']).lower()}**.",
        "Runtime inputs use known-validation only; development rule selection uses opened unknown test labels.",
        "",
        "| Nested LOSO | AUROC | AUPR | FPR95 oriented | OSCR |",
        "|---|---:|---:|---:|---:|",
        (
            f"| Combined gain | {nested['combined']['unknown_auroc']:+.6f} | "
            f"{nested['combined']['unknown_aupr']:+.6f} | "
            f"{nested['combined']['unknown_fpr95']:+.6f} | "
            f"{nested['combined']['oscr']:+.6f} |"
        ),
        "",
        f"Nested selected paths: `{nested['selected_paths']}`.",
    ]
    return "\n".join(lines) + "\n"


def canonical_hash(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_manifest(report: dict[str, Any], phase_spec: dict[str, Any]) -> dict[str, Any]:
    selected = report["full_development"]["selected_rule"]
    frozen = bool(report["freeze_candidate"] and selected)
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_validation_router_candidate_v1",
        "status": "frozen_unconfirmed" if frozen else "no_candidate",
        "frozen_before_confirmation": frozen,
        "candidate": {
            "name": "known_validation_class_tail_router_v1",
            "selected_rule": selected if frozen else None,
            "candidate_endpoint": CAUCHY,
            "fallback_endpoint": REFERENCE,
            "runtime_features_use_known_validation_only": True,
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "development": {
            "phases": phase_spec,
            "run_count": report["validation"]["run_count"],
            "scenario_count": report["validation"]["scenario_count"],
            "source_metrics_combined_sha256": report["validation"][
                "source_metrics_combined_sha256"
            ],
            "rule_selection_uses_test_unknown_labels": True,
            "nested_loso": report["nested_loso"],
        },
        "confirmation": {
            **CONFIRMATION,
            "expected_run_count": sum(
                len(values) for values in CONFIRMATION["scenarios"].values()
            )
            * len(CONFIRMATION["seeds"]),
            "seed_disjoint": True,
            "scenario_boundary": {
                "cic_iot2023": "unseen_attack_scenarios_and_unseen_seeds",
                "cic_ton_iot": "all_attack_scenarios_cross_seed_replication",
            },
        },
        "confirmation_gate": {
            "unit": "scenario mean across confirmation seeds",
            "combined_unknown_auroc_mean_improvement_required": True,
            "combined_unknown_auroc_bootstrap_ci_lower_gt_zero": True,
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


def analyze(runs: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    selected, screening = choose_rule(runs)
    nested = nested_loso(runs)
    freeze = selected is not None and nested["passes"]
    return {
        "schema_version": "strict_v4_known_validation_router_development_v1",
        "status": "freeze_candidate" if freeze else "rejected_development_candidate",
        "freeze_candidate": freeze,
        "validation": validation,
        "full_development": {
            "selected_rule": selected,
            "selected_rule_name": selected["name"] if selected else None,
            "screening": screening,
        },
        "nested_loso": nested,
    }


def main() -> None:
    from analyze_strict_v4_entropy_cauchy_fusion import PHASES

    parser = argparse.ArgumentParser(
        description="Develop a known-validation-only strict-v4 endpoint router"
    )
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--confirmation-v1-root", type=Path, required=True)
    parser.add_argument("--confirmation-v2-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    runs, validation = load_runs(
        {
            "pilot": args.pilot_root,
            "confirmation_v1": args.confirmation_v1_root,
            "confirmation_v2": args.confirmation_v2_root,
        },
        PHASES,
    )
    report = analyze(runs, validation)
    manifest = build_manifest(report, PHASES)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(markdown(report), encoding="utf-8")
    (args.output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "selected_rule": report["full_development"]["selected_rule_name"],
                "nested_loso": report["nested_loso"]["combined"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
