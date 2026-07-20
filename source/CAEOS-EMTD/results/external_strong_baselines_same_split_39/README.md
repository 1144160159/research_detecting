# External strong baselines on the same 39 tasks

This compact archive compares the fixed CAEOS v1.4.4 gate with official-method adaptations of CLOSR and CADE. Full models, score arrays, logs, and per-run metrics remain on the GPU server.

## Fixed protocol

- Datasets: DoHBrw2020, Mal_TLS2023, HIKARI2021.
- Tasks: 13 leave-one-attack-out scenarios with seeds 7, 11, and 19; 39 paired runs.
- Splits: CaptureId grouping for DoH; full-feature fingerprint grouping for Mal_TLS and HIKARI.
- Calibration: known validation data only; real unknown samples are test-only.
- CLOSR: official 200-epoch class-specific contrastive configuration.
- CADE: official architecture/objective adapted to PyTorch, 250 AE epochs and 30 classifier epochs.

## Global AUROC

| Method | Mean AUROC | CAEOS W/T/L | Wilcoxon p |
|---|---:|---:|---:|
| CAEOS v1.4.4 | `0.932796` | - | - |
| CLOSR | `0.767187` | 33/0/6 | `2.40e-08` |
| CADE | `0.630395` | 39/0/0 | `3.64e-12` |

Files:

- `comparison.json` and `comparison.md`: paired CAEOS/CLOSR/CADE comparison.
- `cade_summary.json` and `cade_summary.md`: calibrated versus fixed MAD=3.5 CADE results.
- `cade_manifest.json`: completion status for all 39 CADE runs.
