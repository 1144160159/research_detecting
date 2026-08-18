"""Create-only materializers for stage, candidate, and algorithm release artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from hft_mgbs.algorithm_campaign_replay import verify_algorithm_campaign_raw_replay
from hft_mgbs.algorithm_optimality import audit_algorithm_search
from hft_mgbs.stage_evidence import (
    aggregate_stage_evidence,
    load_contract,
    validate_stage_receipt,
)


SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class ReleaseMaterializationError(RuntimeError):
    pass


def _pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, item in items:
        if key in value:
            raise ReleaseMaterializationError("duplicate JSON key: " + key)
        value[key] = item
    return value


def _nonfinite(value: str) -> None:
    raise ReleaseMaterializationError("non-finite JSON: " + value)


def _stable(path: Path, maximum: int = 128 * 1024 * 1024) -> bytes:
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ReleaseMaterializationError("symlink component rejected: {}".format(path))
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ReleaseMaterializationError("bounded regular file required: {}".format(path))
        chunks = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(1024 * 1024, remaining))
            if not block:
                raise ReleaseMaterializationError("short read: {}".format(path))
            chunks.append(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise ReleaseMaterializationError("file grew during read: {}".format(path))
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda item: (
        item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns
    )
    if identity(before) != identity(after):
        raise ReleaseMaterializationError("file changed during read: {}".format(path))
    return b"".join(chunks)


def _json(path: Path) -> Tuple[Dict[str, Any], bytes]:
    raw = _stable(path)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    if not isinstance(value, dict):
        raise ReleaseMaterializationError("JSON object required: {}".format(path))
    return value, raw


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _safe_parent(path: Path) -> Path:
    parent = path.parent.absolute()
    current = Path(parent.anchor)
    for part in parent.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ReleaseMaterializationError("output parent contains a symlink")
    return parent.resolve(strict=True)


def _create_bytes(path: Path, raw: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise ReleaseMaterializationError("create-only output exists: {}".format(path))
    parent = _safe_parent(path)
    descriptor, temporary_raw = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(parent))
    temporary = Path(temporary_raw)
    created = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise ReleaseMaterializationError("create-only output raced")
        os.link(str(temporary), str(path))
        created = True
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    if created:
        os.chmod(str(path), 0o400 if os.name != "nt" else 0o600)


def _create_json(path: Path, value: Mapping[str, Any]) -> str:
    raw = _canonical(value)
    _create_bytes(path, raw)
    return _sha(raw)


def _create_json_transaction(outputs: Sequence[Tuple[Path, Any]]) -> Dict[Path, str]:
    """Publish multiple JSON files create-only, rolling back a partial link set."""
    if not outputs:
        raise ReleaseMaterializationError("at least one transactional output is required")
    paths = [path.absolute() for path, _ in outputs]
    if len(paths) != len(set(paths)):
        raise ReleaseMaterializationError("transactional output paths must be distinct")
    parents = {_safe_parent(path) for path in paths}
    if len(parents) != 1:
        raise ReleaseMaterializationError("transactional outputs must share one directory")
    for path in paths:
        if path.exists() or path.is_symlink():
            raise ReleaseMaterializationError("create-only output exists: {}".format(path))
    parent = next(iter(parents))
    temporaries = []
    published = []
    digests: Dict[Path, str] = {}
    try:
        for path, value in zip(paths, (value for _, value in outputs)):
            raw = _canonical(value)
            descriptor, temporary_raw = tempfile.mkstemp(
                prefix=path.name + ".", suffix=".tmp", dir=str(parent)
            )
            temporary = Path(temporary_raw)
            temporaries.append(temporary)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            digests[path] = _sha(raw)
        for path, temporary in zip(paths, temporaries):
            if path.exists() or path.is_symlink():
                raise ReleaseMaterializationError("create-only output raced")
            os.link(str(temporary), str(path))
            published.append(path)
        for path in published:
            os.chmod(str(path), 0o400 if os.name != "nt" else 0o600)
    except BaseException:
        for path in reversed(published):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise
    finally:
        for temporary in temporaries:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
    return digests


def materialize_stage_receipt(
    *, raw_receipt_path: Path, contract_path: Path, output_path: Path, audit_path: Path
) -> Dict[str, Any]:
    receipt, raw = _json(raw_receipt_path)
    contract = load_contract(contract_path)
    result = validate_stage_receipt(receipt, contract)
    if result.get("qualified") is not True or result.get("errors") != []:
        raise ReleaseMaterializationError(
            "stage raw receipt is not independently qualified: {}".format(result.get("errors"))
        )
    receipt_sha = _sha(raw)
    _create_bytes(output_path, raw)
    audit = {
        "schema_version": 1,
        "scope": "hft_mgbs_stage_receipt_materialization_v1",
        "stage": receipt.get("stage"),
        "candidate_id": receipt.get("candidate_id"),
        "backend": receipt.get("backend"),
        "qualified": True,
        "raw_receipt_sha256": receipt_sha,
        "materialized_receipt_sha256": receipt_sha,
        "stage_contract_sha256": contract.sha256,
        "derived_production_pareto_metrics": result.get("derived"),
        "errors": [],
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
    }
    _create_json(audit_path, audit)
    return audit


def materialize_stage_campaign(
    *,
    raw_receipt_paths: Iterable[Path],
    contract_path: Path,
    output_dir: Path,
    backend_binding_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Seal a complete R1--R4 campaign only after independent recomputation."""
    paths = tuple(raw_receipt_paths)
    if not paths:
        raise ReleaseMaterializationError("stage campaign requires raw receipts")
    if not output_dir.is_absolute():
        raise ReleaseMaterializationError("stage campaign output directory must be absolute")
    if output_dir.exists() or output_dir.is_symlink():
        raise ReleaseMaterializationError("stage campaign output directory must be new")
    contract = load_contract(contract_path)
    backend_binding = None
    backend_binding_sha256 = None
    if backend_binding_path is not None:
        backend_binding, backend_binding_raw = _json(backend_binding_path)
        if set(backend_binding) != {"primary_backend", "fallback_backend"}:
            raise ReleaseMaterializationError("backend binding has an invalid schema")
        backend_binding_sha256 = _sha(backend_binding_raw)
    receipts = []
    raw_receipts = []
    for path in paths:
        receipt, raw = _json(path)
        receipts.append(receipt)
        raw_receipts.append(raw)
    result = aggregate_stage_evidence(receipts, contract, backend_binding=backend_binding)
    if result.get("qualified") is not True or result.get("errors") != []:
        raise ReleaseMaterializationError(
            "stage campaign is not independently qualified: {}".format(result.get("errors"))
        )
    parent = _safe_parent(output_dir)
    temporary = Path(tempfile.mkdtemp(prefix=output_dir.name + ".", suffix=".tmp", dir=str(parent)))
    try:
        receipt_entries = []
        for index, (receipt, raw, source) in enumerate(zip(receipts, raw_receipts, paths)):
            filename = "receipt-{:03d}-{}-{}.json".format(
                index,
                receipt.get("stage"),
                receipt.get("backend_role", receipt.get("backend")),
            )
            (temporary / filename).write_bytes(raw)
            receipt_entries.append({
                "index": index,
                "stage": receipt.get("stage"),
                "candidate_id": receipt.get("candidate_id"),
                "backend": receipt.get("backend"),
                "backend_role": receipt.get("backend_role"),
                "source_path": str(source.resolve()),
                "filename": filename,
                "sha256": _sha(raw),
                "size_bytes": len(raw),
            })
        manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_sealed_stage_campaign_manifest_v1",
            "stage_contract_sha256": contract.sha256,
            "backend_binding_sha256": backend_binding_sha256,
            "receipt_count": len(receipt_entries),
            "receipts": receipt_entries,
        }
        manifest_raw = _canonical(manifest)
        (temporary / "manifest.json").write_bytes(manifest_raw)
        campaign_receipt = {
            "schema_version": 1,
            "scope": "hft_mgbs_sealed_stage_campaign_receipt_v1",
            "qualified": True,
            "stage_qualified": result.get("stage_qualified"),
            "backend_roles_qualified": result.get("backend_roles_qualified"),
            "derived_production_pareto_metrics": result.get(
                "derived_production_pareto_metrics"
            ),
            "receipt_count": result.get("receipt_count"),
            "stage_contract_sha256": contract.sha256,
            "backend_binding": backend_binding,
            "backend_binding_sha256": backend_binding_sha256,
            "manifest_sha256": _sha(manifest_raw),
            "errors": [],
            "production_release_accepted": False,
            "final_pareto_ingestion_allowed": False,
        }
        (temporary / "campaign_receipt.json").write_bytes(_canonical(campaign_receipt))
        if output_dir.exists() or output_dir.is_symlink():
            raise ReleaseMaterializationError("stage campaign output raced")
        os.replace(str(temporary), str(output_dir))
    except BaseException:
        import shutil
        shutil.rmtree(str(temporary), ignore_errors=True)
        raise
    return campaign_receipt


