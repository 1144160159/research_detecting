from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

from scipy.stats import rankdata

from caeos.actsub_posthoc import OFFICIAL_COMMIT
from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
METHODS = ("actsub_scale_fixed", "mlp_msp", "mlp_energy", "opendetect")


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _report(payload, method, path):
    report = payload.get("reports", {}).get(method)
    if not isinstance(report, dict):
        raise ValueError(f"missing report {method}: {path}")
    result = {metric: float(report[metric]) for metric in METRICS}
    if not all(math.isfinite(value) for value in result.values()):
        raise ValueError(f"non-finite report {method}: {path}")
    return result


def _fingerprint(payload):
    value = payload.get("split_metadata", {}).get("split_fingerprint")
    return (
        None
        if value is None
        else json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def _formula_integrity(payload, path):
    if payload.get("schema_version") != "strict_v4_mlp_actsub_scale_fixed_v1":
        raise ValueError(f"unexpected ActSub metrics schema: {path}")
    selection = payload.get("selection_evidence", {})
    postprocessor = selection.get("postprocessor", {})
    fit = selection.get("fit_diagnostics", {})
    validation = selection.get("validation_diagnostics", {})
    test = selection.get("test_diagnostics", {})
    index = int(fit.get("balance_index", -1))
    dimension = int(fit.get("embedding_dimension", -1))
    checks = {
        "method": postprocessor.get("method") == "ActSub-SCALE-Fixed",
        "official_commit": postprocessor.get("official_commit") == OFFICIAL_COMMIT,
        "official_formula": postprocessor.get("official_formula")
        == "Eq. 10 decisive_energy_times_insignificant_score_power_lambda",
        "percentile": float(postprocessor.get("scale_percentile", -1.0)) == 95.0,
        "lambda": float(postprocessor.get("lambda", -1.0)) == 2.0,
        "neighbors": int(postprocessor.get("neighbors", -1)) == 10,
        "no_ood_sweep": "without_APS_OOD_sweep"
        in str(postprocessor.get("hyperparameter_policy", "")),
        "known_training_fit": postprocessor.get("fit_split")
        == "known_training_embeddings_only",
        "balance_index": 0 <= index < dimension,
        "training_count": int(fit.get("known_training_sample_count", 0)) >= 10,
        "validation_finite": validation.get("all_scores_finite") is True,
        "test_finite": test.get("all_scores_finite") is True,
        "prediction_unchanged": selection.get(
            "prediction_uses_unmodified_frozen_model"
        )
        is True,
        "label_integrity": selection.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False,
    }
    if not all(checks.values()):
        raise ValueError(f"ActSub formula integrity failed for {path}: {checks}")
    nonconstant = (
        float(validation.get("score_standard_deviation", 0.0)) > 1e-12
        and float(test.get("score_standard_deviation", 0.0)) > 1e-12
    )
    return checks, nonconstant


def analyze(pilot_root, source_root, opendetect_root, gate):
    protocol = _read(pilot_root / "protocol_manifest.json")
    if gate.get("schema_version") != "strict_v4_mlp_actsub_scale_fixed_expansion_gate_v1":
        raise ValueError("unexpected ActSub gate schema")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("ActSub gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("ActSub gate protocol binding mismatch")
    blocks = []
    formula_checks = []
    nonconstant_checks = []
    failures = list(pilot_root.glob("**/failure.json"))
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            paths = {
                "new": pilot_root / suite / f"{scenario}_seed7" / "metrics.json",
                "source": source_root / suite / f"{scenario}_seed7_mlp" / "metrics.json",
                "external": opendetect_root
                / suite
                / f"{scenario}_seed7_opendetect"
                / "metrics.json",
            }
            payloads = {name: _read(path) for name, path in paths.items()}
            fingerprints = [
                _fingerprint(payloads[name]) for name in ("new", "source", "external")
            ]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError(f"split mismatch for {suite}/{scenario}")
            integrity, nonconstant = _formula_integrity(payloads["new"], paths["new"])
            formula_checks.append(integrity)
            nonconstant_checks.append(nonconstant)
            blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "reports": {
                        "actsub_scale_fixed": _report(
                            payloads["new"], "actsub_scale_fixed", paths["new"]
                        ),
                        "mlp_msp": _report(payloads["source"], "msp", paths["source"]),
                        "mlp_energy": _report(
                            payloads["source"], "energy", paths["source"]
                        ),
                        "opendetect": _report(
                            payloads["external"], "opendetect", paths["external"]
                        ),
                    },
                }
            )
    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / len(
                blocks
            )
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-v for v in values])
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / 4.0
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))
    gains = {}
    for metric in UNKNOWN_METRICS:
        values = []
        for block in blocks:
            candidate = block["reports"]["actsub_scale_fixed"][metric]
            reference = block["reports"]["mlp_msp"][metric]
            values.append(
                reference - candidate if metric == "unknown_fpr95" else candidate - reference
            )
        gains[metric] = sum(values) / len(values)
    by_suite = defaultdict(list)
    for block in blocks:
        values = []
        for metric in UNKNOWN_METRICS:
            candidate = block["reports"]["actsub_scale_fixed"][metric]
            reference = block["reports"]["mlp_msp"][metric]
            values.append(
                reference - candidate if metric == "unknown_fpr95" else candidate - reference
            )
        by_suite[block["suite"]].append(sum(values) / 4.0)
    suite_gains = {
        suite: sum(values) / len(values) for suite, values in sorted(by_suite.items())
    }
    candidate_row = next(row for row in overall if row["method"] == "actsub_scale_fixed")
    known_diff = max(
        abs(
            block["reports"]["actsub_scale_fixed"]["known_macro_f1"]
            - block["reports"]["mlp_msp"]["known_macro_f1"]
        )
        for block in blocks
    )
    checks = {
        "pilot_runs_complete": len(blocks) == 14 and not failures,
        "split_integrity": True,
        "known_f1_nonregression": known_diff <= 1e-12,
        "formula_integrity": len(formula_checks) == 14,
        "score_nonconstant": len(nonconstant_checks) == 14 and all(nonconstant_checks),
        "top_two_rank": candidate_row["mean_unknown_metric_rank"] <= 2.0,
        "metric_breadth": sum(value > 0.0 for value in gains.values()) >= 3,
        "overall_gain": sum(gains.values()) / 4.0 > 0.0,
        "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 5
        and min(suite_gains.values()) >= -0.03,
    }
    return {
        "schema_version": "strict_v4_mlp_actsub_scale_fixed_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks),
        "failure_count": len(failures),
        "formula_integrity_count": len(formula_checks),
        "nonconstant_score_count": sum(nonconstant_checks),
        "overall": overall,
        "actsub_vs_mlp_msp_oriented_mean_gains": gains,
        "actsub_vs_mlp_msp_four_metric_mean_gain": sum(gains.values()) / 4.0,
        "actsub_vs_mlp_msp_suite_mean_gains": suite_gains,
        "known_f1_max_absolute_difference": known_diff,
        "expansion_checks": checks,
        "decision": {"expand_actsub_to_full102": all(checks.values())},
    }


def render(result):
    lines = [
        "# Strict-v4 ActSub-SCALE-Fixed pilot analysis",
        "",
        "Expand ActSub to full 102: `%s`."
        % ("YES" if result["decision"]["expand_actsub_to_full102"] else "NO"),
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | "
            "{unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | "
            "{mean_unknown_metric_rank:.2f} |".format(**row)
        )
    lines.extend(["", "## Expansion gate", ""])
    for name, passed in result["expansion_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(
        args.pilot_root, args.source_root, args.opendetect_root, _read(args.gate)
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render(result)
    (args.output_dir / "analysis.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
