from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SEEDS = (907, 911, 919)
SCENARIOS = (
    "bot",
    "ddos",
    "dos_goldeneye",
    "dos_hulk",
    "dos_slowhttptest",
    "dos_slowloris",
    "ftp_patator",
    "heartbleed",
    "infiltration",
    "portscan",
    "ssh_patator",
    "web_bruteforce",
    "web_sql_injection",
    "web_xss",
)


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_canonical(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    declared = value.get("manifest_sha256")
    body = dict(value)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")
    return value


def task_hashes(pairwise_dir: Path, xgboost_dir: Path) -> dict[str, str]:
    paths = {
        "pairwise_metrics": pairwise_dir / "metrics.json",
        "pairwise_scores": pairwise_dir / "scores.npz",
        "pairwise_evidence": pairwise_dir / "evidence_package.npz",
        "xgboost_metrics": xgboost_dir / "metrics.json",
        "xgboost_scores": xgboost_dir / "scores.npz",
    }
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    return {name: file_hash(path) for name, path in paths.items()}


def build_protocol(
    *,
    project_root: Path,
    development_protocol_path: Path,
    development_result_path: Path,
    pairwise_root: Path,
    xgboost_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    development_protocol_path = development_protocol_path.resolve()
    development_result_path = development_result_path.resolve()
    pairwise_root = pairwise_root.resolve()
    xgboost_root = xgboost_root.resolve()
    result_root = result_root.resolve()
    if (result_root / "confirmation.json").is_file():
        raise ValueError("fresh hybrid confirmation result must be zero at freeze")
    development_protocol = load_canonical(
        development_protocol_path, "development protocol"
    )
    development_result = load_canonical(
        development_result_path, "development result"
    )
    if (
        development_result.get("state")
        != "complete_seed7_development_selection"
        or development_result.get("binding", {}).get(
            "protocol_manifest_sha256"
        )
        != development_protocol["manifest_sha256"]
    ):
        raise ValueError("invalid development selection chain")
    selected = development_result["selected"]["configuration"]
    source_sha256 = {}
    for seed in SEEDS:
        seed_sources = {}
        for scenario in SCENARIOS:
            identity = f"{scenario}_seed{seed}"
            seed_sources[scenario] = task_hashes(
                pairwise_root / identity, xgboost_root / identity
            )
        source_sha256[str(seed)] = seed_sources
    implementations = (
        "evaluate_strict_v4_hybrid_self_algorithm_development.py",
        "evaluate_strict_v4_hybrid_self_algorithm_confirmation.py",
    )
    implementation_sha256 = {
        name: file_hash(project_root / name) for name in implementations
    }
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_hybrid_self_algorithm_confirmation_protocol_v1",
        "state": "frozen_zero_result_fresh_confirmation",
        "algorithm": development_result["algorithm"],
        "selected_configuration": selected,
        "selection_source": {
            "seed": 7,
            "development_protocol_path": str(development_protocol_path),
            "development_protocol_file_sha256": file_hash(
                development_protocol_path
            ),
            "development_protocol_manifest_sha256": development_protocol[
                "manifest_sha256"
            ],
            "development_result_path": str(development_result_path),
            "development_result_file_sha256": file_hash(
                development_result_path
            ),
            "development_result_manifest_sha256": development_result[
                "manifest_sha256"
            ],
        },
        "suite": "cicids2017",
        "seeds": list(SEEDS),
        "scenarios": list(SCENARIOS),
        "expected_task_count": len(SEEDS) * len(SCENARIOS),
        "pairwise_root": str(pairwise_root),
        "xgboost_root": str(xgboost_root),
        "result_root": str(result_root),
        "source_sha256": source_sha256,
        "implementation_sha256": implementation_sha256,
        "target_contract": {
            "self_algorithm_only": True,
            "alert_accuracy_at_least": 0.95,
            "benign_fpr_strictly_below": 0.05,
            "known_attack_type_accuracy_at_least": 0.95,
            "unknown_attack_recall_at_least": 0.95,
            "all_fresh_seeds_must_pass": True,
        },
        "anti_leakage": {
            "fresh_test_or_unknown_labels_used_for_selection": False,
            "configuration_is_exactly_seed7_selected": True,
            "fresh_execution_is_read_only": True,
        },
        "formal_output_counts_at_freeze": {
            "confirmation": 0,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--development-protocol", type=Path, required=True)
    parser.add_argument("--development-result", type=Path, required=True)
    parser.add_argument("--pairwise-root", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        project_root=args.project_root,
        development_protocol_path=args.development_protocol,
        development_result_path=args.development_result,
        pairwise_root=args.pairwise_root,
        xgboost_root=args.xgboost_root,
        result_root=args.result_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
