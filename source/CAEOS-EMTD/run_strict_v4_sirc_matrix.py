from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from caeos.sirc_posthoc import METHODS


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def without_suffix(value: str, suffix: str) -> str:
    if not value.endswith(suffix):
        raise ValueError("%r does not end with %r" % (value, suffix))
    return value[: -len(suffix)]


def select_pilot_scenarios(coverage: dict[str, Any]) -> dict[str, list[str]]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    coverage_sha = coverage.get("manifest_sha256")
    registry = coverage.get("scenario_registry")
    if not isinstance(coverage_sha, str) or not isinstance(registry, dict):
        raise ValueError("coverage manifest is incomplete")
    selected = {}
    for suite in sorted(registry):
        scenarios = registry[suite].get("scenarios", [])
        if len(scenarios) < 2:
            raise ValueError("suite %s has fewer than two scenarios" % suite)
        indices = []
        attempt = 0
        while len(indices) < 2:
            token = "%s:sirc_msp_fixed:%s:%d" % (coverage_sha, suite, attempt)
            index = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:16], 16) % len(scenarios)
            if index not in indices:
                indices.append(index)
            attempt += 1
        selected[suite] = [scenarios[index] for index in indices]
    return selected


def source_artifacts(run: Path) -> dict[str, str]:
    return {name: sha256_file(run / name) for name in ("metrics.json", "scores.npz", "model.pt")}


