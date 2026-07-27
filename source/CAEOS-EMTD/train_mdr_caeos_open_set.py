from __future__ import annotations

import json
import sys
from pathlib import Path

import train_hybrid_open_set as base
from caeos.structured_robust import (
    DEFAULT_FAMILY_SEVERITIES,
    StructuredRobustHybridClassifier,
)


MDR_CONFIGURATION = {
    "weight": 0.25,
    "sample_fraction": 0.25,
    "augmentation_seed": 331,
}


class ConfiguredStructuredRobustClassifier(StructuredRobustHybridClassifier):
    """Importable configured class so captured runtimes remain serializable."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            structured_augmentation_weight=float(MDR_CONFIGURATION["weight"]),
            structured_sample_fraction=float(
                MDR_CONFIGURATION["sample_fraction"]
            ),
            structured_family_severities=DEFAULT_FAMILY_SEVERITIES,
            structured_augmentation_seed=int(
                MDR_CONFIGURATION["augmentation_seed"]
            ),
            **kwargs,
        )


def pop_option(arguments: list, option: str, default: str) -> str:
    if option not in arguments:
        return default
    index = arguments.index(option)
    if index + 1 >= len(arguments):
        raise ValueError(f"{option} requires a value")
    value = arguments[index + 1]
    del arguments[index : index + 2]
    return value


def option_value(arguments: list, option: str) -> str:
    try:
        return arguments[arguments.index(option) + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"{option} is required") from error


def main() -> None:
    arguments = list(sys.argv)
    weight = float(pop_option(arguments, "--mdr-augmentation-weight", "0.25"))
    sample_fraction = float(
        pop_option(arguments, "--mdr-sample-fraction", "0.25")
    )
    augmentation_seed = int(
        pop_option(arguments, "--mdr-augmentation-seed", "331")
    )
    health_quantile = float(
        pop_option(arguments, "--mdr-health-quantile", "0.99")
    )
    output_dir = Path(option_value(arguments, "--output-dir"))

    MDR_CONFIGURATION.update(
        {
            "weight": weight,
            "sample_fraction": sample_fraction,
            "augmentation_seed": augmentation_seed,
        }
    )
    base.ConflictAwareHybridClassifier = ConfiguredStructuredRobustClassifier
    sys.argv = arguments
    base.main()

    metrics_path = output_dir / "metrics.json"
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    payload["model"] = "mdr_caeos_structured_robust_pairwise_v1"
    payload["mdr_candidate"] = {
        "augmentation_weight": weight,
        "sample_fraction": sample_fraction,
        "family_severities": DEFAULT_FAMILY_SEVERITIES,
        "augmentation_seed": augmentation_seed,
        "health_quantile": health_quantile,
        "unknown_or_test_labels_used_for_training_or_selection": False,
        "wrapper": Path(__file__).name,
    }
    metrics_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
