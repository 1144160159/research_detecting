from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def derive_seed(
    design_manifest_sha256: str,
    dataset: str,
    unknown_attack_family: str,
    training_seed: int,
    purpose: str,
) -> int:
    token = (
        f"{design_manifest_sha256}:{dataset}:{unknown_attack_family}:"
        f"{int(training_seed)}:{purpose}"
    )
    return int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) & (
        2**31 - 1
    )


def build_scenarios(
    *,
    design: Dict[str, Any],
    preparation: Dict[str, Any],
    data_root: Path,
) -> list[Dict[str, Any]]:
    if (
        preparation.get("schema_version")
        != "gpu_external_dataset_preparation_summary_v1"
        or preparation.get("ready_for_frozen_external_experiments")
        is not True
    ):
        raise ValueError("external dataset preparation is incomplete")
    benign = {"LSNM2024": "normal", "CICDDoS2019": "BENIGN"}
    records: list[Dict[str, Any]] = []
    for dataset in design["datasets"]:
        manifest_path = data_root / dataset / "manifest.json"
        manifest = load(manifest_path)
        entry = preparation.get("datasets", {}).get(dataset, {})
        if (
            manifest.get("schema_version")
            != "gpu_external_prepared_dataset_manifest_v1"
            or manifest.get("dataset") != dataset
            or manifest.get("passed") is not True
            or entry.get("manifest_sha256") != file_hash(manifest_path)
        ):
            raise ValueError(f"invalid prepared dataset manifest: {dataset}")
        for seed in design["seeds"]:
            sidecar = manifest.get("files", {}).get(str(seed))
            csv_path = data_root / dataset / f"seed{seed}.csv"
            sidecar_path = Path(str(csv_path) + ".json")
            if (
                not isinstance(sidecar, dict)
                or sidecar.get("schema_version")
                != "gpu_external_prepared_seed_v1"
                or sidecar.get("passed") is not True
                or sidecar.get("csv_sha256") != file_hash(csv_path)
                or file_hash(sidecar_path) == ""
            ):
                raise ValueError(
                    f"invalid prepared seed sidecar: {dataset}/{seed}"
                )
            labels = sorted(map(str, sidecar["label_counts"]))
            matches = [
                label
                for label in labels
                if label.casefold() == benign[dataset].casefold()
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"exactly one benign label required: {dataset}/{seed}"
                )
            benign_label = matches[0]
            attacks = [label for label in labels if label != benign_label]
            if len(attacks) < 2 or any(
                int(sidecar["groups_per_label"].get(label, 0)) < 3
                for label in labels
            ):
                raise ValueError(
                    f"insufficient external labels/groups: {dataset}/{seed}"
                )
            for attack in attacks:
                records.append(
                    {
                        "dataset": dataset,
                        "unknown_attack_family": attack,
                        "benign_label": benign_label,
                        "seed": int(seed),
                        "augmentation_seed": derive_seed(
                            design["manifest_sha256"],
                            dataset,
                            attack,
                            seed,
                            "augmentation",
                        ),
                        "validation_profile_seed": derive_seed(
                            design["manifest_sha256"],
                            dataset,
                            attack,
                            seed,
                            "validation_profile",
                        ),
                        "csv": str(csv_path.resolve()),
                        "csv_sha256": sidecar["csv_sha256"],
                        "sidecar": str(sidecar_path.resolve()),
                        "sidecar_sha256": file_hash(sidecar_path),
                        "label_count": len(labels),
                    }
                )
    identities = {
        (
            item["dataset"],
            item["unknown_attack_family"],
            item["seed"],
        )
        for item in records
    }
    if len(identities) != len(records):
        raise ValueError("duplicate MDR external scenario identity")
    return records


