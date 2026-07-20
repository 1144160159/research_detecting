from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class FOSSNode:
    depth: int
    majority_class: int
    centroid: np.ndarray
    radius: float
    split_dimension: int = -1
    split_value: float = 0.0
    left: Optional["FOSSNode"] = None
    right: Optional["FOSSNode"] = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None or self.right is None


class FOSSTree:
    """One weighted-entropy Monte Carlo isolation tree from FOSS.

    Tree construction follows Algorithms 1-2 of Zhao et al. (TON 2024).
    Labels do not participate in split selection and are only retained for the
    majority class assigned to a reached leaf.
    """

    def __init__(
        self,
        max_depth: int,
        min_samples: int = 1,
        candidate_dimensions: int = 5,
        seed: int = 7,
    ) -> None:
        self.max_depth = int(max_depth)
        self.min_samples = int(min_samples)
        self.candidate_dimensions = int(candidate_dimensions)
        self.rng = np.random.RandomState(seed)
        self.root: Optional[FOSSNode] = None
        self.path_threshold = 0

    @staticmethod
    def _majority(labels: np.ndarray) -> int:
        values, counts = np.unique(labels.astype(np.int64), return_counts=True)
        return int(values[np.argmax(counts)])

    @staticmethod
    def _weighted_entropy(values: np.ndarray) -> float:
        values = np.asarray(values, dtype=np.float64)
        low = float(values.min())
        high = float(values.max())
        if not np.isfinite(low) or not np.isfinite(high) or high <= low:
            return float("inf")
        normalized = (values - low) / (high - low)
        unique, counts = np.unique(normalized, return_counts=True)
        probability = counts.astype(np.float64) / len(normalized)
        expectation = float(np.sum(unique * probability))
        information = -probability * np.log2(np.maximum(probability, 1e-12))
        distance = np.abs(unique - expectation)
        return float(np.sum(information / np.maximum(distance, 1e-12)))

    def _choose_dimension(self, values: np.ndarray) -> int:
        dimensions = values.shape[1]
        count = min(max(1, self.candidate_dimensions), dimensions)
        candidates = self.rng.choice(dimensions, size=count, replace=False)
        entropy = np.asarray(
            [self._weighted_entropy(values[:, index]) for index in candidates]
        )
        if np.isfinite(entropy).any():
            return int(candidates[int(np.argmin(entropy))])
        variable = np.flatnonzero(np.ptp(values, axis=0) > 0)
        return int(self.rng.choice(variable)) if len(variable) else -1

    def _leaf(self, values: np.ndarray, labels: np.ndarray, depth: int) -> FOSSNode:
        centroid = values.mean(axis=0)
        distance = np.linalg.norm(values - centroid, axis=1)
        radius = float(distance.max()) if len(distance) else 0.0
        return FOSSNode(
            depth=depth,
            majority_class=self._majority(labels),
            centroid=centroid.astype(np.float64, copy=False),
            radius=radius,
        )

    def _build(self, values: np.ndarray, labels: np.ndarray, depth: int) -> FOSSNode:
        if (
            depth >= self.max_depth
            or len(values) <= self.min_samples
            or np.all(np.ptp(values, axis=0) == 0)
        ):
            return self._leaf(values, labels, depth)

        dimension = self._choose_dimension(values)
        if dimension < 0:
            return self._leaf(values, labels, depth)
        low = float(values[:, dimension].min())
        high = float(values[:, dimension].max())
        split = float(self.rng.uniform(low, high))
        left_mask = values[:, dimension] < split
        if not left_mask.any() or left_mask.all():
            split = float(np.median(values[:, dimension]))
            left_mask = values[:, dimension] < split
        if not left_mask.any() or left_mask.all():
            return self._leaf(values, labels, depth)

        node = self._leaf(values, labels, depth)
        node.split_dimension = dimension
        node.split_value = split
        node.left = self._build(values[left_mask], labels[left_mask], depth + 1)
        node.right = self._build(values[~left_mask], labels[~left_mask], depth + 1)
        return node

    def _traverse(self, value: np.ndarray) -> FOSSNode:
        if self.root is None:
            raise RuntimeError("FOSS tree has not been fitted")
        node = self.root
        while not node.is_leaf:
            node = (
                node.left
                if value[node.split_dimension] < node.split_value
                else node.right
            )
        return node

    def fit(
        self,
        values: np.ndarray,
        labels: np.ndarray,
        threshold_values: np.ndarray,
    ) -> None:
        self.root = self._build(values, labels, depth=0)
        depths = np.asarray(
            [self._traverse(value).depth for value in threshold_values],
            dtype=np.int64,
        )
        self.path_threshold = self._balanced_depth_threshold(depths)

    @staticmethod
    def _balanced_depth_threshold(depths: np.ndarray) -> int:
        ordered = np.sort(np.asarray(depths, dtype=np.int64))
        candidates = np.unique(ordered)
        best = int(candidates[0])
        best_difference = float("inf")
        for candidate in candidates[:-1]:
            left = ordered[ordered <= candidate]
            right = ordered[ordered > candidate]
            if not len(left) or not len(right):
                continue
            difference = abs(float(left.std()) - float(right.std()))
            if difference < best_difference:
                best = int(candidate)
                best_difference = difference
        return best

    def vote(self, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        labels = np.empty(len(values), dtype=np.int64)
        unknown = np.empty(len(values), dtype=bool)
        for index, value in enumerate(np.asarray(values, dtype=np.float64)):
            leaf = self._traverse(value)
            labels[index] = leaf.majority_class
            short_path = leaf.depth <= self.path_threshold
            outside_cloud = np.linalg.norm(value - leaf.centroid) >= leaf.radius
            unknown[index] = short_path and outside_cloud
        return labels, unknown

    def structural_features(
        self, values: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        depth = np.empty(len(values), dtype=np.float64)
        cloud_deviation = np.empty(len(values), dtype=np.float64)
        unknown = np.empty(len(values), dtype=np.float64)
        for index, value in enumerate(np.asarray(values, dtype=np.float64)):
            leaf = self._traverse(value)
            depth[index] = leaf.depth / max(1, self.max_depth)
            distance = float(np.linalg.norm(value - leaf.centroid))
            ratio = distance / max(leaf.radius, 1e-12)
            cloud_deviation[index] = np.log1p(min(ratio, 1e6))
            unknown[index] = float(
                leaf.depth <= self.path_threshold and distance >= leaf.radius
            )
        return depth, cloud_deviation, unknown


class FOSSForest:
    """FOSS forest adapted to the shared tabular open-set protocol."""

    def __init__(
        self,
        num_trees: int = 30,
        subsample_size: int = 100,
        candidate_dimensions: int = 5,
        min_samples: int = 1,
        seed: int = 7,
    ) -> None:
        if num_trees < 1 or subsample_size < 2:
            raise ValueError("FOSS requires trees and at least two subsamples")
        self.num_trees = int(num_trees)
        self.subsample_size = int(subsample_size)
        self.candidate_dimensions = int(candidate_dimensions)
        self.min_samples = int(min_samples)
        self.seed = int(seed)
        self.num_classes = 0
        self.trees: list[FOSSTree] = []

    def fit(self, values: np.ndarray, labels: np.ndarray) -> None:
        values = np.asarray(values, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)
        if values.ndim != 2 or len(values) != len(labels) or not len(values):
            raise ValueError("FOSS expects a non-empty matrix aligned with labels")
        if not np.isfinite(values).all():
            raise ValueError("FOSS requires finite preprocessed features")
        self.num_classes = int(labels.max()) + 1
        rng = np.random.RandomState(self.seed)
        sample_size = min(self.subsample_size, len(values))
        max_depth = int(np.ceil(np.log2(sample_size)))
        self.trees = []
        for index in range(self.num_trees):
            selected = rng.choice(len(values), size=sample_size, replace=False)
            tree = FOSSTree(
                max_depth=max_depth,
                min_samples=self.min_samples,
                candidate_dimensions=self.candidate_dimensions,
                seed=self.seed + 1009 * (index + 1),
            )
            tree.fit(values[selected], labels[selected], values)
            self.trees.append(tree)

    def predict(self, values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.trees:
            raise RuntimeError("FOSS forest has not been fitted")
        values = np.asarray(values, dtype=np.float64)
        class_votes = np.zeros((len(values), self.num_classes), dtype=np.int64)
        unknown_votes = np.zeros(len(values), dtype=np.float64)
        rows = np.arange(len(values))
        for tree in self.trees:
            labels, unknown = tree.vote(values)
            class_votes[rows, labels] += 1
            unknown_votes += unknown.astype(np.float64)
        prediction = class_votes.argmax(axis=1)
        probability = class_votes / max(1, len(self.trees))
        risk = unknown_votes / len(self.trees)
        return prediction, risk, probability

    def transform(self, values: np.ndarray) -> np.ndarray:
        """Encode known-only random-partition paths and leaf-cloud geometry."""
        if not self.trees:
            raise RuntimeError("FOSS forest has not been fitted")
        values = np.asarray(values, dtype=np.float64)
        features = []
        unknown_votes = np.zeros(len(values), dtype=np.float64)
        for tree in self.trees:
            depth, cloud_deviation, unknown = tree.structural_features(values)
            features.extend((depth, cloud_deviation))
            unknown_votes += unknown
        features.append(unknown_votes / len(self.trees))
        return np.stack(features, axis=1)

    def transform_aggregated(self, values: np.ndarray) -> np.ndarray:
        """Return a compact summary of the forest partition geometry."""
        if not self.trees:
            raise RuntimeError("FOSS forest has not been fitted")
        depth_columns = []
        cloud_columns = []
        unknown_columns = []
        for tree in self.trees:
            depth, cloud_deviation, unknown = tree.structural_features(values)
            depth_columns.append(depth)
            cloud_columns.append(cloud_deviation)
            unknown_columns.append(unknown)
        depth = np.stack(depth_columns, axis=1)
        cloud = np.stack(cloud_columns, axis=1)
        unknown = np.stack(unknown_columns, axis=1)
        return np.stack(
            [
                depth.mean(axis=1),
                depth.std(axis=1),
                depth.min(axis=1),
                depth.max(axis=1),
                cloud.mean(axis=1),
                cloud.std(axis=1),
                cloud.max(axis=1),
                unknown.mean(axis=1),
            ],
            axis=1,
        )
