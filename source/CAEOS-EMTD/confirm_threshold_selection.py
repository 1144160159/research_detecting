from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Confirm a frozen threshold target")
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--confirmation-sensitivity", required=True)
    parser.add_argument("--confirmation-seeds", required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260716)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def confirm(
    selection: dict[str, object],
    sensitivity: dict[str, object],
    confirmation_seeds: tuple[int, ...],
    repetitions: int,
    bootstrap_seed: int,
) -> dict[str, object]:
    if selection.get("purpose") != "development_only_threshold_selection":
        raise ValueError("selection manifest is not development-only")
    if selection.get("eligible_for_confirmation_or_final_metrics") is not False:
        raise ValueError("development selection must be ineligible for final metrics")
    development_seeds = {int(seed) for seed in selection["development_seeds"]}
    overlap = sorted(development_seeds & set(confirmation_seeds))
    if overlap:
        raise ValueError(f"development/confirmation seed overlap: {overlap}")
    if tuple(int(seed) for seed in sensitivity.get("seeds", [])) != confirmation_seeds:
        raise ValueError("confirmation sensitivity seed mismatch")
    if not sensitivity.get("coverage_validated"):
        raise ValueError("confirmation sensitivity coverage is not validated")
    if sensitivity.get("risk") != selection.get("risk"):
        raise ValueError("risk mismatch between selection and confirmation")
    target = float(selection["selected_target_known_acceptance"])
    key = str(target)
    if key not in sensitivity["acceptances"]:
        raise ValueError(f"selected target {target} missing from confirmation")
    selected = sensitivity["acceptances"][key]
    scenario_rows = selected["by_scenario"]
    if len(scenario_rows) != int(sensitivity["scenario_count"]):
        raise ValueError("confirmation scenario coverage mismatch")
    values = np.asarray(
        [row["metrics"]["known_acceptance_rate"] for row in scenario_rows],
        dtype=np.float64,
    )
    if repetitions < 100:
        raise ValueError("bootstrap repetitions must be at least 100")
    rng = np.random.default_rng(bootstrap_seed)
    indices = rng.integers(0, len(values), size=(repetitions, len(values)))
    means = values[indices].mean(axis=1)
    lower, upper = np.percentile(means, [2.5, 97.5])
    observed = float(values.mean())
    minimum = float(selection["minimum_test_known_acceptance"])
    reported = float(selected["scenario_mean"]["known_acceptance_rate"])
    if not np.isclose(observed, reported, atol=1e-12, rtol=0.0):
        raise ValueError("reported confirmation mean does not match scenario rows")
    return {
        "purpose": "independent_threshold_confirmation",
        "confirmation_passes": observed >= minimum,
        "selected_target_known_acceptance": target,
        "minimum_test_known_acceptance": minimum,
        "observed_test_known_acceptance": observed,
        "bootstrap_95_ci": {
            "method": "percentile_scenario_block_bootstrap",
            "repetitions": repetitions,
            "seed": bootstrap_seed,
            "lower": float(lower),
            "upper": float(upper),
        },
        "bootstrap_lower_bound_meets_minimum": float(lower) >= minimum,
        "unknown_rejection_rate": float(
            selected["scenario_mean"]["unknown_rejection_rate"]
        ),
        "unknown_f1": float(selected["scenario_mean"]["unknown_f1"]),
        "risk": selection["risk"],
        "development_seeds": sorted(development_seeds),
        "confirmation_seeds": list(confirmation_seeds),
        "seed_overlap": [],
        "scenario_count": len(scenario_rows),
        "seed_repeats_are_averaged_within_scenario": True,
    }


def main() -> None:
    args = parse_arguments()
    selection_path = Path(args.selection_manifest)
    sensitivity_path = Path(args.confirmation_sensitivity)
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    sensitivity = json.loads(sensitivity_path.read_text(encoding="utf-8"))
    confirmation_seeds = tuple(
        int(token.strip())
        for token in args.confirmation_seeds.split(",")
        if token.strip()
    )
    if not confirmation_seeds or len(confirmation_seeds) != len(set(confirmation_seeds)):
        raise ValueError("confirmation seeds must be unique and non-empty")
    report = confirm(
        selection,
        sensitivity,
        confirmation_seeds,
        args.bootstrap_repetitions,
        args.bootstrap_seed,
    )
    report["selection_manifest"] = str(selection_path)
    report["selection_manifest_sha256"] = sha256(selection_path)
    report["confirmation_sensitivity"] = str(sensitivity_path)
    report["confirmation_sensitivity_sha256"] = sha256(sensitivity_path)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
