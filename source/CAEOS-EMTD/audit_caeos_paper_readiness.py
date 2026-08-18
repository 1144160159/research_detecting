from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Iterable


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def nested_artifact_state(
    output_root: Path, paths: Iterable[str], *, require_gate_pass: bool
) -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    for relative in paths:
        path = output_root / relative
        state: dict[str, Any] = {
            "path": relative,
            "exists": path.is_file(),
            "requires_gate_pass": require_gate_pass,
        }
        if require_gate_pass and path.is_file():
            try:
                state["gate_pass"] = load_json(path).get("gate_pass") is True
            except (OSError, ValueError, json.JSONDecodeError) as error:
                state["gate_pass"] = False
                state["error"] = f"{type(error).__name__}: {error}"
        state["passes"] = state["exists"] and (
            not require_gate_pass or state.get("gate_pass") is True
        )
        states.append(state)
    return states


def active_feature_processes() -> dict[str, dict[str, Any]]:
    active: dict[str, dict[str, Any]] = {}
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return active
    for process in proc_root.iterdir():
        if not process.name.isdigit():
            continue
        try:
            arguments = [
                item.decode("utf-8", "replace")
                for item in (process / "cmdline").read_bytes().split(b"\0")
                if item
            ]
            if (
                "prepare_caeos_splitpcap_class_csv.py" not in arguments
                or "--dataset" not in arguments
            ):
                continue
            dataset_id = arguments[arguments.index("--dataset") + 1]
            active[dataset_id] = {
                "pid": int(process.name),
            }
        except (OSError, ValueError):
            continue
    return active


def check_class_csv(item: dict[str, Any], *, check_files: bool) -> dict[str, Any]:
    verification = item.get("verification") or {}
    label_counts = verification.get("label_status_counts") or {}
    label_statuses_admitted = bool(label_counts) and all(
        str(name).startswith("aligned_unique_") for name in label_counts
    )
    file_state: dict[str, Any] = {"checked": check_files}
    if check_files:
        path = Path(str(item.get("path", "")))
        file_state.update(
            {
                "exists": path.is_file(),
                "size_matches": path.is_file()
                and path.stat().st_size == item.get("size_bytes"),
            }
        )
    checks = {
        "attack_category_present": bool(item.get("attack_category")),
        "positive_rows": isinstance(item.get("rows"), int) and item["rows"] > 0,
        "sha256_present": isinstance(item.get("sha256"), str)
        and len(item["sha256"]) == 64,
        "full_row_validation": verification.get("full_row_validation") is True,
        "label_statuses_admitted": label_statuses_admitted,
    }
    if check_files:
        checks["file_exists"] = bool(file_state.get("exists"))
        checks["size_matches"] = bool(file_state.get("size_matches"))
    return {
        "attack_category": item.get("attack_category"),
        "rows": item.get("rows"),
        "checks": checks,
        "file": file_state,
        "passes": all(checks.values()),
    }


