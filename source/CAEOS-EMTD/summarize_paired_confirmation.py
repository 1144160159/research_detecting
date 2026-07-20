from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.stats import rankdata, wilcoxon


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)
INFERENCE_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
LOWER_IS_BETTER = {"unknown_fpr95"}
REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize a frozen CAEOS candidate confirmation using scenarios as "
            "the independent inference units"
        )
    )
    parser.add_argument("--reference-root", required=True)
    parser.add_argument("--candidate-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--expected-scenarios", type=int, required=True)
    parser.add_argument("--candidate-risk-policy", required=True)
    parser.add_argument("--reference-risk-policy", required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260716)
    return parser.parse_args()


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=lambda name: (p_values[name], name))
    adjusted: dict[str, float] = {}
    running_max = 0.0
    hypotheses = len(ordered)
    for rank, name in enumerate(ordered):
        candidate = min(1.0, (hypotheses - rank) * p_values[name])
        running_max = max(running_max, candidate)
        adjusted[name] = running_max
    return adjusted


def stable_bootstrap_seed(base_seed: int, metric: str) -> int:
    digest = hashlib.sha256(f"{base_seed}|{metric}".encode("utf-8")).digest()
    return (base_seed + int.from_bytes(digest[:8], "little")) % (2**63 - 1)


def bootstrap_ci(
    values: Iterable[float], repetitions: int, seed: int
) -> dict[str, object]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.size == 0:
        raise ValueError("cannot bootstrap zero scenario blocks")
    if repetitions < 100:
        raise ValueError("bootstrap repetitions must be at least 100")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, array.size, size=(repetitions, array.size))
    means = array[indices].mean(axis=1)
    lower, upper = np.percentile(means, [2.5, 97.5])
    return {
        "method": "percentile_scenario_block_bootstrap",
        "confidence_level": 0.95,
        "repetitions": repetitions,
        "seed": int(seed),
        "lower": float(lower),
        "upper": float(upper),
    }


def effect_sizes(values: Iterable[float]) -> dict[str, dict[str, object]]:
    array = np.asarray(list(values), dtype=np.float64)
    nonzero = array[np.abs(array) > 1e-12]
    if array.size < 2:
        cohen = {"value": None, "status": "undefined_fewer_than_two_pairs"}
    else:
        standard_deviation = float(array.std(ddof=1))
        if standard_deviation <= 1e-15:
            cohen = {"value": None, "status": "undefined_zero_variance"}
        else:
            cohen = {
                "value": float(array.mean() / standard_deviation),
                "status": "computed",
            }
    if nonzero.size == 0:
        rank_biserial = {"value": 0.0, "status": "all_ties"}
    else:
        ranks = rankdata(np.abs(nonzero), method="average")
        positive = float(ranks[nonzero > 0].sum())
        negative = float(ranks[nonzero < 0].sum())
        rank_biserial = {
            "value": (positive - negative) / (positive + negative),
            "status": "computed",
        }
    return {
        "paired_cohens_dz": cohen,
        "matched_pairs_rank_biserial": rank_biserial,
    }


def paired_wilcoxon(values: Iterable[float]) -> dict[str, object]:
    array = np.asarray(list(values), dtype=np.float64)
    nonzero = array[np.abs(array) > 1e-12]
    if nonzero.size == 0:
        return {
            "statistic": 0.0,
            "raw_p_value": 1.0,
            "holm_adjusted_p_value": None,
            "nonzero_pairs": 0,
            "status": "all_ties",
        }
    result = wilcoxon(nonzero, alternative="two-sided")
    return {
        "statistic": float(result.statistic),
        "raw_p_value": float(result.pvalue),
        "holm_adjusted_p_value": None,
        "nonzero_pairs": int(nonzero.size),
        "status": "computed",
    }


def task_key(path: Path, root: Path) -> tuple[str, str, int]:
    relative = path.relative_to(root)
    if len(relative.parts) != 3 or relative.name != "metrics.json":
        raise ValueError(f"unexpected metrics path: {path}")
    suite = relative.parts[0]
    run = relative.parts[1]
    if "_seed" not in run:
        raise ValueError(f"run directory has no seed suffix: {path.parent}")
    scenario, seed_text = run.rsplit("_seed", 1)
    return suite, scenario, int(seed_text)


