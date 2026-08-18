from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

from lxml import etree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MARKER_RE = re.compile(
    rb'(<w:(?:commentRangeStart|commentRangeEnd|commentReference)\b[^>]*\bw:id=")(-?\d+)(")'
)


def q(local: str) -> str:
    return f"{{{W}}}{local}"


def logical_id(text: str) -> str | None:
    match = re.match(r"^\[[^0-9]*(\d{3})/154", text)
    if match:
        return f"M{int(match.group(1)):03d}"
    match = re.match(r"^\[[^0-9]*(\d{2})/26", text)
    if match:
        return f"S{int(match.group(1)):02d}"
    return None


def comment_id_map(xml_data: bytes) -> dict[str, str]:
    root = ET.fromstring(xml_data)
    result: dict[str, str] = {}
    for comment in root.findall(q("comment")):
        lid = logical_id("".join(comment.itertext()))
        wid = comment.get(q("id"))
        if lid is None or wid is None:
            raise RuntimeError("Comment without a recognized logical or Word id.")
        if lid in result:
            raise RuntimeError(f"Duplicate logical comment id: {lid}")
        result[lid] = wid
    return result


def is_comment_bundle_part(name: str) -> bool:
    return (
        name.startswith("word/comments")
        or name.startswith("word/_rels/comments")
        or name == "word/people.xml"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("word", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    temp = args.output.with_suffix(".tmp.docx")
    if temp.exists():
        temp.unlink()

    with zipfile.ZipFile(args.base) as base_zip, zipfile.ZipFile(
        args.word
    ) as word_zip:
        base_comments = base_zip.read("word/comments.xml")
        word_comments = word_zip.read("word/comments.xml")
        base_map = comment_id_map(base_comments)
        word_map = comment_id_map(word_comments)
        if set(base_map) != set(word_map):
            raise RuntimeError(
                f"Logical comment sets differ: missing={sorted(set(base_map)-set(word_map))}, "
                f"extra={sorted(set(word_map)-set(base_map))}"
            )

        numeric_map = {base_map[lid]: word_map[lid] for lid in base_map}
        base_document = base_zip.read("word/document.xml")
        seen_old_ids: set[str] = set()

        def replace_marker(match: re.Match[bytes]) -> bytes:
            old_id = match.group(2).decode("ascii")
            if old_id not in numeric_map:
                raise RuntimeError(f"Document references unknown comment id {old_id}.")
            seen_old_ids.add(old_id)
            return (
                match.group(1)
                + numeric_map[old_id].encode("ascii")
                + match.group(3)
            )

        remapped_document, marker_count = MARKER_RE.subn(
            replace_marker, base_document
        )
        if seen_old_ids != set(numeric_map):
            raise RuntimeError(
                f"Not every comment id was referenced: {sorted(set(numeric_map)-seen_old_ids)}"
            )

        word_bundle = {
            name: word_zip.read(name)
            for name in word_zip.namelist()
            if is_comment_bundle_part(name)
        }
        if "word/comments.xml" not in word_bundle:
            raise RuntimeError("Word DOCX has no comments.xml part.")

        base_names = set(base_zip.namelist())
        with zipfile.ZipFile(temp, "w") as output_zip:
            for info in base_zip.infolist():
                if info.filename == "word/document.xml":
                    data = remapped_document
                elif info.filename in word_bundle:
                    data = word_bundle[info.filename]
                else:
                    data = base_zip.read(info.filename)
                output_zip.writestr(info, data)
            for name, data in word_bundle.items():
                if name not in base_names:
                    output_zip.writestr(name, data)

    with zipfile.ZipFile(temp) as check_zip:
        bad = check_zip.testzip()
        if bad is not None:
            raise RuntimeError(f"Merged DOCX failed ZIP validation at {bad}.")
        output_map = comment_id_map(check_zip.read("word/comments.xml"))
        if output_map != word_map:
            raise RuntimeError("Merged comments.xml does not match the Word source.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(temp, args.output)
    changed_ids = sum(base_map[lid] != word_map[lid] for lid in base_map)
    print(
        {
            "comments": len(base_map),
            "remapped_comment_ids": changed_ids,
            "comment_markers": marker_count,
            "comment_bundle_parts": sorted(word_bundle),
        }
    )


if __name__ == "__main__":
    main()
