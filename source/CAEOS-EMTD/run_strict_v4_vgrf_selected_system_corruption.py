from __future__ import annotations

import argparse
import json
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from evaluate_strict_v4_vgrf_selected_system_corruption import (
    evaluate_record,
)
from run_strict_v4_vgrf_selected_system_seed317 import load


def write_state(
    path: Path,
    *,
    protocol: dict,
    completed: list[dict],
    state: str,
) -> None:
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_corruption_state_v1"
        ),
        "state": state,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_source_pairs": 306,
        "expected_conditions": 1530,
        "completed_source_pairs": len(completed),
        "completed_conditions": 5 * len(completed),
        "blocks": completed,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(protocol.get("source_registry", [])) != 306
    ):
        raise ValueError("invalid selected-system execution protocol")
    active = Path(__file__).resolve()
    if protocol.get("implementation_sha256", {}).get(
        active.name
    ) != file_hash(active):
        raise ValueError("active corruption runner SHA mismatch")
    completed: list[dict] = []
    write_state(
        args.state, protocol=protocol, completed=completed, state="running"
    )
    for record in protocol["source_registry"]:
        output = (
            args.output_root
            / record["suite"]
            / record["scenario"]
            / f"seed{record['seed']}"
            / "paired_corruption.json"
        )
        if output.is_file():
            result = load(output)
            if (
                result.get("manifest_sha256") != canonical_hash(result)
                or result.get("protocol_manifest_sha256")
                != protocol["manifest_sha256"]
                or len(result.get("conditions", [])) != 5
            ):
                raise ValueError("existing corruption block mismatch")
        else:
            result = evaluate_record(record=record, protocol=protocol)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        completed.append(
            {
                "suite": record["suite"],
                "scenario": record["scenario"],
                "seed": int(record["seed"]),
                "output": str(output.resolve()),
                "output_sha256": file_hash(output),
            }
        )
        write_state(
            args.state,
            protocol=protocol,
            completed=completed,
            state="running",
        )
        print(
            f"corrupted {record['suite']}/{record['scenario']}_seed"
            f"{record['seed']}",
            flush=True,
        )
    write_state(
        args.state,
        protocol=protocol,
        completed=completed,
        state="complete",
    )
    (args.state.parent / "corruption_execution_complete").touch()


if __name__ == "__main__":
    main()
