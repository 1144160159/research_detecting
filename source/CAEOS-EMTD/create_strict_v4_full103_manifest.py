from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from run_nested_gate_matrix import (
    CICIDS2017_SCENARIOS,
    CIC_IOT2023_SCENARIOS,
    CIC_TON_IOT_SCENARIOS,
    EDGE_IIOT_SCENARIOS,
    NF_CSE_SCENARIOS,
    NF_UNSW_SCENARIOS,
    USTC_TFC2016_SCENARIOS,
)
from select_strict_v4_external_risk_candidate import canonical_hash


SCENARIOS = {
    "edge_iiot": EDGE_IIOT_SCENARIOS,
    "nf_cse": NF_CSE_SCENARIOS,
    "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
    "nf_unsw": NF_UNSW_SCENARIOS,
    "cicids2017": CICIDS2017_SCENARIOS,
    "cic_ton_iot": CIC_TON_IOT_SCENARIOS,
    "cic_iot2023": CIC_IOT2023_SCENARIOS,
}
MAXIMUM_PER_CLASS = {
    "edge_iiot": 1000,
    "nf_cse": 1000,
    "ustc_tfc2016": 3000,
    "nf_unsw": 5000,
    "cicids2017": 5000,
    "cic_ton_iot": 1000,
    "cic_iot2023": 1000,
}
IMPLEMENTATIONS = (
    "create_strict_v4_full103_manifest.py",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
    "analyze_caeos_closr_fusion.py",
    "caeos/pseudo_unknown_risk.py",
    "scripts/run_strict_v4_full103_seed7.sh",
)
CONFIGS = (
    "configs/edge_iiot.json",
    "configs/nf_cse_cic_ids2018_v2.json",
    "configs/ustc_tfc2016_nfstream.json",
    "configs/nf_unsw_nb15.json",
    "configs/cicids2017_strict.json",
    "configs/cic_ton_iot_strict.json",
    "configs/cic_iot2023_strict.json",
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_cache(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"cache must use suite=path syntax: {value!r}")
    suite, raw_path = value.split("=", 1)
    suite = suite.strip()
    if suite not in SCENARIOS:
        raise ValueError(f"unknown cache suite: {suite!r}")
    path = Path(raw_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"cache file is missing: {path}")
    if not Path(f"{path}.json").is_file():
        raise FileNotFoundError(f"cache sidecar is missing: {path}.json")
    return suite, path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--pairwise-manifest", type=Path, required=True)
    parser.add_argument("--external-manifest", type=Path, required=True)
    parser.add_argument("--cache", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    caches = dict(parse_cache(value) for value in args.cache)
    if set(caches) != set(SCENARIOS):
        raise ValueError(
            f"cache coverage mismatch: expected={sorted(SCENARIOS)}, "
            f"observed={sorted(caches)}"
        )
    if sum(len(values) for values in SCENARIOS.values()) != 102:
        raise ValueError("strict-v4 scenario registry no longer contains 102 scenarios")

    pairwise = json.loads(args.pairwise_manifest.read_text(encoding="utf-8"))
    external = json.loads(args.external_manifest.read_text(encoding="utf-8"))
    if pairwise.get("manifest_sha256") != (
        "9fb6ba9a4c28be1cd3ef63153d814b4b5b956999890e24d35fbfd749d8091f01"
    ):
        raise ValueError("unexpected pairwise candidate manifest")
    if external.get("manifest_sha256") != (
        "7db2189d36cb5f5b9086f9dcd593dc30dd204a3f75b285035965cc65108130a8"
    ):
        raise ValueError("unexpected external-risk candidate manifest")

    payload: dict[str, Any] = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "status": "frozen_before_coverage_results",
        "purpose": (
            "single-seed coverage screen before multi-seed confirmatory SOTA matrix"
        ),
        "seed": 7,
        "datasets": 7,
        "scenario_inference_units": 102,
        "scenario_registry": {
            suite: {
                "count": len(values),
                "scenarios": list(values),
                "maximum_per_class": MAXIMUM_PER_CLASS[suite],
            }
            for suite, values in SCENARIOS.items()
        },
        "expected_runs": {
            "pairwise_caeos": 102,
            "mlp_openmax": 102,
            "fixed_fusion_reports": 102,
        },
        "candidate": {
            "base_algorithm": "nested_boundary_pairwise_pseudo_unknown_blend",
            "pairwise_manifest_sha256": pairwise["manifest_sha256"],
            "expert_model": "mlp",
            "expert_risk": "openmax",
            "fusion": "rank_union",
            "external_manifest_sha256": external["manifest_sha256"],
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "cache_artifacts": {
            suite: {
                "path": str(path),
                "sha256": file_hash(path),
                "sidecar_sha256": file_hash(Path(f"{path}.json")),
            }
            for suite, path in caches.items()
        },
        "implementation_sha256": {
            relative: file_hash(project_root / relative)
            for relative in IMPLEMENTATIONS
        },
        "config_sha256": {
            relative: file_hash(project_root / relative) for relative in CONFIGS
        },
        "inference_boundary": {
            "coverage_seed_is_confirmatory": False,
            "scenario_is_future_inference_unit": True,
            "seed_repeats_must_be_averaged_within_scenario": True,
            "full_sota_requires_multi_seed_strong_baseline_matrix": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
