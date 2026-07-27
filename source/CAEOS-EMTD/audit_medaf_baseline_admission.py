from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import canonical_hash


REQUIRED_FILES = (
    "README.md",
    "core/net.py",
    "core/train.py",
    "core/test.py",
    "misc/osr.yml",
    "osr_main.py",
    "requirements.txt",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def git_bytes(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    ).stdout


def inspect_source(files: Dict[str, str]) -> Dict[str, Any]:
    net = files["core/net.py"]
    train = files["core/train.py"]
    test = files["core/test.py"]
    config = files["misc/osr.yml"]
    main = files["osr_main.py"]
    checks = {
        "three_expert_branches_present": all(
            token in net
            for token in (
                "branch1_cls",
                "branch2_cls",
                "branch3_cls",
            )
        ),
        "adaptive_gate_present": (
            "gate_pred = F.softmax" in net
            and "gate_logits = gate_logits.sum(-1)" in net
        ),
        "attention_diversity_training_present": (
            "def attnDiv" in train and "attnDiv(branch_cams)" in train
        ),
        "training_loader_only_in_train_function": (
            "def train(train_loader" in train
            and "out_loader" not in train
            and "test_loader" not in train
        ),
        "source_evaluates_test_and_unknown_each_epoch": (
            "if (epoch + 1) % options['test_step'] == 0" in main
            and "evaluation(model, test_loader, out_loader" in main
        ),
        "source_threshold_uses_combined_test_unknown_labels": (
            "roc_curve(open_labels, prob)" in test
            and "np.abs(np.array(tpr) - 0.95).argmin()" in test
            and "open_pred = (total_pred > threshold)" in test
        ),
        "source_has_no_known_validation_loader": (
            "validation_loader" not in main
            and "valid_loader" not in main
            and "val_loader" not in main
        ),
        "official_score_is_gated_msp": (
            "score_wgts : [1,0,0]" in config
            and "branch_opt : -1" in config
            and "gate_temp  : 100" in config
            and "lgs_temp    : 100" in config
        ),
        "source_reports_auroc_and_aupr": (
            "AUROC:" in test
            and "AUPR_IN:" in test
            and "AUPR_OUT:" in test
        ),
        "source_reports_fpr95": "FPR95" in test,
        "source_reports_oscr": "OSCR" in test,
        "source_reports_ece": "ECE" in test,
        "source_backbone_is_2d_convolutional": (
            "nn.Conv2d" in net and "AdaptiveAvgPool2d" in net
        ),
    }
    required_positive = (
        "three_expert_branches_present",
        "adaptive_gate_present",
        "attention_diversity_training_present",
        "training_loader_only_in_train_function",
        "source_evaluates_test_and_unknown_each_epoch",
        "source_threshold_uses_combined_test_unknown_labels",
        "source_has_no_known_validation_loader",
        "official_score_is_gated_msp",
        "source_reports_auroc_and_aupr",
        "source_backbone_is_2d_convolutional",
    )
    if not all(checks[key] for key in required_positive):
        missing = [key for key in required_positive if not checks[key]]
        raise ValueError(f"MEDAF source contract mismatch: {missing}")
    return checks


def build_audit(
    repo: Path,
    bundle: Path,
    *,
    expected_commit: str,
    expected_bundle_sha256: str,
    result_count_at_audit: int,
) -> Dict[str, Any]:
    if int(result_count_at_audit) != 0:
        raise ValueError("MEDAF admission audit requires zero model results")
    head = git_output(repo, "rev-parse", "HEAD").strip()
    status = git_output(repo, "status", "--porcelain")
    tracked = [
        item
        for item in git_output(repo, "ls-files").splitlines()
        if item.strip()
    ]
    missing = [name for name in REQUIRED_FILES if name not in tracked]
    if missing:
        raise ValueError(f"missing required MEDAF source files: {missing}")
    bundle_sha256 = file_hash(bundle)
    source_blobs = {
        name: git_bytes(repo, "show", f"HEAD:{name}")
        for name in REQUIRED_FILES
    }
    source_files = {
        name: content.decode("utf-8")
        for name, content in source_blobs.items()
    }
    source_sha256 = {
        name: hashlib.sha256(content).hexdigest()
        for name, content in source_blobs.items()
    }
    checks = inspect_source(source_files)
    identity_passes = (
        head == expected_commit
        and status == ""
        and bundle_sha256 == expected_bundle_sha256
        and len(tracked) == 16
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_medaf_baseline_admission_audit_v2",
        "revision": {
            "reason": (
                "replace cross-platform worktree byte hashes with canonical "
                "Git blob content hashes"
            ),
            "model_results_observed_before_revision": 0,
            "method_or_admission_gate_changed": False,
            "superseded_attempts": {
                "windows_worktree_sha": {
                    "manifest_sha256": (
                        "24ad940f20fbf5ee3dd6820dba5806927c6bff0d9236db686"
                        "023b61e391a34cb"
                    ),
                    "file_sha256": (
                        "f0c6e43dbaf097fb85202f0868057ba311b4619267778faf"
                        "4068236f71652f12"
                    ),
                },
                "linux_worktree_sha": {
                    "manifest_sha256": (
                        "4874bfe15141ccd8b811dc99913734a77d69322cf0dbf262"
                        "5a760941b10ca8e1"
                    ),
                    "file_sha256": (
                        "08a2355e5510620d21fe1b712038b6028579d026c7012085"
                        "f7c9b0cceedd1f26"
                    ),
                },
            },
        },
        "method": {
            "name": "MEDAF",
            "paper": (
                "Exploring Diverse Representations for Open Set Recognition"
            ),
            "venue": "AAAI 2024",
            "doi": "10.1609/aaai.v38i6.28385",
            "official_repository": "https://github.com/Vanixxz/MEDAF",
        },
        "source_identity": {
            "expected_commit": expected_commit,
            "observed_commit": head,
            "git_tree": git_output(repo, "rev-parse", "HEAD^{tree}").strip(),
            "working_tree_clean": status == "",
            "tracked_file_count": len(tracked),
            "bundle_sha256": bundle_sha256,
            "expected_bundle_sha256": expected_bundle_sha256,
            "required_file_sha256": source_sha256,
            "hash_semantics": "canonical_git_blob_content",
            "passes": identity_passes,
        },
        "source_contract": checks,
        "strict_v4_protocol_conflicts": {
            "test_and_unknown_labels_define_source_f1_threshold": checks[
                "source_threshold_uses_combined_test_unknown_labels"
            ],
            "test_and_unknown_are_monitored_each_epoch": checks[
                "source_evaluates_test_and_unknown_each_epoch"
            ],
            "known_validation_loader_absent": checks[
                "source_has_no_known_validation_loader"
            ],
            "input_contract_is_2d_spatial_attention_not_tabular_views": checks[
                "source_backbone_is_2d_convolutional"
            ],
            "missing_strict_metrics": [
                name
                for name, present in (
                    ("unknown_fpr95", checks["source_reports_fpr95"]),
                    ("oscr", checks["source_reports_oscr"]),
                    ("ece", checks["source_reports_ece"]),
                )
                if not present
            ],
        },
        "adapter_requirements": [
            "name the implementation MEDAF-Tabular adapter, not native MEDAF",
            "freeze the tabular or multi-view attention-map definition before results",
            "fit model only on known-training with group-disjoint splits",
            "select every threshold and adapter hyperparameter on known-validation only",
            "do not evaluate known-test or unknown-test during training or selection",
            "retain the three experts, diversity loss, adaptive gate, and gated-MSP score",
            "report Known Macro-F1, AUROC, AUPR, FPR95, OSCR, and ECE",
            "pre-register a small cross-suite pilot and expansion gate at zero results",
        ],
        "decision": {
            "official_source_snapshot_admitted": identity_passes,
            "native_medaf_strict_v4_execution_admitted": False,
            "named_tabular_adapter_candidate": identity_passes,
            "formal_method_count_increment": 0,
            "model_metrics_generated": False,
            "reason": (
                "the official image implementation is reproducible, but its "
                "reported F1 threshold consumes known-test and unknown-test "
                "labels and its spatial attention contract is not the "
                "strict-v4 tabular multi-view contract"
            ),
        },
        "result_count_at_audit": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-bundle-sha256", required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result_count = (
        sum(1 for _ in args.result_root.rglob("metrics.json"))
        if args.result_root.exists()
        else 0
    )
    value = build_audit(
        args.repo,
        args.bundle,
        expected_commit=args.expected_commit,
        expected_bundle_sha256=args.expected_bundle_sha256,
        result_count_at_audit=result_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
