from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION_FILES = (
    "create_strict_v4_attention_fusion_protocol.py",
    "analyze_strict_v4_attention_fusion.py",
    "scripts/run_strict_v4_attention_fusion_analysis.sh",
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
        raise ValueError("attention protocol must be frozen at zero analyses")
    if source_protocol.get("schema_version") != "strict_v4_conflict_metric_protocol_v3":
        raise ValueError("unexpected source protocol schema")
    if source_protocol.get("manifest_sha256") != canonical_hash(source_protocol):
        raise ValueError("source protocol SHA mismatch")
    if source_protocol.get("expected_scenarios") != 102:
        raise ValueError("attention analysis requires 102 source scenarios")
    result = {
        "schema_version": "strict_v4_attention_fusion_protocol_v1",
        "status": "frozen_before_analysis",
        "scope": "lightweight_tabular_side_channel_attention_baseline",
        "source_protocol_manifest_sha256": source_protocol["manifest_sha256"],
        "source_manifest_sha256": source_protocol["source_manifest_sha256"],
        "expected_scenarios": 102,
        "seed": 7,
        "candidate": "entropy_conditioned_learnable_attention",
        "comparators": [
            "uniform_probability_average",
            "caeos_reliability_fusion",
        ],
        "attention_definition": (
            "softmax(centered_modality_bias + beta * "
            "(1-normalized_probability_entropy))"
        ),
        "fit_data": "known_validation_only",
        "fit_objective": "validation_multiclass_nll_plus_l2",
        "l2_penalty": 1e-4,
        "parameter_bound": 8.0,
        "optimizer": "scipy_lbfgsb_maxiter500",
        "unknown_risk": "one_minus_max_fused_probability",
        "test_labels_used_for_fitting_or_selection": False,
        "metrics": [
            "known_macro_f1",
            "unknown_auroc",
            "unknown_aupr",
            "unknown_fpr95",
            "oscr",
            "known_ece",
        ],
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATION_FILES
        },
        "analysis_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def freeze_or_validate(
    output: Path, expected: dict[str, Any], observed_analyses: int
) -> dict[str, Any]:
    if output.is_file():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != expected:
            raise ValueError("existing attention protocol differs from current evidence")
        return existing
    if observed_analyses != 0:
        raise ValueError("attention protocol must be frozen at zero analyses")
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
