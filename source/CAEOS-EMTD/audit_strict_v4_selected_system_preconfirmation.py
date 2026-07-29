from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
    require_canonical,
    write_json,
)
from run_strict_v4_selected_system_parrot_safety import block_path
from summarize_strict_v4_selected_system_preconfirmation import (
    SCHEMA as SUMMARY_SCHEMA,
    summarize_records,
    validate_record,
)


SCHEMA = "strict_v4_selected_system_preconfirmation_audit_v1"


def build_audit(
    *,
    project_root: Path,
    protocol_path: Path,
    summary_path: Path,
    run_root: Path,
) -> dict[str, Any]:
    protocol = load(protocol_path)
    summary = load(summary_path)
    require_canonical(protocol, PROTOCOL_SCHEMA, "preconfirmation protocol")
    require_canonical(summary, SUMMARY_SCHEMA, "preconfirmation summary")
    registry = {
        (
            item["suite"],
            item["scenario"],
            int(item["training_seed"]),
        ): item
        for item in summary.get("record_file_registry", [])
    }
    records = []
    record_hashes_match = len(registry) == 306
    for source in protocol["sources"]:
        identity = (
            source["suite"],
            source["scenario"],
            int(source["training_seed"]),
        )
        path = block_path(run_root, source) / "preconfirmation.json"
        if (
            not path.is_file()
            or identity not in registry
            or registry[identity].get("record_file_sha256")
            != file_hash(path)
        ):
            record_hashes_match = False
            continue
        record = load(path)
        validate_record(record, protocol, source)
        records.append(record)
    try:
        recomputed = summarize_records(records, protocol)
    except (KeyError, TypeError, ValueError):
        recomputed = {}
    implementation_hashes_match = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    checks = {
        "protocol_is_canonical": True,
        "summary_is_canonical": True,
        "selected_algorithm_bound_end_to_end": (
            summary.get("selected_algorithm")
            == protocol.get("selected_algorithm")
            and all(
                record.get("selected_algorithm")
                == protocol.get("selected_algorithm")
                for record in records
            )
        ),
        "all_306_records_bound_by_file_hash": (
            record_hashes_match and len(records) == 306
        ),
        "implementation_hashes_match": implementation_hashes_match,
        "independent_recomputation_exact": all(
            summary.get(key) == recomputed.get(key)
            for key in (
                "validation",
                "classic_main_gate",
                "absolute_corruption_gate",
                "comparative_corruption_gate",
                "selective_sota_claims",
            )
        ),
        "all_1530_paired_conditions_present": (
            summary.get("validation", {}).get(
                "paired_corruption_condition_count"
            )
            == 1530
        ),
        "fresh_candidate_and_opendetect_refits": all(
            record.get("fresh_candidate_refit_performed") is True
            and record.get("fresh_opendetect_refit_performed") is True
            for record in records
        ),
        "same_arrays_and_no_condition_selection": all(
            record.get("same_candidate_opendetect_clean_arrays") is True
            and record.get("same_corrupted_arrays_per_condition") is True
            and record.get(
                "unknown_or_test_labels_used_for_fitting_selection_or_corruption"
            )
            is False
            for record in records
        ),
    }
    integrity = all(checks.values())
    classic = bool(summary.get("classic_main_gate", {}).get("passes"))
    absolute = bool(
        summary.get("absolute_corruption_gate", {}).get("passes")
    )
    comparative = bool(
        summary.get("comparative_corruption_gate", {}).get("passes")
    )
    unknown_selective = bool(
        summary.get("selective_sota_claims", {})
        .get("unknown_detection", {})
        .get("passes")
    )
    robustness_selective = bool(
        summary.get("selective_sota_claims", {})
        .get("corruption_robustness_vs_opendetect", {})
        .get("passes")
    )
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "independent_audit_complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "selected_algorithm": protocol["selected_algorithm"],
        "checks": checks,
        "passes": integrity,
        "classic_main_gate_passes": integrity and classic,
        "absolute_corruption_gate_passes": integrity and absolute,
        "comparative_corruption_gate_passes": integrity and comparative,
        "all_three_effect_gates_pass": (
            integrity and classic and absolute and comparative
        ),
        "selective_unknown_detection_sota_authorized": (
            integrity and unknown_selective
        ),
        "selective_corruption_robustness_sota_authorized": (
            integrity and robustness_selective
        ),
        "any_selective_sota_authorized": (
            integrity and (unknown_selective or robustness_selective)
        ),
        "claim_boundary": {
            "integrity_pass_does_not_imply_effect_pass": True,
            "negative_effect_result_remains_terminal_and_reportable": True,
            "comprehensive_sota_authorized_only_if_all_three_gates_pass": (
                integrity and classic and absolute and comparative
            ),
            "selective_claim_does_not_authorize_comprehensive_sota": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = load(args.protocol)
    if protocol["implementation_sha256"].get(Path(__file__).name) != file_hash(
        Path(__file__).resolve()
    ):
        raise ValueError("active preconfirmation auditor SHA drifted")
    value = build_audit(
        project_root=args.project_root.resolve(),
        protocol_path=args.protocol.resolve(),
        summary_path=args.summary.resolve(),
        run_root=args.run_root.resolve(),
    )
    write_json(args.output, value)
    print(
        json.dumps(
            {
                "integrity_passes": value["passes"],
                "classic_main_gate_passes": value[
                    "classic_main_gate_passes"
                ],
                "absolute_corruption_gate_passes": value[
                    "absolute_corruption_gate_passes"
                ],
                "comparative_corruption_gate_passes": value[
                    "comparative_corruption_gate_passes"
                ],
                "manifest_sha256": value["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
