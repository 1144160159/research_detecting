from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze a known-acceptance target from development-only sensitivity"
    )
    parser.add_argument("--sensitivity", required=True)
    parser.add_argument("--minimum-test-known-acceptance", type=float, required=True)
    parser.add_argument("--expected-development-seeds", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_target(
    report: dict[str, object],
    minimum_test_known_acceptance: float,
    expected_development_seeds: tuple[int, ...],
) -> dict[str, object]:
    if not 0.0 < minimum_test_known_acceptance < 1.0:
        raise ValueError("minimum test known acceptance must be in (0, 1)")
    observed_seeds = tuple(int(seed) for seed in report.get("seeds", []))
    if observed_seeds != expected_development_seeds:
        raise ValueError(
            f"development seed mismatch: expected {expected_development_seeds}, "
            f"observed {observed_seeds}"
        )
    if not report.get("coverage_validated"):
        raise ValueError("sensitivity coverage was not validated")
    candidates = []
    for key, item in report["acceptances"].items():
        target = float(item["target_known_acceptance"])
        observed = float(item["scenario_mean"]["known_acceptance_rate"])
        candidates.append(
            {
                "target_known_acceptance": target,
                "development_test_known_acceptance": observed,
                "eligible": observed >= minimum_test_known_acceptance,
            }
        )
    eligible = [item for item in candidates if item["eligible"]]
    if not eligible:
        raise ValueError("no threshold target meets the development constraint")
    selected = min(eligible, key=lambda item: item["target_known_acceptance"])
    return {
        "purpose": "development_only_threshold_selection",
        "eligible_for_confirmation_or_final_metrics": False,
        "selection_rule": (
            "smallest validation known-acceptance target whose scenario-mean "
            "development test known acceptance meets the fixed minimum"
        ),
        "minimum_test_known_acceptance": minimum_test_known_acceptance,
        "selected_target_known_acceptance": selected["target_known_acceptance"],
        "selected_development_test_known_acceptance": selected[
            "development_test_known_acceptance"
        ],
        "development_seeds": list(expected_development_seeds),
        "risk": report["risk"],
        "grid": sorted(candidates, key=lambda item: item["target_known_acceptance"]),
        "confirmation_requirement": (
            "use seeds and artifacts disjoint from development and earlier confirmation"
        ),
    }


def main() -> None:
    args = parse_arguments()
    sensitivity_path = Path(args.sensitivity)
    report = json.loads(sensitivity_path.read_text(encoding="utf-8"))
    expected_seeds = tuple(
        int(token.strip())
        for token in args.expected_development_seeds.split(",")
        if token.strip()
    )
    if not expected_seeds or len(expected_seeds) != len(set(expected_seeds)):
        raise ValueError("expected development seeds must be unique and non-empty")
    manifest = select_target(
        report, args.minimum_test_known_acceptance, expected_seeds
    )
    manifest["sensitivity_artifact"] = str(sensitivity_path)
    manifest["sensitivity_sha256"] = sha256(sensitivity_path)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
