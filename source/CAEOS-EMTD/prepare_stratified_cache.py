from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build one deterministic stratified CSV cache for repeated leave-out runs"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--max-per-class", type=int, required=True)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata", default="")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_cache(
    csv_path: str,
    config_path: str,
    max_per_class: int,
    chunksize: int,
    seed: int,
    output_path: str,
    metadata_path: str = "",
    loader: Callable[..., object] | None = None,
) -> dict[str, object]:
    if loader is None:
        from caeos.data import load_stratified_reservoir

        loader = load_stratified_reservoir
    config_file = Path(config_path)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    label_column = str(config["label_column"])
    modalities = config["modalities"]
    feature_columns = [
        column for columns in modalities.values() for column in columns
    ]
    group_column = str(config.get("group_column", ""))
    frame = loader(
        csv_path,
        label_column,
        feature_columns,
        max_per_class,
        chunksize,
        seed,
        additional_columns=([group_column] if group_column else []),
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    source = Path(csv_path)
    report = {
        "source_csv": str(source.resolve()),
        "source_size_bytes": source.stat().st_size,
        "source_sha256": sha256(source),
        "config": str(config_file.resolve()),
        "config_sha256": sha256(config_file),
        "seed": seed,
        "max_per_class": max_per_class,
        "rows": int(len(frame)),
        "per_class": {
            str(label): int(count)
            for label, count in frame[label_column].value_counts().sort_index().items()
        },
        "columns": list(frame.columns),
        "output_csv": str(output.resolve()),
        "output_sha256": sha256(output),
    }
    metadata = (
        Path(metadata_path)
        if metadata_path
        else output.with_suffix(output.suffix + ".json")
    )
    metadata.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    args = parse_arguments()
    report = build_cache(
        args.csv,
        args.config,
        args.max_per_class,
        args.chunksize,
        args.seed,
        args.output,
        args.metadata,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
