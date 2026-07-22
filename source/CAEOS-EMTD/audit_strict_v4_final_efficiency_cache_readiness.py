from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_seed7_cache_artifacts(
    coverage: dict[str, Any], path_overrides: dict[str, Path] | None = None
) -> dict[str, dict[str, object]]:
    records = coverage.get("cache_artifacts")
    if not isinstance(records, dict) or len(records) != 7:
        raise ValueError("coverage manifest must bind seven cache artifacts")
    overrides = path_overrides or {}
    result = {}
    for suite, record in sorted(records.items()):
        if not isinstance(record, dict):
            raise ValueError(f"invalid cache record: {suite}")
        path = overrides.get(suite, Path(str(record.get("path", ""))))
        sidecar = Path(str(path) + ".json")
        path_matches = bool(
            path.is_file() and file_hash(path) == record.get("sha256")
        )
        sidecar_matches = bool(
            sidecar.is_file()
            and file_hash(sidecar) == record.get("sidecar_sha256")
        )
        result[suite] = {
            "path": str(path),
            "path_exists_and_sha_matches": path_matches,
            "sidecar_exists_and_sha_matches": sidecar_matches,
            "ready": path_matches and sidecar_matches,
        }
    return result


def find_seed191_artifacts(
    search_roots: Sequence[Path], expected_suites: Sequence[str]
) -> dict[str, list[dict[str, object]]]:
    paths_by_suite: dict[str, set[Path]] = {suite: set() for suite in expected_suites}
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*seed191*.csv"):
            lowered_parts = {part.lower() for part in path.parts}
            for suite in expected_suites:
                if suite.lower() in lowered_parts:
                    paths_by_suite[suite].add(path.resolve())
    result = {}
    for suite, paths in paths_by_suite.items():
        records = []
        for path in sorted(paths, key=str):
            sidecar = Path(str(path) + ".json")
            ready = path.is_file() and sidecar.is_file()
            records.append(
                {
                    "path": str(path),
                    "sha256": file_hash(path) if path.is_file() else None,
                    "sidecar_path": str(sidecar),
                    "sidecar_sha256": file_hash(sidecar)
                    if sidecar.is_file()
                    else None,
                    "ready": ready,
                }
            )
        result[suite] = records
    return result


def build_audit(
    coverage: dict[str, Any],
    *,
    search_roots: Sequence[Path],
    path_overrides: dict[str, Path] | None = None,
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage manifest schema")
    seed7 = verify_seed7_cache_artifacts(coverage, path_overrides)
    suites = sorted(seed7)
    seed191 = find_seed191_artifacts(search_roots, suites)
    seed7_ready = sum(int(record["ready"]) for record in seed7.values())
    seed191_ready = sum(
        int(len(records) == 1 and records[0]["ready"])
        for records in seed191.values()
    )
    return {
        "schema_version": "strict_v4_final_efficiency_cache_readiness_v1",
        "coverage_manifest_sha256": coverage.get("manifest_sha256"),
        "seed7_frozen_replay": {
            "ready_suites": seed7_ready,
            "expected_suites": len(suites),
            "all_sha_verified": seed7_ready == len(suites),
            "artifacts": seed7,
        },
        "seed191_training_sentinels": {
            "ready_suites": seed191_ready,
            "expected_suites": len(suites),
            "precompute_required": seed191_ready != len(suites),
            "artifacts": seed191,
            "exactly_one_complete_artifact_required_per_suite": True,
            "precompute_is_outside_timed_region": True,
        },
        "gates": {
            "protocol_freeze_blocked_by_cache_precompute": False,
            "formal_timing_allowed": bool(
                seed7_ready == len(suites) and seed191_ready == len(suites)
            ),
            "raw_data_or_cache_generation_must_not_enter_timed_region": True,
        },
    }


def render(audit: dict[str, Any]) -> str:
    seed7 = audit["seed7_frozen_replay"]
    seed191 = audit["seed191_training_sentinels"]
    return "\n".join(
        [
            "# Strict-v4 final efficiency cache readiness",
            "",
            f"- Seed7 frozen replay caches: `{seed7['ready_suites']}/{seed7['expected_suites']}`.",
            f"- Seed191 training caches: `{seed191['ready_suites']}/{seed191['expected_suites']}`.",
            f"- Seed191 precompute required: `{seed191['precompute_required']}`.",
            f"- Formal timing allowed: `{audit['gates']['formal_timing_allowed']}`.",
            "- Cache generation is excluded from all timed regions.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--search-root", type=Path, action="append", default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    audit = build_audit(coverage, search_roots=args.search_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "cache_readiness.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "cache_readiness.md").write_text(
        render(audit), encoding="utf-8"
    )
    print(render(audit), end="")


if __name__ == "__main__":
    main()
