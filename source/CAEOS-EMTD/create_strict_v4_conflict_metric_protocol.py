from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


EXPECTED_SCENARIOS = 102
IMPLEMENTATION_FILES = (
    "create_strict_v4_conflict_metric_protocol.py",
    "analyze_strict_v4_conflict_metrics.py",
    "scripts/run_strict_v4_conflict_metric_analysis.sh",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def collect_sources(run_root: Path) -> list[dict[str, Any]]:
    records = []
    for evidence_path in sorted(run_root.glob("*/*_seed7/evidence_package.npz")):
        scenario_dir = evidence_path.parent
        scores_path = scenario_dir / "scores.npz"
        metrics_path = scenario_dir / "metrics.json"
        if not scores_path.is_file() or not metrics_path.is_file():
            raise ValueError("incomplete source scenario: %s" % scenario_dir)
        records.append(
            {
                "scenario_dir": scenario_dir.relative_to(run_root).as_posix(),
                "evidence_sha256": file_hash(evidence_path),
                "scores_sha256": file_hash(scores_path),
                "metrics_sha256": file_hash(metrics_path),
                "evidence_bytes": evidence_path.stat().st_size,
                "scores_bytes": scores_path.stat().st_size,
            }
        )
    if len(records) != EXPECTED_SCENARIOS:
        raise ValueError(
            "expected %d source scenarios, found %d"
            % (EXPECTED_SCENARIOS, len(records))
        )
    return records


def create_protocol(
    project_root: Path, run_root: Path, observed_analysis: int
) -> dict[str, Any]:
    if observed_analysis != 0:
        raise ValueError("conflict analysis protocol must be frozen at zero analyses")
    records = collect_sources(run_root)
    source_binding = {"records": records}
    result = {
        "schema_version": "strict_v4_conflict_metric_protocol_v3",
        "status": "frozen_before_analysis",
        "scope": "posthoc_mechanism_analysis_not_model_selection",
        "source_run_root": str(run_root.resolve()),
        "source_method": "strict_v4_full103_pairwise_caeos_seed7",
        "seed": 7,
        "expected_scenarios": EXPECTED_SCENARIOS,
        "metrics": [
            "d1_label_disagreement",
            "d2_cosine_distance",
            "d3_jensen_shannon",
            "d4_symmetric_kl",
            "d5_raw_ds_conflict",
            "d6_conditional_ds_conflict",
            "d7_reliability_conditional_conflict",
        ],
        "metric_definitions": {
            "d1_label_disagreement": "mean pairwise top-1 mismatch",
            "d2_cosine_distance": "mean pairwise one-minus-cosine probability distance",
            "d3_jensen_shannon": "mean pairwise base-2 Jensen-Shannon divergence",
            "d4_symmetric_kl": "mean pairwise half symmetric KL divergence",
            "d5_raw_ds_conflict": "mean pairwise off-diagonal evidence mass",
            "d6_conditional_ds_conflict": (
                "D5 divided by paired committed evidence mass, then pair mean"
            ),
            "d7_reliability_conditional_conflict": (
                "reliability-product weighted pair mean of D6"
            ),
        },
        "control_variable": "mean_view_uncertainty",
        "probability_floor_for_divergences": 1e-12,
        "outcomes": [
            "unknown_auroc",
            "rank_biserial_effect",
            "spearman_with_uncertainty",
            "log_likelihood_gain_controlling_uncertainty",
            "one_degree_likelihood_ratio_pvalue",
        ],
        "incremental_information_rule": (
            "positive standardized metric coefficient and one-degree "
            "likelihood-ratio p-value below 0.05"
        ),
        "logistic_regularization_C": 1e4,
        "test_labels_used_for_model_fitting_or_selection": False,
        "test_labels_used_for_posthoc_statistical_analysis": True,
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATION_FILES
        },
        "source_manifest_sha256": canonical_hash(source_binding),
        "sources": records,
        "analysis_observed_at_freeze": 0,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def freeze_or_validate(
    output: Path, expected: dict[str, Any], observed_analysis: int
) -> dict[str, Any]:
    if output.is_file():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != expected:
            raise ValueError("existing conflict protocol differs from current evidence")
        return existing
    if observed_analysis != 0:
        raise ValueError("conflict analysis protocol must be frozen at zero analyses")
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
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    observed = int((args.output_dir / "analysis.json").is_file())
    expected = create_protocol(
        args.project_root.resolve(), args.run_root.resolve(), 0
    )
    protocol = freeze_or_validate(
        args.output_dir / "protocol_manifest.json", expected, observed
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
