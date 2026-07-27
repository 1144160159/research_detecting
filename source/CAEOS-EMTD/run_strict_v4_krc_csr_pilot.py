from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from audit_krc_csr_pilot import audit
from capture_pairwise_runtime import file_hash
from certify_krc_csr import certify, load
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_krc_csr_selection import select
from summarize_krc_csr_pilot import summarize_krc


def write(path: Path, value: Dict[str, Any]) -> None:
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError("canonical KRC output required")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(
    protocol_path: Path,
    design_path: Path,
    admission_path: Path,
    source_capture_root: Path,
    source_evaluation_root: Path,
    run_root: Path,
    result_root: Path,
    project_root: Path,
) -> Dict[str, Any]:
    protocol = load(protocol_path)
    design = load(design_path)
    admission = load(admission_path)
    implementation_sha256 = {
        name: file_hash(project_root / relative)
        for name, relative in protocol["implementation"].items()
    }
    if (
        protocol.get("manifest_sha256") != canonical_hash(protocol)
        or implementation_sha256 != protocol["implementation_sha256"]
    ):
        raise ValueError("canonical implementation-bound KRC protocol required")
    certificates = []
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            value = certify(
                protocol,
                source_capture_root / suite / scenario,
                suite=suite,
                scenario=scenario,
            )
            path = run_root / "certificates" / suite / scenario / "certificate.json"
            write(path, value)
            certificates.append(value)
    cert_by_identity = {
        (value["suite"], value["scenario"]): value
        for value in certificates
    }
    selected_paths = []
    source_items = []
    for source_path in sorted(
        source_evaluation_root.rglob("evaluation.json")
    ):
        source = load(source_path)
        value = select(
            protocol,
            cert_by_identity[(source["suite"], source["scenario"])],
            source,
            source_file_sha256=file_hash(source_path),
        )
        output = (
            run_root
            / "evaluations"
            / source["suite"]
            / source["scenario"]
            / source["condition"]
            / "evaluation.json"
        )
        write(output, value)
        selected_paths.append(output)
        source_items.append((source_path, source))
    summary = summarize_krc(
        protocol, design, admission, certificates, selected_paths
    )
    summary_path = result_root / "summary.json"
    write(summary_path, summary)
    audited = audit(
        protocol,
        design,
        admission,
        [
            (
                run_root
                / "certificates"
                / value["suite"]
                / value["scenario"]
                / "certificate.json",
                value,
            )
            for value in certificates
        ],
        source_items,
        [(path, load(path)) for path in selected_paths],
        summary,
        source_capture_root,
        implementation_sha256,
    )
    audit_path = result_root / "audit.json"
    write(audit_path, audited)
    if audited["passes"] is not True:
        raise RuntimeError("KRC development audit failed")
    (result_root / "pilot_complete").write_text(
        audited["manifest_sha256"] + "\n", encoding="utf-8"
    )
    return {
        "certificate_count": len(certificates),
        "evaluation_count": len(selected_paths),
        "enabled_scenario_count": summary["enabled_scenario_count"],
        "development_gate_passes": summary["passes"],
        "expand_to_full102_confirmation": summary["expand_to_full102"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--source-capture-root", type=Path, required=True)
    parser.add_argument("--source-evaluation-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.protocol.resolve(),
        args.design.resolve(),
        args.admission.resolve(),
        args.source_capture_root.resolve(),
        args.source_evaluation_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        args.project_root.resolve(),
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
