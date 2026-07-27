from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


RATE_METRICS = (
    "false_alert_rate",
    "known_attack_assignment_rate",
    "reject_rate",
    "operational_intervention_rate",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def bootstrap_mean(
    values: Iterable[float], *, seed: int, repetitions: int
) -> Dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if (
        array.ndim != 1
        or not len(array)
        or not np.isfinite(array).all()
        or int(repetitions) < 1
    ):
        raise ValueError("finite nonempty bootstrap values required")
    rng = np.random.default_rng(int(seed))
    sampled = array[
        rng.integers(
            0, len(array), size=(int(repetitions), len(array))
        )
    ].mean(axis=1)
    return {
        "n": int(len(array)),
        "mean": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(sampled, 0.025)),
            float(np.quantile(sampled, 0.975)),
        ],
    }


def bootstrap_independent_difference(
    left: Iterable[float],
    right: Iterable[float],
    *,
    seed: int,
    repetitions: int,
) -> Dict[str, Any]:
    left_array = np.asarray(list(left), dtype=np.float64)
    right_array = np.asarray(list(right), dtype=np.float64)
    if (
        not len(left_array)
        or not len(right_array)
        or not np.isfinite(left_array).all()
        or not np.isfinite(right_array).all()
    ):
        raise ValueError("finite nonempty independent samples required")
    rng = np.random.default_rng(int(seed))
    left_sample = left_array[
        rng.integers(
            0,
            len(left_array),
            size=(int(repetitions), len(left_array)),
        )
    ].mean(axis=1)
    right_sample = right_array[
        rng.integers(
            0,
            len(right_array),
            size=(int(repetitions), len(right_array)),
        )
    ].mean(axis=1)
    difference = left_sample - right_sample
    return {
        "left_n": int(len(left_array)),
        "right_n": int(len(right_array)),
        "mean_difference": float(
            left_array.mean() - right_array.mean()
        ),
        "bootstrap_95ci": [
            float(np.quantile(difference, 0.025)),
            float(np.quantile(difference, 0.975)),
        ],
    }


