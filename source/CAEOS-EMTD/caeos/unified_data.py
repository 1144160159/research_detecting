"""Contract-driven access to the unified CAEOS multimodal CSV reservoir.

The module deliberately separates immutable data admission, row filtering,
group-aware open-set splitting, feature materialization, and train-only
sampling.  This keeps test labels and validation/test distributions out of
the sampling path while preserving a replayable audit trail.
"""

from __future__ import annotations

import base64
import binascii
import csv
import hashlib
import heapq
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, MutableMapping, Optional, Sequence


CSV_SCHEMA_VERSION = "caeos_unified_multimodal_csv_schema_v4"
FEATURE_VIEW_SCHEMA_VERSION = "caeos_unified_multimodal_feature_views_v1"
DATASET_MANIFEST_SCHEMA_VERSION = "caeos_dataset_class_csv_manifest_v1"
CONTENT_POLICY_SCHEMA_VERSION = "caeos_content_conflict_policy_v1"
DUPLICATE_AUDIT_SCHEMA_VERSION = "caeos_flow_duplicate_audit_v2"
POLICY_REGISTRY_SCHEMA_VERSION = "caeos_unified_data_access_policy_v1"
SPLIT_PLAN_SCHEMA_VERSION = "caeos_grouped_open_set_split_v1"
SAMPLING_AUDIT_SCHEMA_VERSION = "caeos_train_only_sampling_audit_v1"

LABEL_COLUMNS = (
    "traffic_class",
    "attack_category",
    "attack_subcategory",
    "fine_label",
    "family_label",
    "binary_label",
)
KNOWN_PARTITIONS = ("train", "known_validation", "known_test")
ALL_PARTITIONS = (*KNOWN_PARTITIONS, "unknown_test", "excluded_mixed")
GRAPH_SOURCE_COLUMNS = (
    "packet_count_stored",
    "packet_length_seq",
    "packet_iat_us_seq",
    "direction_seq",
    "packet_payload_length_seq",
    "tcp_flags_seq",
    "packet_ttl_seq",
)


class DataContractError(ValueError):
    """Raised when an immutable data or experiment contract is violated."""


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise DataContractError(f"JSON object required: {path}")
    return value


def canonical_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_embedded_hash(value: Mapping[str, Any], field_name: str) -> str:
    observed = str(value.get(field_name, ""))
    unsigned = dict(value)
    unsigned.pop(field_name, None)
    expected = canonical_json_hash(unsigned)
    if observed != expected:
        raise DataContractError(
            f"invalid embedded {field_name}: {observed or '<missing>'} != {expected}"
        )
    return observed


def sha256_file(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_bytes), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_fields(row: Mapping[str, str], columns: Sequence[str]) -> bytes:
    digest = hashlib.sha256()
    for column in columns:
        digest.update(column.encode("ascii"))
        digest.update(b"\0")
        digest.update(row[column].encode("utf-8"))
        digest.update(b"\0")
    return digest.digest()


def _is_sha256(value: str) -> bool:
    if len(value) != 64:
        return False
    try:
        bytes.fromhex(value)
    except ValueError:
        return False
    return True


def _resolve_declared_file(
    declared: str,
    *,
    sibling_dir: Path,
    fallback_dirs: Sequence[Path] = (),
) -> Path:
    path = Path(declared)
    candidates = [path, sibling_dir / path.name]
    candidates.extend(root / path.name for root in fallback_dirs)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[1]


def _stable_priority(seed: int, *parts: str) -> int:
    digest = hashlib.sha256()
    digest.update(str(seed).encode("ascii"))
    for part in parts:
        digest.update(b"\0")
        digest.update(part.encode("utf-8"))
    return int.from_bytes(digest.digest(), "big")


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    type_name: str
    values: Optional[tuple[Any, ...]] = None


@dataclass(frozen=True)
class CsvSchemaContract:
    path: Path
    raw: Mapping[str, Any]
    columns: tuple[ColumnSpec, ...]
    column_by_name: Mapping[str, ColumnSpec]
    sha256: str

    @classmethod
    def load(cls, path: Path) -> "CsvSchemaContract":
        raw = load_json_object(path)
        if raw.get("schema_version") != CSV_SCHEMA_VERSION:
            raise DataContractError(f"unsupported unified CSV schema: {path}")
        items = raw.get("columns")
        if not isinstance(items, list) or not items:
            raise DataContractError("CSV schema columns must be a non-empty list")
        columns: list[ColumnSpec] = []
        for item in items:
            if not isinstance(item, dict) or not item.get("name") or not item.get("type"):
                raise DataContractError("invalid column definition in CSV schema")
            values = item.get("values")
            columns.append(
                ColumnSpec(
                    name=str(item["name"]),
                    type_name=str(item["type"]),
                    values=tuple(values) if isinstance(values, list) else None,
                )
            )
        names = [item.name for item in columns]
        if len(names) != len(set(names)):
            raise DataContractError("CSV schema contains duplicate column names")
        return cls(
            path=path,
            raw=raw,
            columns=tuple(columns),
            column_by_name={item.name: item for item in columns},
            sha256=canonical_json_hash(raw),
        )

    @property
    def column_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.columns)

    def validate_header(self, fieldnames: Optional[Sequence[str]], source: Path) -> None:
        if fieldnames is None:
            raise DataContractError(f"CSV header is missing: {source}")
        observed = tuple(fieldnames)
        if observed != self.column_names:
            missing = sorted(set(self.column_names) - set(observed))
            extra = sorted(set(observed) - set(self.column_names))
            raise DataContractError(
                f"CSV header differs from frozen schema for {source}; "
                f"missing={missing}, extra={extra}, order_matches={not missing and not extra}"
            )

    def validate_final_labels(self, row: Mapping[str, str]) -> None:
        traffic_class = row.get("traffic_class", "")
        binary_label = row.get("binary_label", "")
        if traffic_class not in {"Benign", "Malicious"}:
            raise DataContractError(f"invalid final traffic_class: {traffic_class!r}")
        if binary_label not in {"0", "1"}:
            raise DataContractError(f"invalid final binary_label: {binary_label!r}")
        if (traffic_class == "Benign") != (binary_label == "0"):
            raise DataContractError("traffic_class and binary_label disagree")
        for name in ("attack_category", "attack_subcategory", "fine_label", "family_label"):
            if not row.get(name):
                raise DataContractError(f"required final label is empty: {name}")
        if traffic_class == "Benign" and row["attack_category"] != "Benign":
            raise DataContractError("benign row has a non-Benign attack_category")

    def parse_value(self, column: str, value: str) -> Any:
        spec = self.column_by_name[column]
        type_name = spec.type_name
        if type_name == "string":
            parsed: Any = value
        elif type_name == "sha256_hex":
            if not _is_sha256(value):
                raise DataContractError(f"invalid SHA-256 value in {column}")
            parsed = value
        elif type_name == "hex64":
            if not _is_sha256(value):
                raise DataContractError(f"invalid 64-character hexadecimal value in {column}")
            parsed = value
        elif type_name == "base64":
            try:
                parsed = base64.b64decode(value, validate=True)
            except (binascii.Error, ValueError) as error:
                raise DataContractError(f"invalid base64 value in {column}") from error
        elif type_name.endswith("_sequence") or type_name == "uint32_sequence_256":
            parsed = self._parse_integer_sequence(column, value, type_name)
        elif type_name.startswith("float"):
            parsed = float(value)
            if not math.isfinite(parsed):
                raise DataContractError(f"non-finite value in {column}")
        else:
            parsed = int(value)
            lower, upper = self._integer_bounds(type_name)
            if parsed < lower or parsed > upper:
                raise DataContractError(f"out-of-range {type_name} value in {column}")
        if spec.values is not None and parsed not in spec.values:
            raise DataContractError(f"unsupported value in {column}: {parsed!r}")
        return parsed

    def validate_full_row(self, row: Mapping[str, str]) -> None:
        if tuple(row.keys()) != self.column_names:
            raise DataContractError("row columns differ from the frozen schema")
        for spec in self.columns:
            self.parse_value(spec.name, row[spec.name])
        self.validate_final_labels(row)
        stored = int(row["packet_count_stored"])
        if stored > int(self.raw["maximum_packets_stored"]):
            raise DataContractError("packet_count_stored exceeds the schema maximum")
        if int(row["payload_bytes_stored"]) > int(self.raw["payload_prefix_bytes"]):
            raise DataContractError("payload_bytes_stored exceeds the schema maximum")
        if int(row["sanitized_l4_bytes_stored"]) > int(
            self.raw["sanitized_l4_prefix_bytes"]
        ):
            raise DataContractError("sanitized_l4_bytes_stored exceeds the schema maximum")

    @staticmethod
    def _integer_bounds(type_name: str) -> tuple[int, int]:
        signed = type_name.startswith("int")
        width_text = type_name[3:] if signed else type_name[4:]
        if not width_text.isdigit():
            raise DataContractError(f"unsupported integer type: {type_name}")
        width = int(width_text)
        if signed:
            return -(2 ** (width - 1)), 2 ** (width - 1) - 1
        return 0, 2**width - 1

    def _parse_integer_sequence(
        self, column: str, value: str, type_name: str
    ) -> tuple[int, ...]:
        if not value:
            values: tuple[int, ...] = ()
        else:
            try:
                values = tuple(int(item) for item in value.split(";"))
            except ValueError as error:
                raise DataContractError(f"invalid integer sequence in {column}") from error
        base_type = type_name.split("_sequence", 1)[0]
        lower, upper = self._integer_bounds(base_type)
        if any(item < lower or item > upper for item in values):
            raise DataContractError(f"out-of-range sequence element in {column}")
        if type_name == "uint32_sequence_256" and len(values) != 256:
            raise DataContractError("payload_histogram must contain exactly 256 bins")
        return values


