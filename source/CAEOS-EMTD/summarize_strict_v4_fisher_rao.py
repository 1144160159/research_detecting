from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

from scipy.stats import rankdata

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("known_macro_f1", "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
UNKNOWN_METRICS = METRICS[1:]
CANDIDATES = ("fim_standard", "fim_tensor", "fim_additive")
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
    return None if value is None else json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _formula_integrity(payload, path):
    if payload.get("schema_version") != "strict_v4_mlp_fisher_rao_family_v1":
        raise ValueError(f"unexpected Fisher-Rao metrics schema: {path}")
    selection = payload.get("selection_evidence", {})
    post = selection.get("postprocessor", {})
    fit = selection.get("fit_diagnostics", {})
    validation = selection.get("validation_diagnostics", {})
    test = selection.get("test_diagnostics", {})
    checks = {
        "family": post.get("family") == "Fisher-Rao-FIM-Trace",
        "standard_formula": str(post.get("standard_formula", "")).startswith("Eq.7"),
        "tensor_formula": str(post.get("tensor_formula", "")).startswith("Eq.9"),
        "additive_formula": str(post.get("additive_formula", "")).startswith("Eq.13"),
        "variance_balance": post.get("coefficient_policy")
        == "Eq.14-15 ID-only analytic variance balancing",
        "known_training_fit": post.get("fit_split")
        == "known_training_embeddings_logits_and_labels_only",
        "training_count": int(fit.get("known_training_sample_count", 0)) > 0,
        "feature_rank": int(fit.get("feature_subspace_rank", 0)) > 0,
        "probability_rank": int(fit.get("probability_subspace_rank", 0)) > 0,
        "lambda_m_negative": float(fit.get("lambda_magnitude_signed", 0.0)) < 0.0,
        "lambda_y_positive": float(fit.get("lambda_residual_signed", 0.0)) > 0.0,
        "validation_finite": validation.get("all_scores_finite") is True,
        "test_finite": test.get("all_scores_finite") is True,
        "prediction_unchanged": selection.get("prediction_uses_unmodified_frozen_model") is True,
        "label_integrity": selection.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        ) is False,
    }
    if not all(checks.values()):
        raise ValueError(f"Fisher-Rao formula integrity failed for {path}: {checks}")
    nonconstant = {
        method: (
            float(validation.get("score_standard_deviation", {}).get(method, 0.0)) > 1e-12
            and float(test.get("score_standard_deviation", {}).get(method, 0.0)) > 1e-12
        )
        for method in CANDIDATES
    }
    return checks, nonconstant


