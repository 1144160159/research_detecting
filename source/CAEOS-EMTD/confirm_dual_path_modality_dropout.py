from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean
from typing import Any

from evaluate_dual_path_robustness import evaluate_pair


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_manifest_hash(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    encoded = json.dumps(
        core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_manifest_hash(payload)
    if payload.get("manifest_sha256") != actual:
        raise ValueError("confirmation manifest internal SHA mismatch")
    for relative, expected in payload.get("code_sha256", {}).items():
        target = project_root / relative
        if file_sha256(target) != expected:
            raise ValueError(f"frozen code SHA mismatch: {relative}")
    selection_sha = payload["candidate"]["weight_selection"][
        "selection_artifact_sha256"
    ]
    selection_path = project_root / "selection/modality_dropout_weight_selection.json"
    if file_sha256(selection_path) != selection_sha:
        raise ValueError("weight-selection artifact SHA mismatch")
    return payload


def apply_gates(
    pairs: list[dict[str, Any]], manifest: dict[str, Any]
) -> dict[str, Any]:
    gates = manifest["confirmation_gates"]
    decisions = []
    corrupted_gains: dict[str, list[float]] = {
        "known_macro_f1": [],
        "oscr": [],
    }
    for pair in pairs:
        baseline = pair["detector_report"]
        candidate = pair["dual_path_report"]
        deltas = {
            metric: float(candidate[metric]) - float(baseline[metric])
            for metric in ("known_macro_f1", "oscr")
        }
        condition_gate = (
            gates["per_clean_pair"]
            if pair["condition"] == "clean"
            else gates["per_corrupted_pair"]
        )
        routed_rate = float(
            pair.get("decision_architecture", {}).get("routed_sample_rate", 1.0)
        )
        routing_passed = True
        if "routed_sample_rate_maximum" in condition_gate:
            routing_passed = routing_passed and routed_rate <= float(
                condition_gate["routed_sample_rate_maximum"]
            ) + 1e-12
        if "routed_sample_rate_minimum" in condition_gate:
            routing_passed = routing_passed and routed_rate >= float(
                condition_gate["routed_sample_rate_minimum"]
            ) - 1e-12
        passed = (
            pair.get("detector_ranking_metrics_exactly_preserved") is True
            and routing_passed
            and deltas["known_macro_f1"]
            >= float(condition_gate["known_macro_f1_delta_minimum"]) - 1e-12
            and deltas["oscr"]
            >= float(condition_gate["oscr_delta_minimum"]) - 1e-12
        )
        if pair["condition"] != "clean":
            for metric in corrupted_gains:
                corrupted_gains[metric].append(deltas[metric])
        decisions.append(
            {
                "scenario": pair["scenario"],
                "condition": pair["condition"],
                "deltas": deltas,
                "routed_sample_rate": routed_rate,
                "routing_passed": routing_passed,
                "passed": passed,
            }
        )
    means = {metric: mean(values) for metric, values in corrupted_gains.items()}
    mean_gate = gates["corrupted_scenario_mean"]
    mean_passed = (
        means["known_macro_f1"]
        >= float(mean_gate["known_macro_f1_gain_minimum"]) - 1e-12
        and means["oscr"] >= float(mean_gate["oscr_gain_minimum"]) - 1e-12
    )
    confirmed = all(decision["passed"] for decision in decisions) and mean_passed
    return {
        "pair_decisions": decisions,
        "corrupted_scenario_mean_gain": means,
        "corrupted_scenario_mean_gate_passed": mean_passed,
        "confirmed": confirmed,
    }


def build_confirmation(
    project_root: Path,
    manifest: dict[str, Any],
    clean_detector_root: Path,
    confirmation_root: Path,
) -> dict[str, Any]:
    pairs = []
    prediction_routing = manifest.get("candidate", {}).get(
        "prediction_routing", "always_robust"
    )
    seed = int(manifest["heldout_confirmation"]["seeds"][0])
    for scenario in manifest["heldout_confirmation"]["scenarios"]:
        run_name = f"{scenario}_seed{seed}"
        for condition in manifest["heldout_confirmation"]["conditions"]:
            condition_id = condition["id"]
            if condition_id == "clean":
                detector_run = clean_detector_root / "edge_iiot" / run_name
                classifier_directory = "classifier_clean"
            else:
                detector_run = (
                    confirmation_root / "detector_missing" / "edge_iiot" / run_name
                )
                classifier_directory = "classifier_missing"
            classifier_run = (
                confirmation_root / classifier_directory / "edge_iiot" / run_name
            )
            result = evaluate_pair(
                detector_run,
                classifier_run,
                prediction_routing=prediction_routing,
            )
            result["scenario"] = scenario
            result["condition"] = condition_id
            pairs.append(result)
    expected = int(manifest["heldout_confirmation"]["paired_evaluations"])
    if len(pairs) != expected:
        raise ValueError(f"paired evaluation count mismatch: {len(pairs)} != {expected}")
    gate_result = apply_gates(pairs, manifest)
    return {
        "schema_version": "dual_path_modality_dropout_confirmation_result_v1",
        "state": "confirmed" if gate_result["confirmed"] else "rejected",
        "manifest_sha256": manifest["manifest_sha256"],
        "unknown_or_test_labels_used_for_training_selection_or_threshold": False,
        "unknown_test_labels_used_for_confirmation_evaluation_only": True,
        "scope": "two heldout scenarios at one seed; promotion gate only",
        "pairs": pairs,
        "gates": gate_result,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Dual-path Modality-dropout Confirmation",
        "",
        f"State: **{result['state']}**",
        "",
        "| Scenario | Condition | Baseline F1 | Candidate F1 | Delta F1 | Baseline OSCR | Candidate OSCR | Delta OSCR | Gate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    decisions = {
        (row["scenario"], row["condition"]): row
        for row in result["gates"]["pair_decisions"]
    }
    for pair in result["pairs"]:
        baseline = pair["detector_report"]
        candidate = pair["dual_path_report"]
        decision = decisions[(pair["scenario"], pair["condition"])]
        lines.append(
            "| {scenario} | {condition} | {bf1:.4f} | {cf1:.4f} | {df1:+.4f} | {bo:.4f} | {co:.4f} | {do:+.4f} | {gate} |".format(
                scenario=pair["scenario"],
                condition=pair["condition"],
                bf1=baseline["known_macro_f1"],
                cf1=candidate["known_macro_f1"],
                df1=decision["deltas"]["known_macro_f1"],
                bo=baseline["oscr"],
                co=candidate["oscr"],
                do=decision["deltas"]["oscr"],
                gate="PASS" if decision["passed"] else "FAIL",
            )
        )
    means = result["gates"]["corrupted_scenario_mean_gain"]
    lines.extend(
        [
            "",
            "Corrupted-scenario mean gains: Known F1 {:+.4f}, OSCR {:+.4f}.".format(
                means["known_macro_f1"], means["oscr"]
            ),
            "",
            "This is a promotion gate for a larger robustness matrix, not a final SOTA or significance claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Confirm the frozen dual-path robust candidate")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--clean-detector-root", type=Path, required=True)
    parser.add_argument("--confirmation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(args.manifest, args.project_root)
    result = build_confirmation(
        args.project_root, manifest, args.clean_detector_root, args.confirmation_root
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    args.markdown_output.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"state": result["state"], **result["gates"]["corrupted_scenario_mean_gain"]}))


if __name__ == "__main__":
    main()
