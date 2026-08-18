from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=40)
    args = parser.parse_args()
    text_dir = Path(__file__).resolve().parents[1] / "03_全文抽取缓存"
    for path in sorted(text_dir.glob("[0-9][0-9]_*.txt")):
        number = int(path.name[:2])
        if not args.start <= number <= args.end:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"\bAbstract\b", text, re.I)
        excerpt = text[match.start() : match.start() + 2200] if match else text[:2200]
        excerpt = re.sub(r"\s+", " ", excerpt).strip()
        datasets = sorted(set(re.findall(
            r"(?:CIC[-_ ]?(?:IDS|IoT|DDoS)[-_ ]?\d{4}|USTC[-_ ]?TFC[-_ ]?2016|"
            r"ISCX[-_ ]?(?:VPN|Tor|VPN-NonVPN)[-_ ]?2016|UNSW[-_ ]?NB15|"
            r"CTU[-_ ]?13|BoT[-_ ]?IoT|ToN[-_ ]?IoT|MNET2024|ISCX2012|"
            r"CrossPlatform|ISCX[-_ ]?VPN[-_ ]?NonVPN)", text, re.I
        )))
        print(f"## {path.stem}\nDATASETS: {', '.join(datasets) or '[not auto-located]'}\n{excerpt}\n")


if __name__ == "__main__":
    main()
