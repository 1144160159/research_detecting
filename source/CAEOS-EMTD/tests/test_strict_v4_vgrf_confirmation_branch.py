from __future__ import annotations

import json
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_vgrf_confirmation_protocol import SEEDS, build_inputs
from summarize_strict_v4_vgrf_confirmation import gain


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    coverage = json.loads((ROOT / "results/strict_v4_full103_seed7/coverage_manifest_v2.json").read_text(encoding="utf-8"))
    assert coverage["manifest_sha256"] == canonical_hash(coverage)
    records = build_inputs(ROOT, coverage)
    assert len(records) == 204
    assert len({(r["suite"], r["scenario"], r["training_seed"]) for r in records}) == 204
    assert {r["training_seed"] for r in records} == set(SEEDS)
    assert {seed: sum(r["training_seed"] == seed for r in records) for seed in SEEDS} == {311: 102, 313: 102}
    assert len({r["suite"] for r in records}) == 7
    assert abs(gain(0.8, 0.7, "unknown_auroc") - 0.1) < 1e-12
    assert abs(gain(0.1, 0.2, "unknown_fpr95") - 0.1) < 1e-12
    print("8/8 PASS")


if __name__ == "__main__":
    main()
