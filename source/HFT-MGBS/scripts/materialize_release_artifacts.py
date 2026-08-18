#!/usr/bin/env python3
"""Materialize verified stage, candidate, or algorithm-promotion artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hft_mgbs.release_materializer import (
    ReleaseMaterializationError,
    materialize_candidate_receipt,
    materialize_candidate_set,
    materialize_release_configuration,
    materialize_stage_campaign,
    materialize_stage_receipt,
    promote_algorithm_campaign,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    stage = subparsers.add_parser("stage")
    stage.add_argument("--raw-receipt", required=True, type=Path)
    stage.add_argument("--contract", required=True, type=Path)
    stage.add_argument("--output", required=True, type=Path)
    stage.add_argument("--audit", required=True, type=Path)
    stage_campaign = subparsers.add_parser("stage-campaign")
    stage_campaign.add_argument("--raw-receipt", required=True, action="append", type=Path)
    stage_campaign.add_argument("--contract", required=True, type=Path)
    stage_campaign.add_argument("--backend-binding", type=Path)
    stage_campaign.add_argument("--output-dir", required=True, type=Path)
    candidate = subparsers.add_parser("candidate")
    candidate.add_argument("--record", required=True, type=Path)
    candidate.add_argument("--unified-audit", required=True, type=Path)
    candidate.add_argument("--trusted-unified-audit-sha256", required=True)
    candidate.add_argument("--algorithm-search", required=True, type=Path)
    candidate.add_argument("--runtime-decision-receipt", required=True, type=Path)
    candidate.add_argument("--output-receipt", required=True, type=Path)
    candidate.add_argument("--output-record", required=True, type=Path)
    candidate_set = subparsers.add_parser("candidate-set")
    candidate_set.add_argument("--record", required=True, action="append", type=Path)
    candidate_set.add_argument("--minimum-candidates", type=int, default=2)
    candidate_set.add_argument("--output-dir", required=True, type=Path)
    algorithm = subparsers.add_parser("algorithm")
    algorithm.add_argument("--repo-root", required=True, type=Path)
    algorithm.add_argument("--contract", required=True, type=Path)
    algorithm.add_argument("--campaign-root", required=True, type=Path)
    algorithm.add_argument("--formal-receipt", required=True, type=Path)
    algorithm.add_argument("--output-dir", required=True, type=Path)
    release = subparsers.add_parser("release-config")
    release.add_argument("--promotion-dir", required=True, type=Path)
    release.add_argument("--formal-receipt", required=True, type=Path)
    release.add_argument("--contract", required=True, type=Path)
    release.add_argument("--release-candidate", required=True, type=Path)
    release.add_argument("--manifest-template", required=True, type=Path)
    release.add_argument("--policy-template", required=True, type=Path)
    release.add_argument("--new-nic-r0-trust-profile", required=True, type=Path)
    release.add_argument("--runtime-failover-policy", type=Path)
    release.add_argument("--deployment-candidate-id", required=True)
    release.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        if arguments.command == "stage":
            value = materialize_stage_receipt(
                raw_receipt_path=arguments.raw_receipt,
                contract_path=arguments.contract,
                output_path=arguments.output,
                audit_path=arguments.audit,
            )
            print("stage={} qualified=true".format(value["stage"]))
        elif arguments.command == "stage-campaign":
            value = materialize_stage_campaign(
                raw_receipt_paths=arguments.raw_receipt,
                contract_path=arguments.contract,
                backend_binding_path=arguments.backend_binding,
                output_dir=arguments.output_dir,
            )
            print("receipts={} stage_campaign=sealed".format(value["receipt_count"]))
        elif arguments.command == "candidate":
            value = materialize_candidate_receipt(
                candidate_record_path=arguments.record,
                unified_audit_path=arguments.unified_audit,
                trusted_unified_audit_sha256=arguments.trusted_unified_audit_sha256,
                algorithm_search_path=arguments.algorithm_search,
                runtime_decision_receipt_path=arguments.runtime_decision_receipt,
                output_receipt_path=arguments.output_receipt,
                output_record_path=arguments.output_record,
            )
            print("candidate={} receipt=sealed".format(value["candidate_id"]))
        elif arguments.command == "candidate-set":
            value = materialize_candidate_set(
                candidate_record_paths=arguments.record,
                output_dir=arguments.output_dir,
                minimum_candidates=arguments.minimum_candidates,
            )
            print("candidates={} set=sealed".format(value["candidate_count"]))
        elif arguments.command == "algorithm":
            value = promote_algorithm_campaign(
                repo_root=arguments.repo_root,
                contract_path=arguments.contract,
                campaign_root=arguments.campaign_root,
                formal_receipt_path=arguments.formal_receipt,
                output_dir=arguments.output_dir,
            )
            print("winner={} promotion=staged".format(value["winner"]))
        else:
            value = materialize_release_configuration(
                promotion_dir=arguments.promotion_dir,
                formal_receipt_path=arguments.formal_receipt,
                contract_path=arguments.contract,
                release_candidate_path=arguments.release_candidate,
                manifest_template_path=arguments.manifest_template,
                policy_template_path=arguments.policy_template,
                new_nic_r0_trust_profile_path=arguments.new_nic_r0_trust_profile,
                runtime_failover_policy_path=arguments.runtime_failover_policy,
                deployment_candidate_id=arguments.deployment_candidate_id,
                output_dir=arguments.output_dir,
            )
            print("winner={} release_config=staged".format(value["winner"]))
    except (ReleaseMaterializationError, OSError, ValueError) as error:
        print("materialization rejected: {}".format(error), file=sys.stderr)
        return 74
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