@dataclass(frozen=True)
class FeatureViewContract:
    path: Path
    raw: Mapping[str, Any]
    sha256: str

    @classmethod
    def load(
        cls, path: Path, schema: CsvSchemaContract
    ) -> "FeatureViewContract":
        raw = load_json_object(path)
        if raw.get("schema_version") != FEATURE_VIEW_SCHEMA_VERSION:
            raise DataContractError(f"unsupported feature-view schema: {path}")
        if raw.get("source_csv_schema") != schema.raw.get("schema_version"):
            raise DataContractError("feature views are not bound to the selected CSV schema")
        modalities = raw.get("modalities")
        if not isinstance(modalities, dict) or set(modalities) != {
            "payload_semantics",
            "packet_behavior",
            "packet_interaction_graph",
        }:
            raise DataContractError("feature-view contract must define exactly three modalities")
        persisted = set(schema.column_names)
        derived = set(modalities["packet_behavior"].get("derived_from_existing_columns", []))
        referenced: set[str] = set()
        for section in modalities.values():
            if not isinstance(section, dict):
                raise DataContractError("invalid modality definition")
            for key, values in section.items():
                if key.endswith("_columns") and isinstance(values, list):
                    referenced.update(str(value) for value in values)
        unknown = referenced - persisted - derived
        if unknown:
            raise DataContractError(f"feature views reference unknown columns: {sorted(unknown)}")
        return cls(path=path, raw=raw, sha256=canonical_json_hash(raw))

    @property
    def forbidden_columns(self) -> frozenset[str]:
        return frozenset(str(value) for value in self.raw["default_forbidden_model_features"])

    def validate_request(
        self,
        modalities: Sequence[str],
        *,
        payload_bytes: int,
        packet_count: int,
    ) -> tuple[str, ...]:
        requested = tuple(dict.fromkeys(modalities))
        known = set(self.raw["modalities"])
        if not requested or not set(requested).issubset(known):
            raise DataContractError(f"invalid modality request: {requested}")
        payload_candidates = self.raw["modalities"]["payload_semantics"][
            "selection_candidates"
        ]
        packet_candidates = self.raw["modalities"]["packet_behavior"][
            "selection_candidates"
        ]
        if payload_bytes not in payload_candidates:
            raise DataContractError(f"payload_bytes must be one of {payload_candidates}")
        if packet_count not in packet_candidates:
            raise DataContractError(f"packet_count must be one of {packet_candidates}")
        return requested


def _summary(values: Sequence[int]) -> tuple[float, float, float, float]:
    if not values:
        return (0.0, 0.0, 0.0, 0.0)
    floats = [float(value) for value in values]
    mean = statistics.fmean(floats)
    std = statistics.pstdev(floats) if len(floats) > 1 else 0.0
    return (min(floats), max(floats), mean, std)


