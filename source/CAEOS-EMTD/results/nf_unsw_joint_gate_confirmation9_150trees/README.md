# NF-UNSW v1.4.4 independent confirmation

This directory contains the compact evidence archive for the frozen v1.4.4 confirmation. Per-sample predictions and sampled CSV files remain on the GPU server.

## Protocol

- Dataset: NF-UNSW-NB15-v2.
- Unknown families: Analysis, Backdoor, DoS, Exploits, Generic, and Reconnaissance.
- Independent seeds: 47, 53, 59, 61, 67, 71, 73, 79, and 83.
- Scale: at most 5000 rows per class and 150 trees.
- Split: cross-label fingerprints removed before fingerprint-grouped train/validation/test splitting.
- Frozen risk rule: `nested_hierarchical_joint_gate` with minimum inner robust gain `0.055`.

## Result

The v1.4.4 mean unknown AUROC is `0.763173`, compared with `0.747583` for v1.4.3. The paired outcome is 12 wins, 41 ties, and 1 loss; the exact two-sided Wilcoxon p-value over changed pairs is `0.001709`. AUPR, OSCR, FPR95, unknown F1, known acceptance, and unknown rejection all improve on average. Reconnaissance seed73 is the retained negative case.

## Files

- `manifest_*.json`: exact commands and completion state for both execution batches.
- `summary.json` and `summary.md`: combined nine-seed runtime result against v1.4.3.
- `replay_gain_0055.json`: independent offline replay of the frozen safety gate.
- `seed*_max5000.csv.json`: source, class counts, columns, seed, and SHA-256 for every deterministic remote cache.