def materialize_candidate_receipt(
    *,
    candidate_record_path: Path,
    unified_audit_path: Path,
    trusted_unified_audit_sha256: str,
    algorithm_search_path: Path,
    runtime_decision_receipt_path: Path,
    output_receipt_path: Path,
    output_record_path: Path,
) -> Dict[str, Any]:
    if not SHA_RE.fullmatch(trusted_unified_audit_sha256):
        raise ReleaseMaterializationError("trusted unified-audit SHA-256 is invalid")
    record, _ = _json(candidate_record_path)
    unified, unified_raw = _json(unified_audit_path)
    search, search_raw = _json(algorithm_search_path)
    runtime, runtime_raw = _json(runtime_decision_receipt_path)
    if _sha(unified_raw) != trusted_unified_audit_sha256:
        raise ReleaseMaterializationError("unified audit differs from its external trust root")
    candidate_id = record.get("candidate_id")
    algorithm_id = record.get("algorithm_id")
    backend = record.get("backend")
    if not all(isinstance(value, str) and value for value in (candidate_id, algorithm_id, backend)):
        raise ReleaseMaterializationError("candidate identity is incomplete")
    if search.get("selected_candidate") != algorithm_id:
        raise ReleaseMaterializationError("candidate algorithm differs from the qualified search winner")
    expected_unified = {
        "schema_version": 1,
        "scope": "hft_mgbs_unified_candidate_evidence_audit",
        "candidate_id": candidate_id,
        "algorithm_id": algorithm_id,
        "candidate_evidence_accepted": True,
        "accepted": False,
        "production_release_accepted": False,
        "selection_performed": False,
        "selected_candidate": None,
        "final_pareto_ingestion_allowed": True,
        "full_pipeline_qualified": True,
        "errors": [],
    }
    for name, expected in expected_unified.items():
        if unified.get(name) != expected:
            raise ReleaseMaterializationError("unified audit field is not qualified: " + name)
    if unified.get("derived_production_pareto_metrics") != record.get("metrics"):
        raise ReleaseMaterializationError("unified audit metrics differ from the candidate record")
    if record.get("fallback_qualified") is not True or record.get("restoration_verified") is not True:
        raise ReleaseMaterializationError("candidate fallback/restoration evidence is incomplete")
    if record.get("final_pareto_ingestion_allowed") is not True:
        raise ReleaseMaterializationError("candidate is not admitted to Pareto materialization")
    run_ids = record.get("measured_run_ids")
    repeats = record.get("measured_repeats")
    if not isinstance(run_ids, list) or len(run_ids) != repeats or len(run_ids) < 3 \
      or len(run_ids) != len(set(run_ids)) or any(not isinstance(item, str) or not item for item in run_ids):
        raise ReleaseMaterializationError("candidate measured run identities are incomplete")
    runtime_sha = _sha(runtime_raw)
    runtime_reference = record.get("runtime_decision_receipt")
    if not isinstance(runtime_reference, Mapping) or runtime_reference.get("sha256") != runtime_sha \
      or runtime.get("receipt_scope") != "hft_mgbs_capture_runtime_decision_receipt_v1":
        raise ReleaseMaterializationError("runtime decision receipt identity is invalid")
    for name in ("code_sha256", "input_sha256", "evidence_manifest_sha256"):
        if not SHA_RE.fullmatch(str(record.get(name, ""))):
            raise ReleaseMaterializationError("candidate identity is invalid: " + name)
    receipt = {
        "schema_version": 1,
        "scope": "sealed_unified_candidate_evidence_receipt",
        "candidate_id": candidate_id,
        "algorithm_id": algorithm_id,
        "backend": backend,
        "candidate_evidence_accepted": True,
        "production_release_accepted": False,
        "selection_performed": False,
        "final_pareto_ingestion_allowed": True,
        "fallback_qualified": True,
        "restoration_verified": True,
        "algorithm_search_sha256": _sha(search_raw),
        "measured_run_ids": list(run_ids),
        "metrics": record.get("metrics"),
        "manifest_status": record.get("manifest_status"),
        "measured_repeats": repeats,
        "unified_candidate_evidence_audit_sha256": _sha(unified_raw),
        "evidence": record.get("evidence"),
        "code_sha256": record.get("code_sha256"),
        "input_sha256": record.get("input_sha256"),
        "evidence_manifest_sha256": record.get("evidence_manifest_sha256"),
        "runtime_decision_receipt_sha256": runtime_sha,
    }
    materialized = dict(record)
    receipt_sha = _sha(_canonical(receipt))
    materialized["candidate_evidence_receipt"] = {
        "path": str(output_receipt_path.resolve()),
        "sha256": receipt_sha,
    }
    materialized["unified_candidate_evidence_audit"] = {
        "path": str(unified_audit_path.resolve()),
        "sha256": _sha(unified_raw),
    }
    _create_json_transaction(
        ((output_receipt_path, receipt), (output_record_path, materialized))
    )
    return materialized


