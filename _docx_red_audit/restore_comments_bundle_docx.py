from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


def is_comment_bundle_part(name: str) -> bool:
    return (
        name.startswith("word/comments")
        or name.startswith("word/_rels/comments")
        or name == "word/people.xml"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    temp = args.target.with_suffix(".comments-bundle.tmp.docx")
    if temp.exists():
        temp.unlink()

    with zipfile.ZipFile(args.source) as source_zip, zipfile.ZipFile(
        args.target
    ) as target_zip:
        target_parts = {
            name: target_zip.read(name)
            for name in target_zip.namelist()
            if is_comment_bundle_part(name)
        }
        if "word/comments.xml" not in target_parts:
            raise RuntimeError("Target DOCX has no comments.xml part.")

        source_names = set(source_zip.namelist())
        with zipfile.ZipFile(temp, "w") as output_zip:
            for info in source_zip.infolist():
                data = target_parts.get(info.filename, source_zip.read(info.filename))
                output_zip.writestr(info, data)
            for name, data in target_parts.items():
                if name not in source_names:
                    output_zip.writestr(name, data)

    with zipfile.ZipFile(temp) as check_zip:
        bad = check_zip.testzip()
        if bad is not None:
            raise RuntimeError(f"Patched DOCX failed ZIP validation at {bad}.")
        for name, data in target_parts.items():
            if check_zip.read(name) != data:
                raise RuntimeError(f"Comment bundle part changed: {name}")

    shutil.move(temp, args.target)
    print({"preserved_comment_parts": sorted(target_parts)})


if __name__ == "__main__":
    main()
