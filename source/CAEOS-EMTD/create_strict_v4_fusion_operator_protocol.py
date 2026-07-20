from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION_FILES = (
    "create_strict_v4_fusion_operator_protocol.py",
    "analyze_strict_v4_fusion_operators.py",
    "analyze_strict_v4_attention_fusion.py",
    "scripts/run_strict_v4_fusion_operator_analysis.sh",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_protocol(
    project_root: Path,
    source_protocol: dict[str, Any],
    observed_analyses: int,
) -> dict[str, Any]:
    if observed_analyses != 0:
        raise ValueError("fusion operator protocol must be frozen at zero analyses")
    if source_protocol.get("schema_version") != "strict_v4_conflict_metric_protocol_v3":
        raise ValueError("unexpected source protocol schema")
    if source_protocol.get("manifest_sha256") != canonical_hash(source_protocol):
        raise ValueError("source protocol SHA mismatch")
    if source_protocol.get("expected_scenarios") != 102:
        raise ValueError("fusion operator analysis requires 102 source scenarios")
    result = {
        "schema_version": "strict_v4_fusion_operator_protocol_v2",
        "status": "frozen_before_analysis",
        "scope": "shared_frozen_evidence_clean_fusion_operator_ablation",
        "source_protocol_manifest_sha256": source_protocol["manifest_sha256"],
        "source_manifest_sha256": source_protocol["source_manifest_sha256"],
        "expected_scenarios": 102,
        "seed": 7,
        "methods": [
            "f2_probability_average",
            "f3_entropy_conditioned_attention",
            "f4_edl_evidence_sum",
            "f5_reliability_gate",
            "f6_standard_ds_fusion",
            "f9_caeos_final_probability",
        ],
        "definitions": {
            "f2_probability_average": "mean_of_normalized_view_probabilities",
            "f3_entropy_conditioned_attention": (
                "known_validation_nll_fit_modality_bias_plus_entropy_slope"
            ),
            "f4_edl_evidence_sum": "dirichlet_probability_from_summed_view_evidence",
            "f5_reliability_gate": (
                "reliability_weighted_raw_view_probability_then_output_normalization"
            ),
            "f6_standard_ds_fusion": "sequential_ronetc_equations_5_to_7",
            "f9_caeos_final_probability": "frozen_test_final_probability",
        },
        "unknown_risk": "one_minus_max_fused_probability",
        "fit_data": "f3_known_validation_only; other operators have no fitted parameters",
        "test_labels_used_for_fitting_or_selection": False,
        "pollution_claim_allowed": False,
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATION_FILES
        },
        "analysis_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def freeze_or_validate(output: Path, expected: dict[str, Any], observed: int) -> dict[str, Any]:
    if output.is_file():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != expected:
            raise ValueError("existing fusion operator protocol differs from current evidence")
        return existing
    if observed != 0:
        raise ValueError("fusion operator protocol must be frozen at zero analyses")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root", type=Path, default=Path(__file__).resolve().parent
    )
    parser.add_argument("--source-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.source_protocol.read_text(encoding="utf-8"))
    observed = int((args.output_dir / "analysis.json").is_file())
    expected = create_protocol(args.project_root.resolve(), source, 0)
    protocol = freeze_or_validate(
        args.output_dir / "protocol_manifest.json", expected, observed
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
