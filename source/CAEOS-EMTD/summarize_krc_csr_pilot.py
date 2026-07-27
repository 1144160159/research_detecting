from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from certify_krc_csr import load
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_csr_caeos_pilot import summarize


def summarize_krc(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    admission: Dict[str, Any],
    certificates: List[Dict[str, Any]],
    evaluation_paths: List[Path],
) -> Dict[str, Any]:
    if (
        protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(certificates) != 14
    ):
        raise ValueError("canonical KRC protocol and 14 certificates required")
    identities = {
        (str(value["suite"]), str(value["scenario"]))
        for value in certificates
    }
    if len(identities) != 14 or any(
        value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        for value in certificates
    ):
        raise ValueError("invalid KRC certificate universe")
    enabled = {
        (str(value["suite"]), str(value["scenario"]))
        for value in certificates
        if value["routing_enabled"] is True
    }
    base = summarize(design, admission, evaluation_paths)
    source_checks = dict(base["checks"])
    source_checks.update(
        {
            "certificate_count_14": True,
            "development_enabled_scenario_count_minimum": (
                len(enabled)
                >= int(
                    protocol["development_gate"][
                        "enabled_scenario_count_minimum"
                    ]
                )
            ),
            "development_enabled_suite_count_minimum": (
                len({suite for suite, _ in enabled})
                >= int(
                    protocol["development_gate"][
                        "enabled_suite_count_minimum"
                    ]
                )
            ),
        }
    )
    base.update(
        {
            "schema_version": "strict_v4_krc_csr_pilot_summary_v1",
            "algorithm": "krc_csr_caeos_v1",
            "krc_protocol_manifest_sha256": protocol["manifest_sha256"],
            "source_csr_summary_manifest_sha256": protocol[
                "source_exact_replay_summary_manifest_sha256"
            ],
            "certificate_count": len(certificates),
            "enabled_scenario_count": len(enabled),
            "enabled_suite_count": len({suite for suite, _ in enabled}),
            "enabled_identities": sorted(
                "/".join(identity) for identity in enabled
            ),
            "checks": source_checks,
            "passes": all(source_checks.values()),
            "expand_to_full102": all(source_checks.values()),
            "claim_boundary": {
                "development_selection_is_report_materialization": True,
                "confirmation_requires_real_runtime_execution": True,
                "pilot_success_does_not_establish_sota": True,
                "primary_confirmation_excludes_14_development_scenarios": True,
            },
        }
    )
    base.pop("manifest_sha256", None)
    base["manifest_sha256"] = canonical_hash(base)
    return base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--certificate-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize_krc(
        load(args.protocol),
        load(args.design),
        load(args.admission),
        [
            load(path)
            for path in sorted(
                args.certificate_root.rglob("certificate.json")
            )
        ],
        sorted(args.evaluation_root.rglob("evaluation.json")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
