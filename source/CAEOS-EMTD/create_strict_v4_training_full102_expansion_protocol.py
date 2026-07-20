from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


GROUPS = {
    "complementary": {
        "pilot_schema": "strict_v4_complementary_training_pilot_protocol_v1",
        "analysis_schema": "strict_v4_complementary_training_pilot_analysis_v1",
        "allowed_methods": {"arpl", "palm", "ronetc", "foss"},
        "runner": "run_neural_baseline_matrix.py",
    },
    "aegis": {
        "pilot_schema": "strict_v4_aegis_training_pilot_protocol_v1",
        "analysis_schema": "strict_v4_aegis_training_pilot_analysis_v1",
        "allowed_methods": {"aegis_clean_adapter"},
        "runner": "run_aegis_baseline_matrix.py",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object: %s" % path)
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scenario_registry(coverage: dict[str, Any]) -> dict[str, list[str]]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage schema")
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("strict-v4 coverage SHA mismatch")
    registry = {
        suite: list(details.get("scenarios", []))
        for suite, details in coverage.get("scenario_registry", {}).items()
    }
    if sum(map(len, registry.values())) != 102 or len(registry) != 7:
        raise ValueError("full102 coverage must contain 7 suites and 102 scenarios")
    if any(not scenarios or len(scenarios) != len(set(scenarios)) for scenarios in registry.values()):
        raise ValueError("invalid or duplicate scenario registry")
    return registry


def create_protocol(
    group: str,
    coverage: dict[str, Any],
    pilot_protocol: dict[str, Any],
    pilot_analysis: dict[str, Any],
    pilot_analysis_sha256: str,
    project_root: Path,
    observed_metrics: int,
) -> dict[str, Any]:
    settings = GROUPS[group]
    if observed_metrics != 0:
        raise ValueError("full102 expansion protocol must be frozen at zero results")
    if pilot_protocol.get("schema_version") != settings["pilot_schema"]:
        raise ValueError("unexpected pilot protocol schema")
    if pilot_protocol.get("manifest_sha256") != canonical_hash(pilot_protocol):
        raise ValueError("pilot protocol SHA mismatch")
    if pilot_analysis.get("schema_version") != settings["analysis_schema"]:
        raise ValueError("unexpected pilot analysis schema")
    if pilot_analysis.get("status") != "complete":
        raise ValueError("pilot analysis is incomplete")
    if pilot_analysis.get("pilot_protocol_manifest_sha256") != pilot_protocol.get(
        "manifest_sha256"
    ):
        raise ValueError("pilot analysis/protocol binding mismatch")
    candidates = list(pilot_analysis.get("expand_to_full102", []))
    if not candidates or len(candidates) != len(set(candidates)):
        raise ValueError("pilot analysis does not require a unique full102 candidate set")
    if not set(candidates) <= settings["allowed_methods"]:
        raise ValueError("unsupported full102 candidate")
    decisions = pilot_analysis.get("candidate_decisions", {})
    if not all(decisions.get(method, {}).get("expand_to_full102") is True for method in candidates):
        raise ValueError("candidate decision does not require full102")

    implementations = dict(pilot_protocol.get("implementation_sha256", {}))
    if settings["runner"] not in implementations:
        raise ValueError("pilot protocol does not bind the required runner")
    for name, expected in implementations.items():
        if file_hash(project_root / name) != expected:
            raise ValueError("pilot-bound implementation changed: %s" % name)

    registry = scenario_registry(coverage)
    result = {
        "schema_version": "strict_v4_training_full102_expansion_protocol_v1",
        "status": "frozen_before_full102_results",
        "group": group,
        "scope": "development_full102_followup_required_by_prefrozen_pilot_gate",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
        "pilot_analysis_sha256": pilot_analysis_sha256,
        "scenario_registry": registry,
        "seed": 7,
        "methods": candidates,
        "expected_scenarios": 102,
        "expected_runs": 102 * len(candidates),
        "fit_data": "known_training_only",
        "checkpoint_and_threshold_data": "known_validation_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "comparison_reference": "opendetect_on_identical_frozen_seed7_splits",
        "implementation_sha256": implementations,
        "full102_metrics_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def freeze_or_validate_protocol(
    output: Path, expected: dict[str, Any], observed_metrics: int
) -> dict[str, Any]:
    if output.is_file():
        existing = read_json(output)
        if existing != expected:
            raise ValueError("existing full102 protocol differs from current bound evidence")
        return existing
    if observed_metrics != 0:
        raise ValueError("full102 expansion protocol must be frozen at zero results")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", choices=tuple(GROUPS), required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--expansion-root", type=Path, required=True)
    args = parser.parse_args()

    output = args.expansion_root / "protocol_manifest.json"
    pilot_analysis = read_json(args.pilot_analysis)
    expected = create_protocol(
        args.group,
        read_json(args.coverage),
        read_json(args.pilot_protocol),
        pilot_analysis,
        canonical_hash(pilot_analysis),
        args.project_root.resolve(),
        0,
    )
    observed = (
        len(list(args.expansion_root.glob("*/*/metrics.json")))
        if args.expansion_root.is_dir()
        else 0
    )
    protocol = freeze_or_validate_protocol(output, expected, observed)
    if protocol.get("group") != args.group:
        raise ValueError("existing full102 protocol group mismatch")
    print(json.dumps({"protocol": protocol["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
