from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_tao_net_direct_baseline_protocol import (
    REQUIRED_RELEASE_ARTIFACTS,
    canonical_hash,
    file_hash,
    verify_sources,
)


RAW_REQUIRED_FILES = {
    "iscxvpn": {
        "PCAPs/NonVPN-PCAPs-03.zip": 10342707183,
        "PCAPs/NonVPN-PCAPs-02.zip": 12698509108,
        "PCAPs/VPN-PCAPs-02.zip": 1666120873,
        "PCAPs/VPN-PCAPS-01.zip": 670550834,
        "PCAPs/NonVPN-PCAPs-01.zip": 839164750,
    },
    "iscxtor": {
        "PCAPs/Tor.tar.xz": 11827793332,
        "PCAPs/NonTor.tar.xz": 9418400492,
        "CSVs/Scenario-A-merged_5s.csv": 15150853,
        "CSVs/Scenario-B-merged_5s.csv": 3218326,
    },
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("schema_version")
        != "strict_v4_tao_net_direct_baseline_protocol_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError("invalid TAO-Net direct-baseline protocol")
    return value


def verify_implementation(
    protocol: dict[str, Any], name: str, path: Path
) -> None:
    if (
        not path.is_file()
        or protocol["implementation_sha256"].get(name) != file_hash(path)
    ):
        raise ValueError(f"TAO-Net audit implementation SHA mismatch: {name}")


def required_artifact_inventory(repository: Path) -> dict[str, Any]:
    records = [
        {
            "relative_path": relative,
            "present": (repository / relative).is_file(),
        }
        for relative in REQUIRED_RELEASE_ARTIFACTS
    ]
    present = sum(int(item["present"]) for item in records)
    return {
        "expected": len(records),
        "present": present,
        "missing": len(records) - present,
        "records": records,
        "complete": present == len(records),
    }


def raw_dataset_inventory(
    roots: dict[str, Path],
    expected: dict[str, dict[str, int]] = RAW_REQUIRED_FILES,
) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for name, required in expected.items():
        root = roots[name]
        files = []
        for relative, expected_bytes in required.items():
            path = root / relative
            observed = path.stat().st_size if path.is_file() else None
            files.append(
                {
                    "relative_path": relative,
                    "expected_bytes": expected_bytes,
                    "observed_bytes": observed,
                    "passes": observed == expected_bytes,
                }
            )
        records[name] = {
            "root": str(root.resolve()),
            "root_exists": root.is_dir(),
            "files": files,
            "raw_identity_candidate_complete": all(
                item["passes"] for item in files
            ),
        }
    return records


def admission_decision(
    native_execution_gates: dict[str, bool],
    strict_v4_main_table_gates: dict[str, bool],
) -> dict[str, Any]:
    native = all(native_execution_gates.values())
    main_table = native and all(strict_v4_main_table_gates.values())
    return {
        "native_execution_gates": native_execution_gates,
        "strict_v4_main_table_gates": strict_v4_main_table_gates,
        "native_execution_admitted": native,
        "strict_v4_main_table_admitted": main_table,
    }


def build_audit(
    *,
    protocol: dict[str, Any],
    repository: Path,
    paper: Path,
    iscxvpn_raw: Path,
    iscxtor_raw: Path,
    chnapp_root: Path,
) -> dict[str, Any]:
    verify_sources(repository, paper)
    release = required_artifact_inventory(repository)
    raw = raw_dataset_inventory(
        {"iscxvpn": iscxvpn_raw, "iscxtor": iscxtor_raw},
    )
    raw_coverage = sum(
        int(item["raw_identity_candidate_complete"])
        for item in raw.values()
    )
    chnapp_present = chnapp_root.is_dir()
    exact_preprocessed_coverage = 0
    native_gates = {
        "official_code_identity": True,
        "official_paper_identity": True,
        "released_execution_artifacts_complete": release["complete"],
        "three_exact_preprocessed_datasets_complete": (
            exact_preprocessed_coverage == 3
        ),
        "published_configuration_complete": False,
        "paper_and_released_default_threshold_identity": False,
    }
    main_table_gates = {
        "same_open_set_task_as_strict_v4": False,
        "zero_unknown_validation_exposure": False,
        "unknown_candidate_label_set_hidden_from_decision_rule": False,
        "no_test_label_threshold_selection_in_released_default": False,
        "same_metrics_as_strict_v4": False,
    }
    admission = admission_decision(native_gates, main_table_gates)
    value: dict[str, Any] = {
        "schema_version": "strict_v4_tao_net_direct_baseline_audit_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "official_code_identity": {
            "passes": True,
            "commit": protocol["official_source"]["commit"],
            "tracked_file_count": protocol["official_source"][
                "tracked_file_count"
            ],
        },
        "released_artifact_inventory": release,
        "gpu_dataset_inventory": {
            "raw_source_candidate_coverage": f"{raw_coverage}/3",
            "raw_source_candidates": raw,
            "chnapp_root": str(chnapp_root.resolve()),
            "chnapp_root_present": chnapp_present,
            "exact_tao_preprocessed_manifest_available": False,
            "exact_tao_preprocessed_dataset_coverage": (
                f"{exact_preprocessed_coverage}/3"
            ),
            "crossplatform_derived_arrays_are_not_admitted_without_tao_manifest": (
                True
            ),
        },
        "released_code_protocol_findings": protocol[
            "released_snapshot_findings"
        ],
        "strict_v4_comparison_boundary": protocol["comparison_boundary"],
        "admission": admission,
        "paper_contract_admitted": True,
        "official_source_snapshot_admitted": True,
        "native_execution_admitted": admission[
            "native_execution_admitted"
        ],
        "strict_v4_main_table_admitted": admission[
            "strict_v4_main_table_admitted"
        ],
        "appendix_protocol_candidate": True,
        "model_metrics_generated": False,
        "baseline_count_increment": 0,
        "decision": (
            "freeze_as_direct-domain_protocol-layering candidate; do not "
            "execute or rank against strict-v4 until exact configs, manifests, "
            "all datasets, and leakage-free thresholds are available"
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--paper", type=Path, required=True)
    parser.add_argument("--iscxvpn-raw", type=Path, required=True)
    parser.add_argument("--iscxtor-raw", type=Path, required=True)
    parser.add_argument("--chnapp-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("TAO-Net audit output already exists")
    protocol = load(args.protocol)
    active = Path(__file__).resolve()
    verify_implementation(protocol, active.name, active)
    value = build_audit(
        protocol=protocol,
        repository=args.repository.resolve(),
        paper=args.paper.resolve(),
        iscxvpn_raw=args.iscxvpn_raw.resolve(),
        iscxtor_raw=args.iscxtor_raw.resolve(),
        chnapp_root=args.chnapp_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