@dataclass(frozen=True)
class FeatureMaterializer:
    schema: CsvSchemaContract
    feature_views: FeatureViewContract
    modalities: tuple[str, ...]
    payload_bytes: int = 512
    packet_count: int = 16
    include_sanitized_l4_baseline: bool = False

    @classmethod
    def create(
        cls,
        schema: CsvSchemaContract,
        feature_views: FeatureViewContract,
        modalities: Sequence[str] = (
            "payload_semantics",
            "packet_behavior",
            "packet_interaction_graph",
        ),
        *,
        payload_bytes: int = 512,
        packet_count: int = 16,
        include_sanitized_l4_baseline: bool = False,
    ) -> "FeatureMaterializer":
        requested = feature_views.validate_request(
            modalities, payload_bytes=payload_bytes, packet_count=packet_count
        )
        return cls(
            schema=schema,
            feature_views=feature_views,
            modalities=requested,
            payload_bytes=payload_bytes,
            packet_count=packet_count,
            include_sanitized_l4_baseline=include_sanitized_l4_baseline,
        )

    @property
    def request_manifest(self) -> dict[str, Any]:
        value = {
            "modalities": list(self.modalities),
            "payload_bytes": self.payload_bytes,
            "packet_count": self.packet_count,
            "include_sanitized_l4_baseline": self.include_sanitized_l4_baseline,
            "feature_view_sha256": self.feature_views.sha256,
            "schema_sha256": self.schema.sha256,
        }
        value["feature_request_sha256"] = canonical_json_hash(value)
        return value

    def materialize(self, row: Mapping[str, str]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        if "payload_semantics" in self.modalities:
            output["payload_semantics"] = self._payload_view(row)
        behavior: Optional[dict[str, Any]] = None
        if "packet_behavior" in self.modalities:
            behavior = self._behavior_view(row)
            output["packet_behavior"] = behavior
        if "packet_interaction_graph" in self.modalities:
            output["packet_interaction_graph"] = self._graph_view(row, behavior)
        forbidden = self.feature_views.forbidden_columns.intersection(
            column for view in output.values() if isinstance(view, dict) for column in view
        )
        if forbidden:
            raise DataContractError(f"forbidden model features escaped projection: {sorted(forbidden)}")
        return output

    def _payload_view(self, row: Mapping[str, str]) -> dict[str, Any]:
        config = self.feature_views.raw["modalities"]["payload_semantics"]
        columns = list(config["primary_columns"])
        if self.include_sanitized_l4_baseline:
            columns.extend(config["raw_byte_baseline_columns"])
        view = {column: self.schema.parse_value(column, row[column]) for column in columns}
        view["payload_b64"] = view["payload_b64"][: self.payload_bytes]
        if "sanitized_l4_b64" in view:
            view["sanitized_l4_b64"] = view["sanitized_l4_b64"][: self.payload_bytes]
        return view

    def _behavior_view(self, row: Mapping[str, str]) -> dict[str, Any]:
        config = self.feature_views.raw["modalities"]["packet_behavior"]
        scalar_columns = config["safe_scalar_columns"]
        sequence_columns = config["sequence_columns"]
        encrypted_columns = config["encrypted_protocol_structure_columns"]
        view = {
            column: self.schema.parse_value(column, row[column])
            for column in scalar_columns
        }
        for column in (*sequence_columns, *encrypted_columns):
            parsed = self.schema.parse_value(column, row[column])
            if isinstance(parsed, tuple):
                parsed = parsed[: self.packet_count]
            view[column] = parsed
        derived = self._derived_behavior(row)
        for name in config["derived_from_existing_columns"]:
            view[name] = derived[name]
        return view

    def _derived_behavior(self, row: Mapping[str, str]) -> dict[str, Any]:
        lengths = self._sequence(row, "packet_length_seq")
        directions = self._sequence(row, "direction_seq")
        payload_lengths = self._sequence(row, "packet_payload_length_seq")
        count = min(
            self.packet_count,
            int(row["packet_count_stored"]),
            len(lengths),
            len(directions),
        )
        lengths = lengths[:count]
        directions = directions[:count]
        payload_lengths = payload_lengths[:count]
        first_direction = next((value for value in directions if value != 0), 1)
        relative = tuple(value * first_direction for value in directions)
        signed_lengths = tuple(
            length * direction for length, direction in zip(lengths, relative)
        )
        burst_packets: list[int] = []
        burst_bytes: list[int] = []
        for index, (direction, length) in enumerate(zip(relative, lengths)):
            if index == 0 or direction != relative[index - 1]:
                burst_packets.append(1)
                burst_bytes.append(length)
            else:
                burst_packets[-1] += 1
                burst_bytes[-1] += length
        payload_present = sum(1 for value in payload_lengths if value > 0)
        payload_fraction = payload_present / count if count else 0.0
        tls_present = bool(row.get("tls_record_type_seq") or row.get("quic_version_seq"))
        payload_present_anywhere = int(row.get("payload_bytes_total", "0")) > 0
        return {
            "initiator_relative_direction_seq": relative,
            "signed_packet_length_seq": signed_lengths,
            "directional_burst_count": len(burst_packets),
            "directional_burst_packet_count_summary": _summary(burst_packets),
            "directional_burst_byte_summary": _summary(burst_bytes),
            "payload_presence_fraction": payload_fraction,
            "modality_missingness_mask": (
                int(not payload_present_anywhere),
                int(count == 0),
                int(not tls_present),
            ),
        }

    def _graph_view(
        self, row: Mapping[str, str], behavior: Optional[Mapping[str, Any]]
    ) -> dict[str, Any]:
        derived = (
            dict(behavior)
            if behavior is not None
            else self._derived_behavior(row)
        )
        lengths = self._sequence(row, "packet_length_seq")
        iats = self._sequence(row, "packet_iat_us_seq")
        payload_lengths = self._sequence(row, "packet_payload_length_seq")
        flags = self._sequence(row, "tcp_flags_seq")
        ttl = self._sequence(row, "packet_ttl_seq")
        relative = tuple(derived["initiator_relative_direction_seq"])
        signed = tuple(derived["signed_packet_length_seq"])
        count = min(
            self.packet_count,
            int(row["packet_count_stored"]),
            len(lengths),
            len(relative),
        )

        def at(values: Sequence[int], index: int) -> int:
            return int(values[index]) if index < len(values) else 0

        nodes = tuple(
            (
                at(signed, index),
                at(iats, index),
                at(relative, index),
                at(payload_lengths, index),
                at(flags, index),
                at(ttl, index),
            )
            for index in range(count)
        )
        edges: set[tuple[int, int, str]] = set()
        for index in range(1, count):
            self._add_bidirectional_edge(edges, index - 1, index, "temporal_adjacency")
            if relative[index] == relative[index - 1]:
                self._add_bidirectional_edge(
                    edges, index - 1, index, "same_direction_burst_membership"
                )
            else:
                self._add_bidirectional_edge(
                    edges, index - 1, index, "request_response_transition"
                )
        return {
            "node_feature_order": (
                "signed_packet_length",
                "packet_iat_us",
                "initiator_relative_direction",
                "packet_payload_length",
                "tcp_flags",
                "packet_ttl",
            ),
            "nodes": nodes,
            "edges": tuple(sorted(edges)),
        }

    def _sequence(self, row: Mapping[str, str], column: str) -> tuple[int, ...]:
        value = self.schema.parse_value(column, row[column])
        return tuple(value[: self.packet_count])

    @staticmethod
    def _add_bidirectional_edge(
        edges: set[tuple[int, int, str]], left: int, right: int, relation: str
    ) -> None:
        edges.add((left, right, relation))
        edges.add((right, left, relation))


@dataclass(frozen=True)
class ClassCsvContract:
    attack_category: str
    path: Path
    rows: int
    size_bytes: int
    sha256: str
    verification: Mapping[str, Any]


@dataclass(frozen=True)
class DatasetManifestContract:
    path: Path
    raw: Mapping[str, Any]
    class_csvs: tuple[ClassCsvContract, ...]
    manifest_sha256: str

    @property
    def dataset_id(self) -> str:
        return str(self.raw["dataset_id"])

    @property
    def row_count(self) -> int:
        declared = self.raw.get("row_count")
        if declared is not None:
            return int(declared)
        return sum(item.rows for item in self.class_csvs)

    @classmethod
    def load(
        cls,
        path: Path,
        schema: CsvSchemaContract,
        *,
        output_root: Optional[Path] = None,
        integrity: str = "stat",
        admitted_label_prefixes: Sequence[str] = ("aligned_unique_",),
    ) -> "DatasetManifestContract":
        if integrity not in {"manifest", "stat", "sha256"}:
            raise DataContractError("integrity must be manifest, stat, or sha256")
        raw = load_json_object(path)
        if raw.get("schema_version") != DATASET_MANIFEST_SCHEMA_VERSION:
            raise DataContractError(f"unsupported dataset manifest: {path}")
        if raw.get("complete") is not True:
            raise DataContractError(f"dataset manifest is incomplete: {path}")
        manifest_sha = verify_embedded_hash(raw, "manifest_sha256")
        if raw.get("schema_sha256") and raw["schema_sha256"] != schema.sha256:
            raise DataContractError("dataset manifest is bound to a different CSV schema")
        dataset_id = str(raw.get("dataset_id", ""))
        if not dataset_id:
            raise DataContractError("dataset manifest has no dataset_id")
        items = raw.get("class_csvs")
        if not isinstance(items, list) or not items:
            raise DataContractError("dataset manifest has no class CSVs")
        fallback = ()
        if output_root is not None:
            fallback = (output_root / dataset_id,)
        class_csvs: list[ClassCsvContract] = []
        categories: set[str] = set()
        for item in items:
            if not isinstance(item, dict):
                raise DataContractError("invalid class CSV manifest entry")
            category = str(item.get("attack_category", ""))
            if not category or category in categories:
                raise DataContractError("class CSV attack categories must be non-empty and unique")
            categories.add(category)
            rows = int(item.get("rows", 0))
            size_bytes = int(item.get("size_bytes", 0))
            file_sha = str(item.get("sha256", ""))
            verification = item.get("verification")
            if rows <= 0 or size_bytes <= 0 or not _is_sha256(file_sha):
                raise DataContractError(f"invalid class CSV contract for {category}")
            if not isinstance(verification, dict):
                raise DataContractError(f"missing class CSV verification for {category}")
            if verification.get("full_row_validation") is not True:
                raise DataContractError(f"full row validation did not pass for {category}")
            if int(verification.get("rows", -1)) != rows:
                raise DataContractError(f"verified row count differs for {category}")
            statuses = verification.get("label_status_counts", {})
            if not isinstance(statuses, dict) or sum(int(v) for v in statuses.values()) != rows:
                raise DataContractError(f"invalid label-status counts for {category}")
            if any(
                not any(str(status).startswith(prefix) for prefix in admitted_label_prefixes)
                for status in statuses
            ):
                raise DataContractError(f"unadmitted label status in {category}: {sorted(statuses)}")
            resolved = _resolve_declared_file(
                str(item.get("path", "")), sibling_dir=path.parent, fallback_dirs=fallback
            )
            if integrity in {"stat", "sha256"}:
                if not resolved.is_file():
                    raise DataContractError(f"class CSV is missing: {resolved}")
                if resolved.stat().st_size != size_bytes:
                    raise DataContractError(f"class CSV size differs: {resolved}")
            if integrity == "sha256" and sha256_file(resolved) != file_sha:
                raise DataContractError(f"class CSV SHA-256 differs: {resolved}")
            class_csvs.append(
                ClassCsvContract(category, resolved, rows, size_bytes, file_sha, verification)
            )
        declared_row_count = raw.get("row_count")
        if declared_row_count is not None and sum(item.rows for item in class_csvs) != int(
            declared_row_count
        ):
            raise DataContractError("class CSV row sum differs from dataset manifest")
        return cls(path=path, raw=raw, class_csvs=tuple(class_csvs), manifest_sha256=manifest_sha)


@dataclass(frozen=True)
class ContentConflictFilter:
    policy_path: Optional[Path]
    policy: Optional[Mapping[str, Any]]
    policy_sha256: Optional[str]
    ambiguous_keys: frozenset[bytes]
    excluded_non_model_columns: frozenset[str]

    @classmethod
    def allow_all(cls, excluded_columns: Iterable[str]) -> "ContentConflictFilter":
        return cls(None, None, None, frozenset(), frozenset(excluded_columns))

    @classmethod
    def load(
        cls,
        path: Path,
        manifest: DatasetManifestContract,
    ) -> "ContentConflictFilter":
        raw = load_json_object(path)
        if raw.get("schema_version") != CONTENT_POLICY_SCHEMA_VERSION:
            raise DataContractError(f"unsupported content-conflict policy: {path}")
        policy_sha = verify_embedded_hash(raw, "policy_sha256")
        if raw.get("dataset_id") != manifest.dataset_id:
            raise DataContractError("content policy dataset_id differs from manifest")
        if raw.get("dataset_manifest_sha256") != manifest.manifest_sha256:
            raise DataContractError("content policy is stale for the selected dataset manifest")
        if raw.get("decision") != "exclude_all_rows_whose_model_content_sha256_is_cross_label":
            raise DataContractError("unsupported content-conflict decision")
        if raw.get("model_view_gate_pass") is not True:
            raise DataContractError("content-conflict model-view gate did not pass")
        key_path = _resolve_declared_file(
            str(raw.get("ambiguous_content_path", "")), sibling_dir=path.parent
        )
        if not key_path.is_file():
            raise DataContractError(f"ambiguous-content index is missing: {key_path}")
        if key_path.stat().st_size != int(raw.get("ambiguous_content_size_bytes", -1)):
            raise DataContractError("ambiguous-content index size differs from policy")
        if sha256_file(key_path) != raw.get("ambiguous_content_sha256"):
            raise DataContractError("ambiguous-content index SHA-256 differs from policy")
        content = key_path.read_bytes()
        if len(content) % 32:
            raise DataContractError("ambiguous-content index is truncated")
        keys = frozenset(content[offset : offset + 32] for offset in range(0, len(content), 32))
        if len(keys) != int(raw.get("ambiguous_content_key_count", -1)):
            raise DataContractError("ambiguous-content key count differs from policy")
        fingerprint = raw.get("fingerprint_contract")
        if not isinstance(fingerprint, dict):
            raise DataContractError("content policy has no fingerprint contract")
        excluded = fingerprint.get("excluded_non_model_columns")
        if not isinstance(excluded, list) or not excluded:
            raise DataContractError("content policy has no non-model column exclusion contract")
        return cls(path, raw, policy_sha, keys, frozenset(str(v) for v in excluded))

    def content_columns(self, fieldnames: Sequence[str]) -> tuple[str, ...]:
        columns = tuple(name for name in fieldnames if name not in self.excluded_non_model_columns)
        if not columns:
            raise DataContractError("no model-eligible columns remain for content filtering")
        return columns

    def content_digest(self, row: Mapping[str, str], fieldnames: Sequence[str]) -> bytes:
        return digest_fields(row, self.content_columns(fieldnames))

    def is_eligible(self, row: Mapping[str, str], fieldnames: Sequence[str]) -> bool:
        if not self.ambiguous_keys:
            return True
        return self.content_digest(row, fieldnames) not in self.ambiguous_keys


@dataclass(frozen=True)
class DuplicateAuditContract:
    path: Path
    raw: Mapping[str, Any]
    sha256: str
    capture_equivalence_edges: tuple[tuple[str, str], ...]
    binding_mode: str

    @classmethod
    def load(
        cls,
        path: Path,
        manifest: DatasetManifestContract,
        conflict_filter: ContentConflictFilter,
    ) -> "DuplicateAuditContract":
        raw = load_json_object(path)
        if raw.get("schema_version") != DUPLICATE_AUDIT_SCHEMA_VERSION:
            raise DataContractError(f"unsupported duplicate audit: {path}")
        if raw.get("dataset_id") != manifest.dataset_id:
            raise DataContractError("duplicate audit dataset_id differs from manifest")
        if int(raw.get("row_count", -1)) != manifest.row_count:
            raise DataContractError("duplicate audit row count differs from manifest")
        audit_sha = sha256_file(path)
        binding_mode = "current_manifest"
        if raw.get("dataset_manifest_sha256") != manifest.manifest_sha256:
            repair = (conflict_filter.policy or {}).get("content_invariant_identity_repair")
            checks = repair.get("checks", {}) if isinstance(repair, dict) else {}
            if not checks or not all(checks.values()):
                raise DataContractError("duplicate audit is stale for the selected manifest")
            binding_mode = "content_invariant_identity_repair"
        if conflict_filter.policy is not None:
            policy = conflict_filter.policy
            if policy.get("source_duplicate_audit_sha256") != audit_sha:
                raise DataContractError("content policy is not bound to the selected duplicate audit")
            if policy.get("fingerprint_contract") != raw.get("fingerprint_contract"):
                raise DataContractError("content policy and duplicate audit fingerprint contracts differ")
        elif raw.get("gate_pass") is not True:
            raise DataContractError("raw duplicate audit failed and no remediation policy was supplied")
        content = raw.get("content")
        if not isinstance(content, dict):
            raise DataContractError("duplicate audit has no content result")
        edges: list[tuple[str, str]] = []
        for edge in content.get("capture_equivalence_edges", []):
            if not isinstance(edge, list) or len(edge) != 2:
                raise DataContractError("invalid capture-equivalence edge")
            left, right = str(edge[0]), str(edge[1])
            if not _is_sha256(left) or not _is_sha256(right) or left == right:
                raise DataContractError("invalid capture-equivalence endpoint")
            edges.append(tuple(sorted((left, right))))
        return cls(path, raw, audit_sha, tuple(sorted(set(edges))), binding_mode)


@dataclass(frozen=True)
class DatasetPolicySpec:
    dataset_id: str
    manifest: str
    duplicate_audit: str
    content_conflict_policy: Optional[str]
    require_content_conflict_policy: bool
    label_status_prefixes: tuple[str, ...]
    dataset_role: str


@dataclass(frozen=True)
class DatasetPolicyRegistry:
    path: Path
    raw: Mapping[str, Any]
    sha256: str
    specs: Mapping[str, DatasetPolicySpec]

    @classmethod
    def load(cls, path: Path) -> "DatasetPolicyRegistry":
        raw = load_json_object(path)
        if raw.get("schema_version") != POLICY_REGISTRY_SCHEMA_VERSION:
            raise DataContractError(f"unsupported data-access policy registry: {path}")
        defaults = raw.get("defaults")
        datasets = raw.get("datasets")
        if not isinstance(defaults, dict) or not isinstance(datasets, dict) or not datasets:
            raise DataContractError("policy registry requires defaults and datasets")
        default_prefixes = tuple(str(v) for v in defaults.get("label_status_prefixes", []))
        if not default_prefixes:
            raise DataContractError("policy registry has no admitted label-status prefixes")
        specs: dict[str, DatasetPolicySpec] = {}
        for dataset_id, item in datasets.items():
            if not isinstance(item, dict):
                raise DataContractError(f"invalid policy registry entry: {dataset_id}")
            prefixes = tuple(str(v) for v in item.get("label_status_prefixes", default_prefixes))
            spec = DatasetPolicySpec(
                dataset_id=str(dataset_id),
                manifest=str(item.get("manifest", f"{dataset_id}/dataset.manifest.json")),
                duplicate_audit=str(item.get("duplicate_audit", "")),
                content_conflict_policy=(
                    str(item["content_conflict_policy"])
                    if item.get("content_conflict_policy")
                    else None
                ),
                require_content_conflict_policy=bool(
                    item.get(
                        "require_content_conflict_policy",
                        defaults.get("require_content_conflict_policy", True),
                    )
                ),
                label_status_prefixes=prefixes,
                dataset_role=str(item.get("dataset_role", "external_confirmation")),
            )
            if not spec.duplicate_audit:
                raise DataContractError(f"duplicate audit path missing for {dataset_id}")
            if spec.require_content_conflict_policy and not spec.content_conflict_policy:
                raise DataContractError(f"content policy path missing for {dataset_id}")
            specs[spec.dataset_id] = spec
        return cls(path, raw, sha256_file(path), specs)

    def for_dataset(self, dataset_id: str) -> DatasetPolicySpec:
        try:
            return self.specs[dataset_id]
        except KeyError as error:
            raise DataContractError(f"dataset is absent from the policy registry: {dataset_id}") from error


@dataclass
class LoadAudit:
    dataset_id: str
    raw_rows: int = 0
    eligible_rows: int = 0
    excluded_rows: Counter[str] = field(default_factory=Counter)
    rows_by_family: Counter[str] = field(default_factory=Counter)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "raw_rows": self.raw_rows,
            "eligible_rows": self.eligible_rows,
            "excluded_rows": dict(sorted(self.excluded_rows.items())),
            "rows_by_family": dict(sorted(self.rows_by_family.items())),
        }


