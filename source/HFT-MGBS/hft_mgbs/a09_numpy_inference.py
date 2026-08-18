"""Validated NumPy execution of the frozen A09 ExtraTrees ensemble.

This module compiles already-fitted sklearn trees into dense, read-only arrays.
It does not fit, prune, calibrate, or otherwise change a model or threshold.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class _CompiledForest:
    children_left: np.ndarray
    children_right: np.ndarray
    feature: np.ndarray
    threshold: np.ndarray
    positive_probability: np.ndarray
    tree_count: int
    feature_count: int
    max_depth: int

    @classmethod
    def from_sklearn(cls, model, positive_index: int) -> "_CompiledForest":
        estimators = tuple(getattr(model, "estimators_", ()))
        if not estimators:
            raise ValueError("A09 member has no fitted trees")
        classes = np.asarray(getattr(model, "classes_", ()))
        if classes.ndim != 1 or len(classes) != 2:
            raise ValueError("A09 NumPy engine requires a binary classifier")
        if not 0 <= positive_index < len(classes) or classes[positive_index] != 1:
            raise ValueError("A09 positive class index is not bound to label 1")
        feature_count = int(getattr(model, "n_features_in_", 0))
        if feature_count < 1:
            raise ValueError("A09 member has no valid feature count")

        node_counts = [int(estimator.tree_.node_count) for estimator in estimators]
        if any(count < 1 for count in node_counts):
            raise ValueError("A09 member contains an empty tree")
        max_nodes = max(node_counts)
        tree_count = len(estimators)
        left = np.full((tree_count, max_nodes), -1, dtype=np.intp)
        right = np.full((tree_count, max_nodes), -1, dtype=np.intp)
        feature = np.full((tree_count, max_nodes), -2, dtype=np.intp)
        threshold = np.full((tree_count, max_nodes), np.nan, dtype=np.float64)
        probability = np.full((tree_count, max_nodes), np.nan, dtype=np.float64)
        max_depth = 0

        for tree_index, estimator in enumerate(estimators):
            tree = estimator.tree_
            count = node_counts[tree_index]
            tree_left = np.asarray(tree.children_left, dtype=np.intp)
            tree_right = np.asarray(tree.children_right, dtype=np.intp)
            tree_feature = np.asarray(tree.feature, dtype=np.intp)
            tree_threshold = np.asarray(tree.threshold, dtype=np.float64)
            values = np.asarray(tree.value, dtype=np.float64)
            if any(
                array.shape[0] != count
                for array in (tree_left, tree_right, tree_feature, tree_threshold, values)
            ):
                raise ValueError("A09 tree arrays disagree with node_count")
            if values.ndim != 3 or values.shape[1] != 1 or values.shape[2] != 2:
                raise ValueError("A09 tree has an unsupported class-value layout")
            leaf = (tree_left == -1) & (tree_right == -1)
            internal = ~leaf
            if np.any((tree_left == -1) != (tree_right == -1)):
                raise ValueError("A09 tree has a half-defined child pair")
            if np.any(tree_left[internal] <= np.flatnonzero(internal)) or np.any(
                tree_right[internal] <= np.flatnonzero(internal)
            ):
                raise ValueError("A09 tree children do not follow their parent")
            if np.any(tree_left[internal] >= count) or np.any(tree_right[internal] >= count):
                raise ValueError("A09 tree child index is out of range")
            if np.any(tree_feature[internal] < 0) or np.any(
                tree_feature[internal] >= feature_count
            ):
                raise ValueError("A09 tree feature index is out of range")
            if not np.all(np.isfinite(tree_threshold[internal])):
                raise ValueError("A09 tree contains a non-finite split threshold")

            reachable = np.zeros(count, dtype=bool)
            depths = np.zeros(count, dtype=np.intp)
            stack = [0]
            while stack:
                node = stack.pop()
                if reachable[node]:
                    raise ValueError("A09 tree contains a cycle or shared child")
                reachable[node] = True
                if not leaf[node]:
                    for child in (int(tree_left[node]), int(tree_right[node])):
                        depths[child] = depths[node] + 1
                        stack.append(child)
            if not np.all(reachable):
                raise ValueError("A09 tree contains unreachable nodes")

            totals = values[:, 0, :].sum(axis=1)
            if not np.all(np.isfinite(values[leaf])) or np.any(totals[leaf] <= 0.0):
                raise ValueError("A09 tree has invalid leaf class weights")
            leaf_probability = np.full(count, np.nan, dtype=np.float64)
            # sklearn <=1.3 commonly exposes weighted class counts in value;
            # newer fitted trees expose normalized proportions.  Tree.predict
            # returns the latter directly, so a second normalization would move
            # production probabilities by a few ULPs.  The representation is
            # unambiguous at the whole-tree level for a fitted classifier.
            leaf_totals = totals[leaf]
            values_are_probabilities = bool(
                np.all(np.abs(leaf_totals - 1.0) <= 1.0e-10)
                and np.all(values[leaf, 0, :] >= 0.0)
                and np.all(values[leaf, 0, :] <= 1.0 + 1.0e-10)
            )
            if values_are_probabilities:
                leaf_probability[leaf] = values[leaf, 0, positive_index]
            else:
                leaf_probability[leaf] = (
                    values[leaf, 0, positive_index] / leaf_totals
                )
            left[tree_index, :count] = tree_left
            right[tree_index, :count] = tree_right
            feature[tree_index, :count] = tree_feature
            threshold[tree_index, :count] = tree_threshold
            probability[tree_index, :count] = leaf_probability
            max_depth = max(max_depth, int(depths.max()))

        for array in (left, right, feature, threshold, probability):
            array.setflags(write=False)
        return cls(
            children_left=left,
            children_right=right,
            feature=feature,
            threshold=threshold,
            positive_probability=probability,
            tree_count=tree_count,
            feature_count=feature_count,
            max_depth=max_depth,
        )

    def predict_positive_probability(self, matrix: np.ndarray) -> np.ndarray:
        values = np.asarray(matrix, dtype=np.float32)
        if values.ndim != 2 or values.shape[1] != self.feature_count:
            raise ValueError("A09 matrix feature count does not match the frozen model")
        if not np.all(np.isfinite(values)):
            raise ValueError("A09 matrix contains non-finite values")
        batch_size = values.shape[0]
        if batch_size == 0:
            return np.empty(0, dtype=np.float64)

        nodes = np.zeros((batch_size, self.tree_count), dtype=np.intp)
        tree_indices = np.arange(self.tree_count, dtype=np.intp)[None, :]
        row_indices = np.arange(batch_size, dtype=np.intp)[:, None]
        for _ in range(self.max_depth + 1):
            features = self.feature[tree_indices, nodes]
            internal = features >= 0
            if not np.any(internal):
                break
            safe_features = np.where(internal, features, 0)
            split_values = values[row_indices, safe_features]
            split_thresholds = self.threshold[tree_indices, nodes]
            go_left = split_values <= split_thresholds
            next_nodes = np.where(
                go_left,
                self.children_left[tree_indices, nodes],
                self.children_right[tree_indices, nodes],
            )
            nodes = np.where(internal, next_nodes, nodes)
        if np.any(self.feature[tree_indices, nodes] >= 0):
            raise RuntimeError("A09 tree traversal exceeded the validated maximum depth")
        leaf_probabilities = self.positive_probability[tree_indices, nodes]
        if not np.all(np.isfinite(leaf_probabilities)):
            raise RuntimeError("A09 tree traversal did not terminate at valid leaves")
        # sklearn's ForestClassifier accumulates one tree at a time into a
        # float64 output buffer.  Reproduce that order; np.mean(axis=1) may use
        # a different reduction tree and move the result by one ULP.
        result = np.zeros(batch_size, dtype=np.float64)
        for tree_index in range(self.tree_count):
            result += leaf_probabilities[:, tree_index]
        result /= self.tree_count
        return result


class A09NumpyExactPredictor:
    """Probability-compatible executor for exactly three frozen A09 members."""

    engine_name = "numpy_exact_v1"

    def __init__(self, models: Sequence[object], positive_indices: Sequence[int]):
        if len(models) != 3 or len(positive_indices) != 3:
            raise ValueError("A09 NumPy engine requires exactly three ensemble members")
        self._forests = tuple(
            _CompiledForest.from_sklearn(model, int(positive_index))
            for model, positive_index in zip(models, positive_indices)
        )
        feature_counts = {forest.feature_count for forest in self._forests}
        if len(feature_counts) != 1:
            raise ValueError("A09 ensemble members disagree on feature count")
        self.feature_count = feature_counts.pop()
        self.tree_counts = tuple(forest.tree_count for forest in self._forests)

    def predict_positive_probability(self, matrix) -> np.ndarray:
        member_probabilities = [
            forest.predict_positive_probability(matrix) for forest in self._forests
        ]
        # np.mean(list, axis=0), used by gpu_service.py, first materializes this
        # three-row float64 array and then reduces it in member order.
        return np.mean(member_probabilities, axis=0)