def _validated_materialized_candidate(path: Path) -> Tuple[Dict[str, Any], str, str]:
    record, record_raw = _json(path)
    reference = record.get("candidate_evidence_receipt")
    if not isinstance(reference, Mapping):
        raise ReleaseMaterializationError("candidate record omits its sealed receipt")
    receipt_path_raw = reference.get("path")
    expected_receipt_sha = reference.get("sha256")
    if not isinstance(receipt_path_raw, str) or not Path(receipt_path_raw).is_absolute() \
      or not SHA_RE.fullmatch(str(expected_receipt_sha or "")):
        raise ReleaseMaterializationError("candidate receipt reference is not absolute and sealed")
    receipt, receipt_raw = _json(Path(receipt_path_raw))
    receipt_sha = _sha(receipt_raw)
    if receipt_sha != expected_receipt_sha:
        raise ReleaseMaterializationError("candidate receipt SHA-256 drifted")
    expected = {
        "schema_version": 1,
        "scope": "sealed_unified_candidate_evidence_receipt",
        "candidate_id": record.get("candidate_id"),
        "algorithm_id": record.get("algorithm_id"),
        "backend": record.get("backend"),
        "candidate_evidence_accepted": True,
        "production_release_accepted": False,
        "selection_performed": False,
        "final_pareto_ingestion_allowed": True,
        "fallback_qualified": True,
        "restoration_verified": True,
    }
    for name, expected_value in expected.items():
        if receipt.get(name) != expected_value:
            raise ReleaseMaterializationError("candidate receipt field drifted: " + name)
    for name in (
        "metrics", "manifest_status", "measured_repeats", "evidence",
        "code_sha256", "input_sha256", "evidence_manifest_sha256",
    ):
        if receipt.get(name) != record.get(name):
            raise ReleaseMaterializationError("candidate receipt does not bind record field: " + name)
    runs = receipt.get("measured_run_ids")
    if not isinstance(runs, list) or len(runs) != receipt.get("measured_repeats") \
      or len(runs) < 3 or len(runs) != len(set(runs)):
        raise ReleaseMaterializationError("candidate receipt run identities are incomplete")
    for name in (
        "algorithm_search_sha256", "unified_candidate_evidence_audit_sha256",
        "runtime_decision_receipt_sha256",
    ):
        if not SHA_RE.fullmatch(str(receipt.get(name, ""))):
            raise ReleaseMaterializationError("candidate receipt identity is invalid: " + name)
    return record, _sha(record_raw), receipt_sha


