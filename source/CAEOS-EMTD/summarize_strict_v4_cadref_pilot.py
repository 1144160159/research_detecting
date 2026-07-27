from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

from scipy.stats import rankdata

from caeos.cadref_posthoc import OFFICIAL_COMMIT
from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
CANDIDATES = ("caref", "cadref_energy_fixed")
METHODS = CANDIDATES + ("mlp_energy", "opendetect")


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
    if payload.get("schema_version") != "strict_v4_mlp_cadref_family_v1":
        raise ValueError(f"unexpected CADRef metrics schema: {path}")
    selection = payload.get("selection_evidence", {})
    postprocessor = selection.get("postprocessor", {})
    fit = selection.get("fit_diagnostics", {})
    validation = selection.get("validation_diagnostics", {})
    test = selection.get("test_diagnostics", {})
    checks = {
        "family": postprocessor.get("family") == "CARef-and-CADRef-Energy-Fixed",
        "official_commit": postprocessor.get("official_commit") == OFFICIAL_COMMIT,
        "caref_formula": postprocessor.get("caref_formula")
        == "Eq.6 negative normalized L1 relative feature error",
        "cadref_formula": postprocessor.get("cadref_formula")
        == "Eq.10 negative(Ep/Energy(x)+En/mean_train_Energy)",
        "energy_default": postprocessor.get("logit_method") == "Energy",
        "no_ood_sweep": "without_OOD_sweep"
        in str(postprocessor.get("hyperparameter_policy", "")),
        "known_training_fit": postprocessor.get("fit_split")
        == "known_training_embeddings_and_logits_only",
        "training_count": int(fit.get("known_training_sample_count", 0)) > 0,
        "predicted_class_support": int(fit.get("supported_predicted_class_count", 0)) > 0,
        "mean_energy_finite_nonzero": math.isfinite(float(fit.get("global_mean_energy", 0.0)))
        and abs(float(fit.get("global_mean_energy", 0.0))) > 1e-12,
        "validation_finite": validation.get("all_scores_finite") is True,
        "test_finite": test.get("all_scores_finite") is True,
        "validation_energy_nonzero": float(validation.get("minimum_absolute_energy", 0.0))
        > 1e-12,
        "test_energy_nonzero": float(test.get("minimum_absolute_energy", 0.0)) > 1e-12,
        "prediction_unchanged": selection.get("prediction_uses_unmodified_frozen_model")
        is True,
        "label_integrity": selection.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False,
    }
    if not all(checks.values()):
        raise ValueError(f"CADRef formula integrity failed for {path}: {checks}")
    nonconstant = {
        "caref": (
            float(validation.get("caref_score_standard_deviation", 0.0)) > 1e-12
            and float(test.get("caref_score_standard_deviation", 0.0)) > 1e-12
        ),
        "cadref_energy_fixed": (
            float(validation.get("cadref_score_standard_deviation", 0.0)) > 1e-12
            and float(test.get("cadref_score_standard_deviation", 0.0)) > 1e-12
        ),
    }
    return checks, nonconstant


def _oriented(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(pilot_root, source_root, opendetect_root, gate):
    protocol = _read(pilot_root / "protocol_manifest.json")
    if gate.get("schema_version") != "strict_v4_mlp_cadref_family_expansion_gate_v1":
        raise ValueError("unexpected CADRef gate schema")
    if gate.get("manifest_sha256") != canonical_hash(gate):
        raise ValueError("CADRef gate SHA mismatch")
    if gate.get("pilot_protocol_manifest_sha256") != protocol.get("manifest_sha256"):
        raise ValueError("CADRef gate protocol binding mismatch")
    blocks = []
    formula_checks = []
    nonconstant_checks = {method: [] for method in CANDIDATES}
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
            fingerprints = [_fingerprint(payloads[name]) for name in ("new", "source", "external")]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError(f"split mismatch for {suite}/{scenario}")
            integrity, nonconstant = _formula_integrity(payloads["new"], paths["new"])
            formula_checks.append(integrity)
            for method in CANDIDATES:
                nonconstant_checks[method].append(nonconstant[method])
            blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "reports": {
                        "caref": _report(payloads["new"], "caref", paths["new"]),
                        "cadref_energy_fixed": _report(
                            payloads["new"], "cadref_energy_fixed", paths["new"]
                        ),
                        "mlp_energy": _report(payloads["source"], "energy", paths["source"]),
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
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / len(blocks)
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-v for v in values])
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / 4.0
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))

    candidate_results = {}
    expand = []
    for method in CANDIDATES:
        gains = {
            metric: sum(
                _oriented(
                    block["reports"][method][metric],
                    block["reports"]["mlp_energy"][metric],
                    metric,
                )
                for block in blocks
            )
            / len(blocks)
            for metric in UNKNOWN_METRICS
        }
        by_suite = defaultdict(list)
        for block in blocks:
            by_suite[block["suite"]].append(
                sum(
                    _oriented(
                        block["reports"][method][metric],
                        block["reports"]["mlp_energy"][metric],
                        metric,
                    )
                    for metric in UNKNOWN_METRICS
                )
                / 4.0
            )
        suite_gains = {
            suite: sum(values) / len(values) for suite, values in sorted(by_suite.items())
        }
        row = next(item for item in overall if item["method"] == method)
        known_diff = max(
            abs(
                block["reports"][method]["known_macro_f1"]
                - block["reports"]["mlp_energy"]["known_macro_f1"]
            )
            for block in blocks
        )
        checks = {
            "pilot_runs_complete": len(blocks) == 14 and not failures,
            "split_integrity": True,
            "known_f1_nonregression": known_diff <= 1e-12,
            "formula_integrity": len(formula_checks) == 14,
            "score_nonconstant": len(nonconstant_checks[method]) == 14
            and all(nonconstant_checks[method]),
            "top_two_rank": row["mean_unknown_metric_rank"] <= 2.0,
            "metric_breadth": sum(value > 0.0 for value in gains.values()) >= 3,
            "overall_gain": sum(gains.values()) / 4.0 > 0.0,
            "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 5
            and min(suite_gains.values()) >= -0.03,
        }
        if all(checks.values()):
            expand.append(method)
        candidate_results[method] = {
            "vs_mlp_energy_oriented_mean_gains": gains,
            "vs_mlp_energy_four_metric_mean_gain": sum(gains.values()) / 4.0,
            "vs_mlp_energy_suite_mean_gains": suite_gains,
            "known_f1_max_absolute_difference": known_diff,
            "expansion_checks": checks,
        }
    return {
        "schema_version": "strict_v4_mlp_cadref_family_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": gate["manifest_sha256"],
        "scenario_count": len(blocks),
        "failure_count": len(failures),
        "formula_integrity_count": len(formula_checks),
        "nonconstant_score_counts": {
            method: sum(nonconstant_checks[method]) for method in CANDIDATES
        },
        "overall": overall,
        "candidates": candidate_results,
        "decision": {
            "expand_methods_to_full102": expand,
            "expand_family_to_full102": bool(expand),
        },
    }


def render(result):
    expanded = result["decision"]["expand_methods_to_full102"]
    lines = [
        "# Strict-v4 CARef/CADRef-Energy-Fixed pilot analysis",
        "",
        "Expand shared family to full 102: `%s` (%s)."
        % ("YES" if expanded else "NO", ", ".join(expanded) if expanded else "none"),
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
    for method in CANDIDATES:
        lines.extend(["", f"## {method} expansion gate", ""])
        for name, passed in result["candidates"][method]["expansion_checks"].items():
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
