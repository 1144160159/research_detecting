from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

from lxml import etree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
}
def qn(prefix: str, local: str) -> str:
    return f"{{{NS[prefix]}}}{local}"


def spec_id(text: str) -> str | None:
    match = re.match(r"^\[[^0-9]*(\d{3})/154", text)
    if match:
        return f"M{int(match.group(1)):03d}"
    match = re.match(r"^\[[^0-9]*(\d{2})/26", text)
    if match:
        return f"S{int(match.group(1)):02d}"
    return None


def remove_comment_markers(xml_data: bytes, ids: set[str]) -> bytes:
    root = ET.fromstring(xml_data, parser=ET.XMLParser(remove_blank_text=False))
    marker_tags = {
        qn("w", "commentRangeStart"),
        qn("w", "commentRangeEnd"),
        qn("w", "commentReference"),
    }
    for parent in root.iter():
        for child in list(parent):
            if child.tag in marker_tags and child.get(qn("w", "id")) in ids:
                parent.remove(child)
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--delete", nargs="+", required=True)
    args = parser.parse_args()

    delete_specs = set(args.delete)
    temp = args.target.with_suffix(".tmp.docx")
    if temp.exists():
        temp.unlink()

    with zipfile.ZipFile(args.source) as source_zip:
        parser = ET.XMLParser(remove_blank_text=False)
        comments_root = ET.fromstring(
            source_zip.read("word/comments.xml"), parser=parser
        )
        word_ids: set[str] = set()
        para_ids: set[str] = set()
        for comment in list(comments_root):
            if comment.tag != qn("w", "comment"):
                continue
            text = "".join(comment.itertext())
            if spec_id(text) not in delete_specs:
                continue
            word_id = comment.get(qn("w", "id"))
            if word_id is not None:
                word_ids.add(word_id)
            for paragraph in comment.findall(".//w:p", NS):
                para_id = paragraph.get(qn("w14", "paraId"))
                if para_id:
                    para_ids.add(para_id)
            comments_root.remove(comment)

        if len(word_ids) != len(delete_specs):
            raise RuntimeError(
                f"Expected {len(delete_specs)} comments, found {len(word_ids)}: {sorted(word_ids)}"
            )

        replacements: dict[str, bytes] = {
            "word/comments.xml": ET.tostring(
                comments_root,
                encoding="UTF-8",
                xml_declaration=True,
                standalone=True,
            ),
            "word/document.xml": remove_comment_markers(
                source_zip.read("word/document.xml"), word_ids
            ),
        }

        durable_ids: set[str] = set()
        if "word/commentsIds.xml" in source_zip.namelist():
            root = ET.fromstring(
                source_zip.read("word/commentsIds.xml"), parser=parser
            )
            for child in list(root):
                if child.get(qn("w16cid", "paraId")) in para_ids:
                    durable_id = child.get(qn("w16cid", "durableId"))
                    if durable_id:
                        durable_ids.add(durable_id)
                    root.remove(child)
            replacements["word/commentsIds.xml"] = ET.tostring(
                root, encoding="UTF-8", xml_declaration=True, standalone=True
            )

        if "word/commentsExtended.xml" in source_zip.namelist():
            root = ET.fromstring(
                source_zip.read("word/commentsExtended.xml"), parser=parser
            )
            for child in list(root):
                if (
                    child.get(qn("w15", "paraId")) in para_ids
                    or child.get(qn("w15", "paraIdParent")) in para_ids
                ):
                    root.remove(child)
            replacements["word/commentsExtended.xml"] = ET.tostring(
                root, encoding="UTF-8", xml_declaration=True, standalone=True
            )

        if "word/commentsExtensible.xml" in source_zip.namelist():
            root = ET.fromstring(
                source_zip.read("word/commentsExtensible.xml"), parser=parser
            )
            for child in list(root):
                if child.get(qn("w16cex", "durableId")) in durable_ids:
                    root.remove(child)
            replacements["word/commentsExtensible.xml"] = ET.tostring(
                root, encoding="UTF-8", xml_declaration=True, standalone=True
            )

        with zipfile.ZipFile(temp, "w") as target_zip:
            for info in source_zip.infolist():
                target_zip.writestr(
                    info, replacements.get(info.filename, source_zip.read(info.filename))
                )

    with zipfile.ZipFile(temp) as check_zip:
        bad = check_zip.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt output part: {bad}")
        comments_root = ET.fromstring(
            check_zip.read("word/comments.xml"),
            parser=ET.XMLParser(remove_blank_text=False),
        )
        remaining = comments_root.findall("w:comment", NS)
        if len(remaining) == 0:
            raise RuntimeError("All comments were removed unexpectedly.")

    args.target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(temp, args.target)
    print(
        {
            "deleted_spec_ids": sorted(delete_specs),
            "deleted_word_ids": sorted(word_ids, key=int),
            "deleted_para_ids": sorted(para_ids),
            "remaining_comments": len(remaining),
        }
    )


if __name__ == "__main__":
    main()
