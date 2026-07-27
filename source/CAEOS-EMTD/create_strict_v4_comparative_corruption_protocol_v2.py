from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def create_protocol_v2(
    v1: dict[str, Any],
    *,
    v1_file_sha256: str,
    evaluator_sha256: str,
    runner_sha256: str,
    summarizer_sha256: str,
    revision_creator_sha256: str,
    failed_evaluation_log_sha256: Optional[str],
    paired_results_observed_at_revision: int,
    runtime_capture_pairs_observed_at_revision: int,
) -> dict[str, Any]:
    if (
        v1.get("schema_version")
        != "strict_v4_comparative_corruption_protocol_v1"
        or v1.get("manifest_sha256") != canonical_hash(v1)
    ):
        raise ValueError("invalid comparative corruption v1 protocol")
    if int(paired_results_observed_at_revision) != 0:
        raise ValueError("v2 revision requires zero paired results")
    if int(runtime_capture_pairs_observed_at_revision) < 0:
        raise ValueError("runtime capture count cannot be negative")
    value = {
        key: item
        for key, item in v1.items()
        if key
        not in {
            "schema_version",
            "status",
            "manifest_sha256",
            "implementation_sha256",
            "paired_results_observed_at_freeze",
        }
    }
    implementations = dict(v1["implementation_sha256"])
    implementations.update(
        {
            "evaluator": evaluator_sha256,
            "runner": runner_sha256,
            "summarizer": summarizer_sha256,
            "protocol_revision_creator": revision_creator_sha256,
        }
    )
    value.update(
        {
            "schema_version": (
                "strict_v4_comparative_corruption_protocol_v2"
            ),
            "status": (
                "zero_paired_result_schema_fix_for_test_unknown_field"
            ),
            "supersedes_protocol_manifest_sha256": v1[
                "manifest_sha256"
            ],
            "supersedes_protocol_file_sha256": v1_file_sha256,
            "paired_results_observed_at_revision": 0,
            "runtime_capture_pairs_observed_at_revision": int(
                runtime_capture_pairs_observed_at_revision
            ),
            "failed_evaluation_log_sha256": failed_evaluation_log_sha256,
            "v1_failure_log_preserved": (
                failed_evaluation_log_sha256 is not None
            ),
            "implementation_sha256": implementations,
            "allowed_change": {
                "test_unknown_attribute_from_unknown_to_is_unknown": True,
                "dataset_schema_matches_multiview_flow_dataset": True,
                "source_registry_unchanged": True,
                "candidate_and_comparator_runtime_unchanged": True,
                "corruption_conditions_unchanged": True,
                "seeds_and_modalities_unchanged": True,
                "metrics_and_statistical_gates_unchanged": True,
                "no_paired_effect_result_available_for_change": True,
            },
            "claim_boundary": {
                "v1_failure_is_preserved": True,
                "runtime_captures_are_not_paired_effect_results": True,
                "v2_does_not_change_algorithm_or_effect_gate": True,
            },
        }
    )
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-protocol", type=Path, required=True)
    parser.add_argument("--evaluator", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--summarizer", type=Path, required=True)
    parser.add_argument("--failed-evaluation-log", type=Path)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paired = len(list(args.run_root.glob("**/paired_corruption.json")))
    captures = len(list(args.run_root.glob("**/capture_manifest.json")))
    value = create_protocol_v2(
        load(args.v1_protocol),
        v1_file_sha256=file_hash(args.v1_protocol),
        evaluator_sha256=file_hash(args.evaluator),
        runner_sha256=file_hash(args.runner),
        summarizer_sha256=file_hash(args.summarizer),
        revision_creator_sha256=file_hash(Path(__file__).resolve()),
        failed_evaluation_log_sha256=(
            file_hash(args.failed_evaluation_log)
            if args.failed_evaluation_log is not None
            else None
        ),
        paired_results_observed_at_revision=paired,
        runtime_capture_pairs_observed_at_revision=captures // 2,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
