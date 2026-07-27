from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


EXPECTED_HEAD = "a1574f38741772ac79628131f9fbef8a7c78374a"
EXPECTED_REMOTE = "https://github.com/WaIdo/TAO-NET.git"
EXPECTED_PAPER_SHA256 = (
    "9aea18ac0cecde001d38fb24eca25d46d282e126a2384609591d42ba804ef491"
)
EXPECTED_TRACKED_FILES = 168
KEY_FILES = {
    "README.md": (
        "5c59f1edec9cd7eb1d0f267ef5246d83d2c4f1bb30fed13be75be9d567ea35c1"
    ),
    "stage1_ood_detection/my_datasets.py": (
        "2b11613612427af982c5b1c519c7fe21b0362211828242dba39ddf444b16ffd2"
    ),
    "stage1_ood_detection/run.py": (
        "ede24e8f5b05afef047cf144a1fc5ec52253e94e8abfc19ca26223350b1349eb"
    ),
    "stage1_ood_detection/my_uncertainty.py": (
        "f8f650d14934abfddba7562e704b1da523fbd1384817e664db80bb5d4940d07b"
    ),
    "stage2_ood_llm/llm_client.py": (
        "ee13f6855b6b87a5204adba624576cc963b18d51e3551e2793911db28792b0b0"
    ),
    "stage2_ood_llm/driver.py": (
        "6bc12ab25cf4d9f1f9c29c249ad3994f089abe11dd09ed61e984341a1e372c2c"
    ),
    "stage2_id_branch.py": (
        "5315b885e4c105da1a8ebf5401559aeba9a84fd8be4ec6401010566d4dd1d1e2"
    ),
    "stage2_pacrep_tsinghua/config/model-en.conf": (
        "fbb156eba86ebc004e71fb5f7aaa47134c5dd18ede0b303dccd03ed062bf8ddf"
    ),
    "stage2_pacrep_vpn/config/model-en.conf": (
        "fbb156eba86ebc004e71fb5f7aaa47134c5dd18ede0b303dccd03ed062bf8ddf"
    ),
    "stage2_pacrep_nontor/config/model-en.conf": (
        "fbb156eba86ebc004e71fb5f7aaa47134c5dd18ede0b303dccd03ed062bf8ddf"
    ),
}
REQUIRED_RELEASE_ARTIFACTS = [
    "stage1_ood_detection/0_data_process_factory/processed_train.json",
    "stage1_ood_detection/0_data_process_factory/processed_valid.json",
    "stage1_ood_detection/0_data_process_factory/processed_test.json",
    "stage2_pacrep_tsinghua/data/sample/train.txt",
    "stage2_pacrep_tsinghua/data/sample/valid.txt",
    "stage2_pacrep_tsinghua/data/sample/test.txt",
    "stage2_pacrep_tsinghua/saved_model/english_bert_base.bin",
    "stage2_pacrep_vpn/data/sample/train.txt",
    "stage2_pacrep_vpn/data/sample/valid.txt",
    "stage2_pacrep_vpn/data/sample/test.txt",
    "stage2_pacrep_vpn/saved_model/english_bert_base.bin",
    "stage2_pacrep_nontor/data/sample/train.txt",
    "stage2_pacrep_nontor/data/sample/valid.txt",
    "stage2_pacrep_nontor/data/sample/test.txt",
    "stage2_pacrep_nontor/saved_model/english_bert_base.bin",
]


def canonical_hash(value: dict[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "manifest_sha256"}
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def git_blob_hash(repository: Path, relative: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), "show", f"HEAD:{relative}"],
        check=True,
        capture_output=True,
    )
    return hashlib.sha256(completed.stdout).hexdigest()


def verify_sources(repository: Path, paper: Path) -> dict[str, Any]:
    if git(repository, "rev-parse", "HEAD") != EXPECTED_HEAD:
        raise ValueError("TAO-Net HEAD does not match the frozen official commit")
    remote = git(repository, "remote", "get-url", "origin")
    if remote.rstrip("/") != EXPECTED_REMOTE.rstrip("/"):
        raise ValueError("TAO-Net origin does not match the official repository")
    if git(repository, "status", "--porcelain=v1"):
        raise ValueError("TAO-Net source snapshot is not clean")
    tracked = git(repository, "ls-files").splitlines()
    if len(tracked) != EXPECTED_TRACKED_FILES:
        raise ValueError("TAO-Net tracked-file count mismatch")
    observed = {}
    for relative, expected in KEY_FILES.items():
        path = repository / relative
        if not path.is_file() or git_blob_hash(repository, relative) != expected:
            raise ValueError(f"TAO-Net key-file SHA mismatch: {relative}")
        observed[relative] = expected
    if not paper.is_file() or file_hash(paper) != EXPECTED_PAPER_SHA256:
        raise ValueError("TAO-Net paper SHA mismatch")
    return {
        "repository": str(repository.resolve()),
        "repository_url": EXPECTED_REMOTE,
        "commit": EXPECTED_HEAD,
        "tracked_file_count": len(tracked),
        "key_git_blob_content_sha256": observed,
        "paper": str(paper.resolve()),
        "paper_sha256": EXPECTED_PAPER_SHA256,
    }


