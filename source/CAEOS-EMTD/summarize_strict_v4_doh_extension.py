from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate
from summarize_strict_v4_full103 import (
    PAIRWISE_METHOD,
    REFERENCE_METHOD,
    base_report,
    full_report_metrics,
    parse_task,
)
from summarize_strict_v4_pilot import aggregate_table


SCENARIOS = {"dns2tcp", "dnscat2", "iodine"}
POLICY = "strict_v4_doh_extension_pairwise_screen_v1"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_hashed(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} SHA mismatch")


def load_blocks(
    raw: dict[str, Any],
    seeds: set[int],
    gate_root: Path,
    mlp_root: Path,
    baseline_root: Path,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    expected = {(scenario, seed) for scenario in SCENARIOS for seed in seeds}
    if raw.get("overall", {}).get("number_of_runs") != len(expected):
        raise ValueError("DoH raw fusion run count mismatch")
    if set(raw.get("selection_scope", {}).get("seeds", [])) != seeds:
        raise ValueError("DoH raw fusion seed scope mismatch")
    observed: set[tuple[str, int]] = set()
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    artifact_checks = 0
    split_checks = 0
    for run in raw["runs"]:
        scenario, seed = parse_task(run["task"])
        task = (scenario, seed)
        if run["suite"] != "doh" or task not in expected or task in observed:
            raise ValueError(f"unexpected or duplicate DoH task: {task}")
        observed.add(task)
        gate_dir = gate_root / "doh" / f"{scenario}_seed{seed}"
        mlp_dir = mlp_root / "doh" / f"{scenario}_seed{seed}_mlp"
        for directory, names in (
            (
                gate_dir,
                ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json"),
            ),
            (mlp_dir, ("metrics.json", "scores.npz", "provenance.json")),
        ):
            missing = [name for name in names if not (directory / name).is_file()]
            if missing:
                raise ValueError(f"missing DoH artifacts under {directory}: {missing}")
            artifact_checks += len(names)
        gate_metrics = json.loads((gate_dir / "metrics.json").read_text(encoding="utf-8"))
        mlp_metrics = json.loads((mlp_dir / "metrics.json").read_text(encoding="utf-8"))
        if gate_metrics.get("risk_policy") != POLICY:
            raise ValueError(f"DoH pairwise policy mismatch for {task}")
        if gate_metrics.get("risk_selection_details", {}).get(
            "unknown_or_test_labels_used_for_selection"
        ) is not False:
            raise ValueError(f"DoH CAEOS leakage guard failed for {task}")
        if mlp_metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        ) is not False:
            raise ValueError(f"DoH MLP leakage guard failed for {task}")
        gate_fingerprint = gate_metrics["split_metadata"]["split_fingerprint"]["combined"]
        mlp_fingerprint = mlp_metrics["split_metadata"]["split_fingerprint"]["combined"]
        audit = run.get("audit", {})
        if not (
            gate_fingerprint == mlp_fingerprint == audit.get("split_fingerprint")
            and audit.get("split_fingerprints_identical") is True
            and audit.get("caeos_unknown_or_test_labels_used_for_selection") is False
            and audit.get(
                "expert_unknown_or_test_labels_used_for_fitting_or_selection"
            )
            is False
            and audit.get("fusion_calibration_split") == "known_only_validation"
            and audit.get("test_labels_used_for_final_metrics_only") is True
        ):
            raise ValueError(f"DoH fusion audit failed for {task}")
        split_checks += 1
        label = f"doh/{scenario}/seed{seed}"
        methods = {
            REFERENCE_METHOD: base_report(gate_dir),
            PAIRWISE_METHOD: full_report_metrics(run["gate_report"], f"{label}/pairwise"),
            "caeos_openmax_risk": full_report_metrics(
                run["expert_report"], f"{label}/openmax"
            ),
        }
        for method, report in run["reports"].items():
            methods[f"caeos_openmax_{method}"] = full_report_metrics(
                report, f"{label}/{method}"
            )
        for risk, report in mlp_metrics["reports"].items():
            methods[f"mlp_{risk}"] = full_report_metrics(
                report, f"{label}/mlp_{risk}"
            )
        for model in ("opendetect", "classical_ood"):
            directory = baseline_root / "doh" / f"{scenario}_seed{seed}_{model}"
            missing = [
                name
                for name in ("metrics.json", "scores.npz", "provenance.json")
                if not (directory / name).is_file()
            ]
            if missing:
                raise ValueError(f"missing DoH baseline artifacts under {directory}: {missing}")
            artifact_checks += 3
            metrics = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
            fingerprint = metrics["split_metadata"]["split_fingerprint"]["combined"]
            if fingerprint != gate_fingerprint:
                raise ValueError(f"DoH baseline split mismatch for {task}/{model}")
            evidence = metrics.get("selection_evidence", {})
            if model == "opendetect":
                safe = evidence.get(
                    "unknown_or_test_labels_used_for_fitting_or_selection"
                ) is False
            else:
                safe = (
                    evidence.get("unknown_or_test_labels_used_for_training") is False
                    and evidence.get("unknown_or_test_labels_used_for_thresholds") is False
                )
            if not safe:
                raise ValueError(f"DoH baseline leakage guard failed for {task}/{model}")
            for method, report in metrics["reports"].items():
                methods[method] = full_report_metrics(report, f"{label}/{method}")
        blocks[f"{scenario}/seed{seed}"] = methods
    if observed != expected:
        raise ValueError(f"DoH task coverage mismatch: missing={sorted(expected-observed)}")
    method_set = set(next(iter(blocks.values())))
    if any(set(methods) != method_set for methods in blocks.values()):
        raise ValueError("DoH method coverage differs across tasks")
    return blocks, {
        "passes": True,
        "scenario_count": len(SCENARIOS),
        "seed_count": len(seeds),
        "run_count": len(blocks),
        "method_count": len(method_set),
        "artifact_checks": artifact_checks,
        "split_fingerprint_checks": split_checks,
        "unknown_or_test_labels_used_for_selection": False,
    }