def _oriented(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def _collect(root, source_root, opendetect_root, protocol):
    blocks = []
    integrity_count = 0
    nonconstant = {method: 0 for method in CANDIDATES}
    for suite, scenarios in protocol["selected_scenarios"].items():
        for scenario in scenarios:
            paths = {
                "new": root / suite / f"{scenario}_seed7" / "metrics.json",
                "source": source_root / suite / f"{scenario}_seed7_mlp" / "metrics.json",
                "external": opendetect_root / suite
                / f"{scenario}_seed7_opendetect" / "metrics.json",
            }
            payloads = {name: _read(path) for name, path in paths.items()}
            fingerprints = [_fingerprint(payloads[name]) for name in ("new", "source", "external")]
            if fingerprints[0] is None or len(set(fingerprints)) != 1:
                raise ValueError(f"split mismatch for {suite}/{scenario}")
            _, item_nonconstant = _formula_integrity(payloads["new"], paths["new"])
            integrity_count += 1
            for method in CANDIDATES:
                nonconstant[method] += int(item_nonconstant[method])
            reports = {
                method: _report(payloads["new"], method, paths["new"])
                for method in CANDIDATES
            }
            reports["mlp_energy"] = _report(payloads["source"], "energy", paths["source"])
            reports["opendetect"] = _report(
                payloads["external"], "opendetect", paths["external"]
            )
            blocks.append({"suite": suite, "scenario": scenario, "reports": reports})
    return blocks, integrity_count, nonconstant


def analyze(root, source_root, opendetect_root, mode, gate=None, pilot_analysis=None):
    protocol = _read(root / "protocol_manifest.json")
    matrix = _read(root / "matrix_summary.json")
    expected = 14 if mode == "pilot" else 102
    if (
        protocol.get("schema_version") != "strict_v4_mlp_fisher_rao_family_protocol_v1"
        or protocol.get("mode") != mode
        or protocol.get("expected_runs") != expected
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid Fisher-Rao protocol")
    if (
        matrix.get("schema_version") != "strict_v4_mlp_fisher_rao_family_matrix_v1"
        or matrix.get("status") != "complete"
        or matrix.get("completed_runs") != expected
        or matrix.get("failures") != 0
        or matrix.get("protocol_manifest_sha256") != protocol["manifest_sha256"]
    ):
        raise ValueError("incomplete Fisher-Rao matrix")
    if mode == "pilot":
        if (
            gate is None
            or gate.get("schema_version")
            != "strict_v4_mlp_fisher_rao_family_expansion_gate_v1"
            or gate.get("manifest_sha256") != canonical_hash(gate)
            or gate.get("pilot_protocol_manifest_sha256") != protocol["manifest_sha256"]
        ):
            raise ValueError("invalid Fisher-Rao expansion gate")
    elif (
        pilot_analysis is None
        or pilot_analysis.get("schema_version")
        != "strict_v4_mlp_fisher_rao_family_pilot_analysis_v1"
        or not pilot_analysis.get("decision", {}).get("expand_methods_to_full102")
    ):
        raise ValueError("full Fisher-Rao analysis lacks an eligible pilot method")

    blocks, integrity_count, nonconstant = _collect(
        root, source_root, opendetect_root, protocol
    )
    failures = list(root.glob("**/failure.json"))
    if len(blocks) != expected or failures or integrity_count != expected:
        raise ValueError("Fisher-Rao artifact coverage is incomplete")
    overall = []
    for method in METHODS:
        row = {"method": method}
        for metric in METRICS:
            row[metric] = sum(block["reports"][method][metric] for block in blocks) / expected
        overall.append(row)
    for metric in UNKNOWN_METRICS:
        values = [row[metric] for row in overall]
        ranks = rankdata(values if metric == "unknown_fpr95" else [-value for value in values])
        for row, rank in zip(overall, ranks):
            row.setdefault("metric_ranks", {})[metric] = float(rank)
    for row in overall:
        row["mean_unknown_metric_rank"] = sum(row["metric_ranks"].values()) / 4.0
    overall.sort(key=lambda row: (row["mean_unknown_metric_rank"], row["method"]))

    candidates = {}
    expanded = []
    for method in CANDIDATES:
        gains = {
            metric: sum(
                _oriented(
                    block["reports"][method][metric],
                    block["reports"]["mlp_energy"][metric], metric,
                )
                for block in blocks
            ) / expected
            for metric in UNKNOWN_METRICS
        }
        by_suite = defaultdict(list)
        for block in blocks:
            by_suite[block["suite"]].append(
                sum(
                    _oriented(
                        block["reports"][method][metric],
                        block["reports"]["mlp_energy"][metric], metric,
                    )
                    for metric in UNKNOWN_METRICS
                ) / 4.0
            )
        suite_gains = {
            suite: sum(values) / len(values) for suite, values in sorted(by_suite.items())
        }
        known_diff = max(
            abs(block["reports"][method]["known_macro_f1"]
                - block["reports"]["mlp_energy"]["known_macro_f1"])
            for block in blocks
        )
        candidate = {
            "vs_mlp_energy_oriented_mean_gains": gains,
            "vs_mlp_energy_four_metric_mean_gain": sum(gains.values()) / 4.0,
            "vs_mlp_energy_suite_mean_gains": suite_gains,
            "known_f1_max_absolute_difference": known_diff,
        }
        if mode == "pilot":
            row = next(item for item in overall if item["method"] == method)
            checks = {
                "pilot_runs_complete": expected == 14 and not failures,
                "split_integrity": True,
                "known_f1_nonregression": known_diff <= 1e-12,
                "formula_integrity": integrity_count == 14,
                "score_nonconstant": nonconstant[method] == 14,
                "top_two_rank": row["mean_unknown_metric_rank"] <= 2.0,
                "metric_breadth": sum(value > 0.0 for value in gains.values()) >= 3,
                "overall_gain": sum(gains.values()) / 4.0 > 0.0,
                "suite_robustness": sum(value >= 0.0 for value in suite_gains.values()) >= 5
                and min(suite_gains.values()) >= -0.03,
            }
            candidate["expansion_checks"] = checks
            if all(checks.values()):
                expanded.append(method)
        candidates[method] = candidate
    result = {
        "schema_version": f"strict_v4_mlp_fisher_rao_family_{mode}_analysis_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_count": expected,
        "failure_count": 0,
        "formula_integrity_count": integrity_count,
        "nonconstant_score_counts": nonconstant,
        "overall": overall,
        "candidates": candidates,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
    }
    if mode == "pilot":
        result["expansion_gate_manifest_sha256"] = gate["manifest_sha256"]
        result["decision"] = {
            "expand_methods_to_full102": expanded,
            "expand_family_to_full102": bool(expanded),
        }
    else:
        result["pilot_expanded_methods"] = pilot_analysis["decision"]["expand_methods_to_full102"]
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render(result):
    lines = [
        f"# Strict-v4 Fisher-Rao {result['scenario_count']}-scenario analysis", "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["overall"]:
        lines.append(
            "| {method} | {known_macro_f1:.6f} | {unknown_auroc:.6f} | "
            "{unknown_aupr:.6f} | {unknown_fpr95:.6f} | {oscr:.6f} | "
            "{mean_unknown_metric_rank:.2f} |".format(**row)
        )
    if "decision" in result:
        expanded = result["decision"]["expand_methods_to_full102"]
        lines.extend(["", "Expand to full 102: `%s` (%s)." % (
            "YES" if expanded else "NO", ", ".join(expanded) if expanded else "none"
        )])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "full"), required=True)
    parser.add_argument("--gate", type=Path)
    parser.add_argument("--pilot-analysis", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(
        args.root, args.source_root, args.opendetect_root, args.mode,
        _read(args.gate) if args.gate else None,
        _read(args.pilot_analysis) if args.pilot_analysis else None,
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
