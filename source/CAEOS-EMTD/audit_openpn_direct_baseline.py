from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EVIDENCE_SCHEMA = "strict_v4_openpn_direct_baseline_evidence_v1"
AUDIT_SCHEMA = "strict_v4_openpn_direct_baseline_audit_v1"
DOI = "10.1177/0926227X251414058"
TITLE = (
    "An expert-in-the-loop framework for unknown attack detection via "
    "open-set recognition"
)


def canonical_hash(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("manifest_sha256", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_evidence(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_evidence(value)
    return value


def validate_evidence(value: dict[str, Any]) -> None:
    if value.get("schema_version") != EVIDENCE_SCHEMA:
        raise ValueError("unsupported OpenPN evidence schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError("OpenPN evidence manifest SHA mismatch")

    publication = value.get("publication", {})
    if publication.get("doi") != DOI:
        raise ValueError("OpenPN DOI identity mismatch")
    if publication.get("title") != TITLE:
        raise ValueError("OpenPN title identity mismatch")
    if publication.get("venue") != "Journal of Computer Security":
        raise ValueError("OpenPN venue identity mismatch")
    if publication.get("volume") != "34" or publication.get("issue") != "3":
        raise ValueError("OpenPN issue identity mismatch")
    if publication.get("pages") != "193-210":
        raise ValueError("OpenPN page identity mismatch")
    if publication.get("first_published_online") != "2026-02-10":
        raise ValueError("OpenPN publication date mismatch")
    if publication.get("restricted_access") is not True:
        raise ValueError("OpenPN publisher access status is not frozen")

    openalex = value.get("openalex", {})
    required_closed_access = {
        "is_oa": False,
        "oa_status": "closed",
        "best_oa_location": None,
        "any_repository_has_fulltext": False,
        "has_fulltext": False,
        "pdf_url": None,
    }
    for key, expected in required_closed_access.items():
        if openalex.get(key) != expected:
            raise ValueError(f"OpenPN OpenAlex field mismatch: {key}")

    claims = value.get("publisher_abstract_contract", {})
    required_claims = (
        "openpn_recognizes_known_and_unknown_traffic",
        "expert_verification_is_used_after_detection",
        "density_based_k_reciprocal_clustering_is_used",
        "continuous_learning_uses_verified_novel_attacks",
        "experiments_reported_on_three_public_datasets",
    )
    for key in required_claims:
        if claims.get(key) is not True:
            raise ValueError(f"OpenPN abstract contract is incomplete: {key}")

    discovery = value.get("implementation_discovery", {})
    queries = discovery.get("github_repository_queries", [])
    if len(queries) < 3:
        raise ValueError("OpenPN repository search coverage is incomplete")
    if any(
        not isinstance(item.get("total_count"), int)
        or item["total_count"] != 0
        for item in queries
    ):
        raise ValueError("OpenPN repository search result is not frozen")
    if discovery.get("verified_author_implementation_found") is not False:
        raise ValueError("OpenPN author implementation status is invalid")
    if discovery.get("negative_search_not_proof_of_absence") is not True:
        raise ValueError("OpenPN negative-search limitation is missing")
    if discovery.get("github_code_search_authenticated") is not False:
        raise ValueError("OpenPN GitHub code-search boundary is invalid")


def build_audit(evidence: dict[str, Any]) -> dict[str, Any]:
    validate_evidence(evidence)
    native_gates = {
        "official_paper_identity_verified": True,
        "full_text_available_for_method_audit": False,
        "verified_author_implementation_available": False,
        "exact_model_and_loss_reconstructable": False,
        "exact_dataset_preprocessing_and_class_lists_available": False,
        "exact_split_seed_and_selection_protocol_available": False,
    }
    strict_gates = {
        "static_openpn_stage_isolatable_from_adaptation": False,
        "zero_unknown_validation_or_selection_exposure_verified": False,
        "unknown_labels_hidden_from_training_and_selection_verified": False,
        "same_group_disjoint_split_contract_verified": False,
        "same_flow_level_no_payload_input_contract_verified": False,
        "strict_v4_metrics_reproducible": False,
    }
    full_framework_gates = {
        "expert_verified_unknowns_used_for_continual_learning": True,
        "zero_unknown_exposure_static_benchmark_compatible": False,
    }
    native_admitted = all(native_gates.values())
    strict_admitted = native_admitted and all(strict_gates.values())
    value: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA,
        "evidence_manifest_sha256": evidence["manifest_sha256"],
        "publication_identity": {
            "doi": DOI,
            "title": TITLE,
            "venue": evidence["publication"]["venue"],
            "volume": evidence["publication"]["volume"],
            "issue": evidence["publication"]["issue"],
            "pages": evidence["publication"]["pages"],
            "first_published_online": evidence["publication"][
                "first_published_online"
            ],
            "publisher_access": "restricted",
            "openalex_oa_status": evidence["openalex"]["oa_status"],
        },
        "publisher_abstract_contract": evidence[
            "publisher_abstract_contract"
        ],
        "implementation_discovery": evidence["implementation_discovery"],
        "native_reproduction_gates": native_gates,
        "strict_v4_main_table_gates": strict_gates,
        "published_full_framework_boundary": full_framework_gates,
        "native_execution_admitted": native_admitted,
        "strict_v4_main_table_admitted": strict_admitted,
        "initial_openpn_static_stage_candidate": True,
        "initial_stage_candidate_requires_full_text_or_author_code": True,
        "published_full_framework_main_table_admitted": False,
        "related_work_admitted": True,
        "online_adaptation_future_work_admitted": True,
        "model_metrics_generated": False,
        "baseline_count_increment": 0,
        "evidence_limitations": [
            "publisher full text was restricted during this audit",
            "OpenAlex reports no open or repository full-text location",
            "repository and public-web searches did not verify author code",
            "negative repository search is not proof that code does not exist",
            "abstract evidence cannot establish model, threshold, split, or "
            "dataset details",
        ],
        "decision": (
            "admit OpenPN as related-work and an online-adaptation boundary; "
            "do not execute, count, or rank it in strict-v4; reconsider only "
            "the initial static OpenPN stage after full text or verified "
            "author code makes its zero-unknown protocol reconstructable"
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("OpenPN audit output already exists")
    value = build_audit(load_evidence(args.evidence.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