def load_root(root: Path) -> dict[tuple[str, str, int], dict[str, object]]:
    runs: dict[tuple[str, str, int], dict[str, object]] = {}
    for path in sorted(root.glob("*/*/metrics.json")):
        key = task_key(path, root)
        if key in runs:
            raise ValueError(f"duplicate task under {root}: {key}")
        missing = [name for name in REQUIRED_ARTIFACTS if not (path.parent / name).exists()]
        if missing:
            raise ValueError(f"missing artifacts for {key} under {root}: {missing}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        runs[key] = {"path": path, "payload": payload}
    if not runs:
        raise ValueError(f"no metrics found under {root}")
    return runs


def validate_coverage(
    runs: dict[tuple[str, str, int], dict[str, object]],
    seeds: set[int],
    expected_scenarios: int,
    label: str,
) -> None:
    grouped: dict[tuple[str, str], set[int]] = defaultdict(set)
    for suite, scenario, seed in runs:
        grouped[(suite, scenario)].add(seed)
    if len(grouped) != expected_scenarios:
        raise ValueError(
            f"{label} scenario coverage mismatch: expected {expected_scenarios}, "
            f"found {len(grouped)}"
        )
    mismatched = {
        f"{suite}/{scenario}": sorted(observed)
        for (suite, scenario), observed in grouped.items()
        if observed != seeds
    }
    if mismatched:
        raise ValueError(
            f"{label} seed coverage mismatch: expected {sorted(seeds)}, "
            f"observed {mismatched}"
        )


def split_fingerprint(payload: dict[str, object]) -> dict[str, object]:
    metadata = payload.get("split_metadata", {})
    fingerprint = metadata.get("split_fingerprint") if isinstance(metadata, dict) else None
    if not isinstance(fingerprint, dict) or not fingerprint.get("combined"):
        raise ValueError("metrics payload has no complete split fingerprint")
    return fingerprint


def build_rows(
    reference_root: Path,
    candidate_root: Path,
    seeds: set[int],
    expected_scenarios: int,
    candidate_risk_policy: str,
    reference_risk_policy: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    reference = load_root(reference_root)
    candidate = load_root(candidate_root)
    validate_coverage(reference, seeds, expected_scenarios, "reference")
    validate_coverage(candidate, seeds, expected_scenarios, "candidate")
    if set(reference) != set(candidate):
        missing_reference = sorted(set(candidate) - set(reference))
        missing_candidate = sorted(set(reference) - set(candidate))
        raise ValueError(
            "paired task mismatch: "
            f"missing_reference={missing_reference}, missing_candidate={missing_candidate}"
        )
    rows: list[dict[str, object]] = []
    split_checks = 0
    for key in sorted(candidate):
        reference_payload = reference[key]["payload"]
        candidate_payload = candidate[key]["payload"]
        if candidate_payload.get("risk_policy") != candidate_risk_policy:
            raise ValueError(
                f"candidate risk policy mismatch for {key}: "
                f"{candidate_payload.get('risk_policy')!r}"
            )
        if reference_payload.get("risk_policy") != reference_risk_policy:
            raise ValueError(
                f"reference risk policy mismatch for {key}: "
                f"{reference_payload.get('risk_policy')!r}"
            )
        details = candidate_payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"candidate selection leakage guard failed for {key}")
        reference_details = reference_payload.get("risk_selection_details", {})
        if reference_details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"reference selection leakage guard failed for {key}")
        candidate_split = split_fingerprint(candidate_payload)
        reference_split = split_fingerprint(reference_payload)
        if candidate_split != reference_split:
            raise ValueError(f"split fingerprint mismatch for {key}")
        split_checks += 1
        candidate_report = candidate_payload.get("selected_report", {})
        reference_report = reference_payload.get("selected_report", {})
        for metric in METRICS:
            if metric not in candidate_report or metric not in reference_report:
                raise ValueError(f"missing metric {metric!r} for {key}")
        suite, scenario, seed = key
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": candidate_payload.get("selected_risk"),
                "reference_selected": reference_payload.get("selected_risk"),
                "candidate_report": candidate_report,
                "reference_report": reference_report,
                "split_fingerprint": candidate_split["combined"],
            }
        )
    return rows, {
        "paired_tasks": len(rows),
        "expected_seeds": sorted(seeds),
        "expected_scenarios": expected_scenarios,
        "task_sets_identical": True,
        "split_fingerprint_pair_checks": split_checks,
        "split_fingerprints_identical": True,
        "candidate_selection_uses_unknown_or_test_labels": False,
        "reference_selection_uses_unknown_or_test_labels": False,
    }