@dataclass(frozen=True)
class RawDataRecord:
    dataset_id: str
    partition: str
    row: Mapping[str, str]

    @property
    def sample_id(self) -> str:
        return self.row["sample_id"]

    @property
    def capture_id(self) -> str:
        return self.row["capture_id"]


@dataclass(frozen=True)
class ModelExample:
    dataset_id: str
    partition: str
    sample_id: str
    capture_id: str
    labels: Mapping[str, str]
    views: Mapping[str, Any]


@dataclass(frozen=True)
class _CaptureObservation:
    capture_id: str
    families: frozenset[str]
    rows: int


@dataclass(frozen=True)
class _EquivalenceGroup:
    group_id: str
    captures: tuple[str, ...]
    families: frozenset[str]
    rows: int


class _UnionFind:
    def __init__(self, values: Iterable[str]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: str) -> str:
        parent = self.parent[value]
        while parent != self.parent[parent]:
            self.parent[parent] = self.parent[self.parent[parent]]
            parent = self.parent[parent]
        while value != parent:
            next_value = self.parent[value]
            self.parent[value] = parent
            value = next_value
        return parent

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        first, second = sorted((left_root, right_root))
        self.parent[second] = first


@dataclass(frozen=True)
class SplitPlan:
    dataset_id: str
    dataset_manifest_sha256: str
    content_policy_sha256: Optional[str]
    duplicate_audit_sha256: str
    seed: int
    label_column: str
    unknown_families: tuple[str, ...]
    known_ratios: Mapping[str, float]
    assignments: Mapping[str, str]
    summary: Mapping[str, Any]
    split_plan_sha256: str

    def partition_for(self, capture_id: str) -> str:
        try:
            return self.assignments[capture_id]
        except KeyError as error:
            raise DataContractError(f"capture is absent from split plan: {capture_id}") from error

    def unsigned_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SPLIT_PLAN_SCHEMA_VERSION,
            "dataset_id": self.dataset_id,
            "dataset_manifest_sha256": self.dataset_manifest_sha256,
            "content_policy_sha256": self.content_policy_sha256,
            "duplicate_audit_sha256": self.duplicate_audit_sha256,
            "seed": self.seed,
            "label_column": self.label_column,
            "unknown_families": list(self.unknown_families),
            "known_ratios": dict(self.known_ratios),
            "assignments": dict(sorted(self.assignments.items())),
            "summary": dict(self.summary),
        }

    def to_dict(self) -> dict[str, Any]:
        value = self.unsigned_dict()
        value["split_plan_sha256"] = self.split_plan_sha256
        return value

    @classmethod
    def create(cls, **kwargs: Any) -> "SplitPlan":
        provisional = cls(split_plan_sha256="", **kwargs)
        digest = canonical_json_hash(provisional.unsigned_dict())
        return cls(split_plan_sha256=digest, **kwargs)

    @classmethod
    def load(cls, path: Path) -> "SplitPlan":
        raw = load_json_object(path)
        if raw.get("schema_version") != SPLIT_PLAN_SCHEMA_VERSION:
            raise DataContractError(f"unsupported split plan: {path}")
        verify_embedded_hash(raw, "split_plan_sha256")
        return cls(
            dataset_id=str(raw["dataset_id"]),
            dataset_manifest_sha256=str(raw["dataset_manifest_sha256"]),
            content_policy_sha256=raw.get("content_policy_sha256"),
            duplicate_audit_sha256=str(raw["duplicate_audit_sha256"]),
            seed=int(raw["seed"]),
            label_column=str(raw["label_column"]),
            unknown_families=tuple(str(v) for v in raw["unknown_families"]),
            known_ratios={str(k): float(v) for k, v in raw["known_ratios"].items()},
            assignments={str(k): str(v) for k, v in raw["assignments"].items()},
            summary=raw["summary"],
            split_plan_sha256=str(raw["split_plan_sha256"]),
        )


