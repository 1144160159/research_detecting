from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from certify_krc_csr import load
from create_strict_v4_external_confirmation_protocol import canonical_hash


def select(
    protocol: Dict[str, Any],
    certificate: Dict[str, Any],
    source: Dict[str, Any],
    *,
    source_file_sha256: str,
) -> Dict[str, Any]:
    identity = f"{source.get('suite')}/{source.get('scenario')}"
    if (
        protocol.get("manifest_sha256") != canonical_hash(protocol)
        or certificate.get("manifest_sha256")
        != canonical_hash(certificate)
        or certificate.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or source.get("manifest_sha256") != canonical_hash(source)
        or source.get("runtime_revision")
        != "exact_clean_probability_replay_v2"
        or source.get("repair_protocol_manifest_sha256")
        != protocol["source_exact_replay_protocol_manifest_sha256"]
        or source_file_sha256
        != protocol["source_evaluation_file_sha256"].get(
            f"{identity}/{source.get('condition')}"
        )
    ):
        raise ValueError("protocol-bound KRC source evidence required")
    enabled = bool(certificate["routing_enabled"])
    value = copy.deepcopy(source)
    value.update(
        {
            "algorithm": "krc_csr_caeos_v1",
            "runtime_revision": "known_only_reliability_certificate_v1",
            "krc_protocol_manifest_sha256": protocol["manifest_sha256"],
            "certificate_manifest_sha256": certificate[
                "manifest_sha256"
            ],
            "source_exact_replay_evaluation_manifest_sha256": source[
                "manifest_sha256"
            ],
            "source_exact_replay_evaluation_file_sha256": (
                source_file_sha256
            ),
            "routing_enabled_by_known_only_certificate": enabled,
            "development_selection_materialization": (
                "select exact source CSR report when enabled; otherwise "
                "select exact Pairwise report"
            ),
        }
    )
    if not enabled:
        value["candidate_report"] = copy.deepcopy(
            source["pairwise_report"]
        )
        value["routing"] = {
            "active_count": 0,
            "active_rate": 0.0,
            "missing_count": int(source["routing"]["missing_count"]),
            "missing_rate": float(source["routing"]["missing_rate"]),
            "prediction_exactly_pairwise_all_rows": True,
            "probability_exactly_pairwise_all_rows": True,
            "risk_monotone_not_below_pairwise": True,
            "inactive_risk_exactly_pairwise": True,
            "unknown_or_test_labels_used": False,
        }
    value.pop("manifest_sha256", None)
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source-evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = select(
        load(args.protocol),
        load(args.certificate),
        load(args.source_evaluation),
        source_file_sha256=file_hash(args.source_evaluation),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