def aggregate(
    rows: list[dict[str, object]],
    bootstrap_repetitions: int,
    bootstrap_seed: int,
) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[f"{row['suite']}/{row['scenario']}"] .append(row)
    result: dict[str, object] = {
        "inference_unit": "scenario",
        "scenario_count": len(grouped),
        "seed_repeats_are_averaged_within_scenario": True,
        "primary_metric": "unknown_auroc",
        "holm_family": list(INFERENCE_METRICS),
        "candidate_selected_paths": dict(
            Counter(str(row["candidate_selected"]) for row in rows)
        ),
        "reference_selected_paths": dict(
            Counter(str(row["reference_selected"]) for row in rows)
        ),
        "metrics": {},
    }
    raw_p_values: dict[str, float] = {}
    for metric in METRICS:
        direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
        reference_means: list[float] = []
        candidate_means: list[float] = []
        raw_deltas: list[float] = []
        oriented_deltas: list[float] = []
        scenario_rows: list[dict[str, object]] = []
        for scenario, items in sorted(grouped.items()):
            reference_mean = float(
                np.mean([row["reference_report"][metric] for row in items])
            )
            candidate_mean = float(
                np.mean([row["candidate_report"][metric] for row in items])
            )
            raw_delta = candidate_mean - reference_mean
            oriented_delta = direction * raw_delta
            reference_means.append(reference_mean)
            candidate_means.append(candidate_mean)
            raw_deltas.append(raw_delta)
            oriented_deltas.append(oriented_delta)
            scenario_rows.append(
                {
                    "scenario": scenario,
                    "seed_count": len(items),
                    "reference_mean": reference_mean,
                    "candidate_mean": candidate_mean,
                    "raw_delta": raw_delta,
                    "oriented_improvement": oriented_delta,
                }
            )
        oriented_array = np.asarray(oriented_deltas, dtype=np.float64)
        wilcoxon_report = paired_wilcoxon(oriented_deltas)
        if metric in INFERENCE_METRICS:
            raw_p_values[metric] = float(wilcoxon_report["raw_p_value"])
        result["metrics"][metric] = {
            "direction": "lower_is_better" if direction < 0 else "higher_is_better",
            "reference_scenario_mean": float(np.mean(reference_means)),
            "candidate_scenario_mean": float(np.mean(candidate_means)),
            "raw_mean_delta": float(np.mean(raw_deltas)),
            "oriented_mean_improvement": float(oriented_array.mean()),
            "wins": int((oriented_array > 1e-12).sum()),
            "ties": int((np.abs(oriented_array) <= 1e-12).sum()),
            "losses": int((oriented_array < -1e-12).sum()),
            "bootstrap_95_ci": bootstrap_ci(
                oriented_deltas,
                bootstrap_repetitions,
                stable_bootstrap_seed(bootstrap_seed, metric),
            ),
            "effect_sizes": effect_sizes(oriented_deltas),
            "wilcoxon": wilcoxon_report,
            "scenario_blocks": scenario_rows,
        }
    adjusted = holm_adjust(raw_p_values)
    for metric, adjusted_p in adjusted.items():
        result["metrics"][metric]["wilcoxon"][
            "holm_adjusted_p_value"
        ] = adjusted_p
    auroc = result["metrics"]["unknown_auroc"]
    aupr = result["metrics"]["unknown_aupr"]
    fpr95 = result["metrics"]["unknown_fpr95"]
    oscr = result["metrics"]["oscr"]
    mean_safety = {
        "auroc_improves": auroc["oriented_mean_improvement"] > 0.0,
        "aupr_nonregression": aupr["oriented_mean_improvement"] >= 0.0,
        "oscr_nonregression": oscr["oriented_mean_improvement"] >= 0.0,
        "fpr95_raw_regression_at_most_0_01": fpr95["raw_mean_delta"] <= 0.01,
    }
    mean_safety["passes"] = all(mean_safety.values())
    result["decision"] = {
        "mean_safety_gate": mean_safety,
        "primary_bootstrap_ci_excludes_zero": auroc["bootstrap_95_ci"]["lower"] > 0.0,
        "primary_holm_p_below_0_05": auroc["wilcoxon"][
            "holm_adjusted_p_value"
        ]
        < 0.05,
    }
    result["decision"]["confirmatory_evidence_passes"] = bool(
        mean_safety["passes"]
        and result["decision"]["primary_bootstrap_ci_excludes_zero"]
        and result["decision"]["primary_holm_p_below_0_05"]
    )
    return result


def markdown(report: dict[str, object]) -> str:
    summary = report["scenario_blocked_inference"]
    lines = [
        "# Frozen candidate confirmation",
        "",
        f"Paired runs: {report['validation']['paired_tasks']}; "
        f"inference units: {summary['scenario_count']} scenarios.",
        "Seed repeats are averaged within scenarios before inference.",
        "",
        "| Metric | Reference | Candidate | Oriented improvement | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = summary["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        adjusted = item["wilcoxon"]["holm_adjusted_p_value"]
        adjusted_text = "NA" if adjusted is None else f"{adjusted:.3g}"
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{item['wins']}/{item['ties']}/{item['losses']} | {adjusted_text} |"
        )
    decision = summary["decision"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Mean safety gate: **{'PASS' if decision['mean_safety_gate']['passes'] else 'FAIL'}**",
            f"Confirmatory evidence: **{'PASS' if decision['confirmatory_evidence_passes'] else 'FAIL'}**",
            "",
            "The confirmatory gate requires positive AUROC, non-regressing AUPR/OSCR, "
            "FPR95 raw regression no greater than 0.01, a positive AUROC bootstrap lower "
            "bound, and Holm-adjusted AUROC p < 0.05.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    seeds = {int(value) for value in args.seeds.split(",") if value.strip()}
    if not seeds:
        raise ValueError("at least one confirmation seed is required")
    rows, validation = build_rows(
        Path(args.reference_root),
        Path(args.candidate_root),
        seeds,
        args.expected_scenarios,
        args.candidate_risk_policy,
        args.reference_risk_policy,
    )
    report = {
        "reference_root": args.reference_root,
        "candidate_root": args.candidate_root,
        "validation": validation,
        "scenario_blocked_inference": aggregate(
            rows, args.bootstrap_repetitions, args.bootstrap_seed
        ),
        "runs": rows,
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "confirmation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "confirmation.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["scenario_blocked_inference"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
