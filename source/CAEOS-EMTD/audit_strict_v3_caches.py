from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate strict-v3 cache sidecars against actual CSV content"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--seeds", default="7,11,19,23,37")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_counts(path: Path, label_column: str) -> tuple[int, dict[str, int]]:
    counts: Counter[str] = Counter()
    rows = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or label_column not in reader.fieldnames:
            raise ValueError(f"{path} is missing label column {label_column}")
        for row in reader:
            counts[str(row[label_column]).strip()] += 1
            rows += 1
    return rows, dict(sorted(counts.items()))


def audit_cache(
    path: Path,
    label_column: str,
    expected_seed: int,
    expected_maximum: int,
) -> dict[str, object]:
    sidecar = Path(f"{path}.json")
    problems = []
    if not sidecar.is_file():
        return {"path": str(path.resolve()), "problems": ["missing sidecar"]}
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    actual_sha = sha256(path)
    actual_rows, actual_counts = csv_counts(path, label_column)
    checks = {
        "seed": (metadata.get("seed"), expected_seed),
        "max_per_class": (metadata.get("max_per_class"), expected_maximum),
        "rows": (metadata.get("rows"), actual_rows),
        "per_class": (metadata.get("per_class"), actual_counts),
        "output_sha256": (metadata.get("output_sha256"), actual_sha),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            problems.append(f"{name}: {actual!r} != {expected!r}")
    return {
        "path": str(path.resolve()),
        "sidecar": str(sidecar.resolve()),
        "seed": expected_seed,
        "max_per_class": expected_maximum,
        "rows": actual_rows,
        "per_class": actual_counts,
        "sha256": actual_sha,
        "problems": problems,
    }


def audit(root: str, seeds: list[int], maximum: int) -> dict[str, object]:
    base = Path(root)
    suite_labels = {"nf_unsw": "Attack", "cicids2017": "Label"}
    reports = []
    for suite, label_column in suite_labels.items():
        directory = base / suite / "stratified"
        for seed in seeds:
            path = directory / f"seed{seed}_max{maximum}.csv"
            if not path.is_file():
                reports.append(
                    {
                        "suite": suite,
                        "seed": seed,
                        "path": str(path.resolve()),
                        "problems": ["missing cache"],
                    }
                )
                continue
            report = audit_cache(path, label_column, seed, maximum)
            report["suite"] = suite
            reports.append(report)
    failures = [report for report in reports if report["problems"]]
    return {
        "schema_version": "strict_v3_cache_audit_v1",
        "root": str(base.resolve()),
        "seeds": seeds,
        "max_per_class": maximum,
        "expected_cache_count": len(suite_labels) * len(seeds),
        "cache_count": len(reports),
        "reports": reports,
        "failure_count": len(failures),
        "failures": failures,
        "passes": not failures,
    }


def main() -> None:
    args = parse_arguments()
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    report = audit(args.root, seeds, args.max_per_class)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
