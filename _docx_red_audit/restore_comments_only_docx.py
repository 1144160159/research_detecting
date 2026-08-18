from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


COMMENTS_PART = "word/comments.xml"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    temp = args.target.with_suffix(".comments-only.tmp.docx")
    if temp.exists():
        temp.unlink()

    with zipfile.ZipFile(args.source) as source_zip, zipfile.ZipFile(args.target) as target_zip:
        if COMMENTS_PART not in source_zip.namelist() or COMMENTS_PART not in target_zip.namelist():
            raise RuntimeError("Comments part is missing from source or target DOCX.")
        comments = target_zip.read(COMMENTS_PART)

        with zipfile.ZipFile(temp, "w") as output_zip:
            for info in source_zip.infolist():
                data = comments if info.filename == COMMENTS_PART else source_zip.read(info.filename)
                output_zip.writestr(info, data)

    with zipfile.ZipFile(temp) as check_zip:
        if check_zip.testzip() is not None:
            raise RuntimeError("Patched DOCX failed ZIP validation.")
        if check_zip.read(COMMENTS_PART) != comments:
            raise RuntimeError("Comments part changed during patching.")

    shutil.move(temp, args.target)


if __name__ == "__main__":
    main()