def validate_full_expansion(gate: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    if gate.get("schema_version") != "strict_v4_mlp_sirc_msp_fixed_expansion_gate_v1":
        raise ValueError("unexpected SIRC expansion gate schema")
    if analysis.get("schema_version") != "strict_v4_mlp_sirc_msp_fixed_pilot_analysis_v1":
        raise ValueError("unexpected SIRC pilot analysis schema")
    if analysis.get("expansion_gate_manifest_sha256") != gate.get("manifest_sha256"):
        raise ValueError("SIRC pilot analysis is not bound to the expansion gate")
    methods = analysis.get("decision", {}).get("expand_methods")
    if not isinstance(methods, list) or not methods:
        raise ValueError("SIRC pilot did not approve any method for full expansion")
    if not set(methods).issubset(METHODS):
        raise ValueError("SIRC pilot approved an unknown method")
    return sorted(methods)


def valid_output(output: Path, expected_source: dict[str, str]) -> bool:
    paths = {name: output / name for name in ("metrics.json", "provenance.json", "scores.npz")}
    if not all(path.is_file() for path in paths.values()):
        return False
    try:
        metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
        provenance = json.loads(paths["provenance.json"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        set(metrics.get("reports", {})) == set(METHODS)
        and provenance.get("source_artifact_sha256") == expected_source
        and provenance.get("methods") == list(METHODS)
    )


def run_one(evaluator: Path, source: Path, output: Path, device: str, expected_source: dict[str, str]) -> dict[str, str]:
    if valid_output(output, expected_source):
        return {"source": str(source), "output": str(output), "state": "reused"}
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, str(evaluator), "--source-run", str(source), "--output-dir", str(output), "--device", device],
        text=True, capture_output=True,
    )
    (output / "run.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError("SIRC run failed for %s: %s" % (source, completed.stderr[-3000:]))
    if not valid_output(output, expected_source):
        raise RuntimeError("SIRC output validation failed for %s" % source)
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--protocol-only", action="store_true")
    parser.add_argument("--expansion-gate", type=Path)
    parser.add_argument("--pilot-analysis", type=Path)
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    pilot = select_pilot_scenarios(coverage)
    all_sources = sorted(path.parent for path in source_root.glob("*/*_mlp/metrics.json"))
    if len(all_sources) != 102:
        raise ValueError("expected 102 frozen MLP runs, found %d" % len(all_sources))
    source_by_identity = {}
    for source in all_sources:
        scenario = without_suffix(without_suffix(source.name, "_mlp"), "_seed7")
        source_by_identity[(source.parent.name, scenario)] = source
    if len(source_by_identity) != 102:
        raise ValueError("frozen MLP source identities are not unique")
    selected_identities = sorted(source_by_identity) if args.mode == "full" else sorted(
        (suite, scenario) for suite, items in pilot.items() for scenario in items
    )
    sources = [source_by_identity[identity] for identity in selected_identities]
    expanded_methods = list(METHODS)
    expansion_evidence: dict[str, Any] = {}
    if args.mode == "full":
        if args.expansion_gate is None or args.pilot_analysis is None:
            raise ValueError("full SIRC expansion requires --expansion-gate and --pilot-analysis")
        gate = json.loads(args.expansion_gate.read_text(encoding="utf-8"))
        analysis = json.loads(args.pilot_analysis.read_text(encoding="utf-8"))
        expanded_methods = validate_full_expansion(gate, analysis)
        expansion_evidence = {
            "pilot_protocol_manifest_sha256": analysis["pilot_protocol_manifest_sha256"],
            "pilot_expansion_gate_manifest_sha256": gate["manifest_sha256"],
            "pilot_analysis_sha256": sha256_file(args.pilot_analysis),
            "gate_selected_expanded_methods": expanded_methods,
            "incidental_shared_forward_diagnostics": sorted(set(METHODS) - set(expanded_methods)),
        }
    base = Path(__file__).resolve().parent
    evaluator = base / "evaluate_mlp_sirc.py"
    scorer = base / "caeos" / "sirc_posthoc.py"
    source_hashes = {str(path.relative_to(source_root)): source_artifacts(path) for path in sources}
    protocol = {
        "schema_version": "strict_v4_mlp_sirc_msp_fixed_protocol_v1",
        "status": "frozen_before_sirc_results", "mode": args.mode,
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": "all frozen scenarios" if args.mode == "full" else "two SIRC-SHA-indexed scenarios per suite independent of metric values",
        "selected_scenarios": {
            suite: [scenario for selected_suite, scenario in selected_identities if selected_suite == suite]
            for suite in sorted({suite for suite, _ in selected_identities})
        },
        "expected_runs": len(sources), "methods": list(METHODS),
        "paper": "https://openaccess.thecvf.com/content/ACCV2022/html/Xia_Augmenting_Softmax_Information_for_Selective_Classification_with_Out-of-Distribution_Data_ACCV_2022_paper.html",
        "official_implementation": "https://github.com/Guoxoug/SIRC",
        "official_implementation_commit": "0b492695d5bf34942cd8b333d10a998f763c3eff",
        "formula": "official SIRC MSP primary confidence with separately declared L1 and negative ViM-residual auxiliaries",
        "parameter_policy": "a=known-train auxiliary mean-3*std and b=1/std exactly as official default",
        "variant_policy": "both official auxiliary variants reported independently; no test-OOD variant selection",
        "fit_data": "known_training_features_and_logits_only", "threshold_data": "known_validation_only",
        "ood_parameter_sweep": False, "test_labels": "final_metrics_and_development_expansion_gate_only",
        "prediction_policy": "unmodified_frozen_classifier_prediction",
        "nonredundancy": "softmax-information-retaining nonlinear combination differs from standalone MSP, ViM and global feature scores",
        "expansion_evidence": expansion_evidence,
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": {"evaluator": sha256_file(evaluator), "scorer": sha256_file(scorer), "runner": sha256_file(Path(__file__).resolve())},
    }
    canonical = json.dumps(protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    protocol["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    output_root.mkdir(parents=True, exist_ok=True)
    protocol_path = output_root / "protocol_manifest.json"
    if protocol_path.is_file():
        if json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
            raise ValueError("existing SIRC protocol differs from frozen inputs")
    else:
        protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.protocol_only:
        print(json.dumps(protocol, ensure_ascii=False, sort_keys=True), flush=True)
        return
    futures = {}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for source in sources:
            relative = source.relative_to(source_root)
            output = output_root / relative.parent / without_suffix(relative.name, "_mlp")
            future = executor.submit(run_one, evaluator, source, output, args.device, source_hashes[str(relative)])
            futures[future] = relative
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    completed = sum(
        valid_output(output_root / source.relative_to(source_root).parent / without_suffix(source.name, "_mlp"), source_hashes[str(source.relative_to(source_root))])
        for source in sources
    )
    if completed != len(sources):
        raise RuntimeError("SIRC coverage incomplete: %d/%d" % (completed, len(sources)))
    summary = {
        "schema_version": "strict_v4_mlp_sirc_msp_fixed_matrix_v1", "status": "complete", "mode": args.mode,
        "expected_runs": len(sources), "completed_runs": completed, "failures": 0,
        "methods_per_run": list(METHODS), "report_count": completed * len(METHODS),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {state: sum(item["state"] == state for item in results) for state in ("completed", "reused")},
    }
    (output_root / "matrix_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "sirc_msp_fixed_complete").write_text(protocol["manifest_sha256"] + "\n", encoding="ascii")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