class UnifiedDatasetLoader:
    """Read and enforce one dataset's immutable access contract."""

    def __init__(
        self,
        *,
        schema: CsvSchemaContract,
        feature_views: FeatureViewContract,
        registry: DatasetPolicyRegistry,
        policy_spec: DatasetPolicySpec,
        manifest: DatasetManifestContract,
        conflict_filter: ContentConflictFilter,
        duplicate_audit: DuplicateAuditContract,
        materializer: FeatureMaterializer,
        row_validation: str,
    ) -> None:
        if row_validation not in {"labels", "full"}:
            raise DataContractError("row_validation must be labels or full")
        self.schema = schema
        self.feature_views = feature_views
        self.registry = registry
        self.policy_spec = policy_spec
        self.manifest = manifest
        self.conflict_filter = conflict_filter
        self.duplicate_audit = duplicate_audit
        self.materializer = materializer
        self.row_validation = row_validation
        self.last_load_audit = LoadAudit(manifest.dataset_id)

    @classmethod
    def open(
        cls,
        *,
        output_root: Path,
        schema_path: Path,
        feature_views_path: Path,
        policy_registry_path: Path,
        dataset_id: str,
        integrity: str = "stat",
        row_validation: str = "labels",
        modalities: Sequence[str] = (
            "payload_semantics",
            "packet_behavior",
            "packet_interaction_graph",
        ),
        payload_bytes: int = 512,
        packet_count: int = 16,
        include_sanitized_l4_baseline: bool = False,
    ) -> "UnifiedDatasetLoader":
        schema = CsvSchemaContract.load(schema_path)
        feature_views = FeatureViewContract.load(feature_views_path, schema)
        registry = DatasetPolicyRegistry.load(policy_registry_path)
        spec = registry.for_dataset(dataset_id)
        manifest_path = output_root / spec.manifest
        manifest = DatasetManifestContract.load(
            manifest_path,
            schema,
            output_root=output_root,
            integrity=integrity,
            admitted_label_prefixes=spec.label_status_prefixes,
        )
        if manifest.dataset_id != dataset_id:
            raise DataContractError("selected dataset_id differs from dataset manifest")
        excluded = set(feature_views.raw["audit_only_columns"])
        excluded.update(feature_views.raw["target_columns"])
        excluded.update(feature_views.raw["default_forbidden_model_features"])
        conflict_filter = ContentConflictFilter.allow_all(excluded)
        if spec.content_conflict_policy:
            conflict_filter = ContentConflictFilter.load(
                output_root / spec.content_conflict_policy, manifest
            )
        elif spec.require_content_conflict_policy:
            raise DataContractError("required content-conflict policy is absent")
        duplicate_audit = DuplicateAuditContract.load(
            output_root / spec.duplicate_audit, manifest, conflict_filter
        )
        materializer = FeatureMaterializer.create(
            schema,
            feature_views,
            modalities,
            payload_bytes=payload_bytes,
            packet_count=packet_count,
            include_sanitized_l4_baseline=include_sanitized_l4_baseline,
        )
        return cls(
            schema=schema,
            feature_views=feature_views,
            registry=registry,
            policy_spec=spec,
            manifest=manifest,
            conflict_filter=conflict_filter,
            duplicate_audit=duplicate_audit,
            materializer=materializer,
            row_validation=row_validation,
        )

    def metadata_report(self) -> dict[str, Any]:
        report = {
            "dataset_id": self.manifest.dataset_id,
            "dataset_role": self.policy_spec.dataset_role,
            "row_count": self.manifest.row_count,
            "class_csv_count": len(self.manifest.class_csvs),
            "dataset_manifest_sha256": self.manifest.manifest_sha256,
            "schema_sha256": self.schema.sha256,
            "feature_views_sha256": self.feature_views.sha256,
            "policy_registry_sha256": self.registry.sha256,
            "content_policy_sha256": self.conflict_filter.policy_sha256,
            "ambiguous_content_key_count": len(self.conflict_filter.ambiguous_keys),
            "duplicate_audit_sha256": self.duplicate_audit.sha256,
            "duplicate_audit_binding_mode": self.duplicate_audit.binding_mode,
            "capture_equivalence_edge_count": len(
                self.duplicate_audit.capture_equivalence_edges
            ),
            "feature_request": self.materializer.request_manifest,
            "gate_pass": True,
        }
        report["report_sha256"] = canonical_json_hash(report)
        return report

    def iter_contract_rows(self) -> Iterator[dict[str, str]]:
        """Yield rows that satisfy the immutable manifest, schema, and label contract."""
        audit = LoadAudit(self.manifest.dataset_id)
        self.last_load_audit = audit
        for class_csv in self.manifest.class_csvs:
            observed_rows = 0
            with class_csv.path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                self.schema.validate_header(reader.fieldnames, class_csv.path)
                for row in reader:
                    observed_rows += 1
                    audit.raw_rows += 1
                    self._validate_row(row, class_csv)
                    audit.eligible_rows += 1
                    audit.rows_by_family[row["family_label"]] += 1
                    yield row
            if observed_rows != class_csv.rows:
                raise DataContractError(
                    f"observed row count differs from manifest for {class_csv.path}: "
                    f"{observed_rows} != {class_csv.rows}"
                )
        if audit.raw_rows != self.manifest.row_count:
            raise DataContractError("streamed row count differs from dataset manifest")

    def strategy(self) -> "OpenSetDataStrategy":
        return OpenSetDataStrategy(self)

    def iter_eligible_rows(self) -> Iterator[dict[str, str]]:
        """Compatibility facade; new code should use ``loader.strategy()``."""
        yield from self.strategy().iter_eligible_rows()

    def build_split_plan(
        self,
        *,
        unknown_families: Iterable[str],
        seed: int,
        label_column: str = "family_label",
        train_ratio: float = 0.7,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.2,
        mixed_unknown_action: str = "reject",
    ) -> SplitPlan:
        return self.strategy().build_split_plan(
            unknown_families=unknown_families,
            seed=seed,
            label_column=label_column,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
            test_ratio=test_ratio,
            mixed_unknown_action=mixed_unknown_action,
        )

    def iter_records(
        self,
        split_plan: SplitPlan,
        *,
        partitions: Optional[Iterable[str]] = None,
        selected_sample_ids: Optional[Iterable[str]] = None,
    ) -> Iterator[RawDataRecord]:
        yield from self.strategy().iter_records(
            split_plan,
            partitions=partitions,
            selected_sample_ids=selected_sample_ids,
        )

    def materialize_records(
        self, records: Iterable[RawDataRecord]
    ) -> Iterator[ModelExample]:
        for record in records:
            yield ModelExample(
                dataset_id=record.dataset_id,
                partition=record.partition,
                sample_id=record.sample_id,
                capture_id=record.capture_id,
                labels={name: record.row[name] for name in LABEL_COLUMNS},
                views=self.materializer.materialize(record.row),
            )

    def _validate_row(self, row: Mapping[str, str], class_csv: ClassCsvContract) -> None:
        if row.get("schema_version") != self.schema.raw["schema_version"]:
            raise DataContractError("row schema_version differs from selected schema")
        if row.get("dataset_id") != self.manifest.dataset_id:
            raise DataContractError("row dataset_id differs from selected manifest")
        if row.get("attack_category") != class_csv.attack_category:
            raise DataContractError("row attack_category differs from class CSV contract")
        if not any(
            row.get("label_status", "").startswith(prefix)
            for prefix in self.policy_spec.label_status_prefixes
        ):
            raise DataContractError(f"row label_status is not admitted: {row.get('label_status')!r}")
        self.schema.validate_final_labels(row)
        if self.row_validation == "full":
            self.schema.validate_full_row(row)

    def _validate_split_plan_binding(self, split_plan: SplitPlan) -> None:
        if split_plan.dataset_id != self.manifest.dataset_id:
            raise DataContractError("split plan dataset_id differs from loader")
        if split_plan.dataset_manifest_sha256 != self.manifest.manifest_sha256:
            raise DataContractError("split plan is stale for the selected dataset manifest")
        if split_plan.content_policy_sha256 != self.conflict_filter.policy_sha256:
            raise DataContractError("split plan is bound to a different content policy")
        if split_plan.duplicate_audit_sha256 != self.duplicate_audit.sha256:
            raise DataContractError("split plan is bound to a different duplicate audit")
        if canonical_json_hash(split_plan.unsigned_dict()) != split_plan.split_plan_sha256:
            raise DataContractError("split plan canonical hash is invalid")