def materialize_candidate_set(
    *, candidate_record_paths: Iterable[Path], output_dir: Path, minimum_candidates: int = 2
) -> Dict[str, Any]:
    """Seal the exact candidate array consumed by the production Pareto selector."""
    paths = tuple(candidate_record_paths)
    if minimum_candidates < 2:
        raise ReleaseMaterializationError("candidate-set minimum must be at least two")
    if len(paths) < minimum_candidates:
        raise ReleaseMaterializationError("insufficient independently sealed candidates")
    if output_dir.exists() or output_dir.is_symlink():
        raise ReleaseMaterializationError("candidate-set output directory must be new")
    records = []
    inputs = []
    candidate_ids = set()
    algorithm_search_shas = set()
    for path in paths:
        record, record_sha, receipt_sha = _validated_materialized_candidate(path)
        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id or candidate_id in candidate_ids:
            raise ReleaseMaterializationError("candidate IDs must be nonempty and distinct")
        candidate_ids.add(candidate_id)
        receipt_reference = record["candidate_evidence_receipt"]
        receipt, _ = _json(Path(receipt_reference["path"]))
        algorithm_search_shas.add(receipt["algorithm_search_sha256"])
        records.append(record)
        inputs.append({
            "candidate_id": candidate_id,
            "record_path": str(path.resolve()),
            "record_sha256": record_sha,
            "candidate_receipt_sha256": receipt_sha,
        })
    if len(algorithm_search_shas) != 1:
        raise ReleaseMaterializationError("candidates do not share one algorithm-search identity")
    parent = _safe_parent(output_dir)
    temporary = Path(tempfile.mkdtemp(prefix=output_dir.name + ".", suffix=".tmp", dir=str(parent)))
    try:
        candidates_path = temporary / "candidates.json"
        candidates_raw = _canonical(records)
        candidates_path.write_bytes(candidates_raw)
        manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_sealed_candidate_set_v1",
            "candidate_count": len(records),
            "candidate_ids": sorted(candidate_ids),
            "algorithm_search_sha256": next(iter(algorithm_search_shas)),
            "candidates_sha256": _sha(candidates_raw),
            "inputs": inputs,
            "production_release_accepted": False,
            "selection_performed": False,
            "final_pareto_ingestion_allowed": True,
        }
        (temporary / "manifest.json").write_bytes(_canonical(manifest))
        if output_dir.exists() or output_dir.is_symlink():
            raise ReleaseMaterializationError("candidate-set output raced")
        os.replace(str(temporary), str(output_dir))
    except BaseException:
        import shutil
        shutil.rmtree(str(temporary), ignore_errors=True)
        raise
    return manifest