def compare(
    blocks: dict[str, dict[str, dict[str, float]]], candidate: str
) -> dict[str, Any]:
    rows = []
    for key, methods in sorted(blocks.items()):
        scenario, seed_text = key.rsplit("/seed", 1)
        rows.append(
            {
                "suite": "doh",
                "scenario": scenario,
                "seed": int(seed_text),
                "candidate_selected": candidate,
                "reference_selected": PAIRWISE_METHOD,
                "candidate_report": methods[candidate],
                "reference_report": methods[PAIRWISE_METHOD],
            }
        )
    return aggregate(rows, 10000, 20260719)


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 DoH capture-group extension screen",
        "",
        f"Validation: **PASS**; scenarios: {report['validation']['scenario_count']}; "
        f"seeds: {report['validation']['seed_count']}; methods: "
        f"{report['validation']['method_count']}.",
        "This external screen reports every pre-existing method and selects no new router.",
        "",
        "| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(report["overall"], 1):
        lines.append(
            f"| {rank} | {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.3f} |"
        )
    lines.extend(
        [
            "",
            "Inference uses three dataset-scenarios; seed repeats are averaged within "
            "scenario. This is strict external-generalization evidence, not a standalone "
            "full-SOTA claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--gate-root", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--protocol-manifest", type=Path, required=True)
    parser.add_argument("--extension-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol_manifest.read_text(encoding="utf-8"))
    audit = json.loads(args.extension_audit.read_text(encoding="utf-8"))
    validate_hashed(
        protocol,
        "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "confirmation protocol",
    )
    validate_hashed(audit, "strict_v4_extension_dataset_audit_v1", "extension audit")
    if not audit["datasets"]["dohbrw2020"]["strict_group_generalization_eligible"]:
        raise ValueError("DoH is not strict group-generalization eligible")
    raw = json.loads(args.raw_fusion.read_text(encoding="utf-8"))
    seeds = set(protocol["confirmation_seeds"])
    blocks, validation = load_blocks(
        raw, seeds, args.gate_root, args.mlp_root, args.baseline_root
    )
    overall = aggregate_table(blocks)
    comparisons = {
        method: compare(blocks, method)
        for method in sorted(next(iter(blocks.values())))
        if method != PAIRWISE_METHOD
    }
    result = {
        "schema_version": "strict_v4_doh_extension_screen_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "extension_audit_sha256": audit["manifest_sha256"],
        "raw_fusion_sha256": file_hash(args.raw_fusion),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
        "validation": validation,
        "overall": overall,
        "comparisons_vs_pairwise": comparisons,
        "selection_policy": "descriptive_only_no_method_selected_on_doh_test_results",
        "full_sota_claim_allowed": False,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
