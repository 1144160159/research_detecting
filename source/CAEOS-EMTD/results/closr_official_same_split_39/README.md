# CLOSR official-config same-split comparison

This directory contains the compact local archive for the 39-run CLOSR comparison. Models, score arrays, and per-run logs remain on the GPU server.

## Protocol

- Suites: DoHBrw2020, Mal_TLS2023, and HIKARI2021.
- Seeds: 7, 11, and 19.
- CLOSR: three 1024-wide MLP layers, 64-dimensional class heads, 200 epochs, batch size 4096, peak learning rate `1e-5`, weight decay `0.0403709`.
- Centroids: fitted from known training samples only.
- Rejection threshold: calibrated on the independent known validation split only.
- Gate comparator: the matching v1.4.3 result; v1.4.4 leaves these 39 paths unchanged.

## Result

CAEOS obtains mean unknown AUROC `0.932796`, while CLOSR obtains `0.767187`. The paired result is 33 wins and 6 losses for CAEOS, with two-sided Wilcoxon `p=2.40e-08`. CLOSR wins all three HIKARI Bruteforce-XML runs, two Probing runs, and one Mal_TLS Tor run.

## Files

- `manifest.json`: completion state and runtime metadata for all 39 CLOSR runs.
- `comparison.json`: full paired metrics and per-run values.
- `comparison.md`: compact per-suite report.

