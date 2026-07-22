from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


def valid_output(path: Path, protocol_sha: str, mode: str) -> bool:
    if not path.is_file():
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    return (
        payload.get("schema_version")
        == "strict_v4_optimized_efficiency_triad_block_v1"
        and payload.get("protocol_manifest_sha256") == protocol_sha
        and payload.get("measurement_mode") == mode
        and payload.get("input_arrays_equal") is True
        and payload.get("optimized_equivalence", {}).get("passes") is True
        and payload.get("unknown_or_test_labels_used") is False
        and len(payload.get("records", [])) == 9
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--v5-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--block-runner", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if (
        protocol.get("schema_version")
        != "strict_v4_optimized_efficiency_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("optimized efficiency protocol validation failed")
    if protocol["implementation_sha256"].get("triad_matrix_runner") != file_hash(
        Path(__file__)
    ):
        raise ValueError("active matrix runner SHA mismatch")
    if protocol["implementation_sha256"].get("triad_block_runner") != file_hash(
        args.block_runner
    ):
        raise ValueError("active block runner SHA mismatch")
    expected = 0
    for row in protocol["scenarios"]:
        suite, scenario = row["suite"], row["scenario"]
        source = args.v5_root / "inference" / suite / scenario
        for mode, comparator_dir in (
            ("native_primary", "comparator_native_capture"),
            ("cpu_normalized_secondary", "comparator_cpu_capture"),
        ):
            expected += 1
            output = args.output_root / suite / scenario / mode / "triad_metrics.json"
            if valid_output(output, protocol["manifest_sha256"], mode):
                continue
            command = [
                sys.executable,
                str(args.block_runner),
                "--protocol",
                str(args.protocol),
                "--candidate-capture",
                str(source / "candidate_capture"),
                "--comparator-capture",
                str(source / comparator_dir),
                "--measurement-mode",
                mode,
                "--output",
                str(output),
            ]
            output.parent.mkdir(parents=True, exist_ok=True)
            with (output.parent / "execution.log").open("a", encoding="utf-8") as log:
                subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
            if not valid_output(output, protocol["manifest_sha256"], mode):
                raise ValueError(f"triad block failed validation: {output}")
    observed = sum(1 for _ in args.output_root.rglob("triad_metrics.json"))
    if observed != expected or expected != 204:
        raise ValueError(f"optimized matrix incomplete: {observed}/{expected}")
    (args.output_root / "execution_complete").touch()


if __name__ == "__main__":
    main()
