from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from summarize_neural_comparison_strict_v2 import _validate_pair_identity


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def audit(gate_root: Path, baseline_roots: list[Path]) -> dict[str, object]:
    counts: Counter[str] = Counter()
    issues = []
    checked_paths = set()
    for baseline_root in baseline_roots:
        for path in sorted(baseline_root.glob("*/*/metrics.json")):
            resolved = path.resolve()
            if resolved in checked_paths:
                issues.append(f"duplicate baseline metrics path: {path}")
                continue
            checked_paths.add(resolved)
            try:
                payload = read_object(path)
                seed = int(payload["seed"])
                suite = path.parent.parent.name
                marker = f"_seed{seed}"
                if marker not in path.parent.name:
                    raise ValueError(f"run directory does not encode seed {seed}")
                scenario = path.parent.name.split(marker, 1)[0]
                gate_path = gate_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
                if not gate_path.is_file():
                    raise ValueError(f"missing paired gate metrics: {gate_path}")
                gate_payload = read_object(gate_path)
                _validate_pair_identity(
                    gate_payload,
                    gate_path,
                    payload,
                    path,
                    (suite, scenario, seed),
                )
                counts[suite] += 1
            except (OSError, ValueError, KeyError, TypeError) as error:
                issues.append(f"{path}: {error}")
    return {
        "schema_version": "partial_pair_identity_audit_v1",
        "gate_root": str(gate_root),
        "baseline_roots": [str(path) for path in baseline_roots],
        "checked_pairs": sum(counts.values()),
        "checked_by_suite": dict(sorted(counts.items())),
        "issue_count": len(issues),
        "issues": issues,
        "passes": not issues,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit all currently completed paired runs")
    parser.add_argument("--gate-root", required=True)
    parser.add_argument("--baseline-root", action="append", required=True)
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = audit(
        Path(args.gate_root), [Path(value) for value in args.baseline_root]
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["passes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