def verify_implementation(
    project_root: Path, relatives: Iterable[str]
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing MDR external implementation: {relative}"
            )
        output[relative] = file_hash(path)
    for relative in (
        "capture_mdr_caeos_runtime.py",
        "train_mdr_caeos_open_set.py",
        "train_hybrid_open_set.py",
        "train_neural_open_set.py",
        "caeos/mdr_runtime.py",
        "caeos/mdr_fusion.py",
        "caeos/structured_robust.py",
    ):
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing MDR runtime source: {relative}")
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def create_protocol(
    *,
    project_root: Path,
    data_root: Path,
    run_root: Path,
    design: Dict[str, Any],
    postselection: Dict[str, Any],
    external_v1: Dict[str, Any],
    selection: Dict[str, Any],
    confirmation_protocol: Dict[str, Any],
    confirmation_summary: Dict[str, Any],
    confirmation_audit: Dict[str, Any],
    preparation: Dict[str, Any],
    input_file_sha256: Dict[str, str],
    observed_metrics: int,
) -> Dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_mdr_external_malicious_design_v1",
        "MDR external design",
    )
    require_canonical(
        postselection,
        "strict_v4_mdr_postselection_evidence_design_v1",
        "MDR post-selection design",
    )
    require_canonical(
        external_v1,
        "gpu_external_dataset_evaluation_design_protocol_v1",
        "external v1 design",
    )
    require_canonical(
        selection,
        "strict_v4_final_self_algorithm_selection_v2",
        "MDR final selection",
    )
    require_canonical(
        confirmation_protocol,
        "strict_v4_mdr_caeos_confirmation_protocol_v1",
        "MDR confirmation protocol",
    )
    require_canonical(
        confirmation_summary,
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        "MDR confirmation summary",
    )
    require_canonical(
        confirmation_audit,
        "strict_v4_mdr_caeos_confirmation_audit_v1",
        "MDR confirmation audit",
    )
    if int(observed_metrics) != 0:
        raise ValueError("MDR external protocol must freeze before metrics")
    if (
        design["input_manifest_sha256"]["postselection_design"]
        != postselection["manifest_sha256"]
        or design["input_manifest_sha256"]["external_v1_design"]
        != external_v1["manifest_sha256"]
    ):
        raise ValueError("MDR external design source binding mismatch")
    if (
        selection.get("selected_algorithm") != "mdr_caeos_v1"
        or selection.get("mdr_confirmation_passes") is not True
        or selection.get("protocol_manifest_sha256")
        != confirmation_protocol["manifest_sha256"]
        or selection.get("summary_manifest_sha256")
        != confirmation_summary["manifest_sha256"]
        or confirmation_summary.get("decision", {}).get("passes")
        is not True
        or confirmation_audit.get("passes") is not True
        or confirmation_audit.get("protocol_manifest_sha256")
        != confirmation_protocol["manifest_sha256"]
        or confirmation_audit.get("summary_manifest_sha256")
        != confirmation_summary["manifest_sha256"]
    ):
        raise ValueError("positive canonical MDR confirmation is required")
    selected_weight = float(
        confirmation_protocol["selected_augmentation_weight"]
    )
    scenarios = build_scenarios(
        design=design, preparation=preparation, data_root=data_root
    )
    implementations = verify_implementation(
        project_root, design["required_implementation"]
    )
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_protocol_v1"
        ),
        "status": (
            "frozen_after_positive_mdr_selection_and_preparation_"
            "before_external_metrics"
        ),
        "selected_algorithm": "mdr_caeos_v1",
        "primary_comparator": "opendetect",
        "design_manifest_sha256": design["manifest_sha256"],
        "selection_manifest_sha256": selection["manifest_sha256"],
        "confirmation_protocol_manifest_sha256": confirmation_protocol[
            "manifest_sha256"
        ],
        "confirmation_summary_manifest_sha256": confirmation_summary[
            "manifest_sha256"
        ],
        "confirmation_audit_manifest_sha256": confirmation_audit[
            "manifest_sha256"
        ],
        "mdr_policy": {
            "augmentation_weight": selected_weight,
            "sample_fraction": float(
                confirmation_protocol["confirmation"][
                    "training_sample_fraction"
                ]
            ),
            "health_quantile": float(
                confirmation_protocol["confirmation"]["health_quantile"]
            ),
            "weight_reselected_on_external_data": False,
        },
        "pairwise_runtime_policy": external_v1[
            "pairwise_runtime_policy"
        ],
        "opendetect_policy": design["opendetect_policy"],
        "formal_metrics": design["formal_metrics"],
        "confirmation_gate": design["confirmation_gate"],
        "statistics": design["statistics"],
        "scenarios": scenarios,
        "scenario_count": len(scenarios),
        "expected_formal_runs": 2 * len(scenarios),
        "formal_metric_count_at_freeze": 0,
        "paths": {
            "project_root": str(project_root.resolve()),
            "data_root": str(data_root.resolve()),
            "run_root": str(run_root.resolve()),
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementations,
        "claim_boundary": design["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument("--external-v1-design", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--preparation-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "design": args.design,
        "postselection_design": args.postselection_design,
        "external_v1_design": args.external_v1_design,
        "selection": args.selection,
        "confirmation_protocol": args.confirmation_protocol,
        "confirmation_summary": args.confirmation_summary,
        "confirmation_audit": args.confirmation_audit,
        "preparation_summary": args.preparation_summary,
    }
    observed = (
        len(list(args.run_root.glob("**/metrics.json")))
        if args.run_root.exists()
        else 0
    )
    value = create_protocol(
        project_root=args.project_root,
        data_root=args.data_root,
        run_root=args.run_root,
        design=load(args.design),
        postselection=load(args.postselection_design),
        external_v1=load(args.external_v1_design),
        selection=load(args.selection),
        confirmation_protocol=load(args.confirmation_protocol),
        confirmation_summary=load(args.confirmation_summary),
        confirmation_audit=load(args.confirmation_audit),
        preparation=load(args.preparation_summary),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        observed_metrics=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