def promote_algorithm_campaign(
    *,
    repo_root: Path,
    contract_path: Path,
    campaign_root: Path,
    formal_receipt_path: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    if output_dir.exists() or output_dir.is_symlink():
        raise ReleaseMaterializationError("promotion output directory must be new")
    replay = verify_algorithm_campaign_raw_replay(
        repo_root=repo_root,
        contract_path=contract_path,
        campaign_root=campaign_root,
        formal_receipt_path=formal_receipt_path,
    )
    if replay.get("accepted") is not True or replay.get("authoritative_raw_replay_complete") is not True:
        raise ReleaseMaterializationError("authoritative raw replay rejected the campaign")
    formal, formal_raw = _json(formal_receipt_path)
    reference = formal.get("suggested_algorithm_search_projection")
    if not isinstance(reference, Mapping) or not isinstance(reference.get("path"), str) \
      or not SHA_RE.fullmatch(str(reference.get("sha256", ""))):
        raise ReleaseMaterializationError("formal receipt omits the projected algorithm search")
    projection_path = Path(reference["path"]).resolve(strict=True)
    projection_path.relative_to(campaign_root.resolve(strict=True))
    projection, projection_raw = _json(projection_path)
    if _sha(projection_raw) != reference["sha256"]:
        raise ReleaseMaterializationError("projected search identity drifted")
    audit = audit_algorithm_search(projection)
    winner = replay.get("selected_candidate")
    if audit.get("accepted") is not True or audit.get("confirmatory_practical_winner") != winner \
      or projection.get("selected_candidate") != winner:
        raise ReleaseMaterializationError("projected algorithm search does not reproduce the winner")
    parent = _safe_parent(output_dir)
    temporary = Path(tempfile.mkdtemp(prefix=output_dir.name + ".", suffix=".tmp", dir=str(parent)))
    try:
        search_path = temporary / "algorithm_search_promoted.json"
        audit_path = temporary / "algorithm_optimality_audit.json"
        search_path.write_bytes(_canonical(projection))
        audit_path.write_bytes(_canonical(audit))
        receipt = {
            "schema_version": 1,
            "scope": "hft_mgbs_algorithm_campaign_promotion_receipt_v1",
            "accepted": True,
            "winner": winner,
            "contract_sha256": _sha(_stable(contract_path)),
            "formal_receipt_sha256": _sha(formal_raw),
            "projection_sha256": _sha(projection_raw),
            "promoted_algorithm_search_sha256": _sha(search_path.read_bytes()),
            "optimality_audit_sha256": _sha(audit_path.read_bytes()),
            "authoritative_raw_replay_complete": True,
            "raw_repeat_count": replay.get("raw_repeat_count"),
            "candidate_count": replay.get("evaluated_candidate_count"),
            "production_joint_optimum_proven": False,
            "final_pareto_ingestion_allowed": False,
        }
        receipt_path = temporary / "promotion_receipt.json"
        receipt_path.write_bytes(_canonical(receipt))
        manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_algorithm_promotion_manifest_v1",
            "winner": winner,
            "artifacts": [
                {"path": path.name, "sha256": _sha(path.read_bytes())}
                for path in (search_path, audit_path, receipt_path)
            ],
            "release_configuration_materialization_required": True,
            "production_release_accepted": False,
        }
        (temporary / "manifest.json").write_bytes(_canonical(manifest))
        if output_dir.exists() or output_dir.is_symlink():
            raise ReleaseMaterializationError("promotion output raced")
        os.replace(str(temporary), str(output_dir))
    except BaseException:
        import shutil
        shutil.rmtree(str(temporary), ignore_errors=True)
        raise
    return receipt