class OpenSetDataStrategy:
    """Apply experiment policy after immutable dataset admission."""

    def __init__(self, loader: UnifiedDatasetLoader) -> None:
        self.loader = loader
        self.last_load_audit = LoadAudit(loader.manifest.dataset_id)

    def iter_eligible_rows(self) -> Iterator[dict[str, str]]:
        audit = LoadAudit(self.loader.manifest.dataset_id)
        self.last_load_audit = audit
        fieldnames = self.loader.schema.column_names
        for row in self.loader.iter_contract_rows():
            audit.raw_rows += 1
            if not self.loader.conflict_filter.is_eligible(row, fieldnames):
                audit.excluded_rows["cross_label_model_content"] += 1
                continue
            audit.eligible_rows += 1
            audit.rows_by_family[row["family_label"]] += 1
            yield row
        if audit.raw_rows != self.loader.manifest.row_count:
            raise DataContractError("strategy input row count differs from dataset manifest")
        expected_eligible = (
            int(self.loader.conflict_filter.policy["model_eligible_row_count"])
            if self.loader.conflict_filter.policy is not None
            else self.loader.manifest.row_count
        )
        if audit.eligible_rows != expected_eligible:
            raise DataContractError(
                f"eligible row count differs from policy: {audit.eligible_rows} != {expected_eligible}"
            )

    def build_split_plan(
        self,
        *,
        unknown_families: Iterable[str],
        seed: int,
        label_column: str = "family_label",
        train_ratio: float = 0.7,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.2,
        mixed_unknown_action: str = "reject",
    ) -> SplitPlan:
        if label_column not in LABEL_COLUMNS:
            raise DataContractError(f"unsupported open-set label column: {label_column}")
        if mixed_unknown_action not in {"reject", "exclude"}:
            raise DataContractError("mixed_unknown_action must be reject or exclude")
        ratios = {
            "train": float(train_ratio),
            "known_validation": float(validation_ratio),
            "known_test": float(test_ratio),
        }
        if any(value < 0 for value in ratios.values()) or not math.isclose(
            sum(ratios.values()), 1.0, rel_tol=0.0, abs_tol=1e-12
        ):
            raise DataContractError("known split ratios must be non-negative and sum to one")
        unknown = tuple(sorted(set(str(value) for value in unknown_families)))
        if not unknown or "Benign" in unknown:
            raise DataContractError("unknown_families must be non-empty and cannot include Benign")
        captures = self._scan_capture_observations(label_column)
        groups, ignored_edges = self._equivalence_groups(captures)
        assignments: dict[str, str] = {}
        known_by_stratum: dict[str, list[_EquivalenceGroup]] = defaultdict(list)
        partition_groups: Counter[str] = Counter()
        partition_rows: Counter[str] = Counter()
        mixed_groups = 0
        for group in groups:
            unknown_labels = group.families.intersection(unknown)
            known_labels = group.families.difference(unknown)
            if unknown_labels and known_labels:
                mixed_groups += 1
                if mixed_unknown_action == "reject":
                    raise DataContractError(
                        "capture-equivalence group spans known and unknown families: "
                        f"{group.group_id} {sorted(group.families)}"
                    )
                partition = "excluded_mixed"
                self._assign_group(assignments, group, partition)
                partition_groups[partition] += 1
                partition_rows[partition] += group.rows
            elif unknown_labels:
                partition = "unknown_test"
                self._assign_group(assignments, group, partition)
                partition_groups[partition] += 1
                partition_rows[partition] += group.rows
            else:
                stratum = "|".join(sorted(group.families))
                known_by_stratum[stratum].append(group)
        for stratum, stratum_groups in sorted(known_by_stratum.items()):
            ordered = sorted(
                stratum_groups,
                key=lambda item: (
                    _stable_priority(
                        seed,
                        self.loader.manifest.dataset_id,
                        stratum,
                        item.group_id,
                    ),
                    item.group_id,
                ),
            )
            counts = self._allocate_counts(len(ordered), ratios)
            offset = 0
            for partition in KNOWN_PARTITIONS:
                for group in ordered[offset : offset + counts[partition]]:
                    self._assign_group(assignments, group, partition)
                    partition_groups[partition] += 1
                    partition_rows[partition] += group.rows
                offset += counts[partition]
        if set(assignments) != set(captures):
            raise DataContractError("not every eligible capture received a split assignment")
        summary = {
            "eligible_capture_count": len(captures),
            "equivalence_group_count": len(groups),
            "capture_equivalence_edges": len(
                self.loader.duplicate_audit.capture_equivalence_edges
            ),
            "ignored_edges_without_two_eligible_captures": ignored_edges,
            "mixed_known_unknown_group_count": mixed_groups,
            "partition_group_counts": dict(sorted(partition_groups.items())),
            "partition_row_counts": dict(sorted(partition_rows.items())),
            "load_audit": self.last_load_audit.to_dict(),
            "group_leakage_count": 0,
        }
        return SplitPlan.create(
            dataset_id=self.loader.manifest.dataset_id,
            dataset_manifest_sha256=self.loader.manifest.manifest_sha256,
            content_policy_sha256=self.loader.conflict_filter.policy_sha256,
            duplicate_audit_sha256=self.loader.duplicate_audit.sha256,
            seed=int(seed),
            label_column=label_column,
            unknown_families=unknown,
            known_ratios=ratios,
            assignments=assignments,
            summary=summary,
        )

    def iter_records(
        self,
        split_plan: SplitPlan,
        *,
        partitions: Optional[Iterable[str]] = None,
        selected_sample_ids: Optional[Iterable[str]] = None,
    ) -> Iterator[RawDataRecord]:
        self.loader._validate_split_plan_binding(split_plan)
        allowed = set(partitions or ALL_PARTITIONS)
        if not allowed.issubset(ALL_PARTITIONS):
            raise DataContractError(f"unsupported requested partitions: {sorted(allowed)}")
        selected = set(selected_sample_ids) if selected_sample_ids is not None else None
        for row in self.iter_eligible_rows():
            partition = split_plan.partition_for(row["capture_id"])
            if partition not in allowed or partition == "excluded_mixed":
                continue
            if selected is not None and row["sample_id"] not in selected:
                continue
            yield RawDataRecord(self.loader.manifest.dataset_id, partition, row)

    def _scan_capture_observations(
        self, label_column: str
    ) -> Mapping[str, _CaptureObservation]:
        families: dict[str, set[str]] = defaultdict(set)
        rows: Counter[str] = Counter()
        for row in self.iter_eligible_rows():
            capture_id = row["capture_id"]
            if not capture_id:
                raise DataContractError("eligible row has an empty capture_id")
            families[capture_id].add(row[label_column])
            rows[capture_id] += 1
        return {
            capture_id: _CaptureObservation(
                capture_id, frozenset(families[capture_id]), rows[capture_id]
            )
            for capture_id in families
        }

    def _equivalence_groups(
        self, captures: Mapping[str, _CaptureObservation]
    ) -> tuple[list[_EquivalenceGroup], int]:
        union = _UnionFind(captures)
        ignored = 0
        for left, right in self.loader.duplicate_audit.capture_equivalence_edges:
            if left not in captures or right not in captures:
                ignored += 1
                continue
            union.union(left, right)
        members: dict[str, list[str]] = defaultdict(list)
        for capture_id in captures:
            members[union.find(capture_id)].append(capture_id)
        groups: list[_EquivalenceGroup] = []
        for values in members.values():
            ordered = tuple(sorted(values))
            families = frozenset(
                family for capture_id in ordered for family in captures[capture_id].families
            )
            rows = sum(captures[capture_id].rows for capture_id in ordered)
            group_id = hashlib.sha256("\0".join(ordered).encode("ascii")).hexdigest()
            groups.append(_EquivalenceGroup(group_id, ordered, families, rows))
        return sorted(groups, key=lambda item: item.group_id), ignored

    @staticmethod
    def _allocate_counts(total: int, ratios: Mapping[str, float]) -> dict[str, int]:
        raw = {name: total * ratios[name] for name in KNOWN_PARTITIONS}
        counts = {name: int(math.floor(raw[name])) for name in KNOWN_PARTITIONS}
        remaining = total - sum(counts.values())
        order = sorted(
            KNOWN_PARTITIONS,
            key=lambda name: (-(raw[name] - counts[name]), KNOWN_PARTITIONS.index(name)),
        )
        for name in order[:remaining]:
            counts[name] += 1
        return counts

    @staticmethod
    def _assign_group(
        assignments: MutableMapping[str, str], group: _EquivalenceGroup, partition: str
    ) -> None:
        for capture_id in group.captures:
            if capture_id in assignments:
                raise DataContractError("capture received multiple split assignments")
            assignments[capture_id] = partition


