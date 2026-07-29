from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
    require_canonical,
    write_json,
)
from evaluate_strict_v4_selected_system_preconfirmation import (
    clean_source_run,
    evaluate_source,
    split_fingerprint,
)
from run_strict_v4_selected_system_efficiency import (
    opendetect_capture_command,
    run_capture_command,
    validate_opendetect_capture,
)
from run_strict_v4_selected_system_parrot_safety import (
    block_path,
    candidate_capture_command,
    materialize_rrc,
    source_capture_dir,
    validate_source_capture,
)
from summarize_strict_v4_selected_system_preconfirmation import (
    build_summary,
    render,
)
from audit_strict_v4_selected_system_preconfirmation import build_audit


COMPLETION_SCHEMA = "strict_v4_selected_system_preconfirmation_completion_v1"


def require_empty_or_complete(directory: Path, marker: Path) -> None:
    if marker.is_file():
        return
    if directory.exists() and any(directory.iterdir()):
        raise ValueError(f"partial output requires intervention: {directory}")


def run_mahalanobis_pp(
    *,
    protocol: dict[str, Any],
    project_root: Path,
    run_root: Path,
    source: dict[str, Any],
    python: str,
) -> None:
    block = block_path(run_root, source)
    source_run = clean_source_run(protocol, run_root, source)
    output = block / "mahalanobis_pp"
    metrics_path = output / "metrics.json"
    if metrics_path.is_file():
        metrics = load(metrics_path)
        if (
            metrics.get("schema_version")
            != "strict_v4_mlp_mahalanobis_pp_v1"
            or metrics.get("method") != "mahalanobis_pp"
            or split_fingerprint(
                metrics.get("split_metadata", {}).get("split_fingerprint")
            )
            != source["source_split_fingerprint"]
        ):
            raise ValueError("existing Mahalanobis++ output is invalid")
        return
    require_empty_or_complete(output, metrics_path)
    output.mkdir(parents=True, exist_ok=True)
    log_path = output / "execution.log"
    command = [
        python,
        str(project_root / "evaluate_mlp_mahalanobis_pp.py"),
        "--source-run",
        str(source_run),
        "--output-dir",
        str(output),
        "--device",
        "auto",
        "--num-workers",
        "0",
    ]
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write(json.dumps({"command": command}) + "\n")
        log.flush()
        completed = subprocess.run(
            [*protocol["resource_contract"]["subprocess_prefix"], *command],
            cwd=project_root,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0 or not metrics_path.is_file():
        raise RuntimeError(f"Mahalanobis++ evaluation failed: {output}")
    metrics = load(metrics_path)
    if (
        metrics.get("schema_version") != "strict_v4_mlp_mahalanobis_pp_v1"
        or metrics.get("method") != "mahalanobis_pp"
        or split_fingerprint(
            metrics.get("split_metadata", {}).get("split_fingerprint")
        )
        != source["source_split_fingerprint"]
    ):
        raise ValueError("new Mahalanobis++ output is invalid")


def execute(
    *,
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    python: str,
) -> dict[str, Any]:
    protocol = load(protocol_path)
    require_canonical(protocol, PROTOCOL_SCHEMA, "preconfirmation protocol")
    if (
        protocol.get("execution_admitted") is not True
        or protocol.get("run_root") != run_root.resolve().as_posix()
        or os.environ.get(
            "SELECTED_SYSTEM_PRECONFIRMATION_EXCLUSIVE_MACHINE_GATE"
        )
        != "passed"
    ):
        raise ValueError("preconfirmation exclusive-machine gate is required")
    for relative, expected in protocol["implementation_sha256"].items():
        path = project_root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    prefix = list(protocol["resource_contract"]["subprocess_prefix"])
    selected = protocol["selected_algorithm"]

    for source in protocol["sources"]:
        directory = source_capture_dir(run_root, source, selected)
        marker = directory / "capture_manifest.json"
        if not marker.is_file():
            require_empty_or_complete(directory, marker)
            run_capture_command(
                command=candidate_capture_command(
                    python=python,
                    project_root=project_root,
                    run_root=run_root,
                    protocol=protocol,
                    source=source,
                ),
                directory=directory,
                prefix=prefix,
                method=selected,
                source=source,
            )
    if selected == "rrc_csr_caeos_v1":
        materialize_rrc(protocol, run_root)
    for source in protocol["sources"]:
        if not validate_source_capture(protocol, run_root, source):
            raise FileNotFoundError("candidate capture is incomplete")

    for source in protocol["sources"]:
        run_mahalanobis_pp(
            protocol=protocol,
            project_root=project_root,
            run_root=run_root,
            source=source,
            python=python,
        )
        block = block_path(run_root, source)
        directory = block / "opendetect_capture"
        marker = directory / "capture_manifest.json"
        if not marker.is_file():
            require_empty_or_complete(directory, marker)
            run_capture_command(
                command=opendetect_capture_command(
                    python=python,
                    project_root=project_root,
                    run_root=run_root,
                    protocol=protocol,
                    source=source,
                ),
                directory=directory,
                prefix=prefix,
                method="opendetect",
                source=source,
            )
        validate_opendetect_capture(protocol, run_root, source)

    for source in protocol["sources"]:
        output = block_path(run_root, source) / "preconfirmation.json"
        if output.is_file():
            existing = load(output)
            if (
                existing.get("manifest_sha256") != canonical_hash(existing)
                or existing.get("protocol_manifest_sha256")
                != protocol["manifest_sha256"]
                or existing.get("selected_algorithm") != selected
            ):
                raise ValueError(f"existing task record is invalid: {output}")
            continue
        value = evaluate_source(
            protocol=protocol,
            project_root=project_root,
            run_root=run_root,
            source=source,
        )
        write_json(output, value)

    result_root.mkdir(parents=True, exist_ok=True)
    summary = build_summary(protocol=protocol, run_root=run_root)
    summary_path = result_root / "summary.json"
    write_json(summary_path, summary)
    with (result_root / "summary.md").open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(render(summary))
    audit = build_audit(
        project_root=project_root,
        protocol_path=protocol_path,
        summary_path=summary_path,
        run_root=run_root,
    )
    audit_path = result_root / "audit.json"
    write_json(audit_path, audit)
    completion: dict[str, Any] = {
        "schema_version": COMPLETION_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "audit_manifest_sha256": audit["manifest_sha256"],
        "audit_file_sha256": file_hash(audit_path),
        "selected_algorithm": selected,
        "integrity_passes": audit["passes"],
        "classic_main_gate_passes": audit["classic_main_gate_passes"],
        "absolute_corruption_gate_passes": audit[
            "absolute_corruption_gate_passes"
        ],
        "comparative_corruption_gate_passes": audit[
            "comparative_corruption_gate_passes"
        ],
        "all_three_effect_gates_pass": audit["all_three_effect_gates_pass"],
        "selective_unknown_detection_sota_authorized": audit[
            "selective_unknown_detection_sota_authorized"
        ],
        "selective_corruption_robustness_sota_authorized": audit[
            "selective_corruption_robustness_sota_authorized"
        ],
        "any_selective_sota_authorized": audit[
            "any_selective_sota_authorized"
        ],
        "negative_result_is_terminal_and_reportable": True,
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    write_json(result_root / "execution_complete.json", completion)
    return completion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_preconfirmation_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("runs/strict_v4_selected_system_preconfirmation_v1"),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path("results/strict_v4_selected_system_preconfirmation_v1"),
    )
    parser.add_argument("--python", default=sys.executable)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else (root / path).resolve()

    completion = execute(
        protocol_path=resolve(args.protocol),
        project_root=root,
        run_root=resolve(args.run_root),
        result_root=resolve(args.result_root),
        python=args.python,
    )
    print(json.dumps(completion, sort_keys=True))


if __name__ == "__main__":
    main()
