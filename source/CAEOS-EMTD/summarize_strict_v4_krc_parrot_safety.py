from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_mdr_parrot_safety import aggregate as mdr_aggregate


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def rename_krc(value: Any) -> Any:
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            name = str(key).replace("mdr_caeos_v1", "krc_csr_caeos_v1")
            if name.startswith("mdr_"):
                name = "krc_" + name[4:]
            output[name] = rename_krc(item)
        return output
    if isinstance(value, list):
        return [rename_krc(item) for item in value]
    return value


def aggregate(
    records: list[Dict[str, Any]], protocol: Dict[str, Any]
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_parrot_safety_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(records) != 30
    ):
        raise ValueError("canonical KRC protocol and 30 model pairs required")
    translated_protocol = deepcopy(protocol)
    translated_protocol["schema_version"] = (
        "strict_v4_mdr_parrot_safety_protocol_v1"
    )
    translated_protocol["selected_algorithm"] = "mdr_caeos_v1"
    translated_protocol["manifest_sha256"] = canonical_hash(
        translated_protocol
    )
    translated_records = []
    for record in records:
        value = deepcopy(record)
        if (
            value.get("schema_version")
            != "strict_v4_krc_parrot_model_pair_metrics_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or value.get("candidate_model_refit_for_parrot") is not False
        ):
            raise ValueError("invalid KRC PARROT model-pair metrics")
        value["schema_version"] = (
            "strict_v4_mdr_parrot_model_pair_metrics_v1"
        )
        value["protocol_manifest_sha256"] = translated_protocol[
            "manifest_sha256"
        ]
        for capture in value["records"]:
            capture["mdr_caeos_v1"] = capture.pop("krc_csr_caeos_v1")
        value.pop("candidate_model_refit_for_parrot", None)
        value["manifest_sha256"] = canonical_hash(value)
        translated_records.append(value)
    return rename_krc(mdr_aggregate(translated_records, translated_protocol))


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    records = []
    registry = []
    for source in protocol["source_model_pairs"]:
        path = (
            run_root
            / "evaluations"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
            / "model_pair_metrics.json"
        )
        if not path.is_file():
            raise FileNotFoundError(f"missing KRC PARROT metrics: {path}")
        records.append(load(path))
        registry.append(
            {
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "opendetect_training_seed": int(
                    source["opendetect_training_seed"]
                ),
                "metrics_file_sha256": file_hash(path),
            }
        )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_parrot_safety_summary_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate(records, protocol),
        "model_pair_metrics_file_registry": registry,
        "claim_boundary": {
            "successful_gate_allows": (
                "cross_domain_benign_false_alert_safety_noninferiority"
            ),
            "does_not_support_malicious_accuracy_or_parrot_sota": True,
            "does_not_replace_malicious_external_confirmation": True,
            "candidate_model_refit_for_parrot": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(load(args.protocol), args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
