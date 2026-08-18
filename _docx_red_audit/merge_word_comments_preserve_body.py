from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

from lxml import etree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MARKER_RE = re.compile(
    rb'<w:(?:commentRangeStart|commentRangeEnd|commentReference)\b[^>]*\bw:id="(\d+)"[^>]*/>',
    re.DOTALL,
)


def logical_id(text: str) -> str | None:
    match = re.match(r"^\[[^0-9]*(\d{3})/154", text)
    if match:
        return f"M{int(match.group(1)):03d}"
    match = re.match(r"^\[[^0-9]*(\d{2})/26", text)
    if match:
        return f"S{int(match.group(1)):02d}"
    return None


def comment_id_map(archive: zipfile.ZipFile) -> dict[str, str]:
    root = ET.fromstring(archive.read("word/comments.xml"))
    result: dict[str, str] = {}
    for comment in root.findall(f"{{{W}}}comment"):
        lid = logical_id("".join(comment.itertext()))
        wid = comment.get(f"{{{W}}}id")
        if lid is None or wid is None:
            raise RuntimeError("Comment has no logical or Word id.")
        if lid in result:
            raise RuntimeError(f"Duplicate logical comment id: {lid}")
        result[lid] = wid
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("body_source", type=Path)
    parser.add_argument("word_comments_source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    temp = args.output.with_suffix(".merge.tmp.docx")
    if temp.exists():
        temp.unlink()

    with zipfile.ZipFile(args.body_source) as body_zip, zipfile.ZipFile(
        args.word_comments_source
    ) as word_zip:
        body_ids = comment_id_map(body_zip)
        word_ids = comment_id_map(word_zip)
        if set(body_ids) != set(word_ids):
            raise RuntimeError(
                f"Logical comment ids differ: body-only={sorted(set(body_ids)-set(word_ids))}, "
                f"word-only={sorted(set(word_ids)-set(body_ids))}"
            )
        id_mapping = {body_ids[lid]: word_ids[lid] for lid in body_ids}

        body_document = body_zip.read("word/document.xml")
        remapped = 0

        def remap_marker(match: re.Match[bytes]) -> bytes:
            nonlocal remapped
            old_id = match.group(1).decode("ascii")
            if old_id not in id_mapping:
                raise RuntimeError(f"Document marker references unknown comment id {old_id}.")
            new_id = id_mapping[old_id]
            if old_id != new_id:
                remapped += 1
            element = match.group(0)
            return re.sub(
                rb'w:id="\d+"',
                f'w:id="{new_id}"'.encode("ascii"),
                element,
                count=1,
            )

        merged_document, marker_count = MARKER_RE.subn(remap_marker, body_document)

        with zipfile.ZipFile(temp, "w") as output_zip:
            for info in word_zip.infolist():
                data = (
                    merged_document
                    if info.filename == "word/document.xml"
                    else word_zip.read(info.filename)
                )
                output_zip.writestr(info, data)

    with zipfile.ZipFile(temp) as check_zip:
        bad = check_zip.testzip()
        if bad is not None:
            raise RuntimeError(f"Merged DOCX failed ZIP validation at {bad}.")
        target_ids = set(comment_id_map(check_zip).values())
        document = check_zip.read("word/document.xml")
        marker_ids = {
            match.group(1).decode("ascii") for match in MARKER_RE.finditer(document)
        }
        if not marker_ids.issubset(target_ids):
            raise RuntimeError(
                f"Unresolved marker ids: {sorted(marker_ids-target_ids, key=int)}"
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(temp, args.output)
    print(
        {
            "comments": len(body_ids),
            "comment_markers": marker_count,
            "remapped_markers": remapped,
            "renumbered_comments": sum(
                1 for old_id, new_id in id_mapping.items() if old_id != new_id
            ),
        }
    )


if __name__ == "__main__":
    main()