def aggregate(
    records: list[Dict[str, Any]], protocol: Dict[str, Any]
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_parrot_safety_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(records) != 30
    ):
        raise ValueError("canonical protocol and 30 model pairs required")
    expected = {
        (str(item["scenario"]), int(item["training_seed"]))
        for item in protocol["source_model_pairs"]
    }
    seen = set()
    by_capture: Dict[str, list[Dict[str, Any]]] = defaultdict(list)
    source_benign = []
    for value in records:
        source = value.get("source", {})
        identity = (
            str(source.get("scenario")),
            int(source.get("training_seed", -1)),
        )
        if (
            value.get("schema_version")
            != "strict_v4_mdr_parrot_model_pair_metrics_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("state") != "complete"
            or value.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or identity not in expected
            or identity in seen
            or int(value.get("capture_count", -1)) != 320
            or int(value.get("failure_count", -1)) != 0
            or value.get(
                "parrot_features_or_labels_used_for_fit_selection_"
                "calibration_or_threshold"
            )
            is not False
            or value.get("payload_decryption_used") is not False
        ):
            raise ValueError("invalid MDR PARROT model-pair metrics")
        seen.add(identity)
        source_reference = value["source_benign_reference"]
        source_benign.append(
            float(source_reference["false_alert_rate"])
        )
        capture_seen = set()
        for record in value["records"]:
            capture_id = str(record["capture_id"])
            if capture_id in capture_seen:
                raise ValueError("duplicate capture within model pair")
            capture_seen.add(capture_id)
            for method in ("mdr_caeos_v1", "opendetect"):
                metrics = record[method]
                if any(
                    not np.isfinite(float(metrics[name]))
                    or not 0.0 <= float(metrics[name]) <= 1.0
                    for name in RATE_METRICS
                ):
                    raise ValueError("invalid benign rate metric")
            by_capture[capture_id].append(record)
    if seen != expected or len(by_capture) != 320 or any(
        len(values) != 30 for values in by_capture.values()
    ):
        raise ValueError("MDR PARROT model/capture coverage mismatch")
    frozen_captures = {
        str(item["capture_id"]): item
        for item in protocol["parrot_captures"]
    }
    if set(by_capture) != set(frozen_captures):
        raise ValueError("MDR PARROT capture identity drift")

    capture_blocks = []
    series: Dict[str, list[float]] = defaultdict(list)
    by_application: Dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for capture_id, values in sorted(by_capture.items()):
        application = str(frozen_captures[capture_id]["application"])
        if {str(item["application"]) for item in values} != {application}:
            raise ValueError("PARROT application identity drift")
        block: Dict[str, Any] = {
            "capture_id": capture_id,
            "application": application,
            "model_pair_count": 30,
            "flow_row_count": int(values[0]["flow_row_count"]),
            "mdr_caeos_v1": {},
            "opendetect": {},
        }
        if len({int(item["flow_row_count"]) for item in values}) != 1:
            raise ValueError("PARROT flow row count differs by model")
        for method in ("mdr_caeos_v1", "opendetect"):
            for metric in RATE_METRICS:
                mean = float(
                    np.mean([item[method][metric] for item in values])
                )
                block[method][metric] = mean
                series[f"{method}_{metric}"].append(mean)
        difference = (
            block["mdr_caeos_v1"]["false_alert_rate"]
            - block["opendetect"]["false_alert_rate"]
        )
        block["mdr_minus_opendetect_false_alert_rate"] = difference
        series["mdr_minus_opendetect_false_alert_rate"].append(difference)
        capture_blocks.append(block)
        by_application[application].append(block)
    if len(by_application) != 80 or any(
        len(values) != 4 for values in by_application.values()
    ):
        raise ValueError("MDR PARROT application coverage mismatch")

    repetitions = int(
        protocol["aggregation"]["capture_block_bootstrap_repetitions"]
    )
    seed = int(protocol["aggregation"]["capture_block_bootstrap_seed"])
    inference = {
        name: bootstrap_mean(
            values,
            seed=seed + index,
            repetitions=repetitions,
        )
        for index, (name, values) in enumerate(sorted(series.items()))
    }
    source_difference = bootstrap_independent_difference(
        series["mdr_caeos_v1_false_alert_rate"],
        source_benign,
        seed=seed + 100,
        repetitions=repetitions,
    )
    application_records = []
    for application, values in sorted(by_application.items()):
        application_records.append(
            {
                "application": application,
                "capture_count": 4,
                "mdr_false_alert_rate": float(
                    np.mean(
                        [
                            item["mdr_caeos_v1"]["false_alert_rate"]
                            for item in values
                        ]
                    )
                ),
                "mdr_operational_intervention_rate": float(
                    np.mean(
                        [
                            item["mdr_caeos_v1"][
                                "operational_intervention_rate"
                            ]
                            for item in values
                        ]
                    )
                ),
            }
        )
    fraction_below_020 = float(
        np.mean(
            [
                item["mdr_false_alert_rate"] <= 0.20
                for item in application_records
            ]
        )
    )
    gate = protocol["confirmation_gate"]
    checks = {
        "all_320_captures_and_80_applications_covered": True,
        "applications_with_false_alert_rate_at_most_0_20_minimum_fraction": (
            fraction_below_020
            >= float(
                gate[
                    "applications_with_false_alert_rate_at_most_0_20_"
                    "minimum_fraction"
                ]
            )
        ),
        "candidate_false_alert_minus_source_benign_95ci_upper_maximum": (
            source_difference["bootstrap_95ci"][1]
            <= float(
                gate[
                    "candidate_false_alert_minus_source_benign_95ci_"
                    "upper_maximum"
                ]
            )
        ),
        "candidate_false_alert_rate_bootstrap_95ci_upper_maximum": (
            inference["mdr_caeos_v1_false_alert_rate"][
                "bootstrap_95ci"
            ][1]
            <= float(
                gate[
                    "candidate_false_alert_rate_bootstrap_95ci_"
                    "upper_maximum"
                ]
            )
        ),
        "candidate_known_attack_assignment_95ci_upper_maximum": (
            inference["mdr_caeos_v1_known_attack_assignment_rate"][
                "bootstrap_95ci"
            ][1]
            <= float(
                gate[
                    "candidate_known_attack_assignment_95ci_upper_"
                    "maximum"
                ]
            )
        ),
        "candidate_minus_opendetect_false_alert_95ci_upper_maximum": (
            inference["mdr_minus_opendetect_false_alert_rate"][
                "bootstrap_95ci"
            ][1]
            <= float(
                gate[
                    "candidate_minus_opendetect_false_alert_95ci_"
                    "upper_maximum"
                ]
            )
        ),
        "failure_count_zero": True,
        "forbidden_fit_selection_or_threshold_use_observed": (
            gate[
                "forbidden_fit_selection_or_threshold_use_observed"
            ]
            is False
        ),
    }
    return {
        "model_pair_count": 30,
        "capture_count": 320,
        "application_count": 80,
        "failure_count": 0,
        "capture_blocks": capture_blocks,
        "application_records": application_records,
        "applications_with_false_alert_rate_at_most_0_20_fraction": (
            fraction_below_020
        ),
        "capture_block_inference": inference,
        "candidate_minus_source_benign_inference": source_difference,
        "source_benign_model_reference_values": source_benign,
        "confirmation_checks": checks,
        "safety_gate_passes": all(checks.values()),
    }


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    records = []
    registry = []
    for source in protocol["source_model_pairs"]:
        path = (
            run_root
            / "evaluations"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
            / "model_pair_metrics.json"
        )
        if not path.is_file():
            raise FileNotFoundError(f"missing MDR PARROT metrics: {path}")
        records.append(load(path))
        registry.append(
            {
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "metrics_file_sha256": file_hash(path),
            }
        )
    aggregate_value = aggregate(records, protocol)
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_parrot_safety_summary_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate_value,
        "model_pair_metrics_file_registry": registry,
        "claim_boundary": {
            "successful_gate_allows": (
                "cross_domain_benign_false_alert_safety_noninferiority"
            ),
            "does_not_support_malicious_accuracy_or_parrot_sota": True,
            "does_not_replace_malicious_external_confirmation": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(load(args.protocol), args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
