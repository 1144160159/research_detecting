from __future__ import annotations

import hashlib
from typing import Any

import numpy as np


FAMILY_ORDER = ("Benign", "DDoS", "DoS", "Mirai")


def deterministic_rank(seed: int, label: str, group: str) -> str:
    return hashlib.sha256(
        f"{seed}\0{label}\0{group}".encode("utf-8")
    ).hexdigest()


def select_pseudo_unknown_fine_labels(
    fine_labels: np.ndarray,
    families: np.ndarray,
    outer_train_mask: np.ndarray,
    unknown_family: str,
    seed: int,
) -> dict[str, str]:
    selected: dict[str, str] = {}
    known_attack_families = sorted(
        set(families[outer_train_mask].tolist())
        - {"Benign", unknown_family}
    )
    for family in known_attack_families:
        candidates = sorted(
            set(
                fine_labels[
                    outer_train_mask & (families == family)
                ].tolist()
            )
        )
        if len(candidates) < 2:
            raise ValueError(
                f"{family} needs at least two fine labels for nested "
                "pseudo-unknown selection"
            )
        selected[family] = min(
            candidates,
            key=lambda fine_label: deterministic_rank(
                seed + 104729,
                f"pseudo-unknown:{family}",
                fine_label,
            ),
        )
    if not selected:
        raise ValueError("no known attack family supports pseudo-unknowns")
    return selected


def split_capture_groups(
    fine_labels: np.ndarray,
    families: np.ndarray,
    capture_groups: np.ndarray,
    unknown_family: str,
    seed: int,
) -> dict[str, Any]:
    known = families != unknown_family
    train_groups: set[str] = set()
    validation_groups: set[str] = set()
    test_groups: set[str] = set()
    assignment: dict[str, dict[str, list[str]]] = {}
    for fine_label in sorted(set(fine_labels[known].tolist())):
        groups = sorted(
            set(capture_groups[known & (fine_labels == fine_label)].tolist()),
            key=lambda group: deterministic_rank(seed, fine_label, group),
        )
        if len(groups) < 4:
            raise ValueError(
                f"{fine_label} has {len(groups)} known capture groups"
            )
        fine_family = set(
            families[known & (fine_labels == fine_label)].tolist()
        )
        if len(fine_family) != 1:
            raise ValueError(f"{fine_label} maps to multiple families")
        if fine_family == {"Benign"}:
            validation = groups[:2]
            test = [groups[2]]
            train = groups[3:]
        else:
            validation = [groups[0]]
            test = [groups[1]]
            train = groups[2:]
        assignment[fine_label] = {
            "train": train,
            "validation": validation,
            "test": test,
        }
        train_groups.update(train)
        validation_groups.update(validation)
        test_groups.update(test)
    if train_groups & validation_groups:
        raise ValueError("train/validation capture overlap")
    if train_groups & test_groups:
        raise ValueError("train/test capture overlap")
    if validation_groups & test_groups:
        raise ValueError("validation/test capture overlap")

    unknown_groups = set(capture_groups[families == unknown_family].tolist())
    if unknown_groups & (train_groups | validation_groups | test_groups):
        raise ValueError("unknown capture overlaps a known split")
    train_mask = known & np.isin(capture_groups, sorted(train_groups))
    validation_mask = known & np.isin(
        capture_groups, sorted(validation_groups)
    )
    known_test_mask = known & np.isin(capture_groups, sorted(test_groups))
    unknown_test_mask = families == unknown_family
    return {
        "train_mask": train_mask,
        "validation_mask": validation_mask,
        "known_test_mask": known_test_mask,
        "unknown_test_mask": unknown_test_mask,
        "assignment": assignment,
        "unknown_groups": sorted(unknown_groups),
        "overlap": {
            "train_validation": 0,
            "train_test": 0,
            "validation_test": 0,
            "unknown_known": 0,
        },
    }


def family_mapping(unknown_family: str) -> tuple[list[str], dict[str, int]]:
    labels = [
        family for family in FAMILY_ORDER if family != unknown_family
    ]
    if labels[0] != "Benign":
        raise ValueError("Benign must remain class index zero")
    return labels, {label: index for index, label in enumerate(labels)}


def encode_known_labels(
    families: np.ndarray,
    mapping: dict[str, int],
    unknown_family: str,
) -> np.ndarray:
    encoded = np.full(len(families), -1, dtype=np.int64)
    for family, index in mapping.items():
        encoded[families == family] = index
    if np.any(encoded[families != unknown_family] < 0):
        raise ValueError("known family label was not encoded")
    return encoded