def check_dataset_manifest(
    output_root: Path,
    dataset: dict[str, Any],
    required_fields: Iterable[str],
    *,
    check_files: bool,
) -> dict[str, Any]:
    dataset_id = str(dataset["id"])
    path = output_root / dataset_id / "dataset.manifest.json"
    result: dict[str, Any] = {
        "dataset_id": dataset_id,
        "paper_role": dataset["role"],
        "manifest_path": str(path),
        "manifest_exists": path.is_file(),
        "required_for_development": bool(dataset.get("required_for_development")),
    }
    if not path.is_file():
        result.update({"complete": False, "passes_manifest_gate": False})
        return result
    try:
        manifest = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result.update(
            {
                "complete": False,
                "passes_manifest_gate": False,
                "error": f"{type(error).__name__}: {error}",
            }
        )
        return result

    missing_fields = [name for name in required_fields if manifest.get(name) is None]
    class_csvs = [
        check_class_csv(item, check_files=check_files)
        for item in manifest.get("class_csvs", [])
        if isinstance(item, dict)
    ]
    row_sum = sum(item.get("rows") or 0 for item in manifest.get("class_csvs", []))
    exclusion = manifest.get("label_exclusion_summary") or {}
    maximum_excluded_packet_fraction = (
        (manifest.get("processing_policy") or {})
        .get("label_alignment", {})
        .get("maximum_excluded_packet_fraction")
    )
    observed_excluded_packet_fraction = exclusion.get("excluded_packet_fraction")
    exclusion_within_policy = (
        maximum_excluded_packet_fraction is None
        or (
            isinstance(observed_excluded_packet_fraction, (int, float))
            and observed_excluded_packet_fraction <= maximum_excluded_packet_fraction
        )
    )
    checks = {
        "complete": manifest.get("complete") is True,
        "dataset_id_matches": manifest.get("dataset_id") == dataset_id,
        "required_fields_present": not missing_fields,
        "positive_row_count": isinstance(manifest.get("row_count"), int)
        and manifest["row_count"] > 0,
        "class_csvs_present": bool(class_csvs),
        "class_csvs_pass": bool(class_csvs)
        and all(item["passes"] for item in class_csvs),
        "class_row_sum_matches": row_sum == manifest.get("row_count"),
        "exclusion_within_declared_policy": exclusion_within_policy,
    }
    result.update(
        {
            "complete": manifest.get("complete") is True,
            "row_count": manifest.get("row_count"),
            "class_csv_count": len(class_csvs),
            "manifest_sha256": manifest.get("manifest_sha256"),
            "missing_required_fields": missing_fields,
            "class_csvs": class_csvs,
            "checks": checks,
            "passes_manifest_gate": all(checks.values()),
        }
    )
    return result


def build_report(
    contract: dict[str, Any], output_root: Path, *, check_files: bool
) -> dict[str, Any]:
    d0 = contract["gates"]["D0"]
    datasets = [
        check_dataset_manifest(
            output_root,
            dataset,
            d0["required_dataset_manifest_fields"],
            check_files=check_files,
        )
        for dataset in contract["datasets"]
    ]
    development = [item for item in datasets if item["required_for_development"]]
    required_artifacts = {
        gate_id: {
            "presence": nested_artifact_state(
                output_root,
                gate.get("required_presence_artifacts", []),
                require_gate_pass=False,
            ),
            "gate": nested_artifact_state(
                output_root,
                gate.get("required_gate_artifacts", []),
                require_gate_pass=True,
            ),
        }
        for gate_id, gate in contract["gates"].items()
        if gate.get("required_presence_artifacts")
        or gate.get("required_gate_artifacts")
    }
    d0_states = required_artifacts.get("D0", {"presence": [], "gate": []})
    p0_states = required_artifacts.get("P0", {"presence": [], "gate": []})
    d0_artifacts_pass = all(
        item["passes"] for values in d0_states.values() for item in values
    )
    p0_artifacts_pass = all(
        item["passes"] for values in p0_states.values() for item in values
    )
    all_manifests_pass = all(item["passes_manifest_gate"] for item in datasets)
    development_manifests_pass = bool(development) and all(
        item["passes_manifest_gate"] for item in development
    )
    return {
        "schema_version": "caeos_paper_readiness_audit_v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contract_schema_version": contract["schema_version"],
        "output_root": str(output_root),
        "check_files": check_files,
        "active_feature_processes": active_feature_processes(),
        "datasets": datasets,
        "summary": {
            "dataset_count": len(datasets),
            "complete_manifest_count": sum(
                bool(item["complete"]) for item in datasets
            ),
            "passing_manifest_count": sum(
                bool(item["passes_manifest_gate"]) for item in datasets
            ),
            "development_manifest_ready": development_manifests_pass,
            "paper_inventory_manifest_ready": all_manifests_pass,
            "D0_artifacts_ready": d0_artifacts_pass,
            "P0_artifacts_ready": p0_artifacts_pass,
            "D0_pass": all_manifests_pass and d0_artifacts_pass,
            "P0_pass": all_manifests_pass
            and d0_artifacts_pass
            and p0_artifacts_pass,
            "F0_authorized": all_manifests_pass
            and d0_artifacts_pass
            and p0_artifacts_pass,
        },
        "required_artifacts": required_artifacts,
    }


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    report = build_report(
        load_json(args.contract), args.output_root, check_files=args.check_files
    )
    if args.output:
        write_atomic(args.output, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
