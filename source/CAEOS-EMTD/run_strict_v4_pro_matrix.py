from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from caeos.pro_posthoc import (
    OFFICIAL_CODE_URL,
    OFFICIAL_COMMIT,
    PAPER_URL,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
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
                ("%s:pro-cvpr2025:%s:%d" % (coverage_sha, suite, attempt)).encode(
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
    postprocessor = provenance.get("postprocessor", {})
    return (
        metrics.get("schema_version") == "strict_v4_mlp_pro_msp_fixed_v1"
        and set(metrics.get("reports", {})) == {"pro_msp_fixed"}
        and provenance.get("source_artifact_sha256") == expected_source
        and provenance.get("methods") == ["pro_msp_fixed"]
        and postprocessor.get("official_commit") == OFFICIAL_COMMIT
        and float(postprocessor.get("step_size", -1.0)) == 0.003
        and int(postprocessor.get("steps", -1)) == 1
    )


def run_one(evaluator, source, output, device, expected_source):
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
            "--step-size",
            "0.003",
            "--steps",
            "1",
            "--temperature",
            "1.0",
        ],
        text=True,
        capture_output=True,
    )
    (output / "run.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError("PRO run failed for %s: %s" % (source, completed.stderr[-2000:]))
    if not valid_output(output, expected_source):
        raise RuntimeError("PRO output validation failed for %s" % source)
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
    evaluator = base / "evaluate_mlp_pro.py"
    scorer = base / "caeos" / "pro_posthoc.py"
    source_hashes = {
        str(path.relative_to(source_root)): source_artifacts(path) for path in sources
    }
    protocol = {
        "schema_version": "strict_v4_mlp_pro_msp_fixed_protocol_v1",
        "status": "frozen_before_pro_results",
        "mode": args.mode,
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": (
            "all frozen scenarios"
            if args.mode == "full"
            else "two PRO-SHA-indexed scenarios per suite independent of metric values"
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
        "methods": ["pro_msp_fixed"],
        "paper": PAPER_URL,
        "official_code": OFFICIAL_CODE_URL,
        "official_commit": OFFICIAL_COMMIT,
        "adapter": {
            "official_class": "PROv2_MSP_Postprocessor",
            "score": "minimum MSP over original and one sign-gradient step",
            "step_size": 0.003,
            "steps": 1,
            "temperature": 1.0,
            "hyperparameter_policy": "official defaults; no APS OOD sweep",
            "prediction_source": "unperturbed frozen MLP",
            "input_space": "known-training-standardized tabular coordinates",
            "projection_policy": "none matching official code",
        },
        "fit_data": "none",
        "threshold_data": "known_validation_only",
        "test_labels": "final_metrics_and_development_expansion_gate_only",
        "metrics_observed_at_freeze": 0,
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": {
            "evaluator": sha256_file(evaluator),
            "scorer": sha256_file(scorer),
            "runner": sha256_file(Path(__file__).resolve()),
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    output_root.mkdir(parents=True, exist_ok=True)
    protocol_path = output_root / "protocol_manifest.json"
    observed = len(list(output_root.glob("*/*/metrics.json")))
    if protocol_path.is_file():
        if json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
            raise ValueError("existing PRO protocol differs from frozen inputs")
    else:
        if observed:
            raise ValueError("refusing to freeze PRO protocol after results exist")
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
        raise RuntimeError("PRO coverage incomplete: %d/%d" % (completed, len(sources)))
    summary = {
        "schema_version": "strict_v4_mlp_pro_msp_fixed_matrix_v1",
        "status": "complete",
        "mode": args.mode,
        "expected_runs": len(sources),
        "completed_runs": completed,
        "failures": 0,
        "methods_per_run": ["pro_msp_fixed"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "pro_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )


if __name__ == "__main__":
    main()
