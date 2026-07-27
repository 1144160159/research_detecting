from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path
from typing import Any

import prepare_gpu_external_datasets as base
from external_dataset_labels import canonical_external_label
from external_dataset_protocol_utils import canonical_hash


def require_admission(audit: dict[str, Any], dataset: str) -> None:
    if (
        audit.get("schema_version")
        != "gpu_malicious_dataset_reconciled_admission_audit_v2"
        or audit.get("manifest_sha256") != canonical_hash(audit)
        or audit.get("admission_passed") is not True
        or audit.get("datasets", {}).get(dataset, {}).get("admission_passed")
        is not True
    ):
        raise ValueError(f"{dataset} lacks canonical reconciled admission")


def prepare_dataset(
    *,
    dataset: str,
    archive_paths: list[Path],
    config: dict[str, Any],
    seeds: list[int],
    groups_per_label: int,
    rows_per_group: int,
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any]]:
    features = base.feature_columns(config)
    states = {
        seed: base.SeedReservoir(seed, groups_per_label, rows_per_group)
        for seed in seeds
    }
    source_rows = 0
    missing_group_rows = 0
    source_labels: Counter[str] = Counter()
    for archive, info in base.iter_csv_members(archive_paths):
        with archive.open(info) as raw:
            text = io.TextIOWrapper(
                raw, encoding="utf-8-sig", errors="replace", newline=""
            )
            reader = csv.reader(text)
            header = [
                base.normalized_header(value) for value in next(reader, [])
            ]
            columns = {name: index for index, name in enumerate(header)}
            sessionizer = (
                base.LsnmSessionizer(info.filename)
                if dataset == "LSNM2024"
                else None
            )
            previous_time: dict[str, float] = {}
            for row_index, row in enumerate(reader, 1):
                if not row:
                    continue
                source_rows += 1
                if dataset == "LSNM2024":
                    label = base.lsnm_path_label(info.filename)
                    group = (
                        sessionizer.group(row, columns)
                        if sessionizer
                        else None
                    )
                else:
                    label = canonical_external_label(
                        "CICDDoS2019",
                        info.filename,
                        base.row_value(row, columns, "Label"),
                    )
                    group = base.cicddos_group(info.filename, row, columns)
                if not label or group is None:
                    missing_group_rows += 1
                    continue
                source_labels[label] += 1
                selected_states = [
                    state
                    for state in states.values()
                    if state.consider_group(label, group)
                ]
                if not selected_states:
                    continue
                if dataset == "LSNM2024":
                    timestamp = base.numeric_value(
                        base.row_value(
                            row, columns, "Frame Time (Epoch)", "Time"
                        )
                    )
                    delta = max(
                        0.0, timestamp - previous_time.get(group, timestamp)
                    )
                    previous_time[group] = timestamp
                    normalized = base.lsnm_row(
                        row, columns, features, group, label, delta
                    )
                else:
                    normalized = base.cicddos_row(
                        row, columns, features, group, label
                    )
                for state in selected_states:
                    state.consider_row(
                        label=label,
                        group=group,
                        member=info.filename,
                        row_index=row_index,
                        row=normalized,
                    )
    outputs = {seed: state.output_rows() for seed, state in states.items()}
    summary = {
        "dataset": dataset,
        "source_rows": source_rows,
        "source_label_counts": dict(sorted(source_labels.items())),
        "missing_group_or_label_rows": missing_group_rows,
        "features": features,
        "seeds": {str(seed): states[seed].summary() for seed in seeds},
        "label_reconciliation": {
            "UDP-lag": "UDPLag"
        }
        if dataset == "CICDDoS2019"
        else {},
    }
    return outputs, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        choices=("LSNM2024", "CICDDoS2019"),
        required=True,
    )
    parser.add_argument("--admission-audit", type=Path, required=True)
    parser.add_argument("--expansion-protocol", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[223, 227, 229])
    parser.add_argument("--groups-per-label", type=int, required=True)
    parser.add_argument("--rows-per-group", type=int, required=True)
    args = parser.parse_args()
    audit = json.loads(args.admission_audit.read_text(encoding="utf-8"))
    protocol = json.loads(
        args.expansion_protocol.read_text(encoding="utf-8")
    )
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require_admission(audit, args.dataset)
    identities = protocol["source_identity"]
    token = "LSNM2024" if args.dataset == "LSNM2024" else "CICDDoS2019"
    archives = [
        Path(item["path"]) for item in identities if token in item["path"]
    ]
    outputs, summary = prepare_dataset(
        dataset=args.dataset,
        archive_paths=archives,
        config=config,
        seeds=args.seeds,
        groups_per_label=args.groups_per_label,
        rows_per_group=args.rows_per_group,
    )
    provenance = {
        "reconciled_admission_audit_sha256": base.sha256_file(
            args.admission_audit
        ),
        "label_reconciliation_protocol_manifest_sha256": audit[
            "protocol_manifest_sha256"
        ],
        "expansion_protocol_sha256": base.sha256_file(
            args.expansion_protocol
        ),
        "config_sha256": base.sha256_file(args.config),
        "source_sha256": audit["source_sha256"],
        "groups_per_label": args.groups_per_label,
        "rows_per_group": args.rows_per_group,
    }
    manifest = base.write_prepared(
        dataset=args.dataset,
        outputs=outputs,
        summary=summary,
        config=config,
        output_root=args.output_root,
        provenance=provenance,
    )
    if not manifest["passed"]:
        raise SystemExit(
            f"{args.dataset} v2 preparation failed integrity gates"
        )
    print(json.dumps({"dataset": args.dataset, "passed": True}, sort_keys=True))


if __name__ == "__main__":
    main()
