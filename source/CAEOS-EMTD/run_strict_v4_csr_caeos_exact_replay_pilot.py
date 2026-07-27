from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from audit_csr_caeos_exact_replay_pilot import audit
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_csr_caeos_exact_replay_runtime import evaluate
from materialize_csr_caeos_exact_replay import (
    load,
    materialize,
    validate_protocol,
)
from summarize_csr_caeos_pilot import summarize


def write_canonical(path: Path, value: Dict[str, Any]) -> None:
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError("canonical output required")
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
    run_root: Path,
    result_root: Path,
    project_root: Path,
) -> Dict[str, Any]:
    protocol = load(protocol_path)
    validate_protocol(protocol)
    design = load(design_path)
    admission = load(admission_path)
    implementation_hashes = {
        name: file_hash(project_root / relative)
        for name, relative in protocol["implementation"].items()
    }
    if implementation_hashes != protocol["implementation_sha256"]:
        raise ValueError("exact-replay implementation differs from protocol")
    if (
        design.get("manifest_sha256") != canonical_hash(design)
        or design.get("manifest_sha256")
        != protocol["design_manifest_sha256"]
        or admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("manifest_sha256")
        != protocol["clean_admission_manifest_sha256"]
        or admission.get("passes") is not True
    ):
        raise ValueError("protocol-bound design and admission required")

    capture_root = run_root / "captures"
    evaluation_root = run_root / "evaluations"
    capture_count = 0
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            source_dir = source_capture_root / suite / scenario
            output_dir = capture_root / suite / scenario
            manifest_path = output_dir / "repair_capture_manifest.json"
            if manifest_path.exists():
                value = load(manifest_path)
                if (
                    value.get("manifest_sha256") != canonical_hash(value)
                    or value.get("repair_protocol_manifest_sha256")
                    != protocol["manifest_sha256"]
                ):
                    raise ValueError("invalid existing exact-replay capture")
            elif output_dir.exists() and any(output_dir.iterdir()):
                raise ValueError("partial exact-replay capture directory")
            else:
                materialize(
                    protocol,
                    source_dir,
                    output_dir,
                    suite=suite,
                    scenario=scenario,
                    materializer_file_sha256=implementation_hashes[
                        "materializer"
                    ],
                    wrapper_file_sha256=implementation_hashes["wrapper"],
                )
            capture_count += 1
            print(
                f"repair_capture={capture_count}/14 "
                f"suite={suite} scenario={scenario}",
                flush=True,
            )

    evaluation_count = 0
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            capture_dir = capture_root / suite / scenario
            for condition in design["development"]["conditions"]:
                output = (
                    evaluation_root
                    / suite
                    / scenario
                    / condition
                    / "evaluation.json"
                )
                if output.exists():
                    value = load(output)
                    if (
                        value.get("manifest_sha256") != canonical_hash(value)
                        or value.get("repair_protocol_manifest_sha256")
                        != protocol["manifest_sha256"]
                    ):
                        raise ValueError(
                            f"invalid existing exact-replay evaluation: {output}"
                        )
                elif output.parent.exists() and any(output.parent.iterdir()):
                    raise ValueError(
                        f"partial exact-replay evaluation directory: {output.parent}"
                    )
                else:
                    evaluate(
                        capture_dir,
                        design,
                        protocol,
                        suite=suite,
                        scenario=scenario,
                        condition=condition,
                        output=output,
                    )
                evaluation_count += 1
                print(
                    f"evaluation={evaluation_count}/84 "
                    f"suite={suite} scenario={scenario} "
                    f"condition={condition}",
                    flush=True,
                )

    evaluation_paths = sorted(
        evaluation_root.rglob("evaluation.json")
    )
    summary = summarize(design, admission, evaluation_paths)
    summary_path = result_root / "summary.json"
    write_canonical(summary_path, summary)
    audited = audit(
        protocol,
        design,
        admission,
        summary,
        sorted(source_capture_root.rglob("capture_manifest.json")),
        sorted(capture_root.rglob("repair_capture_manifest.json")),
        evaluation_paths,
        implementation_file_sha256=implementation_hashes,
    )
    audit_path = result_root / "audit.json"
    write_canonical(audit_path, audited)
    if audited["passes"] is not True:
        raise RuntimeError("CSR exact-replay integrity audit failed")
    (result_root / "pilot_complete").write_text(
        audited["manifest_sha256"] + "\n", encoding="utf-8"
    )
    return {
        "repair_capture_count": capture_count,
        "evaluation_count": evaluation_count,
        "scientific_effect_gate_passes": bool(summary["passes"]),
        "expand_to_full102": bool(summary["expand_to_full102"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--source-capture-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.protocol.resolve(),
        args.design.resolve(),
        args.admission.resolve(),
        args.source_capture_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        args.project_root.resolve(),
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
