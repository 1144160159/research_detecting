from __future__ import annotations

import json
import sys
from pathlib import Path

import train_hybrid_open_set as base
from caeos.modality_dropout import ModalityDropoutHybridClassifier


def pop_option(arguments: list[str], option: str, default: str) -> str:
    if option not in arguments:
        return default
    index = arguments.index(option)
    if index + 1 >= len(arguments):
        raise ValueError(f"{option} requires a value")
    value = arguments[index + 1]
    del arguments[index : index + 2]
    return value


def option_value(arguments: list[str], option: str) -> str:
    try:
        return arguments[arguments.index(option) + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"{option} is required") from error


def main() -> None:
    arguments = list(sys.argv)
    copies = int(pop_option(arguments, "--train-modality-dropout-copies", "1"))
    weight = float(pop_option(arguments, "--train-modality-dropout-weight", "1.0"))
    field_severities = tuple(
        float(value)
        for value in pop_option(
            arguments, "--train-field-dropout-severities", ""
        ).split(",")
        if value.strip()
    )
    augmentation_seed = int(
        pop_option(arguments, "--train-dropout-seed", "20260717")
    )
    output_dir = Path(option_value(arguments, "--output-dir"))

    class ConfiguredModalityDropoutClassifier(ModalityDropoutHybridClassifier):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                modality_dropout_copies=copies,
                modality_dropout_weight=weight,
                field_dropout_severities=field_severities,
                augmentation_seed=augmentation_seed,
                **kwargs,
            )

    base.ConflictAwareHybridClassifier = ConfiguredModalityDropoutClassifier
    sys.argv = arguments
    base.main()

    metrics_path = output_dir / "metrics.json"
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    payload["model"] = "mc7_modality_dropout_open_set"
    payload["training_augmentation"] = payload["model_selection"][
        "validation_scores"
    ]["training_augmentation"]
    payload["training_augmentation"]["wrapper"] = Path(__file__).name
    payload["training_augmentation"]["unknown_or_test_labels_used"] = False
    metrics_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