def build_protocol(
    repository: Path,
    paper: Path,
    *,
    creator: Path,
    auditor: Path,
    test: Path,
) -> dict[str, Any]:
    sources = verify_sources(repository, paper)
    value: dict[str, Any] = {
        "schema_version": "strict_v4_tao_net_direct_baseline_protocol_v1",
        "created_at_utc": "2026-07-23T21:08:40Z",
        "result_freeze_policy": "protocol_before_any_tao_net_model_metric",
        "supersession_history": [
            {
                "file": (
                    "protocol_manifest_superseded_windows_worktree_sha.json"
                ),
                "file_sha256": (
                    "77622490c97d6dd5363ca2991c47c0d280ae309c2ddfe4201161b2739d6cb2a4"
                ),
                "manifest_sha256": (
                    "10c1ea6c74a5e28a7a0e2bc0cbf7ae5274d9cf2aa54cd56838ed1bf61f0cdf59"
                ),
                "reason": (
                    "replace platform-dependent Windows worktree byte hashes "
                    "with canonical Git blob content SHA-256"
                ),
                "effect_results_existed_at_supersession": False,
            },
            {
                "file": (
                    "protocol_manifest_superseded_admission_gate_scope.json"
                ),
                "file_sha256": (
                    "cfce73792bdfd6ddebebcd3e6698b712dccad96ba297a87e105c9cd596020db4"
                ),
                "manifest_sha256": (
                    "1b7b4ed238de35d99b636c2d6301fefb3c4bf990992df30fe01c544d003e657c"
                ),
                "audit_file": (
                    "audit_superseded_admission_gate_scope.json"
                ),
                "audit_file_sha256": (
                    "f88285609ebdefb2996309c5e4111e4103febb324cd318ea5486b089952712e6"
                ),
                "audit_manifest_sha256": (
                    "2662d68d7fc37714437dcc7617de39c08e592542d94b486ab7911c95eb173a9d"
                ),
                "reason": (
                    "separate native-reproduction gates from strict-v4 "
                    "main-table comparability gates"
                ),
                "effect_results_existed_at_supersession": False,
            },
        ],
        "paper_identity": {
            "title": (
                "TAO-Net: Two-stage Adaptive OOD Classification Network "
                "for Fine-grained Encrypted Traffic Classification"
            ),
            "arxiv": "2512.15753",
            "doi": "10.1016/j.neucom.2026.133170",
            "publication": "Neurocomputing 679 (2026) 133170",
            "source_url": "https://arxiv.org/abs/2512.15753",
            "pdf_sha256": EXPECTED_PAPER_SHA256,
        },
        "official_source": sources,
        "paper_frozen_protocol": {
            "datasets": {
                "CHNAPP": {
                    "total": 614575,
                    "train": 485782,
                    "validation": 64391,
                    "test": 64392,
                    "id_classes": 4,
                    "ood_classes": 2,
                },
                "ISCXVPN": {
                    "total": 492598,
                    "train": 443337,
                    "validation": 24631,
                    "test": 24630,
                    "id_classes": 9,
                    "ood_classes": 4,
                },
                "ISCXTor": {
                    "total": 1287303,
                    "train": 450001,
                    "validation": 82287,
                    "test": 82287,
                    "id_classes": 8,
                    "ood_classes": 4,
                },
            },
            "training_contains_only_id": True,
            "validation_contains_id_and_ood_ratio": "7:3",
            "test_contains_id_and_ood_ratio": "7:3",
            "strict_prompt_constrains_generation_to_ood_candidate_labels": True,
            "hybrid_alpha": 0.6,
            "fixed_delta": 0.75,
            "runs": 5,
            "reported_seed": 42,
            "metrics": ["macro_precision", "macro_f1", "micro_f1", "recall"],
        },
        "released_snapshot_findings": {
            "readme_says_final_configs_unreleased": True,
            "readme_says_dataset_manifests_unreleased": True,
            "readme_says_deployment_scripts_unreleased": True,
            "stage1_dataset_implementation_count": 1,
            "stage1_implemented_dataset": "CHNAPP_alias_Tinghuaall",
            "validation_is_merged_into_training": True,
            "default_threshold_method": "youden",
            "default_youden_consumes_test_id_and_ood_scores": True,
            "test_labels_partition_id_and_ood_before_threshold_search": True,
            "paper_fixed_delta_differs_from_released_default": True,
            "llm_branch_requires_external_api_or_unfrozen_local_substitute": True,
            "required_release_artifacts": REQUIRED_RELEASE_ARTIFACTS,
            "required_release_artifact_count": len(REQUIRED_RELEASE_ARTIFACTS),
        },
        "comparison_boundary": {
            "same_protocol_as_strict_v4": False,
            "strict_v4_unknown_validation_exposure": False,
            "tao_net_unknown_validation_exposure": True,
            "strict_v4_unknown_class_identity_available_to_decision_rule": False,
            "tao_net_strict_prompt_receives_ood_candidate_label_set": True,
            "strict_v4_primary_metrics": [
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "tao_net_reported_metrics": [
                "macro_precision",
                "macro_f1",
                "micro_f1",
                "recall",
            ],
            "paper_results_must_not_be_ranked_in_strict_v4_main_table": True,
        },
        "admission_policy": {
            "official_code_identity_required": True,
            "all_required_release_artifacts_required": True,
            "all_three_exact_preprocessed_datasets_required": True,
            "unknown_validation_exposure_forbidden_in_strict_v4_main_table": True,
            "test_labels_for_threshold_selection_forbidden": True,
            "native_execution_requires_paper_config_not_inferred_config": True,
            "appendix_protocol_candidate_allowed": True,
            "baseline_count_increment_before_native_execution": 0,
        },
        "implementation_sha256": {
            creator.name: file_hash(creator),
            auditor.name: file_hash(auditor),
            test.name: file_hash(test),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--paper", type=Path, required=True)
    parser.add_argument("--auditor", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("TAO-Net protocol output already exists")
    value = build_protocol(
        args.repository.resolve(),
        args.paper.resolve(),
        creator=Path(__file__).resolve(),
        auditor=args.auditor.resolve(),
        test=args.test.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
