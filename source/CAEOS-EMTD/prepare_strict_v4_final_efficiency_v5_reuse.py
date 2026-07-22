from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


CAUCHY_RISK = "cauchy_modality_support_union"
PAIRWISE_EQUIVALENCE_MODE = "source_components_plus_stable_runtime_shadow"
OPENDETECT_EQUIVALENCE_MODE = "runtime_vs_uninstrumented_same_device_shadow"


def load_manifest(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected schema in {path}")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"canonical hash mismatch in {path}")
    return payload


def require_equivalence(path: Path, mode: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (
        payload.get("passes") is not True
        or payload.get("prediction_array_equal") is not True
        or float(payload.get("risk_max_absolute_difference", float("inf"))) > 1e-12
        or float(payload.get("absolute_tolerance", float("inf"))) > 1e-12
        or payload.get("equivalence_mode") != mode
        or payload.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError(f"equivalence gate failed: {path}")
    return payload


def capture_selected_risk(capture: Path) -> str:
    manifest = json.loads((capture / "capture_manifest.json").read_text())
    runtime_evidence = manifest.get("runtime_evidence", {})
    selected = runtime_evidence.get("selected_risk", manifest.get("selected_risk"))
    if not isinstance(selected, str):
        raise ValueError(f"candidate capture lacks selected risk: {capture}")
    return selected


def copy_capture(source: Path, destination: Path, mode: str) -> dict[str, Any]:
    if destination.exists():
        raise ValueError(f"reuse destination already exists: {destination}")
    require_equivalence(source / "equivalence.json", mode)
    manifest = json.loads((source / "capture_manifest.json").read_text())
    shutil.copytree(source, destination, copy_function=shutil.copy2)
    source_files = sorted(path for path in source.rglob("*") if path.is_file())
    copied_files = sorted(path for path in destination.rglob("*") if path.is_file())
    if [p.relative_to(source) for p in source_files] != [
        p.relative_to(destination) for p in copied_files
    ]:
        raise ValueError(f"capture inventory changed during reuse: {source}")
    hashes = {}
    for original, copied in zip(source_files, copied_files):
        original_hash = file_hash(original)
        if file_hash(copied) != original_hash:
            raise ValueError(f"capture copy hash mismatch: {copied}")
        hashes[str(copied.relative_to(destination))] = original_hash
    return {
        "source": str(source),
        "destination": str(destination),
        "schema_version": manifest.get("schema_version"),
        "files_sha256": hashes,
    }


def prepare_reuse(
    *,
    old_protocol_path: Path,
    new_protocol_path: Path,
    old_plan_path: Path,
    new_plan_path: Path,
    old_root: Path,
    new_root: Path,
    failure_path: Path,
    archived_old_runtime: Path,
    active_new_runtime: Path,
    output_dir: Path,
) -> dict[str, Any]:
    old_protocol = load_manifest(
        old_protocol_path, "strict_v4_final_efficiency_protocol_v2"
    )
    new_protocol = load_manifest(
        new_protocol_path, "strict_v4_final_efficiency_protocol_v2"
    )
    old_plan = load_manifest(old_plan_path, "strict_v4_final_efficiency_execution_plan_v2")
    new_plan = load_manifest(new_plan_path, "strict_v4_final_efficiency_execution_plan_v2")
    if old_plan.get("protocol_manifest_sha256") != old_protocol["manifest_sha256"]:
        raise ValueError("old plan/protocol binding mismatch")
    if new_plan.get("protocol_manifest_sha256") != new_protocol["manifest_sha256"]:
        raise ValueError("new plan/protocol binding mismatch")
    if len(old_plan.get("training_blocks", [])) != 21 or len(
        old_plan.get("inference_blocks", [])
    ) != 102:
        raise ValueError("old efficiency scope is incomplete")
    if len(new_plan.get("training_blocks", [])) != 21 or len(
        new_plan.get("inference_blocks", [])
    ) != 102:
        raise ValueError("new efficiency scope is incomplete")
    old_identities = [
        (block["suite"], block["scenario"], block.get("repetition"))
        for block in old_plan["training_blocks"] + old_plan["inference_blocks"]
    ]
    new_identities = [
        (block["suite"], block["scenario"], block.get("repetition"))
        for block in new_plan["training_blocks"] + new_plan["inference_blocks"]
    ]
    if old_identities != new_identities:
        raise ValueError("old and new plan scopes differ")
    if list(new_root.rglob("efficiency_metrics.json")) or list(
        new_root.rglob("capture_manifest.json")
    ):
        raise ValueError("new formal root is not empty before reuse")
    failure = json.loads(failure_path.read_text(encoding="utf-8"))
    if (
        failure.get("status") != "failed_closed"
        or failure.get("valid_for_complete_efficiency_claim") is not False
        or failure.get("reason") != "learned_tail_runtime_shadow_rank_instability"
    ):
        raise ValueError("v4 failure evidence is missing or incompatible")
    old_runtime_hash = file_hash(archived_old_runtime)
    new_runtime_hash = file_hash(active_new_runtime)
    if old_protocol["implementation_sha256"].get("candidate_pairwise_runtime") != old_runtime_hash:
        raise ValueError("archived runtime does not match old protocol")
    if new_protocol["implementation_sha256"].get("candidate_pairwise_runtime") != new_runtime_hash:
        raise ValueError("active runtime does not match new protocol")
    if old_runtime_hash == new_runtime_hash:
        raise ValueError("runtime fix did not change implementation hash")

    copied: list[dict[str, Any]] = []
    skipped_learned: list[str] = []
    missing_old: list[str] = []
    for block in old_plan["training_blocks"]:
        relative = Path("training") / block["suite"] / block["scenario"] / f"rep{block['repetition']}"
        old_block, new_block = old_root / relative, new_root / relative
        candidate = old_block / "candidate_capture"
        if (candidate / "capture_manifest.json").is_file():
            selected = capture_selected_risk(candidate)
            if selected == CAUCHY_RISK:
                copied.append(
                    copy_capture(
                        candidate, new_block / "candidate_capture", PAIRWISE_EQUIVALENCE_MODE
                    )
                )
            else:
                skipped_learned.append(str(relative / "candidate_capture"))
        else:
            missing_old.append(str(relative / "candidate_capture"))
        comparator = old_block / "comparator_capture"
        if (comparator / "capture_manifest.json").is_file():
            copied.append(
                copy_capture(
                    comparator,
                    new_block / "comparator_capture",
                    OPENDETECT_EQUIVALENCE_MODE,
                )
            )
        else:
            missing_old.append(str(relative / "comparator_capture"))

    for block in old_plan["inference_blocks"]:
        relative = Path("inference") / block["suite"] / block["scenario"]
        old_block, new_block = old_root / relative, new_root / relative
        candidate = old_block / "candidate_capture"
        if (candidate / "capture_manifest.json").is_file():
            selected = capture_selected_risk(candidate)
            if selected == CAUCHY_RISK:
                copied.append(
                    copy_capture(
                        candidate, new_block / "candidate_capture", PAIRWISE_EQUIVALENCE_MODE
                    )
                )
            else:
                skipped_learned.append(str(relative / "candidate_capture"))
        else:
            missing_old.append(str(relative / "candidate_capture"))
        for dirname in ("comparator_native_capture", "comparator_cpu_capture"):
            comparator = old_block / dirname
            if (comparator / "capture_manifest.json").is_file():
                copied.append(
                    copy_capture(
                        comparator,
                        new_block / dirname,
                        OPENDETECT_EQUIVALENCE_MODE,
                    )
                )
            else:
                missing_old.append(str(relative / dirname))

    forbidden = [
        path
        for pattern in ("*standalone_benchmark.json", "efficiency_metrics.json")
        for path in new_root.rglob(pattern)
    ]
    if forbidden:
        raise ValueError("timing result leaked into reuse root: " + str(forbidden[0]))
    audit = {
        "schema_version": "strict_v4_final_efficiency_v5_capture_reuse_audit_v1",
        "status": "capture_reuse_complete",
        "old_protocol_manifest_sha256": old_protocol["manifest_sha256"],
        "new_protocol_manifest_sha256": new_protocol["manifest_sha256"],
        "old_plan_manifest_sha256": old_plan["manifest_sha256"],
        "new_plan_manifest_sha256": new_plan["manifest_sha256"],
        "old_runtime_sha256": old_runtime_hash,
        "new_runtime_sha256": new_runtime_hash,
        "reuse_policy": {
            "candidate_allowed_selected_risk": CAUCHY_RISK,
            "opendetect_capture_reuse_allowed": True,
            "learned_blend_candidate_capture_reuse_allowed": False,
            "standalone_benchmark_reuse_allowed": False,
            "paired_efficiency_metric_reuse_allowed": False,
        },
        "copied_capture_count": len(copied),
        "skipped_learned_candidate_captures": sorted(skipped_learned),
        "missing_old_captures": sorted(missing_old),
        "copied_captures": copied,
        "unknown_or_test_labels_used": False,
        "valid_for_v4_complete_claim": False,
        "requires_v5_execution_and_summary": True,
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "reuse_complete").touch()
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-protocol", type=Path, required=True)
    parser.add_argument("--new-protocol", type=Path, required=True)
    parser.add_argument("--old-plan", type=Path, required=True)
    parser.add_argument("--new-plan", type=Path, required=True)
    parser.add_argument("--old-root", type=Path, required=True)
    parser.add_argument("--new-root", type=Path, required=True)
    parser.add_argument("--failure", type=Path, required=True)
    parser.add_argument("--archived-old-runtime", type=Path, required=True)
    parser.add_argument("--active-new-runtime", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    audit = prepare_reuse(
        old_protocol_path=args.old_protocol,
        new_protocol_path=args.new_protocol,
        old_plan_path=args.old_plan,
        new_plan_path=args.new_plan,
        old_root=args.old_root,
        new_root=args.new_root,
        failure_path=args.failure,
        archived_old_runtime=args.archived_old_runtime,
        active_new_runtime=args.active_new_runtime,
        output_dir=args.output_dir,
    )
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
