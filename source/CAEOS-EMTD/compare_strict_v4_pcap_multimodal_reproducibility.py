from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


EXCLUDED_KEYS = {
    "elapsed_seconds",
    "family_crossfit_model_path",
    "family_crossfit_model_sha256",
    "manifest_sha256",
    "path",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scrub_runtime_evidence(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: scrub_runtime_evidence(item)
            for key, item in sorted(value.items())
            if key not in EXCLUDED_KEYS and key != "gpu_execution"
        }
    if isinstance(value, list):
        return [scrub_runtime_evidence(item) for item in value]
    return value


def compare_scores(left_path: Path, right_path: Path) -> dict[str, Any]:
    arrays = {}
    with (
        np.load(left_path, allow_pickle=False) as left,
        np.load(right_path, allow_pickle=False) as right,
    ):
        left_names = set(left.files)
        right_names = set(right.files)
        for name in sorted(left_names | right_names):
            if name not in left_names or name not in right_names:
                arrays[name] = {
                    "present_left": name in left_names,
                    "present_right": name in right_names,
                    "exact": False,
                }
                continue
            left_array = np.asarray(left[name])
            right_array = np.asarray(right[name])
            same_shape = left_array.shape == right_array.shape
            same_dtype = left_array.dtype == right_array.dtype
            exact = bool(
                same_shape
                and same_dtype
                and np.array_equal(left_array, right_array)
            )
            block: dict[str, Any] = {
                "shape_left": list(left_array.shape),
                "shape_right": list(right_array.shape),
                "dtype_left": str(left_array.dtype),
                "dtype_right": str(right_array.dtype),
                "exact": exact,
            }
            if (
                same_shape
                and np.issubdtype(left_array.dtype, np.number)
                and np.issubdtype(right_array.dtype, np.number)
            ):
                difference = np.abs(
                    left_array.astype(np.float64)
                    - right_array.astype(np.float64)
                )
                block["maximum_absolute_difference"] = float(
                    difference.max(initial=0.0)
                )
            arrays[name] = block
    return {
        "left_file_sha256": file_hash(left_path),
        "right_file_sha256": file_hash(right_path),
        "array_names_exact": left_names == right_names,
        "arrays": arrays,
        "all_arrays_exact": bool(
            left_names == right_names
            and all(item["exact"] for item in arrays.values())
        ),
    }


def compare_metrics(left_path: Path, right_path: Path) -> dict[str, Any]:
    left = json.loads(left_path.read_text(encoding="utf-8"))
    right = json.loads(right_path.read_text(encoding="utf-8"))
    left_core = scrub_runtime_evidence(left)
    right_core = scrub_runtime_evidence(right)
    return {
        "left_file_sha256": file_hash(left_path),
        "right_file_sha256": file_hash(right_path),
        "excluded_runtime_keys": sorted(EXCLUDED_KEYS | {"gpu_execution"}),
        "core_metrics_exact": left_core == right_core,
    }


def compare_roots(left_root: Path, right_root: Path) -> dict[str, Any]:
    left_root = left_root.resolve()
    right_root = right_root.resolve()
    left_scenarios = {
        path.name[: -len("_metrics.json")]
        for path in left_root.glob("*_metrics.json")
    }
    right_scenarios = {
        path.name[: -len("_metrics.json")]
        for path in right_root.glob("*_metrics.json")
    }
    scenarios = {}
    for scenario in sorted(left_scenarios | right_scenarios):
        left_metrics = left_root / f"{scenario}_metrics.json"
        right_metrics = right_root / f"{scenario}_metrics.json"
        left_scores = left_root / f"{scenario}_scores.npz"
        right_scores = right_root / f"{scenario}_scores.npz"
        required = (left_metrics, right_metrics, left_scores, right_scores)
        if not all(path.is_file() for path in required):
            scenarios[scenario] = {
                "complete_pair": False,
                "missing": [
                    str(path)
                    for path in required
                    if not path.is_file()
                ],
                "passed": False,
            }
            continue
        metrics = compare_metrics(left_metrics, right_metrics)
        scores = compare_scores(left_scores, right_scores)
        scenarios[scenario] = {
            "complete_pair": True,
            "metrics": metrics,
            "scores": scores,
            "passed": bool(
                metrics["core_metrics_exact"]
                and scores["all_arrays_exact"]
            ),
        }
    passed = bool(
        left_scenarios == right_scenarios
        and scenarios
        and all(block["passed"] for block in scenarios.values())
    )
    payload: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_reproducibility_comparison_v1"
        ),
        "state": "complete",
        "left_root": str(left_root),
        "right_root": str(right_root),
        "scenario_names_exact": left_scenarios == right_scenarios,
        "scenarios": scenarios,
        "reproducibility_passed": passed,
        "claim_boundary": {
            "requires_exact_score_arrays": True,
            "requires_core_metrics_after_runtime_scrub": True,
            "does_not_compare_wall_clock_or_gpu_sampler_evidence": True,
            "does_not_compare_output_paths_or_serialized_model_bytes": True,
        },
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    payload["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-root", type=Path, required=True)
    parser.add_argument("--right-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = compare_roots(args.left_root, args.right_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest_sha256": payload["manifest_sha256"],
                "output": str(args.output.resolve()),
                "reproducibility_passed": payload[
                    "reproducibility_passed"
                ],
                "scenario_names": sorted(payload["scenarios"]),
            },
            sort_keys=True,
        )
    )
    if not payload["reproducibility_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