def _promotion_artifacts(promotion_dir: Path) -> Tuple[Dict[str, Any], Dict[str, Path]]:
    manifest, _ = _json(promotion_dir / "manifest.json")
    if manifest.get("scope") != "hft_mgbs_algorithm_promotion_manifest_v1" \
      or manifest.get("production_release_accepted") is not False:
        raise ReleaseMaterializationError("algorithm promotion manifest is invalid")
    entries = manifest.get("artifacts")
    if not isinstance(entries, list) or len(entries) != 3:
        raise ReleaseMaterializationError("algorithm promotion manifest artifact set is invalid")
    paths: Dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, Mapping) or not isinstance(entry.get("path"), str) \
          or Path(entry["path"]).name != entry["path"] \
          or not SHA_RE.fullmatch(str(entry.get("sha256", ""))):
            raise ReleaseMaterializationError("algorithm promotion artifact reference is invalid")
        path = promotion_dir / entry["path"]
        raw = _stable(path)
        if _sha(raw) != entry["sha256"]:
            raise ReleaseMaterializationError("algorithm promotion artifact SHA-256 drifted")
        paths[path.name] = path
    expected = {
        "algorithm_search_promoted.json", "algorithm_optimality_audit.json", "promotion_receipt.json"
    }
    if set(paths) != expected:
        raise ReleaseMaterializationError("algorithm promotion artifact names are not exact")
    return manifest, paths


