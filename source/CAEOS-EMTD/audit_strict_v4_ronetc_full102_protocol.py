from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from run_nested_gate_matrix import (
    CICIDS2017_SCENARIOS,
    CIC_IOT2023_SCENARIOS,
    CIC_TON_IOT_SCENARIOS,
    EDGE_IIOT_SCENARIOS,
    NF_CSE_SCENARIOS,
    NF_UNSW_SCENARIOS,
    USTC_TFC2016_SCENARIOS,
)


SUITES = {
    "nf_unsw": NF_UNSW_SCENARIOS,
    "cicids2017": CICIDS2017_SCENARIOS,
    "cic_iot2023": CIC_IOT2023_SCENARIOS,
    "cic_ton_iot": CIC_TON_IOT_SCENARIOS,
    "edge_iiot": EDGE_IIOT_SCENARIOS,
    "nf_cse": NF_CSE_SCENARIOS,
    "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
}
REQUIRED_IMPLEMENTATION = (
    "create_strict_v4_ronetc_full102_protocol.py",
    "run_neural_baseline_matrix.py",
    "train_neural_open_set.py",
    "caeos/ronetc.py",
    "summarize_strict_v4_ronetc_full102.py",
    "audit_strict_v4_ronetc_full102.py",
)
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")
CACHE_ARGUMENTS = {
    "nf_unsw": ("--nf-unsw-csv", "--nf-unsw-max-per-class", 5000),
    "cicids2017": (
        "--cicids2017-csv",
        "--cicids2017-max-per-class",
        5000,
    ),
    "cic_iot2023": (
        "--cic-iot2023-csv",
        "--cic-iot2023-max-per-class",
        1000,
    ),
    "cic_ton_iot": (
        "--cic-ton-iot-csv",
        "--cic-ton-iot-max-per-class",
        1000,
    ),
    "edge_iiot": ("--edge-iiot-csv", "--edge-iiot-max-per-class", 1000),
    "nf_cse": ("--nf-cse-csv", "--nf-cse-max-per-class", 1000),
    "ustc_tfc2016": ("--ustc-csv", "--ustc-max-per-class", 3000),
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def expected_identities() -> set[tuple[str, str, str, int]]:
    return {
        (suite, scenario, "ronetc", 7)
        for suite, scenarios in SUITES.items()
        for scenario in scenarios
    }


def option_value(command: list[Any], option: str) -> Any:
    if option not in command:
        return None
    index = command.index(option)
    return command[index + 1] if index + 1 < len(command) else None


def audit_protocol(
    protocol_path: Path,
    project_root: Path,
    full_summary: Path,
    coverage_manifest: Path,
    baseline_manifest: Path,
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    project_root = project_root.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))

    claimed_manifest = protocol.get("manifest_sha256")
    manifest_payload = dict(protocol)
    manifest_payload.pop("manifest_sha256", None)
    actual_manifest = canonical_hash(manifest_payload)

    tasks = protocol.get("tasks", [])
    actual_identities = {
        (
            task.get("suite"),
            task.get("scenario"),
            task.get("model"),
            task.get("seed"),
        )
        for task in tasks
    }
    expected = expected_identities()
    artifact_counts = {
        artifact: sum(
            (Path(task.get("output_dir", "")) / artifact).is_file()
            for task in tasks
        )
        for artifact in REQUIRED_ARTIFACTS
    }

    implementation = protocol.get("implementation_sha256", {})
    implementation_matches = {
        name: (
            name in implementation
            and (project_root / name).is_file()
            and implementation[name] == file_hash(project_root / name)
        )
        for name in REQUIRED_IMPLEMENTATION
    }
    source_evidence = protocol.get("source_evidence_sha256", {})
    source_matches = {
        "strict_v4_full102_summary": (
            full_summary.is_file()
            and source_evidence.get("strict_v4_full102_summary")
            == file_hash(full_summary)
        ),
        "strict_v4_coverage_manifest": (
            coverage_manifest.is_file()
            and source_evidence.get("strict_v4_coverage_manifest")
            == file_hash(coverage_manifest)
        ),
        "strict_v4_baseline_manifest_v2": (
            baseline_manifest.is_file()
            and source_evidence.get("strict_v4_baseline_manifest_v2")
            == file_hash(baseline_manifest)
        ),
    }

    command = protocol.get("command", [])
    baseline_value = (
        json.loads(baseline_manifest.read_text(encoding="utf-8"))
        if baseline_manifest.is_file()
        else {}
    )
    baseline_payload = (
        dict(baseline_value) if isinstance(baseline_value, dict) else {}
    )
    baseline_claimed = baseline_payload.pop("manifest_sha256", None)
    baseline_canonical = bool(
        baseline_claimed == canonical_hash(baseline_payload)
    )
    cache_evidence = (
        baseline_value.get("cache_artifacts", {})
        if isinstance(baseline_value, dict)
        else {}
    )
    cache_command_valid = bool(
        baseline_canonical and set(cache_evidence) == set(CACHE_ARGUMENTS)
    )
    for suite, (csv_option, maximum_option, maximum) in (
        CACHE_ARGUMENTS.items()
    ):
        evidence = cache_evidence.get(suite, {})
        csv_path = Path(evidence.get("path", ""))
        sidecar_path = Path(f"{csv_path}.json")
        cache_command_valid = bool(
            cache_command_valid
            and option_value(command, csv_option) == evidence.get("path")
            and option_value(command, maximum_option) == str(maximum)
            and csv_path.is_file()
            and sidecar_path.is_file()
            and file_hash(csv_path) == evidence.get("sha256")
            and file_hash(sidecar_path) == evidence.get("sidecar_sha256")
        )
    paired_input = protocol.get("paired_input_contract", {})
    checks = {
        "schema_and_state": (
            protocol.get("schema_version")
            == "strict_v4_ronetc_full102_protocol_v1"
            and protocol.get("state") == "frozen_zero_result"
        ),
        "manifest_matches": claimed_manifest == actual_manifest,
        "universe_exact": (
            protocol.get("universe", {}).get("suite_count") == 7
            and protocol.get("universe", {}).get("scenario_count") == 102
            and protocol.get("universe", {}).get("task_count") == 102
            and len(tasks) == 102
            and len(actual_identities) == 102
            and actual_identities == expected
        ),
        "implementation_hashes_match": all(implementation_matches.values()),
        "source_evidence_hashes_match": all(source_matches.values()),
        "command_is_frozen_target": (
            "--suite" in command
            and command[command.index("--suite") + 1] == "strict_v4_primary"
            and "--models" in command
            and command[command.index("--models") + 1] == "ronetc"
            and "--seeds" in command
            and command[command.index("--seeds") + 1] == "7"
            and "--workers" in command
            and command[command.index("--workers") + 1] == "1"
        ),
        "paired_cache_command_and_hashes_match": (
            cache_command_valid
            and paired_input.get("suite_count") == 7
            and paired_input.get(
                "postselection_corruption_cache_is_not_used"
            )
            is True
            and paired_input.get("csv_sha256")
            == {
                suite: evidence["sha256"]
                for suite, evidence in cache_evidence.items()
            }
            and paired_input.get("sidecar_sha256")
            == {
                suite: evidence["sidecar_sha256"]
                for suite, evidence in cache_evidence.items()
            }
        ),
        "formal_result_artifacts_absent": all(
            count == 0 for count in artifact_counts.values()
        ),
        "claim_boundary_is_conservative": (
            protocol.get("claim_boundary", {}).get(
                "authorizes_comprehensive_sota_before_execution"
            )
            is False
            and protocol.get("claim_boundary", {}).get(
                "authorizes_algorithm_selection"
            )
            is False
        ),
        "analysis_contract_is_frozen": (
            protocol.get("analysis_contract", {}).get(
                "summary_implementation"
            )
            == "summarize_strict_v4_ronetc_full102.py"
            and protocol.get("analysis_contract", {}).get(
                "independent_audit_implementation"
            )
            == "audit_strict_v4_ronetc_full102.py"
            and protocol.get("analysis_contract", {}).get(
                "required_outputs_after_execution"
            )
            == [
                "summary.json",
                "summary.md",
                "audit.json",
                "execution_complete.json",
            ]
        ),
    }
    audit: dict[str, Any] = {
        "schema_version": "strict_v4_ronetc_full102_protocol_audit_v1",
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256_claimed": claimed_manifest,
        "protocol_manifest_sha256_recomputed": actual_manifest,
        "checks": checks,
        "implementation_matches": implementation_matches,
        "source_evidence_matches": source_matches,
        "artifact_counts": artifact_counts,
        "passed": all(checks.values()),
    }
    audit["audit_manifest_sha256"] = canonical_hash(audit)
    return audit


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Independently audit a frozen strict-v4 RoNeTC protocol."
    )
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    audit = audit_protocol(
        args.protocol,
        args.project_root,
        args.full_summary.resolve(),
        args.coverage_manifest.resolve(),
        args.baseline_manifest.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "passed": audit["passed"],
                "audit_manifest_sha256": audit["audit_manifest_sha256"],
            }
        )
    )
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
