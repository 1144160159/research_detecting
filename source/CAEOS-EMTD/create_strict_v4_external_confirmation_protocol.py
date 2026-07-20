from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CLASSICAL_METHODS = {
    "isolation_forest",
    "one_class_svm",
    "local_outlier_factor",
    "pca_reconstruction",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("manifest_sha256", None)
    encoded = json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_source(method: str) -> str:
    if method.startswith("mlp_"):
        return "existing_mlp_confirmation_runs"
    if method == "opendetect":
        return "new_opendetect_confirmation_runs"
    if method in CLASSICAL_METHODS:
        return "new_shared_classical_confirmation_runs"
    raise ValueError(f"unsupported external confirmation method: {method}")


def create_protocol(
    summary: dict[str, Any],
    coverage: dict[str, Any],
    router_protocol: dict[str, Any],
) -> dict[str, Any]:
    if summary.get("schema_version") != "strict_v4_full103_coverage_summary_v1":
        raise ValueError("unexpected full summary schema")
    validation = summary.get("validation", {})
    required_validation = {
        "summary_validation_passes": validation.get("passes") is True,
        "scenario_count_is_102": validation.get("scenario_count") == 102,
        "method_count_at_least_22": validation.get("method_count", 0) >= 22,
        "independent_baseline_runs_complete": validation.get(
            "independent_baseline_run_checks"
        )
        == 204,
        "split_fingerprints_identical": validation.get(
            "split_fingerprints_identical"
        )
        is True,
    }
    if not all(required_validation.values()):
        raise ValueError("full independent-baseline summary is incomplete")
    if not summary.get("baseline_manifest_sha256"):
        raise ValueError("full summary is not bound to a baseline manifest")
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    if summary.get("coverage_manifest_sha256") != coverage.get("manifest_sha256"):
        raise ValueError("summary coverage binding mismatch")
    if (
        router_protocol.get("schema_version")
        != "strict_v4_domain_safe_router_confirmation_protocol_v1"
    ):
        raise ValueError("unexpected router confirmation protocol schema")

    candidates = [
        row for row in summary.get("overall", []) if not row["method"].startswith("caeos_")
    ]
    if not candidates:
        raise ValueError("full summary contains no non-CAEOS comparator")
    selected = min(
        candidates,
        key=lambda row: (float(row["mean_unknown_metric_rank"]), row["method"]),
    )
    seeds = sorted(int(seed) for seed in router_protocol["confirmation_seeds"])
    if len(seeds) < 3 or 7 in seeds or len(seeds) != len(set(seeds)):
        raise ValueError("external confirmation seeds are not independent")
    scenario_count = int(validation["scenario_count"])
    result = {
        "schema_version": "strict_v4_external_confirmation_protocol_v1",
        "status": "frozen_before_external_confirmation",
        "selection_rule": (
            "among every non-CAEOS method in the complete seed7 102-scenario table, "
            "minimize mean rank over AUROC, AUPR, FPR95 and OSCR; break ties by method name"
        ),
        "selection_uses_development_seed_only": True,
        "development_seed": 7,
        "selected_comparator": selected["method"],
        "selected_comparator_run_source": run_source(selected["method"]),
        "selected_development_row": selected,
        "eligible_non_caeos_methods": sorted(row["method"] for row in candidates),
        "confirmation_seeds": seeds,
        "scenario_count": scenario_count,
        "expected_comparator_runs": scenario_count * len(seeds),
        "confirmation_gate": {
            "all_four_unknown_metric_means_strictly_positive": True,
            "auroc_and_aupr_bootstrap_lower_strictly_positive": True,
            "all_four_unknown_metric_holm_p_below_0_05": True,
            "all_suite_unknown_metric_means_nonnegative": True,
            "known_macro_f1_nonnegative": True,
        },
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "baseline_manifest_sha256": summary["baseline_manifest_sha256"],
        "router_confirmation_protocol_sha256": router_protocol["manifest_sha256"],
        "summary_validation_checks": required_validation,
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--router-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.full_summary.read_text(encoding="utf-8"))
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    router_protocol = json.loads(args.router_protocol.read_text(encoding="utf-8"))
    result = create_protocol(summary, coverage, router_protocol)
    result["full_summary_file_sha256"] = file_hash(args.full_summary)
    result["coverage_manifest_file_sha256"] = file_hash(args.coverage_manifest)
    result["router_protocol_file_sha256"] = file_hash(args.router_protocol)
    result["creator_implementation_sha256"] = file_hash(Path(__file__))
    result["manifest_sha256"] = canonical_hash(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "selected_comparator": result["selected_comparator"],
        "run_source": result["selected_comparator_run_source"],
        "manifest_sha256": result["manifest_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
