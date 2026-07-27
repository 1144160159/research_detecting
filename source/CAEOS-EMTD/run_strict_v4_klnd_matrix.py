from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


METHODS = ("klnd1", "klnd2", "klnd3")
OFFICIAL_COMMIT = "673320b86dcaf72dcdeae5159b3b8ce91ac5e19c"
PAPER_SHA256 = "dd64018fd7875ca862ed50ab41b935a414bd1631fa5d3841c504f0806b38e52a"
OFFICIAL_GIT_BLOB_CONTENT_SHA256 = {
    "Experiments/AWF/AWF_kNLD.ipynb": (
        "39e18530a7b855d7eb34cc5c5fce0ab16f1c515fd2cac57f0b3edbd4d60d2a34"
    ),
    "Experiments/DF/DF_kNLD.ipynb": (
        "d91ed011f561c0e71c9571f169acabeaf38fbc9e54aa2f6632416cba5ee591e0"
    ),
    "Experiments/DC/DC_kNLD.ipynb": (
        "c8fb56ad42a7a16962619782205ae5f45483f6389e710db5970e710880624742"
    ),
    "Experiments/SETA/SETA.ipynb": (
        "ff89e3399c483a107f6ee54013431a176e451c4f0465fdc3aecdb0aed3701bd5"
    ),
    "Experiments/IoT/IoT_kNLD.ipynb": (
        "5cf368bd8d58528d9cf6ca21071866e1f53ddd90a01100a1a3fdc192f3a87df4"
    ),
}


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


def select_pilot_scenarios(
    coverage: dict[str, Any],
) -> dict[str, list[str]]:
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
            payload = "%s:klnd:%s:%s:%d" % (
                coverage_sha,
                OFFICIAL_COMMIT,
                suite,
                attempt,
            )
            index = int(
                hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16], 16
            ) % len(scenarios)
            if index not in indices:
                indices.append(index)
            attempt += 1
        selected[suite] = [scenarios[index] for index in indices]
    return selected


def source_artifacts(run: Path) -> dict[str, str]:
    return {
        name: sha256_file(run / name)
        for name in ("metrics.json", "scores.npz", "model.pt")
    }


def git_blob_sha256(repository: Path, relative: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), "show", "HEAD:" + relative],
        check=True,
        capture_output=True,
    )
    return hashlib.sha256(completed.stdout).hexdigest()


