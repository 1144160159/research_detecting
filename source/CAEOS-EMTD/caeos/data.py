from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset


class MultiViewFlowDataset(Dataset):
    def __init__(
        self,
        views: Sequence[np.ndarray],
        quality: np.ndarray,
        labels: np.ndarray,
        is_unknown: np.ndarray,
    ):
        self.views = [torch.as_tensor(view, dtype=torch.float32) for view in views]
        self.quality = torch.as_tensor(quality, dtype=torch.float32)
        self.labels = torch.as_tensor(labels, dtype=torch.long)
        self.is_unknown = torch.as_tensor(is_unknown, dtype=torch.bool)

    def __len__(self) -> int:
        return int(self.labels.shape[0])

    def __getitem__(self, index: int) -> Dict[str, object]:
        return {
            "views": tuple(view[index] for view in self.views),
            "quality": self.quality[index],
            "label": self.labels[index],
            "is_unknown": self.is_unknown[index],
        }


class TabularViewPreprocessor:
    def __init__(self):
        self.median: np.ndarray = None
        self.mean: np.ndarray = None
        self.std: np.ndarray = None

    def fit(self, values: np.ndarray) -> None:
        values = values.astype(np.float64, copy=True)
        values[~np.isfinite(values)] = np.nan
        median = np.nanmedian(values, axis=0)
        median[~np.isfinite(median)] = 0.0
        filled = np.where(np.isnan(values), median, values)
        mean = filled.mean(axis=0)
        std = filled.std(axis=0)
        std[std < 1e-8] = 1.0
        self.median = median.astype(np.float32)
        self.mean = mean.astype(np.float32)
        self.std = std.astype(np.float32)

    def transform(self, values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.median is None:
            raise RuntimeError("preprocessor has not been fitted")
        values = values.astype(np.float32, copy=True)
        finite = np.isfinite(values)
        quality = finite.mean(axis=1).astype(np.float32)
        values[~finite] = np.nan
        values = np.where(np.isnan(values), self.median, values)
        values = (values - self.mean) / self.std
        values = np.clip(values, -12.0, 12.0)
        return values.astype(np.float32), quality

    def state_dict(self) -> Dict[str, object]:
        return {
            "median": self.median.tolist(),
            "mean": self.mean.tolist(),
            "std": self.std.tolist(),
        }


@dataclass
class DataBundle:
    train: MultiViewFlowDataset
    validation: MultiViewFlowDataset
    test: MultiViewFlowDataset
    input_dims: List[int]
    modality_names: List[str]
    class_names: List[str]
    benign_index: int
    preprocessing: Dict[str, object]
    sample_counts: Dict[str, int]
    split_metadata: Dict[str, object] = field(default_factory=dict)


def load_stratified_reservoir(
    csv_path: str,
    label_column: str,
    feature_columns: Sequence[str],
    max_per_class: int,
    chunksize: int,
    seed: int,
    additional_columns: Sequence[str] = (),
) -> pd.DataFrame:
    """Scan a CSV while retaining a bounded random reservoir per class."""
    required = list(
        dict.fromkeys(
            list(feature_columns) + list(additional_columns) + [label_column]
        )
    )
    reservoirs: Dict[str, pd.DataFrame] = {}
    class_rngs: Dict[str, np.random.RandomState] = {}

    def class_rng(label: str) -> np.random.RandomState:
        if label not in class_rngs:
            digest = hashlib.blake2b(
                (str(seed) + "\0" + label).encode("utf-8"), digest_size=4
            ).digest()
            class_seed = int.from_bytes(digest, byteorder="little", signed=False)
            class_rngs[label] = np.random.RandomState(class_seed)
        return class_rngs[label]

    for chunk in pd.read_csv(
        csv_path, usecols=required, chunksize=chunksize, low_memory=False
    ):
        chunk[label_column] = chunk[label_column].astype(str).str.strip()
        for label, group in chunk.groupby(label_column, sort=False):
            candidate = group.copy()
            candidate["__priority"] = class_rng(str(label)).uniform(
                size=len(candidate)
            )
            if label in reservoirs:
                candidate = pd.concat([reservoirs[label], candidate], ignore_index=True)
            if len(candidate) > max_per_class:
                candidate = candidate.nsmallest(max_per_class, "__priority")
            reservoirs[label] = candidate
    if not reservoirs:
        raise ValueError("no samples were loaded from %s" % csv_path)
    frame = pd.concat(reservoirs.values(), ignore_index=True)
    return frame.drop(columns="__priority")


def _numeric_matrix(frame: pd.DataFrame, columns: Sequence[str]) -> np.ndarray:
    numeric = frame.loc[:, list(columns)].apply(pd.to_numeric, errors="coerce")
    return numeric.to_numpy(dtype=np.float32)


def row_fingerprint(frame: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    """Return a deterministic fingerprint over canonicalized feature values."""
    canonical = frame.loc[:, list(columns)].astype(str).apply(
        lambda values: values.str.strip().str.lower()
    )
    return pd.util.hash_pandas_object(canonical, index=False).astype("uint64")


def split_frame_fingerprint(
    frame: pd.DataFrame, columns: Sequence[str]
) -> str:
    """Hash ordered raw split contents for strict cross-run pairing."""
    ordered_columns = list(dict.fromkeys(columns))
    canonical = frame.loc[:, ordered_columns].copy()
    canonical = canonical.where(~canonical.isna(), "<MISSING>").astype(str)
    row_hashes = pd.util.hash_pandas_object(canonical, index=False).to_numpy(
        dtype=np.uint64
    )
    digest = hashlib.sha256()
    digest.update(len(frame).to_bytes(8, byteorder="little", signed=False))
    for column in ordered_columns:
        encoded = str(column).encode("utf-8")
        digest.update(len(encoded).to_bytes(4, byteorder="little", signed=False))
        digest.update(encoded)
    digest.update(row_hashes.astype("<u8", copy=False).tobytes(order="C"))
    return digest.hexdigest()


def split_fingerprint_metadata(
    train_frame: pd.DataFrame,
    validation_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    columns: Sequence[str],
) -> Dict[str, object]:
    fingerprints = {
        "train": split_frame_fingerprint(train_frame, columns),
        "validation": split_frame_fingerprint(validation_frame, columns),
        "test": split_frame_fingerprint(test_frame, columns),
    }
    combined = hashlib.sha256()
    for name in ("train", "validation", "test"):
        combined.update(name.encode("ascii"))
        combined.update(fingerprints[name].encode("ascii"))
    return {
        "schema_version": "1.0",
        "algorithm": "sha256_over_ordered_canonical_pandas_row_hashes",
        "columns": list(dict.fromkeys(columns)),
        **fingerprints,
        "combined": combined.hexdigest(),
    }


def drop_cross_label_fingerprint_groups(
    frame: pd.DataFrame,
    label_column: str,
    feature_columns: Sequence[str],
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Remove feature-identical groups carrying contradictory labels."""
    fingerprint = row_fingerprint(frame, feature_columns)
    work = pd.DataFrame(
        {
            "fingerprint": fingerprint.to_numpy(),
            "label": frame[label_column].astype(str).str.strip().to_numpy(),
        }
    )
    label_counts = work.groupby("fingerprint", sort=False)["label"].nunique()
    conflicting = set(label_counts[label_counts > 1].index.tolist())
    removed_mask = fingerprint.isin(conflicting).to_numpy()
    removed_labels = frame.loc[removed_mask, label_column].astype(str).str.strip()
    report = {
        "enabled": True,
        "conflicting_fingerprint_groups": int(len(conflicting)),
        "removed_rows": int(removed_mask.sum()),
        "removed_rows_per_class": {
            str(label): int(count)
            for label, count in removed_labels.value_counts().sort_index().items()
        },
    }
    return frame.loc[~removed_mask].reset_index(drop=True), report


def stratified_fingerprint_group_split(
    frame: pd.DataFrame,
    label_column: str,
    feature_columns: Sequence[str],
    seed: int,
    fractions: Tuple[float, float, float] = (0.70, 0.15, 0.15),
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    """Split label-pure fingerprint groups without crossing split boundaries."""
    if not np.isclose(sum(fractions), 1.0):
        raise ValueError("split fractions must sum to one")
    work = frame.copy()
    work["__fingerprint"] = row_fingerprint(work, feature_columns).to_numpy()
    label_counts = work.groupby("__fingerprint", sort=False)[label_column].nunique()
    conflicting = set(label_counts[label_counts > 1].index.tolist())
    if conflicting:
        raise ValueError(
            "%d feature fingerprints contain multiple labels" % len(conflicting)
        )

    rng = np.random.RandomState(seed)
    split_parts: List[List[pd.DataFrame]] = [[], [], []]
    per_class_counts: Dict[str, Dict[str, int]] = {}
    for label, label_frame in work.groupby(label_column, sort=True):
        groups = [group for _, group in label_frame.groupby("__fingerprint", sort=False)]
        rng.shuffle(groups)
        target = np.asarray(fractions, dtype=np.float64) * len(label_frame)
        counts = np.zeros(3, dtype=np.int64)
        for group in groups:
            remaining_ratio = (target - counts) / np.maximum(target, 1.0)
            split_index = int(np.argmax(remaining_ratio))
            split_parts[split_index].append(group)
            counts[split_index] += len(group)
        per_class_counts[str(label)] = {
            "train": int(counts[0]),
            "validation": int(counts[1]),
            "test": int(counts[2]),
        }

    def combine(parts: List[pd.DataFrame]) -> pd.DataFrame:
        if not parts:
            return work.iloc[0:0].drop(columns="__fingerprint")
        return pd.concat(parts, ignore_index=True).drop(columns="__fingerprint")

    train_frame, validation_frame, test_frame = [
        combine(parts) for parts in split_parts
    ]
    fingerprint_sets = [
        set(row_fingerprint(part, feature_columns).tolist())
        for part in (train_frame, validation_frame, test_frame)
    ]
    metadata = {
        "strategy": "fingerprint_grouped",
        "fractions": list(fractions),
        "per_class_counts": per_class_counts,
        "fingerprint_overlap": {
            "train_validation": len(fingerprint_sets[0] & fingerprint_sets[1]),
            "train_test": len(fingerprint_sets[0] & fingerprint_sets[2]),
            "validation_test": len(fingerprint_sets[1] & fingerprint_sets[2]),
        },
    }
    return train_frame, validation_frame, test_frame, metadata


def stratified_column_group_split(
    frame: pd.DataFrame,
    label_column: str,
    group_column: str,
    seed: int,
    fractions: Tuple[float, float, float] = (0.70, 0.15, 0.15),
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    """Split label-pure capture/session groups without group leakage."""
    if group_column not in frame:
        raise ValueError("group column %s is absent" % group_column)
    if not np.isclose(sum(fractions), 1.0):
        raise ValueError("split fractions must sum to one")
    group_labels = frame.groupby(group_column, sort=False)[label_column].nunique()
    conflicting = set(group_labels[group_labels > 1].index.tolist())
    if conflicting:
        raise ValueError("%d groups contain multiple labels" % len(conflicting))

    rng = np.random.RandomState(seed)
    split_parts: List[List[pd.DataFrame]] = [[], [], []]
    per_class_groups: Dict[str, Dict[str, int]] = {}
    for label, label_frame in frame.groupby(label_column, sort=True):
        groups = [group for _, group in label_frame.groupby(group_column, sort=False)]
        if len(groups) < 3:
            raise ValueError("class %s has fewer than three groups" % label)
        rng.shuffle(groups)
        target = np.asarray(fractions, dtype=np.float64) * len(label_frame)
        counts = np.zeros(3, dtype=np.int64)
        assigned_groups = np.zeros(3, dtype=np.int64)
        for group in groups:
            remaining_ratio = (target - counts) / np.maximum(target, 1.0)
            split_index = int(np.argmax(remaining_ratio))
            split_parts[split_index].append(group)
            counts[split_index] += len(group)
            assigned_groups[split_index] += 1
        if np.any(assigned_groups == 0):
            raise ValueError("class %s did not cover every split" % label)
        per_class_groups[str(label)] = {
            "train": int(assigned_groups[0]),
            "validation": int(assigned_groups[1]),
            "test": int(assigned_groups[2]),
        }

    splits = [pd.concat(parts, ignore_index=True) for parts in split_parts]
    group_sets = [set(split[group_column].astype(str)) for split in splits]
    metadata = {
        "strategy": "capture_grouped",
        "group_column": group_column,
        "fractions": list(fractions),
        "per_class_groups": per_class_groups,
        "group_overlap": {
            "train_validation": len(group_sets[0] & group_sets[1]),
            "train_test": len(group_sets[0] & group_sets[2]),
            "validation_test": len(group_sets[1] & group_sets[2]),
        },
    }
    return splits[0], splits[1], splits[2], metadata


def temporal_column_group_split(
    frame: pd.DataFrame,
    label_column: str,
    group_column: str,
    time_column: str,
    fractions: Tuple[float, float, float] = (0.70, 0.15, 0.15),
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    """Assign each class's capture groups chronologically to train/validation/test."""
    if group_column not in frame or time_column not in frame:
        raise ValueError("temporal split requires group and time columns")
    if not np.isclose(sum(fractions), 1.0):
        raise ValueError("split fractions must sum to one")
    if frame[time_column].isna().any():
        raise ValueError("temporal split contains missing capture timestamps")

    work = frame.copy()
    work["__capture_time"] = pd.to_datetime(work[time_column], errors="raise", utc=True)
    group_labels = work.groupby(group_column, sort=False)[label_column].nunique()
    if (group_labels > 1).any():
        raise ValueError("temporal split groups must be label-pure")
    group_times = work.groupby(group_column, sort=False)["__capture_time"].nunique()
    if (group_times != 1).any():
        raise ValueError("each temporal split group must have one capture timestamp")

    split_parts: List[List[pd.DataFrame]] = [[], [], []]
    per_class_groups: Dict[str, Dict[str, int]] = {}
    per_class_ranges: Dict[str, Dict[str, Dict[str, str]]] = {}
    for label, label_frame in work.groupby(label_column, sort=True):
        groups = [
            group
            for _, group in sorted(
                label_frame.groupby(group_column, sort=False),
                key=lambda item: (
                    item[1]["__capture_time"].iloc[0],
                    str(item[0]),
                ),
            )
        ]
        if len(groups) < 3:
            raise ValueError("class %s has fewer than three temporal groups" % label)
        train_count = max(1, int(np.floor(fractions[0] * len(groups))))
        validation_count = max(1, int(np.floor(fractions[1] * len(groups))))
        if train_count + validation_count >= len(groups):
            train_count = len(groups) - 2
            validation_count = 1
        boundaries = (train_count, train_count + validation_count)
        assigned = (groups[: boundaries[0]], groups[boundaries[0] : boundaries[1]], groups[boundaries[1] :])
        ranges: Dict[str, Dict[str, str]] = {}
        counts: Dict[str, int] = {}
        for split_index, (split_name, split_groups) in enumerate(
            zip(("train", "validation", "test"), assigned)
        ):
            split_parts[split_index].extend(split_groups)
            counts[split_name] = len(split_groups)
            timestamps = [group["__capture_time"].iloc[0] for group in split_groups]
            ranges[split_name] = {
                "minimum": min(timestamps).isoformat(),
                "maximum": max(timestamps).isoformat(),
            }
        if not (
            pd.Timestamp(ranges["train"]["maximum"])
            <= pd.Timestamp(ranges["validation"]["minimum"])
            <= pd.Timestamp(ranges["test"]["minimum"])
        ):
            raise AssertionError("temporal split ordering failed for class %s" % label)
        per_class_groups[str(label)] = counts
        per_class_ranges[str(label)] = ranges

    splits = [
        pd.concat(parts, ignore_index=True).drop(columns="__capture_time")
        for parts in split_parts
    ]
    group_sets = [set(split[group_column].astype(str)) for split in splits]
    metadata = {
        "strategy": "temporal_capture_grouped",
        "group_column": group_column,
        "time_column": time_column,
        "fractions": list(fractions),
        "ordering": "per_class_ascending_capture_time",
        "per_class_groups": per_class_groups,
        "per_class_time_ranges": per_class_ranges,
        "group_overlap": {
            "train_validation": len(group_sets[0] & group_sets[1]),
            "train_test": len(group_sets[0] & group_sets[2]),
            "validation_test": len(group_sets[1] & group_sets[2]),
        },
    }
    return splits[0], splits[1], splits[2], metadata


def _split_known_frame(
    frame: pd.DataFrame,
    label_column: str,
    feature_columns: Sequence[str],
    seed: int,
    split_strategy: str,
    group_column: str = "",
    time_column: str = "",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    if split_strategy == "fingerprint_grouped":
        return stratified_fingerprint_group_split(
            frame, label_column, feature_columns, seed
        )
    if split_strategy == "capture_grouped":
        if not group_column:
            raise ValueError("capture_grouped requires config group_column")
        return stratified_column_group_split(
            frame, label_column, group_column, seed
        )
    if split_strategy == "temporal_capture_grouped":
        if not group_column or not time_column:
            raise ValueError(
                "temporal_capture_grouped requires config group_column and time_column"
            )
        return temporal_column_group_split(
            frame, label_column, group_column, time_column
        )
    if split_strategy != "random":
        raise ValueError("unsupported split strategy: %s" % split_strategy)
    train_frame, holdout_frame = train_test_split(
        frame,
        test_size=0.30,
        random_state=seed,
        stratify=frame[label_column],
    )
    validation_frame, test_frame = train_test_split(
        holdout_frame,
        test_size=0.50,
        random_state=seed,
        stratify=holdout_frame[label_column],
    )
    return train_frame, validation_frame, test_frame, {
        "strategy": "random",
        "fractions": [0.70, 0.15, 0.15],
    }


def prepare_tabular_open_set(
    csv_path: str,
    config: Mapping[str, object],
    unknown_classes: Sequence[str],
    benign_class: str,
    max_per_class: int = 5000,
    chunksize: int = 100000,
    seed: int = 7,
    split_strategy: str = "random",
) -> DataBundle:
    label_column = str(config["label_column"])
    modalities = config["modalities"]
    modality_names = list(modalities.keys())
    feature_columns = [column for name in modality_names for column in modalities[name]]
    group_column = str(config.get("group_column", ""))
    time_column = str(config.get("time_column", ""))
    frame = load_stratified_reservoir(
        csv_path,
        label_column,
        feature_columns,
        max_per_class,
        chunksize,
        seed,
        additional_columns=[
            column for column in (group_column, time_column) if column
        ],
    )

    available_labels = set(frame[label_column].astype(str))
    missing_unknown = set(unknown_classes) - available_labels
    if missing_unknown:
        raise ValueError("unknown classes not found: %s" % sorted(missing_unknown))
    if benign_class not in available_labels:
        raise ValueError("benign class %s is absent" % benign_class)

    unknown_mask = frame[label_column].isin(list(unknown_classes))
    known_frame = frame.loc[~unknown_mask].reset_index(drop=True)
    unknown_frame = frame.loc[unknown_mask].reset_index(drop=True)

    cross_label_filter = {
        "enabled": False,
        "removed_rows": 0,
        "scope": "known_only",
        "unknown_labels_used": False,
    }
    if bool(config.get("drop_cross_label_fingerprints", False)):
        known_frame, cross_label_filter = drop_cross_label_fingerprint_groups(
            known_frame, label_column, feature_columns
        )
        cross_label_filter.update(
            {
                "scope": "known_only",
                "unknown_labels_used": False,
            }
        )

    remaining_classes = sorted(set(known_frame[label_column]) - {benign_class})
    class_names = [benign_class] + remaining_classes
    class_to_index = {name: index for index, name in enumerate(class_names)}

    train_frame, validation_frame, known_test_frame, split_metadata = (
        _split_known_frame(
            known_frame,
            label_column,
            feature_columns,
            seed,
            split_strategy,
            group_column,
            time_column,
        )
    )
    split_metadata["cross_label_fingerprint_filter"] = cross_label_filter
    test_frame = pd.concat([known_test_frame, unknown_frame], ignore_index=True)
    fingerprint_columns = [
        *feature_columns,
        *([group_column] if group_column else []),
        *([time_column] if time_column else []),
        label_column,
    ]
    split_metadata["split_fingerprint"] = split_fingerprint_metadata(
        train_frame,
        validation_frame,
        test_frame,
        fingerprint_columns,
    )
    split_metadata["reservoir_sampling"] = {
        "strategy": "per_label_random_priority",
        "seed": int(seed),
        "max_per_class": int(max_per_class),
    }

    preprocessors: Dict[str, TabularViewPreprocessor] = {}
    for name in modality_names:
        processor = TabularViewPreprocessor()
        processor.fit(_numeric_matrix(train_frame, modalities[name]))
        preprocessors[name] = processor

    def make_dataset(split_frame: pd.DataFrame) -> MultiViewFlowDataset:
        view_arrays = []
        quality_columns = []
        for name in modality_names:
            values, quality = preprocessors[name].transform(
                _numeric_matrix(split_frame, modalities[name])
            )
            view_arrays.append(values)
            quality_columns.append(quality)
        raw_labels = split_frame[label_column].astype(str)
        is_unknown = raw_labels.isin(list(unknown_classes)).to_numpy(dtype=bool)
        labels = raw_labels.map(class_to_index).fillna(-1).to_numpy(dtype=np.int64)
        quality = np.stack(quality_columns, axis=1)
        return MultiViewFlowDataset(view_arrays, quality, labels, is_unknown)

    retained_frame = pd.concat([known_frame, unknown_frame], ignore_index=True)
    sample_counts = {
        str(label): int(count)
        for label, count in retained_frame[label_column].value_counts().to_dict().items()
    }
    return DataBundle(
        train=make_dataset(train_frame),
        validation=make_dataset(validation_frame),
        test=make_dataset(test_frame),
        input_dims=[len(modalities[name]) for name in modality_names],
        modality_names=modality_names,
        class_names=class_names,
        benign_index=class_to_index[benign_class],
        preprocessing={
            "modalities": modalities,
            "processors": {
                name: preprocessors[name].state_dict() for name in modality_names
            },
        },
        sample_counts=sample_counts,
        split_metadata=split_metadata,
    )


def prepare_tabular_closed_set(
    csv_path: str,
    config: Mapping[str, object],
    benign_class: str,
    max_per_class: int = 5000,
    chunksize: int = 100000,
    seed: int = 7,
    split_strategy: str = "random",
) -> DataBundle:
    return prepare_tabular_open_set(
        csv_path=csv_path,
        config=config,
        unknown_classes=[],
        benign_class=benign_class,
        max_per_class=max_per_class,
        chunksize=chunksize,
        seed=seed,
        split_strategy=split_strategy,
    )


def make_synthetic_open_set(
    num_classes: int = 4,
    samples_per_class: int = 240,
    unknown_samples: int = 240,
    seed: int = 7,
) -> DataBundle:
    rng = np.random.RandomState(seed)
    input_dims = [12, 9, 7]
    modality_names = ["flow", "protocol", "relation"]
    centers = [rng.normal(0.0, 2.5, size=(num_classes, dim)) for dim in input_dims]

    known_views = [[] for _ in input_dims]
    known_labels = []
    for class_index in range(num_classes):
        for modality_index, dim in enumerate(input_dims):
            known_views[modality_index].append(
                centers[modality_index][class_index]
                + rng.normal(0.0, 0.65, size=(samples_per_class, dim))
            )
        known_labels.extend([class_index] * samples_per_class)
    known_views = [np.concatenate(parts, axis=0).astype(np.float32) for parts in known_views]
    known_labels = np.asarray(known_labels, dtype=np.int64)

    indices = np.arange(len(known_labels))
    train_index, holdout_index = train_test_split(
        indices, test_size=0.30, random_state=seed, stratify=known_labels
    )
    validation_index, known_test_index = train_test_split(
        holdout_index,
        test_size=0.50,
        random_state=seed,
        stratify=known_labels[holdout_index],
    )

    unknown_views = []
    for modality_index, dim in enumerate(input_dims):
        source_class = modality_index % num_classes
        unknown_views.append(
            (
                centers[modality_index][source_class]
                + 1.5
                + rng.normal(0.0, 0.85, size=(unknown_samples, dim))
            ).astype(np.float32)
        )

    def known_dataset(index: np.ndarray) -> MultiViewFlowDataset:
        return MultiViewFlowDataset(
            [view[index] for view in known_views],
            np.ones((len(index), len(input_dims)), dtype=np.float32),
            known_labels[index],
            np.zeros(len(index), dtype=bool),
        )

    test_views = [
        np.concatenate([view[known_test_index], unknown], axis=0)
        for view, unknown in zip(known_views, unknown_views)
    ]
    test_labels = np.concatenate(
        [known_labels[known_test_index], np.full(unknown_samples, -1, dtype=np.int64)]
    )
    test_unknown = np.concatenate(
        [np.zeros(len(known_test_index), dtype=bool), np.ones(unknown_samples, dtype=bool)]
    )
    test_quality = np.ones((len(test_labels), len(input_dims)), dtype=np.float32)

    return DataBundle(
        train=known_dataset(train_index),
        validation=known_dataset(validation_index),
        test=MultiViewFlowDataset(test_views, test_quality, test_labels, test_unknown),
        input_dims=input_dims,
        modality_names=modality_names,
        class_names=["Benign"] + ["Attack_%d" % i for i in range(1, num_classes)],
        benign_index=0,
        preprocessing={},
        sample_counts={
            "known": int(len(known_labels)),
            "unknown": int(unknown_samples),
        },
    )


def make_synthetic_multiclass(
    num_classes: int = 4,
    samples_per_class: int = 240,
    seed: int = 7,
) -> DataBundle:
    bundle = make_synthetic_open_set(
        num_classes=num_classes,
        samples_per_class=samples_per_class,
        unknown_samples=samples_per_class,
        seed=seed,
    )
    known = ~bundle.test.is_unknown
    test = MultiViewFlowDataset(
        [view[known].numpy() for view in bundle.test.views],
        bundle.test.quality[known].numpy(),
        bundle.test.labels[known].numpy(),
        np.zeros(int(known.sum()), dtype=bool),
    )
    return DataBundle(
        train=bundle.train,
        validation=bundle.validation,
        test=test,
        input_dims=bundle.input_dims,
        modality_names=bundle.modality_names,
        class_names=bundle.class_names,
        benign_index=bundle.benign_index,
        preprocessing=bundle.preprocessing,
        sample_counts={"known": num_classes * samples_per_class},
    )
