"""Canonical digests for Rust-to-inference feature stream equivalence."""

from __future__ import annotations

import hashlib
import json


def _digest_lines(lines):
    digest = hashlib.sha256()
    for line in sorted(lines):
        digest.update(line.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def summarize_feature_vectors(feature_vectors):
    full_hashes = []
    base_hashes = []
    deep_tier_count = 0
    for features in feature_vectors:
        if len(features) != 38:
            raise ValueError(
                "expected 38 features, received {}".format(len(features))
            )
        serialized = json.dumps(
            features,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        )
        base_serialized = json.dumps(
            features[:34],
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        )
        full_hashes.append(
            hashlib.sha256(serialized.encode("ascii")).hexdigest()
        )
        base_hashes.append(
            hashlib.sha256(base_serialized.encode("ascii")).hexdigest()
        )
        deep_tier_count += int(features[37] == 1.0)
    return {
        "flow_count": len(feature_vectors),
        "feature_count": 38,
        "base_feature_multiset_sha256": _digest_lines(base_hashes),
        "full_feature_multiset_sha256": _digest_lines(full_hashes),
        "deep_tier_count": deep_tier_count,
        "base_feature_hashes": sorted(base_hashes),
        "full_feature_hashes": sorted(full_hashes),
    }


def compare_feature_summaries(before, after, require="full"):
    if require not in ("base", "full"):
        raise ValueError("require must be base or full")
    checks = {
        "flow_count_equal": before.get("flow_count")
        == after.get("flow_count"),
        "feature_count_equal": before.get("feature_count")
        == after.get("feature_count")
        == 38,
        "base_feature_multiset_equal": before.get(
            "base_feature_multiset_sha256"
        )
        == after.get("base_feature_multiset_sha256"),
        "full_feature_multiset_equal": before.get(
            "full_feature_multiset_sha256"
        )
        == after.get("full_feature_multiset_sha256"),
        "deep_tier_count_equal": before.get("deep_tier_count")
        == after.get("deep_tier_count"),
    }
    required_checks = [
        "flow_count_equal",
        "feature_count_equal",
        "base_feature_multiset_equal",
    ]
    if require == "full":
        required_checks.extend(
            ("full_feature_multiset_equal", "deep_tier_count_equal")
        )
    return {
        "checks": checks,
        "required_equivalence": require,
        "required_checks": required_checks,
        "accepted": all(checks[name] for name in required_checks),
    }