def verify_official_repository(repository: Path) -> dict[str, Any]:
    if not repository.is_dir():
        raise FileNotFoundError("official k-LND repository is absent")
    head = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if head != OFFICIAL_COMMIT:
        raise ValueError("official k-LND repository commit mismatch")
    status = subprocess.run(
        ["git", "-C", str(repository), "status", "--porcelain"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    if status:
        raise ValueError("official k-LND repository worktree is dirty")
    observed = {
        relative: git_blob_sha256(repository, relative)
        for relative in OFFICIAL_GIT_BLOB_CONTENT_SHA256
    }
    if observed != OFFICIAL_GIT_BLOB_CONTENT_SHA256:
        raise ValueError("official k-LND notebook SHA mismatch")
    tracked = subprocess.run(
        ["git", "-C", str(repository), "ls-files"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    return {
        "path": str(repository),
        "commit": head,
        "tracked_file_count": len(tracked),
        "worktree_clean": True,
        "git_blob_content_sha256": observed,
    }


def valid_output(output: Path, expected_source: dict[str, str]) -> bool:
    paths = {
        name: output / name
        for name in ("metrics.json", "provenance.json", "scores.npz")
    }
    if not all(path.is_file() for path in paths.values()):
        return False
    try:
        metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
        provenance = json.loads(
            paths["provenance.json"].read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return False
    return (
        set(metrics.get("reports", {})) == set(METHODS)
        and metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False
        and provenance.get("source_artifact_sha256") == expected_source
        and provenance.get("methods") == list(METHODS)
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
        ],
        text=True,
        capture_output=True,
    )
    (output / "run.log").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError(
            "k-LND run failed for %s: %s"
            % (source, completed.stderr[-3000:])
        )
    if not valid_output(output, expected_source):
        raise RuntimeError("k-LND output validation failed for %s" % source)
    return {"source": str(source), "output": str(output), "state": "completed"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--paper", type=Path, required=True)
    parser.add_argument("--official-repository", type=Path, required=True)
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
    paper = args.paper.resolve()
    if not paper.is_file() or sha256_file(paper) != PAPER_SHA256:
        raise ValueError("k-LND paper identity mismatch")
    official_identity = verify_official_repository(
        args.official_repository.resolve()
    )
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    pilot = select_pilot_scenarios(coverage)
    all_sources = sorted(
        path.parent for path in source_root.glob("*/*_mlp/metrics.json")
    )
    if len(all_sources) != 102:
        raise ValueError(
            "expected 102 frozen MLP runs, found %d" % len(all_sources)
        )
    source_by_identity = {}
    for source in all_sources:
        scenario_seed = without_suffix(source.name, "_mlp")
        scenario = without_suffix(scenario_seed, "_seed7")
        source_by_identity[(source.parent.name, scenario)] = source
    if len(source_by_identity) != 102:
        raise ValueError("frozen MLP source identities are not unique")
    selected_identities = (
        sorted(source_by_identity)
        if args.mode == "full"
        else sorted(
            (suite, scenario)
            for suite, items in pilot.items()
            for scenario in items
        )
    )
    sources = [source_by_identity[identity] for identity in selected_identities]
    base = Path(__file__).resolve().parent
    evaluator = base / "evaluate_mlp_klnd.py"
    scorer = base / "caeos" / "klnd.py"
    source_hashes = {
        str(path.relative_to(source_root)): source_artifacts(path)
        for path in sources
    }
    protocol = {
        "schema_version": "strict_v4_mlp_klnd_protocol_v1",
        "status": "frozen_before_klnd_results",
        "mode": args.mode,
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": (
            "all frozen scenarios"
            if args.mode == "full"
            else "two official-commit-and-coverage-SHA-indexed scenarios per suite independent of metric values"
        ),
        "selected_scenarios": {
            suite: [
                scenario
                for selected_suite, scenario in selected_identities
                if selected_suite == suite
            ]
            for suite in sorted({suite for suite, _ in selected_identities})
        },
        "expected_runs": len(sources),
        "methods": list(METHODS),
        "paper": "https://doi.org/10.1016/j.comnet.2023.109991",
        "paper_path": str(paper),
        "paper_sha256": PAPER_SHA256,
        "official_repository": (
            "https://github.com/ThiliniDahanayaka/"
            "Open-Set-Traffic-Classification"
        ),
        "official_source_identity": official_identity,
        "formula": {
            "klnd1": "D1 = d_predicted",
            "klnd2": "risk = -D2 where D2 = sum_neighbor(d_i - d_predicted)",
            "klnd3": "D3 = d_predicted / sum_neighbor(d_i)",
        },
        "adaptation": (
            "freeze the strict MLP and apply k-LND to its class-logit vector; "
            "no retraining or unknown-label fitting"
        ),
        "class_center_data": (
            "correctly_classified_known_training_logits_only"
        ),
        "native_threshold_data": (
            "correctly_classified_known_validation_logits_only"
        ),
        "native_threshold_policy": (
            "90th percentile after orienting every risk so higher is more unknown; "
            "this is equivalent to the official 10th-percentile D2 lower-tail rule"
        ),
        "neighbor_policy": "all_other_known_classes",
        "strict_deployment_threshold_data": "known_validation_risk_only",
        "strict_known_acceptance": 0.95,
        "ood_parameter_sweep": False,
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
    protocol["manifest_sha256"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    output_root.mkdir(parents=True, exist_ok=True)
    protocol_path = output_root / "protocol_manifest.json"
    if protocol_path.is_file():
        if json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
            raise ValueError("existing k-LND protocol differs from frozen inputs")
    else:
        protocol_path.write_text(
            json.dumps(protocol, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if args.protocol_only:
        print(json.dumps(protocol, ensure_ascii=False, sort_keys=True), flush=True)
        return
    futures = {}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for source in sources:
            relative = source.relative_to(source_root)
            output = (
                output_root
                / relative.parent
                / without_suffix(relative.name, "_mlp")
            )
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
        raise RuntimeError(
            "k-LND coverage incomplete: %d/%d" % (completed, len(sources))
        )
    summary = {
        "schema_version": "strict_v4_mlp_klnd_matrix_v1",
        "status": "complete",
        "mode": args.mode,
        "expected_runs": len(sources),
        "completed_runs": completed,
        "failures": 0,
        "methods_per_run": list(METHODS),
        "report_count": completed * len(METHODS),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "execution_states": {
            state: sum(item["state"] == state for item in results)
            for state in ("completed", "reused")
        },
    }
    (output_root / "matrix_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_root / "klnd_complete").write_text(
        protocol["manifest_sha256"] + "\n", encoding="ascii"
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