def materialize_release_configuration(
    *,
    promotion_dir: Path,
    formal_receipt_path: Path,
    contract_path: Path,
    release_candidate_path: Path,
    manifest_template_path: Path,
    policy_template_path: Path,
    new_nic_r0_trust_profile_path: Path,
    deployment_candidate_id: str,
    output_dir: Path,
    runtime_failover_policy_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Build an auditable config package without turning pending hardware gates green."""
    if output_dir.exists() or output_dir.is_symlink():
        raise ReleaseMaterializationError("release-configuration output directory must be new")
    if not deployment_candidate_id or any(c in deployment_candidate_id for c in "\r\n\x00"):
        raise ReleaseMaterializationError("deployment candidate identity is invalid")
    promotion_manifest, artifacts = _promotion_artifacts(promotion_dir)
    promotion_receipt, _ = _json(artifacts["promotion_receipt.json"])
    search, search_raw = _json(artifacts["algorithm_search_promoted.json"])
    optimality, optimality_raw = _json(artifacts["algorithm_optimality_audit.json"])
    formal, formal_raw = _json(formal_receipt_path)
    contract, contract_raw = _json(contract_path)
    release_candidate, release_candidate_raw = _json(release_candidate_path)
    manifest_template, _ = _json(manifest_template_path)
    policy_template, _ = _json(policy_template_path)
    trust_profile, trust_profile_raw = _json(new_nic_r0_trust_profile_path)
    runtime_failover_policy = None
    runtime_failover_policy_raw = None
    if runtime_failover_policy_path is not None:
        runtime_failover_policy, runtime_failover_policy_raw = _json(
            runtime_failover_policy_path
        )
        legacy = (
            runtime_failover_policy.get("backend_requirements", {})
            .get("current_tpacket_v3_bcm57810", {})
        )
        boundaries = runtime_failover_policy.get("qualification_boundaries", {})
        if (
            runtime_failover_policy.get("schema_version") != 2
            or runtime_failover_policy.get("scope")
            != "hft_mgbs_capture_runtime_failover_policy_v2"
            or legacy.get("role") != "degraded_service_continuity_fallback"
            or legacy.get("production_eligible") is not False
            or legacy.get("service_continuity_eligible") is not True
            or boundaries.get("current_hardware_is_production_sla_eligible")
            is not False
        ):
            raise ReleaseMaterializationError(
                "runtime failover policy does not preserve the degraded fallback boundary"
            )
    winner = promotion_receipt.get("winner")
    if promotion_receipt.get("accepted") is not True \
      or not isinstance(winner, str) or search.get("selected_candidate") != winner \
      or optimality.get("accepted") is not True \
      or optimality.get("confirmatory_practical_winner") != winner:
        raise ReleaseMaterializationError("algorithm promotion does not bind one accepted winner")
    if promotion_manifest.get("winner") != winner:
        raise ReleaseMaterializationError("algorithm promotion winner drifted")
    if _sha(formal_raw) != promotion_receipt.get("formal_receipt_sha256") \
      or _sha(contract_raw) != promotion_receipt.get("contract_sha256"):
        raise ReleaseMaterializationError("formal campaign trust roots differ from the promotion")
    if release_candidate.get("candidate_id") != winner:
        raise ReleaseMaterializationError("release candidate does not implement the promoted winner")
    if trust_profile.get("scope") != "hft_mgbs_new_nic_r0_unified_trust_profile":
        raise ReleaseMaterializationError("new-NIC R0 trust profile instance is invalid")
    references = manifest_template.get("config_artifacts")
    if not isinstance(references, Mapping):
        raise ReleaseMaterializationError("release manifest template has no config artifacts")
    parent = _safe_parent(output_dir)
    temporary = Path(tempfile.mkdtemp(prefix=output_dir.name + ".", suffix=".tmp", dir=str(parent)))
    try:
        copied: Dict[str, Tuple[str, str]] = {}
        dynamic_names = {
            "algorithm_search", "algorithm_optimality_audit", "release_candidate",
            "new_nic_r0_trust_profile",
        }
        for name, reference in references.items():
            if name in dynamic_names:
                continue
            if not isinstance(reference, Mapping) or not isinstance(reference.get("path"), str):
                raise ReleaseMaterializationError("manifest config reference is invalid: " + str(name))
            source = (manifest_template_path.parent / reference["path"]).resolve(strict=True)
            source.relative_to(manifest_template_path.parent.resolve(strict=True))
            raw = _stable(source)
            if _sha(raw) != reference.get("sha256"):
                raise ReleaseMaterializationError("manifest template config drifted: " + str(name))
            target_name = "dependency__{}__{}".format(name, source.name)
            (temporary / target_name).write_bytes(raw)
            copied[str(name)] = (target_name, _sha(raw))
        dynamic = {
            "algorithm_search": ("algorithm_search_promoted.json", search_raw),
            "algorithm_optimality_audit": ("algorithm_optimality_audit.json", optimality_raw),
            "release_candidate": ("release_candidate.json", release_candidate_raw),
            "new_nic_r0_trust_profile": ("new_nic_r0_trust_profile.json", trust_profile_raw),
        }
        if runtime_failover_policy_raw is not None:
            dynamic["runtime_failover_policy"] = (
                "capture_runtime_failover_policy.json",
                runtime_failover_policy_raw,
            )
        for name, (target_name, raw) in dynamic.items():
            (temporary / target_name).write_bytes(raw)
            copied[name] = (target_name, _sha(raw))
        (temporary / "algorithm_campaign_contract.json").write_bytes(contract_raw)
        (temporary / "algorithm_campaign_receipt.json").write_bytes(formal_raw)
        manifest = copy_mapping = dict(manifest_template)
        manifest = json.loads(json.dumps(copy_mapping, allow_nan=False))
        manifest["candidate_id"] = winner
        manifest["deployment_candidate_id"] = deployment_candidate_id
        manifest["status"] = "algorithm_promoted__hardware_and_stage_gates_pending"
        manifest["config_artifacts"] = {
            name: {"path": path, "sha256": digest}
            for name, (path, digest) in sorted(copied.items())
        }
        manifest["algorithm_campaign_gate"] = {
            "required": True,
            "contract": {
                "path": "algorithm_campaign_contract.json", "sha256": _sha(contract_raw)
            },
            "receipt": {
                "path": "algorithm_campaign_receipt.json", "sha256": _sha(formal_raw)
            },
        }
        manifest["final_pareto_eligible"] = False
        policy = json.loads(json.dumps(policy_template, allow_nan=False))
        policy["algorithm_search_gate"]["path"] = "algorithm_search_promoted.json"
        policy["algorithm_search_gate"]["sha256"] = _sha(search_raw)
        policy["algorithm_search_gate"]["allowed_algorithm_ids"] = [winner]
        policy["algorithm_search_gate"]["optimality_audit_path"] = "algorithm_optimality_audit.json"
        policy["algorithm_search_gate"]["optimality_audit_sha256"] = _sha(optimality_raw)
        policy["algorithm_campaign_gate"] = dict(manifest["algorithm_campaign_gate"])
        manifest_raw = _canonical(manifest)
        policy_raw = _canonical(policy)
        (temporary / "release_manifest.json").write_bytes(manifest_raw)
        (temporary / "final_pareto_policy.json").write_bytes(policy_raw)
        receipt = {
            "schema_version": 1,
            "scope": "hft_mgbs_release_configuration_materialization_receipt_v1",
            "accepted": True,
            "winner": winner,
            "deployment_candidate_id": deployment_candidate_id,
            "release_manifest_sha256": _sha(manifest_raw),
            "final_pareto_policy_sha256": _sha(policy_raw),
            "formal_campaign_receipt_sha256": _sha(formal_raw),
            "algorithm_search_sha256": _sha(search_raw),
            "algorithm_optimality_audit_sha256": _sha(optimality_raw),
            "release_candidate_sha256": _sha(release_candidate_raw),
            "new_nic_r0_trust_profile_sha256": _sha(trust_profile_raw),
            "new_nic_r0_trust_profile_status": trust_profile.get("status"),
            "runtime_failover_policy_sha256": (
                _sha(runtime_failover_policy_raw)
                if runtime_failover_policy_raw is not None
                else None
            ),
            "runtime_failover_code_ready": runtime_failover_policy is not None,
            "current_hardware_fallback_role": (
                "degraded_service_continuity_fallback_only"
                if runtime_failover_policy is not None
                else None
            ),
            "hardware_and_stage_evidence_required": True,
            "production_release_accepted": False,
            "final_pareto_ingestion_allowed": False,
        }
        (temporary / "materialization_receipt.json").write_bytes(_canonical(receipt))
        package_manifest = {
            "schema_version": 1,
            "scope": "hft_mgbs_release_configuration_package_v1",
            "artifacts": [
                {"path": path.name, "sha256": _sha(path.read_bytes())}
                for path in sorted(temporary.iterdir(), key=lambda item: item.name)
                if path.is_file()
            ],
            "production_release_accepted": False,
        }
        (temporary / "package_manifest.json").write_bytes(_canonical(package_manifest))
        if output_dir.exists() or output_dir.is_symlink():
            raise ReleaseMaterializationError("release-configuration output raced")
        os.replace(str(temporary), str(output_dir))
    except BaseException:
        import shutil
        shutil.rmtree(str(temporary), ignore_errors=True)
        raise
    return receipt
