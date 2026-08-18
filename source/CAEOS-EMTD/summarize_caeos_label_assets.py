from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from prepare_caeos_unified_multimodal_csv import load_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    audit = load_json(args.audit)
    summary = []
    for dataset in audit["datasets"]:
        candidates = dataset.get("candidates", [])
        suffix_counts = Counter(item["suffix"] for item in candidates)
        header_groups: dict[tuple[str, ...], list[dict]] = {}
        for item in candidates:
            fields = tuple(field.strip() for field in item.get("header_fields", []))
            if fields:
                header_groups.setdefault(fields, []).append(item)
        headers = []
        for fields, items in sorted(
            header_groups.items(), key=lambda pair: (-len(pair[1]), pair[0])
        )[: args.limit]:
            headers.append(
                {
                    "file_count": len(items),
                    "fields": list(fields),
                    "representative_path": items[0]["path"],
                }
            )
        summary.append(
            {
                "id": dataset["id"],
                "candidate_count": len(candidates),
                "suffix_counts": dict(sorted(suffix_counts.items())),
                "header_groups": headers,
            }
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