@dataclass(frozen=True)
class TrainingSamplingPolicy:
    seed: int
    label_column: str = "family_label"
    default_class_cap: Optional[int] = None
    class_caps: Mapping[str, int] = field(default_factory=dict)
    max_rows_per_group: Optional[int] = None
    group_column: str = "capture_id"

    def validate(self) -> None:
        if self.label_column not in LABEL_COLUMNS:
            raise DataContractError(f"unsupported sampling label column: {self.label_column}")
        if self.group_column not in {"capture_id", "flow_key_hash"}:
            raise DataContractError(f"unsupported sampling group column: {self.group_column}")
        if self.default_class_cap is not None and self.default_class_cap <= 0:
            raise DataContractError("default_class_cap must be positive")
        if any(int(value) <= 0 for value in self.class_caps.values()):
            raise DataContractError("every class-specific cap must be positive")
        if self.max_rows_per_group is not None and self.max_rows_per_group <= 0:
            raise DataContractError("max_rows_per_group must be positive")
        if self.default_class_cap is None and not self.class_caps:
            raise DataContractError(
                "bounded sampling requires default_class_cap or explicit class_caps; "
                "use iter_train_passthrough for an unchanged training distribution"
            )


@dataclass(frozen=True)
class SamplingResult:
    records: tuple[RawDataRecord, ...]
    audit: Mapping[str, Any]


