from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION_PATHS = (
    "caeos/tail_aware_ranking.py",
    "train_hybrid_open_set.py",
    "run_nested_gate_matrix.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def amend(
    protocol: dict[str, Any],
    *,
    current_hashes: dict[str, str],
    failure_logs: dict[str, bytes],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if protocol.get("schema_version") != "strict_v4_tail_aware_pilot_protocol_v1":
        raise ValueError("unexpected tail-aware pilot protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("original tail-aware pilot protocol SHA mismatch")
    original_sha = protocol["manifest_sha256"]
    original_hashes = protocol.get("implementation_sha256", {})
    if set(original_hashes) != set(IMPLEMENTATION_PATHS):
        raise ValueError("original implementation hash set is incomplete")
    changed = sorted(
        name for name in IMPLEMENTATION_PATHS if original_hashes[name] != current_hashes[name]
    )
    if changed != ["caeos/tail_aware_ranking.py", "train_hybrid_open_set.py"]:
        raise ValueError("integration amendment changed an unauthorized source set")
    if len(failure_logs) != 2:
        raise ValueError("integration amendment requires exactly two failed pilot logs")
    for name, raw in failure_logs.items():
        text = raw.decode("utf-8")
        if "KeyError: '0.5'" not in text or "selected_alpha" not in text:
            raise ValueError(f"unexpected pilot failure signature: {name}")

    revised = copy.deepcopy(protocol)
    revised.pop("manifest_sha256", None)
    revised["status"] = "refrozen_after_output_integration_fix_before_successful_pilot"
    revised["implementation_sha256"] = dict(current_hashes)
    revised["protocol_revision"] = {
        "supersedes_manifest_sha256": original_sha,
        "reason": (
            "tail-aware training completed but the report-only fold diagnostic reader "
            "used the legacy flat candidate layout; no metrics, scores or evidence "
            "artifacts were produced"
        ),
        "algorithm_hyperparameter_scenario_or_seed_changed": False,
        "failed_attempt_count": 2,
    }
    revised["manifest_sha256"] = canonical_hash(revised)
    amendment: dict[str, Any] = {
        "schema_version": "strict_v4_tail_aware_pilot_integration_fix_v1",
        "original_protocol_manifest_sha256": original_sha,
        "revised_protocol_manifest_sha256": revised["manifest_sha256"],
        "changed_implementation_files": changed,
        "original_implementation_sha256": original_hashes,
        "revised_implementation_sha256": current_hashes,
        "failed_run_log_sha256": {
            name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(failure_logs.items())
        },
        "failure_signature": "legacy flat fold diagnostic lookup KeyError after training",
        "metrics_scores_or_evidence_produced": False,
        "algorithm_hyperparameter_scenario_or_seed_changed": False,
    }
    amendment["record_sha256"] = canonical_hash(amendment)
    return revised, amendment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--failed-run", type=Path, action="append", required=True)
    parser.add_argument("--revised-protocol", type=Path, required=True)
    parser.add_argument("--amendment", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    failure_logs = {}
    for directory in args.failed_run:
        for forbidden in ("metrics.json", "scores.npz", "evidence_package.npz"):
            if (directory / forbidden).exists():
                raise ValueError(f"failed pilot unexpectedly produced {forbidden}")
        log = directory / "run.log"
        failure_logs[directory.name] = log.read_bytes()
    current_hashes = {
        name: sha256(args.project_root / name) for name in IMPLEMENTATION_PATHS
    }
    revised, amendment = amend(
        protocol, current_hashes=current_hashes, failure_logs=failure_logs
    )
    args.revised_protocol.write_text(
        json.dumps(revised, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.amendment.write_text(
        json.dumps(amendment, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(amendment, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
