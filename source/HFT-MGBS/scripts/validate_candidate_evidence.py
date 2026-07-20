"""Validate a final candidate envelope before Pareto evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hft_mgbs.evidence import CandidateEvidenceEnvelope, audit_candidate_evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    with args.candidate.open("r", encoding="utf-8") as handle:
        envelope = CandidateEvidenceEnvelope.from_mapping(json.load(handle))
    audit = audit_candidate_evidence(envelope)
    print(json.dumps(audit.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if audit.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
