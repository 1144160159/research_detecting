"""Compare two captured Rust raw_v1 feature-stream summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.feature_equivalence import compare_feature_summaries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--require",
        choices=("base", "full"),
        default="full",
    )
    args = parser.parse_args()
    before = json.loads(args.before.read_text(encoding="utf-8"))
    after = json.loads(args.after.read_text(encoding="utf-8"))
    result = compare_feature_summaries(before, after, require=args.require)
    result.update(
        {
            "schema_version": 1,
            "scope": "rust_feature_stream_equivalence_comparison",
            "before": str(args.before),
            "after": str(args.after),
            "before_base_feature_multiset_sha256": before[
                "base_feature_multiset_sha256"
            ],
            "after_base_feature_multiset_sha256": after[
                "base_feature_multiset_sha256"
            ],
            "before_full_feature_multiset_sha256": before[
                "full_feature_multiset_sha256"
            ],
            "after_full_feature_multiset_sha256": after[
                "full_feature_multiset_sha256"
            ],
        }
    )
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
