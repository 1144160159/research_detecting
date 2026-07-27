from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from caeos.gsc_posthoc import PAPER_URL
from run_strict_v4_klm_matrix import sha256_file, source_artifacts, without_suffix


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
            digest = hashlib.sha256(
                ("%s:gsc-iccv2025:%s:%d" % (coverage_sha, suite, attempt)).encode(
                    "utf-8"
                )
            ).hexdigest()
            index = int(digest[:16], 16) % len(scenarios)
            if index not in indices:
                indices.append(index)
            attempt += 1
        selected[suite] = [scenarios[index] for index in indices]
    return selected


def valid_output(output: Path, expected_source: dict[str, str]) -> bool:
    paths = {
        name: output / name for name in ("metrics.json", "provenance.json", "scores.npz")
    }
    if not all(path.is_file() for path in paths.values()):
        return False
    try:
        metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
        provenance = json.loads(paths["provenance.json"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        metrics.get("schema_version") == "strict_v4_mlp_gsc_v1"
        and set(metrics.get("reports", {})) == {"gsc"}
        and provenance.get("source_artifact_sha256") == expected_source
        and provenance.get("methods") == ["gsc"]
        and float(provenance.get("mask_ratio", -1.0)) == 0.05
    )


def run_one(
    evaluator: Path,
    source: Path,
    output: Path,
    device: str,
    expected_source: dict[str, str],
) -> dict[str, str]:
    if valid_output(output, expected_source):
        return {"source": str(source), "output": str(output), "state": "reused"}
    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            sys.executable,
            str(evaluator),
            "--source-run",
            str(source),
            "--output-dir",
            str(output),
            "--device",
            device,
            "--mask-ratio",
            "0.05",
        ],
        text=True,
        capture_output=True,
    )
    (output / "run.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError("GSC run failed for %s: %s" % (source, completed.stderr[-2000:]))
    if not valid_output(output, expected_source):
        raise RuntimeError("GSC output validation failed for %s" % source)
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
    identities = (
        sorted(source_by_identity)
        if args.mode == "full"
        else sorted(
            (suite, scenario)
            for suite, items in pilot.items()
            for scenario in items
        )
    )
    sources = [source_by_identity[identity] for identity in identities]
    base = Path(__file__).resolve().parent
    evaluator = base / "evaluate_mlp_gsc.py"
    scorer = base / "caeos" / "gsc_posthoc.py"
    source_hashes = {
        str(path.relative_to(source_root)): source_artifacts(path) for path in sources
    }
    protocol = {
        "schema_version": "strict_v4_mlp_gsc_protocol_v1",
        "status": "frozen_before_gsc_results",
        "mode": args.mode,
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": (
            "all frozen scenarios"
            if args.mode == "full"
            else "two GSC-SHA-indexed scenarios per suite, independent of metric values"
        ),
        "selected_scenarios": {
            suite: [
                scenario
                for selected_suite, scenario in identities
                if selected_suite == suite
            ]
            for suite in sorted({suite for suite, _ in identities})
        },
        "expected_runs": len(sources),
        "methods": ["gsc"],
        "paper": PAPER_URL,
        "official_code_status": "paper_states_code_to_be_released_no_repository_bound",
        "adapter": {
            "split_layer": "frozen_mlp_penultimate_embedding",
            "intervention": "zero_top_5_percent_absolute_predicted_logit_gradient",
            "logit_update": "paper_first_order_jacobian_update",
            "linear_head_behavior": "first_order_exact_class_fixed_mask_reported",
        },
        "fit_data": "none_frozen_embedding_logits_and_classifier_weight_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_metrics_and_development_expansion_gate_only",
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": {
            "evaluator": sha256_file(evaluator),
            "scorer": sha256_file(scorer),
            "runner": sha256_file(Path(__file__).resolve()),
        },
    }
    canonical = json.dumps(
        protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    protocol["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    output_root.mkdir(parents=True, exist_ok=True)
    protocol_path = output_root / "protocol_manifest.json"
    if protocol_path.is_file():
        if json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
            raise ValueError("existing GSC protocol differs from frozen inputs")
    else:
        protocol_path.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if args.protocol_only:
        print(json.dumps(protocol, ensure_ascii=False, sort_keys=True), flush=True)
        return

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for source in sources:
            relative = source.relative_to(source_root)
            output = output_root / relative.parent / without_suffix(relative.name, "_mlp")
            future = executor.submit(
                run_one, evaluator, source, output, args.device, source_hashes[str(relative)]
            )
            futures[future] = relative
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    completed = sum(
        valid_output(
            output_root
            / source.relative_to(source_root).parent
            / without_suffix(source.name, "_mlp"),
            source_hashes[str(source.relative_to(source_root))],
        )
        for source in sources
    )
    if completed != len(sources):
        raise RuntimeError("GSC coverage incomplete: %d/%d" % (completed, len(sources)))
    summary = {
        "schema_version": "strict_v4_mlp_gsc_matrix_v1",
        "status": "complete",
        "mode": args.mode,
        "expected_runs": len(sources),
        "completed_runs": completed,
        "failures": 0,
        "methods_per_run": ["gsc"],
        "report_count": completed,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "gsc_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )


if __name__ == "__main__":
    main()
