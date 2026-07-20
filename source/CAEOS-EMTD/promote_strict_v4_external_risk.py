from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


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
    if manifest.get("schema_version") != "strict_v4_external_risk_candidate_v1":
        raise ValueError("unexpected external-risk manifest schema")
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("external-risk manifest SHA mismatch")
    if confirmation.get("schema_version") != "strict_v4_external_risk_confirmation_v1":
        raise ValueError("unexpected external-risk confirmation schema")
    if confirmation.get("manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("confirmation does not bind the external-risk manifest")
    if confirmation.get("decision", {}).get("passes") is not True:
        raise ValueError("external-risk candidate did not pass its frozen gate")

    metrics = {
        name: {
            "reference": values["reference_scenario_mean"],
            "candidate": values["candidate_scenario_mean"],
            "oriented_gain": values["oriented_mean_improvement"],
            "bootstrap_95_ci": values["bootstrap_95_ci"],
            "holm_adjusted_p_value": values["wilcoxon"][
                "holm_adjusted_p_value"
            ],
        }
        for name, values in confirmation["combined"]["metrics"].items()
    }
    candidate = manifest["candidate"]
    promoted = {
        "schema_version": "strict_v4_confirmed_external_risk_candidate_v1",
        "status": "confirmed_for_full_matrix_evaluation",
        "base_algorithm": candidate["base_algorithm"],
        "expert_model": candidate["expert_model"],
        "expert_risk": candidate["expert_risk"],
        "fusion": candidate["fusion"],
        "calibration": candidate["calibration"],
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
            "metrics": metrics,
            "by_suite": {
                suite: {
                    metric: report["metrics"][metric][
                        "oriented_mean_improvement"
                    ]
                    for metric in (
                        "unknown_auroc",
                        "unknown_aupr",
                        "unknown_fpr95",
                        "oscr",
                    )
                }
                for suite, report in confirmation["by_suite"].items()
            },
        },
        "evidence_boundary": {
            "supports": (
                "promotion as the current strict-v4 full-matrix algorithm; all four "
                "open-set metrics improve overall and within both confirmation suites, "
                "with unchanged known-class predictions"
            ),
            "does_not_support": (
                "a seven-dataset, 103-scenario SOTA claim or Holm-significant superiority; "
                "the full matrix and strong-baseline comparison remain pending"
            ),
        },
    }
    promoted["record_sha256"] = canonical_hash(promoted)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(promoted, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Strict-v4 current confirmed external-risk candidate",
        "",
        f"Status: **{promoted['status']}**.",
        f"Endpoint: `{promoted['expert_model']}/{promoted['expert_risk']}` + "
        f"`{promoted['fusion']}`.",
        f"Record SHA256: `{promoted['record_sha256']}`.",
        "",
        "| Metric | Base CAEOS | Fused CAEOS | Oriented gain | 95% CI | Holm p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in (
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    ):
        values = metrics[name]
        ci = values["bootstrap_95_ci"]
        p_value = values["holm_adjusted_p_value"]
        lines.append(
            f"| {name} | {values['reference']:.6f} | {values['candidate']:.6f} | "
            f"{values['oriented_gain']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{'NA' if p_value is None else f'{p_value:.6g}'} |"
        )
    lines.extend(
        [
            "",
            "This record authorizes full strict-v4 evaluation only. It is not a "
            "seven-dataset SOTA or multiple-comparison significance claim.",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(promoted, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