class TrainOnlySampler:
    """Apply deterministic, bounded sampling to training rows only."""

    def __init__(self, policy: TrainingSamplingPolicy) -> None:
        policy.validate()
        self.policy = policy

    @staticmethod
    def iter_train_passthrough(
        records: Iterable[RawDataRecord],
    ) -> Iterator[RawDataRecord]:
        for record in records:
            if record.partition != "train":
                raise DataContractError(
                    f"train-only sampler received {record.partition} data"
                )
            yield record

    def select(self, records: Iterable[RawDataRecord]) -> SamplingResult:
        input_by_class: Counter[str] = Counter()
        input_by_dataset: Counter[str] = Counter()
        class_heaps: dict[str, list[tuple[int, str, RawDataRecord]]] = {}
        if self.policy.max_rows_per_group is not None:
            group_heaps: dict[tuple[str, str], list[tuple[int, str, RawDataRecord]]] = {}
            for record in records:
                self._validate_train_record(record)
                label = record.row[self.policy.label_column]
                input_by_class[label] += 1
                input_by_dataset[record.dataset_id] += 1
                group = record.row[self.policy.group_column]
                heap = group_heaps.setdefault((label, group), [])
                self._bounded_push(heap, record, self.policy.max_rows_per_group)
            for heap in group_heaps.values():
                for _, _, record in heap:
                    self._push_class_candidate(class_heaps, record)
        else:
            for record in records:
                self._validate_train_record(record)
                label = record.row[self.policy.label_column]
                input_by_class[label] += 1
                input_by_dataset[record.dataset_id] += 1
                self._push_class_candidate(class_heaps, record)
        selected = [item[2] for heap in class_heaps.values() for item in heap]
        selected.sort(
            key=lambda record: (
                record.row[self.policy.label_column],
                _stable_priority(
                    self.policy.seed,
                    record.dataset_id,
                    record.sample_id,
                ),
                record.sample_id,
            )
        )
        selected_by_class = Counter(
            record.row[self.policy.label_column] for record in selected
        )
        selected_by_dataset = Counter(record.dataset_id for record in selected)
        audit: dict[str, Any] = {
            "schema_version": SAMPLING_AUDIT_SCHEMA_VERSION,
            "partition_scope": "train_only",
            "validation_or_test_rows_seen": 0,
            "strategy": "deterministic_sha256_priority_reservoir",
            "seed": self.policy.seed,
            "label_column": self.policy.label_column,
            "group_column": self.policy.group_column,
            "default_class_cap": self.policy.default_class_cap,
            "class_caps": dict(sorted(self.policy.class_caps.items())),
            "max_rows_per_group": self.policy.max_rows_per_group,
            "input_rows": sum(input_by_class.values()),
            "selected_rows": len(selected),
            "input_rows_by_class": dict(sorted(input_by_class.items())),
            "selected_rows_by_class": dict(sorted(selected_by_class.items())),
            "input_rows_by_dataset": dict(sorted(input_by_dataset.items())),
            "selected_rows_by_dataset": dict(sorted(selected_by_dataset.items())),
        }
        audit["sampling_audit_sha256"] = canonical_json_hash(audit)
        return SamplingResult(tuple(selected), audit)

    def _push_class_candidate(
        self,
        class_heaps: MutableMapping[str, list[tuple[int, str, RawDataRecord]]],
        record: RawDataRecord,
    ) -> None:
        label = record.row[self.policy.label_column]
        cap = self.policy.class_caps.get(label, self.policy.default_class_cap)
        if cap is None:
            raise DataContractError(f"no class cap is defined for observed label: {label}")
        heap = class_heaps.setdefault(label, [])
        self._bounded_push(heap, record, int(cap))

    def _bounded_push(
        self,
        heap: list[tuple[int, str, RawDataRecord]],
        record: RawDataRecord,
        cap: int,
    ) -> None:
        priority = _stable_priority(
            self.policy.seed,
            record.dataset_id,
            record.sample_id,
        )
        item = (-priority, record.sample_id, record)
        if len(heap) < cap:
            heapq.heappush(heap, item)
        elif priority < -heap[0][0]:
            heapq.heapreplace(heap, item)

    @staticmethod
    def _validate_train_record(record: RawDataRecord) -> None:
        if record.partition != "train":
            raise DataContractError(
                f"train-only sampler received {record.partition} data"
            )


def build_experiment_data_manifest(
    loader: UnifiedDatasetLoader,
    split_plan: SplitPlan,
    sampling_result: Optional[SamplingResult] = None,
) -> dict[str, Any]:
    loader._validate_split_plan_binding(split_plan)
    value: dict[str, Any] = {
        "schema_version": "caeos_experiment_data_manifest_v1",
        "dataset_id": loader.manifest.dataset_id,
        "dataset_manifest_sha256": loader.manifest.manifest_sha256,
        "schema_sha256": loader.schema.sha256,
        "feature_views_sha256": loader.feature_views.sha256,
        "policy_registry_sha256": loader.registry.sha256,
        "content_policy_sha256": loader.conflict_filter.policy_sha256,
        "duplicate_audit_sha256": loader.duplicate_audit.sha256,
        "split_plan_sha256": split_plan.split_plan_sha256,
        "feature_request": loader.materializer.request_manifest,
        "sampling_audit": sampling_result.audit if sampling_result else None,
        "unknown_test_used_for_selection": False,
        "threshold_fit_scope": "known_only_validation",
    }
    value["experiment_data_manifest_sha256"] = canonical_json_hash(value)
    return value


__all__ = [
    "ContentConflictFilter",
    "CsvSchemaContract",
    "DataContractError",
    "DatasetManifestContract",
    "DatasetPolicyRegistry",
    "DuplicateAuditContract",
    "FeatureMaterializer",
    "FeatureViewContract",
    "LoadAudit",
    "ModelExample",
    "OpenSetDataStrategy",
    "RawDataRecord",
    "SamplingResult",
    "SplitPlan",
    "TrainOnlySampler",
    "TrainingSamplingPolicy",
    "UnifiedDatasetLoader",
    "build_experiment_data_manifest",
    "canonical_json_hash",
    "digest_fields",
    "sha256_file",
]
