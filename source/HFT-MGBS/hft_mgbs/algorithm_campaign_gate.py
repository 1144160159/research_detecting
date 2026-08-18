"""Shared fail-closed gate for the bounded algorithm qualification campaign.

This gate proves algorithm-side qualification only.  It deliberately does not
read or emit physical capture campaign receipts and cannot grant production.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from hft_mgbs.algorithm_campaign import load_strict_json, validate_contract
from hft_mgbs.algorithm_campaign_replay import (
    REPLAY_SCOPE,
    verify_algorithm_campaign_raw_replay,
)
from hft_mgbs.algorithm_optimality import METRIC_NAMES, audit_algorithm_search


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_SCOPE = "hft_mgbs_algorithm_qualification_campaign_receipt_v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _add(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def _has_symlink_component(path: Path) -> bool:
    current = path
    while True:
        if current.is_symlink():
            return True
        parent = current.parent
        if parent == current:
            return False
        current = parent


def _mapped_path(raw_path: str, base: Path, remote_artifact_root: Path | None) -> Path:
    declared = Path(raw_path)
    if remote_artifact_root is not None:
        # POSIX formal receipts are mirrored under their absolute hierarchy.
        # Reject ambiguous or escaping spellings *before* PurePosixPath can
        # normalise away a lexical ``.`` component.
        pure = PurePosixPath(raw_path)
        raw_parts = raw_path.split("/")
        if (
            not pure.is_absolute()
            or "\\" in raw_path
            or any(character in raw_path for character in "\r\n\x00")
            or any(part in (".", "..") for part in raw_parts)
        ):
            raise ValueError("unsafe remote artifact path")
        relative = Path(*pure.parts[1:])
        root = remote_artifact_root.resolve()
        mapped = root / relative
        mapped.resolve(strict=False).relative_to(root)
        return mapped
    pure_posix_absolute = PurePosixPath(raw_path).is_absolute()
    if pure_posix_absolute:
        if declared.is_absolute():
            return declared
        # On Windows, Path('/opt/...') is not a native absolute path and later
        # resolve() would silently reinterpret it below the current drive.
        # Such a GPU declaration requires an explicit import mirror.
        raise ValueError("remote artifact root required")
    return declared if declared.is_absolute() else base / declared


def _regular_reference(
    base: Path,
    value: object,
    prefix: str,
    errors: list[str],
    remote_artifact_root: Path | None = None,
) -> tuple[Path | None, Mapping[str, Any] | None, str | None]:
    if not isinstance(value, Mapping):
        _add(errors, prefix + ".reference")
        return None, None, None
    raw_path = value.get("path")
    expected = value.get("sha256")
    if not isinstance(raw_path, str) or not raw_path or any(
        character in raw_path for character in "\r\n\x00"
    ):
        _add(errors, prefix + ".path")
        return None, None, None
    if not isinstance(expected, str) or SHA256_RE.fullmatch(expected) is None:
        _add(errors, prefix + ".declared_sha256")
        return None, None, None
    try:
        lexical = _mapped_path(raw_path, base, remote_artifact_root)
    except ValueError:
        _add(errors, prefix + ".path")
        return None, None, None
    if _has_symlink_component(lexical):
        _add(errors, prefix + ".symlink")
        return None, None, None
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError):
        _add(errors, prefix + ".file")
        return None, None, None
    if not resolved.is_file() or resolved.is_symlink():
        _add(errors, prefix + ".file")
        return None, None, None
    actual = _sha256(resolved)
    if actual != expected:
        _add(errors, prefix + ".sha256")
        return resolved, None, actual
    try:
        payload = load_strict_json(resolved)
    except (OSError, UnicodeError, ValueError):
        _add(errors, prefix + ".json")
        return resolved, None, actual
    if not isinstance(payload, Mapping):
        _add(errors, prefix + ".schema")
        return resolved, None, actual
    return resolved, payload, actual


def _validate_authoritative_raw_replay(
    value: object,
    *,
    contract: Mapping[str, Any],
    contract_sha: str,
    receipt: Mapping[str, Any],
    receipt_path: Path,
    receipt_sha: str,
    winner: str,
    errors: list[str],
) -> None:
    prefix = "algorithm_campaign.authoritative_raw_replay."
    if not isinstance(value, Mapping):
        _add(errors, prefix + "result")
        return

    expected = {
        "schema_version": 1,
        "scope": REPLAY_SCOPE,
        "campaign_id": contract.get("campaign_id"),
        "campaign_run_id": receipt.get("campaign_run_id"),
        "contract_sha256": contract_sha,
        "algorithm_search_sha256": receipt.get("algorithm_search_sha256"),
        "input_manifest_entry_count": 27,
        "candidate_count": 10,
        "evaluated_candidate_count": 10,
        "feasible_candidate_count": receipt.get("feasible_candidate_count"),
        "qualified_candidate_count": receipt.get("qualified_candidate_count"),
        "mode_count": 2,
        "repeats_per_mode": 3,
        "raw_repeat_count": 60,
        "regenerated_artifact_count": 12,
        "formal_algorithm_only_accepted": True,
        "selected_candidate": winner,
        "candidate_receipts_match_raw_replay": True,
        "projection_matches_raw_replay": True,
        "formal_receipt_matches_raw_replay": True,
        "campaign_tree_unchanged": True,
        "authoritative_raw_replay_complete": True,
        "accepted": True,
        "production_joint_optimum_proven": False,
        "final_pareto_ingestion_allowed": False,
        "writes_campaign_tree": False,
        "errors": [],
    }
    for name, expected_value in expected.items():
        if value.get(name) != expected_value:
            _add(errors, prefix + name)

    formal_reference = value.get("formal_receipt")
    if not isinstance(formal_reference, Mapping):
        _add(errors, prefix + "formal_receipt")
    else:
        try:
            replay_receipt_path = Path(str(formal_reference.get("path"))).resolve(
                strict=True
            )
        except (OSError, RuntimeError, ValueError):
            _add(errors, prefix + "formal_receipt.path")
        else:
            if replay_receipt_path != receipt_path.resolve(strict=True):
                _add(errors, prefix + "formal_receipt.path")
        if formal_reference.get("sha256") != receipt_sha:
            _add(errors, prefix + "formal_receipt.sha256")

    before = value.get("campaign_tree_before")
    after = value.get("campaign_tree_after")
    if not isinstance(before, Mapping) or before != after:
        _add(errors, prefix + "campaign_tree_unchanged")
    else:
        entry_count = before.get("entry_count")
        tree_sha = before.get("sha256")
        if (
            not isinstance(entry_count, int)
            or isinstance(entry_count, bool)
            or entry_count <= 0
            or not isinstance(tree_sha, str)
            or SHA256_RE.fullmatch(tree_sha) is None
        ):
            _add(errors, prefix + "campaign_tree_snapshot")


def verify_algorithm_campaign_gate(
    repo_root: Path,
    gate: object,
    *,
    reference_base: Path | None = None,
    remote_artifact_root: Path | None = None,
) -> dict[str, Any]:
    """Rehash and replay one algorithm campaign receipt.

    The formal finalizer has already recomputed every raw candidate receipt.
    This import gate independently revalidates the frozen contract, rehashes
    the formal receipt and projected search, and recomputes its optimality
    audit.  A missing receipt is an intentional pending/fail-closed state.
    """

    errors: list[str] = []
    if not isinstance(gate, Mapping) or gate.get("required") is not True:
        return {
            "qualified": False,
            "winner": None,
            "contract_sha256": None,
            "receipt_sha256": None,
            "projection_sha256": None,
            "errors": ["algorithm_campaign.gate"],
        }
    base = (reference_base or repo_root).resolve()
    mirror = remote_artifact_root.resolve() if remote_artifact_root is not None else None
    contract_path, contract, contract_sha = _regular_reference(
        base, gate.get("contract"), "algorithm_campaign.contract", errors
    )
    receipt_path, receipt, receipt_sha = _regular_reference(
        base,
        gate.get("receipt"),
        "algorithm_campaign.receipt",
        errors,
        mirror,
    )
    # The contract validator owns repository-relative paths, so derive the
    # checkout root from a contract stored under ``configs/``.  This keeps the
    # gate usable from manifests and policies whose own directory is configs/.
    validation_root = repo_root.resolve()
    if contract_path is not None and contract_path.parent.name == "configs":
        validation_root = contract_path.parent.parent.resolve()
    expected_artifacts: Mapping[str, Any] | None = None
    if contract_path is not None and contract is not None:
        try:
            _validated_contract, _search, expected_artifacts, _specs = validate_contract(
                validation_root, contract_path
            )
        except (OSError, UnicodeError, ValueError):
            _add(errors, "algorithm_campaign.contract.replay")

    projection_sha = None
    winner = None
    campaign_root: Path | None = None
    if receipt is not None and contract is not None and contract_sha is not None:
        expected_scalars = {
            "schema_version": 1,
            "scope": RECEIPT_SCOPE,
            "campaign_id": contract.get("campaign_id"),
            "contract_sha256": contract_sha,
            "algorithm_search_sha256": (contract.get("algorithm_search") or {}).get(
                "sha256"
            ),
            "expected_candidate_count": 10,
            "evaluated_candidate_count": 10,
            "campaign_evidence_complete": True,
            "algorithm_only_practical_optimum_proven": True,
            "accepted": True,
            "production_joint_optimum_proven": False,
            "final_pareto_ingestion_allowed": False,
            "source_algorithm_search_modified": False,
            "raw_results_remain_on_gpu": True,
            "errors": [],
        }
        for name, expected in expected_scalars.items():
            if receipt.get(name) != expected:
                _add(errors, "algorithm_campaign.receipt." + name)
        candidates = receipt.get("candidate_receipts")
        input_manifest = receipt.get("input_hash_manifest")
        if (
            not isinstance(input_manifest, Mapping)
            or not isinstance(input_manifest.get("path"), str)
            or not isinstance(input_manifest.get("sha256"), str)
            or SHA256_RE.fullmatch(str(input_manifest.get("sha256"))) is None
            or not isinstance(input_manifest.get("entry_count"), int)
            or isinstance(input_manifest.get("entry_count"), bool)
            or int(input_manifest.get("entry_count")) <= 0
        ):
            _add(errors, "algorithm_campaign.receipt.input_hash_manifest")
        expected_ids = {"A{:02d}".format(index) for index in range(1, 11)}
        if (
            not isinstance(candidates, list)
            or len(candidates) != 10
            or {
                item.get("candidate_id")
                for item in candidates
                if isinstance(item, Mapping)
            }
            != expected_ids
            or any(
                not isinstance(item, Mapping)
                or not isinstance(item.get("sha256"), str)
                or SHA256_RE.fullmatch(str(item.get("sha256"))) is None
                for item in candidates
            )
        ):
            _add(errors, "algorithm_campaign.receipt.candidate_receipts")
        feasible_count = receipt.get("feasible_candidate_count")
        qualified_count = receipt.get("qualified_candidate_count")
        if (
            not isinstance(feasible_count, int)
            or isinstance(feasible_count, bool)
            or not 1 <= feasible_count <= 10
            or not isinstance(qualified_count, int)
            or isinstance(qualified_count, bool)
            or qualified_count != feasible_count
        ):
            _add(errors, "algorithm_campaign.receipt.qualified_candidate_count")

        projection_path, projection, projection_sha = _regular_reference(
            receipt_path.parent if receipt_path is not None else base,
            receipt.get("suggested_algorithm_search_projection"),
            "algorithm_campaign.projection",
            errors,
            mirror,
        )
        if projection_path is not None and projection is not None:
            campaign_root = projection_path.parent.resolve()
            try:
                input_path = _mapped_path(
                    str(input_manifest.get("path", "")),
                    receipt_path.parent if receipt_path is not None else base,
                    mirror,
                )
                if _has_symlink_component(input_path):
                    raise ValueError("symlink")
                input_resolved = input_path.resolve(strict=True)
                input_resolved.relative_to(campaign_root)
            except (OSError, RuntimeError, ValueError):
                _add(errors, "algorithm_campaign.receipt.input_hash_manifest.file")
            else:
                if (
                    not input_resolved.is_file()
                    or input_resolved.is_symlink()
                    or _sha256(input_resolved) != input_manifest.get("sha256")
                ):
                    _add(errors, "algorithm_campaign.receipt.input_hash_manifest.sha256")
            candidate_by_id = {
                item.get("candidate_id"): item
                for item in candidates
                if isinstance(item, Mapping)
            }
            projection_candidates = projection.get("candidates")
            if not isinstance(projection_candidates, list):
                _add(errors, "algorithm_campaign.projection.candidates")
                projection_candidates = []
            independently_qualified = 0
            for projected in projection_candidates:
                if not isinstance(projected, Mapping):
                    _add(errors, "algorithm_campaign.projection.candidates")
                    continue
                candidate_id = projected.get("id")
                reference = candidate_by_id.get(candidate_id)
                if not isinstance(reference, Mapping):
                    _add(errors, "algorithm_campaign.projection.candidate_binding")
                    continue
                expected_hash = reference.get("sha256")
                if (
                    projected.get("evidence_sha256") != expected_hash
                    or projected.get("evidence") != reference.get("path")
                ):
                    _add(errors, "algorithm_campaign.projection.candidate_binding")
                # Candidate receipt paths are absolute GPU paths.  When this
                # verifier runs on the GPU host it must rehash all ten.  A
                # mirrored/imported receipt therefore remains unqualified
                # unless those files are mounted at the bound paths.
                try:
                    candidate_path = _mapped_path(
                        str(reference.get("path", "")),
                        receipt_path.parent if receipt_path is not None else base,
                        mirror,
                    )
                    if _has_symlink_component(candidate_path):
                        raise ValueError("symlink")
                    candidate_path.resolve(strict=True).relative_to(campaign_root)
                except (OSError, RuntimeError, ValueError):
                    _add(errors, "algorithm_campaign.candidate_receipt.path")
                    continue
                if (
                    not candidate_path.is_absolute()
                    or not candidate_path.is_file()
                    or candidate_path.is_symlink()
                ):
                    _add(errors, "algorithm_campaign.candidate_receipt.file")
                    continue
                if _sha256(candidate_path) != expected_hash:
                    _add(errors, "algorithm_campaign.candidate_receipt.sha256")
                    continue
                try:
                    candidate_receipt = load_strict_json(candidate_path)
                except (OSError, UnicodeError, ValueError):
                    _add(errors, "algorithm_campaign.candidate_receipt.json")
                    continue
                violations = (
                    candidate_receipt.get("hard_constraint_violations")
                    if isinstance(candidate_receipt, Mapping)
                    else None
                )
                hard_constraints_passed = (
                    candidate_receipt.get("hard_constraints_passed")
                    if isinstance(candidate_receipt, Mapping)
                    else None
                )
                if (
                    not isinstance(candidate_receipt, Mapping)
                    or candidate_receipt.get("scope")
                    != "hft_mgbs_algorithm_candidate_qualification_receipt_v1"
                    or candidate_receipt.get("candidate_id") != candidate_id
                    or candidate_receipt.get("campaign_id") != receipt.get("campaign_id")
                    or candidate_receipt.get("contract_sha256") != contract_sha
                    or candidate_receipt.get("algorithm_search_sha256")
                    != receipt.get("algorithm_search_sha256")
                    or not isinstance(hard_constraints_passed, bool)
                    or not isinstance(violations, list)
                    or hard_constraints_passed != (len(violations) == 0)
                    or candidate_receipt.get("production_joint_optimum_proven") is not False
                    or candidate_receipt.get("final_pareto_ingestion_allowed") is not False
                    or candidate_receipt.get("input_hash_manifest") != input_manifest
                    or candidate_receipt.get("bound_repository_artifacts")
                    != expected_artifacts
                ):
                    _add(errors, "algorithm_campaign.candidate_receipt.binding")
                elif hard_constraints_passed:
                    independently_qualified += 1
                projected_contract = projected.get("mode_contract")
                projected_modes = projected.get("mode_metrics")
                projected_worst = projected.get("reported_worst_case_metrics")
                receipt_worst = candidate_receipt.get(
                    "reported_worst_case_metrics"
                )
                selection_worst = (
                    {
                        name: receipt_worst[name]
                        for name in METRIC_NAMES
                        if name in receipt_worst
                    }
                    if isinstance(receipt_worst, Mapping)
                    else None
                )
                if (
                    projected_contract != candidate_receipt.get("mode_contract")
                    or projected_modes != candidate_receipt.get("mode_metrics")
                    or not isinstance(selection_worst, Mapping)
                    or len(selection_worst) != len(METRIC_NAMES)
                    or projected_worst != selection_worst
                ):
                    _add(errors, "algorithm_campaign.projection.candidate_payload")
            if independently_qualified != qualified_count:
                _add(errors, "algorithm_campaign.receipt.qualified_candidate_count")
            recomputed = audit_algorithm_search(projection)
            if receipt.get("projection_optimality_audit") != recomputed:
                _add(errors, "algorithm_campaign.projection.audit_binding")
            required_audit = {
                "accepted": True,
                "algorithm_only_practical_optimum_proven": True,
                "actual_candidate_count": 10,
                "paired_metric_complete_candidate_count": 10,
                "evidence_hash_complete_candidate_count": 10,
                "feasible_metric_complete_candidate_count": qualified_count,
                "confirmatory_evidence_hash_complete": True,
                "errors": [],
                "production_joint_optimum_proven": False,
                "final_pareto_ingestion_allowed": False,
            }
            for name, expected in required_audit.items():
                if recomputed.get(name) != expected:
                    _add(errors, "algorithm_campaign.projection.audit." + name)
            front = recomputed.get("practical_front_recomputed_from_available_metrics")
            candidate = recomputed.get("confirmatory_practical_winner")
            if (
                not isinstance(front, list)
                or len(front) != 1
                or candidate != front[0]
                or projection.get("selected_candidate") != candidate
            ):
                _add(errors, "algorithm_campaign.projection.winner")
            else:
                winner = candidate

    raw_replay: Mapping[str, Any] | None = None
    if (
        not errors
        and contract_path is not None
        and contract is not None
        and contract_sha is not None
        and receipt_path is not None
        and receipt is not None
        and receipt_sha is not None
        and winner is not None
    ):
        # Formal artifacts live at <campaign-root>/receipts/campaign_receipt.json.
        # Retain compatibility with a verifier fixture rooted directly beside
        # the receipt; the replay API itself enforces the exact formal layout.
        if campaign_root is None:
            campaign_root = (
                receipt_path.parent.parent
                if receipt_path.parent.name == "receipts"
                else receipt_path.parent
            )
        original_receipt_path = campaign_root / "receipts" / "campaign_receipt.json"
        replay_receipt_path = receipt_path
        if (
            original_receipt_path.is_file()
            and not _has_symlink_component(original_receipt_path)
            and _sha256(original_receipt_path) == receipt_sha
        ):
            replay_receipt_path = original_receipt_path
        replay_contract_path = contract_path
        plan_path = campaign_root / "plan.json"
        try:
            plan_payload = load_strict_json(plan_path)
            plan_contract = plan_payload.get("contract")
            declared_contract_path = _mapped_path(
                str(plan_contract.get("path", "")), campaign_root, mirror
            )
            declared_contract_path = declared_contract_path.resolve(strict=True)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
            pass
        else:
            if (
                isinstance(plan_contract, Mapping)
                and plan_contract.get("sha256") == contract_sha
                and declared_contract_path.is_file()
                and not _has_symlink_component(declared_contract_path)
                and _sha256(declared_contract_path) == contract_sha
            ):
                replay_contract_path = declared_contract_path
        try:
            replay_value = verify_algorithm_campaign_raw_replay(
                validation_root,
                replay_contract_path,
                campaign_root,
                replay_receipt_path,
            )
        except Exception as error:  # fail closed at the shared release boundary
            _add(
                errors,
                "algorithm_campaign.authoritative_raw_replay.exception."
                + type(error).__name__,
            )
        else:
            if isinstance(replay_value, Mapping):
                raw_replay = replay_value
            _validate_authoritative_raw_replay(
                replay_value,
                contract=contract,
                contract_sha=contract_sha,
                receipt=receipt,
                receipt_path=replay_receipt_path,
                receipt_sha=receipt_sha,
                winner=winner,
                errors=errors,
            )
    elif receipt is not None and not any(
        error.startswith("algorithm_campaign.authoritative_raw_replay.")
        for error in errors
    ):
        _add(errors, "algorithm_campaign.authoritative_raw_replay.prerequisites")

    qualified = not errors
    return {
        "qualified": qualified,
        "winner": winner if qualified else None,
        "contract_sha256": contract_sha,
        "receipt_sha256": receipt_sha,
        "projection_sha256": projection_sha,
        "authoritative_raw_replay": raw_replay,
        "errors": errors,
    }
