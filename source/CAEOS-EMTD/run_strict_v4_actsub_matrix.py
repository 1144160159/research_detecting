from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from caeos.actsub_posthoc import OFFICIAL_CODE_URL, OFFICIAL_COMMIT, PAPER_URL
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
            raise ValueError(f"suite {suite} has fewer than two scenarios")
        indices = []
        attempt = 0
        while len(indices) < 2:
            digest = hashlib.sha256(
                f"{coverage_sha}:actsub-iccv2025:{suite}:{attempt}".encode("utf-8")
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
        metrics.get("schema_version") == "strict_v4_mlp_actsub_scale_fixed_v1"
        and set(metrics.get("reports", {})) == {"actsub_scale_fixed"}
        and provenance.get("source_artifact_sha256") == expected_source
        and provenance.get("methods") == ["actsub_scale_fixed"]
        and postprocessor.get("official_commit") == OFFICIAL_COMMIT
        and float(postprocessor.get("scale_percentile", -1.0)) == 95.0
        and float(postprocessor.get("lambda", -1.0)) == 2.0
        and int(postprocessor.get("neighbors", -1)) == 10
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
            "--percentile",
            "95",
            "--lambda",
            "2",
            "--neighbors",
            "10",
        ],
        text=True,
        capture_output=True,
    )
    (output / "run.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError(
            f"ActSub run failed for {source}: {completed.stderr[-2000:]}"
        )
    if not valid_output(output, expected_source):
        raise RuntimeError(f"ActSub output validation failed for {source}")
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
        raise ValueError(f"expected 102 frozen MLP runs, found {len(all_sources)}")
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
    evaluator = base / "evaluate_mlp_actsub.py"
    scorer = base / "caeos" / "actsub_posthoc.py"
    source_hashes = {
        str(path.relative_to(source_root)): source_artifacts(path) for path in sources
    }
    protocol = {
        "schema_version": "strict_v4_mlp_actsub_scale_fixed_protocol_v1",
        "status": "frozen_before_actsub_results",
        "mode": args.mode,
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": (
            "all frozen scenarios"
            if args.mode == "full"
            else "two ActSub-SHA-indexed scenarios per suite independent of metric values"
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
        "methods": ["actsub_scale_fixed"],
        "paper": PAPER_URL,
        "official_code": OFFICIAL_CODE_URL,
        "official_commit": OFFICIAL_COMMIT,
        "adapter": {
            "formula": "ActSub Eq. 10 with SCALE decisive and cosine insignificant scores",
            "scale_percentile": 95.0,
            "lambda": 2.0,
            "neighbors": 10,
            "balance_index": "automatic Eq. 4 on known-training embeddings",
            "hyperparameter_policy": "official ResNet defaults; APS OOD sweep disabled",
            "prediction_source": "unmodified frozen MLP",
        },
        "fit_data": "known_training_embeddings_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_metrics_and_development_expansion_gate_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
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
            raise ValueError("existing ActSub protocol differs from frozen inputs")
    else:
        if observed:
            raise ValueError("refusing to freeze ActSub protocol after results exist")
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
                run_one,
                evaluator,
                source,
                output,
                args.device,
                source_hashes[str(relative)],
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
        raise RuntimeError(f"ActSub coverage incomplete: {completed}/{len(sources)}")
    summary = {
        "schema_version": "strict_v4_mlp_actsub_scale_fixed_matrix_v1",
        "status": "complete",
        "mode": args.mode,
        "expected_runs": len(sources),
        "completed_runs": completed,
        "failures": 0,
        "methods_per_run": ["actsub_scale_fixed"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "actsub_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )


if __name__ == "__main__":
    main()
