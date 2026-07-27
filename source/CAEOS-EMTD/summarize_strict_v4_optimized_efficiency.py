from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


METRICS = (
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
    "samples_per_second",
)
METHODS = ("original", "optimized", "comparator")


def median_ci(values: list[float], seed: int) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    if array.size != 102 or not np.isfinite(array).all():
        raise ValueError("ratio vector must contain 102 finite values")
    rng = np.random.default_rng(seed)
    samples = np.median(
        array[rng.integers(0, array.size, size=(5000, array.size))], axis=1
    )
    return {
        "n_scenarios": 102,
        "median": float(np.median(array)),
        "bootstrap_95ci": [
            float(np.quantile(samples, 0.025)),
            float(np.quantile(samples, 0.975)),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if (
        protocol.get("schema_version")
        != "strict_v4_optimized_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("optimized efficiency protocol validation failed")
    if protocol["implementation_sha256"].get("triad_summarizer") != file_hash(
        Path(__file__)
    ):
        raise ValueError("active optimized summarizer SHA mismatch")
    if not (args.result_root / "execution_complete").is_file():
        raise ValueError("optimized efficiency matrix is incomplete")
    ratios: dict[str, dict[int, dict[str, list[float]]]] = {
        mode: {
            batch: {
                f"{numerator}_over_{denominator}_{metric}": []
                for numerator, denominator in (
                    ("optimized", "original"),
                    ("optimized", "comparator"),
                    ("original", "comparator"),
                )
                for metric in METRICS
            }
            for batch in (1, 64, 512)
        }
        for mode in protocol["measurement_modes"]
    }
    equivalence_count = 0
    artifact_size_gate_count = 0
    block_count = 0
    for row in protocol["scenarios"]:
        for mode in protocol["measurement_modes"]:
            path = (
                args.result_root
                / row["suite"]
                / row["scenario"]
                / mode
                / "triad_metrics.json"
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            if (
                payload.get("schema_version")
                != "strict_v4_optimized_efficiency_triad_block_v1"
                or payload.get("protocol_manifest_sha256")
                != protocol["manifest_sha256"]
                or payload.get("measurement_mode") != mode
                or payload.get("input_arrays_equal") is not True
                or payload.get("optimized_equivalence", {}).get("passes") is not True
                or payload.get("unknown_or_test_labels_used") is not False
            ):
                raise ValueError(f"invalid optimized block: {path}")
            records = payload.get("records", [])
            if len(records) != 9:
                raise ValueError(f"optimized block records incomplete: {path}")
            artifact_bytes = payload.get("deployment_artifact_bytes", {})
            if (
                int(artifact_bytes.get("original", 0)) <= 0
                or int(artifact_bytes.get("optimized", 0))
                != int(artifact_bytes.get("original", 0))
                or int(artifact_bytes.get("optimized_wrapper_persistent_bytes", -1))
                != 0
                or int(artifact_bytes.get("comparator", 0)) <= 0
            ):
                raise ValueError(f"optimized artifact-size gate failed: {path}")
            by_key = {
                (str(record["method_role"]), int(record["batch_size"])): record
                for record in records
            }
            if set(by_key) != {(method, batch) for method in METHODS for batch in (1, 64, 512)}:
                raise ValueError(f"optimized block record identity mismatch: {path}")
            for batch in (1, 64, 512):
                for numerator, denominator in (
                    ("optimized", "original"),
                    ("optimized", "comparator"),
                    ("original", "comparator"),
                ):
                    for metric in METRICS:
                        left = float(by_key[(numerator, batch)][metric])
                        right = float(by_key[(denominator, batch)][metric])
                        if not np.isfinite(left) or not np.isfinite(right) or right <= 0:
                            raise ValueError(f"invalid timing value in {path}")
                        ratios[mode][batch][
                            f"{numerator}_over_{denominator}_{metric}"
                        ].append(left / right)
            equivalence_count += 1
            artifact_size_gate_count += 1
            block_count += 1
    if (
        block_count != 204
        or equivalence_count != 204
        or artifact_size_gate_count != 204
    ):
        raise ValueError("optimized efficiency coverage is incomplete")
    aggregate = {}
    target_checks = []
    seed = 12000
    for mode in protocol["measurement_modes"]:
        aggregate[mode] = {}
        for batch in (1, 64, 512):
            aggregate[mode][str(batch)] = {}
            for name, values in ratios[mode][batch].items():
                aggregate[mode][str(batch)][name] = median_ci(values, seed)
                seed += 1
            p99 = aggregate[mode][str(batch)][
                "optimized_over_original_latency_p99_ms"
            ]["median"]
            throughput = aggregate[mode][str(batch)][
                "optimized_over_original_samples_per_second"
            ]["median"]
            target_checks.append(p99 <= 0.5 and throughput >= 2.0)
    summary = {
        "schema_version": "strict_v4_optimized_efficiency_summary_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "triad_block_count": block_count,
        "optimized_equivalence_block_count": equivalence_count,
        "artifact_size_gate_block_count": artifact_size_gate_count,
        "aggregate": aggregate,
        "gates": {
            "all_102_scenarios_x_2_modes_complete": True,
            "all_full_input_equivalence_checks_pass": True,
            "optimized_artifact_size_nonincrease_passes": True,
            "two_x_deployment_target_passes": bool(all(target_checks)),
            "two_x_target_checks_passed": int(sum(target_checks)),
            "two_x_target_checks_total": len(target_checks),
        },
        "claim_policy": protocol["claim_policy"],
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary_complete").touch()
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
