from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from certify_krc_csr import certify, load
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_krc_csr_selection import select
from summarize_krc_csr_pilot import summarize_krc


def audit(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    admission: Dict[str, Any],
    certificates: list[tuple[Path, Dict[str, Any]]],
    sources: list[tuple[Path, Dict[str, Any]]],
    selected: list[tuple[Path, Dict[str, Any]]],
    summary: Dict[str, Any],
    source_capture_root: Path,
    implementation_sha256: Dict[str, str],
) -> Dict[str, Any]:
    cert_by_identity = {
        (value["suite"], value["scenario"]): value
        for _, value in certificates
    }
    source_by_identity = {
        (value["suite"], value["scenario"], value["condition"]): (
            path,
            value,
        )
        for path, value in sources
    }
    selected_by_identity = {
        (value["suite"], value["scenario"], value["condition"]): value
        for _, value in selected
    }
    cert_exact = True
    for identity, value in cert_by_identity.items():
        expected = certify(
            protocol,
            source_capture_root / identity[0] / identity[1],
            suite=identity[0],
            scenario=identity[1],
        )
        cert_exact = cert_exact and value == expected
    selection_exact = True
    for identity, (path, source) in source_by_identity.items():
        expected = select(
            protocol,
            cert_by_identity[identity[:2]],
            source,
            source_file_sha256=file_hash(path),
        )
        selection_exact = (
            selection_exact
            and selected_by_identity.get(identity) == expected
        )
    recomputed = summarize_krc(
        protocol,
        design,
        admission,
        list(cert_by_identity.values()),
        [path for path, _ in selected],
    )
    checks = {
        "protocol_canonical": (
            protocol["manifest_sha256"] == canonical_hash(protocol)
        ),
        "implementation_hashes_exactly_bound": (
            implementation_sha256 == protocol["implementation_sha256"]
        ),
        "certificate_count_14": len(certificates) == 14,
        "certificates_exactly_recomputed_known_only": cert_exact,
        "source_evaluation_count_84": len(sources) == 84,
        "selection_evaluation_count_84": len(selected) == 84,
        "selections_exactly_recomputed": selection_exact,
        "summary_exactly_recomputed": summary == recomputed,
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_pilot_audit_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "implementation_file_sha256": implementation_sha256,
        "checks": checks,
        "passes": all(checks.values()),
        "scientific_development_gate_passes": bool(summary["passes"]),
        "expand_to_full102_confirmation": bool(summary["expand_to_full102"]),
        "claim_boundary": {
            "audit_passes_means_integrity_only": True,
            "development_pass_does_not_establish_sota": True,
            "confirmation_requires_real_runtime_execution": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--certificate-root", type=Path, required=True)
    parser.add_argument("--source-evaluation-root", type=Path, required=True)
    parser.add_argument("--selection-evaluation-root", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--source-capture-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    value = audit(
        protocol,
        load(args.design),
        load(args.admission),
        [
            (path, load(path))
            for path in sorted(
                args.certificate_root.rglob("certificate.json")
            )
        ],
        [
            (path, load(path))
            for path in sorted(
                args.source_evaluation_root.rglob("evaluation.json")
            )
        ],
        [
            (path, load(path))
            for path in sorted(
                args.selection_evaluation_root.rglob("evaluation.json")
            )
        ],
        load(args.summary),
        args.source_capture_root.resolve(),
        {
            name: file_hash(args.project_root / relative)
            for name, relative in protocol["implementation"].items()
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
