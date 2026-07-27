from __future__ import annotations

from pathlib import Path


CICDDOS2019_LABEL_ALIASES = {
    "UDP-lag": "UDPLag",
}


def normalized_label(value: str) -> str:
    return " ".join(str(value).strip().split())


def _identity_token(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def canonical_external_label(dataset: str, member: str, label: str) -> str:
    value = normalized_label(label)
    if dataset != "CICDDoS2019" or value not in CICDDOS2019_LABEL_ALIASES:
        return value
    canonical = CICDDOS2019_LABEL_ALIASES[value]
    if _identity_token(Path(member).stem) != _identity_token(canonical):
        raise ValueError(
            f"CICDDoS2019 label alias {value!r} is outside its canonical "
            f"member: {member}"
        )
    return canonical
