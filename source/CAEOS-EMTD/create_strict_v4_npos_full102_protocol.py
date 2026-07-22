from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from create_strict_v4_npos_pilot_protocol import load_json, source_record


def create_protocol(
    coverage: dict[str, Any],
    pilot_protocol: dict[str, Any],
    pilot_analysis: dict[str, Any],
    project_root: Path,
    mlp_root: Path,
    comparator_root: Path,
    observed_metrics: int,
) -> dict[str, Any]:
    if (
        coverage.get("schema_version") != "strict_v4_coverage_manifest_v2"
        or coverage.get("manifest_sha256") != canonical_hash(coverage)
    ):
        raise ValueError("NPOS full102 coverage validation failed")
    if (
        pilot_protocol.get("schema_version") != "strict_v4_npos_pilot_protocol_v1"
        or pilot_protocol.get("manifest_sha256") != canonical_hash(pilot_protocol)
        or pilot_analysis.get("schema_version") != "strict_v4_npos_pilot_analysis_v1"
        or pilot_analysis.get("manifest_sha256") != canonical_hash(pilot_analysis)
        or pilot_analysis.get("protocol_manifest_sha256")
        != pilot_protocol["manifest_sha256"]
        or pilot_analysis.get("decision", {}).get("expand_to_full102") is not True
    ):
        raise ValueError("NPOS full102 requires a passing frozen pilot")
    if observed_metrics != 0:
        raise ValueError("NPOS full102 protocol must freeze before full results")
    for name, expected in pilot_protocol["implementation_sha256"].items():
        if name == "protocol_creator":
            continue
        path = project_root / name
        if file_hash(path) != expected:
            raise ValueError(f"NPOS implementation changed after pilot freeze: {name}")
    registry = coverage.get("scenario_registry", {})
    sources = [
        source_record(mlp_root, comparator_root, suite, scenario)
        for suite in sorted(registry)
        for scenario in registry[suite]["scenarios"]
    ]
    if len(sources) != 102:
        raise ValueError("NPOS full102 source registry is incomplete")
    protocol = {
        "schema_version": "strict_v4_npos_full102_protocol_v1",
        "status": "frozen_after_passing_pilot_before_full102_results",
        "scope": "development_full102_strong_baseline_screen",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
        "pilot_analysis_manifest_sha256": pilot_analysis["manifest_sha256"],
        "source_registry": sources,
        "source_registry_count": 102,
        "seed": 7,
        "method": "npos_knn",
        "reference_methods": ["opendetect", "mlp_knn"],
        "expected_runs": 102,
        "official_source": pilot_protocol["official_source"],
        "frozen_hyperparameters": pilot_protocol["frozen_hyperparameters"],
        "adaptation_disclosure": pilot_protocol["adaptation_disclosure"],
        "fit_data": "known_training_only",
        "threshold_data": "known_validation_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "implementation_sha256": {
            name: expected
            for name, expected in pilot_protocol["implementation_sha256"].items()
            if name != "protocol_creator"
        },
        "full102_metrics_observed_at_freeze": 0,
    }
    protocol["full102_protocol_creator_sha256"] = file_hash(Path(__file__))
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--comparator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    observed = len(list(args.run_root.glob("*/*_seed7_npos/metrics.json"))) if args.run_root.exists() else 0
    protocol = create_protocol(
        load_json(args.coverage),
        load_json(args.pilot_protocol),
        load_json(args.pilot_analysis),
        args.project_root.resolve(),
        args.mlp_root.resolve(),
        args.comparator_root.resolve(),
        observed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / "protocol_manifest.json"
    if path.is_file() and load_json(path) != protocol:
        raise ValueError("existing frozen NPOS full102 protocol differs")
    if not path.is_file():
        path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "protocol_complete").touch()
    print(json.dumps({"manifest_sha256": protocol["manifest_sha256"], "runs": 102}, sort_keys=True))


if __name__ == "__main__":
    main()
