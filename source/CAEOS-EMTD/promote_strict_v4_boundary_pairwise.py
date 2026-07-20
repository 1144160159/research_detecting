from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_strict_v4_pseudo_unknown_development import canonical_hash


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--confirmation", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    confirmation = load_json(args.confirmation)
    if manifest.get("schema_version") != "strict_v4_boundary_pairwise_candidate_v1":
        raise ValueError("unexpected candidate manifest schema")
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("candidate manifest SHA mismatch")
    if confirmation.get("schema_version") != "strict_v4_boundary_pairwise_confirmation_v1":
        raise ValueError("unexpected confirmation schema")
    if confirmation.get("manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("confirmation does not bind the candidate manifest")
    if confirmation.get("decision", {}).get("passes") is not True:
        raise ValueError("candidate did not pass the frozen confirmation gate")

    metrics = {
        name: {
            "reference": values["reference_scenario_mean"],
            "candidate": values["candidate_scenario_mean"],
            "oriented_gain": values["oriented_mean_improvement"],
            "bootstrap_95_ci": values["bootstrap_95_ci"],
        }
        for name, values in confirmation["combined"]["metrics"].items()
    }
    promoted = {
        "schema_version": "strict_v4_confirmed_risk_candidate_v1",
        "status": "confirmed_for_full_matrix_evaluation",
        "risk_selection": manifest["candidate"]["risk_selection"],
        "training_objective": manifest["candidate"]["training_objective"],
        "parameters": {
            key: manifest["candidate"][key]
            for key in (
                "maximum_alpha",
                "minimum_fold_gain",
                "hard_pseudo_fraction",
                "interpolation",
                "max_per_task",
            )
        },
        "candidate_manifest_sha256": manifest["manifest_sha256"],
        "candidate_manifest_file_sha256": hashlib.sha256(
            args.manifest.read_bytes()
        ).hexdigest(),
        "confirmation_file_sha256": hashlib.sha256(
            args.confirmation.read_bytes()
        ).hexdigest(),
        "confirmation": {
            "runs": confirmation["validation"]["run_count"],
            "scenario_blocks": confirmation["validation"]["scenario_count"],
            "seeds": confirmation["validation"]["seeds"],
            "endpoint_counts": confirmation["decision"]["endpoint_counts"],
            "metrics": metrics,
        },
        "evidence_boundary": {
            "supports": (
                "promotion to the strict-v4 full-matrix candidate; known-class F1 is "
                "unchanged and all four open-set metrics improve in the frozen confirmation"
            ),
            "does_not_support": (
                "a seven-dataset, 103-scenario SOTA claim or universal improvement over "
                "all baselines; the full matrix and strong-baseline comparison remain pending"
            ),
        },
    }
    promoted["record_sha256"] = canonical_hash(promoted)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(promoted, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# Strict-v4 current confirmed risk candidate",
        "",
        f"Status: **{promoted['status']}**.",
        f"Risk selection: `{promoted['risk_selection']}`.",
        f"Record SHA256: `{promoted['record_sha256']}`.",
        "",
        "| Metric | Reference | Candidate | Oriented gain | 95% CI |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"):
        values = metrics[name]
        ci = values["bootstrap_95_ci"]
        lines.append(
            f"| {name} | {values['reference']:.6f} | {values['candidate']:.6f} | "
            f"{values['oriented_gain']:+.6f} | [{ci['lower']:+.6f}, {ci['upper']:+.6f}] |"
        )
    lines.extend(
        [
            "",
            "This promotes the candidate to full strict-v4 evaluation only. It is not a "
            "seven-dataset SOTA claim.",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(promoted, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
