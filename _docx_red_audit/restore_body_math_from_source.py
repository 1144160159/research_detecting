from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

from lxml import etree as ET

OMATH_RE = re.compile(rb"<m:oMath(?:\s[^>]*)?>.*?</m:oMath>", re.DOTALL)
COMMENT_MARKER_RE = re.compile(
    rb'<w:(?:commentRangeStart|commentRangeEnd|commentReference)\b[^>]*\bw:id="(\d+)"[^>]*/>',
    re.DOTALL,
)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    temp = args.target.with_suffix(".body-math.tmp.docx")
    if temp.exists():
        temp.unlink()

    with zipfile.ZipFile(args.source) as source_zip, zipfile.ZipFile(
        args.target
    ) as target_zip:
        source_document = source_zip.read("word/document.xml")
        target_document = target_zip.read("word/document.xml")
        source_maths = OMATH_RE.findall(source_document)
        target_maths = OMATH_RE.findall(target_document)
        if len(source_maths) != len(target_maths):
            raise RuntimeError(
                f"Body math count differs: source={len(source_maths)}, target={len(target_maths)}"
            )

        comments_root = ET.fromstring(target_zip.read("word/comments.xml"))
        valid_comment_ids = {
            comment.get(f"{{{W}}}id")
            for comment in comments_root.findall(f"{{{W}}}comment")
        }
        removed_markers = 0

        def clean_markers(formula: bytes) -> bytes:
            nonlocal removed_markers

            def replace_marker(match: re.Match[bytes]) -> bytes:
                nonlocal removed_markers
                comment_id = match.group(1).decode("ascii")
                if comment_id in valid_comment_ids:
                    return match.group(0)
                removed_markers += 1
                return b""

            return COMMENT_MARKER_RE.sub(replace_marker, formula)

        cleaned_source_maths = [clean_markers(formula) for formula in source_maths]
        replacements = iter(cleaned_source_maths)
        restored_document, replaced = OMATH_RE.subn(
            lambda _match: next(replacements), target_document
        )
        if replaced != len(source_maths):
            raise RuntimeError(
                f"Replaced {replaced} formulas, expected {len(source_maths)}."
            )

        with zipfile.ZipFile(temp, "w") as output_zip:
            for info in target_zip.infolist():
                data = (
                    restored_document
                    if info.filename == "word/document.xml"
                    else target_zip.read(info.filename)
                )
                output_zip.writestr(info, data)

    with zipfile.ZipFile(temp) as check_zip:
        bad = check_zip.testzip()
        if bad is not None:
            raise RuntimeError(f"Patched DOCX failed ZIP validation at {bad}.")
        restored_maths = OMATH_RE.findall(check_zip.read("word/document.xml"))
        if len(restored_maths) != len(source_maths):
            raise RuntimeError("Restored body math count changed unexpectedly.")

    shutil.move(temp, args.target)
    print(
        {
            "restored_body_math_objects": len(source_maths),
            "removed_stale_comment_markers": removed_markers,
        }
    )


if __name__ == "__main__":
    main()
