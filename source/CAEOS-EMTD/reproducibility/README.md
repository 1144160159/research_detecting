# CAEOS-EMTD minimal reproduction

This package addresses the minimum public reproducibility boundary for the
current open-set encrypted malicious-traffic study. It fixes two datasets and
one unknown family per dataset:

- Mal_TLS2023: `Tor_None_TLS_CC`
- HIKARI2021: `Probing`

Each task runs the same three predeclared risk profiles:
`support_union`, `cauchy_evidence`, and `nested_conflict_gate`. The split is
`fingerprint_grouped`; no test-label oracle is used for model or threshold
selection.

## Environment

Use Python 3.9.23 and install the pinned GPU dependencies:

```bash
python -m pip install -r requirements-lock-gpu-cu121.txt
```

The captured GPU environment is recorded in
`reproducibility/environment-gpu-cu121.json`. Config JSON files and the lock
file are explicitly excluded from Git LFS so a source checkout remains
readable without fetching data artifacts.

## Preflight

The smoke profile is a fast execution and artifact-integrity check. It is not
scientific evidence.

```bash
python reproducibility/run_minimal_repro.py \
  --mal-csv /path/to/malicious_TLS.csv \
  --hikari-csv /path/to/HIKARI2021_model.csv \
  --mode smoke \
  --output-root results/minimal_repro \
  --dry-run
```

Remove `--dry-run` to execute six runs. The paper profile executes three seeds
for all six dataset/profile combinations:

```bash
python reproducibility/run_minimal_repro.py \
  --mal-csv /path/to/malicious_TLS.csv \
  --hikari-csv /path/to/HIKARI2021_model.csv \
  --mode paper \
  --output-root results/minimal_repro \
  --hash-inputs
```

The runner refuses to overwrite existing metrics unless `--reuse` is supplied.
It emits a manifest containing source/config hashes, input identity, exact
commands, selected metrics, and hashes of `metrics.json`, `scores.npz`, and
`evidence_package.npz`.

## Claim boundary

The paper profile is a focused, reviewer-facing comparison of the support,
conflict, and validation-driven nested paths. It does not by itself establish
comprehensive SOTA, final algorithm selection, cross-dataset generalization, or
deployment safety.
