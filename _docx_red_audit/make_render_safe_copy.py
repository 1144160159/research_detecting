from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from PIL import Image


source = Path(sys.argv[1])
target = Path(sys.argv[2])
target.parent.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(source) as zin, zipfile.ZipFile(target, "w") as zout:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename.startswith("word/media/") and info.filename.lower().endswith(".png"):
            with Image.open(io.BytesIO(data)) as image:
                normalized = image.convert("RGB")
                buffer = io.BytesIO()
                normalized.save(buffer, format="PNG", compress_level=6)
                data = buffer.getvalue()
        zout.writestr(info, data)

print(target)
